# 트립픽 v49 — 문제점 전수 진단 리포트

- 대상: `trippick_repo` (소스 `tour_hub/`) · 라이브 `https://trippick.pages.dev`
- 진단일: 2026-11-24 (KST)
- 측정 도구: `tour_hub/tools/v49_*.py` (Playwright 390/1280 실측, CPU 4x 스로틀 + Slow 4G 1.6Mbps·RTT 750ms, 정적 파싱)
- 원칙: 추측 없이 실제 HTML·이미지 파일·브라우저 계측값만 사용. 모든 수치는 이 저장소의 빌드 산출물(`deploy_site/`) 기준.

---

## 1. 페이지 용량·성능 (Core Web Vitals 병목)

### 1-1. 홈(`/`) 이 1.65MB 인 이유 — 실측 분해

| 구성 요소 | 크기 | 비고 |
|---|---|---|
| HTML 마크업 | **1,019,592 B** | 15,757개 DOM 노드, `<div>` 1,611 · `<a>` 872 · `<img>` 146 |
| 인라인 CSS | **200,337 B** | `<style>` 1개. 서브페이지가 쓰는 `assets/site.css`(313,432 B)와 별도로 홈에 전체 CSS를 다시 인라인 |
| 인라인 JSON/JS | **434,255 B** | 아래 표 |
| **합계** | **1,654,184 B (1.58MB)** | gzip 274,971 B |

인라인 JSON/JS 내역 (gzip 이전 원본):

| id | 내용 | 크기 |
|---|---|---|
| `tpSearch` | 사이트 검색 색인 401건 (입력할 때만 사용) | 130 KB |
| JSON-LD | 구조화 데이터 | 66 KB |
| `tpData` | 예산 계산기 상품 데이터 | 63 KB |
| `tpCompare` | 비교 바구니 데이터 | 66 KB |
| `tpBundles` | 묶음 상품 | 27 KB |
| 인라인 JS 8블록 | 필터·계산기·검색 등 | 38 KB |

**DOM·문서 길이**: 홈 15,757 노드 · 문서 높이 1280px에서 **58,683px**, 390px에서 26,796px. 섹션별로는 `#regions` 7,413 노드(84개 상품 카드), `#foods` 2,310, `#checklist` 1,521, `#tripcom` 947, `#essentials` 792, `#courses` 718, `#gifts` 627. `/stays` 6,679 노드(108장 카드, 390px 문서 높이 79,321px), `/guides/` 1,745 노드(102장 카드).

**이미지 속성**: 홈 `<img>` 146개 중 `loading="lazy"` 145개, `fetchpriority` 1개, **`decoding="async"` 0개**, width/height 누락 0. 첫 화면(390) 안에 걸리는 이미지 1장(히어로)은 lazy 아님 — 올바름.

### 1-2. 실제 전송량 (모바일 390 · Slow 4G)

| 페이지 | HTML | 리소스 합계 | 그중 이미지 | DOM |
|---|---|---|---|---|
| `/` | 1.65MB | **3.60MB** | 2.36MB | 15,758 |
| `/stays` | 0.64MB | 1.72MB | 0.24MB | 6,680 |
| `/guides/` | 0.26MB | **6.66MB** | 5.25MB | 1,745 |
| `/exchange` | 0.08MB | 0.02MB | 0 | 689 |
| `/passes` | 0.12MB | 0.04MB | 0 | 1,069 |

원인 (파일 실측):
- **히어로 preload 불일치**: `<link rel="preload" as="image" href="…hero_kyoto_street.jpg">` 에 `imagesrcset` 이 없어 모바일에서도 2000w 원본(387KB)을 받고, `<picture>` 가 고른 `_sm`(108KB)까지 **중복 다운로드**.
- **코스 커버 5장**: 1600×1000 JPEG 184~387KB(`danang` 386KB, `sapporo` 381KB, `tokyo` 328KB, `osaka` 302KB, `jeju` 184KB)를 260px 썸네일과 800px 패널에 그대로 사용.
- **가이드 목록 96장**: 640×360 표시에 원본(최대 1200~1536px)을 사용. 그중 `images/winter/warm5.jpg` **2.48MB(1536×1024)**, `images/winter/best6.jpg` **2.00MB(1448×1086)** — 두 장이 목록 첫 화면 전송량의 84%.
- `images/` 전체 401장 55MB 중 120KB 초과 169개(37.9MB)가 재인코딩 없이 커밋돼 있었음.

