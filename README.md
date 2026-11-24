# korean-seo-skill

> A Claude Code skill that checks web pages, sitemaps, RSS feeds and blog post titles against the Naver Search Advisor webmaster guide and Google Search Central (docs in Korean).

**네이버와 구글 검색에 잘 걸리는 웹 페이지·블로그 글을 만들도록 돕는 Claude Code 스킬이에요.**
네이버 서치어드바이저 웹마스터 가이드(54개 문서)와 구글 Search Central(핵심 44쪽 정독, 2026-11-20 기준)에서 실제 판단에 쓰이는 기준만 추려 점검표로 만들고, 숫자로 셀 수 있는 것은 스크립트로 검사해요.

- **숫자 기준:** 제목 40자·설명 80자, og:image 150×150·5,000 byte·3:1, 파비콘 정사각형 32px 권장·절대 경로, RSS 본문 전체·10MB, 사이트맵 5만 URL·10MB
- **네이버만의 규칙:** 이동 경로(BreadcrumbList)에 "홈" 같은 일반 낱말 금지, 파비콘 같은 rel 하나, `#` 조각 주소는 버려짐, 연관 채널로 인식하는 서비스 목록
- **구글이 다른 점:** 파비콘 형식(구글 목록에 SVG 없음 — PNG·ICO 48px 넘게), 첫 화면 `WebSite` JSON-LD 로 사이트 이름, 보이는 날짜와 `dateModified`·`lastmod` 는 실제로 고쳤을 때만, AI 개요는 일반 SEO 와 같음(llms.txt·글 조각내기 불필요), Googlebot 은 HTML 앞 2MB 만, Core Web Vitals 기준
- **네이버 AI 브리핑:** 공식으로 알려진 것(보도자료·웹마스터 가이드)과 업계 관찰을 구분해요. 출처 선정 기준은 공개되지 않았고, `nosourceinfo` 는 AI 출처설명을 끄는 명령이지 AI 브리핑을 끄는 방법이 아니라고 안내해요
- **불이익을 피하는 법:** 키워드 반복·낚시성 제목·검색만을 위한 잦은 제목 변경 — "키워드 다 넣어 줘" 같은 요청에도 기준 안의 제목과 나머지 키워드를 둘 곳을 제안
- **검사 도구:** 배포된 사이트를 네이버 검색로봇(Yeti) 이름으로 점검하고 구글 항목(SVG 파비콘·사이트 이름·2MB)도 함께 확인, og:image 파일의 실제 크기·용량·비율을 재고, 일반 브라우저로 받은 응답과 비교해 클로킹·자바스크립트로만 그리는 쪽을 찾아요(`check-site.py`). 설치된 Chrome 이 있으면 `--render` 로 자바스크립트 실행 전·후의 title·canonical·robots·h1·본문을 비교하고, `CRUX_API_KEY` 가 있으면 실제 사용자 Core Web Vitals(LCP·INP·CLS)도 봐요, 마크다운 글 제목·설명 검사(`check-meta.mjs`) — 둘 다 설치할 것 없음

## 설치

### Claude Code (플러그인 마켓플레이스)

```
/plugin marketplace add Dev-BestOW/korean-seo-skill
/plugin install korean-seo@korean-seo-skill
```

**두 줄 모두 실행해야 해요.** 첫 줄은 이 저장소를 마켓플레이스로 **등록**만 하고(한 번만), 둘째 줄이 플러그인을 **설치**해요. 첫 줄만 하면 스킬이 켜지지 않아요.
설치한 뒤 `/reload-plugins` 를 실행하거나 Claude Code 를 다시 열면 바로 쓸 수 있어요. 새 버전은 `/plugin update korean-seo@korean-seo-skill` 로 받아요.
명령 대신 `/plugin` 메뉴에서 Marketplaces › korean-seo-skill › korean-seo › Install 을 골라도 같아요.

설치하면 웹 페이지 메타·사이트맵·RSS·블로그 제목을 다룰 때 스킬이 저절로 켜져요. 직접 부르려면 "korean-seo 스킬로 점검해 줘".

