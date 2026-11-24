#!/usr/bin/env python3
"""배포된 사이트를 네이버 검색로봇(Yeti) 이름으로 요청해 웹마스터 가이드 기준을 점검한다.

사용: python3 check-site.py https://example.com [--limit 200]

검사하는 것
- robots.txt: 200 + text/plain, Disallow 목록, Sitemap 위치
- http→https, www→대표 주소 301
- 없는 주소가 404 상태인지(소프트 404 아님), /favicon.ico
- 사이트맵의 모든 쪽: 상태 200, <title> 1개·40자, description 있음·80자, 제목=설명 아님,
  h1 1개, canonical(절대 주소·자기 자신), og:type/title/description/image/url, viewport, utf-8,
  noindex/nofollow, 파비콘 href 절대 주소·같은 rel 중복, img alt, javascript: 링크, 같은 호스트 http 링크,
  JSON-LD 파싱·BreadcrumbList 이름("홈"·"top" 같은 일반 낱말), 첫 화면 WebSite(name) — 구글 사이트 이름
- 구글: 첫 화면 파비콘이 SVG 뿐인지(구글 형식 목록에 SVG 없음, 구글은 첫 화면 파비콘만 씀), HTML 2MB 초과(Googlebot 은 앞 2MB 만 읽음)
- 사이트 전체: 중복 제목·설명, og:image 를 몇 쪽이 같이 쓰는지
- og:image 파일(이미지마다 한 번): 절대 주소, 200·image/*, 5,000 byte 이상, 150×150 초과, 가로:세로 3:1 이내(PNG·JPEG·GIF·WebP 머리에서 읽음)
- 같은 쪽을 일반 브라우저 이름으로도 요청해 Yeti 와 비교: 상태·title 이 다르거나 본문 글자 수가 크게 다르면 클로킹으로 보일 수 있음
- 자바스크립트를 실행하지 않은 HTML 의 본문 글자가 거의 없으면(화면을 JS 로만 그림) 검색로봇이 내용을 못 읽을 수 있음
- --render: 시스템 Chrome(헤드리스)으로 자바스크립트를 실행한 뒤의 DOM 과 비교 — title·canonical·robots 를 JS 가 바꾸는지,
  h1·본문이 JS 를 실행해야만 생기는지. 구글은 렌더링한 쪽을 보지만 렌더링 전 noindex 면 렌더링하지 않고,
  JS 로 canonical 을 바꾸지 말라고 한다. 네이버는 렌더링 여부를 공개하지 않았다 — 실행 전 HTML 에 내용이 있는 편이 안전하다.
  Chrome·Edge·Chromium 을 찾지 못하면(CHROME_PATH 로 지정 가능) 건너뛴다. 쪽마다 몇 초 걸린다(--limit 와 함께).
- 환경 변수 CRUX_API_KEY 가 있으면 Chrome UX Report API 로 사이트 전체(origin)의 실제 사용자 Core Web Vitals
  (LCP·INP·CLS 75번째 백분위, 최근 28일)를 한 번 묻는다. 방문이 적은 사이트는 데이터가 없다(404 → "데이터 없음").
표준 라이브러리만 쓴다(설치 없음). --no-compare 로 브라우저 비교를 끄면 요청이 절반으로 준다.
"""
import argparse
import collections
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

UA = 'Mozilla/5.0 (compatible; Yeti/1.1; +https://naver.me/spd)'
BROWSER_UA = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
)
TITLE_MAX, DESC_MAX = 40, 80
OG_MIN_BYTES, OG_MIN_SIDE, OG_MAX_RATIO = 5000, 150, 3
# 자바스크립트 없이 본문 글자(공백 제외)가 이보다 적으면 JS 로만 그리는 쪽으로 본다
JS_ONLY_TEXT = 100
# Yeti·브라우저 본문 글자 수가 이 비율 넘게 다르면 다른 내용을 주는 것으로 본다(광고·날짜 같은 작은 차이는 넘지 않게)
UA_TEXT_DIFF = 0.3
GENERIC_CRUMBS = {'홈', 'home', 'top', '메인', 'main'}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def get(url, ua=UA, follow=False):
    req = urllib.request.Request(url, headers={'User-Agent': ua})
    opener = urllib.request.build_opener() if follow else OPENER
    try:
        with opener.open(req, timeout=20) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:  # DNS·연결 오류
        return 0, {}, str(e).encode()


