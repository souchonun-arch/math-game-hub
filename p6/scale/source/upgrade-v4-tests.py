#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《認識比例尺》v4 測試與說明同步腳本
把 smoke.js / pages-check.js / shot.js / README.md 由 v3（診斷 8 題、每層 8 題）
校正為 v4（診斷 5 題滿分 9、不可重做、每層 4 題出門票、分步與錯例為參考示範）。
"""
import pathlib

D = pathlib.Path("/Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風")


def load(name):
    return (D / name).read_text("utf-8")


def save(name, s):
    (D / name).write_text(s, "utf-8")


def rep(s, old, new, label, count=1):
    if old not in s:
        raise SystemExit("❌ 錨點搵唔到 [%s]：%s" % (label, old[:70]))
    return s.replace(old, new, count)


def seg(s, start, end, new, label):
    a = s.find(start)
    if a < 0:
        raise SystemExit("❌ 段起點搵唔到：" + label)
    b = s.find(end, a + len(start))
    if b < 0:
        raise SystemExit("❌ 段終點搵唔到：" + label)
    return s[:a] + new + s[b:]


# ══════════════════════════════════════════════════════════════════════
# 1. smoke.js
# ══════════════════════════════════════════════════════════════════════
m = load("smoke.js")
m = rep(m, '煙測 v3（診斷 8 題加權分層／本層 8 題／一次作答／報告圖片）',
        '煙測 v4（診斷 5 題滿分 9／不可重做／每層 4 題出門票／一次作答／報告圖片）', "煙測標題")

# 【1】初始化
m = rep(m, 'ok(w.E("DATA.clinic.length") === 6 && w.E("DATA.exit.length") === 6, "錯例 6 題／出門票 6 題（每層各 2）");',
        'ok(w.E("DATA.clinic.length") === 6 && w.E("DATA.exit.length") === 12, "錯例 6 題／出門票 12 題（每層各 4）");', "題庫數量")
m = rep(m, 'ok(w.E("DATA.derive.length") === 3 && w.E("DIAG.length") === 8, "推演 3 步／診斷 8 題");',
        'ok(w.E("DATA.derive.length") === 3 && w.E("DIAG.length") === 5, "推演 3 步／診斷 5 題");', "診斷題數")
m = rep(m, 'ok(w.E("CFG.minutes") === 20, "時間預算 20 分鐘（診斷 8 ＋ 練習 8）");',
        'ok(w.E("CFG.minutes") === 15, "時間預算 15 分鐘（診斷 5 ＋ 出門票 4）");', "時間預算")
m = rep(m, 'ok(w.E("DIAG.reduce((s,q)=>s+q.d,0)") === 15, "診斷加權滿分 15 分");',
        'ok(w.E("DIAG.reduce((s,q)=>s+q.d,0)") === 9, "診斷加權滿分 9 分");', "診斷滿分")
m = rep(m, 'ok(w.E("[1,2,3].map(d=>DIAG.filter(q=>q.d===d).length).join(\',\')") === "3,3,2",\n      "診斷梯度 ★3／★★3／★★★2");',
        'ok(w.E("[1,2,3].map(d=>DIAG.filter(q=>q.d===d).length).join(\',\')") === "2,2,1",\n      "診斷梯度 ★2／★★2／★★★1");', "診斷梯度")
m = rep(m, 'ok(w.E("[1,2,3].every(L=>{const P=PLAN[L];return P.steps.length===4&&P.clinic.length===2&&P.exit.length===2;})"),\n      "三層 PLAN 各派 4＋2＋2＝8 題");',
        'ok(w.E("[1,2,3].every(L=>{const P=PLAN[L];return P.steps.length===4&&P.clinic.length===2&&P.exit.length===4;})"),\n      "三層 PLAN：示範 4＋2，出門票各派 4 題");', "PLAN 題數")

# 【2】先分層
m = rep(m, '    finishDiag(w, 8);\n    ok(w.E("ST.diag.done") === true && w.E("ST.diag.level") === 3, "8 題全對（15 分）→ ★★★ 拓展層");\n    ok(w.E("ST.diag.score") === 15 && w.E("ST.diag.max") === 15, "診斷得分與滿分正確寫入狀態");',
        '    finishDiag(w, 5);\n    ok(w.E("ST.diag.done") === true && w.E("ST.diag.level") === 3, "5 題全對（9 分）→ ★★★ 拓展層");\n    ok(w.E("ST.diag.score") === 9 && w.E("ST.diag.max") === 9, "診斷得分與滿分正確寫入狀態");', "全對分層")
m = rep(m, '    const w2 = await boot(); finishDiag(w2, 6);\n    ok(w2.E("ST.diag.level") === 2 && w2.E("ST.diag.score") === 9, "前 6 題答對（9 分）→ ★★ 發展層");\n    const w1 = await boot(); finishDiag(w1, 3);\n    ok(w1.E("ST.diag.level") === 1 && w1.E("ST.diag.score") === 3, "只答對 3 題基礎（3 分）→ ★ 基礎層");',
        '    const w2 = await boot(); finishDiag(w2, 4);\n    ok(w2.E("ST.diag.level") === 2 && w2.E("ST.diag.score") === 6, "前 4 題答對（6 分）→ ★★ 發展層");\n    const w1 = await boot(); finishDiag(w1, 2);\n    ok(w1.E("ST.diag.level") === 1 && w1.E("ST.diag.score") === 2, "只答對 2 題基礎（2 分）→ ★ 基礎層");', "部分答對分層")

# 【2b】加權分層精準度（整段換）
SEC2B = r'''  console.log("\n【2b】加權分層精準度：5 題 9 分仍可拉開層級");
  {
    const wa = await boot(); finishDiagIdx(wa, [0,1,2,4]);       /* 7 分 */
    const wb = await boot(); finishDiag(wb, 5);                  /* 9 分 */
    ok(wa.E("ST.diag.level") === 3 && wb.E("ST.diag.level") === 3,
      "7 分與 9 分同屬 ★★★ 拓展層");
    ok(wa.E("ST.diag.score") === 7 && wb.E("ST.diag.score") === 9 &&
       wa.E("ST.diag.score") !== wb.E("ST.diag.score"),
      "同層級內得分仍可區分（7 / 9），不再全部 100 分");
    ok(wa.E("ST.diag.max") === 9 && wb.E("ST.diag.max") === 9, "診斷滿分固定為 9 分");

    const wc = await boot(); finishDiagIdx(wc, [2,3,4]);         /* 7 分但基礎題全錯 */
    ok(wc.E("ST.diag.level") === 1,
      "基礎題全錯即使高階題全對（7 分），仍落在 ★ 基礎層");
    ok(wc.E("ST.diag.baseOk") === 0, "基礎題答對數正確記錄為 0");

    const wd = await boot(); finishDiagIdx(wd, [0,1,2]);         /* 4 分 */
    ok(wd.E("ST.diag.score") === 4 && wd.E("ST.diag.level") === 2,
      "4 分且基礎題過門檻 → ★★ 發展層");
    const we = await boot(); finishDiagIdx(we, [0]);             /* 1 分 */
    ok(we.E("ST.diag.score") === 1 && we.E("ST.diag.level") === 1,
      "1 分 → ★ 基礎層");
    ok(/5 題分層診斷/.test(we.document.getElementById("page-intro").textContent) ||
       /5 題分層診斷/.test(html), "引入頁與教材標示 5 題診斷");
  }

  console.log("\n【2c】診斷不可重做：答錯不補答、完成後只顯示結果");
  {
    const w = await boot();
    w.E('UI.open("diag")');
    const items = w.document.querySelectorAll("#mBody .sc-item");
    ok(items.length === 5, "診斷顯示 5 題");
    const it0 = items[0];
    it0.querySelector(".sc-in").value = "___wrong___";
    it0.querySelector('[data-a="ck"]').click();
    ok(it0.querySelector(".sc-in").disabled, "診斷答錯後輸入欄即時鎖定");
    ok(/不能補答/.test(it0.querySelector(".sc-fb").textContent), "明確告知不能補答");
    it0.querySelector(".sc-in").disabled = false;
    it0.querySelector(".sc-in").value = w.E("DIAG[0].a[0]");
    it0.querySelector('[data-a="ck"]').click();
    ok(w.E("ST.diag.q0.locked") === true && w.E("ST.diag.q0.ok") === false,
      "即使再填正確答案，該題仍鎖定為答錯，不計分");
    w.document.querySelector('#mBody [data-a="fin"]').click();
    ok(w.E("ST.diag.done") === true, "診斷已完成");
    w.E('UI.open("diag")');
    const t = w.document.getElementById("mBody").textContent;
    ok(/不可重做/.test(t), "再次開啟診斷只顯示「已完成，不可重做」");
    ok(w.document.querySelectorAll("#mBody .sc-in").length === 0, "不可重做：不再提供任何作答欄");
    w.E('UI.open("teacher")');
    ok(!/重做分層診斷/.test(w.document.getElementById("mBody").textContent),
      "老師專用已移除「重做分層診斷」入口");
  }

'''
m = seg(m, r'  console.log("\n【2b】加權分層精準度', r'  console.log("\n【3】分層針對性', SEC2B, "【2b】＋【2c】")

# 【3】分層針對性（整段換）
SEC3 = r'''  console.log("\n【3】分層針對性：每層只派 4 題出門票；分步／錯例為參考示範");
  for (const lv of [1, 2, 3]) {
    const w = await boot(lv);
    const tag = "★".repeat(lv) + "☆".repeat(3 - lv);
    const p = w.E("planOf()");
    w.E('UI.open("steps")');
    const st = w.document.getElementById("mBody").textContent;
    ok(/參考示範/.test(st) && /不必作答/.test(st), tag + " 分步列式為參考示範、不必作答");
    ok(w.document.querySelectorAll("#mBody .sc-item").length === 0 &&
       w.document.querySelectorAll("#mBody .sc-in").length === 0, tag + " 分步示範頁沒有任何作答題");
    ok(w.document.querySelectorAll("#mBody .sc-src").length === 4, tag + " 示範列出本層 4 題教材依據");
    ok(w.document.querySelectorAll("#mBody .sc-sec").length === 4, tag + " 示範 4 題皆標示預估秒數");
    ok(!!w.document.querySelector('#mBody [data-a="toexit"]'), tag + " 提供「前往出門票」按鈕");
    ok(/本層主題/.test(st), tag + " 顯示本層主題：" + p.topic);
    w.E('UI.open("clinic")');
    ok(/參考示範/.test(w.document.getElementById("mBody").textContent) &&
       w.document.querySelectorAll("#mBody .sc-item").length === 0, tag + " 錯例醫院為參考示範、不必作答");
    w.E('UI.open("exit")');
    ok(w.document.querySelectorAll("#mBody .sc-item").length === 4, tag + " 出門票只派 4 題");
    ok(w.document.querySelectorAll("#mBody .sc-item .sc-src").length === 4, tag + " 出門票 4 題皆附教材依據");
    ok(w.E("activeIds('steps').length===0 && activeIds('clinic').length===0 && activeIds('exit').length===4"),
      tag + " activeIds 回傳 0／0／4，合計 4 題");
    ok(w.E("planOf().steps.every(i=>DATA.steps[i].d===" + lv + ")") &&
       w.E("planOf().clinic.every(i=>DATA.clinic[i].d===" + lv + ")") &&
       w.E("planOf().exit.every(i=>DATA.exit[i].d===" + lv + ")"),
      tag + " 示範與出門票難度全部等於本層");
    ok(w.E("activeIds('exit').every(i=>DATA.exit[i].d===" + lv + ")"), tag + " 4 題出門票皆為本層難度");
    w.E('go("practice")');
    ok(w.document.querySelectorAll("#page-practice .match-box").length === 4, tag + " 配對表 4 格");
    ok(!!w.document.querySelector("#page-practice .report-entry"), tag + " 練習頁有學生報告入口");
    ok(/今日只派 4 題出門票/.test(w.document.getElementById("page-practice").textContent),
      tag + " 配對表標明今日只派 4 題出門票");
  }

'''
m = seg(m, r'  console.log("\n【3】分層針對性', r'  console.log("\n【4】比例尺專用', SEC3, "【3】")

# 【4】分步配圖測試 → 示範頁
m = rep(m, '    w.BZ.UI.open("steps");\n    ok(w.document.querySelectorAll("#mBody .sc-item .figbox svg").length === 4, "本層 4 題分步皆配圖");',
        '    w.BZ.UI.open("steps");\n    ok(/參考示範/.test(w.document.getElementById("mBody").textContent) &&\n       w.document.querySelectorAll("#mBody .sc-src").length === 4,\n      "分步示範頁列出本層 4 題題目、答案與教材依據");', "【4】分步示範")

# 【5】一次作答改由出門票驗證
m = rep(m, '    const w = await boot(2);\n    w.E(\'UI.open("steps")\');\n    const item = w.document.querySelector("#mBody .sc-item");\n    const idx = w.E("activeIds(\'steps\')[0]");',
        '    const w = await boot(2);\n    w.E(\'UI.open("exit")\');\n    const item = w.document.querySelector("#mBody .sc-item");\n    const idx = w.E("activeIds(\'exit\')[0]");', "【5】開出門票")
m = rep(m, '    ok(w.E("ST.steps[" + idx + "].locked") === true, "作答後 rec.locked = true");',
        '    ok(w.E("ST.exit[" + idx + "].locked") === true, "作答後 rec.locked = true");', "【5】locked")
m = rep(m, '    item.querySelector(".sc-in").value = w.E("DATA.steps[" + idx + "].a[0]");',
        '    item.querySelector(".sc-in").value = w.E("DATA.exit[" + idx + "].a[0]");', "【5】正確答案")
m = rep(m, '    w.E(\'UI.open("steps")\');\n    const again = w.document.querySelector("#mBody .sc-item");',
        '    w.E(\'UI.open("exit")\');\n    const again = w.document.querySelector("#mBody .sc-item");', "【5】重開")

# 【6】錯題重練由出門票產生
m = rep(m, '    w.E(\'UI.open("steps")\');\n    const item = w.document.querySelector("#mBody .sc-item");\n    item.querySelector(".sc-in").value = "999";\n    item.querySelector(\'[data-act="check"]\').click();\n    w.E(\'UI.open("wrong")\');',
        '    w.E(\'UI.open("exit")\');\n    const item = w.document.querySelector("#mBody .sc-item");\n    item.querySelector(".sc-in").value = "999";\n    item.querySelector(\'[data-act="check"]\').click();\n    w.E(\'UI.open("wrong")\');', "【6】開出門票")
m = rep(m, "return DATA.steps[i].redo.a[0];", "return DATA.exit[i].redo.a[0];", "【6】變式題答案")

# 【6b】重練答錯
m = rep(m, '    w.E(\'UI.open("steps")\');\n    const it0 = w.document.querySelector("#mBody .sc-item");',
        '    w.E(\'UI.open("exit")\');\n    const it0 = w.document.querySelector("#mBody .sc-item");', "【6b】開出門票")

# 【6c】錯例醫院改為示範頁檢查（整段換）
SEC6C = r'''  console.log("\n【6c】錯例醫院改為參考示範，不產生作答題");
  {
    const w = await boot(2);
    w.E('UI.open("clinic")');
    const t = w.document.getElementById("mBody").textContent;
    ok(/參考示範/.test(t) && /不必作答/.test(t), "錯例醫院標明參考示範、不必作答");
    ok(w.document.querySelectorAll("#mBody .sc-item").length === 0 &&
       w.document.querySelectorAll("#mBody .opt-btn").length === 0,
      "錯例示範頁沒有作答題與選項按鈕");
    ok(/正確答案/.test(t) && /教材依據/.test(t), "示範頁直接列出正確答案、解釋與教材依據");
    ok(!!w.document.querySelector('#mBody [data-a="toexit"]'), "提供「前往出門票」按鈕");
  }

'''
m = seg(m, r'  console.log("\n【6c】錯例醫院', r'  console.log("\n【7】學生個人報告', SEC6C, "【6c】")

# 【7】學生報告
m = rep(m, '    w.E(\'UI.open("steps")\');\n    const it = w.document.querySelector("#mBody .sc-item");\n    it.querySelector(".sc-in").value = "777";',
        '    w.E(\'UI.open("exit")\');\n    const it = w.document.querySelector("#mBody .sc-item");\n    it.querySelector(".sc-in").value = "777";', "【7】開出門票")
m = rep(m, '    ok(/時間預算 20 分鐘/.test(t), "報告列出 20 分鐘時間預算");',
        '    ok(/時間預算 15 分鐘/.test(t), "報告列出 15 分鐘時間預算");', "【7】時間")
m = rep(m, '    ok(recTables.length > 0 && recTables[recTables.length - 1].querySelectorAll("tr").length === 9,\n      "本層逐題記錄含 8 題（分步 4＋錯例 2＋出門票 2）＋標題列");',
        '    ok(recTables.length > 0 && recTables[recTables.length - 1].querySelectorAll("tr").length === 5,\n      "本層逐題記錄含 4 題出門票＋標題列（分步與錯例不計）");', "【7】逐題記錄")
m = rep(m, '    ok(/0 \\/ 8/.test(texts), "報告卡統計分母為 8 題，與今日配題一致（不是 6）");',
        '    ok(/0 \\/ 4/.test(texts), "報告卡統計分母為 4 題，與今日配題一致");', "【7】分母")
m = rep(m, '    ok(/診斷 \\d+ \\/ 15 分/.test(texts), "報告卡印出診斷加權得分（滿分 15）");',
        '    ok(/診斷 \\d+ \\/ 9 分/.test(texts), "報告卡印出診斷加權得分（滿分 9）");', "【7】診斷得分")
m = rep(m, '    ok(/陳大明/.test(texts), "圖片內容印有學生姓名");',
        '    ok(/今日須作答 9 題/.test(texts), "報告卡標示今日共 9 題（診斷 5＋出門票 4）");\n    ok(/陳大明/.test(texts), "圖片內容印有學生姓名");', "【7】新增總題數")

# 【7b】老師專用
m = rep(m, '    ok(w.document.querySelectorAll("#mBody .t-btn").length === 9, "老師專用 9 個入口（新增教材依據一覽）");',
        '    ok(w.document.querySelectorAll("#mBody .t-btn").length === 8, "老師專用 8 個入口（移除重做診斷）");', "【7b】入口數")
m = rep(m, '    ok(w.document.querySelectorAll("#mBody table tr").length === 25, "逐題對照表：標題列＋12 分步＋6 錯例＋6 出門票");',
        '    ok(w.document.querySelectorAll("#mBody table tr").length === 31, "逐題對照表：標題列＋12 分步＋6 錯例＋12 出門票");', "【7b】對照表")

# 【8】總結卡
m = rep(m, '    w.E(\'UI.open("steps")\');\n    const nav = Array.from(w.document.querySelectorAll("#mBtns [data-f]")).map(b => b.textContent).join(" ");',
        '    w.E(\'UI.open("exit")\');\n    const nav = Array.from(w.document.querySelectorAll("#mBtns [data-f]")).map(b => b.textContent).join(" ");', "【8】開出門票")
m = rep(m, '    const idx = w.E("activeIds(\'steps\')[0]");\n    item.querySelector(".sc-in").value = w.E("DATA.steps[" + idx + "].a[0]");',
        '    const idx = w.E("activeIds(\'exit\')[0]");\n    item.querySelector(".sc-in").value = w.E("DATA.exit[" + idx + "].a[0]");', "【8】答案")
m = rep(m, '    ok(saved.steps[idx] && saved.steps[idx].done, "完成狀態寫入 localStorage");',
        '    ok(saved.exit[idx] && saved.exit[idx].done, "完成狀態寫入 localStorage");', "【8】存檔")

# 【9】出門票題數
m = rep(m, '    ok(w.E("ST.exit[" + idx + "].done") === true, "出門票 2 題皆答對");',
        '    ok(w.E("ST.exit[" + idx + "].done") === true, "出門票 4 題皆答對");', "【9】題數")

# 【10】數學正確性
m = rep(m, '    ok(w.E("DATA.steps[4].a[0]") === "480" && w.E("DATA.exit[2].a[0]") === "2000", "題庫答案與課本附加例題一致");',
        '    ok(w.E("DATA.steps[4].a[0]") === "480" && w.E("DATA.exit[4].a[0]") === "2000", "題庫答案與課本附加例題一致");', "【10】答案索引")
m = rep(m, '    ok(w.E("[1,2,3].every(L=>DATA.steps.filter(s=>s.d===L).length===4 && DATA.clinic.filter(c=>c.d===L).length===2 && DATA.exit.filter(e=>e.d===L).length===2)"),\n      "每層恰有 4 分步＋2 錯例＋2 出門票（共 8 題）");',
        '    ok(w.E("[1,2,3].every(L=>DATA.steps.filter(s=>s.d===L).length===4 && DATA.clinic.filter(c=>c.d===L).length===2 && DATA.exit.filter(e=>e.d===L).length===4)"),\n      "每層恰有 4 分步示範＋2 錯例示範＋4 出門票");', "【10】分層題數")
m = rep(m, '    ok(w.E("DIAG.reduce((s,q)=>s+q.d,0)===15 && DIAG.filter(q=>q.d===3).length===2"),\n      "診斷加權總分 15 分，含 2 題 3 分題");',
        '    ok(w.E("DIAG.reduce((s,q)=>s+q.d,0)===9 && DIAG.filter(q=>q.d===3).length===1"),\n      "診斷加權總分 9 分，含 1 題 3 分題");', "【10】診斷配分")

# 【11】品質鐵律加 v4 檢查
m = rep(m, '    const w2 = await boot(2);\n    const scriptTags = w2.document.querySelectorAll("script").length;',
        '''    ok(/分層診斷已完成，不可重做/.test(html) && /不能補答/.test(html),
      "診斷不可重做：答錯即鎖、不補答、完成後只顯示結果");
    ok(!/t:"重做分層診斷"/.test(html), "老師專用已移除重做診斷入口");
    ok(/if\\(stage!=="exit"\\) return \\[\\];/.test(html),
      "只有出門票派題，分步與錯例不產生作答題");
    ok(/今日須作答 9 題（診斷 5 ＋ 出門票 4）/.test(html), "教材標示今日共 9 題");
    const w2 = await boot(2);
    const scriptTags = w2.document.querySelectorAll("script").length;''', "【11】v4 檢查")

# 結尾標題
m = rep(m, '  console.log("\\n===== " + pass + " 通過 / " + fail + " 失敗 =====");',
        '  console.log("\\n===== " + pass + " 通過 / " + fail + " 失敗 =====（v4：診斷 5 題／9 分／不可重做；每層 4 題出門票）");', "結尾")
save("smoke.js", m)
print("✅ smoke.js 已升級為 v4")

# ══════════════════════════════════════════════════════════════════════
# 2. pages-check.js
# ══════════════════════════════════════════════════════════════════════
p = load("pages-check.js")
p = rep(p, '  ok(lv === 3, "8 題診斷完成並分層（本次 ★★★）");',
        '  ok(lv === 3, "5 題診斷完成並分層（本次 ★★★）");', "pages 分層")
p = rep(p, '  ok(dg.n === 8 && dg.score === 15 && dg.max === 15 && dg.right === 8,\n    "加權分層：8 題全對得 15 / 15 分（不再只有「全對／非全對」）");',
        '  ok(dg.n === 5 && dg.score === 9 && dg.max === 9 && dg.right === 5,\n    "加權分層：5 題全對得 9 / 9 分（不再只有「全對／非全對」）");', "pages 得分")
p = rep(p, '    /今日只派 8 題/.test(document.body.textContent)), "練習頁顯示本層配對表（4 格、今日只派 8 題）");',
        '    /今日只派 4 題出門票/.test(document.body.textContent)), "練習頁顯示本層配對表（4 格、今日只派 4 題出門票）");', "pages 配對表")
p = rep(p, '''  await page.evaluate(() => BZ.UI.open("steps"));
  await wait(250);
  ok(await page.evaluate(() => !!document.querySelector("#mBody .sc-item .sc-src") &&
    /教材依據/.test(document.getElementById("mBody").textContent)), "HTTP 環境下逐題教材依據正常顯示");
  ok(await page.evaluate(() => document.querySelectorAll("#mBody .sc-item .figsvg").length === 4),
    "HTTP 環境下本層 4 題分步像素圖解皆正常顯示");''',
        '''  await page.evaluate(() => BZ.UI.open("steps"));
  await wait(250);
  ok(await page.evaluate(() => !!document.querySelector("#mBody .sc-src") &&
    /參考示範/.test(document.getElementById("mBody").textContent)),
    "HTTP 環境下分步示範頁顯示教材依據與參考示範");
  await page.evaluate(() => BZ.UI.open("exit"));
  await wait(250);
  ok(await page.evaluate(() => document.querySelectorAll("#mBody .sc-item").length === 4 &&
    !!document.querySelector("#mBody .sc-item .sc-src")),
    "HTTP 環境下本層 4 題出門票與逐題教材依據皆正常顯示");''', "pages 示範與出門票")
p = rep(p, '    document.querySelectorAll("#mBody table tr").length === 25), "老師可開啟逐題教材依據對照表（25 列）");',
        '    document.querySelectorAll("#mBody table tr").length === 31), "老師可開啟逐題教材依據對照表（31 列）");', "pages 對照表")
save("pages-check.js", p)
print("✅ pages-check.js 已升級為 v4")

# ══════════════════════════════════════════════════════════════════════
# 3. shot.js
# ══════════════════════════════════════════════════════════════════════
sh = load("shot.js")
sh = rep(sh, '  /* 分步列式：本層 4 題＋教材依據 */',
         '  /* 分步列式：本層 4 題參考示範＋教材依據 */', "shot 註解")
sh = rep(sh, '    const el = document.querySelector("#mBody .sc-item .sc-src");',
         '    const el = document.querySelector("#mBody .sc-src");', "shot 依據列")
sh = rep(sh, '''  /* 答錯 → 一次鎖定＋提示自動出現 */
  await page.evaluate(() => {
    BZ.UI.close();
    BZ.UI.open("steps");
    const it = document.querySelector("#mBody .sc-item");''',
         '''  /* 答錯 → 一次鎖定＋提示自動出現（改用出門票驗證） */
  await page.evaluate(() => {
    BZ.UI.close();
    BZ.UI.open("exit");
    const it = document.querySelector("#mBody .sc-item");''', "shot 答錯")
sh = rep(sh, '''    stepLocked: (() => {
      const i = BZ.activeIds("steps")[0];
      return !!(BZ.ST.steps[i] && BZ.ST.steps[i].locked);
    })(),''',
         '''    exitLocked: (() => {
      const i = BZ.activeIds("exit")[0];
      return !!(BZ.ST.exit[i] && BZ.ST.exit[i].locked);
    })(),''', "shot 鎖定狀態")
save("shot.js", sh)
print("✅ shot.js 已升級為 v4")

# ══════════════════════════════════════════════════════════════════════
# 4. github-pages/README.md
# ══════════════════════════════════════════════════════════════════════
r = (D / "github-pages" / "README.md").read_text("utf-8")
pairs = [
    ("建議時間：約 20 分鐘（拓展層因題目較深，實際約 20–22 分鐘）",
     "建議時間：約 15 分鐘（拓展層因題目較深，實際約 15–17 分鐘）"),
    ("先完成 **8 題分層診斷**（比的化簡、單位換算、前項化為 1）。題目依難度配分：★ 題 1 分、★★ 題 2 分、★★★ 題 3 分，**滿分 15 分**；系統以加權得分加上基礎題門檻判定層級，同一層級內仍可從得分看出程度差異，避免多數學生集中在滿分而無法分層。未完成診斷前，練習不會開啟。",
     "先完成 **5 題分層診斷**（比的化簡、單位換算、前項化為 1）。題目依難度配分：★ 題 1 分、★★ 題 2 分、★★★ 題 3 分，**滿分 9 分**；系統以加權得分加上基礎題門檻判定層級，同一層級內仍可從得分看出程度差異。**每題只作答一次，答錯不補答，診斷完成後不可重做**。未完成診斷前，練習不會開啟。"),
    ("系統依診斷結果配對 **★ 基礎層／★★ 發展層／★★★ 拓展層**，每層只派 **8 題**：分步列式 4 題、錯例醫院 2 題、出門票 2 題，八題皆為本層難度且屬同一概念主題鏈。其餘 16 題收在「解題鏈一覽」，僅供參考，不必作答。",
     "系統依診斷結果配對 **★ 基礎層／★★ 發展層／★★★ 拓展層**，每層只派 **4 題出門票**，四題皆為本層難度且屬同一概念主題鏈。分步列式與錯例醫院改為「參考示範」，列出本層題目、答案、解釋與教材依據，**不必作答**。"),
    ("每題**只作答一次**，送出後即鎖定，不能修改。",
     "出門票每題**只作答一次**，送出後即鎖定，不能修改。")
]
for a, b in pairs:
    r = rep(r, a, b, "README " + a[:18])
r = r.replace("時間預算約 20 分鐘；拓展層較深，實際約 20 至 22 分鐘。",
              "時間預算約 15 分鐘；拓展層較深，實際約 15 至 17 分鐘。")
r = r.replace("（243 項）", "（v4 煙測）").replace("（23 項）", "（v4 HTTP 模擬）")
r = r.replace("診斷加權分層（滿分 15 分）與每層 8 題配對",
              "診斷加權分層（滿分 9 分）、不可重做與每層 4 題出門票配對")
r = r.replace("每層 8 題配對", "每層 4 題出門票配對")
r = r.replace("分步列式 4 題", "分步列式示範 4 題")
(D / "github-pages" / "README.md").write_text(r, "utf-8")
print("✅ README.md 已升級為 v4")

print("\n✅ upgrade-v4-tests.py 完成")
