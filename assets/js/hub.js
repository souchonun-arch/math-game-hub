/* ===========================================================
   數學遊戲總站 — 前端邏輯
   讀 data/games.json 渲染卡片、課題分類、搜尋、QR Code
   首頁 page=home 顯示三個入口；分區頁 page=section 顯示卡片
   =========================================================== */

(function () {
  'use strict';

  var BASE = document.documentElement.getAttribute('data-base') || '.';
  var SECTION = document.documentElement.getAttribute('data-section') || '';
  var PAGE = document.documentElement.getAttribute('data-page') || 'section';

  var rootUrl = new URL(BASE + '/', location.href).href;

  var state = {
    games: [],
    topics: {},
    sections: [],
    secMap: {},
    q: '',
    topic: 'all'
  };

  /* 課題 → emoji（冇封面圖，用 emoji 代替，零請求） */
  var TOPIC_EMOJI = {
    '99乘法表': '✖️',
    '直式乘法': '📐',
    '四則運算次序': '🧑‍🍳',
    '毫米與分米': '📏',
    '單位換算': '🔄',
    '澳門幣': '💰',
    '折扣與賺賠': '🛒',
    '百分數': '💯',
    '單利息': '🐉',
    '小數分數百分數互化': '🔢',
    '24點遊戲': '🃏',
    '小數分數速算': '⚡'
  };

  var GRADIENTS = [
    'linear-gradient(135deg,#60a5fa,#2563eb)',
    'linear-gradient(135deg,#34d399,#059669)',
    'linear-gradient(135deg,#fbbf24,#f59e0b)',
    'linear-gradient(135deg,#f472b6,#db2777)',
    'linear-gradient(135deg,#a78bfa,#7c3aed)',
    'linear-gradient(135deg,#22d3ee,#0891b2)',
    'linear-gradient(135deg,#fb7185,#e11d48)',
    'linear-gradient(135deg,#4ade80,#16a34a)'
  ];

  function $(sel) { return document.querySelector(sel); }

  function loadJSON(rel) {
    return fetch(new URL(rel, rootUrl).href, { cache: 'no-store' })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      });
  }

  function absUrl(entry) {
    return new URL(entry, rootUrl).href;
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function wifiBadge(g) {
    if (g.wifi === 'heavy') {
      return '<span class="badge heavy">⚠️ ' + g.sizeText + ' · 要用 Wi-Fi</span>';
    }
    if (g.wifi === 'medium') {
      return '<span class="badge medium">⚠️ ' + g.sizeText + ' · 建議 Wi-Fi</span>';
    }
    return '<span class="badge light">' + g.sizeText + '</span>';
  }

  /* ---------------- QR Code ---------------- */
  function makeQrSvg(text, cellSize) {
    if (typeof qrcode !== 'function') {
      console.error('qrcode 函式庫未載入');
      return '';
    }
    var qr = qrcode(0, 'Q');
    qr.addData(text);
    qr.make();
    var svg = qr.createSvgTag({ cellSize: cellSize || 6, margin: 2, scalable: true });
    // scalable 模式出嚟嘅 SVG 冇 width/height，補返上去避免部分瀏覽器高度塌縮
    if (svg.indexOf('width=') === -1) {
      var m = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
      if (m) svg = svg.replace('<svg ', '<svg width="' + m[1] + '" height="' + m[2] + '" ');
    }
    return svg;
  }

  function openQrModal(game) {
    var mask = $('#qr-mask');
    var box = $('#qr-body');
    var url = absUrl(game.entry);
    if (!mask || !box) return;
    box.innerHTML =
      '<h3>' + esc(game.title) + '</h3>' +
      '<p class="modal-sub">' + esc(game.topic) + ' · 用相機掃一掃就開到</p>' +
      '<div class="qr-box">' + makeQrSvg(url, 7) + '</div>' +
      '<div class="qr-url">' + esc(url) + '</div>' +
      '<button class="modal-close" id="qr-close">閂咗佢</button>';
    mask.hidden = false;
    $('#qr-close').onclick = function () { mask.hidden = true; };
  }

  function openPageQr() {
    var sec = state.secMap[SECTION];
    var mask = $('#qr-mask');
    var box = $('#qr-body');
    if (!mask || !box) return;
    var url = absUrl(SECTION + '/');
    box.innerHTML =
      '<h3>' + esc(sec ? sec.title : '') + '</h3>' +
      '<p class="modal-sub">掃一掃就入到呢區全部遊戲</p>' +
      '<div class="qr-box">' + makeQrSvg(url, 7) + '</div>' +
      '<div class="qr-url">' + esc(url) + '</div>' +
      '<button class="modal-close" id="qr-close">閂咗佢</button>';
    mask.hidden = false;
    $('#qr-close').onclick = function () { mask.hidden = true; };
  }

  /* ---------------- 列印海報 ---------------- */
  function printPoster() {
    var area = $('#print-area');
    if (!area) { window.print(); return; }
    var list = filtered();
    var html = '<h2>' + esc((state.secMap[SECTION] || {}).title || '') + ' — 遊戲 QR 海報</h2>' +
      '<p class="print-sub">用手機相機掃一掃，直接開遊戲</p><div class="print-grid">';
    list.forEach(function (g) {
      html += '<div class="print-item">' +
        '<div class="pi-title">' + esc(g.title) + '</div>' +
        makeQrSvg(absUrl(g.entry), 5) +
        '<div class="pi-sub">' + esc(g.topic) + ' · ' + esc(g.sizeText) + '</div>' +
        '</div>';
    });
    html += '</div>';
    area.innerHTML = html;
    setTimeout(function () { window.print(); }, 250);
  }

  /* ---------------- 篩選 ---------------- */
  function filtered() {
    var q = state.q.trim().toLowerCase();
    return state.games.filter(function (g) {
      if (state.topic !== 'all' && g.topic !== state.topic) return false;
      if (!q) return true;
      var hay = [g.title, g.topic, g.id, (g.keywords || []).join(' ')].join(' ').toLowerCase();
      return hay.indexOf(q) !== -1;
    });
  }

  /* ---------------- 渲染：分區頁 ---------------- */
  function renderChips() {
    var wrap = $('#chips');
    if (!wrap) return;
    var list = state.topics[SECTION] || [];
    var html = '<button class="chip' + (state.topic === 'all' ? ' active' : '') +
      '" data-topic="all">全部</button>';
    list.forEach(function (t) {
      var count = state.games.filter(function (g) { return g.topic === t; }).length;
      if (!count) return;
      html += '<button class="chip' + (state.topic === t ? ' active' : '') +
        '" data-topic="' + esc(t) + '">' + esc(t) + ' (' + count + ')</button>';
    });
    wrap.innerHTML = html;
    Array.prototype.forEach.call(wrap.querySelectorAll('.chip'), function (btn) {
      btn.onclick = function () {
        state.topic = btn.getAttribute('data-topic');
        renderChips();
        renderCards();
      };
    });
  }

  function cardHtml(g, idx) {
    var emoji = TOPIC_EMOJI[g.topic] || '🎮';
    var grad = GRADIENTS[idx % GRADIENTS.length];
    var net = g.needsNetwork ? '<span class="badge net">需外網</span>' : '';
    return '' +
      '<article class="card" data-id="' + esc(g.id) + '">' +
        '<div class="card-visual" style="--card-grad:' + grad + '">' + emoji + '</div>' +
        '<div class="card-body">' +
          '<h3 class="card-title">' + esc(g.title) + '</h3>' +
          '<span class="card-topic">' + esc(g.topic) + '</span>' +
          '<div class="card-meta">' + wifiBadge(g) + net + '</div>' +
          '<div class="card-actions">' +
            '<a class="btn btn-play" href="' + esc(absUrl(g.entry)) + '" target="_blank" rel="noopener">開始遊戲 ▶</a>' +
            '<button class="btn btn-qr" data-qr="' + esc(g.id) + '" title="顯示 QR Code">QR</button>' +
          '</div>' +
        '</div>' +
      '</article>';
  }

  function renderCards() {
    var grid = $('#grid');
    var info = $('#result-info');
    if (!grid) return;
    var list = filtered();
    if (!list.length) {
      grid.innerHTML = '<div class="empty">搵唔到相關遊戲 🤷<br>試下第二個關鍵字？</div>';
      if (info) info.textContent = '';
      return;
    }
    grid.innerHTML = list.map(cardHtml).join('');
    if (info) {
      info.textContent = '顯示 ' + list.length + ' / ' + state.games.length + ' 款遊戲';
    }
    Array.prototype.forEach.call(grid.querySelectorAll('[data-qr]'), function (btn) {
      btn.onclick = function () {
        var id = btn.getAttribute('data-qr');
        var g = state.games.filter(function (x) { return x.id === id; })[0];
        if (g) openQrModal(g);
      };
    });
  }

  /* ---------------- 渲染：首頁 ---------------- */
  function renderHome() {
    var grid = $('#section-grid');
    if (!grid) return;
    grid.innerHTML = state.sections.map(function (sec) {
      var items = state.games.filter(function (g) { return g.section === sec.id; });
      var total = items.reduce(function (a, g) { return a + g.totalBytes; }, 0);
      var mb = (total / (1024 * 1024)).toFixed(1);
      return '' +
        '<a class="section-card" href="' + esc(absUrl(sec.id + '/')) + '">' +
          '<div class="section-top" style="background:' + sec.gradient + '">' + sec.icon + '</div>' +
          '<div class="section-info">' +
            '<h2>' + esc(sec.title) + '</h2>' +
            '<p>' + esc(sec.desc) + '</p>' +
            '<div class="section-foot">' +
              '<span class="section-count">' + items.length + ' 款 · ' + mb + ' MB</span>' +
              '<span class="section-go" style="background:' + sec.color + '">入去玩 ▶</span>' +
            '</div>' +
          '</div>' +
        '</a>';
    }).join('');
  }

  /* ---------------- 啟動 ---------------- */
  function bootHome() {
    $('#hero-count').textContent = '共 ' + state.games.length + ' 款遊戲';
    renderHome();
    var up = $('#updated-at');
    if (up) up.textContent = state.meta.updated || '';
  }

  function bootSection() {
    var sec = state.secMap[SECTION];
    if (!sec) { console.error('搵唔到分區：' + SECTION); return; }
    document.documentElement.style.setProperty('--hero-grad', sec.gradient);
    document.documentElement.style.setProperty('--accent', sec.color);
    document.documentElement.style.setProperty('--accent-soft', sec.colorSoft);
    $('#hero-title').textContent = sec.title;
    $('#hero-desc').textContent = sec.desc;
    $('#hero-icon').textContent = sec.icon;
    $('#hero-count').textContent = state.games.length + ' 款遊戲';

    var qrBtn = $('#btn-page-qr');
    if (qrBtn) qrBtn.onclick = openPageQr;
    var printBtn = $('#btn-print');
    if (printBtn) printBtn.onclick = printPoster;

    var search = $('#search');
    if (search) {
      search.oninput = function () {
        state.q = search.value;
        renderCards();
      };
    }

    var mask = $('#qr-mask');
    if (mask) {
      mask.onclick = function (e) {
        if (e.target === mask) mask.hidden = true;
      };
    }

    renderChips();
    renderCards();
    var up = $('#updated-at');
    if (up) up.textContent = state.meta.updated || '';
  }

  Promise.all([
    loadJSON('data/games.json'),
    loadJSON('data/sections.json'),
    loadJSON('data/topics.json')
  ]).then(function (res) {
    var games = res[0] || {};
    state.meta = { updated: games.updated || '' };
    state.games = (games.games || []).filter(function (g) {
      return PAGE === 'home' ? true : g.section === SECTION;
    });
    state.sections = res[1] || [];
    state.sections.forEach(function (s) { state.secMap[s.id] = s; });
    state.topics = res[2] || {};

    document.title = PAGE === 'home'
      ? '數學遊戲總站'
      : ((state.secMap[SECTION] || {}).title || '遊戲') + ' — 數學遊戲總站';

    if (PAGE === 'home') bootHome(); else bootSection();
  }).catch(function (e) {
    var grid = $('#grid');
    console.error(e);
    if (grid) {
      grid.innerHTML = '<div class="empty">載入失敗 😢<br>' + esc(e.message) +
        '<br><br>如果你係直接開檔案（file://），要用本機伺服器先睇到：<br>' +
        '<code>python3 -m http.server 8000</code></div>';
    }
  });
})();
