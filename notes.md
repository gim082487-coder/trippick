# 트립픽 작업 노트

## v63 — 2026-11-27 (14:0x~) · 가이드 3편(도쿄 3박4일·무비자 체류기간·동남아 렌터카) + sitemap-index 분리

### 배포
- 커밋 **`64448ca`** → `main` 푸시(`f3701fa..64448ca`), Cloudflare Pages 라이브 반영 확인
- 사이트맵 **177 → 180 URL**(가이드 3편) · 가이드 **135 → 138편** · `sitemap-index.xml` 신설
- `robots.txt`에 `Sitemap: .../sitemap-index.xml` 병기(기존 `sitemap.xml` 줄 유지)

### 신규 가이드 3편 (135 → 138편)
- `/guides/tokyo-3n4d-course-budget` — 도쿄 3박4일. 게이세이 본선 1,060엔·82분(1회 환승), 하네다 게이큐 330엔·11분, 지하철 24/48/72시간 800/1,200/1,500엔(24시간권 3장보다 900엔↓), 스카이트리 1,800·3,000엔(현장 +500엔), 시부야 스카이 온라인 2,700·3,400엔(현장 3,000·3,700엔·2주 전 0시 판매), 도쿄타워 1,500엔, 도쿄도청 무료, 디즈니 1데이 8,900엔~/애프터3 7,900엔~/애프터5 5,400엔~, 2인 교통·입장료 7만 3,619원(전망대 둘이면 11만 9,209원)
- `/guides/visa-free-stay-duration-guide` — 무비자 체류기간. 외교부 해외안전여행 사증면제 목록(2026.11) 기준 일본·대만·홍콩·마카오·말레이시아·태국 90일, 몽골 90일(한시 ~2026-12-31), 베트남 45일(2028-03-14까지), 괌 45일(관광만), 중국 30일(~2026-12-31), 필리핀·라오스 30일, 인도네시아는 VOA 30일 500,000루피아(약 3만 6,800원) + 1회 30일 연장. 태국은 2026-09-15 개편에도 협정 우선(주태국 대사관 2026-09-09). 여권은 필리핀만 "체류 종료 후 6개월"
- `/guides/southeast-asia-rental-car-license-guide` — 동남아 렌터카·국제면허. IDP 9,000원·1년·책자형, 태국은 IDP+한국면허 원본+여권(좌측통행), 베트남은 2023-07-23 상호인정 협정으로 입국일부터 1년(B범주)·영문면허 불가·실제 대여 거절/보증금 1,000달러 안팎 사례, 필리핀 90일, 말레이시아 12개월 미만 IDP(2026-10-01부터 LMM 교환), **발리는 한국 IDP 불인정**(주인도네시아 대사관 발리 분관 안전공지 "발리는 국제 운전면허로 운전을 할 수 없음")

### sitemap-index 분리 (서치콘솔 `가져올 수 없음` 5회 연속 대응)
- `build_pages.py`의 `write_sitemap()`을 `_urlset()` + 4종 출력으로 확장. `/sitemap.xml`은 **180 URL 그대로 유지**(한 글자 수준 동일 포맷)
- `/sitemap-index.xml` → `sitemap-core.xml` 15(홈·/cities/·도구 13) · `sitemap-hubs.xml` 26 · `sitemap-guides.xml` 139(/guides/ + 가이드 138)
- 세 분할의 URL 합 180 = `sitemap.xml` 180, **중복 0·집합 동일**(로컬·라이브 실측)
- `scheduled-actions/🔍-구글-서치콘솔-색인-요청-재시도/action.md`에 11-28 실행용 메모 추가: `/sitemap-index.xml` 추가 제출, 사이트맵 수 177→180개 갱신

### 레거시 정리
- `tour_hub/exchange.html`(83KB, 11-26 렌더본)은 빌드 미사용·참조 0건 확인 후 `git rm`. 정본은 `content/pages/exchange.html`(빌드 소스)로 유지, `/exchange` 라이브 200