def image_size(b):
    """PNG·GIF·JPEG·WebP 머리에서 (가로, 세로). 모르는 형식이면 None"""
    if b[:8] == b'\x89PNG\r\n\x1a\n' and len(b) >= 24:
        return int.from_bytes(b[16:20], 'big'), int.from_bytes(b[20:24], 'big')
    if b[:6] in (b'GIF87a', b'GIF89a') and len(b) >= 10:
        return int.from_bytes(b[6:8], 'little'), int.from_bytes(b[8:10], 'little')
    if b[:4] == b'RIFF' and b[8:12] == b'WEBP' and len(b) >= 30:
        kind = b[12:16]
        if kind == b'VP8 ':
            return int.from_bytes(b[26:28], 'little') & 0x3FFF, int.from_bytes(b[28:30], 'little') & 0x3FFF
        if kind == b'VP8L':
            bits = int.from_bytes(b[21:25], 'little')
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if kind == b'VP8X':
            return int.from_bytes(b[24:27], 'little') + 1, int.from_bytes(b[27:30], 'little') + 1
    if b[:2] == b'\xff\xd8':
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            marker = b[i + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
                i += 1 if marker == 0xFF else 2
                continue
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                return int.from_bytes(b[i + 7:i + 9], 'big'), int.from_bytes(b[i + 5:i + 7], 'big')
            i += 2 + int.from_bytes(b[i + 2:i + 4], 'big')
    return None


def check_og_image(img, issues):
    """네이버 웹마스터 가이드 "콘텐츠 마크업": og:image 150×150 초과·5,000 byte 이상·가로:세로 3:1 이내"""
    if not img.startswith('http'):
        issues['og:image 가 상대 주소'].append(img)
        return
    status, headers, body = get(img, follow=True)
    ctype = {k.lower(): v for k, v in headers.items()}.get('content-type', '')
    if status != 200 or not ctype.startswith('image/'):
        issues['og:image 를 받을 수 없음(200·image/* 아님)'].append(f'{status} {ctype} {img}')
        return
    if len(body) < OG_MIN_BYTES:
        issues[f'og:image {OG_MIN_BYTES:,} byte 미만'].append(f'{len(body)} byte {img}')
    size = image_size(body)
    if not size:
        issues['og:image 크기를 읽지 못함(PNG·JPEG·GIF·WebP 아님)'].append(f'{ctype} {img}')
        return
    w, h = size
    if w <= OG_MIN_SIDE or h <= OG_MIN_SIDE:
        issues[f'og:image {OG_MIN_SIDE}×{OG_MIN_SIDE} 이하'].append(f'{w}×{h} {img}')
    if h and w and max(w, h) / min(w, h) > OG_MAX_RATIO:
        issues[f'og:image 가로:세로 {OG_MAX_RATIO}:1 넘음'].append(f'{w}×{h} {img}')


def page_summary(body):
    """(title, 본문 글자 수) — 자바스크립트를 실행하지 않은 HTML 기준, 공백 제외"""
    t = body.decode('utf-8', 'replace')
    tl = re.search(r'<title[^>]*>(.*?)</title>', t, re.S)
    m = re.search(r'<body[^>]*>(.*)', t, re.S | re.I)
    text = m.group(1) if m else t
    text = re.sub(r'<(script|style|noscript|template|svg)\b.*?</\1>', ' ', text, flags=re.S | re.I)
    text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
    return (html.unescape(tl.group(1)).strip() if tl else ''), len(re.sub(r'\s+', '', text))


def dom_facts(t):
    """HTML 글 → 검색에 중요한 값. 렌더링 전·후를 같은 방법으로 읽어 비교한다"""
    head = t.split('</head>')[0]
    tl = re.search(r'<title[^>]*>(.*?)</title>', head, re.S)
    c = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]*)"', head)
    r = re.search(r'<meta[^>]*name="robots"[^>]*content="([^"]*)"', head)
    _, text_len = page_summary(t.encode())
    return {
        'title': html.unescape(tl.group(1)).strip() if tl else '',
        'canonical': c.group(1) if c else '',
        'robots': (r.group(1) if r else '').replace(' ', '').lower(),
        'h1': len(re.findall(r'<h1[\s>]', t)),
        'text': text_len,
    }