### 1-3. 렌더 비용 (CPU 4x 스로틀, 390)

| 페이지 | TaskDuration | LayoutDuration | 최장 롱태스크 |
|---|---|---|---|
| `/` | **17.4s** | **7.1s** | 632ms |
| `/stays` | 8.6s | 5.8s | 553ms |
| `/guides/` | 5.8s | 3.0s | 462ms |

DOM 1.5만 노드를 첫 화면에서 전부 스타일·레이아웃하고 있었다(화면 밖 섹션 포함).

---

## 2. 콘텐츠 품질·애드센스 리스크 (가이드 103편 전수)

> **정정(2026-11-24 v50)** — 이 절의 “1,446자 최단 가이드 / 1,800자 미만 7편”은 계수 버그입니다. `tools/v49_content_audit.py`가 요약박스(g-sum)를 지울 때 쓴 `re.sub(r'<div class="g-sum">.*?</div>\s*</div>')`가 일부 글에서 본문 대부분을 함께 삭제했습니다(예: travel-hacks 11,933자 중 9,089자). div 깊이를 세는 균형 파서로 바꾼 `tools/v50_content_audit.py`로 다시 재면 **최단 2,214자·중앙값 3,550자·1,800자 미만 0편**입니다. 제휴 링크 밀도 상위 3편(괌vs사이판·오사카vs후쿠오카·다낭vs나트랑)과 제목 유사도 지적은 유효합니다.

- 본문(3줄 요약·목차 박스 제외, 공백 제외) 글자수: 최소 1,446 · p10 1,860 · 중앙값 **2,738** · 최대 6,136.
- **1,500자 미만 1편**: `travel-hacks-hotel-flight-restaurant` 1,446자(내부링크 2).
- **1,800자 미만 7편**: 위 1편 + `nhatrang-dalat-tour-vs-free` 1,704 · `tokyo-package-4d-vs-3d` 1,727 · `tokyo-food-route` 1,741 · `vietnam-golf-54-vs-36` 1,787 · `hawaii-hyatt-vs-sheraton` 1,794 · `jeju-aircarotel-3-packages` 1,823.
- 본문 내 제휴 링크 총 160개. 밀도 상위: `guam-vs-saipan-comparison` **16개 / 5,380자(1개당 336자)**, `osaka-vs-fukuoka-comparison` 14/4,952, `danang-vs-nhatrang-comparison` 12/3,995. 제휴 링크가 본문 설명보다 앞서는 구간은 없으나, 심사 관점에서 "얇은 제휴 페이지"로 읽힐 여지가 있는 구간이다.
- 제목 유사도(자카드) 상위: `autumn-travel-destinations` ↔ `spring-travel-destinations` **0.64**, `japan-esim` ↔ `vietnam-esim` 0.56, `esim-roaming-insurance-guide` ↔ `vietnam-esim` 0.50, `spring` ↔ `winter-december-best6` 0.46 — 카니발라이제이션 후보.

---

## 3. 내부 링크 고립 (수정 전)

131개 콘텐츠 페이지의 유입 내부 링크(in-degree, 자기 자신·`/guides/` 목록 제외 아님) 계산 결과:

- 최저 **1**: `danang-vs-nhatrang-comparison`, `europe-train-eurail-vs-point`, `osaka-vs-fukuoka-comparison` — `/guides/` 목록에서만 링크.
- **2**: `incheon-airport-parking-bus`, `japan-ryokan-onsen-etiquette-budget`, `taipei-3n4d-course-budget`.
- 가이드 in-degree 중앙값 11, 최대 55. 허브 중 약한 곳: `quiz` 9, `yeosu` 20, `seoul` 22, `busan` 22.
- 원인: `data/guides.json` 의 `related` 가 **단방향**이었다(예: `danang-vs-nhatrang` → 6편을 가리키지만 역링크 0). 허브 `guides` 배열에도 비교·코스 가이드가 빠져 있었다.

---

## 4. 모바일 UX (390 실측)

