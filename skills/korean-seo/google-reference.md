# 구글 Search Central 요약 (2026-11-20 기준)

원문: https://developers.google.com/search/docs — 문서 주소는 `https://developers.google.com/search/docs/<경로>`(뒤에 `?hl=ko` 를 붙이면 한국어).
아래는 판단에 쓰이는 기준만 우리 말로 요약한 것이다(원문을 옮긴 것이 아니다). 이 저장소는 Google 과 관계가 없다.
핵심 44쪽은 정독했고, 나머지는 소제목과 규칙 문장만 훑었다. 채용·상품·레시피 같은 구조화 데이터 유형별 문서는 목록만 확인했다.

## 기본

| 문서 (경로) | 요점 |
|---|---|
| SEO 기본 가이드 (`fundamentals/seo-starter-guide`) | 순위를 보장하는 비법은 없다. 읽기 쉬운 URL, 중복은 리다이렉트·canonical(심하게 걱정할 필요는 없음), 사람들이 쓸 검색어 예상, 좋은 링크 글자, 고품질 이미지 + alt. 신경 쓰지 않아도 되는 것: meta keywords(안 씀), 도메인 속 키워드, 글 길이, 소제목 순서·개수, E-E-A-T 는 순위 요소가 아님 |
| 도움이 되는 콘텐츠 (`fundamentals/creating-helpful-content`) | 독창적 정보·분석, 과장 없는 제목, 저자·방법·이유("Who·How·Why") 밝히기, 가짜 저자 금지. 검색 엔진용 콘텐츠의 징후: 유행만 좇기, 정해진 글자 수, **내용이 크게 안 바뀌었는데 날짜만 바꾸기**, "신선해 보이려고" 대량 추가·삭제 |
| 생성형 AI 기능 최적화 (`fundamentals/ai-optimization-guide`) | AI 개요·AI 모드도 기존 SEO 와 같다(AEO·GEO 도 SEO). 흔한 것과 다른 "비상품성" 콘텐츠, 기술 구조. **필요 없는 것: llms.txt 등 특별 파일, 글 조각내기, AI 용으로 다시 쓰기, 가짜 언급 모으기, 구조화 데이터 과신.** 질문 변형마다 쪽을 만들면 대량 콘텐츠 남용 |
| 생성형 AI 콘텐츠 (`fundamentals/using-gen-ai-content`) | 가치를 더하지 않은 대량 생성은 스팸. 제목·설명·구조화 데이터·alt 도 사람이 사실 확인 |
| 개발자 가이드 (`fundamentals/get-started-developers`) | `<a href>` 링크, SPA 는 화면마다 URL, 글자로 된 내용(CSS `content` 는 색인 안 함), 쪽마다 고유한 title·description |
| 검색 작동 방식 (`fundamentals/how-search-works`) | 크롤링 → 색인(중복 묶어 canonical 선택) → 노출. 돈을 받고 순위를 올리지 않음, 색인 보장 없음 |

## 필수 사항·스팸

| 문서 (경로) | 요점 |
|---|---|
| 검색 필수사항 (`essentials`) | 기술 요구사항 + 스팸 정책 + 핵심 권장(사람들이 쓰는 낱말을 제목·h1·alt·링크 글자에, 크롤링 가능한 링크, 커뮤니티에 알리기) |
| 기술 요구사항 (`essentials/technical`) | Googlebot 차단 없음, HTTP 200, 색인 가능한 내용. noindex 는 크롤링을 허용해야 보인다 |
| 스팸 정책 (`essentials/spam-policies`) | 클로킹, 도어웨이, 만료 도메인, 해킹, 숨긴 글·링크(스크린리더 전용 글·아코디언은 괜찮음), **키워드 채우기**, 링크 스팸(유료 링크는 `sponsored`/`nofollow`), 대량 콘텐츠 남용, 스크래핑, 사이트 평판 남용, 몰래 리다이렉트, 얇은 제휴, 사용자 생성 스팸, 뒤로 가기 가로채기 |

## 검색 결과 모양