def find_chrome():
    """설치된 Chrome 계열 브라우저 경로(없으면 None) — 내려받지 않는다"""
    names = [
        os.environ.get('CHROME_PATH'),
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    ] + [shutil.which(n) for n in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'microsoft-edge')]
    return next((n for n in names if n and os.path.exists(n)), None)


def render(chrome, url, profile):
    """자바스크립트를 실행한 뒤의 DOM — Yeti 이름으로 요청해 실행 전 HTML 과 조건을 맞춘다. 실패하면 None"""
    cmd = [chrome, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--mute-audio',
           f'--user-data-dir={profile}', f'--user-agent={UA}', '--virtual-time-budget=5000', '--dump-dom', url]
    try:
        # close_fds=False → posix_spawn. macOS 에서 urllib 이 프록시 설정(_scproxy, Objective-C)을 읽은 뒤 fork 하면
        # 자식이 exec 전에 죽는다(Chrome 종료 코드 -11) — 2026-11-24 확인
        r = subprocess.run(cmd, capture_output=True, timeout=60, close_fds=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = r.stdout.decode('utf-8', 'replace')
    return out if '<html' in out.lower() else None


def compare_render(url, body, issues, chrome, profile):
    """렌더링 전(검색로봇이 처음 받는 HTML)과 후(JS 실행)의 차이"""
    dom = render(chrome, url, profile)
    if dom is None:
        issues['렌더링 실패(Chrome 이 DOM 을 주지 않음)'].append(url)
        return
    raw, done = dom_facts(body.decode('utf-8', 'replace')), dom_facts(dom)
    if raw['title'] != done['title']:
        issues['JS 가 title 을 바꿈(렌더링 전 제목이 검색 결과에 쓰일 수 있음)'].append(
            f'"{raw["title"][:30]}" → "{done["title"][:30]}" {url}')
    if raw['canonical'] != done['canonical']:
        issues['JS 가 canonical 을 바꿈(구글: JS 로 canonical 을 바꾸지 말 것)'].append(
            f'{raw["canonical"] or "없음"} → {done["canonical"] or "없음"} {url}')
    if raw['robots'] != done['robots']:
        issues['JS 가 robots meta 를 바꿈(구글: 렌더링 전 noindex 면 렌더링하지 않음)'].append(
            f'"{raw["robots"] or "없음"}" → "{done["robots"] or "없음"}" {url}')
    if raw['h1'] == 0 and done['h1'] > 0:
        issues['h1 이 JS 를 실행해야만 생김'].append(url)
    if done['text'] >= JS_ONLY_TEXT and raw['text'] < done['text'] * (1 - UA_TEXT_DIFF):
        issues['본문 대부분이 JS 를 실행해야만 생김(서버 렌더링·정적 생성 권장)'].append(
            f'실행 전 {raw["text"]}자 · 후 {done["text"]}자 {url}')


# Core Web Vitals "좋음" 기준(구글, 75번째 백분위) — CrUX 지표 이름: (화면 이름, 기준, 단위)
CWV = {
    'largest_contentful_paint': ('LCP', 2500, 'ms'),
    'interaction_to_next_paint': ('INP', 200, 'ms'),
    'cumulative_layout_shift': ('CLS', 0.1, ''),
}


def crux(origin, key, issues):
    """실제 Chrome 사용자 기록(CrUX) — 실험실 측정이 아니라 순위에 쓰이는 값에 가깝다. 출력할 줄을 돌려준다"""
    body = json.dumps({'origin': origin, 'metrics': list(CWV)}).encode()
    req = urllib.request.Request(
        f'https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={key}',
        data=body, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            record = json.load(r)['record']
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 'CrUX: 데이터 없음(방문이 적으면 집계되지 않음 — PageSpeed Insights 실험실 값으로 대신 본다)'
        return f'CrUX: 요청 실패 {e.code} (API 키·Chrome UX Report API 사용 설정 확인)'
    except Exception as e:  # 연결 오류
        return f'CrUX: 요청 실패 {e}'
    parts = []
    for metric, (name, limit, unit) in CWV.items():
        p75 = record.get('metrics', {}).get(metric, {}).get('percentiles', {}).get('p75')
        if p75 is None:
            parts.append(f'{name} 없음')
            continue
        value = float(p75)
        parts.append(f'{name} {p75}{unit}')
        if value > limit:
            issues[f'Core Web Vitals {name} 이 "좋음" 기준({limit}{unit}) 넘음 — 실제 사용자 75%'].append(f'{p75}{unit} {origin}')
    return 'CrUX(최근 28일, 모든 기기, 75%): ' + ' · '.join(parts)


def compare_browser(url, status, body, issues):
    """Yeti 와 일반 브라우저에 같은 내용을 주는지 — 다르면 클로킹으로 보일 수 있다(네이버·구글 스팸 정책)"""
    b_status, _, b_body = get(url, ua=BROWSER_UA)
    if b_status != status:
        issues['Yeti·브라우저 상태가 다름(클로킹으로 보일 수 있음)'].append(f'Yeti {status} · 브라우저 {b_status} {url}')
        return
    y_title, y_len = page_summary(body)
    b_title, b_len = page_summary(b_body)
    if y_title != b_title:
        issues['Yeti·브라우저 title 이 다름'].append(f'"{y_title[:30]}" · "{b_title[:30]}" {url}')
    if max(y_len, b_len) and abs(y_len - b_len) / max(y_len, b_len) > UA_TEXT_DIFF:
        issues['Yeti·브라우저 본문 글자 수가 크게 다름'].append(f'Yeti {y_len} · 브라우저 {b_len} {url}')


def sitemap_urls(url, depth=0):
    status, _, body = get(url)
    if status != 200 or depth > 2:
        return []
    text = body.decode('utf-8', 'replace')
    locs = re.findall(r'<loc>\s*(.*?)\s*</loc>', text)
    if '<sitemapindex' in text:
        return [u for loc in locs for u in sitemap_urls(loc, depth + 1)]
    return locs


def check_page(url, host, issues, titles, descs, ogimgs, is_home=False, compare=True, chrome=None, profile=None):
    status, _, body = get(url)
    if compare:
        compare_browser(url, status, body, issues)
    if status != 200:
        issues['상태 200 아님'].append(f'{status} {url}')
        return
    if chrome:
        compare_render(url, body, issues, chrome, profile)
    _, text_len = page_summary(body)
    if text_len < JS_ONLY_TEXT:
        issues[f'JS 없이 본문 글자 {JS_ONLY_TEXT}자 미만(화면을 자바스크립트로만 그리는지 확인 — 그렇다면 서버 렌더링 권장)'].append(
            f'{text_len}자 {url}'
        )
    t = body.decode('utf-8', 'replace')
    head = t.split('</head>')[0]
    tl = re.findall(r'<title[^>]*>(.*?)</title>', head, re.S)
    if len(tl) != 1:
        issues['<head> 의 title 이 1개가 아님'].append(f'{len(tl)} {url}')
    title = html.unescape(tl[0]).strip() if tl else ''
    titles[title].append(url)
    if len(title) > TITLE_MAX:
        issues[f'title {TITLE_MAX}자 초과'].append(f'{len(title)}자 {url}')
    m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', head, re.S)
    desc = html.unescape(m.group(1)).strip() if m else ''
    if not desc:
        issues['description 없음'].append(url)
    else:
        descs[desc].append(url)
        if len(desc) > DESC_MAX:
            issues[f'description {DESC_MAX}자 초과'].append(f'{len(desc)}자 {url}')
        if desc == title:
            issues['description 이 title 과 같음'].append(url)
    h1 = len(re.findall(r'<h1[\s>]', t))
    if h1 != 1:
        issues['h1 이 1개가 아님(JS 로 그리는 쪽이면 무시)'].append(f'{h1} {url}')
    c = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]*)"', head)
    if not c:
        issues['canonical 없음'].append(url)
    elif not c.group(1).startswith('http'):
        issues['canonical 이 상대 주소'].append(url)
    elif c.group(1).rstrip('/') != url.rstrip('/'):
        issues['canonical 이 다른 주소(의도한 것인지 확인)'].append(f'{url} → {c.group(1)}')
    for p in ('og:type', 'og:title', 'og:description', 'og:image', 'og:url'):
        if f'property="{p}"' not in head:
            issues[f'{p} 없음'].append(url)
    oi = re.search(r'property="og:image"[^>]*content="([^"]*)"', head)
    if oi:
        ogimgs[oi.group(1)] += 1
    if 'name="viewport"' not in head:
        issues['viewport 없음'].append(url)
    if not re.search(r'<meta[^>]*charset="?utf-8', head, re.I):
        issues['utf-8 charset 없음'].append(url)
    if re.search(r'name="robots"[^>]*content="[^"]*no(index|follow)', head):
        issues['robots noindex/nofollow(의도한 것인지 확인)'].append(url)
    icons = re.findall(r'<link[^>]*rel="(shortcut icon|icon|apple-touch-icon[^"]*)"[^>]*href="([^"]*)"', head)
    if any(not href.startswith('http') for _, href in icons):
        issues['파비콘 href 가 상대 주소'].append(url)
    if any(n > 1 for n in collections.Counter(r for r, _ in icons).values()):
        issues['같은 rel 의 파비콘이 여러 개'].append(url)
    # 구글은 호스트마다 첫 화면의 파비콘만 쓴다 — 다른 쪽(예: /storybook/)의 SVG 는 검사하지 않는다
    if is_home and icons and all(href.split('?')[0].lower().endswith('.svg') for _, href in icons):
        issues['첫 화면 파비콘이 SVG 뿐(구글 형식 목록에 없음 — PNG·ICO 48px 넘게)'].append(url)
    if len(body) > 2 * 1024 * 1024:
        issues['HTML 2MB 초과(Googlebot 은 앞 2MB 만 읽음)'].append(f'{len(body)} {url}')
    if any(not re.search(r'\balt=', i) for i in re.findall(r'<img\b[^>]*>', t)):
        issues['alt 없는 img'].append(url)
    if re.search(r'href="javascript:', t):
        issues['javascript: 링크'].append(url)
    if re.search(r'(?:href|src)="http://' + re.escape(host), t):
        issues['같은 호스트 http 링크(https 로)'].append(url)
    has_website = [False]
    for block in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            issues['JSON-LD 파싱 실패'].append(url)
            continue
        for obj in data if isinstance(data, list) else data.get('@graph', [data]):
            if isinstance(obj, dict) and obj.get('@type') == 'WebSite' and obj.get('name'):
                has_website[0] = True
            if isinstance(obj, dict) and obj.get('@type') == 'BreadcrumbList':
                for el in obj.get('itemListElement', []):
                    name = el.get('name') or (el.get('item') or {}).get('name') or ''
                    if name.strip().lower() in GENERIC_CRUMBS:
                        issues['BreadcrumbList 이름이 일반 낱말("홈" 등)'].append(f'"{name}" {url}')
                        break
    if is_home and not has_website[0]:
        issues['첫 화면에 WebSite JSON-LD(name) 없음 — 구글 사이트 이름'].append(url)