### 검증
- `build.py` → 상품 84·도시 30·코스 21·필수품 65
- `build_pages --out ../deploy_site --check-links` → **HTML 183개·내부 링크 20,227개 실패 0**
- `verify_v36·41·42·43·44·45·48·51·52·53·54·59·60·61·62` 기대값(138편·180 URL) 갱신 후 **전부 PASS** + `verify_v34` 실패 0 + 신규 `tools/verify_v63.py` PASS(가이드 3편 본문 3,000자 이상·표 5개 이상·FAQ 5·제휴 7~9건·Article/FAQPage·canonical, 사이트맵 4종 합계·중복, robots 2줄, 레거시 제거, /tokyo·/guides/ 표기)
- `tools/v50_content_audit.py` → 138편 **1,800자 미만 0편**, 제목 유사도 최대 0.42 유지
- 로컬·라이브 1280·390 렌더(`tools/v63_shots.py`): 신규 3편+`/tokyo`+`/guides/` **가로 넘침 0·깨진 이미지 0·pageerror 0**, 표 5~8·제휴 8~11. 스크린샷 `trippick_repo/v63_shots/`(`v63_*` 로컬, `live_*` 라이브)
- 라이브: 신규 3편 200(63,844 / 60,325 / 65,056B), `/tokyo` "관련 가이드 15편", `/guides/` "가이드 138편", `sitemap.xml` **180 URL 전부 HTTP 200**(중복 0·BOM 없음), `sitemap-index.xml`·분할 3종 200, Googlebot UA 200
- IndexNow 8 URL 제출 **HTTP 200**(신규 3편·`/tokyo`·`/guides/`·`sitemap.xml`·`sitemap-index.xml`·`robots.txt`), 키 파일 200

## v62 (2026-11-27) — 홈페이지 다듬기

사용자 지시: "오늘도 다해!! 여권번호 입력은 다음에할게 홈페이지 다듬자"

### 1. 홈 HTML 1.6MB → 1.30MB (−308KB, −19.2%)
| 항목 | 전(v61) | 후(v62) | 근거 |
|---|---|---|---|
| `index.html` | 1,606,496B | 1,298,006B | `python3 build.py` 출력 |
| 인라인 CSS | 199,609자 | 0 (외부 `assets/site.css?v=62`) | 규칙 1,887개 중 1,886개가 site.css 와 동일(홈 CSS ⊂ site.css) |
| 본문 들여쓰기 | 110,504B | 0 | `compact_html()` — script·style·pre·textarea 안쪽은 보존 |
| 빈 줄 | 2,764B | 0 | 같은 함수 |

- 1.6MB의 구성(진단): 인라인 CSS 200KB · 코스 21편 마크업 195KB · 도시 30곳 섹션 450KB · 맛집 130KB · 트립닷컴 94KB · 출국 체크리스트 67KB · 필수품 54KB · 선물 35KB · 파인더 33KB · JSON-LD 93KB.
- 300자 단위 중복 블록 검사 결과 **중복 마크업 0건** → 줄일 수 있는 것은 공백과 CSS 위치뿐이었습니다. SEO 콘텐츠(코스·맛집·숙소 카드)는 한 장도 지우지 않았습니다.
- `build.py`: `extern_home_css()`(홈 인라인 `<style>` → `assets/site.css?v=62` 링크) + `compact_html()`. `build_pages.py` 의 `CSS_V` 를 62로 올려 site.css 를 재생성합니다(홈·서브페이지가 같은 CSS 한 파일을 캐시).

### 2. 코스 선택 UI — 21편을 한눈에 (모바일)
- 문제: 모바일에서 `.picker` 가 68vw 가로 스크롤이라 21편 중 1.5장만 보이고, 몇 번째인지·전체가 몇 개인지 알 수 없었습니다.
- 수정: `.pick-idx` 칩 줄을 홈 `#courses` 위에 추가(모바일 ≤720px 에서만 표시). 21개 칩에 번호(01~21)와 도시명("오사카·교토" 등)을 넣고, 선택 상태는 `aria-current` 로 표시합니다. 칩을 누르면 해당 패널이 열리고 큰 카드 스트립도 그 카드로 스크롤됩니다. 큰 카드를 눌러도 칩 상태가 함께 바뀝니다(선택 로직을 `select(id)` 한 곳으로 통합).
- 파일: `template.html`(CSS `.pick-idx/.pidx` + JS `select()`), `build.py:render_course_index()`.

