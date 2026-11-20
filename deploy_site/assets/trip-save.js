/* 트립픽 v25 — 이어보기·공유·저장 (assets/trip-save.js 로 복사됩니다)
   ------------------------------------------------------------------
   1) 최근 본 페이지 이어보기 바 (#contBar)
   2) 외부 공유 버튼 (링크 복사 · 모바일 navigator.share) + 복사됨 ✓ 토스트
   3) 내 여행 준비 요약 (#prepBox, 홈) — 퀴즈 결과·체크리스트 진행률·최근 본 곳
   모든 값은 브라우저 localStorage 에만 남고 서버로 보내지 않습니다. */
(function () {
  'use strict';

  var RECENT_KEY = 'trippick.recent.v1';
  var QUIZ_KEY = 'trippick.quiz.v1';
  var CL_KEY = 'trippick.checklist.v1';
  var MAX_RECENT = 5;

  /* ---------------- 토스트 ---------------- */
  var toastTimer = null;
  function toast(msg) {
    var t = document.querySelector('[data-toast]');
    if (!t) {
      t = document.createElement('div');
      t.className = 'toast';
      t.setAttribute('role', 'status');
      t.setAttribute('aria-live', 'polite');
      t.setAttribute('data-toast', '');
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add('on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove('on'); }, 2200);
  }
  window.tpToast = toast;

  /* ---------------- 저장소 ---------------- */
  function load(key, fallback) {
    try {
      var v = JSON.parse(localStorage.getItem(key) || 'null');
      return v == null ? fallback : v;
    } catch (e) { return fallback; }
  }
  function save(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {}
  }

  /* ---------------- 최근 본 페이지 ---------------- */
  var bar = document.getElementById('contBar');

  function pageInfo() {
    if (!bar) return null;
    var d = bar.dataset;
    if (!d.tpUrl || !d.tpTitle) return null;
    return { url: d.tpUrl, title: d.tpTitle, kind: d.tpKind || '페이지', img: d.tpImg || '' };
  }

  function pushRecent(info) {
    var list = load(RECENT_KEY, []);
    if (!Array.isArray(list)) list = [];
    list = list.filter(function (x) { return x && x.url && x.url !== info.url; });
    list.unshift({ url: info.url, title: info.title, kind: info.kind, img: info.img, t: Date.now() });
    save(RECENT_KEY, list.slice(0, MAX_RECENT));
    return list;
  }

  function renderBar() {
    if (!bar) return;
    var cur = pageInfo();
    var list = load(RECENT_KEY, []);
    if (!Array.isArray(list)) list = [];
    var others = list.filter(function (x) { return x && x.url && (!cur || x.url !== cur.url); }).slice(0, 3);
    if (!others.length) { bar.hidden = true; bar.innerHTML = ''; return; }
    var html = '<div class="cont-in"><span class="cont-k"><svg aria-hidden="true"><use href="#i-clock"/></svg>이어보기</span><div class="cont-row">';
    others.forEach(function (x) {
      html += '<a class="cont-item" href="' + x.url + '">' +
        (x.img ? '<img src="' + x.img + '" alt="" width="76" height="50" loading="lazy" />' : '') +
        '<span class="cont-t"><em>' + x.kind + '</em><b>' + x.title + '</b></span>' +
        '<svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>';
    });
    html += '</div><button type="button" class="cont-x" aria-label="이어보기 숨기기">×</button></div>';
    bar.innerHTML = html;
    bar.hidden = false;
    var x = bar.querySelector('.cont-x');
    if (x) x.addEventListener('click', function () { bar.hidden = true; });
  }

  if (bar) {
    var info = pageInfo();
    if (info) pushRecent(info);
    renderBar();
  }

  /* ---------------- 공유 ---------------- */
  function pageUrl() {
    var l = document.querySelector('link[rel="canonical"]');
    return (l && l.href) ? l.href : window.location.href;
  }
  function pageTitle() {
    var m = document.querySelector('meta[property="og:title"]');
    return (m && m.content) ? m.content : document.title;
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.top = '-1000px';
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand('copy');
        document.body.removeChild(ta);
        ok ? resolve() : reject(new Error('copy failed'));
      } catch (e) { reject(e); }
    });
  }

  /* 위임 처리 — 퀴즈 결과 카드처럼 나중에 그려지는 공유 영역도 같이 동작합니다. */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('[data-share-act]') : null;
    if (!btn) return;
    var box = btn.closest('[data-share]');
    if (!box) return;
    var act = btn.getAttribute('data-share-act');
    var url = box.getAttribute('data-share-url') || pageUrl();
    var title = box.getAttribute('data-share-title') || pageTitle();
    var text = box.getAttribute('data-share-text') || title;

    if (act === 'native' && navigator.share) {
      navigator.share({ title: title, text: text, url: url })
        .then(function () { toast('공유했어요'); })
        .catch(function () { /* 사용자가 공유를 닫았을 때는 아무 것도 하지 않음 */ });
      return;
    }
    /* 데스크톱(공유 시트 없음)이나 공유 실패 시에는 링크 복사로 떨어집니다. */
    copyText(url).then(function () {
      var old = btn.getAttribute('data-label') || btn.textContent;
      btn.setAttribute('data-label', old);
      btn.textContent = '복사됨 ✓';
      btn.classList.add('done');
      toast('복사됨 ✓ — 카톡·메모에 붙여넣으면 미리보기가 나옵니다');
      setTimeout(function () { btn.textContent = old; btn.classList.remove('done'); }, 2000);
    }, function () {
      toast('복사하지 못했어요. 주소창의 링크를 길게 눌러 복사해 주세요.');
    });
  });

  /* 모바일 공유 시트가 없는 기기에서는 ‘공유’ 버튼 라벨을 ‘링크 복사’로 정리합니다. */
  if (!navigator.share) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-share-act="native"]'), function (b) {
      b.hidden = true;
    });
  }

  /* ---------------- 내 여행 준비 요약 (홈 #prepBox) ---------------- */
  var prep = document.getElementById('prepBox');
  if (prep) {
    var quiz = load(QUIZ_KEY, null);
    var checks = load(CL_KEY, {}) || {};
    var done = Object.keys(checks).filter(function (k) { return checks[k]; }).length;
    var recent = load(RECENT_KEY, []);
    if (!Array.isArray(recent)) recent = [];
    var rows = [];
    if (quiz && quiz.name) {
      rows.push('<a class="prep-row" href="' + (quiz.url || '/quiz') + '">' +
        '<span class="prep-k">취향 퀴즈 결과</span>' +
        '<span class="prep-v"><b>' + quiz.name + '</b><em>' + (quiz.why || '내 취향에 맞는 도시') + '</em></span>' +
        '<svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>');
    }
    if (done) {
      rows.push('<a class="prep-row" href="/index.html#checklist">' +
        '<span class="prep-k">출국 준비 체크</span>' +
        '<span class="prep-v"><b>' + done + '개 체크됨</b><em>이 브라우저에 저장된 상태로 이어집니다</em></span>' +
        '<svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>');
    }
    if (recent.length) {
      var links = recent.slice(0, 3).map(function (x) {
        return '<a href="' + x.url + '"><em>' + x.kind + '</em><span>' + x.title + '</span></a>';
      }).join('');
      rows.push('<div class="prep-row prep-row--flat"><span class="prep-k">최근 본 곳</span>' +
        '<span class="prep-links">' + links + '</span></div>');
    }
    if (!rows.length) {
      prep.hidden = true;
    } else {
      prep.innerHTML = '<b class="prep-t"><svg aria-hidden="true"><use href="#i-check"/></svg>내 여행 준비 — 이 브라우저에 저장됨</b>' +
        '<div class="prep-rows">' + rows.join('') + '</div>' +
        '<p class="prep-note">퀴즈 결과·체크리스트·최근 본 페이지는 이 브라우저에만 저장되고 서버로 보내지 않습니다. 다른 기기와는 공유되지 않습니다.</p>';
      prep.hidden = false;
    }
  }
})();
