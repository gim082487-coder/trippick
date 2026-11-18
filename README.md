# 트립픽 (trippick)

여행 코스·가이드투어·숙소·항공을 같은 기준(실질 1인가, 현장 추가금, 취소 규정)으로 비교하는 여행 정보 사이트입니다.
`tour_hub/`에서 정적 HTML을 생성하고, `deploy_site/`가 실제로 서빙되는 산출물입니다.

- 운영 주소: <https://trippick-kr.netlify.app>
- 기술: 파이썬 3로 만든 정적 사이트 생성기 (프레임워크·DB·서버 없음)

## 구성

| 경로 | 내용 |
|---|---|
| `deploy_site/` | 배포본. 이 폴더를 그대로 서빙하면 사이트가 됩니다. |
| `tour_hub/` | 소스. 빌드 스크립트·데이터·본문·이미지 |
| `tour_hub/build.py` | `index.html`(홈) 생성: 상품 카드, 예산 계산기, JSON-LD, 광고 슬롯 |
| `tour_hub/build_pages.py` | 가이드 36편·신뢰 페이지 4종·`sitemap.xml`·`assets/site.css` 생성 |
| `tour_hub/template.html` | 홈 템플릿(디자인 토큰·CSS·섹션 마커) |
| `tour_hub/data/tours.json` | 여행 상품 57개 (가격·포함·불포함·취소 규정·제휴 링크) |
| `tour_hub/data/essentials.json` | 여행 필수품·교통패스·eSIM·공항픽업 22종 |
| `tour_hub/data/tripcom.json` | 트립닷컴 숙소 15개 도시·항공 6개 노선 제휴 링크 |
| `tour_hub/data/courses.json` | 추천 코스 5개(일차별 구성) |
| `tour_hub/data/guides.json` | 가이드 36편 메타데이터(제목·설명·관련 상품) |
| `tour_hub/content/guides/*.html` | 가이드 본문 (HTML 조각) |
| `tour_hub/content/pages/*.html` | 소개·문의·개인정보·약관 본문 |
| `tour_hub/tools/` | 데이터 가공 스크립트 |

## 빌드

```bash
cd tour_hub

# 홈(index.html) — tour_hub/index.html에 생성
python3 build.py

# 가이드·신뢰 페이지·sitemap — tour_hub/에 생성
python3 build_pages.py

# 배포 폴더로 바로 생성 + 내부 링크 전수 검사
python3 build_pages.py --out ../deploy_site --base https://trippick-kr.netlify.app --check-links
```

홈만 다시 만들 때는 `build.py`를, 가이드·CSS·sitemap만 다시 만들 때는 `build_pages.py`를 실행합니다.
`build_pages.py`는 `deploy_site/assets/site.css`를 `template.html`의 `<style>` + `content/pages.css`로 다시 씁니다.
`index.html`·`sitemap.xml`·`about/privacy/terms/contact.html`은 `build.py`/`build_pages.py`가 만든 것을 `deploy_site/`로 복사합니다.

## 호스팅

정적 사이트라 어디든 올릴 수 있습니다. Cloudflare Pages에서는

- 빌드 명령: 없음(비워 둠)
- 출력 디렉터리: `deploy_site`

로 지정하면 빌드 없이 `deploy_site/`가 그대로 서빙됩니다.

## 광고 슬롯

애드센스 승인 전에는 광고 코드를 넣지 않았습니다. 슬롯은 `class="adslot"` 컨테이너로 자리를 잡아 두고,
승인 전에는 **내부 추천 배너**가 보입니다(빈 광고 박스·깨진 레이아웃 없음).
승인 후에는 컨테이너 안의 주석을 풀고 `ca-pub-…`와 `data-ad-slot` 값만 바꾸면 됩니다.

- 홈: `build.py`의 `ad_slot()` — 코스/지역/트립닷컴 섹션 사이 3곳
- 가이드: `build_pages.py`의 `ad_slot()` — 상단·본문 중간·하단 3곳
- CSS: `template.html`의 `.adslot` 블록 (`:has(ins.adsbygoogle)`로 폴백 자동 숨김)

## 제휴 고지

이 사이트는 네이버 여행 커넥트·네이버 쇼핑 커넥트·쿠팡 파트너스·트립닷컴 파트너스에 참여하고 있습니다.
링크를 통한 예약·구매 시 판매자로부터 수수료를 받을 수 있으며, 구매자가 지불하는 가격에는 영향을 주지 않습니다.
가격·취소 규정은 각 판매처 상세페이지를 최종 기준으로 안내합니다.