### 다른 도구(Agent Skills 형식)

`skills/korean-seo` 폴더를 쓰는 도구의 스킬 폴더에 복사하세요. 예: Claude Code 개인 스킬 `~/.claude/skills/korean-seo`, Codex·Gemini CLI 등 `~/.agents/skills/korean-seo`.

### 0.2.0 이하(`naver-seo`)를 설치했다면

0.3.0 부터 이름이 `korean-seo` 로 바뀌었어요(구글까지 다루게 되어서). 옛 것을 지우고 새로 설치해 주세요.

```
/plugin uninstall naver-seo@naver-seo-skill
/plugin marketplace remove naver-seo-skill
/plugin marketplace add Dev-BestOW/korean-seo-skill
/plugin install korean-seo@korean-seo-skill
```

## 검사 도구만 쓰기

```bash
# 배포된 사이트 — robots.txt·301·404·사이트맵의 모든 쪽(title·description·canonical·OG·파비콘·h1·alt·JSON-LD 이동 경로)
# + og:image 크기(150×150 초과)·용량(5,000 byte)·비율(3:1), Yeti·일반 브라우저 응답 비교, JS 없이 본문이 비는 쪽
python3 skills/korean-seo/scripts/check-site.py https://example.com   # --no-compare 로 브라우저 비교 끄기(요청 절반)

# 자바스크립트 실행 전·후 비교 — 설치된 Chrome·Edge·Chromium 을 헤드리스로 띄운다(내려받지 않음, 경로는 CHROME_PATH 로 지정 가능).
# JS 가 title·canonical·robots 를 바꾸는지, h1·본문이 JS 를 실행해야만 생기는지. 쪽마다 1~4초
python3 skills/korean-seo/scripts/check-site.py https://example.com --render --no-compare

# 실제 사용자 Core Web Vitals(Chrome UX Report, 최근 28일 75%) — Google Cloud 에서 Chrome UX Report API 를 켜고 키를 만든다.
# 방문이 적은 사이트는 "데이터 없음"(정상)
CRUX_API_KEY=… python3 skills/korean-seo/scripts/check-site.py https://example.com

# 마크다운 글 프론트매터(title·description) — 길이 초과면 exit 1(CI 에 넣을 수 있음), 낱말 반복은 경고
node skills/korean-seo/scripts/check-meta.mjs src/content/posts
```

Python 3.8+, Node 18+ 표준 라이브러리만 써요.

## 무엇이 달라지나

같은 요청을 스킬 없이·있이 각각 두 번씩 시켜 본 결과예요(2026-11-20, 빈 폴더에서 `claude -p`).

| 요청 | 스킬 없이 | 스킬 있이 |
|---|---|---|
| 새 문서 쪽 head·JSON-LD 만들기 | 설명 87·105자, 이동 경로 "홈", 파비콘 상대 경로·`rel="icon"` 두 개 | 제목 28·31자, 설명 60·73자, 이동 경로 첫 이름은 사이트 이름, 파비콘 절대 경로·rel 하나, 글자 수 점검표 첨부 |
| 블로그 글 제목·설명 정하기 | 제목 48·53자, 설명 139·151자 | 제목 37·38자, 설명 72·78자, 검색어("자바스크립트 깊은 복사")를 앞에 |
| "키워드 다 넣어서 제목 다시 바꿔 줘" | 잦은 변경은 경고했지만 53·54자 키워드 나열 제목을 줌 | 33·36자 제목에 키워드 1~2개, 나머지는 설명·소제목에 한 번씩, 리포트를 보고 바꾸자고 안내 |

| (0.2.0) 첫 화면 파비콘·사이트 이름 정하기 | "구글·네이버 모두 SVG 지원"이라며 SVG 하나로 충분하다고 함 | PNG(96×96)·ICO 로 바꾸고 첫 화면 `WebSite` JSON-LD 로 사이트 이름 지정 |
| (0.2.0) "날짜만 오늘로 바꿔 최신 글처럼" | 스킬 없이도 거절 | 거절 + 실제로 고친 글만 날짜가 바뀌게 하는 방법 |
| (0.5.1) Storybook `iframe.html?id=…` 가 "표준 없는 중복 페이지"로 뜸 | `noindex` 만(3번 모두 `indexifembedded` 없음) | `noindex, indexifembedded` 3번 모두 |

