/* =====================================================================
   v44 — /sos 「여행 중 위기상황 SOS」
   서버가 10개국 패널을 모두 그려 두고(검색·JS 꺼짐 대비), 이 스크립트는
   ① 국가 탭 전환 ② 현지어 카드 전체 화면 보기 만 맡는다.
   ===================================================================== */
(function () {
  'use strict';
  var D = document;
  var KEY = 'trippick.sos.cc';
  var cc = D.getElementById('sosCC');
  var host = D.getElementById('sosPanels');
  if (!cc || !host) return;

  var tabs = Array.prototype.slice.call(cc.querySelectorAll('[data-cc]'));
  var panels = Array.prototype.slice.call(host.querySelectorAll('[data-panel-cc]'));
  if (!tabs.length || !panels.length) return;

  function read() {
    try { return localStorage.getItem(KEY) || ''; } catch (e) { return ''; }
  }
  function save(code) {
    try { localStorage.setItem(KEY, code); } catch (e) {}
  }
  function known(code) {
    for (var i = 0; i < panels.length; i++) if (panels[i].getAttribute('data-panel-cc') === code) return true;
    return false;
  }

  var current = '';
  function select(code, opts) {
    if (!known(code)) return;
    current = code;
    tabs.forEach(function (t) {
      var on = t.getAttribute('data-cc') === code;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      if (on && opts && opts.scrollTab && t.scrollIntoView) {
        try { t.scrollIntoView({ inline: 'center', block: 'nearest', behavior: 'smooth' }); } catch (e) {}
      }
    });
    panels.forEach(function (p) {
      p.hidden = p.getAttribute('data-panel-cc') !== code;
    });
    if (opts && opts.remember) save(code);
  }

  cc.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-cc]') : null;
    if (!b) return;
    select(b.getAttribute('data-cc'), { remember: true, scrollTab: true });
  });

  /* 키보드 좌우 이동 — 탭 목록 안에서만 */
  cc.addEventListener('keydown', function (e) {
    var k = e.key;
    if (k !== 'ArrowRight' && k !== 'ArrowLeft' && k !== 'Home' && k !== 'End') return;
    var idx = tabs.indexOf(D.activeElement);
    if (idx < 0) return;
    e.preventDefault();
    var next = k === 'Home' ? 0 : k === 'End' ? tabs.length - 1 : (idx + (k === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    tabs[next].focus();
    select(tabs[next].getAttribute('data-cc'), { remember: true, scrollTab: true });
  });

  /* 시작 국가 — 저장값 → 주소 #jp → 첫 번째 */
  var start = read();
  var hash = (location.hash || '').replace(/^#/, '').toUpperCase();
  if (known(hash)) start = hash;
  if (!known(start)) start = panels[0].getAttribute('data-panel-cc');
  select(start, { scrollTab: false });

  /* ---- 현지어 카드 → 전체 화면 ---- */
  var ov = D.getElementById('sosOv');
  if (!ov) return;
  var ovKo = D.getElementById('sosOvKo');
  var ovLocal = D.getElementById('sosOvLocal');
  var ovPron = D.getElementById('sosOvPron');
  var ovEn = D.getElementById('sosOvEn');
  var lastFocus = null;
  var prevOverflow = '';

  function open(card) {
    lastFocus = card;
    ovKo.textContent = card.getAttribute('data-ko') || '';
    ovLocal.textContent = card.getAttribute('data-local') || '';
    ovPron.textContent = card.getAttribute('data-pron') || '';
    ovEn.textContent = card.getAttribute('data-en') || '';
    prevOverflow = D.body.style.overflow;
    D.body.style.overflow = 'hidden';
    ov.hidden = false;
    var x = D.getElementById('sosOvX');
    if (x) x.focus();
  }
  function close() {
    if (ov.hidden) return;
    ov.hidden = true;
    D.body.style.overflow = prevOverflow;
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  host.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-ko]') : null;
    if (b) open(b);
  });
  var xBtn = D.getElementById('sosOvX');
  if (xBtn) xBtn.addEventListener('click', close);
  ov.addEventListener('click', function (e) { if (e.target === ov) close(); });
  D.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.key === 'Esc') close();
  });
})();
