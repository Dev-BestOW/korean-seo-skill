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
  JSON-LD 파싱·BreadcrumbList 이름("홈"·"top" 같은 일반 낱말)
- 사이트 전체: 중복 제목·설명, og:image 를 몇 쪽이 같이 쓰는지
표준 라이브러리만 쓴다(설치 없음).
"""
import argparse
import collections
import html
import json
import re
import sys
import urllib.error
import urllib.request

UA = 'Mozilla/5.0 (compatible; Yeti/1.1; +https://naver.me/spd)'
TITLE_MAX, DESC_MAX = 40, 80
GENERIC_CRUMBS = {'홈', 'home', 'top', '메인', 'main'}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with OPENER.open(req, timeout=20) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:  # DNS·연결 오류
        return 0, {}, str(e).encode()


def sitemap_urls(url, depth=0):
    status, _, body = get(url)
    if status != 200 or depth > 2:
        return []
    text = body.decode('utf-8', 'replace')
    locs = re.findall(r'<loc>\s*(.*?)\s*</loc>', text)
    if '<sitemapindex' in text:
        return [u for loc in locs for u in sitemap_urls(loc, depth + 1)]
    return locs


def check_page(url, host, issues, titles, descs, ogimgs):
    status, _, body = get(url)
    if status != 200:
        issues['상태 200 아님'].append(f'{status} {url}')
        return
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
    if any(not re.search(r'\balt=', i) for i in re.findall(r'<img\b[^>]*>', t)):
        issues['alt 없는 img'].append(url)
    if re.search(r'href="javascript:', t):
        issues['javascript: 링크'].append(url)
    if re.search(r'(?:href|src)="http://' + re.escape(host), t):
        issues['같은 호스트 http 링크(https 로)'].append(url)
    for block in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            issues['JSON-LD 파싱 실패'].append(url)
            continue
        for obj in data if isinstance(data, list) else data.get('@graph', [data]):
            if isinstance(obj, dict) and obj.get('@type') == 'BreadcrumbList':
                for el in obj.get('itemListElement', []):
                    name = el.get('name') or (el.get('item') or {}).get('name') or ''
                    if name.strip().lower() in GENERIC_CRUMBS:
                        issues['BreadcrumbList 이름이 일반 낱말("홈" 등)'].append(f'"{name}" {url}')
                        break


def main():
    ap = argparse.ArgumentParser(description='네이버 웹마스터 가이드 기준 사이트 점검')
    ap.add_argument('origin', help='https://example.com (끝 / 없이)')
    ap.add_argument('--limit', type=int, default=500, help='사이트맵에서 검사할 최대 쪽 수')
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
    issues = collections.defaultdict(list)
    titles, descs, ogimgs = collections.defaultdict(list), collections.defaultdict(list), collections.Counter()
    for u in urls[: args.limit]:
        check_page(u, host, issues, titles, descs, ogimgs)
    for t, us in titles.items():
        if len(us) > 1:
            issues['같은 title 을 쓰는 쪽'].append(f'{len(us)}쪽 "{t[:40]}"')
    for d, us in descs.items():
        if len(us) > 1:
            issues['같은 description 을 쓰는 쪽'].append(f'{len(us)}쪽 "{d[:40]}"')
    shared = [(img, n) for img, n in ogimgs.items() if n > 1]
    if shared:
        issues['og:image 를 여러 쪽이 같이 씀(대표 이미지로 안 쓰일 수 있음)'].extend(f'{n}쪽 {img}' for img, n in shared)

    print(f'검사한 쪽 {min(len(urls), args.limit)}\n')
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
