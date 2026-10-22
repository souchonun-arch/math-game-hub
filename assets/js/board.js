/*!
 * 數學遊戲總站 — 本機排行榜（board.js）
 * ------------------------------------------------------------------
 * 純外掛模組，由 scripts/build.py 自動注入每一款遊戲嘅 play.html 最尾。
 * 完全唔會改動遊戲內部程式，只係加一個浮動掣 + 面板。
 *
 * 運作方式：
 *   1. 學生撳 🏆 掣 → 模組掃描畫面上嘅文字，自動偵測分數
 *   2. 學生填名（會記住）→ 提交 → 存入 localStorage
 *   3. 同一部電腦嘅紀錄會累積，Top 20 排行榜
 *   4. 老師可以「匯出」一段文字，貼去 /board/ 合併成全班榜
 *
 * 儲存鍵：mgh_board_v1（全站共用，因為全部遊戲同一個 origin）
 */
(function () {
  'use strict';

  var KEY = 'mgh_board_v1';
  var KEY_NAME = 'mgh_board_name';
  var MAX_ROWS = 20;
  var MAX_PER_GAME = 200;

  var G = window.MGH_GAME || {};
  var GAME_ID = G.id || 'unknown';
  var GAME_TITLE = G.title || '呢個遊戲';

  /* ---------- 存取 ---------- */
  function loadAll() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return {};
      var o = JSON.parse(raw);
      return (o && typeof o === 'object' && o.games) ? o.games : {};
    } catch (e) { return {}; }
  }
  function saveAll(games) {
    try { localStorage.setItem(KEY, JSON.stringify({ v: 1, games: games })); }
    catch (e) { /* 容量爆咗就靜默 */ }
  }
  function rows() {
    var all = loadAll();
    return Array.isArray(all[GAME_ID]) ? all[GAME_ID] : [];
  }
  function saveRows(list) {
    var all = loadAll();
    all[GAME_ID] = list.slice(0, MAX_PER_GAME);
    saveAll(all);
  }
  function clean(s) {
    return String(s == null ? '' : s).replace(/[~;|\r\n]+/g, ' ').trim().slice(0, 24);
  }

  /* ---------- 自動偵測分數 ---------- */
  var PATTERNS = [
    { re: /(?:總分|總得分|得分|分數|積分)\s*[:：]?\s*(\d{1,7})/g, label: '分數' },
    { re: /score\s*[:：]?\s*(\d{1,7})/gi, label: 'score' },
    { re: /答對\s*[:：]?\s*(\d{1,4})\s*題/g, label: '答對題數' },
    { re: /答啱\s*[:：]?\s*(\d{1,4})\s*題/g, label: '答啱題數' },
    { re: /正確\s*[:：]?\s*(\d{1,4})\s*(?:題|道)/g, label: '正確題數' },
    { re: /(\d{1,7})\s*分/g, label: '分' },
    { re: /連對\s*[:：]?\s*(\d{1,4})/g, label: '連對' }
  ];

  function detectScore() {
    var text = '';
    try { text = (document.body && document.body.innerText) || ''; } catch (e) { return null; }
    if (!text) return null;
    if (text.length > 20000) text = text.slice(-20000); // 結算通常喺尾
    var found = [];
    PATTERNS.forEach(function (p) {
      var m, re = new RegExp(p.re.source, p.re.flags);
      while ((m = re.exec(text)) !== null) {
        var v = parseInt(m[1], 10);
        if (!isNaN(v) && v > 0) found.push({ v: v, label: p.label });
        if (found.length > 40) break;
      }
    });
    if (!found.length) return null;
    // 出現最多次嘅數值最可信；平手取最大
    var tally = {};
    found.forEach(function (f) { tally[f.v] = (tally[f.v] || 0) + 1; });
    var best = null, bestN = 0;
    Object.keys(tally).forEach(function (k) {
      var n = tally[k];
      if (n > bestN || (n === bestN && Number(k) > Number(best))) { bestN = n; best = k; }
    });
    return best ? parseInt(best, 10) : null;
  }

  /* ---------- 樣式 ---------- */
  var CSS = [
    '#mgh-board-root{position:fixed;right:14px;bottom:14px;z-index:2147483000;font-family:-apple-system,BlinkMacSystemFont,"PingFang HK","Microsoft JhengHei",sans-serif;}',
    '#mgh-board-btn{width:52px;height:52px;border-radius:50%;border:none;cursor:pointer;font-size:24px;line-height:1;',
    'background:linear-gradient(135deg,#f59e0b,#ef4444);color:#fff;box-shadow:0 6px 18px rgba(0,0,0,.45);',
    'display:flex;align-items:center;justify-content:center;opacity:.92;transition:transform .18s;}',
    '#mgh-board-btn:hover{transform:scale(1.08);opacity:1;}',
    '#mgh-board-panel{position:fixed;right:14px;bottom:76px;width:320px;max-width:calc(100vw - 28px);max-height:74vh;overflow:auto;',
    'background:#141c33;color:#eaf1ff;border:1px solid #33415c;border-radius:16px;box-shadow:0 18px 50px rgba(0,0,0,.6);padding:14px;}',
    '#mgh-board-panel[hidden]{display:none;}',
    '.mgh-h{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px;}',
    '.mgh-h b{font-size:15px;}',
    '.mgh-x{background:none;border:none;color:#93a4c4;font-size:20px;cursor:pointer;line-height:1;padding:0 4px;}',
    '.mgh-sub{font-size:12px;color:#93a4c4;margin:0 0 10px;}',
    '.mgh-row{display:flex;gap:6px;margin-bottom:8px;}',
    '.mgh-inp{flex:1;min-width:0;font-size:16px;padding:8px 10px;border-radius:9px;border:1px solid #3a4667;background:#0e1526;color:#eaf1ff;}',
    '.mgh-inp:focus{outline:2px solid #f59e0b;outline-offset:-1px;}',
    '.mgh-btn{flex:0 0 auto;font-size:13px;font-weight:800;padding:9px 12px;border-radius:9px;border:none;cursor:pointer;',
    'background:linear-gradient(135deg,#f59e0b,#ef4444);color:#fff;}',
    '.mgh-btn.ghost{background:#253352;color:#cfdbf2;}',
    '.mgh-btn.ghost:hover{background:#2e3f66;}',
    '.mgh-hint{font-size:11.5px;color:#8fa3c8;margin:-2px 0 10px;}',
    '.mgh-list{list-style:none;margin:0;padding:0;}',
    '.mgh-list li{display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:8px;font-size:13px;}',
    '.mgh-list li:nth-child(odd){background:rgba(255,255,255,.04);}',
    '.mgh-list li.me{background:rgba(245,158,11,.2);}',
    '.mgh-rank{flex:0 0 26px;font-weight:900;color:#f59e0b;text-align:center;}',
    '.mgh-name{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}',
    '.mgh-score{flex:0 0 auto;font-weight:900;color:#fff;}',
    '.mgh-date{flex:0 0 auto;font-size:10.5px;color:#7f90b4;}',
    '.mgh-empty{font-size:12.5px;color:#8fa3c8;text-align:center;padding:14px 0;}',
    '.mgh-foot{display:flex;gap:6px;margin-top:10px;}',
    '.mgh-foot .mgh-btn{flex:1;font-size:12px;padding:8px 6px;}',
    '.mgh-toast{position:fixed;left:50%;transform:translateX(-50%);bottom:22px;background:#16a34a;color:#fff;',
    'font-size:13px;font-weight:800;padding:9px 16px;border-radius:999px;z-index:2147483001;box-shadow:0 8px 22px rgba(0,0,0,.45);}'
  ].join('');

  function addStyle() {
    var s = document.createElement('style');
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  /* ---------- UI ---------- */
  var root, panel, btn, listEl, nameEl, scoreEl, noteEl, hintEl;

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }

  function build() {
    addStyle();
    root = el('div');
    root.id = 'mgh-board-root';

    btn = el('button');
    btn.id = 'mgh-board-btn';
    btn.type = 'button';
    btn.title = '排行榜';
    btn.textContent = '🏆';
    btn.setAttribute('aria-label', '排行榜');

    panel = el('div');
    panel.id = 'mgh-board-panel';
    panel.hidden = true;

    var h = el('div', 'mgh-h');
    h.appendChild(el('b', null, '🏆 ' + GAME_TITLE));
    var x = el('button', 'mgh-x', '✕');
    x.type = 'button';
    x.onclick = function () { panel.hidden = true; };
    h.appendChild(x);
    panel.appendChild(h);

    panel.appendChild(el('p', 'mgh-sub', '記低你嘅成績，同呢部電腦嘅同學鬥高分'));

    var r1 = el('div', 'mgh-row');
    nameEl = el('input', 'mgh-inp');
    nameEl.type = 'text';
    nameEl.placeholder = '你嘅名';
    nameEl.maxLength = 24;
    try { nameEl.value = localStorage.getItem(KEY_NAME) || ''; } catch (e) { }
    scoreEl = el('input', 'mgh-inp');
    scoreEl.type = 'number';
    scoreEl.placeholder = '分數';
    scoreEl.style.flex = '0 0 84px';
    r1.appendChild(nameEl);
    r1.appendChild(scoreEl);
    panel.appendChild(r1);

    hintEl = el('p', 'mgh-hint', '');
    panel.appendChild(hintEl);

    var r2 = el('div', 'mgh-row');
    noteEl = el('input', 'mgh-inp');
    noteEl.type = 'text';
    noteEl.placeholder = '備註（可唔填）';
    noteEl.maxLength = 24;
    var sub = el('button', 'mgh-btn', '提交');
    sub.type = 'button';
    sub.onclick = submit;
    r2.appendChild(noteEl);
    r2.appendChild(sub);
    panel.appendChild(r2);

    listEl = el('ul', 'mgh-list');
    panel.appendChild(listEl);

    var foot = el('div', 'mgh-foot');
    /* 學生版唔俾匯出／清空 —— 呢啲係老師功能，喺 /board/（有密碼閘）做 */
    var bHelp = el('button', 'mgh-btn ghost', '交咗上課室就自動記錄');
    bHelp.type = 'button';
    bHelp.disabled = true;
    bHelp.style.opacity = '.7';
    bHelp.style.cursor = 'default';
    foot.appendChild(bHelp);
    panel.appendChild(foot);

    root.appendChild(panel);
    root.appendChild(btn);

    btn.onclick = function () {
      panel.hidden = !panel.hidden;
      if (!panel.hidden) { autoFill(); render(); }
    };

    document.body.appendChild(root);
  }

  function autoFill() {
    if (scoreEl.value) return;
    var v = detectScore();
    if (v != null) {
      scoreEl.value = v;
      hintEl.textContent = '🔍 自動偵測到 ' + v + ' 分，啱就撳提交；唔啱自己改。';
    } else {
      hintEl.textContent = '搵唔到分數，自己打返入去啦。';
    }
  }

  function submit() {
    var nm = clean(nameEl.value);
    var sc = parseInt(scoreEl.value, 10);
    if (!nm) { toast('首先要填個名喎！'); nameEl.focus(); return; }
    if (isNaN(sc) || sc < 0) { toast('分數要係數字喎！'); scoreEl.focus(); return; }
    try { localStorage.setItem(KEY_NAME, nm); } catch (e) { }
    var list = rows();
    /* 答題明細（analytics.js 採集，冇就唔帶） */
    var detail = null, aCorrect = null, aWrong = null, aTime = null;
    try {
      if (window.MGHAnalytics && window.MGHAnalytics.snapshot) {
        var snap = window.MGHAnalytics.snapshot();
        detail = snap.detail || [];
        aCorrect = snap.correct; aWrong = snap.wrong; aTime = snap.timeMs;
      }
    } catch (e) { /* 採集失敗唔應該阻礙提交 */ }
    var rec = {
      n: nm, s: sc, d: clean(noteEl.value), t: Date.now(), g: GAME_ID,
      c: aCorrect, w: aWrong, ms: aTime, det: detail
    };
    list.push(rec);
    list.sort(function (a, b) { return b.s - a.s || a.t - b.t; });
    saveRows(list);
    noteEl.value = '';
    scoreEl.value = '';
    render();
    /* 雲端上載（老師設定咗 Google 試算表先會有效，否則靜默） */
    var cloudMsg = '';
    try {
      if (window.MGHCloud && window.MGHCloud.enabled && window.MGHAnalytics) {
        var okc = window.MGHCloud.submit(window.MGHAnalytics.snapshot());
        cloudMsg = okc ? '，已同步到老師嘅雲端記錄' : '';
      }
    } catch (e) { /* 雲端唔好就唔好，唔影響 */ }
    toast('✅ 記低咗！' + nm + ' ' + sc + ' 分' + cloudMsg);
  }

  function render() {
    var list = rows().slice(0, MAX_ROWS);
    listEl.innerHTML = '';
    if (!list.length) {
      var e = el('li', 'mgh-empty', '仲未有人記錄，快啲做第一個！');
      e.style.display = 'block';
      listEl.appendChild(e);
      return;
    }
    var myName = '';
    try { myName = localStorage.getItem(KEY_NAME) || ''; } catch (er) { }
    list.forEach(function (r, i) {
      var li = el('li');
      if (r.n === myName) li.className = 'me';
      li.appendChild(el('span', 'mgh-rank',
        i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : String(i + 1)));
      li.appendChild(el('span', 'mgh-name', r.n + (r.d ? '（' + r.d + '）' : '')));
      li.appendChild(el('span', 'mgh-score', String(r.s)));
      var d = new Date(r.t);
      li.appendChild(el('span', 'mgh-date',
        (d.getMonth() + 1) + '/' + d.getDate()));
      listEl.appendChild(li);
    });
  }

  function toast(msg) {
    var t = el('div', 'mgh-toast', msg);
    document.body.appendChild(t);
    setTimeout(function () { if (t.parentNode) t.parentNode.removeChild(t); }, 1800);
  }

  function exportData() {
    var list = rows();
    if (!list.length) { toast('仲未有記錄'); return; }
    var body = list.map(function (r) {
      return clean(r.n) + '~' + r.s + '~' + (r.d || '') + '~' + r.t;
    }).join(';');
    var txt = 'MGHB1|' + GAME_ID + '|' + body;
    var ok = false;
    try {
      var ta = document.createElement('textarea');
      ta.value = txt;
      ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      ok = document.execCommand('copy');
      document.body.removeChild(ta);
    } catch (e) { ok = false; }
    if (!ok && navigator.clipboard) {
      navigator.clipboard.writeText(txt).then(function () { toast('📋 已複製'); },
        function () { prompt('抄低呢段字畀老師：', txt); });
      return;
    }
    toast(ok ? '📋 已複製，畀老師貼去排行榜' : '抄低呢段字：' + txt.slice(0, 30) + '…');
  }

  function clearBoard() {
    if (!window.confirm('確定清空《' + GAME_TITLE + '》喺呢部電腦嘅全部記錄？冇得還原㗎！')) return;
    var all = loadAll();
    delete all[GAME_ID];
    saveAll(all);
    render();
    toast('已清空');
  }

  /* ---------- 對外 API（畀 /board/ 老師頁用） ---------- */
  window.MGHBoard = {
    KEY: KEY,
    loadAll: loadAll,
    exportFormat: 'MGHB1|<slug>|<name>~<score>~<note>~<ts>;…',
    parse: function (txt) {
      var out = [];
      String(txt || '').split(/\r?\n/).forEach(function (line) {
        line = line.trim();
        if (line.indexOf('MGHB1|') !== 0) return;
        var parts = line.split('|');
        if (parts.length < 3) return;
        var gid = parts[1];
        parts.slice(2).join('|').split(';').forEach(function (rec) {
          var f = rec.split('~');
          if (f.length < 2) return;
          var s = parseInt(f[1], 10);
          if (isNaN(s)) return;
          out.push({ g: gid, n: f[0] || '?', s: s, d: f[2] || '', t: parseInt(f[3], 10) || Date.now() });
        });
      });
      return out;
    }
  };

  function boot() {
    if (window.MGH_NO_PANEL) return;   // 排行榜頁本身唔需要浮動掣
    try { build(); } catch (e) {
      // 外掛出任何事都唔可以拖累遊戲本體
      if (window.console && console.warn) console.warn('[board] 初始化失敗：', e);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