| 문서 (경로) | 요점 |
|---|---|
| 제목 링크 (`appearance/title-link`) | 길이 제한 없음(기기 폭에서 자름). "Home" 같은 모호한 제목·키워드 반복·상투 문구 피하기, 사이트 이름은 짧게 앞이나 뒤에, 가장 큰 제목(h1)을 분명히, 본문과 같은 언어·문자. 구글은 title·h1·og:title·링크 글자·WebSite 데이터로 제목을 바꿔 보여 줄 수 있음 |
| 스니펫 (`appearance/snippet`) | 주로 본문에서 만들고 description 은 더 정확할 때 씀. 길이 제한 없음, 쪽마다 고유, 키워드 나열 금지. `nosnippet`·`max-snippet`·`data-nosnippet` |
| 파비콘 (`appearance/favicon-in-search`) | 첫 화면의 `<link rel="icon|shortcut icon|apple-touch-icon(-precomposed)">`, 호스트마다 하나(서브디렉터리 불가), 정사각형 8px 이상·**48px 넘게 권장**, 형식 **BMP·GIF·ICO·PNG·JPEG·PPM·TIFF**(SVG 는 목록에 없음), 상대·절대 경로 모두 가능, URL 자주 바꾸지 않기 |
| 사이트 이름 (`appearance/site-names`) | 첫 화면의 `WebSite` JSON-LD `name`·`url`(+`alternateName`), og:site_name·title 과 일관되게, 도메인·서브도메인 단위만 |
| AI 기능 (`appearance/ai-features`) | 추가 요건 없음 — 색인 + 스니펫 가능이면 대상. 실적은 Search Console "웹"에 포함. 노출 제어는 nosnippet 등, AI 학습 제어는 Google-Extended |
| 게시 날짜 (`appearance/publication-dates`) | 보이는 날짜("게시"·"수정") + `datePublished`·`dateModified`(시간대 권장)를 일치, 미래·사건 날짜 금지, 다른 날짜를 줄이기 |
| 사이트링크·페이지 경험·CWV (`appearance/sitelinks`·`page-experience`·`core-web-vitals`) | 사이트링크는 자동. CWV 는 순위에 쓰임: LCP ≤ 2.5초, INP < 200ms, CLS < 0.1. HTTPS·모바일·과한 광고·전면 팝업 피하기 |
| 추천 스니펫·전면 팝업 (`appearance/featured-snippets`·`avoid-intrusive-interstitials`) | 추천 스니펫은 지정할 수 없음(nosnippet·max-snippet 으로 빼기만). 전면 팝업 대신 배너 |
| 이미지·Discover (`appearance/google-images`·`google-discover`) | `<img>` + 설명적 파일 이름·alt, 로고·글자 많은 이미지를 대표 이미지로 쓰지 않기. Discover 는 1200px 넘는 이미지 + `max-image-preview:large` |

## 크롤링·색인

