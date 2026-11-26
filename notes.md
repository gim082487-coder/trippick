# 트립픽 작업 노트

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
