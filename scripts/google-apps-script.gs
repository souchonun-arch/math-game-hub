/**
 * ============================================================
 *  數學遊戲總站 — 雲端成績收集（Google Apps Script）
 * ============================================================
 *  老師設定步驟（一次性，約 5 分鐘）：
 *  1. 開 https://script.google.com → 「新增專案」
 *  2. 貼上呢段程式碼 → 儲存
 *  3. 撳「部署」→「新增部署」→「網頁應用程式」
 *     · 執行身分：自己（我）
 *     · 誰可以存取：任何人  ← 最重要，學生要先入到去
 *  4. 部署完會有一條 https://script.google.com/macros/s/xxxx/exec 網址
 *  5. 貼返去 total://  網站嘅 data/cloud.json 嘅 "endpoint" 度（我幫你填）
 *
 *  學生提交成績時會自動 POST 一行資料落試算表。
 * ============================================================
 */

var SHEET_NAME = '遊戲成績';

function doGet(e) {
  return jsonOut({
    ok: true,
    rows: readRows(),
    count: readRows().length
  });
}

function doPost(e) {
  try {
    var raw = e && e.postData ? e.postData.contents : '{}';
    var d = JSON.parse(raw);

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(SHEET_NAME);
    if (!sh) {
      sh = ss.insertSheet(SHEET_NAME);
      sh.appendRow([
        '時間', '姓名', '遊戲', '分數', '答對', '答錯', '總題數',
        '準確率%', '用時(秒)', '錯題明細', '全部作答', '提交時間戳'
      ]);
      sh.setFrozenRows(1);
      var heads = sh.getRange(1, 1, 1, 12);
      heads.setFontWeight('bold');
      heads.setBackground('#e8f0fe');
    }

    sh.appendRow([
      d.time || new Date().toISOString(),
      d.name || '',
      d.game || d.slug || '',
      Number(d.score) || 0,
      d.correct != null ? Number(d.correct) : '',
      d.wrong != null ? Number(d.wrong) : '',
      d.total != null ? Number(d.total) : '',
      d.accuracy != null ? Number(d.accuracy) : '',
      d.seconds != null ? Number(d.seconds) : '',
      d.wrongDetail || '',
      d.allDetail || '',
      d.ts || Date.now()
    ]);

    return jsonOut({ ok: true, count: readRows().length });
  } catch (err) {
    return jsonOut({ ok: false, error: String(err && err.message || err) });
  }
}

/* 讀全部記錄（俾老師頁拉去睇） */
function readRows() {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sh) return [];
  var vals = sh.getDataRange().getValues();
  if (vals.length < 2) return [];
  var head = vals[0];
  var out = [];
  for (var i = 1; i < vals.length; i++) {
    if (!vals[i][0]) continue;
    var o = {};
    for (var j = 0; j < head.length; j++) o[String(head[j])] = vals[i][j];
    out.push(o);
  }
  return out;
}

function jsonOut(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/* 老師用：設定好試算表欄位（部署前可手動跑一次） */
function setupSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  sh.clear();
  sh.appendRow([
    '時間', '姓名', '遊戲', '分數', '答對', '答錯', '總題數',
    '準確率%', '用時(秒)', '錯題明細', '全部作答', '提交時間戳'
  ]);
  sh.setFrozenRows(1);
  sh.getRange(1, 1, 1, 12).setFontWeight('bold');
  return '搞掂：欄位已建立';
}