| 문서 (경로) | 요점 |
|---|---|
| canonical (`crawling-indexing/canonicalization`·`consolidate-duplicate-urls`) | 힌트일 뿐. 리다이렉트(강) > rel=canonical(강) > 사이트맵(약). 절대 주소, 자기 자신 canonical, 방법마다 다른 URL 금지, # 금지, robots.txt·noindex 로 canonical 정하지 않기, HTTPS 우선 |
| 리다이렉트 (`crawling-indexing/301-redirects`) | 영구: 301·308·0초 meta refresh·(최후) JS. 임시: 302·303·307·지연 meta refresh |
| noindex (`crawling-indexing/block-indexing`·`robots-meta-tag`) | meta 또는 X-Robots-Tag, robots.txt 에는 못 씀, 크롤링이 허용돼야 보임. 규칙 충돌 시 더 엄격한 쪽. noarchive·nocache 는 안 씀 |
| robots.txt (`crawling-indexing/robots/*`) | 숨기는 수단이 아님(주소는 색인될 수 있음). 루트·UTF-8·500KiB, 24시간 캐시, 사이트맵은 전체 URL |
| 사이트맵 (`crawling-indexing/sitemaps/*`) | 500쪽 이하·링크가 잘 된 사이트는 없어도 됨. 50MB·5만 URL, 절대 주소, canonical 만, priority·changefreq 무시, lastmod 는 의미 있는 변경만·정확할 때만 사용. 인덱스 파일은 같은 폴더 이하의 사이트맵만 |
| 링크 (`crawling-indexing/links-crawlable`) | `<a href>` 만 확실히 따라감, 설명적이고 짧은 링크 글자, "여기를 클릭" 금지, 중요한 쪽은 내부 링크 하나 이상, 신뢰하지 않는 곳만 nofollow |
| URL 구조 (`crawling-indexing/url-structure`) | # 로 내용 바꾸지 않기, 읽기 쉬운 낱말, 하이픈으로 구분(밑줄 X), 파라미터 최소, 대소문자 구분, 사용자 언어 낱말 가능(퍼센트 인코딩) |
| JS SEO (`crawling-indexing/javascript/*`) | 서버·사전 렌더링 권장, History API, 의미 있는 상태 코드·SPA 소프트 404 처리, noindex 를 JS 로 없애면 안 통함, 콘텐츠 해시 파일 이름(오래 캐시), 지연 로딩은 사용자 조작 없이 보이게 |
| HTTP 상태 (`crawling-indexing/http-network-errors`) | 리다이렉트 10번까지, 4xx(429 제외)는 색인에서 빠짐, 5xx·429 는 크롤링을 늦추고 오래가면 빠짐 |
| meta 태그 (`crawling-indexing/special-tags`·`valid-page-metadata`) | 지원: description, robots/googlebot, notranslate, google-site-verification, charset, viewport. 안 씀: keywords, lang 속성, rel=next/prev. `<head>` 안에 img·iframe 이 있으면 그 뒤 태그를 못 읽음 |
| Googlebot (`crawling-indexing/googlebot`·`overview-google-crawlers`) | HTML 앞 2MB(PDF 64MB)만 읽음, 일반 크롤러 15MB |
| 사이트 이전 (`crawling-indexing/site-move-with-url-changes`) | 옛→새 1:1 301, 한 번에 하나만 바꾸기, 리다이렉트 1년 이상 유지, 주소 변경 도구 |
| 다시 크롤링 요청 (`crawling-indexing/ask-google-to-recrawl`) | URL 검사(할당량, 반복 요청 무의미), 많으면 사이트맵. 며칠~몇 주 |
| 페이지 나누기 (`specialty/ecommerce/pagination-and-incremental-page-loading`) | `<a href>` 로 다음 쪽, 첫 쪽을 canonical 로 쓰지 않기, 쪽 번호에 # 금지, 목록 쪽은 제목이 달라도 되고 같아도 됨 |
| 다국어 (`specialty/international/localized-versions`) | hreflang 은 서로 가리켜야 하고 자기 자신 포함, 절대 주소 |

## 구조화 데이터

| 문서 (경로) | 요점 |
|---|---|
| 일반 지침 (`guides/sd-policies`) | JSON-LD 권장, 화면에 보이는 내용만, 오해 소지·무관한 내용 금지, 필수 속성 다 넣기, 이미지는 크롤링 가능, 중복 쪽에도 같은 데이터, 위반 시 수동 조치(리치 결과 자격만 잃음) |
| 이동 경로 (`appearance/structured-data/breadcrumb`) | ListItem 2개 이상(name·item·position), 마지막 항목은 item 생략 가능, 첫 화면 항목 생략 가능, URL 구조가 아닌 실제 이동 경로 |
| Article (`appearance/structured-data/article`) | 필수 없음. headline, image(5만 픽셀 이상, 16:9·4:3·1:1 여러 장), datePublished·dateModified(ISO 8601 + 시간대), author(Person/Organization, name 에 이름만, url·sameAs). 여러 쪽 글은 쪽마다 또는 전체 보기 쪽을 canonical |
| Organization (`appearance/structured-data/organization`) | 필수 없음, 첫 화면이나 소개 쪽에. logo 112×112 이상·흰 배경에서 보이게, sameAs, 가장 구체적인 하위 유형 |
| 소프트웨어 앱 (`appearance/structured-data/software-app`) | 리치 결과에는 name·offers.price·평점(aggregateRating 또는 review) 필요 — 평점 없는 무료 라이브러리는 대상 아님 |