- 가로 넘침 0 (`/`, `/stays`, `/guides/`, `/exchange`, `/passes`, 가이드 상세 전부).
- 필터 동작: 국가 탭 → 도시 4, 도시 칩 오사카 → 도시 1·카드 4, `/stays` 국내 → 54장. 비교 바 고정(fixed, z 80) 정상.
- **터치 영역 결함**: 상품 카드 액션 버튼이 `비교` **34×48px**, `찜` **30×48px** — 44px 권장치 미달로 옆 버튼 오터치 위험. (헤더 아이콘 38×38, 히어로 CTA 40px, `pc-chip` 35px도 44px 미달이나 카드 액션만 실제 오터치 영향이 큼.)
- 가이드 본문 폭 358px·글자 15.3px·행간 27.8px, 표는 컨테이너 내부 스크롤(477px 표가 358px 안에서 스크롤, 문서 넘침 0), 목차 버튼 109×34px.
- 검색 드롭다운 358×430 정상, 결과 7건.

---

## 5. 외부 리소스·데이터 정합성

- 이미지 404: **0건**(로컬 참조 685개 전수 확인, quiz.html의 JS 템플릿 1건은 오탐). OG 이미지 100개 전부 존재.
- 외부 호스트: `kr.trip.com` 986 · `naver.me` 636 · `link.coupang.com` 182 · `www.google.com`(지도 링크) 134 · `pagead2.googlesyndication.com` 132 · `klook` 13. 폰트는 `assets/fonts/` 자체 호스팅(v47) 유지.
- 애드센스: `ads.txt`(`pub-9563082990728787`) 정상, 로더·`google-adsense-account` 메타 131페이지. 광고 슬롯 3곳은 `<ins>` 없이 내부 배너 폴백.
- **운영 공백**: `data/analytics.json` 의 GA4 `measurementId` 가 비어 있어 gtag 미탑재(Cloudflare Web Analytics만). 유입 채널별 성과를 볼 수단이 없다.
- 폰트 preload 3개 + CSS 1개가 렌더 차단 경로에 있어 FCP 하한을 만든다(아래 잔여 과제).

---

## 6. v49에서 고친 것 (전/후 실측)

측정 조건 동일(390 · CPU 4x · Slow 4G 1.6Mbps/750ms), `tools/v49_perf.py`.

| 지표 | `/` 전 | `/` 후 | `/stays` 전 | `/stays` 후 | `/guides/` 전 | `/guides/` 후 |
|---|---|---|---|---|---|---|
| LCP | 6,480ms | **5,112ms (-21%)** | 7,020ms | **6,608ms (-6%)** | 5,744ms | 5,748ms |
| FCP | 5,860ms | 5,112ms | 7,020ms | 6,608ms | 5,744ms | 5,748ms |
| 리소스 전송 | 3.60MB | **1.17MB (-67%)** | 1.72MB | **1.44MB (-16%)** | 6.66MB | **1.28MB (-81%)** |
| 이미지 전송 | 2.36MB | **0.34MB (-86%)** | 0.24MB | 0.12MB | 5.25MB | **0.08MB (-98%)** |
| TaskDuration | 17.4s | **3.5s (-80%)** | 8.6s | **4.4s (-49%)** | 5.8s | **1.7s (-71%)** |
| LayoutDuration | 7.1s | **0.9s (-87%)** | 5.8s | **2.5s (-57%)** | 3.0s | **0.7s (-77%)** |
| 최장 롱태스크 | 632ms | 426ms | 553ms | 405ms | 462ms | 217ms |
| CLS | 0 | 0 | 0.026 | 0.026 | 0 | 0 |

### 적용 내용

1. **이미지 경량화 (`tools/v49_img_opt.py`, `tools/v49_img_variants.py`)**
   - 120KB 초과 JPEG 169개 재인코딩(최대 폭 1600, q82, progressive): 37.9MB → 31.5MB. `warm5.jpg` 2.48MB → 260KB, `best6.jpg` 2.00MB → 172KB.
   - 가이드 히어로·카드, 코스 커버, 홈 히어로에 **WebP 480/720/960/1440 변형 285개** 생성 후 `<picture><source type="image/webp" srcset=… sizes=…>` 로 연결(변형이 없으면 기존 `<img>` 그대로 → 빌드 이식성 유지).
   - 히어로 `preload` 를 `imagesrcset`/`imagesizes` 로 교체해 모바일 중복 다운로드 제거.
   - 모든 `<img>` 에 `decoding="async"` 자동 부여(빌드 후처리, `build.py`·`build_pages.py`).
