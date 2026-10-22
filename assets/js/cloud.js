/* ============================================================
   MGH Cloud — 學生端自動上載成績到雲端
   ------------------------------------------------------------
   設計：Google Apps Script Web App（老師設定一次，免費）
   · 學生撳「提交」→ 自動 POST 一次 → Google 試算表新增一行
   · 冇設定雲端 URL → 完全靜默，只存本機（唔會出事）
   · 就算 POST 失敗都唔影響遊戲（fire and forget）

   欄位（每行一筆）：
   時間 | 姓名 | 遊戲 | 分數 | 答對 | 答錯 | 用時(秒) | 錯題明細
   ============================================================ */
(function () {
  'use strict';
  if (window.MGH_NO_CLOUD) return;

  var G = window.MGH_GAME || {};
  var ENDPOINT = G.cloudEndpoint || '';   // 由 build.py 注入

  function post(payload) {
    if (!ENDPOINT) return false;
    try {
      // no-cors 唔行（讀唔到回應），用 cors 模式
      fetch(ENDPOINT, {
        method: 'POST',
        mode: 'cors',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(payload),
        redirect: 'follow'
      }).then(function (r) {
        if (!r.ok) console.warn('[MGH Cloud] 上載失敗 HTTP', r.status);
      }).catch(function (e) {
        // 網絡唔通都好正常（例如學校 Wi-Fi 限制）—— 唔阻礙遊戲
        console.warn('[MGH Cloud] 上載失敗：', e && e.message);
      });
      return true;
    } catch (e) {
      return false;
    }
  }

  function buildPayload(snap) {
    var wrongs = (snap.detail || []).filter(function (d) { return !d.ok; });
    return {
      ts: snap.ts,
      time: new Date(snap.ts).toISOString(),
      name: snap.player || '',
      game: snap.title || snap.game,
      slug: snap.game,
      score: snap.score,
      correct: snap.correct,
      wrong: snap.wrong,
      seconds: Math.round((snap.timeMs || 0) / 1000),
      total: (snap.correct || 0) + (snap.wrong || 0),
      accuracy: (snap.correct + snap.wrong) > 0
        ? Math.round(snap.correct / (snap.correct + snap.wrong) * 100)
        : 0,
      /* 錯題明細：每條一格，用 | 分隔 */
      wrongDetail: wrongs.map(function (d) {
        return '題:' + d.q + ' ｜ 答:' + d.user + ' ｜ 正解:' + d.ans;
      }).join(' ▸ '),
      allDetail: (snap.detail || []).map(function (d) {
        return (d.ok ? '✓' : '✗') + d.q + '（' + d.user + '）';
      }).join(' ▸ ')
    };
  }

  window.MGHCloud = {
    enabled: !!ENDPOINT,
    endpoint: ENDPOINT,
    /* 供 board.js 提交時呼叫 */
    submit: function (snap) {
      if (!snap) return false;
      try { return post(buildPayload(snap)); }
      catch (e) { return false; }
    }
  };
})();