### 3. 코스 패널 히어로 이미지 1000px 버그 수정
- 원인: CSS 는 `.panel-hero>img` 를 절대배치했는데 마크업은 `<picture>` 로 감싸 v49 이후 WebP 변형을 쓰면서 선택자가 빗나갔습니다. 그 결과 히어로가 **390px 화면에서 1000px 높이**로 렌더돼(데스크톱 동일) 패널 첫 화면을 이미지가 다 먹었습니다.
- 수정: `.panel-hero>picture{position:absolute;inset:0}` + `.panel-hero>picture>img` 를 절대배치·object-fit:cover. 실측 히어로 높이 **데스크톱 280px · 모바일 132px**(설계값 그대로).
- 부수 효과: 패널마다 1,000px 씩 사라져 홈 전체 높이가 크게 줄었습니다(스크롤·INP 개선).

### 4. 연결성 점검 (수정 불필요 확인)
- 도시 허브 26곳 전부 헤더·푸터에서 `coupons`, `stays`, `./#courses` 로 이어집니다(허브 26/26 확인).
- 가이드 135편 → 허브·`/coupons`·`#courses` 링크 유지.

### 5. 백로그 — eSIM 제휴 링크 점검
- eSIM 27건 전부 `trip_sub3=D21303312` + 고유 `trip_sub1` 로 일관(유럽 5건 포함). 분리 필요 없음.
- eSIM 27건 URL 을 iPhone UA 로 열어 **27/27 HTTP 200 + 한국어 제목** 확인. 홍콩(`hongkong-simcard`)은 `<title>` 이 일반 문구지만 h1 "홍콩 유심 추천"·ItemList 26건으로 실제 eSIM 상품 목록이 맞아 유지했습니다.

### 6. 검증
- `build.py` → 상품 84 · 도시 30 · 코스 21 · 필수품 65.
- `build_pages.py --out ../deploy_site --base https://trippick.pages.dev --check-links` → **HTML 180개 · 내부 링크 19,865개 실패 0**.
- `verify_v36·41·42·43·44·45·48·51·52·53·54·59·60·61·62` 전부 PASS (v51~60 의 `LASTMOD` 기대값을 2026-11-27 로, v61 의 `data-course` 카운트를 코스 카드 한정으로 갱신).
- `tools/v62_shots.py`(신규) 1280·390 — site.css?v=62 로딩·body 배경·Pretendard 적용, 코스 카드 21·패널 21(활성 1), 칩 21개(데스크톱 숨김/모바일 표시), 칩·카드 전환 3편 표본, 히어로 280/132px, 가로 넘침 0·깨진 이미지 0·pageerror 0·콘솔 오류 0. `/stays`·`/passes`·`/coupons`·`/osaka` 200·넘침 0.