2. **렌더 비용 (`template.html`)**
   - 화면 밖 큰 블록 `content-visibility:auto` + `contain-intrinsic-size:auto`: `.flow > section`, `#regions .city`, `.gi-sec`, `.sgrid > .scard`. 인쇄 시엔 `visible`.
   - 부작용(해시 이동 후 섹션이 나중에 그려져 목표 위치가 밀림) 보정: 기존 `openHash` 로직을 확장해 80/350/900/1600ms 에 위치 재정렬, 사용자가 직접 스크롤(wheel·touchmove·keydown)하면 중단. 실측 결과 해시 착지 오차 41~112px(수정 전 최대 -16,629px).
3. **내부 링크 고립 해소 (`tools/v49_links.py`, `data/guides.json`·`city_hubs.json`)**
   - 고립 6편을 관련 허브(다낭·나트랑·오사카·후쿠오카·타이베이)의 `guides` 배열과 관련 가이드 `related`(양방향)에 22건 연결.
   - 결과: 가이드 최소 in-degree **1 → 3**, in-degree ≤2 가이드 **6편 → 0편**. 허브 metaDesc 의 "관련 가이드 N편" 숫자도 실제값으로 동기화(v36 검증 통과).
4. **모바일 터치 영역** — 카드 `비교` 34→44px, `찜` 30→44px (높이 48 유지). 390 실측 `[44, 48]`.

### 라이브 실측 (2026-11-24 13:2x KST, 배포 후 · 동일 스로틀)

| 페이지 | FCP | LCP | HTML(전송) | 리소스 합계 | 이미지 | DOM |
|---|---|---|---|---|---|---|
| `/` | 2,720ms | **3,304ms** | 291KB | 1.09MB | 270KB | 15,781 |
| `/guides/` | 3,144ms | 3,144ms | 56KB | 0.94MB | 82KB | 1,950 |

(Cloudflare 브로틀리 + HTTP/2 + CDN 캐시가 붙어 로컬 측정보다 1.5~1.8초 빠릅니다. 사이트맵 131 URL 전부 HTTP 200 확인.)

### 검증

- `python3 build.py` → 상품 84 · 도시 30 · 코스 5 · 필수품 60, index 1,300KB
- `python3 build_pages.py --out ../deploy_site --base https://trippick.pages.dev --check-links` → HTML 134개 · 내부 링크 13,973개 **실패 0**
- `verify_v36 / v41 / v42 / v43 / v44 / v45 / v48` 전부 통과
- `tools/v49_smoke.py` 20항목 PASS (필터·정렬·검색·비교·찜·계산기·코스탭·/stays 필터·가이드 목차·WebP picture·도구 3페이지, JS 오류 0)

---

## 7. 남은 구조적 문제 (이번에 손대지 않음)

| 우선순위 | 문제 | 근거 | 권장 조치 |
|---|---|---|---|
| 높음 | 홈 HTML 자체가 1.58MB(gzip 275KB)·15.7k 노드 | §1-1 | `tpSearch`(130KB)·`tpData`(63KB)·`tpCompare`(66KB)를 `/data/*.json` 으로 분리하고 검색 포커스·계산기 진입·비교 클릭 시 `fetch`. 예상 -260KB(raw). 섹션별 카드 수 제한("더 보기" → 허브)은 SEO 링크 손실 검토 필요 |
| 높음 | `/stays` LCP 6.6s — 108장 카드를 한 문서에 | §1-3 | 권역 섹션 분리 또는 카드 24장 단위 점진 렌더(JS) |
| 중간 | FCP 하한 — 폰트 preload 3개 + CSS 313KB | §5 | 첫 화면 critical CSS 인라인 + 폰트 preload 1개로 축소 |
| 중간 | GA4 미설정 | `data/analytics.json` | 속성 생성 후 measurementId 입력 → 빌드 (사용자 계정 작업 필요) |
| 중간 | 애드센스 심사 리스크: 1,446자 가이드 1편, 제휴 밀도 상위 3편, 시즌 가이드 제목 중복 0.64 | §2 | `travel-hacks…` 보강 또는 통합, 비교 가이드는 "확인 기준·업데이트" 블록 추가, autumn/spring 은 검색 의도(단풍 시기 vs 벚꽃 시기)로 title/lead 차별화 |
| 낮음 | 허브 `quiz` in-degree 9, `yeosu` 20 | §3 | 허브 상호 링크·가이드 related 추가 |
| 낮음 | `images/` 64MB(WebP 변형 포함) | 저장소 | Cloudflare 이미지 리사이즈 도입 시 변형 파일 제거 가능 |