글자 수는 모델이 적은 값이 아니라 결과를 따로 센 값이에요.

### 직접 다시 재 보기

위 요청과 검사는 [`evals/evals.json`](evals/evals.json)에 있어요. 스킬을 고친 뒤 같은 조건으로 다시 잴 수 있어요.

```bash
node evals/run.mjs                        # 경우 7개 × 스킬 없이·있이 × 1번 (claude -p 14번 — 사용량이 들어요)
node evals/run.mjs --runs 3 --only ai-briefing --model sonnet
```

빈 임시 폴더에서 `--setting-sources project` 로 설치한 플러그인을 읽지 않고, "있이" 는 `--plugin-dir` 로 이 저장소의 스킬만 켜요. 검사는 정규식·글자 수뿐이라 채점 모델이 없어요. 답 전문은 `evals/results/` 에 남아요(커밋 안 함).
0.5.0 결과(2026-11-20, 기본 모델, 경우마다 3번): 검사 18개 × 3번 = 54개 중 **스킬 없이 30개(한 번에 9~11개), 있이 54개** 통과. 없이는 3번 모두 설명 110~167자, 키워드를 나열한 64~79자 제목("복사" 반복), SVG 파비콘·상대 경로 그대로, 문서 쪽에 파비콘 없음이었고, 이동 경로 "홈"은 3번 중 1번, AI 브리핑 출처 기준이 공개되지 않았다는 말은 3번 중 1번만 했어요. 날짜만 바꾸기 거절·canonical 절대 주소·리포트 안내는 스킬 없이도 늘 통과해서 차이를 가르지 못해요.
0.5.1(2026-11-23): 새 경우 `embed-noindex` 3번 — `indexifembedded` 스킬 없이 0/3·있이 3/3. 기존 6경우 18검사는 있이 1번 모두 통과(회귀 없음).
0.6.0(2026-11-24, **haiku**, 경우마다 3번): 0.5.1 그대로는 스킬 없이 30/60·있이 54/60 이었는데, 있이에서 떨어진 곳은 모델이 **스킬을 부르지 않은 답**과 겹쳤어요
(파비콘 1/3·Storybook iframe 0/3 호출 — "한국어 사이트" 라는 말이 없고 태그 하나만 달라는 요청). description 을 "네이버·구글 검색에 나와야 하는 사이트(.kr·한국어 특히), 태그 하나만 답할 때도"·
noindex·dateModified/lastmod 로 넓힌 뒤 **있이 58/60, 스킬 호출 20/21**. 기본 모델 1번은 20/20·호출 7/7(회귀 없음). 평가 표에 "(스킬을 부른 횟수)" 줄이 생겨 —
점수가 떨어지면 먼저 이 줄을 봐요. 낮으면 본문이 아니라 description 문제예요.
새 기준을 더하면 그 기준을 어기기 쉬운 요청과 검사를 `evals.json` 에 함께 더해 주세요.

## 주의

- **네이버·구글 공식 도구가 아니며 두 회사와 관계가 없어요.** 원문은 [네이버 웹마스터 가이드](https://searchadvisor.naver.com/guide)와 [Google Search Central](https://developers.google.com/search/docs?hl=ko)에 있고, 이 저장소의 요약은 원문을 옮긴 것이 아니라 기준만 정리한 거예요.
- 가이드는 바뀔 수 있어요. 중요한 판단은 원문을 다시 확인하세요(`skills/korean-seo/reference.md`·`google-reference.md` 에 문서별 주소).
- 기준을 지켜도 노출·순위가 보장되지는 않아요. 콘텐츠 품질과 외부 링크가 더 중요해요.

## 기여

가이드가 바뀌었거나 빠진 기준이 있으면 이슈·PR 을 보내 주세요. 기준을 고칠 때는 원문 문서 주소를 함께 적어 주세요.

## 라이선스

MIT
