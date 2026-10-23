/* ============================================================
   cloud-rank.js — 雲端排行榜模組（相容舊版 RANK API）
   ------------------------------------------------------------
   原遊戲《冰河紀元》引用 ../cloud-rank.js，提供：
     RANK.submit({game, score, correct, total, seconds, nick})
     RANK.renderTop(el, {game, limit})
     RANK.getNick()

   實作：對接 Google Apps Script Web App（同一個端點，同總站共用）
     · 提交 → POST 一行落試算表
     · 讀榜 → GET 全部，再喺前端篩同遊戲 + 排序
     · 未設定雲端 → 完全靜默（遊戲照玩）
   ============================================================ */
(function () {
  'use strict';
  if (window.RANK) return;   // 已經有就唔好覆蓋

  var CFG_URL = '../data/cloud.json';
  var NICK_KEY = 'mgh_board_name';
  var LOCAL_KEY = 'mgh_rank_v1';

  var endpoint = '';
  var cache = {};      // game -> rows

  function loadCfg() {
    return fetch(CFG_URL, { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) { endpoint = (d && d.endpoint) || ''; return endpoint; })
      .catch(function () { endpoint = ''; return ''; });
  }

  function getNick() {
    try { return localStorage.getItem(NICK_KEY) || ''; } catch (e) { return ''; }
  }

  /* ---------- 本機榜（雲端未設定時的後備，確保遊戲內 panel 有嘢睇） ---------- */
  function localRows(game) {
    try {
      var o = JSON.parse(localStorage.getItem(LOCAL_KEY) || '{}');
      return (o && o.games && o.games[game]) ? o.games[game] : [];
    } catch (e) { return []; }
  }
  function saveLocal(game, rec) {
    try {
      var o = JSON.parse(localStorage.getItem(LOCAL_KEY) || '{}');
      if (!o.games) o.games = {};
      if (!o.games[game]) o.games[game] = [];
      o.games[game].push(rec);
      if (o.games[game].length > 200) o.games[game] = o.games[game].slice(-200);
      localStorage.setItem(LOCAL_KEY, JSON.stringify(o));
    } catch (e) { /* 容量爆咗就靜默 */ }
  }

  /* ---------- 提交 ---------- */
  function submit(rec) {
    rec = rec || {};
    var game = rec.game || 'unknown';
    var nick = rec.nick || getNick() || '同學';
    var row = {
      ts: Date.now(),
      time: new Date().toISOString(),
      name: nick,
      game: game,
      slug: '',
      score: Number(rec.score) || 0,
      correct: rec.correct != null ? Number(rec.correct) : '',
      wrong: rec.total != null && rec.correct != null ? Number(rec.total) - Number(rec.correct) : '',
      total: rec.total != null ? Number(rec.total) : '',
      accuracy: (rec.total > 0 && rec.correct != null)
        ? Math.round(Number(rec.correct) / Number(rec.total) * 100) : '',
      seconds: rec.seconds != null ? Number(rec.seconds) : '',
      wrongDetail: '',
      allDetail: ''
    };
    /* 先存本機（保證唔會丟） */
    saveLocal(game, { n: nick, s: row.score, c: row.correct, t: row.ts });
    /* 再上載雲端 */
    if (!endpoint) {
      loadCfg().then(function (ep) {
        if (ep) postToCloud(row);
      });
    } else {
      postToCloud(row);
    }
    return true;
  }

  function postToCloud(row) {
    try {
      fetch(endpoint, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(row),
        redirect: 'follow'
      }).then(function (r) {
        if (!r.ok) console.warn('[RANK] 上載失敗 HTTP', r.status);
        else cache = {};    // 清快取，下次讀榜要重新攞
      }).catch(function (e) {
        console.warn('[RANK] 上載失敗：', e && e.message);
      });
    } catch (e) { /* 唔好阻礙遊戲 */ }
  }

  /* ---------- 讀榜 ---------- */
  function fetchAll() {
    if (!endpoint) {
      loadCfg().then(function (ep) {
        if (ep) fetchAll();
      });
      return Promise.resolve([]);
    }
    return fetch(endpoint, { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) { return (d && d.rows) ? d.rows : []; })
      .catch(function () { return []; });
  }

  function renderTop(el, opts) {
    opts = opts || {};
    if (!el) return;
    var game = opts.game || '';
    var limit = opts.limit || 10;
    var rows = [];
    var box = el;

    function paint(list) {
      if (!list.length) {
        box.innerHTML = '<div style="font-size:12px;color:#6B7280;padding:6px 0">' +
          '暫時未有記錄</div>';
        return;
      }
      var h = '<table style="width:100%;border-collapse:collapse;font-size:12px">';
      h += '<tr style="color:#6B7280;font-size:11px;text-align:left">' +
        '<th style="padding:3px 4px">#</th><th style="padding:3px 4px">姓名</th>' +
        '<th style="padding:3px 4px;text-align:right">分數</th>' +
        '<th style="padding:3px 4px;text-align:right">答對</th>' +
        '<th style="padding:3px 4px;text-align:right">用時</th></tr>';
      list.slice(0, limit).forEach(function (r, i) {
        var name = String(r['姓名'] || r.name || '同學');
        var sc = r['分數'] != null ? r['分數'] : (r.score != null ? r.score : 0);
        var c = r['答對'] != null && r['答對'] !== '' ? r['答對'] : (r.correct != null ? r.correct : '—');
        var sec = r['用時(秒)'] != null && r['用時(秒)'] !== '' ? r['用時(秒)'] + 's'
          : (r.seconds != null ? r.seconds + 's' : '—');
        var medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i + 1);
        h += '<tr style="border-top:1px solid rgba(0,0,0,.07)">' +
          '<td style="padding:4px">' + medal + '</td>' +
          '<td style="padding:4px">' + esc(name) + '</td>' +
          '<td style="padding:4px;text-align:right;font-weight:700">' + esc(sc) + '</td>' +
          '<td style="padding:4px;text-align:right">' + esc(c) + '</td>' +
          '<td style="padding:4px;text-align:right;color:#6B7280">' + esc(sec) + '</td></tr>';
      });
      box.innerHTML = h + '</table>';
    }

    /* 先顯示本機（快），再換成雲端 */
    paint(localRows(game).slice().sort(function (a, b) { return b.s - a.s; }));

    if (cache[game]) { paint(cache[game]); return; }
    fetchAll().then(function (all) {
      var list = all.filter(function (r) {
        return String(r['遊戲'] || r.game || '') === game;
      });
      list.sort(function (a, b) {
        var sa = Number(a['分數'] != null ? a['分數'] : a.score) || 0;
        var sb = Number(b['分數'] != null ? b['分數'] : b.score) || 0;
        return sb - sa;
      });
      cache[game] = list;
      paint(list);
    });
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  window.RANK = {
    submit: submit,
    renderTop: renderTop,
    getNick: getNick,
    /* 額外：畀其他用途 */
    fetchAll: fetchAll,
    localRows: localRows
  };

  /* 預先載入設定 */
  loadCfg();
})();
