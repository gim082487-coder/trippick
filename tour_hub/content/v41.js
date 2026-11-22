/* 트립픽 v41 — 통합 퀵서치(Ctrl/⌘+K) · 찜 · 나란히 비교
   - 모든 페이지: 헤더 돋보기 → /search_index.json(빌드 생성)에서 도시·가이드·숙소·투어·맛집 검색
   - 모든 페이지: 찜(localStorage) · 헤더 하트 → 찜 목록
   - #tpCompare 가 있는 페이지(홈·/stays): 최대 3개 비교 바 + 비교 모달(localStorage)
   값은 빌드가 데이터에서 만든 것만 씁니다(없는 속성을 지어내지 않음). */
(function () {
  'use strict';
  var D = document;
  var hasLS = (function () { try { localStorage.setItem('tp.v41.t', '1'); localStorage.removeItem('tp.v41.t'); return true; } catch (e) { return false; } })();

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function read(key, def) {
    if (!hasLS) return def;
    try { var v = JSON.parse(localStorage.getItem(key)); return v == null ? def : v; } catch (e) { return def; }
  }
  function write(key, val) { if (!hasLS) return; try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {} }
  function toast(msg) {
    var t = D.querySelector('[data-toast]');
    if (!t) { t = D.createElement('div'); t.className = 'toast'; t.setAttribute('data-toast', ''); t.setAttribute('role', 'status'); D.body.appendChild(t); }
    t.textContent = msg;
    t.classList.add('on');
    clearTimeout(t._tpT);
    t._tpT = setTimeout(function () { t.classList.remove('on'); }, 2200);
  }
  function won(n) { return Math.round(Number(n) || 0).toLocaleString('ko-KR'); }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  /* =========================================================
     1. 통합 퀵서치
     ========================================================= */
  var QS = { modal: null, sheet: null, input: null, list: null, tabs: null, foot: null, idx: null, loading: false, err: false, tab: 'all', cur: -1, shown: [] };

  function buildQS() {
    if (QS.modal) return;
    var d = D.createElement('div');
    d.className = 'qs-modal';
    d.id = 'qsModal';
    d.hidden = true;
    d.innerHTML = '' +
      '<div class="qs-sheet" role="dialog" aria-modal="true" aria-labelledby="qsTitle">' +
      '  <div class="qs-top">' +
      '    <svg class="qs-ic" aria-hidden="true"><use href="#i-search"/></svg>' +
      '    <h2 class="sr-only" id="qsTitle">트립픽 통합 검색</h2>' +
      '    <input class="qs-in" id="qsInput" type="search" autocomplete="off" spellcheck="false" placeholder="도시·가이드·숙소·투어·맛집을 한 번에 (예: 오사카, 온천, 유니버설)" aria-label="통합 검색어" />' +
      '    <button class="qs-esc" type="button" data-qs-close aria-label="검색 닫기">Esc</button>' +
      '  </div>' +
      '  <div class="qs-tabs" role="tablist" aria-label="종류 선택" id="qsTabs"></div>' +
      '  <div class="qs-list" id="qsList" role="listbox" aria-label="검색 결과"></div>' +
      '  <div class="qs-foot"><span id="qsFoot">도시·가이드·숙소·투어·맛집을 한 번에 찾습니다</span>' +
      '    <span class="qs-keys"><b>↑↓</b> 이동 · <b>Enter</b> 열기 · <b>Esc</b> 닫기</span></div>' +
      '</div>';
    D.body.appendChild(d);
    QS.modal = d;
    QS.sheet = d.querySelector('.qs-sheet');
    QS.input = d.querySelector('#qsInput');
    QS.list = d.querySelector('#qsList');
    QS.tabs = d.querySelector('#qsTabs');
    QS.foot = d.querySelector('#qsFoot');

    d.addEventListener('mousedown', function (e) { if (e.target === d) closeQS(); });
    d.addEventListener('click', function (e) {
      if (e.target.closest('[data-qs-close]')) { closeQS(); return; }
      var tab = e.target.closest('[data-qs-tab]');
      if (tab) { QS.tab = tab.getAttribute('data-qs-tab'); syncQSTabs(); renderQS(); QS.input.focus(); return; }
      var row = e.target.closest('[data-qs-go]');
      if (row) { location.href = row.getAttribute('data-qs-go'); }
    });
    QS.input.addEventListener('input', function () { QS.cur = -1; renderQS(); });
    QS.input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!QS.shown.length) return;
        QS.cur = QS.cur < 0 ? 0 : clamp(QS.cur + (e.key === 'ArrowDown' ? 1 : -1), 0, QS.shown.length - 1);
        paintQS();
      } else if (e.key === 'Enter') {
        var pick = QS.cur >= 0 ? QS.shown[QS.cur] : QS.shown[0];
        if (pick) { e.preventDefault(); location.href = pick.u; }
      }
    });
  }

  function loadQS() {
    if (QS.idx || QS.loading) return;
    QS.loading = true;
    QS.cur = -1;
    renderQS();
    fetch('/search_index.json', { credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (data) {
        QS.idx = data;
        QS.loading = false;
        buildQSTabs();
        renderQS();
      })
      .catch(function () {
        QS.loading = false;
        QS.err = true;
        renderQS();
      });
  }

  var KIND_LABEL = { city: '도시', guide: '가이드', stay: '숙소', tour: '투어', food: '맛집' };
  var KIND_ORDER = ['city', 'guide', 'stay', 'tour', 'food'];

  function buildQSTabs() {
    var items = QS.idx.items || [];
    var counts = {};
    items.forEach(function (it) { counts[it.k] = (counts[it.k] || 0) + 1; });
    var html = '<button class="qs-tab on" type="button" role="tab" data-qs-tab="all" aria-selected="true">전체 <i>' + items.length + '</i></button>';
    KIND_ORDER.forEach(function (k) {
      if (!counts[k]) return;
      html += '<button class="qs-tab" type="button" role="tab" data-qs-tab="' + k + '" aria-selected="false">' + KIND_LABEL[k] + ' <i>' + counts[k] + '</i></button>';
    });
    QS.tabs.innerHTML = html;
    QS.foot.textContent = KIND_ORDER.filter(function (k) { return counts[k]; })
      .map(function (k) { return KIND_LABEL[k] + ' ' + counts[k]; }).join(' · ') + ' — 한 번에 찾습니다';
  }

  function syncQSTabs() {
    Array.prototype.forEach.call(QS.tabs.querySelectorAll('[data-qs-tab]'), function (b) {
      var on = b.getAttribute('data-qs-tab') === QS.tab;
      b.classList.toggle('on', on);
      b.setAttribute('aria-selected', on ? 'true' : 'false');
    });
  }

  function qsScore(it, toks, q) {
    var t = (it.t || '').toLowerCase();
    var body = (it.q || '').toLowerCase();
    var s = 0;
    for (var i = 0; i < toks.length; i++) {
      var k = toks[i];
      if (t.indexOf(k) >= 0) s += 8;
      else if (body.indexOf(k) >= 0) s += 3;
      else return -1;
    }
    if (q && t.indexOf(q) === 0) s += 10;
    if (q && t === q) s += 6;
    return s;
  }

  function renderQS() {
    if (!QS.list) return;
    if (QS.err) {
      QS.list.innerHTML = '<div class="qs-empty"><b>검색 색인을 불러오지 못했어요.</b><p>잠시 뒤 다시 열거나 <a href="/guides/">가이드 전체</a>에서 직접 찾아보세요.</p></div>';
      return;
    }
    if (!QS.idx) {
      QS.list.innerHTML = '<div class="qs-empty"><b>' + (QS.loading ? '검색 색인을 불러오는 중…' : '검색을 준비하고 있어요') + '</b></div>';
      return;
    }
    var q = (QS.input.value || '').trim().toLowerCase();
    var toks = q.split(/\s+/).filter(Boolean);
    var items = QS.idx.items || [];
    var out = [];
    if (!toks.length && QS.tab === 'all') {
      // 빈 검색어·전체 탭: 종류별 대표 3개씩만 보여 준다(도시에 쏠리지 않게)
      var seen = {};
      items.forEach(function (it, i) {
        seen[it.k] = (seen[it.k] || 0) + 1;
        if (seen[it.k] <= 3) out.push({ it: it, s: 0, i: i });
      });
    } else {
      items.forEach(function (it, i) {
        if (QS.tab !== 'all' && it.k !== QS.tab) return;
        var s = toks.length ? qsScore(it, toks, q) : 1;
        if (s >= 0) out.push({ it: it, s: s, i: i });
      });
    }
    var kindRank = { city: 0, guide: 1, stay: 2, tour: 3, food: 4 };
    function krank(k) { return kindRank[k] == null ? 9 : kindRank[k]; }
    out.sort(function (a, b) {
      if (b.s !== a.s) return b.s - a.s;
      var k = krank(a.it.k) - krank(b.it.k);
      if (k) return k;
      return a.i - b.i;
    });
    var limit = toks.length ? 40 : (QS.tab === 'all' ? 14 : 60);
    out = out.slice(0, limit);
    QS.shown = out.map(function (x) { return x.it; });
    if (QS.cur >= QS.shown.length) QS.cur = QS.shown.length - 1;

    if (!out.length) {
      QS.list.innerHTML = '<div class="qs-empty"><b>‘' + esc(QS.input.value.trim()) + '’ 결과가 없습니다.</b>' +
        '<p>도시 이름(오사카·파리), 테마(온천·야경·쇼핑), 상품 이름 일부로 다시 찾아보세요.</p></div>';
      return;
    }
    var html = '';
    if (!toks.length) html += '<p class="qs-lead">' + (QS.tab === 'all' ? '바로 가기 — 종류별 대표' : KIND_LABEL[QS.tab] + ' 전체') + '</p>';
    out.forEach(function (x, n) {
      var it = x.it;
      var title = esc(it.t);
      if (toks.length) {
        toks.forEach(function (k) {
          try { title = title.replace(new RegExp('(' + k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); } catch (e) {}
        });
      }
      html += '<a class="qs-row' + (n === QS.cur ? ' on' : '') + '" role="option" aria-selected="' + (n === QS.cur) + '" href="' + esc(it.u) + '" data-qs-go="' + esc(it.u) + '">' +
        '<span class="qs-k k-' + esc(it.k) + '">' + (KIND_LABEL[it.k] || it.k) + '</span>' +
        '<span class="qs-b"><b class="qs-t">' + title + '</b><span class="qs-m">' + esc(it.m) + '</span></span>' +
        '<span class="qs-go">열기</span></a>';
    });
    QS.list.innerHTML = html;
  }

  function paintQS() {
    var rows = QS.list.querySelectorAll('.qs-row');
    Array.prototype.forEach.call(rows, function (r, n) {
      r.classList.toggle('on', n === QS.cur);
      r.setAttribute('aria-selected', String(n === QS.cur));
    });
    var on = rows[QS.cur];
    if (on && on.scrollIntoView) on.scrollIntoView({ block: 'nearest' });
  }

  var qsLastFocus = null;
  function openQS() {
    buildQS();
    loadQS();
    qsLastFocus = D.activeElement;
    QS.modal.hidden = false;
    D.body.classList.add('qs-on');
    QS.input.focus();
    if (QS.input.select) QS.input.select();
  }
  function closeQS() {
    if (!QS.modal || QS.modal.hidden) return;
    QS.modal.hidden = true;
    D.body.classList.remove('qs-on');
    if (qsLastFocus && qsLastFocus.focus) qsLastFocus.focus();
  }

  D.addEventListener('click', function (e) {
    if (e.target.closest('[data-qs-open]')) { e.preventDefault(); openQS(); }
  });
  D.addEventListener('keydown', function (e) {
    var k = (e.key || '').toLowerCase();
    if ((e.metaKey || e.ctrlKey) && k === 'k') { e.preventDefault(); if (QS.modal && !QS.modal.hidden) closeQS(); else openQS(); return; }
    if (k === 'escape' && QS.modal && !QS.modal.hidden) { closeQS(); }
  });

  /* =========================================================
     2. 찜
     ========================================================= */
  var WKEY = 'trippick.wish.v1';
  var wish = read(WKEY, []);
  if (!Array.isArray(wish)) wish = [];
  var WL = { modal: null, body: null, count: null };

  function wishIdx(k) { for (var i = 0; i < wish.length; i++) if (wish[i].k === k) return i; return -1; }

  function syncWish() {
    Array.prototype.forEach.call(D.querySelectorAll('[data-wish]'), function (b) {
      var on = wishIdx(b.getAttribute('data-wish')) >= 0;
      b.setAttribute('aria-pressed', String(on));
      b.title = on ? '찜 해제' : '찜하기 (이 브라우저에 저장)';
      b.setAttribute('aria-label', on ? '찜 해제' : '찜하기');
      var t = b.querySelector('.wish-t');
      if (t) t.textContent = on ? '찜함' : '찜';
    });
    Array.prototype.forEach.call(D.querySelectorAll('[data-wl-count]'), function (n) {
      n.textContent = wish.length > 99 ? '99+' : String(wish.length);
      n.hidden = wish.length === 0;
    });
    if (WL.modal && !WL.modal.hidden) renderWish();
  }

  function toggleWish(btn) {
    var key = btn.getAttribute('data-wish');
    if (!key) return;
    var i = wishIdx(key);
    if (i >= 0) {
      wish.splice(i, 1);
      toast('찜에서 뺐어요');
    } else {
      var d = {};
      try { d = JSON.parse(btn.getAttribute('data-wish-item') || '{}'); } catch (e) {}
      wish.push({ k: key, n: d.n || '', u: d.u || '', i: d.i || '', p: d.p || '', t: d.t || (key.indexOf('stay:') === 0 ? '숙소' : '투어'), at: Date.now() });
      toast('찜했어요 · 헤더 ♥ 에서 모아 볼 수 있어요');
    }
    write(WKEY, wish.slice(-80));
    syncWish();
  }

  function buildWL() {
    if (WL.modal) return;
    var d = D.createElement('div');
    d.className = 'cmp-modal';
    d.id = 'wlModal';
    d.hidden = true;
    d.innerHTML = '<div class="cmp-sheet wl-sheet" role="dialog" aria-modal="true" aria-labelledby="wlTitle">' +
      '<div class="cmp-head"><div><b id="wlTitle">찜한 항목</b> <span class="hint">이 브라우저에만 저장됩니다</span></div>' +
      '<span class="cmp-head-act"><button class="cmp-close" type="button" data-wl-close>닫기</button></span></div>' +
      '<div class="cmp-scroll wl-body" id="wlBody"></div></div>';
    D.body.appendChild(d);
    WL.modal = d;
    WL.body = d.querySelector('#wlBody');
    d.addEventListener('click', function (e) {
      if (e.target === d || e.target.closest('[data-wl-close]')) { closeWL(); return; }
      var del = e.target.closest('[data-wl-del]');
      if (del) {
        var i = wishIdx(del.getAttribute('data-wl-del'));
        if (i >= 0) { wish.splice(i, 1); write(WKEY, wish); syncWish(); renderWish(); toast('찜에서 뺐어요'); }
      }
    });
  }

  function renderWish() {
    if (!WL.body) return;
    if (!wish.length) {
      WL.body.innerHTML = '<div class="qs-empty"><b>아직 찜한 항목이 없습니다.</b>' +
        '<p>숙소·투어 카드의 <b>♥</b> 를 누르면 여기에 모입니다. 숙소는 <a href="/stays">/stays</a>에서 비교해 보세요.</p></div>';
      return;
    }
    var html = '<div class="wl-list">';
    wish.slice().reverse().forEach(function (w) {
      html += '<div class="wl-row">' +
        (w.i ? '<img src="' + esc(w.i) + '" alt="" width="64" height="46" loading="lazy" />' : '<span class="wl-ph">' + esc(w.t) + '</span>') +
        '<span class="wl-t"><a href="' + esc(w.u) + '" target="_blank" rel="noopener sponsored"><b>' + esc(w.n) + '</b></a>' +
        '<span>' + esc(w.t) + (w.p ? ' · ' + esc(w.p) : '') + '</span></span>' +
        '<button class="cmpt-del" type="button" data-wl-del="' + esc(w.k) + '">빼기</button></div>';
    });
    html += '</div><p class="wl-note">찜은 이 브라우저(localStorage)에만 저장되고 서버로 보내지 않습니다. 다른 기기와 공유되지 않습니다.</p>';
    WL.body.innerHTML = html;
  }

  var wlLastFocus = null;
  function openWL() {
    buildWL();
    wlLastFocus = D.activeElement;
    renderWish();
    WL.modal.hidden = false;
    D.body.classList.add('qs-on');
    var c = WL.modal.querySelector('[data-wl-close]');
    if (c) c.focus();
  }
  function closeWL() {
    if (!WL.modal || WL.modal.hidden) return;
    WL.modal.hidden = true;
    D.body.classList.remove('qs-on');
    if (wlLastFocus && wlLastFocus.focus) wlLastFocus.focus();
  }

  D.addEventListener('click', function (e) {
    if (e.target.closest('[data-wl-open]')) { e.preventDefault(); openWL(); return; }
    var w = e.target.closest('[data-wish]');
    if (w) { e.preventDefault(); toggleWish(w); }
  });
  D.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && WL.modal && !WL.modal.hidden) closeWL();
  });
  syncWish();

  /* =========================================================
     3. 나란히 비교 (홈 투어 · /stays 숙소)
     ========================================================= */
  var dataEl = D.getElementById('tpCompare');
  if (!dataEl) return;
  var bar = D.getElementById('cmpBar');
  var modal = D.getElementById('cmpModal');
  var list = D.getElementById('cbList');
  var countEl = D.getElementById('cbCount');
  var openBtn = D.getElementById('cbOpen');
  var clearBtn = D.getElementById('cbClear');
  var closeBtn = D.getElementById('cmpClose');
  var modalBody = D.getElementById('cmpBody');
  if (!bar || !modal || !list || !modalBody) return;

  var MAP = {};
  try { MAP = JSON.parse(dataEl.textContent) || {}; } catch (e) { return; }
  var SKIND = dataEl.getAttribute('data-kind') || 'tour';
  var MAX = parseInt(dataEl.getAttribute('data-max') || '3', 10) || 3;
  var CKEY = 'trippick.cmp.' + SKIND + '.v1';
  var picked = read(CKEY, []);
  if (!Array.isArray(picked)) picked = [];
  picked = picked.filter(function (k) { return !!MAP[k]; }).slice(0, MAX);
  var cmpLastFocus = null;

  function savePicked() { write(CKEY, picked); }

  function syncButtons() {
    Array.prototype.forEach.call(D.querySelectorAll('[data-cmp-add]'), function (b) {
      var on = picked.indexOf(b.getAttribute('data-cmp-add')) >= 0;
      b.setAttribute('aria-pressed', String(on));
      b.textContent = on ? '담김' : '비교';
      b.title = on ? '비교에서 빼기' : '이 상품을 비교 바구니에 담기';
    });
  }

  function renderBar() {
    list.innerHTML = picked.map(function (k) {
      var t = MAP[k];
      return '<div class="cb-item"><img src="' + esc(t.im) + '" alt="" width="26" height="26" loading="lazy" />' +
        '<span>' + esc((t.n || '').length > 26 ? t.n.slice(0, 25) + '…' : t.n) + '</span>' +
        '<button class="cb-x" type="button" data-cmp-del="' + esc(k) + '" aria-label="비교에서 빼기">✕</button></div>';
    }).join('');
    var compact = window.matchMedia && window.matchMedia('(max-width:620px)').matches;
    countEl.textContent = compact ? picked.length + '개 선택' : picked.length + ' / ' + MAX;
    openBtn.disabled = picked.length < 2;
    openBtn.textContent = picked.length >= 2 ? '나란히 비교 (' + picked.length + ')' : '나란히 비교';
    bar.classList.toggle('on', picked.length > 0);
    D.body.classList.toggle('cmp-on', picked.length > 0);
    syncButtons();
  }

  function toggleCmp(k) {
    if (!MAP[k]) return;
    var i = picked.indexOf(k);
    if (i >= 0) picked.splice(i, 1);
    else {
      if (picked.length >= MAX) { toast('비교는 최대 ' + MAX + '개까지 담을 수 있어요. 하나를 빼고 담아주세요.'); return; }
      picked.push(k);
      toast(SKIND === 'stay' ? '비교에 담았어요 · ' + picked.length + '/' + MAX : '비교에 담았어요 · ' + picked.length + '/' + MAX);
    }
    savePicked();
    renderBar();
    if (!modal.hidden) { if (picked.length < 2) closeCmp(); else renderCmp(); }
  }

  function badges(t) {
    if (!t.bd || !t.bd.length) return '';
    return '<span class="cmpt-badges">' + t.bd.map(function (b) {
      return '<span class="db db--' + esc(b[1] || 'm') + '">' + esc(b[0]) + '</span>';
    }).join('') + '</span>';
  }

  function tourRows() {
    var best = Math.min.apply(null, picked.map(function (k) { return MAP[k].real || MAP[k].p; }));
    return [
      ['1인 상품가', function (t) {
        return '<b>' + won(t.p) + '원</b>' + (t.was && t.was > t.p ? '<br><s class="cmpt-soft">' + won(t.was) + '원</s>' : '') +
          (t.ptm ? '<br><span class="cmpt-soft">1팀(1척) 단가</span>' : '');
      }],
      ['현장 추가금', function (t) {
        if (!t.ex) return '<span class="cmpt-soft">' + (t.exas ? '금액 표기 없음<br>' + esc(t.exas) : '없음') + '</span>';
        return '<b>' + won(t.ex) + '원</b><br><span class="cmpt-soft">' + esc(t.exb || '') + '</span>';
      }],
      ['실질 1인가', function (t) {
        var v = t.real || t.p;
        return '<span class="cmpt-real">' + won(v) + '원</span>' + (v === best ? '<span class="cmpt-best">최저</span>' : '');
      }],
      ['평점·리뷰', function (t) {
        if (!t.rt) return '<span class="cmpt-soft">' + esc(t.book || '판매 조건 기준') + '</span>';
        return '<b>' + esc(t.rt) + '</b> / 5' + (t.rv ? '<br><span class="cmpt-soft">리뷰 ' + won(t.rv) + '개</span>' : '');
      }],
      ['출발·소요', function (t) {
        return esc(t.de || '현지 집결') + '<br><span class="cmpt-soft">' + esc(t.du || '') + (t.gui ? ' · ' + esc(t.gui) : '') + '</span>';
      }],
      ['포함 내역', function (t) { return '<span class="cmpt-soft">' + esc(t.inc || '상세페이지 확인') + '</span>'; }],
      ['특징', function (t) { return badges(t) || '<span class="cmpt-soft">—</span>'; }],
      ['취소 규정', function (t) { return esc(t.ca || '판매처 확인') + (t.caf ? '<br><span class="cmpt-soft">' + esc(t.caf) + '</span>' : ''); }],
      ['예약', function (t) {
        return '<a class="cmpt-cta" href="' + esc(t.u) + '" target="_blank" rel="noopener sponsored">' + esc(t.cta || '예약 페이지') + '</a>';
      }]
    ];
  }

  function stayRows() {
    var best = Math.min.apply(null, picked.map(function (k) { return MAP[k].p; }));
    return [
      ['1박 가격', function (t) {
        return '<span class="cmpt-real">' + won(t.p) + '원</span>' + (t.p === best ? '<span class="cmpt-best">최저</span>' : '') +
          '<br><span class="cmpt-soft">' + esc(t.pl || '1박·2인·세금 포함') + '</span>';
      }],
      ['평점·리뷰', function (t) {
        return '<b>' + Number(t.sc).toFixed(1) + '</b> / 10<br><span class="cmpt-soft">리뷰 ' + won(t.rv) + '개</span>';
      }],
      ['세부 점수', function (t) {
        var s = t.ss || {};
        var parts = ['청결도', '위치', '서비스', '시설'].filter(function (n) { return s[n]; })
          .map(function (n) { return n + ' <b>' + esc(s[n]) + '</b>'; });
        return parts.length ? '<span class="cmpt-sub">' + parts.join(' · ') + '</span>' : '<span class="cmpt-soft">—</span>';
      }],
      ['위치', function (t) {
        return '<b>' + esc(t.zone || '') + '</b>' + (t.ac ? '<br><span class="cmpt-soft">' + esc(t.ac) + '</span>' : '');
      }],
      ['테마·포인트', function (t) {
        var tags = (t.th || []).concat(t.pt || []);
        return tags.length ? '<span class="cmpt-soft">' + tags.map(esc).join(' · ') + '</span>' : '<span class="cmpt-soft">—</span>';
      }],
      ['가격 기준', function (t) { return '<span class="cmpt-soft">' + esc(t.basis || '') + '</span>'; }],
      ['특징', function (t) { return badges(t) || '<span class="cmpt-soft">—</span>'; }],
      ['예약', function (t) {
        return '<a class="cmpt-cta" href="' + esc(t.u) + '" target="_blank" rel="noopener sponsored">' + esc(t.cta || '트립닷컴에서 예약') + '</a>';
      }]
    ];
  }

  function renderCmp() {
    if (!picked.length) return;
    var rows = SKIND === 'stay' ? stayRows() : tourRows();
    var head = '<tr><th scope="col">항목</th>' + picked.map(function (k) {
      var t = MAP[k];
      return '<th scope="col"><div class="cmpt-prod"><img src="' + esc(t.im) + '" alt="" loading="lazy" />' +
        '<b>' + esc(t.n) + '</b><span>' + esc(t.sub || '') + '</span>' +
        '<button class="cmpt-del" type="button" data-cmp-del="' + esc(k) + '">이 항목 빼기</button></div></th>';
    }).join('') + '</tr>';
    var body = rows.map(function (r) {
      return '<tr><th scope="row">' + r[0] + '</th>' + picked.map(function (k) { return '<td>' + r[1](MAP[k]) + '</td>'; }).join('') + '</tr>';
    }).join('');
    modalBody.innerHTML = '<table class="cmpt"><caption class="sr-only">선택한 ' + (SKIND === 'stay' ? '숙소 ' : '상품 ') + picked.length +
      '개 비교표</caption><thead>' + head + '</thead><tbody>' + body + '</tbody></table>';
  }

  function openCmp() {
    if (picked.length < 2) return;
    cmpLastFocus = D.activeElement;
    renderCmp();
    modal.hidden = false;
    D.body.style.overflow = 'hidden';
    if (closeBtn) closeBtn.focus();
  }
  function closeCmp() {
    modal.hidden = true;
    D.body.style.overflow = '';
    if (cmpLastFocus && cmpLastFocus.focus) cmpLastFocus.focus();
  }

  D.addEventListener('click', function (e) {
    var add = e.target.closest('[data-cmp-add]');
    if (add) { e.preventDefault(); toggleCmp(add.getAttribute('data-cmp-add')); return; }
    var del = e.target.closest('[data-cmp-del]');
    if (del) { toggleCmp(del.getAttribute('data-cmp-del')); return; }
    if (e.target.closest('#cbOpen')) { openCmp(); return; }
    if (e.target.closest('#cbClear')) {
      picked.length = 0; savePicked(); renderBar();
      if (!modal.hidden) closeCmp();
      toast('비교 바구니를 비웠어요');
      return;
    }
    if (e.target.closest('#cmpClearAll')) {
      picked.length = 0; savePicked(); closeCmp(); renderBar();
      toast('비교 바구니를 비웠어요');
      return;
    }
    if (e.target.closest('#cmpClose') || e.target === modal) closeCmp();
  });
  D.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modal.hidden) closeCmp();
  });

  renderBar();
})();
