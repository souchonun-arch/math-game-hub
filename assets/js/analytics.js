/* ============================================================
   MGH Analytics — 答題明細採集（純外掛，零改動遊戲程式）
   ------------------------------------------------------------
   原理（12 款通用）：
   1) capture-phase click  →  記低學生揀咗邊個（dataset 優先，否則 textContent）
   2) MutationObserver     →  監察按鈕被加上「啱／錯」class
   3) 正解反推            →  答錯嗰刻，同組入面被標「啱」嘅按鈕就係正解
   4) 題目文字 + 結算欄位  →  逐 slug 設定表（DOM id 對照）

   資料格式（每學生一筆）：
   { v:1, game, ts, player, score, correct, wrong, timeMs,
     detail:[ {q, user, ans, ok, ms} ] }
   ============================================================ */
(function () {
  'use strict';
  if (window.MGH_NO_ANALYTICS) return;

  var GAME = window.MGH_GAME || {};
  var SLUG = GAME.id || 'unknown';
  var TITLE = GAME.title || SLUG;
  var KEY = 'mgh_analytics_v1';
  var NAME_KEY = 'mgh_board_name';

  /* ---------- 每款遊戲設定表（只寫 DOM id，唔碰遊戲邏輯） ---------- */
  /* 對錯 class 白名單（實測各款唔同，用多個候選覆蓋） */
  var RIGHT_CLS = ['right', 'ok', 'correct', 'reveal'];
  var WRONG_CLS = ['wrong', 'no', 'wrongpick'];
  var DIM_CLS = ['dim'];   // 答錯後其他選項會變暗

  var CFG = {
    'order-of-operations':      { q: ['#q-text-0', '#q-text-1', '#q-text-2'],  sel: '.ans-btn' },
    'decimal-fraction-percent': { q: ['#q-text-0', '#q-text-1', '#q-text-2'],  sel: '.ans-btn' },
    'unit-conversion':          { q: ['#qtext0', '#qtext1'],                 sel: '.optBtn' },
    'monopoly-mop':             { q: ['#qtext0', '#qtext1'],                 sel: '.optBtn' },
    'supermarket-tycoon':       { q: ['#qtext0', '#qtext1'],                 sel: '.optBtn' },
    'simple-interest-monster':  { q: ['#qt0', '#qt1'],                       sel: '.optBtn' },
    'decimal-fraction-mental':  { q: ['#qtext0', '#qtext1'],                 sel: '.optBtn' },
    'multiplication-race':      { q: ['#q1', '#q2'],                       sel: '#opts1 button, #opts2 button' },
    'percent-spirit-battle':    { q: ['#qo-0', '#qo-1'],                   sel: '.opt' },
    'vertical-multiplication-battle': { q: ['#qNum1', '#qNum2'],       sel: '.cell', perCell: true },
    'game24-invention':         { q: ['#qnum0', '#qnum1'],                 sel: '.key',  custom24: true },
    'mm-dm-measure':            { q: null,                                 sel: null,   customMM: true }
  };
  var cfg = CFG[SLUG] || null;
  if (!cfg) return;

  /* ---------- 狀態 ---------- */
  var st = {
    detail: [],
    correct: 0,
    wrong: 0,
    t0: Date.now(),
    pending: null,     // 最近一次點擊（用戶答案）
    current: null,     // 當前題目文字
    answered: {}       // 同一組按鈕去重（逐格題目會重複觸發）
  };

  function txt(el) {
    if (!el) return '';
    return (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 120);
  }
  /* 顯示用：清走「A 」「1.」呢類選項序號，淨係留答案內容 */
  function cleanAns(s) {
    return String(s == null ? '' : s)
      .replace(/^[A-Da-d]\s*[.、)]?\s*/, '')
      .replace(/^[0-9]+\s*[.、)]?\s*/, '')
      .trim().slice(0, 60);
  }
  function qNow() {
    var ids = cfg.q || [];
    for (var i = 0; i < ids.length; i++) {
      var el = document.querySelector(ids[i]);
      var t = txt(el);
      if (t) return t;
    }
    return '';
  }
  function qRoot() {
    // 由點擊嘅按鈕推斷同組容器（父層或最近 opts 容器）
    var b = st.pending && st.pending.el;
    return b ? b.parentElement : null;
  }
  function siblings(btn) {
    if (!btn || !btn.parentElement) return [];
    return Array.prototype.slice.call(btn.parentElement.querySelectorAll(cfg.sel));
  }
  function hasCls(el, list) {
    if (!el || !el.classList) return false;
    for (var i = 0; i < list.length; i++) {
      if (el.classList.contains(list[i])) return true;
    }
    return false;
  }
  function answerIn(group, skipEl) {
    // 從同組搵「啱」class 嘅按鈕 → 佢就係正解
    if (!group) return '';
    var all = Array.prototype.slice.call(group.querySelectorAll(cfg.sel));
    for (var i = 0; i < all.length; i++) {
      if (all[i] === skipEl) continue;
      if (hasCls(all[i], RIGHT_CLS)) return txt(all[i]);
    }
    // 搵唔到就退而求其次：用戶自己嗰個（佢可能就係啱嘅）
    return '';
  }

  /* ---------- 1) capture-phase click：記低用戶答案 ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest(cfg.sel) : null;
    if (!b) return;
    var ds = b.dataset || {};
    st.pending = {
      el: b,
      group: b.parentElement,
      user: cleanAns(ds.val || ds.ans || txt(b)),   // data-ai / data-oi 係索引號，唔係答案內容
      q: qNow(),                 // 即刻記低，唔等答完（可能即刻換題）
      at: Date.now()
    };
  }, true);

  /* ---------- 2) MutationObserver：監對錯 class ---------- */
  var mo = new MutationObserver(function (muts) {
    for (var i = 0; i < muts.length; i++) {
      var el = muts[i].target;
      if (!el || !el.classList || !st.pending) continue;
      var isRight = hasCls(el, RIGHT_CLS);
      var isWrong = hasCls(el, WRONG_CLS);
      if (!isRight && !isWrong) continue;

      var group = st.pending.group;
      var key = group ? (group.id || group) + '|' + txt(group) : txt(el);
      if (st.answered[key]) continue;

      // 逐格題目（直式乘法）：一條題可能多格，只記第一次判錯
      var ok = isRight;
      if (cfg.perCell && isWrong) {
        // 同題第一次判錯先記
        var qtxt = qNow();
        if (st.detail.some(function (d) { return d.q === qtxt && !d.ok; })) continue;
      }
      st.answered[key] = true;

      /* 正解：答對就係用戶揀嗰個；答錯就搵同組被標「啱」嗰個 */
      var ans = isRight ? st.pending.user : answerIn(group, st.pending.el);
      st.detail.push({
        q: st.pending.q || qNow(),
        user: st.pending.user,
        ans: cleanAns(ans || (isRight ? st.pending.user : '')),
        ok: ok,
        ms: st.pending.lastAt ? (st.pending.at - st.pending.lastAt) : 0,
        at: st.pending.at
      });
      if (ok) st.correct++; else st.wrong++;
      st.pending.lastAt = st.pending.at;
    }
  });
  function startObserve() {
    mo.observe(document.body, { subtree: true, attributes: true, attributeFilter: ['class'] });
  }
  if (document.body) startObserve();
  else document.addEventListener('DOMContentLoaded', startObserve);

  /* ---------- 3) 特別款：24 點 / 拖尺量度 ---------- */
  if (cfg.custom24) {
    // 監聽 .mistake-card 出現 → 由回顧卡抽錯題
    var mo2 = new MutationObserver(function () {
      document.querySelectorAll('.mistake-card').forEach(function (c) {
        if (c.getAttribute('data-seen')) return;
        c.setAttribute('data-seen', '1');
        var t = txt(c);
        st.wrong++;
        st.detail.push({ q: t.slice(0, 80), user: '', ans: '', ok: false, ms: 0, at: Date.now() });
      });
    });
    if (document.body) mo2.observe(document.body, { subtree: true, childList: true });
    else document.addEventListener('DOMContentLoaded', function () { mo2.observe(document.body, { subtree: true, childList: true }); });
  }
  if (cfg.customMM) {
    document.addEventListener('click', function (e) {
      var b = e.target && e.target.closest ? e.target.closest('.submit, button') : null;
      if (!b || !/提交|確定|OK|送出/.test(b.textContent || '')) return;
      var inp = document.querySelector('input.answer, .answer');
      if (!inp) return;
      st.pending = { el: inp, group: inp.parentElement, user: inp.value, at: Date.now() };
    }, true);
  }

  /* ---------- 4) 提交 ---------- */
  function scoreNow() {
    var m = (document.body.innerText || '').match(/(?:得分|分數|總分)\s*[:：]?\s*(\d{1,6})/);
    return m ? Number(m[1]) : 0;
  }
  window.MGHAnalytics = {
    game: SLUG,
    title: TITLE,
    /* 供 board.js 提交時一齊帶走 */
    snapshot: function () {
      var name = '';
      try { name = localStorage.getItem(NAME_KEY) || ''; } catch (e) { }
      return {
        v: 1,
        game: SLUG,
        title: TITLE,
        ts: Date.now(),
        player: name,
        score: scoreNow(),
        correct: st.correct,
        wrong: st.wrong,
        timeMs: Date.now() - st.t0,
        detail: st.detail.slice(-60)
      };
    }
  };
})();