### 7. 배포
- 커밋 `e99fe43`(본문)·`1490154`(라이브 스크린샷) → `main` 푸시. 라이브(https://trippick.pages.dev) 홈 **1,298,220B**(Cloudflare 계측 214B 포함) · `/stays`·`/passes`·`/coupons`·`/osaka`·`/sitemap.xml` 200, `assets/site.css?v=62` 200.
- 라이브 1280·390 스크린샷 `v62_shots/live_*`, IndexNow 변경 URL 제출.

## 2026-11-27 데일리 점검 — 환율 갱신 + verify_v34 실행 환경 정상화

### 1. 환율 (2026-11-27 00:02 UTC 고시 반영)
- 주 API(`open.er-api.com`) `time_last_update_utc = Fri, 27 Nov 2026 00:02:31 +0000` 정상 발행 → 백업(jsDelivr) 불필요.
- 11-26 고시는 주·백업 모두 미발행이어서 11-25 값을 쓰고 있었고, 오늘 11-27 값으로 하루 지연을 해소했습니다.
- 변동(전일 대비): USD 1,342.2819→**1,344.086**(+0.13%) · EUR 1,472.7541→**1,474.9263**(+0.15%) · JPY 8.439→**8.4426**(+0.04%) · CNY 200.9646→**201.3288**(+0.18%) · HKD 171.3502→**171.5266**(+0.10%) · THB 39.582→**39.4773**(-0.26%) · TWD 40.7631→**40.7764** · PHP 21.0544→**21.0588**. VND·SGD·AUD·GBP 동일.
- `staticBasis`·`planner.json fx`는 기준(2026-11-20) 대비 최대 +0.89%(AUD)/+0.71%(JPY)로 3% 미만이라 유지. `/exchange` 고시일 `2026.11.27`·환율표 반영 확인.

### 2. verify_v34 실행 환경 정상화 (도구 수정)
- 이 환경에 Chromium 시스템 라이브러리가 없어 v34는 계속 실행 불가였습니다. `tools/verify_v34.py`가 시작할 때 `/workspace/.tools/chromelibs/root/usr/lib/x86_64-linux-gnu`·`/workspace/.tools/sysroot/usr/lib/x86_64-linux-gnu`를 `LD_LIBRARY_PATH`에 스스로 넣도록 해, 이제 `python3 tools/verify_v34.py`만으로 실행됩니다.
- 그 위에서 드러난 3가지 **검사 스크립트 노후화**를 고쳤습니다(사이트 코드 문제 아님):
  1. `file://`로 열면 계산기 데이터 `fetch()`가 막혀(v50 지연 로드) 홈 묶음 CTA가 늘 0개로 보였습니다 → `deploy_site`를 로컬 HTTP(127.0.0.1)로 서빙해 라이브와 같은 조건으로 검사.
  2. v50 지연 로드 때문에 홈은 `#planner`로 스크롤해 부트시킨 뒤 측정(안 되면 탭 클릭으로 재시도).
  3. `/stays`는 v21+ 기본 필터(all)에서 파리 카드가 `display:none`, 640px 이하에서는 지역 칩이 `#sfFold`에 접혀 있습니다 → 필터를 펼치고 파리 칩을 누른 뒤 배지 간격 측정.
- 결과: 1280·390 전 항목 통과(실패 0). 배지 국기·텍스트 간격 4.0px, 제휴 클릭 추적 정상, 가로 넘침 0, 콘솔 에러 0.

### 3. 데이터·링크·검증
- `build.py` → 상품 84 · 도시 30 · 코스 21 · 필수품 65, 홈 1,022KB(변동 없음).
- `build_pages.py --check-links` → HTML 180개 · 내부 링크 19,865개 **실패 0**, sitemap 177 URL.
- `verify_v36·41·42·43·44·45·48·51·52·53·54·59·60·61·62` 전부 PASS + `verify_v34` PASS.

### 4. /exchange 실시간 환율 소스 순서 정리
- 화면에서 `기준 환율 2026.11.27 고시`인데 실시간 갱신 줄은 `API 11.26 09:00`·엔 8.436원(jsDelivr의 하루 늦은 값)로 어긋나 보였습니다.
- `content/pages/exchange.html`의 `SOURCES`를 **er-api → jsDelivr** 순으로 바꾸고(빌드·일일 갱신이 쓰는 주 소스와 동일), jsDelivr에도 같은 72시간 신선도 검사를 적용했습니다. 안내 문구도 실제 순서로 수정.
- 확인: `기준 환율 2026.11.27` + `API 11.27 오전 09:02 갱신` + 엔 8.443원(1,184엔) — 표·계산기 일치, 콘솔 에러 0.

## v64 (2026-11-27) — 고검색량 가이드 8편 추가·배포

사용자 지시: "더달려 검색키워드 높은 글로 ㄱㄱ"

### 1. 신규 가이드 8편 (146편)
| 슬러그 | 제목 | 핵심 확인값(2026-11-27) |
|---|---|---|
| `us-esta-application-guide` | 미국 ESTA 신청 | $40.62(처리 $10.62+승인 $30) · 2년/90일 · 72시간 전 · 처리 최대 72시간 |
| `uk-eta-application-guide` | 영국 ETA 신청 | £20 · 2년·1회 6개월 · 1일~3영업일 · 한국 2025-01-08부터 |
| `kansai-airport-osaka-kyoto-transfer` | 간사이공항→난바·우메다·교토·USJ | 공항급행 970엔 · 라피트 디지털 1,410엔 · 간쿠쾌속 1,210엔 · 하루카 2,700엔(교토) · 막차 23:55 |
| `new-york-4n5d-course-budget` | 뉴욕 4박5일 | AirTrain $8.75+지하철 $3.00 · OMNY 7일 상한 $35 · 여신상 $26 · ESB $46~ · 메트 $30 |
| `nagoya-3n4d-course-budget` | 나고야 3박4일 | 뮤스카이 1,430엔 · 지브리 스탠더드 3,300엔(2개월 전 10일) · 시라카와고 3,600~4,700엔 |
| `japan-restaurant-reservation-guide` | 일본 식당 예약 | 타베로그 440엔/인 · OMAKASE 390엔/좌석 · 당일·노쇼 100% |
| `macau-1n2d-ferry-bus-guide` | 마카오 1박2일 | 터보젯 194/212/242HK$ · 금바 65/70HK$ · 버스 MOP6 · LRT 6~12MOP |
| `paris-metro-navigo-guide` | 파리 교통권 | 1회 €2.55 · 공항 €14 · 주르 €12.30 · 세멘 €32.40 · 비지트 63.80(3일) |

- 기존 138편과 슬러그·주제 중복 0. `entry-immigration-guide`(제도 개괄), `osaka-usj-transfer`(USJ 단일 구간), `hongkong-macau-3n4d-course`(3박4일 전체)와는 범위를 나눠 썼다.
- 본문: 공백 제외 6,616~7,858자(전 8편 3,000자 이상), 표 6~9개, h2 6개 이상, FAQ 5문항, 제휴 링크 7~11건, 도구 링크 2~3종.
- 히어로 1200×800 + WebP 480/720/960 + OG 1200×630 8편 생성(`tools/make_v64_images.py`). 사진: 펙셀스 5장(신규 3장은 `images/v64_src/`), 위키미디어 CC0 1장, 기존 v33·v55 2장. `photo_credits.json`에 v64 8건 기록.
- 허브 연결: `/osaka`(간사이공항), `/macau`, `/paris` 상단에 신규 편 추가(오사카는 16편 유지 위해 `japan-souvenir-list`를 허브 목록에서 제외). 역링크 12개 가이드에 추가.

### 2. 검증
- `build.py` → 상품 84·도시 30·코스 21·필수품 65, 홈 1,022KB
- `build_pages.py --out ../deploy_site --check-links` → **HTML 191개·내부 링크 21,093개 실패 0**
- `verify_v36·41·42·43·44·45·48·51·52·53·54·59·60·61·62·63` 기대값(146편·188 URL) 갱신 후 전부 PASS + **신규 `tools/verify_v64.py` PASS**
- `v50_content_audit.py` → 146편 **1,800자 미만 0편**, 제목 유사도 최대 **0.42**(신규 뉴욕 편 제목을 차별화해 0.60→0.42로 낮춤)
- `verify_v34` Chromium 렌더 검사 실패 0
- 로컬 1280·390 렌더(`tools/v64_shots.py`): 신규 8편+허브 3곳+`/guides/` **가로 넘침 0·깨진 이미지 0·pageerror 0**. 스크린샷 `v64_shots/v64_*`
- 사이트맵: `sitemap.xml` **188 URL** · `sitemap-index.xml` 분할(core 15·hubs 26·guides 147) 합 188·중복 0
