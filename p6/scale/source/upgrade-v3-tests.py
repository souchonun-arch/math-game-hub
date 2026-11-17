#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3 測試套件升級：煙測／HTTP 模擬／實機截圖／README 同步到
   診斷 8 題加權分層、每層 8 題練習、20 分鐘。"""
import pathlib

ROOT = pathlib.Path("/Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風")


def patch(name, pairs):
    p = ROOT / name
    s = p.read_text("utf-8")
    orig = s
    for old, new, label in pairs:
        if old not in s:
            raise SystemExit("❌ [%s] anchor 搵唔到：%s" % (name, label))
        s = s.replace(old, new, 1)
    if s == orig:
        raise SystemExit("❌ [%s] 沒有改動" % name)
    p.write_text(s, "utf-8")
    print("✅ %s 已更新（%d → %d chars）" % (name, len(orig), len(s)))


# ══════════════════════════════════════════════════════════════════════
# smoke.js
# ══════════════════════════════════════════════════════════════════════
SMOKE = [
    # helper：指定答對哪些診斷題（驗證加權分層與基礎題門檻）
    ('''function finishDiag(w, right) {
  w.E('UI.open("diag")');
  const items = w.document.querySelectorAll("#mBody .sc-item");
  items.forEach(function (it, i) {
    const inp = it.querySelector(".sc-in");
    inp.value = i < right ? w.E("DIAG[" + i + "].a[0]") : "___wrong___";
    it.querySelector('[data-a="ck"]').click();
  });
  w.document.querySelector('#mBody [data-a="fin"]').click();
}
''',
     '''function finishDiag(w, right) {
  return finishDiagIdx(w, Array.from({ length: right }, (_, i) => i));
}

function finishDiagIdx(w, arr) {
  w.E('UI.open("diag")');
  const items = w.document.querySelectorAll("#mBody .sc-item");
  items.forEach(function (it, i) {
    const inp = it.querySelector(".sc-in");
    inp.value = arr.indexOf(i) >= 0 ? w.E("DIAG[" + i + "].a[0]") : "___wrong___";
    it.querySelector('[data-a="ck"]').click();
  });
  w.document.querySelector('#mBody [data-a="fin"]').click();
}
''', "finishDiagIdx helper"),

    ('console.log("===== 認識比例尺｜像素風 煙測（第13課／本層 3 題／一次作答／報告圖片）=====\\n");',
     'console.log("===== 認識比例尺｜像素風 煙測 v3（診斷 8 題加權分層／本層 8 題／一次作答／報告圖片）=====\\n");',
     "煙測標題"),

    ('ok(w.E("DATA.steps.length") === 6, "分步題庫 6 題（供三層挑題）");',
     'ok(w.E("DATA.steps.length") === 12, "分步題庫 12 題（三層各 4 題）");', "分步題庫數"),

    ('ok(w.E("DATA.clinic.length") === 5 && w.E("DATA.exit.length") === 3, "錯例 5 題／出門票 3 題（每層各 1）");',
     'ok(w.E("DATA.clinic.length") === 6 && w.E("DATA.exit.length") === 6, "錯例 6 題／出門票 6 題（每層各 2）");',
     "錯例／出門票題庫數"),

    ('ok(w.E("DATA.derive.length") === 3 && w.E("DIAG.length") === 3, "推演 3 步／診斷 3 題");',
     'ok(w.E("DATA.derive.length") === 3 && w.E("DIAG.length") === 8, "推演 3 步／診斷 8 題");',
     "診斷題數"),

    ('ok(w.E("CFG.minutes") === 12, "時間預算 12 分鐘（題量已削減）");',
     'ok(w.E("CFG.minutes") === 20, "時間預算 20 分鐘（診斷 8 ＋ 練習 8）");', "時間預算"),

    ('    ok(/sc-src/.test(html), "逐題教材依據樣式已注入");',
     '''    ok(/sc-src/.test(html), "逐題教材依據樣式已注入");
    ok(w.E("DIAG.reduce((s,q)=>s+q.d,0)") === 15, "診斷加權滿分 15 分");
    ok(w.E("[1,2,3].map(d=>DIAG.filter(q=>q.d===d).length).join(',')") === "3,3,2",
      "診斷梯度 ★3／★★3／★★★2");
    ok(w.E("[1,2,3].every(L=>{const P=PLAN[L];return P.steps.length===4&&P.clinic.length===2&&P.exit.length===2;})"),
      "三層 PLAN 各派 4＋2＋2＝8 題");
    ok(w.E("[1,2,3].every(L=>PLAN[L].steps.every(i=>DATA.steps[i].d===L))"),
      "PLAN 分步索引全部對應本層難度");''', "新增 v3 初始化斷言"),

    # 【2】分層案例
    ('    finishDiag(w, 3);\n    ok(w.E("ST.diag.done") === true && w.E("ST.diag.level") === 3, "3 題全對 → ★★★ 拓展層");',
     '''    finishDiag(w, 8);
    ok(w.E("ST.diag.done") === true && w.E("ST.diag.level") === 3, "8 題全對（15 分）→ ★★★ 拓展層");
    ok(w.E("ST.diag.score") === 15 && w.E("ST.diag.max") === 15, "診斷得分與滿分正確寫入狀態");''',
     "分層案例：全對"),

    ('''    const w2 = await boot(); finishDiag(w2, 2);
    ok(w2.E("ST.diag.level") === 2, "答對 2 題 → ★★ 發展層");
    const w1 = await boot(); finishDiag(w1, 1);
    ok(w1.E("ST.diag.level") === 1, "答對 1 題 → ★ 基礎層");
  }
''',
     '''    const w2 = await boot(); finishDiag(w2, 6);
    ok(w2.E("ST.diag.level") === 2 && w2.E("ST.diag.score") === 9, "前 6 題答對（9 分）→ ★★ 發展層");
    const w1 = await boot(); finishDiag(w1, 3);
    ok(w1.E("ST.diag.level") === 1 && w1.E("ST.diag.score") === 3, "只答對 3 題基礎（3 分）→ ★ 基礎層");
  }

  console.log("\\n【2b】加權分層精準度：不再全部擠在滿分");
  {
    const wa = await boot(); finishDiagIdx(wa, [0,1,2,3,4,5,6]);   /* 12 分 */
    const wb = await boot(); finishDiag(wb, 8);                     /* 15 分 */
    ok(wa.E("ST.diag.level") === 3 && wb.E("ST.diag.level") === 3,
      "12 分與 15 分同屬 ★★★ 拓展層");
    ok(wa.E("ST.diag.score") === 12 && wb.E("ST.diag.score") === 15 &&
       wa.E("ST.diag.score") !== wb.E("ST.diag.score"),
      "同層級內得分仍可區分（12 / 15），不再全部 100 分");
    ok(wa.E("ST.diag.max") === 15 && wb.E("ST.diag.max") === 15, "診斷滿分固定為 15 分");

    const wc = await boot(); finishDiagIdx(wc, [3,4,5,6,7]);       /* 12 分但基礎題全錯 */
    ok(wc.E("ST.diag.level") === 1,
      "基礎題全錯即使高階題全對（12 分），仍落在 ★ 基礎層");
    ok(wc.E("ST.diag.baseOk") === 0, "基礎題答對數正確記錄為 0");

    const wd = await boot(); finishDiagIdx(wd, [0,1,3,4]);         /* 6 分 */
    ok(wd.E("ST.diag.score") === 6 && wd.E("ST.diag.level") === 2,
      "6 分且基礎題過門檻 → ★★ 發展層");
    const we = await boot(); finishDiagIdx(we, [0,1,2]);           /* 3 分 */
    ok(we.E("ST.diag.score") === 3 && we.E("ST.diag.level") === 1,
      "3 分 → ★ 基礎層");
    ok(/8 題分層診斷/.test(we.document.getElementById("page-intro").textContent) ||
       /8 題分層診斷/.test(html), "引入頁與教材標示 8 題診斷");
  }
''', "分層案例＋2b 精準度測試"),

    # 【3】每層配題
    ('console.log("\\n【3】分層針對性：每層只派 3 題，且是同一條主題鏈");',
     'console.log("\\n【3】分層針對性：每層只派 8 題，且是同一條主題鏈");', "【3】標題"),

    ('ok(w.document.querySelectorAll("#mBody .sc-item").length === 1, tag + " 分步只見 1 題（不再攤開 6 張卡）");',
     'ok(w.document.querySelectorAll("#mBody .sc-item").length === 4, tag + " 分步只見 4 題（不再攤開 12 張卡）");',
     "分步配題數"),

    ('''    ok(w.document.querySelectorAll("#mBody .sc-chain .chain-row").length === 6,
      tag + " 一覽含 1 列本層訓練重點＋其餘 5 題（僅供參考）");''',
     '''    ok(w.document.querySelectorAll("#mBody .sc-chain .chain-row").length === 9,
      tag + " 一覽含 1 列本層訓練重點＋其餘 8 題（僅供參考）");''',
     "解題鏈一覽列數"),

    ('ok(w.document.querySelectorAll("#mBody .sc-sec").length === 1, tag + " 本層題標示預估秒數");',
     'ok(w.document.querySelectorAll("#mBody .sc-sec").length === 4, tag + " 本層 4 題皆標示預估秒數");',
     "秒數標示數"),

    ('ok(w.document.querySelectorAll("#mBody .sc-item").length === 1, tag + " 出門票只派 1 題");',
     'ok(w.document.querySelectorAll("#mBody .sc-item").length === 2, tag + " 出門票只派 2 題");',
     "出門票配題數"),

    ('ok(w.document.querySelectorAll("#mBody .sc-item").length === 1, tag + " 錯例醫院只派 1 題");',
     'ok(w.document.querySelectorAll("#mBody .sc-item").length === 2, tag + " 錯例醫院只派 2 題");',
     "錯例配題數"),

    ('''    ok(w.E("[DATA.steps[planOf().steps].d,DATA.clinic[planOf().clinic].d,DATA.exit[planOf().exit].d].every(d=>d==="
      + lv + ")"), tag + " 三題難度全部等於本層（不跳級、不降級）");''',
     '''    ok(w.E("planOf().steps.every(i=>DATA.steps[i].d===" + lv + ")") &&
       w.E("planOf().clinic.every(i=>DATA.clinic[i].d===" + lv + ")") &&
       w.E("planOf().exit.every(i=>DATA.exit[i].d===" + lv + ")"),
      tag + " 八題難度全部等於本層（不跳級、不降級）");
    ok(w.E("activeIds('steps').length===4 && activeIds('clinic').length===2 && activeIds('exit').length===2"),
      tag + " activeIds 回傳 4／2／2，合計 8 題");''',
     "難度檢查改陣列"),

    ('ok(/今日只派/.test(w.document.getElementById("page-practice").textContent), tag + " 配對表標明今日只派 3 題");',
     'ok(/今日只派 8 題/.test(w.document.getElementById("page-practice").textContent), tag + " 配對表標明今日只派 8 題");',
     "配對表題數"),

    # 【4】分步配圖
    ('ok(w.document.querySelectorAll("#mBody .sc-item .figbox svg").length === 1, "本層分步題配圖");',
     'ok(w.document.querySelectorAll("#mBody .sc-item .figbox svg").length === 4, "本層 4 題分步皆配圖");',
     "分步配圖數"),

    # 【7】報告時間
    ('ok(/時間預算 12 分鐘/.test(t), "報告列出 12 分鐘時間預算");',
     'ok(/時間預算 20 分鐘/.test(t), "報告列出 20 分鐘時間預算");', "報告時間預算"),

    # 【7b】教材依據對照表
    ('ok(w.document.querySelectorAll("#mBody table tr").length === 15, "逐題對照表：標題列＋6 分步＋5 錯例＋3 出門票");',
     'ok(w.document.querySelectorAll("#mBody table tr").length === 25, "逐題對照表：標題列＋12 分步＋6 錯例＋6 出門票");',
     "逐題對照表列數"),

    # 【9】出門票 2 題都要作答才彈總結
    ('''    const w = await boot(2);
    w.E('UI.open("exit")');
    const it = w.document.querySelector("#mBody .sc-item");
    const idx = w.E("activeIds('exit')[0]");
    it.querySelector(".sc-in").value = w.E("DATA.exit[" + idx + "].a[0]");
    it.querySelector('[data-act="check"]').click();
    ok(w.E("ST.exit[" + idx + "].done") === true, "出門票答對");''',
     '''    const w = await boot(2);
    w.E('UI.open("exit")');
    const items = w.document.querySelectorAll("#mBody .sc-item");
    items.forEach(function (it, n) {
      const idx = w.E("activeIds('exit')[" + n + "]");
      it.querySelector(".sc-in").value = w.E("DATA.exit[" + idx + "].a[0]");
      it.querySelector('[data-act="check"]').click();
    });
    const idx = w.E("activeIds('exit')[0]");
    ok(w.E("ST.exit[" + idx + "].done") === true, "出門票 2 題皆答對");''',
     "出門票答對（2 題）"),

    ('''    const w = await boot(1);
    w.E('UI.open("exit")');
    const it = w.document.querySelector("#mBody .sc-item");
    it.querySelector(".sc-in").value = "___wrong___";
    it.querySelector('[data-act="check"]').click();
    ok(w.E("ST.wrongBook.length") === 1, "出門票答錯也記入錯題本");''',
     '''    const w = await boot(1);
    w.E('UI.open("exit")');
    const items = w.document.querySelectorAll("#mBody .sc-item");
    items.forEach(function (it, n) {
      const idx = w.E("activeIds('exit')[" + n + "]");
      it.querySelector(".sc-in").value = n === 0 ? "___wrong___" : w.E("DATA.exit[" + idx + "].a[0]");
      it.querySelector('[data-act="check"]').click();
    });
    ok(w.E("ST.wrongBook.length") === 1, "出門票答錯也記入錯題本");''',
     "出門票答錯（2 題）"),

    # 【10】題庫索引
    ('ok(w.E("DATA.steps[2].a[0]") === "480" && w.E("DATA.exit[1].a[0]") === "2000", "題庫答案與課本附加例題一致");',
     'ok(w.E("DATA.steps[4].a[0]") === "480" && w.E("DATA.exit[2].a[0]") === "2000", "題庫答案與課本附加例題一致");',
     "題庫索引 A"),

    ('ok(w.E("DATA.steps[3].a[0]") === "33000" && w.E("DATA.steps[5].a[0]") === "50", "題庫答案與工作紙／練習13一致");',
     'ok(w.E("DATA.steps[5].a[0]") === "33000" && w.E("DATA.steps[9].a[0]") === "50", "題庫答案與工作紙／練習13一致");',
     "題庫索引 B"),

    ('''    ok(w.E("DATA.steps.every(s=>[1,2,3].indexOf(s.d)>=0)"), "每題都有 d:1/2/3 難度標記");''',
     '''    ok(w.E("DATA.steps.every(s=>[1,2,3].indexOf(s.d)>=0)"), "每題都有 d:1/2/3 難度標記");
    ok(w.E("[1,2,3].every(L=>DATA.steps.filter(s=>s.d===L).length===4 && DATA.clinic.filter(c=>c.d===L).length===2 && DATA.exit.filter(e=>e.d===L).length===2)"),
      "每層恰有 4 分步＋2 錯例＋2 出門票（共 8 題）");
    ok(w.E("DIAG.reduce((s,q)=>s+q.d,0)===15 && DIAG.filter(q=>q.d===3).length===2"),
      "診斷加權總分 15 分，含 2 題 3 分題");''',
     "新增題庫分佈斷言"),
]
patch("smoke.js", SMOKE)


# ══════════════════════════════════════════════════════════════════════
# pages-check.js
# ══════════════════════════════════════════════════════════════════════
PAGES = [
    ('''  const lv = await page.evaluate(() => BZ.ST.diag.level);
  ok(lv === 3, "診斷完成並分層（本次 ★★★）");''',
     '''  const lv = await page.evaluate(() => BZ.ST.diag.level);
  ok(lv === 3, "8 題診斷完成並分層（本次 ★★★）");
  const dg = await page.evaluate(() => ({ score: BZ.ST.diag.score, max: BZ.ST.diag.max,
                                           right: BZ.ST.diag.right, n: BZ.DIAG.length }));
  ok(dg.n === 8 && dg.score === 15 && dg.max === 15 && dg.right === 8,
    "加權分層：8 題全對得 15 / 15 分（不再只有「全對／非全對」）");''',
     "HTTP 診斷得分檢查"),

    ('''    /今日只派 3 題/.test(document.body.textContent)), "練習頁顯示本層配對表（4 格、今日只派 3 題）");''',
     '''    /今日只派 8 題/.test(document.body.textContent)), "練習頁顯示本層配對表（4 格、今日只派 8 題）");''',
     "HTTP 配對表題數"),

    ('''    document.querySelectorAll("#mBody table tr").length === 15), "老師可開啟逐題教材依據對照表");''',
     '''    document.querySelectorAll("#mBody table tr").length === 25), "老師可開啟逐題教材依據對照表（25 列）");''',
     "HTTP 對照表列數"),
]
patch("github-pages/source/pages-check.js", PAGES)
patch("pages-check.js", PAGES)


# ══════════════════════════════════════════════════════════════════════
# shot.js
# ══════════════════════════════════════════════════════════════════════
SHOT = [
    ('  /* 分步列式：本層只 1 題＋教材依據 */',
     '  /* 分步列式：本層 4 題＋教材依據 */', "註解"),
    ('''    level: BZ.level,
    xp: BZ.ST.xp,''',
     '''    level: BZ.level,
    diagScore: BZ.ST.diag.score + " / " + BZ.ST.diag.max,
    planCounts: [BZ.activeIds("steps").length, BZ.activeIds("clinic").length, BZ.activeIds("exit").length],
    xp: BZ.ST.xp,''', "實機狀態輸出"),
]
patch("shot.js", SHOT)
patch("github-pages/source/shot.js", SHOT)


# ══════════════════════════════════════════════════════════════════════
# README.md
# ══════════════════════════════════════════════════════════════════════
README = [
    ("建議時間：約 12 分鐘", "建議時間：約 20 分鐘（拓展層因題目較深，實際約 20–22 分鐘）", "建議時間"),
    ("2. 先完成 **3 題分層診斷**（比的化簡、單位換算、前項化為 1）。未完成診斷前，練習不會開啟。",
     "2. 先完成 **8 題分層診斷**（比的化簡、單位換算、前項化為 1）。題目依難度配分：★ 題 1 分、★★ 題 2 分、★★★ 題 3 分，**滿分 15 分**；系統以加權得分加上基礎題門檻判定層級，同一層級內仍可從得分看出程度差異，避免多數學生集中在滿分而無法分層。未完成診斷前，練習不會開啟。",
     "診斷流程"),
    ("3. 系統依診斷結果配對 **★ 基礎層／★★ 發展層／★★★ 拓展層**，每層只派 **3 題**：分步列式 1 題、錯例醫院 1 題、出門票 1 題，三題屬同一概念主題鏈。其餘題目收在「解題鏈一覽」，僅供參考，不必作答。",
     "3. 系統依診斷結果配對 **★ 基礎層／★★ 發展層／★★★ 拓展層**，每層只派 **8 題**：分步列式 4 題、錯例醫院 2 題、出門票 2 題，八題皆為本層難度且屬同一概念主題鏈。其餘 16 題收在「解題鏈一覽」，僅供參考，不必作答。",
     "配題流程"),
    ("| `source/smoke.js` | jsdom 自動化測試（222 項），驗證分層、鎖定、錯題本、教材依據、角色用語與報告圖片 |",
     "| `source/smoke.js` | jsdom 自動化測試，驗證加權分層、每層 8 題配對、鎖定、錯題本、教材依據、角色用語與報告圖片 |",
     "檔案說明"),
    ("> 生成腳本內建品質檢查：學生可見文字不得出現粵語口語字、不得混入後續章節概念、每題必須附教材依據與預估秒數、答案必須為純數字、不得出現「第 N 組」這類無意義前綴，角色與作答用語須一致，以及分層與作答機制的完整結構檢查。",
     "> 生成腳本內建品質檢查：學生可見文字不得出現粵語口語字、不得混入後續章節概念、每題必須附教材依據與預估秒數、答案必須為純數字、不得出現「第 N 組」這類無意義前綴，角色與作答用語須一致，並檢查診斷加權分層（滿分 15 分）與每層 8 題配對，以及分層與作答機制的完整結構檢查。",
     "品質檢查說明"),
    ("| `source/build.py` | 冪等生成腳本，修改題庫後可重新產出 `index.html`（需配合本機「波仔互動教材模板」） |",
     "| `source/build.py` | 冪等生成腳本，修改題庫後可重新產出 `index.html`（需配合本機「波仔互動教材模板」） |\n| `source/upgrade-v3.py` | v3 升級腳本，記錄「診斷 3→8 題、練習 3→8 題、12→20 分鐘」的完整改動 |",
     "檔案說明加升級腳本"),
]
patch("github-pages/README.md", README)

print("\n✅ 測試套件與 README 已同步 v3")