def main():
    ap = argparse.ArgumentParser(description='네이버 웹마스터 가이드 기준 사이트 점검')
    ap.add_argument('origin', help='https://example.com (끝 / 없이)')
    ap.add_argument('--limit', type=int, default=500, help='사이트맵에서 검사할 최대 쪽 수')
    ap.add_argument('--no-compare', action='store_true', help='일반 브라우저 이름으로 다시 요청해 비교하지 않음(요청 절반)')
    ap.add_argument('--render', action='store_true', help='시스템 Chrome 으로 JS 를 실행한 뒤의 DOM 과 비교(쪽마다 몇 초)')
    args = ap.parse_args()
    origin = args.origin.rstrip('/')
    host = origin.split('//', 1)[1]
    bare = host[4:] if host.startswith('www.') else host

    print(f'# {origin} (User-Agent: Yeti)\n')
    s, h, b = get(origin + '/robots.txt')
    robots = b.decode('utf-8', 'replace') if s == 200 else ''
    print(f'robots.txt: {s} {h.get("Content-Type", "")}')
    print('  Disallow:', [l.strip() for l in robots.splitlines() if l.lower().startswith('disallow')])
    sitemaps = [l.split(':', 1)[1].strip() for l in robots.splitlines() if l.lower().startswith('sitemap')]
    print('  Sitemap:', sitemaps or '없음 — robots.txt 에 Sitemap: 줄을 넣거나 웹마스터도구에 제출')
    for pre in (f'http://{host}/', f'http://www.{bare}/', f'https://www.{bare}/', f'https://{bare}/'):
        if pre.rstrip('/') == origin:
            continue
        s, h, _ = get(pre)
        print(f'redirect {pre} → {s} {h.get("Location", "")}')
    s, _, _ = get(origin + '/__naver_seo_check_404__/')
    print(f'없는 주소: {s}' + ('' if s == 404 else '  ← 404 가 아니면 소프트 404'))
    s, _, _ = get(origin + '/favicon.ico')
    print(f'/favicon.ico: {s}')

    urls = []
    for sm in sitemaps or [origin + '/sitemap.xml']:
        urls += sitemap_urls(sm)
    other = [u for u in urls if not u.startswith(origin)]
    print(f'\n사이트맵 {len(urls)}쪽' + (f', 다른 호스트 {len(other)}개(제출 거부됨): {other[:3]}' if other else ''))
    chrome = find_chrome() if args.render else None
    if args.render and not chrome:
        print('--render: Chrome·Edge·Chromium 을 찾지 못해 건너뜀(CHROME_PATH 로 지정)')
    profile = tempfile.mkdtemp(prefix='korean-seo-chrome-') if chrome else None
    issues = collections.defaultdict(list)
    titles, descs, ogimgs = collections.defaultdict(list), collections.defaultdict(list), collections.Counter()
    for u in urls[: args.limit]:
        check_page(u, host, issues, titles, descs, ogimgs, is_home=u.rstrip('/') == origin, compare=not args.no_compare,
                   chrome=chrome, profile=profile)
    if profile:
        shutil.rmtree(profile, ignore_errors=True)
    for img in ogimgs:
        check_og_image(img, issues)
    for t, us in titles.items():
        if len(us) > 1:
            issues['같은 title 을 쓰는 쪽'].append(f'{len(us)}쪽 "{t[:40]}"')
    for d, us in descs.items():
        if len(us) > 1:
            issues['같은 description 을 쓰는 쪽'].append(f'{len(us)}쪽 "{d[:40]}"')
    shared = [(img, n) for img, n in ogimgs.items() if n > 1]
    if shared:
        issues['og:image 를 여러 쪽이 같이 씀(대표 이미지로 안 쓰일 수 있음)'].extend(f'{n}쪽 {img}' for img, n in shared)

    key = os.environ.get('CRUX_API_KEY')
    if key:
        print(crux(origin, key, issues))
    print(f'검사한 쪽 {min(len(urls), args.limit)}, og:image {len(ogimgs)}개' + (' (렌더링 비교 함)' if chrome else '') + '\n')
    if not issues:
        print('✓ 발견된 문제 없음')
        return 0
    for k, v in issues.items():
        print(f'- {k}: {len(v)}')
        for item in v[:5]:
            print(f'    {item}')
        if len(v) > 5:
            print(f'    … 외 {len(v) - 5}')
    return 1


if __name__ == '__main__':
    sys.exit(main())
