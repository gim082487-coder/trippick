def coupons_page(out_root: Path, base: str) -> Path:
    """v57: 여행 할인코드·쿠폰 — 2026-11-26 확인된 트립닷컴 공식 코드만 수록.

    코드·조건·유효기간은 kr.trip.com/blog/trip-promotions/(2026-11-26 조회)에서 그대로 옮겼고,
    코드 문자열이 페이지에 없는 쿠폰(호텔·공항픽업·비즈니스석)은 '앱/링크에서 발급'으로만 적는다.
    클룩은 코드를 확인하지 못해 공식 쿠폰 페이지 링크만 둔다(가짜 코드 금지).
    """
    B = "https://kr.trip.com"
    AID = "Allianceid=11407530&SID=336341874"

    TRIP = [
        {
            "id": "flight-new",
            "badge": "신규회원",
            "title": "항공권 최대 22,000원 할인",
            "body": "트립닷컴에서 항공권을 처음 예약할 때 쓸 수 있습니다. 22만 원 이상 결제하면 5,000원, 55만 원 이상이면 22,000원이 빠집니다.",
            "code": "TRIPFLIGHT26KR",
            "cond": ["22만 원 이상 5,000원 · 55만 원 이상 22,000원", "신규회원 항공권 첫 예약", "결제 직전 입력"],
            "expiry": "2026.09.01 ~ 12.31",
            "cta": f"https://kr.trip.com/flights/?{AID}&trip_sub1=coupons_flight&trip_sub3=D21275837",
            "ctaLabel": "항공권 검색하며 적용",
        },
        {
            "id": "hotel-new",
            "badge": "앱 발급",
            "title": "호텔 신규 최대 10% (최대 13,000원) 할인",
            "body": "트립닷컴 앱을 내려받아 신규 가입하면 첫 호텔 예약에 쓸 수 있는 코드가 발급됩니다. 코드 문자열은 앱에서만 받을 수 있습니다.",
            "code": "",
            "cond": ["최대 10% · 최대 13,000원", "앱 가입 후 첫 호텔 예약", "앱에서 코드 발급"],
            "expiry": "앱 쿠폰함 표기 확인",
            "cta": f"https://kr.trip.com/hotels/?{AID}&trip_sub1=coupons_hotel&trip_sub3=D21372570",
            "ctaLabel": "호텔 최저가 보기",
        },
        {
            "id": "car-new",
            "badge": "신규회원",
            "title": "렌터카 최대 8% 할인",
            "body": "렌터카를 처음 예약하는 계정에 적용됩니다. 예약 화면에서 차량을 고른 뒤 결제 전에 코드를 넣습니다.",
            "code": "TRIPCAR8",
            "cond": ["최대 8%", "렌터카 첫 예약", "결제 전 코드 입력"],
            "expiry": "페이지 표기 확인",
            "cta": f"https://kr.trip.com/carhire/?{AID}&trip_sub1=coupons_car&trip_sub3=D21303312",
            "ctaLabel": "렌터카 검색하며 적용",
        },
        {
            "id": "transfer-new",
            "badge": "앱 전용",
            "title": "공항픽업 최대 10% 할인 (항공권 예약자는 12%)",
            "body": "앱 홈에서 공항픽업을 열면 10% 쿠폰이 바로 발급됩니다. 이미 트립닷컴에서 항공권을 예약했다면 12%까지 적용됩니다.",
            "code": "",
            "cond": ["앱에서만 쿠폰 발급", "픽업 첫 이용 10% · 항공권 예약자 12%", "항공편 지연 시 추가 요금 없음"],
            "expiry": "앱 쿠폰함 표기 확인",
            "cta": f"https://kr.trip.com/airport-transfers/?{AID}&trip_sub1=coupons_transfer&trip_sub3=D21303312",
            "ctaLabel": "공항픽업 보기",
        },
        {
            "id": "tour-ticket",
            "badge": "코드",
            "title": "투어·티켓 최대 6% 할인",
            "body": "입장권·투어·액티비티 결제에 쓰는 코드입니다. 도시별 상품 상세의 '쿠폰' 칸에 넣으면 적용 금액이 표시됩니다.",
            "code": "TRIPNAVER",
            "cond": ["투어·티켓 최대 6%", "상품별 적용 여부 다름", "결제 화면에서 최종 확인"],
            "expiry": "페이지 표기 확인",
            "cta": f"https://kr.trip.com/things-to-do/?{AID}&trip_sub1=coupons_tour&trip_sub3=D21303312",
            "ctaLabel": "투어·티켓 보기",
        },
        {
            "id": "biz-first",
            "badge": "링크 발급",
            "title": "비즈니스석·일등석 최대 60,000원 할인",
            "body": "비즈니스·일등석 예약에 적용되는 코드입니다. 코드는 트립닷컴 프로모션 페이지의 '비즈니스 항공권 할인 예약하기' 버튼에서 확인합니다.",
            "code": "",
            "cond": ["최대 60,000원", "비즈니스석·일등석", "프로모션 페이지에서 코드 확인"],
            "expiry": "페이지 표기 확인",
            "cta": "https://kr.trip.com/blog/trip-promotions/",
            "ctaLabel": "프로모션 페이지에서 코드 확인",
            "nofollow": True,
        },
    ]

    ALWAYS = [
        ("트래블카드", "해외 결제 수수료 0%", "트래블월렛·트래블로그·토스뱅크는 해외 가맹점 결제 수수료가 0%입니다. 3만 엔을 ATM에서 인출할 때 일반 카드와 6,568원 차이가 납니다.",
         "guides/travel-card-fees-comparison.html", "카드 3종 수수료 비교"),
        ("환전", "공항 37,520원 vs 앱 1,460원", "10만 엔을 바꿀 때 인천공항 환전 37,520원, 시내 14,590원, 앱 환전 우대 1,460원입니다. 같은 날 고시 기준입니다.",
         "guides/travel-card-packing-guide.html", "환전 수수료·짐싸기"),
        ("라운지", "PP·더라운지 카드 확인", "공항 라운지는 카드에 붙은 PP와 더라운지 중 어느 쪽인지에 따라 쓸 수 있는 라운지가 달라집니다.",
         "guides/airport-lounge-card-guide.html", "라운지 카드 비교"),
    ]

    cards = []
    for c in TRIP:
        code_html = (
            f'<div class="cpn-code"><code>{esc(c["code"])}</code>'
            f'<button type="button" class="cpn-copy" data-copy="{esc(c["code"])}" aria-label="{esc(c["code"])} 복사">복사</button></div>'
            if c["code"] else
            '<div class="cpn-code cpn-code--none"><span>코드 문자열 없이 앱·링크에서 발급됩니다</span></div>'
        )
        rel = "noopener" if c.get("nofollow") else "noopener sponsored"
        cards.append(f"""<article class="cpn" id="cpn-{c['id']}">
  <div class="cpn-top"><span class="cpn-p">트립닷컴</span><span class="cpn-b">{esc(c['badge'])}</span></div>
  <b class="cpn-t">{esc(c['title'])}</b>
  <p class="cpn-d">{esc(c['body'])}</p>
  {code_html}
  <ul class="cpn-cond">{''.join(f'<li>{esc(x)}</li>' for x in c['cond'])}</ul>
  <div class="cpn-foot"><span class="cpn-exp">유효 {esc(c['expiry'])}</span>
    <a class="cpn-go" href="{esc(c['cta'])}" target="_blank" rel="{rel}">{esc(c['ctaLabel'])} →</a></div>
</article>""")

    always_cards = "".join(
        f'<a class="cpn cpn--always" href="../{href}">'
        f'<div class="cpn-top"><span class="cpn-p">{esc(kind)}</span><span class="cpn-b">쿠폰 없이</span></div>'
        f'<b class="cpn-t">{esc(title)}</b><p class="cpn-d">{esc(body)}</p>'
        f'<span class="cpn-go">{esc(label)} →</span></a>'
        for kind, title, body, href, label in ALWAYS
    )

    faq = [
        ("트립닷컴 할인코드는 어디에 입력하나요?",
         "결제 화면의 쿠폰·프로모션 코드 입력 칸에 넣습니다. 항공권은 승객 정보를 넣고 결제 직전 화면, 호텔은 결제 수단을 고르는 화면에 칸이 있습니다. 적용 금액이 표시되지 않으면 조건(최소 결제액·신규회원·상품)이 맞지 않는 경우입니다."),
        ("신규회원 할인은 계정마다 한 번인가요?",
         "트립닷컴 신규회원 쿠폰은 계정 기준으로 한 번 발급됩니다. 같은 사람이 계정을 여러 개 만들어 쓰는 것은 약관상 제한될 수 있고, 예약 후 취소·재예약 시 쿠폰이 돌아오지 않는 경우가 있습니다."),
        ("클룩 할인코드는 왜 코드가 없나요?",
         "이 페이지는 2026년 11월 26일 기준으로 코드 문자열과 조건이 공개된 것만 싣습니다. 클룩은 쿠폰이 앱·계정·결제 수단별로 발급되어 공개 문자열을 확인하지 못했으므로, 공식 쿠폰 페이지로만 연결합니다. 확인되는 대로 코드를 추가합니다."),
        ("쿠폰과 카드 할인을 같이 쓸 수 있나요?",
         "보통 쿠폰 1개와 카드 할인은 함께 적용되지만, 상품·결제 수단에 따라 하나만 적용됩니다. 결제 화면의 할인 내역에 두 줄이 모두 표시되는지 확인하고, 표시되지 않으면 결제를 진행하지 마세요."),
        ("유효기간이 지난 코드를 넣으면 어떻게 되나요?",
         "결제 화면에 '사용할 수 없는 코드'로 표시되고 금액은 그대로입니다. 이 페이지는 유효기간이 확인된 코드만 적고, 기간이 끝나면 다음 업데이트에서 지웁니다. 결제 전에 트립닷컴 프로모션 페이지에서 한 번 더 확인하세요."),
    ]
    faq_html = "".join(
        f'<details class="fq"><summary><span class="fq-q"><b>Q.</b> {esc(q)}</span>'
        f'<span class="fq-ic" aria-hidden="true"></span></summary><div class="fq-a">{esc(a)}</div></details>'
        for q, a in faq
    )

    body = f"""<div class="pg-hero">
  <div class="wrap">
    <nav class="pg-crumb" aria-label="위치"><a href="index.html">홈</a><i></i><b>할인쿠폰</b></nav>
    <span class="pg-kicker">COUPON</span>
    <div class="pg-head">
      <h1>여행 할인코드, <em>확인된 것만</em> 모았습니다</h1>
      <p class="dek">트립닷컴 공식 프로모션 페이지에서 2026년 11월 26일 확인한 코드와 조건입니다. 코드 문자열이 공개되지 않은 쿠폰은 '앱·링크 발급'으로만 적고, 클룩은 공식 쿠폰 페이지로 연결합니다.</p>
      <div class="pg-meta">
        <span><b>트립픽 편집</b></span><i></i><span>최종 검증일 2026.11.26</span><i></i>
        <span>코드 {sum(1 for c in TRIP if c['code'])}개 · 앱 발급 {sum(1 for c in TRIP if not c['code'])}개</span>
      </div>
    </div>
  </div>
</div>

<div class="pg-body">
  <div class="wrap">
    <div class="pg-grid">
      <article class="doc">
        <div class="cpn-note">쿠폰 조건·유효기간은 판매처가 바꿀 수 있습니다. 결제 화면에 표시된 최종 금액이 기준이고, 이 페이지는 <b>2026-11-26 확인값</b>만 싣습니다.</div>
        <div class="tb">
          <div class="tb-h"><b>한눈에 보는 트립닷컴 코드</b><span>kr.trip.com 프로모션 페이지 2026-11-26</span></div>
          <div class="tb-scroll">
            <table>
              <thead><tr><th>대상</th><th>혜택</th><th>코드</th><th>조건</th></tr></thead>
              <tbody>
                <tr><td>항공권(신규)</td><td>최대 22,000원</td><td><b>TRIPFLIGHT26KR</b></td><td>22만↑ 5,000 · 55만↑ 22,000</td></tr>
                <tr><td>렌터카(신규)</td><td>최대 8%</td><td><b>TRIPCAR8</b></td><td>첫 예약</td></tr>
                <tr><td>투어·티켓</td><td>최대 6%</td><td><b>TRIPNAVER</b></td><td>상품별 적용 여부 다름</td></tr>
                <tr><td>호텔(신규)</td><td>최대 10%·13,000원</td><td>앱 발급</td><td>앱 가입 후 첫 예약</td></tr>
                <tr><td>공항픽업</td><td>10% (항공 예약자 12%)</td><td>앱 발급</td><td>앱 전용</td></tr>
                <tr><td>비즈니스·일등석</td><td>최대 60,000원</td><td>링크 발급</td><td>프로모션 페이지에서 확인</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <h2 id="trip">트립닷컴 할인코드 6개</h2>
        <div class="cpn-grid">{''.join(cards)}</div>

        <h2 id="klook">클룩(Klook) 쿠폰</h2>
        <div class="cpn-grid">
          <a class="cpn cpn--always" href="https://www.klook.com/ko/coupons/?aid=144067" target="_blank" rel="noopener sponsored">
            <div class="cpn-top"><span class="cpn-p">클룩</span><span class="cpn-b">공식 페이지</span></div>
            <b class="cpn-t">진행 중인 쿠폰·프로모션 목록</b>
            <p class="cpn-d">클룩은 쿠폰을 앱·계정·결제 수단별로 발급해서 공개된 코드 문자열을 확인하지 못했습니다. 공식 쿠폰 페이지에서 내 계정에 발급된 쿠폰과 적용 조건을 확인하세요.</p>
            <span class="cpn-go">클룩 쿠폰 페이지 열기 →</span>
          </a>
        </div>

        <h2 id="always">코드 없이 상시 적용되는 혜택</h2>
        <div class="cpn-grid">{always_cards}</div>

        <h2 id="rules">쓰기 전에 확인할 것</h2>
        <ul>
          <li><b>결제 화면 금액이 기준</b> — 코드를 넣고 할인 줄이 생겼는지, 최종 결제액이 줄었는지 확인한 뒤 결제하세요.</li>
          <li><b>신규회원 조건</b> — 계정당 1회이고, 취소 후 재예약 때 쿠폰이 돌아오지 않는 경우가 있습니다.</li>
          <li><b>앱 전용</b> — 호텔·공항픽업 쿠폰은 앱에서만 발급됩니다. 웹에서는 코드 칸이 보여도 적용되지 않습니다.</li>
          <li><b>중복</b> — 쿠폰 1개와 카드 할인은 함께 적용되는 경우가 많지만, 상품에 따라 하나만 적용됩니다.</li>
          <li><b>유효기간</b> — 기간이 지나면 자동으로失效됩니다. 이 페이지는 확인된 기간만 적고, 끝나면 지웁니다.</li>
        </ul>

        <h2 id="faq">자주 묻는 질문</h2>
        {faq_html}
      </article>
      <aside class="pg-side">
        <div class="side-card">
          <b>쿠폰과 함께 쓰는 도구</b>
          <a href="stays.html">찐숙소 126곳 — 1박 최저가</a>
          <a href="passes.html">교통패스 본전 계산기</a>
          <a href="exchange.html">환율·면세 계산기</a>
          <a href="checklist.html">여행 준비 D-Day</a>
        </div>
      </aside>
    </div>
  </div>
</div>
<style>
.cpn-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:12px 0 6px}}
@media(max-width:700px){{.cpn-grid{{grid-template-columns:1fr}}}}
.cpn{{display:flex;flex-direction:column;gap:7px;border:1px solid var(--line);border-radius:16px;background:#fff;padding:15px 16px}}
.cpn:hover{{border-color:var(--blue);box-shadow:0 3px 14px rgba(16,32,46,.07);text-decoration:none}}
.cpn-top{{display:flex;align-items:center;gap:6px}}
.cpn-p{{font-size:11.5px;font-weight:800;color:var(--blue-600);letter-spacing:.02em}}
.cpn-b{{font-size:10.5px;font-weight:800;color:var(--ink-2);background:var(--soft);border-radius:999px;padding:2px 8px}}
.cpn-t{{font-size:15.5px;font-weight:800;color:var(--navy);line-height:1.35}}
.cpn-d{{margin:0;font-size:12.8px;color:var(--ink-3);line-height:1.62}}
.cpn-code{{display:flex;align-items:center;gap:8px;border:1px dashed var(--blue);border-radius:11px;background:var(--blue-soft);padding:9px 11px}}
.cpn-code code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:14px;font-weight:800;color:var(--navy);letter-spacing:.04em}}
.cpn-copy{{margin-left:auto;border:1px solid var(--blue);background:#fff;color:var(--blue-600);font-size:11.5px;font-weight:800;border-radius:8px;padding:5px 10px;cursor:pointer}}
.cpn-copy.on{{background:var(--blue);color:#fff}}
.cpn-code--none{{border-style:solid;border-color:var(--line);background:var(--soft);font-size:11.8px;color:var(--ink-3)}}
.cpn-cond{{margin:2px 0 0;padding-left:17px;font-size:12.2px;color:var(--ink-3);line-height:1.6}}
.cpn-foot{{margin-top:auto;display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding-top:4px}}
.cpn-exp{{font-size:11.5px;font-weight:700;color:var(--ink-3)}}
.cpn-go{{margin-left:auto;font-size:12.2px;font-weight:800;color:var(--blue-600)}}
.cpn-note{{border:1px solid var(--line);border-left:3px solid var(--blue);border-radius:10px;background:#fff;padding:11px 13px;font-size:12.6px;color:var(--ink-2);line-height:1.6}}
</style>"""

    cpn_ld = {
        "@type": "CollectionPage",
        "name": "여행 할인코드·쿠폰 — 트립닷컴·클룩 (2026년 11월)",
        "description": "트립닷컴 공식 할인코드 6개와 클룩 쿠폰 페이지, 코드 없이 적용되는 여행 혜택을 2026년 11월 26일 기준으로 정리했습니다.",
        "url": f"{base.rstrip('/')}/coupons.html",
        "inLanguage": "ko-KR",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(TRIP),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": {
                        "@type": "Offer",
                        "name": c["title"],
                        "description": " · ".join(c["cond"]),
                        "url": f"{base.rstrip('/')}/coupons.html#cpn-{c['id']}",
                        "availability": "https://schema.org/InStock",
                        "seller": {"@type": "Organization", "name": "Trip.com"},
                    },
                }
                for i, c in enumerate(TRIP)
            ],
        },
    }
    jsonld = graph_ld(
        cpn_ld,
        {
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faq
            ],
        },
        breadcrumb_ld(base, [("트립픽", ""), ("할인쿠폰", None)]),
    )

    script = """<script>
(function () {
  var btns = document.querySelectorAll('[data-copy]');
  Array.prototype.forEach.call(btns, function (btn) {
    btn.addEventListener('click', function () {
      var v = btn.getAttribute('data-copy') || '';
      var done = function () {
        var old = btn.getAttribute('data-old') || btn.textContent;
        btn.setAttribute('data-old', old);
        btn.textContent = '복사됨 ✓';
        btn.classList.add('on');
        setTimeout(function () { btn.textContent = old; btn.classList.remove('on'); }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(v).then(done, function () { done(); });
      } else {
        var ta = document.createElement('textarea');
        ta.value = v;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); } catch (err) {}
        document.body.removeChild(ta);
        done();
      }
    });
  });
})();
</script>"""

    return page(
        out_root,
        "coupons.html",
        title="여행 할인코드·쿠폰 — 트립닷컴·클룩 (2026년 11월) | 트립픽",
        desc="2026-11-26 확인된 트립닷컴 할인코드 TRIPFLIGHT26KR(항공 최대 22,000원)·TRIPCAR8(렌터카 8%)·TRIPNAVER(투어 6%), 앱 발급 호텔·공항픽업 쿠폰과 클룩 쿠폰 페이지, 카드·환전·라운지 상시 혜택을 한 페이지에 정리했습니다.",
        body=body,
        base=base,
        active="coupons",
        keywords="트립닷컴 할인코드, 트립닷컴 쿠폰, 클룩 할인코드, 여행 할인쿠폰, TRIPFLIGHT26KR, TRIPCAR8, TRIPNAVER, 호텔 할인코드, 항공권 할인, 공항픽업 쿠폰",
        jsonld=jsonld,
        scripts=script,
    )


