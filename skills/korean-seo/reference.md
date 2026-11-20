# 네이버 웹마스터 가이드 요약 (2026-11-20 기준)

원문: https://searchadvisor.naver.com/guide — 아래는 문서마다 판단에 쓰이는 기준만 우리 말로 요약한 것이다(원문을 옮긴 것이 아니다). 이 저장소는 네이버와 관계가 없다.
문서 주소는 `https://searchadvisor.naver.com/guide/<id>` 형식이다.

## 검색엔진 최적화 기초

| 문서 (id) | 요점 |
|---|---|
| 최적화의 목적 (`seo-basic-intro`) | 10단계: 웹마스터도구 등록·소유 확인(호스트 단위) → robots 로 Yeti 허용 → 중복 콘텐츠·같은 제목 피하기 → 사이트맵·RSS 제출 → 연관 채널 → `site:` 로 반영 확인(방문 뒤 최대 1주) → noindex·frame·JS 렌더링·JS 리다이렉트 점검 → 링크는 표준 `<a href>` |
| 웹 사이트를 만들 때 (`seo-basic-create`) | 같은 내용은 호스트·URL 하나, 여러 주소면 대표 주소로 301(어려우면 canonical). 호스트 이름에 밑줄 금지. robots.txt 는 루트, 사이트맵 위치 기록. 오류 쪽은 의미 있는 상태 코드(404·403·503), 200 금지. 반응형 권장 |
| robots.txt (`seo-basic-robots`) | 루트·`text/plain`. 2xx 는 규칙 해석, 3xx 는 5번까지 따라감, 4xx 는 모두 허용, 5xx 는 모두 금지(이전 규칙이 있으면 잠시 사용). 규칙은 같은 호스트·프로토콜·포트에만 적용. 파비콘·JS·CSS 경로는 막지 않는다 |
| 웹 페이지의 이동 (`seo-basic-redirect`) | JS 리다이렉트 자제(스팸으로 저평가 가능), 영구 이동 301, 일시 이동 302, 연속 5번 넘기지 않기, 거쳐 가는 주소와 최종 주소 모두 수집 가능해야. 잠시 막을 땐 robots 대신 웹마스터도구 트래픽 제한 |
| 웹 사이트 이전 (`seo-basic-migration`) | 옛 URL 을 새 URL 로 1:1 301, 새 사이트 모든 쪽에 canonical, 새 사이트 등록·사이트맵 제출. 이전이 끝나기 전에 옛 사이트를 robots 로 막거나 끄지 않는다 |
| 운영을 그만둘 때 (`seo-basic-close`) | 1개월 이상 종료 공지, 쓰기 권한 회수. 만료 도메인은 남이 사서 악용할 수 있다 |
| 검색로봇 확인 (`seo-basic-firewall`) | User-Agent `Yeti/1.1`(+https://naver.me/spd), 광고용 `Ads-Naver`, 링크 미리보기 `Blueno`. 진짜인지는 역 DNS(`*.naver.com`) 확인. IP 로 차단하지 말 것 |
| HTTP 규약 (`seo-basic-http`) | 301/302/303/307/308, 400/401/403/404, 500/503 의 뜻 |

## 검색엔진 최적화 고급

| 문서 (id) | 요점 |
|---|---|
| 자바스크립트 최적화 (`seo-advanced-javascript`) | SPA 도 지원하지만 주요 영역은 서버 렌더링 권장. JS·CSS 수집 허용. `#`·`#!` 조각 주소는 버려지므로 독립 콘텐츠는 고유 경로로. JS 파일 주소에 타임스탬프·해시를 강제로 붙이면 해석에 문제가 생길 수 있다 |
| 검색 친화적인 URL (`seo-advanced-url`) | https, 고유 도메인(호스팅 기본 도메인보다), 읽기 쉬운 경로, 파라미터 최소화. 링크는 정적 마크업, 세션·쿠키에 따라 바뀌는 링크 금지 |
| 색인 효율성 (`seo-advanced-indexing`) | 내용 없는 HTML(JS 로만 이동), 소프트 404 는 색인 제외. 자료 없음 404, 로그인 필요 403, 이전 301, 점검·만료 503 |
| SEO 기본 가이드 (`seo-help`) | title 없음·2개 이상·여러 쪽 동일·너무 김, description 없음·동일, h1 2개 이상, alt 없음 — 각각 SEO 진단 항목 |
| 리소스와 링크 (`resource-and-link`) | 렌더링에 필요한 리소스가 robots·IP 로 막히면 불완전하게 해석. `href` 에 JS 호출 금지. 같은 호스트인데 다른 프로토콜(http) 링크는 https 로 |

## 콘텐츠 가이드라인

| 문서 (id) | 요점 |
|---|---|
| 웹 콘텐츠 스팸사례 (`content-abusing`) | 클로킹, 부적절한 리다이렉트, 링크 스팸, 백링크·만료 도메인 악용, 조작, 해킹 콘텐츠, 숨긴 텍스트, **키워드 반복·남용**, **낚시성(제목·설명과 내용 불일치)**, 저품질 대량 생성(AI 사용 자체가 기준은 아님), 스크래핑, 유해·피싱·유사 공공사이트 |
| 콘텐츠 작성 권장 (`content-basic`) | 독특한 브랜드 URL, 간결한 제목·설명(무관한 인기 검색어·반복 금지), 중요한 정보는 텍스트로. 5원칙: 전문성·경험, 일관된 주제(절반 이상 핵심 주제), 진정성·출처 링크(AI 결과는 운영자 관점을 더해서), 읽기 쉬운 구조, 꾸준한 관리·최신 정보·낚시성 썸네일 금지 |

## HTML 마크업

| 문서 (id) | 요점 |
|---|---|
| 선호 URL·로봇 메타 (`markup-structure`) | canonical 은 절대 경로. 메인 쪽은 301 권장. robots 메타 `noindex`·`nofollow`, 네이버 전용 `nosourceinfo`(AI 출처 설명 제외). 리다이렉트만 하는 쪽은 메타가 반영 안 될 수 있음 |
| 콘텐츠 마크업 (`markup-content`) | 메인 title 은 브랜드명, 개별 쪽은 내용 설명. 검색만을 위한 잦은 제목 변경·지나치게 긴 제목·2회 이상 반복 키워드는 불이익. description 1~2문장, 본문 복사·제목과 동일·모든 쪽 동일·키워드 나열 금지. OG 함께 기입. og:image 150×150 초과·5,000 byte 이상·3:1 이내·쪽마다 고유 |
| 모바일 사용성 (`markup-mobile`) | `viewport` 반응형 권장. 별도 모바일 사이트면 canonical 로 데스크톱 주소 지정, 기기별 리다이렉트는 HTTP 로 |
| 파비콘 (`markup-favicon`) | 정사각형 16px 이상(32px 권장), ICO·PNG·GIF·APNG·JPEG·SVG, href 절대 경로, rel 은 shortcut icon·icon·apple-touch-icon(-precomposed), 같은 rel 하나, URL 자주 바꾸지 않기 |

## 웹사이트 검색연동·검증·리포트

| 문서 (id) | 요점 |
|---|---|
| 수집요청·검색제외 (`request-crawl`) | 수집 요청은 우선순위에 따라 1일~몇 주, 매일 반복 요청 불필요, 노출 보장 아님. 제외는 원본 삭제(404) 뒤 요청 |
| RSS·사이트맵 제출 (`request-feed`) | RSS 는 최신 글 **본문 전체**, 같은 도메인, item 1개 이상, 10MB 미만, 느리면 제출 제한. 사이트맵은 모든 URL, 5만 개·10MB 미만, 인덱스 사이트맵 가능 |
| 사이트 간단 체크 (`diagnose-site`) | 로봇 접근, robots, title·description(**제목 40자·설명 80자 권장**, 반복 단어·무관 키워드), noindex, RSS·사이트맵 제출, 꾸준한 관리 |
| URL 검사 (`url-inspection`) | 쪽별 수집·색인 여부, 메타, SEO 항목(반드시 수정/수정하면 좋음/유지) |
| 노출·클릭 리포트 (`report-expose-ctr`) | 웹 검색 영역만(VIEW·블로그 영역 제외), 업데이트 기준일이 1주 전 → 최근 7일은 실제로 2~3주 전 데이터, 90일 보관, 키워드·URL 상위 30 |
| 사이트 진단 (`report-diagnosis`) | 색인·수집제한·색인제외·SEO 분류, 최근 90일, URL 목록 2,000개까지 |
| 사이트 최적화 (`report-seo`) | 수집(로봇룰·사이트맵·RSS), 콘텐츠 관리(제목·설명), 사이트 구조(HTML 태그, 앵커 텍스트, alt), 활성화(콘텐츠 양·외부 평판 — 다른 사이트에서의 자연스러운 링크가 가장 중요) |
| 수집 현황 (`report-crawl-refine`) | 로봇 비허용·DNS·연결 실패·서버 오류·404·콘텐츠 오류·URL 오류·1분 넘는 다운로드·4MB 넘는 HTML |
| 사이트 상태 (`site-summary`) | 인증서 유효성, http→https 리다이렉트, 사이트맵 등록(robots.txt 의 Sitemap 줄도 인정) |

## 구조화된 데이터

| 문서 (id) | 요점 |
|---|---|
| 소개 (`structured-data-intro`) | schema.org, JSON-LD 또는 Microdata 권장, 마크업해도 노출 보장 없음 |
| 연관 채널 (`structured-data-channel`) | 루트 쪽에 Person/Organization + `name`·`url`·`sameAs`. 인식 채널 목록은 SKILL.md 참고 |
| 이동 경로 (`structured-data-breadcrumb`) | 쪽 계층을 키워드로, 넓은 → 좁은 순, **"top"·"홈" 같은 일반 낱말 금지**, 너무 긴 글·숫자·특수문자만으로 된 이름 금지 |
| 주소·캐러셀·평점·레시피·리뷰·식당·TV·영화·소프트웨어 (`structured-data-*`) | 타입별 필수 속성. 공통: 이미지는 원본·중복 없이, 1쪽에 대상 하나 |
| 동영상 (`structured-data-video`) | VideoObject + creator(Person), 채널 쪽 Person, 날짜는 초·시간대 포함 ISO-8601, 유료 영상만 offers. 제휴 신청 필요 |

## AI 브리핑 (웹마스터 가이드 밖 — 네이버 공식 발표)

웹마스터 가이드 54문서 목록에는 AI 브리핑 문서가 없고, 이 표에 id 를 적은 39문서 본문을 "AI·생성형·브리핑" 으로 찾아봤다(2026-11-20). AI 와 관련된 가이드 내용은 `markup-structure` 의 `nosourceinfo`(AI 로 만든 사이트 출처설명 끄기), `content-basic`(AI 로 쓴 글에 운영자 경험·관점 더하기), `content-abusing`(템플릿 대량 발행 — AI 사용 여부만으로는 판단 안 함), `report-seo`(사이트 최적화 등급은 AI 기반 평가, 랭킹의 간접 지표) 뿐이다.

| 자료 | 요점 |
|---|---|
| 보도자료 2025-03-24 (https://www.navercorp.com/media/pressReleasesDetail?seq=32374) | 27일 출시, 가입 없이 검색창에서. 요약 답변과 창작자·원본 콘텐츠 출처를 함께 보여 줌. 공식형·멀티출처형·숏텐츠형·플레이스형·쇼핑형. 정부·공공기관 질문은 공식 출처로 답하고 관련 쪽으로 연결. 블로그·카페·클립 등 콘텐츠 풀을 폭넓게 활용 |
| 네이버 스토리 2025-05-23 (https://www.navercorp.com/story/storyDetail?seq=32525) | 하이퍼클로바X 기반, 검색·숏텐츠·플레이스 등에 적용. 창작자 콘텐츠를 연결·인용하는 환경을 만들 계획 |

출처 선정 기준, 인용을 빼는 방법, 서치어드바이저의 AI 브리핑 유입 리포트는 공식 자료에서 찾지 못했다. 업계 글의 "인용되는 글의 조건"(문단 자립성·40자 직답 등)은 관찰이며 공식 기준이 아니다.

## 제휴 API·IndexNow

| 문서 (id) | 요점 |
|---|---|
| 수집요청 API (`crawl-request-api`) | 제휴 신청 + 소유 확인 필요, Bearer 토큰, 요청당 1,000 URL·2MB, 랜딩·대표 URL 로 |
| IndexNow (`indexnow-about`·`-api-key`·`-request`·`-faq`) | 키 파일(16진수·`-`, 8~128자)을 루트에 `<키>.txt` 로, `GET https://searchadvisor.naver.com/indexnow?url=…&key=…` 또는 POST 로 1만 URL 까지. 다른 검색엔진과 공유, 색인 보장 아님, 사이트맵·RSS 를 대체하지 않음, 도입 뒤 바뀐 URL 만 보냄 |

## FAQ

| 문서 (id) | 요점 |
|---|---|
| 제목·설명 갱신 (`faq-serpedit`) | 네이버가 직접 고치지 않는다 — 운영자가 고치면 수집 뒤 반영. 같은 제목·설명이 많거나 간결하지 않으면 앵커·본문에서 뽑아 쓴다. title·description 과 og 값이 다르면 색인 때 더 적합한 쪽을 고른다 |
| 웹 검색 미노출 (`faq-serpmissing`) | `site:` 로 색인 확인, robots·noindex·`X-Robots-Tag`·방화벽·리소스 차단·중복·품질 점검 |
| 웹 검색 제외 (`faq-serpremove`) | noindex 또는 404/403. robots 로 먼저 막으면 삭제를 확인 못 한다 |
| 서브링크 (`faq-sublink`) | 자동 생성. 표준 링크·앵커 텍스트·alt·GNB 가 도움. 빼려면 링크에 `rel="nosublink"`, 전체는 `<meta name="naver" content="nosublinks">` |
| 사이트 등록·소유 확인 (`faq-start-register`) | 등록 없이도 수집되지만 리포트를 보려면 소유 확인. 확인용 메타는 `<head>` 안, JS·meta refresh·쿠키 리다이렉트·frame 안·body 안은 인식 안 됨 |
| 사이트 브랜드 (`faq-branding`) | 검색 결과의 브랜드 영역은 자동 추출 |
