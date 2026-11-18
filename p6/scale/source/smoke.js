/* 《認識比例尺｜像素風（小六重點班・第13課）》煙測
   跑法：
   NODE_PATH=/Users/chonunsou/.workbuddy/binaries/node/workspace/node_modules \
     /Users/chonunsou/.local/bin/node smoke.js
*/
const fs = require("fs");
const path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const DIR = "/Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風";
const html = fs.readFileSync(path.join(DIR, "認識比例尺-像素風.html"), "utf8");
const LKEY = "bz_scale_level_v1";
const SKEY = "bz_scale_pixel_v1";

let pass = 0, fail = 0;
function ok(c, m) { if (c) { pass++; console.log("  ✓ " + m); } else { fail++; console.log("  ✗ " + m); } }
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function boot(lv) {
  const vc = new VirtualConsole();
  vc.on("jsdomError", () => { });           /* 靜默 audio 未實作 */
  const dom = new JSDOM(html, {
    runScripts: "dangerously", pretendToBeVisual: true, url: "http://localhost/",
    virtualConsole: vc,
    beforeParse: function (w) {
      w.scrollTo = function () { };
      w.print = function () { };
      w.AudioContext = undefined; w.webkitAudioContext = undefined;
      w.__cardTexts = [];
      w.__cardYs = [];
      const texts = w.__cardTexts;
      const ys = w.__cardYs;
      const fake = {
        fillRect() { }, strokeRect() { }, scale() { },
        fillText(t, x, y) { texts.push(String(t)); ys.push(y); },
        fillStyle: "", strokeStyle: "", lineWidth: 1,
        font: "", textAlign: "", textBaseline: ""
      };
      if (w.HTMLCanvasElement) {
        w.HTMLCanvasElement.prototype.getContext = function () {
          if (this.id && this.id.indexOf("pix") === 0) return null;
          return Object.assign({}, fake);
        };
        w.HTMLCanvasElement.prototype.toDataURL = function () {
          return "data:image/png;base64,FAKECARD";
        };
      }
    }
  });
  const w = dom.window;
  if (lv) w.localStorage.setItem(LKEY, JSON.stringify({ level: lv, score: lv, ts: Date.now() }));
  if (w.document.readyState !== "complete") await new Promise(function (r) { w.addEventListener("load", r); });
  await sleep(30);
  w.E = function (expr) { return w.eval(expr); };
  return w;
}

function finishDiag(w, right) {
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

(async function () {
  console.log("===== 認識比例尺｜像素風 煙測 v4（診斷 5 題滿分 9／不可重做／每層 4 題出門票／一次作答／報告圖片）=====\n");

  console.log("【1】初始化、教材範圍與像素層降級");
  {
    const w = await boot();
    ok(w.E("typeof UI") === "object", "UI 引擎載入");
    ok(!!w.BZ && !!w.PIX, "window.BZ／window.PIX 公開介面存在");
    ok(w.E("PIX.enabled") === false, "jsdom 無 Canvas → 像素層靜默降級（不崩）");
    ok(!!w.document.getElementById("pixFx") && !!w.document.getElementById("pixBuddyCv"), "像素 canvas／精靈 DOM 存在");
    ok(/^尺尺：/.test(w.document.getElementById("pixBuddySay").textContent),
      "精靈初始氣泡署名為「尺尺」並引導分層診斷");
    ok(html.indexOf("比比") < 0, "成品沒有沿用舊教材角色「比比」");
    ok(!/再試一次|再接再厲/.test(html), "成品沒有「重試原題」鼓勵語");
    w.E('PIX.say("測試")');
    ok(w.document.getElementById("pixBuddySay").textContent === "尺尺：測試",
      "動態氣泡統一署名「尺尺」");
    w.E('PIX.oops()');
    ok(/已記入錯題本，請前往錯題重練。/.test(w.document.getElementById("pixBuddySay").textContent),
      "答錯後精靈導向錯題重練，而非重試原題");
    ok(w.E("CFG.lesson") === "第13課｜認識比例尺", "課題為第13課「認識比例尺」");
    ok(w.E("CFG.key") === "比例尺 ＝ 圖上距離 : 實際距離（先統一單位，再化成前項為 1 的最簡整數比）", "本課算法正確");
    ok(w.E("DATA.steps.length") === 12, "分步題庫 12 題（三層各 4 題）");
    ok(w.E("DATA.clinic.length") === 6 && w.E("DATA.exit.length") === 12, "錯例 6 題／出門票 12 題（每層各 4）");
    ok(w.E("DATA.derive.length") === 3 && w.E("DIAG.length") === 5, "推演 3 步／診斷 5 題");
    ok(w.document.querySelectorAll(".page").length === 5, "五個分頁");
    ok(w.document.querySelectorAll(".qb-btn").length === 7, "快捷列 4 主線＋我的報告＋錯題重練＋老師");
    ok(w.E("CFG.minutes") === 15, "時間預算 15 分鐘（診斷 5 ＋ 出門票 4）");
    ok(w.E("DATA.steps.every(s=>s.sec>0 && s.src && s.redo && s.redo.a)"), "分步逐題秒數＋教材依據＋變式題齊全");
    ok(w.E("DATA.exit.every(s=>s.sec>0 && s.src && s.redo && s.redo.a)"), "出門票逐題秒數＋教材依據＋變式題齊全");
    ok(w.E("DATA.clinic.every(c=>c.sec>0 && c.src && c.redo && c.redo.a)"), "錯例逐題秒數＋教材依據＋變式題齊全");
    ok(w.E("DIAG.every(d=>d.src && d.sec>0) && DATA.derive.every(d=>d.src)"), "診斷與推演亦附教材依據");
    ok(w.E("[1,2,3].every(L=>PLAN[L] && PLAN[L].topic && PLAN[L].focus)"), "三層都有本層主題與訓練重點");
    ok(w.E("typeof BZ.card==='function' && typeof BZ.drawCard==='function'"), "報告圖片 API 已公開");
    ok(/10 : 1/.test(html) && /B-2-15/.test(html), "包含數學小百科 10 : 1 與基本學力 B-2-15");
    ok(/sc-src/.test(html), "逐題教材依據樣式已注入");
    ok(w.E("DIAG.reduce((s,q)=>s+q.d,0)") === 9, "診斷加權滿分 9 分");
    ok(w.E("[1,2,3].map(d=>DIAG.filter(q=>q.d===d).length).join(',')") === "2,2,1",
      "診斷梯度 ★2／★★2／★★★1");
    ok(w.E("[1,2,3].every(L=>{const P=PLAN[L];return P.steps.length===4&&P.clinic.length===2&&P.exit.length===4;})"),
      "三層 PLAN：示範 4＋2，出門票各派 4 題");
    ok(w.E("[1,2,3].every(L=>PLAN[L].steps.every(i=>DATA.steps[i].d===L))"),
      "PLAN 分步索引全部對應本層難度");
  }

  console.log("\n【2】先分層：未完成診斷不准入練習");
  {
    const w = await boot();
    w.E('UI.open("steps")');
    ok(/分層診斷/.test(w.document.getElementById("mTitle").textContent), "未診斷撳主線 → 自動導向診斷");
    w.E('UI.open("redo")');
    ok(/分層診斷/.test(w.document.getElementById("mTitle").textContent), "未診斷撳錯題重練 → 自動導向診斷");
    w.E('go("practice")');
    ok(!w.document.getElementById("page-practice").classList.contains("active"), "未診斷不能直接進練習頁");
    w.E('UI.open("report")');
    ok(/我的學習報告/.test(w.document.getElementById("mTitle").textContent), "學生可隨時查看個人報告（不需老師權限）");
    finishDiag(w, 5);
    ok(w.E("ST.diag.done") === true && w.E("ST.diag.level") === 3, "5 題全對（9 分）→ ★★★ 拓展層");
    ok(w.E("ST.diag.score") === 9 && w.E("ST.diag.max") === 9, "診斷得分與滿分正確寫入狀態");
    ok(w.E("ST.badges.indexOf('diag')>=0"), "分層完成徽章");
    await sleep(1500);
    ok(!w.document.getElementById("mask").classList.contains("on"), "1.4 秒後診斷彈窗自動關閉");
    w.E('UI.open("steps")');
    ok(/分步列式/.test(w.document.getElementById("mTitle").textContent), "診斷後主線正常開啟");
  }
  {
    const w2 = await boot(); finishDiag(w2, 4);
    ok(w2.E("ST.diag.level") === 2 && w2.E("ST.diag.score") === 6, "前 4 題答對（6 分）→ ★★ 發展層");
    const w1 = await boot(); finishDiag(w1, 2);
    ok(w1.E("ST.diag.level") === 1 && w1.E("ST.diag.score") === 2, "只答對 2 題基礎（2 分）→ ★ 基礎層");
  }

  console.log("\n【2b】加權分層精準度：5 題 9 分仍可拉開層級");
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

  console.log("\n【3】分層針對性：每層只派 4 題出門票；分步／錯例為參考示範");
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

  console.log("\n【4】比例尺專用六種像素圖解＋入場動畫");
  {
    const w = await boot(2);
    ["meaning", "unit", "ratio", "line", "zoom", "flow"].forEach(function (tp) {
      const s = w.E("FIG.draw({t:'" + tp + "'},{stage:0})");
      const shapes = (s.match(/<(rect|text|path)/g) || []).length;
      ok(s.indexOf("<svg") === 0 && s.indexOf("</svg>") > 0 && shapes >= 6,
        "FIG." + tp + " 畫出 " + shapes + " 個像素元件");
    });
    ok(w.E("FIG._arrow()") === "", "保留 _arrow() 相容 stub，推演頁不靜默死機");
    const ln = w.E("FIG.draw({t:'line',step:50,unit:'m'},{stage:0})");
    ok(ln.indexOf("0") > 0 && ln.indexOf("50") > 0 && ln.indexOf("1 : 5000") > 0,
      "線段比例尺圖正確換算 50 m → 1 : 5000");
    const zm = w.E("FIG.draw({t:'zoom'},{stage:0})");
    ok(zm.indexOf("10 : 1") > 0 && zm.indexOf("實際 1 格") > 0, "放大比例尺圖解說明 10 : 1");
    const sv = w.E("FIG.draw({t:'ratio',a:5,b:2400,n:480},{stage:1})");
    const fa = (sv.match(/class=\"fa /g) || []).length;
    const anim = (sv.match(/animation-delay:/g) || []).length;
    ok(fa >= 10 && anim === fa, "每個元件都有逐格入場動畫（" + anim + "/" + fa + "）");
    ok(sv.indexOf("crispEdges") > 0, "SVG 啟用 crispEdges 硬邊");
    const mv = w.E("FIG.draw({t:'meaning',map:1,real:25},{stage:0})");
    ok(mv.indexOf("#25243A") > 0 && sv.indexOf("#2E5CA8") > 0,
      "像素色盤正確寫入（不會變黑色）");
    ok(sv.indexOf("1 : 480") > 0, "化簡比圖顯示課本附加例題答案 1 : 480");
    w.go("intro");
    ok(w.document.querySelectorAll("#page-intro .figbox svg").length === 1, "引入頁主視覺（比例尺的意義）");
    ok(/教學目標/.test(w.document.getElementById("page-intro").textContent), "引入頁列出四個教學目標");
    ok(/數學小百科/.test(w.document.getElementById("page-intro").textContent) ||
      /10 : 1/.test(w.document.getElementById("page-intro").textContent), "引入頁含放大比例尺小百科");
    w.go("explore");
    for (let i = 0; i < 6; i++) w.E("Explore.step()");
    ok(w.document.querySelectorAll("#deriveInline .figbox").length === 3, "推演三步解鎖各出一張圖");
    w.BZ.UI.open("steps");
    ok(/參考示範/.test(w.document.getElementById("mBody").textContent) &&
       w.document.querySelectorAll("#mBody .sc-src").length === 4,
      "分步示範頁列出本層 4 題題目、答案與教材依據");
  }

  console.log("\n【5】一次作答即鎖定：答錯不能修改，錯題一定留下");
  {
    const w = await boot(2);
    w.E('UI.open("exit")');
    const item = w.document.querySelector("#mBody .sc-item");
    const idx = w.E("activeIds('exit')[0]");
    ok(!w.document.querySelector('#mBody [data-act="hint"]'), "沒有可自行按下的提示掣");
    ok(!!w.document.querySelector("#mBody .hint-lock"), "顯示「作答前不能查看提示」說明");
    ok(!w.document.querySelector("#mBody .sc-hint.on"), "作答前提示保持隱藏");
    item.querySelector(".sc-in").value = "999";
    item.querySelector('[data-act="check"]').click();
    ok(w.E("ST.wrongBook.length") === 1, "答錯 → 錯題本 +1");
    ok(w.E("ST.wrongBook[0].mine") === "999", "記錄學生當時的答案");
    ok(w.E("ST.wrongBook[0].ans") !== "999" && w.E("ST.wrongBook[0].ans.length>0"), "記錄正確答案");
    ok(w.E("ST.wrongBook[0].why.length>0"), "inferConcept() 自動歸類錯因：" + w.E("ST.wrongBook[0].why"));
    ok(w.E("ST.exit[" + idx + "].locked") === true, "作答後 rec.locked = true");
    ok(item.querySelector(".sc-in").disabled && item.querySelector('[data-act="check"]').disabled,
      "輸入框與檢查掣即時鎖定");
    ok(!!item.querySelector(".sc-hint.on"), "提示在答錯之後自動出現");
    ok(/不能修改/.test(item.querySelector(".sc-fb").textContent), "明確告知此題不能修改");
    ok(w.E("redoCount()") === 1, "待訂正 1 題");
    item.querySelector(".sc-in").disabled = false;
    item.querySelector(".sc-in").value = w.E("DATA.exit[" + idx + "].a[0]");
    item.querySelector('[data-act="check"]').click();
    ok(w.E("ST.wrongBook.length") === 1 && w.E("ST.wrongBook[0].fixed") === false,
      "即使再填入正確答案，錯題仍然存在、不會被當成沒錯過");
    w.E('UI.open("exit")');
    const again = w.document.querySelector("#mBody .sc-item");
    ok(again.querySelector(".sc-in").disabled, "重開頁面後原題仍是鎖定狀態");
    ok(/已記入錯題本/.test(again.querySelector(".sc-fb").textContent), "重開頁面仍顯示錯題回饋");
    ok(!!again.querySelector(".sc-hint.on"), "重開頁面提示仍可見（因曾答錯）");
    const fb = again.querySelector(".sc-fb");
    ok(fb.className.indexOf("sc-bad") >= 0 && fb.className.indexOf("sc-no") < 0,
      "回饋區使用 .sc-bad，不與題號圓圈 .sc-no 撞名");
  }

  console.log("\n【6】錯題報告 → 錯題重練訂正");
  {
    const w = await boot(2);
    w.E('UI.open("exit")');
    const item = w.document.querySelector("#mBody .sc-item");
    item.querySelector(".sc-in").value = "999";
    item.querySelector('[data-act="check"]').click();
    w.E('UI.open("wrong")');
    const t = w.document.getElementById("mBody").textContent;
    ok(/錯題報告/.test(t) && /學生答案/.test(t) && /正確答案/.test(t), "錯題報告：原題／學生答案／正確答案");
    ok(/錯因概念分布/.test(t) && /待訂正/.test(t), "錯因分布＋訂正狀態");
    ok(/逐題對照/.test(t), "逐題對照表");
    w.E('UI.open("redo")');
    const r = w.document.querySelector("#mBody .sc-item");
    ok(!!r, "重練自動出 1 題");
    ok(!r.querySelector('[data-a="tip"]'), "重練區也沒有可自行按下的提示掣");
    ok(/變式題/.test(w.document.getElementById("mBody").textContent), "標明同類型變式題");
    ok(/當時作答/.test(w.document.getElementById("mBody").textContent), "顯示原錯題回顧");
    const correct = w.E('(function(){var k=ST.wrongBook[0].key;var i=+k.split("-")[1];return DATA.exit[i].redo.a[0];})()');
    r.querySelector(".sc-in").value = correct;
    r.querySelector('[data-a="ck"]').click();
    ok(w.E("ST.wrongBook[0].fixed") === true, "變式題答對 → 標記已訂正");
    ok(w.E("redoCount()") === 0, "待訂正歸零");
    ok(w.E("ST.badges.indexOf('redo')>=0"), "獲得「訂正達人」徽章");
    ok(w.E("ST.xp") > 0, "訂正加經驗值：" + w.E("ST.xp"));
  }

  console.log("\n【6b】重練答錯：不能原地改，只能「再練一次」");
  {
    const w = await boot(2);
    w.E('UI.open("exit")');
    const it0 = w.document.querySelector("#mBody .sc-item");
    it0.querySelector(".sc-in").value = "999";
    it0.querySelector('[data-act="check"]').click();
    w.E('UI.open("redo")');
    const r = w.document.querySelector("#mBody .sc-item");
    r.querySelector(".sc-in").value = "888";
    r.querySelector('[data-a="ck"]').click();
    ok(w.E("redoCount()") === 1, "重練答錯 → 錯題仍在錯題本");
    ok(r.querySelector(".sc-in").disabled, "重練答錯後輸入框鎖定");
    ok(!!r.querySelector(".sc-hint.on"), "重練提示在答錯後自動出現");
    ok(!!r.querySelector('[data-a="again"]'), "提供「再練一次」按鈕（不是原地修改）");
    r.querySelector('[data-a="again"]').click();
    const again = w.document.querySelector("#mBody .sc-item");
    ok(!again.querySelector(".sc-in").disabled, "「再練一次」後重新開放作答");
    ok(w.E("ST.wrongBook[0].fixed") === false, "再練前錯題尚未訂正");
  }

  console.log("\n【6c】錯例醫院改為參考示範，不產生作答題");
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

  console.log("\n【7】學生個人報告：五段＋姓名欄＋PNG 報告卡");
  {
    const w = await boot(2);
    w.E('UI.open("exit")');
    const it = w.document.querySelector("#mBody .sc-item");
    it.querySelector(".sc-in").value = "777";
    it.querySelector('[data-act="check"]').click();
    w.E('UI.open("report")');
    ok(/我的學習報告/.test(w.document.getElementById("mTitle").textContent), "報告標題為學生視角");
    const t = w.document.getElementById("mBody").textContent;
    ["一、整體表現", "二、我的錯題", "三、需要加強的概念", "四、給我的建議", "五、本層逐題記錄"].forEach(function (s) {
      ok(t.indexOf(s) >= 0, "報告含「" + s + "」");
    });
    ok(/時間預算 15 分鐘/.test(t), "報告列出 15 分鐘時間預算");
    ok(/本層主題/.test(t), "報告列出本層主題");
    const sumBoxes = Array.from(w.document.querySelectorAll("#mBody .sum-box")).map(b => b.textContent);
    ok(!sumBoxes.some(s => /-\d/.test(s)), "統計格沒有負數（答錯後「答對」不可變成 -1）");
    ok(/答對0/.test(sumBoxes.join("").replace(/\s/g, "")),
      "一次作答制下答對數正確為 0（改用 stat.ok 計算）");
    const recTables = w.document.querySelectorAll("#mBody table");
    ok(recTables.length > 0 && recTables[recTables.length - 1].querySelectorAll("tr").length === 5,
      "本層逐題記錄含 4 題出門票＋標題列（分步與錯例不計）");
    ok(w.E('inferConcept("線段比例尺每格 1 cm 代表 50 m，寫成數值比例尺")') === "線段比例尺換算",
      "線段比例尺題正確歸類");
    ok(w.E('inferConcept("設計圖上 7.5 dm 代表實際 15 mm，比例尺是 50 : 1")') === "放大比例尺的辨認",
      "放大比例尺題正確歸類（含 50 : 1）");
    ok(w.E('inferConcept("正方形水池實際邊長 24 米，先把 24 米化成 （　）厘米")') === "長度單位統一",
      "單位換算題正確歸類");
    ok(w.E('inferConcept("化簡比 12 : 18 ＝ 2 : （　）")') === "比的化簡",
      "比的化簡題正確歸類");
    const htmlOrder = w.document.getElementById("mBody").innerHTML;
    ok(htmlOrder.indexOf('data-a="card"') < htmlOrder.indexOf("一、整體表現"),
      "「產生報告圖片」按鈕置於報告頂部，學生一開即見");
    const wi = w.document.querySelector("#whoInput");
    ok(!!wi, "學生可填寫姓名／班別／座號");
    wi.value = "六年級甲班 12 號 陳大明";
    wi.dispatchEvent(new w.Event("input", { bubbles: true }));
    ok(w.E("ST.who") === "六年級甲班 12 號 陳大明", "姓名寫入狀態（會持久化）");

    const url = w.E("makeCard()");
    ok(typeof url === "string" && url.indexOf("data:image/png") === 0, "產生 PNG dataURL：" + url);
    ok(!!w.document.querySelector("#cardImg"), "報告圖片預覽插入頁面");
    const dl = w.document.querySelector("#cardDl");
    ok(!!dl && /\.png$/.test(dl.getAttribute("download")), "提供「下載 PNG」按鈕（可上傳給老師）");
    ok(/陳大明/.test(dl.getAttribute("download")), "檔名包含學生姓名，老師易於辨識");
    ok(/認識比例尺/.test(dl.getAttribute("download")), "檔名標示課題為認識比例尺");
    const texts = w.__cardTexts.join("\n");
    ok(/今日須作答 9 題/.test(texts), "報告卡標示今日共 9 題（診斷 5＋出門票 4）");
    ok(/陳大明/.test(texts), "圖片內容印有學生姓名");
    ok(/我的學習報告/.test(texts), "圖片內容印有報告標題");
    ok(/認識比例尺/.test(texts), "圖片內容印有課題");
    ok(/需要加強的概念/.test(texts) && /給我的建議/.test(texts), "圖片內容含概念與建議兩段");
    ok(/錯題/.test(texts), "圖片內容含錯題資訊");
    ok(/0 \/ 4/.test(texts), "報告卡統計分母為 4 題，與今日配題一致");
    ok(/診斷 \d+ \/ 9 分/.test(texts), "報告卡印出診斷加權得分（滿分 9）");
    ok(/④-\d/.test(texts) && !/steps-/.test(texts), "報告卡使用學生可讀題號（④-N），不顯示內部 key");
    ok(w.__cardYs.length > 0 && Math.max.apply(null, w.__cardYs) < 1360,
      "報告卡所有文字都落在 1360 高畫布內（動態排版不溢出）");
    ok(w.E("BZ.card()") === url, "公開 API BZ.card() 亦可直接產生圖片");
  }

  console.log("\n【7b】老師專用：教材依據一覽");
  {
    const w = await boot(2);
    w.E('UI.open("teacher")');
    ok(w.document.querySelectorAll("#mBody .t-btn").length === 8, "老師專用 8 個入口（移除重做診斷）");
    w.E('UI.open("sources")');
    const t = w.document.getElementById("mBody").textContent;
    ok(/教材依據一覽/.test(t) && /課本 p.52/.test(t), "教材依據面板列出課本與附加例題");
    ok(/練習13/.test(t) && /工作紙 24.png/.test(t), "教材依據面板列出習作與工作紙");
    ok(/四、逐題對照/.test(t), "教材依據面板含逐題對照表");
    ok(w.document.querySelectorAll("#mBody table tr").length === 31, "逐題對照表：標題列＋12 分步＋6 錯例＋12 出門票");
    ok(/不涉及後續章節/.test(t), "教材依據面板明確標示章節邊界");
  }

  console.log("\n【8】總結卡、底部導航、存檔");
  {
    const w = await boot(2);
    w.E('UI.open("summary")');
    const s = w.document.getElementById("mBody").textContent;
    ok(/待訂正錯題/.test(s) && /本課算法/.test(s) && /時間預算/.test(s), "總結卡含錯題數／算法／時間預算");
    ok(!!w.document.querySelector('#mBody [data-a="card"]'), "總結卡有「產生報告圖片」掣");
    ok(!!w.document.querySelector('#mBody [data-a="report"]'), "總結卡有「我的學習報告」掣");
    w.E('UI.open("exit")');
    const nav = Array.from(w.document.querySelectorAll("#mBtns [data-f]")).map(b => b.textContent).join(" ");
    ok(/上一步/.test(nav) && /今日總結/.test(nav), "底部導航串接主線（出門票後接今日總結）");
    const item = w.document.querySelector("#mBody .sc-item");
    const idx = w.E("activeIds('exit')[0]");
    item.querySelector(".sc-in").value = w.E("DATA.exit[" + idx + "].a[0]");
    item.querySelector('[data-act="check"]').click();
    const saved = JSON.parse(w.localStorage.getItem(SKEY));
    ok(saved.exit[idx] && saved.exit[idx].done, "完成狀態寫入 localStorage");
    ok(Array.isArray(saved.wrongBook), "錯題本一併持久化");
    ok(!/bz_ratio/.test(html), "localStorage key 已改為本課專用，不與《解比例》共用進度");
  }

  console.log("\n【9】出門票「已作答」即自動彈總結（答對／答錯都會）");
  {
    const w = await boot(2);
    w.E('UI.open("exit")');
    const items = w.document.querySelectorAll("#mBody .sc-item");
    items.forEach(function (it, n) {
      const idx = w.E("activeIds('exit')[" + n + "]");
      it.querySelector(".sc-in").value = w.E("DATA.exit[" + idx + "].a[0]");
      it.querySelector('[data-act="check"]').click();
    });
    const idx = w.E("activeIds('exit')[0]");
    ok(w.E("ST.exit[" + idx + "].done") === true, "出門票 4 題皆答對");
    await sleep(1000);
    ok(/今日總結/.test(w.document.getElementById("mTitle").textContent), "0.8 秒後自動彈今日總結");
  }
  {
    const w = await boot(1);
    w.E('UI.open("exit")');
    const items = w.document.querySelectorAll("#mBody .sc-item");
    items.forEach(function (it, n) {
      const idx = w.E("activeIds('exit')[" + n + "]");
      it.querySelector(".sc-in").value = n === 0 ? "___wrong___" : w.E("DATA.exit[" + idx + "].a[0]");
      it.querySelector('[data-act="check"]').click();
    });
    ok(w.E("ST.wrongBook.length") === 1, "出門票答錯也記入錯題本");
    await sleep(1000);
    ok(/今日總結/.test(w.document.getElementById("mTitle").textContent), "答錯仍自動彈總結，讓學生看到錯題報告");
  }

  console.log("\n【10】數學正確性與教材原式對齊（第13課）");
  {
    ok(Math.abs(2400 / 5 - 480) < 1e-9, "課本附加例題 1：5 : 2400 ＝ 1 : 480");
    ok(Math.abs(9000 / 4.5 - 2000) < 1e-9, "課本附加例題 2：4.5 : 9000 ＝ 1 : 2000");
    ok(Math.abs(4000 / 25 - 160) < 1e-9, "課本附加例題 3(a)：25 : 4000 ＝ 1 : 160");
    ok(Math.abs(9000 / 12 - 750) < 1e-9, "課本附加例題 3(b)：12 : 9000 ＝ 1 : 750");
    ok(Math.abs(36300 / 1.1 - 33000) < 1e-9, "工作紙冊：1.1 : 36 300 ＝ 1 : 33 000");
    ok(Math.abs(95000000 / 19 - 5000000) < 1e-9, "工作紙冊：19 : 95 000 000 ＝ 1 : 5 000 000");
    ok(Math.abs(50 * 100 - 5000) < 1e-9, "線段比例尺 1 cm : 50 m ＝ 1 : 5000");
    ok(Math.abs(100 * 100000 - 10000000) < 1e-9, "線段比例尺 1 cm : 100 km ＝ 1 : 10 000 000");
    ok(Math.abs(750 / 15 - 50) < 1e-9, "練習13 第40題：750 : 15 ＝ 50 : 1（放大）");
    ok(Math.abs(24 / 8 - 3) < 1e-9, "練習13 第42題：24 : 8 ＝ 3 : 1（放大）");
    const w = await boot(2);
    ok(w.E("DATA.steps[4].a[0]") === "480" && w.E("DATA.exit[4].a[0]") === "2000", "題庫答案與課本附加例題一致");
    ok(w.E("DATA.steps[5].a[0]") === "33000" && w.E("DATA.steps[9].a[0]") === "50", "題庫答案與工作紙／練習13一致");
    ok(w.E("DATA.clinic.every(c=>c.size==='big'||c.size==='small')"), "錯例全部標明估大小方向");
    ok(w.E("DATA.clinic.every(c=>c.redo&&c.redo.a)"), "錯例全部有變式題");
    ok(w.E("DATA.steps.every(s=>[1,2,3].indexOf(s.d)>=0)"), "每題都有 d:1/2/3 難度標記");
    ok(w.E("[1,2,3].every(L=>DATA.steps.filter(s=>s.d===L).length===4 && DATA.clinic.filter(c=>c.d===L).length===2 && DATA.exit.filter(e=>e.d===L).length===4)"),
      "每層恰有 4 分步示範＋2 錯例示範＋4 出門票");
    ok(w.E("DIAG.reduce((s,q)=>s+q.d,0)===9 && DIAG.filter(q=>q.d===3).length===1"),
      "診斷加權總分 9 分，含 1 題 3 分題");
    ok(w.E("[1,2,3].every(L=>DATA.steps.some(s=>s.d===L))"), "三個層級都有對應分步題");
    ok(w.E("[1,2,3].every(L=>DATA.exit.some(s=>s.d===L))"), "三個層級都有對應出門票");
    ok(w.E("[1,2,3].every(L=>DATA.clinic.some(s=>s.d===L))"), "三個層級都有對應錯例");
    ok(w.E("!DATA.steps.some(s=>/承第/.test(s.t))"), "題目之間沒有未做的 Dependency");
    ok(w.E("!DATA.steps.some(s=>/第\\s*[0-9]+\\s*組/.test(s.t))"), "沒有「第 N 組」這類無意義前綴");
    ok(w.E("new Set(DATA.steps.map(s=>s.fig.t)).size===5") ||
       w.E("new Set(DATA.steps.map(s=>s.fig.t)).size>=4"), "分步題使用多種像素圖解（題型多樣性）");
    ok(w.E("DATA.steps.some(s=>s.t.indexOf('線段')>=0) && DATA.steps.some(s=>s.t.indexOf('設計圖')>=0)"),
      "涵蓋線段比例尺與放大比例尺兩種題型");
    ok(w.E("norm('33,000') === norm('33000') && norm('33 000') === norm('33000')"),
      "作答容錯：逗號與空白不影響判讀");
  }

  console.log("\n【11】品質鐵律：書面語／章節邊界／單檔／機制");
  {
    ok(!/[喺咗嘅啲啱睇撳搵佢晒唔嗰嚟]/.test(html), "成品沒有粵語口語字（學生可見文字為書面語）");
    ok(!/正比例|反比例|體積|圓面積|求實際距離|求圖上距離|比例尺的應用|第14課/.test(html),
      "沒有混入後續章節（第14課／正反比例／體積／反求）");
    ok(/比例尺 ＝ 圖上距離 : 實際距離/.test(html), "核心定義「圖上距離 : 實際距離」存在");
    ok(/線段比例尺/.test(html) && /10 : 1/.test(html), "線段比例尺與放大比例尺 10 : 1 皆存在");
    ok(/教材依據/.test(html) && /B-2-15/.test(html), "逐題教材依據與基本學力編碼皆存在");
    ok(!/第\s*\d+\s*組/.test(html), "沒有「第 N 組」這類無意義前綴");
    const linkHrefs = (html.match(/<link\s+[^>]*href="([^"]*)"/g) || [])
      .map(s => s.match(/href="([^"]*)"/)[1]);
    ok(linkHrefs.length === 1 && linkHrefs[0].startsWith("data:image/svg+xml") &&
       !/<script\s+src=/.test(html.split("UI.share")[0]),
      "單檔自足、零外連（僅內嵌 favicon；報告頁 QR 除外）");
    ok(!/data-act="hint"|data-a="tip"/.test(html), "成品沒有任何可自行按下的提示掣");
    ok(/rec\.locked=true/.test(html) && /hintEl\.classList\.add\("on"\)/.test(html),
      "一次作答即鎖定＋提示僅在答錯後顯示");
    ok(/function drawCard\(\)/.test(html) && /toDataURL\("image\/png"\)/.test(html), "PNG 報告卡為 Canvas 原生繪製（零外連）");
    ok(/assetUrl\("qrcode.min.js"\)/.test(html) && /rel="icon" href="data:image\/svg\+xml/.test(html),
      "雲端部署修正保留（QR 絕對 URL＋內嵌 favicon）");
    ok(/分層診斷已完成，不可重做/.test(html) && /不能補答/.test(html),
      "診斷不可重做：答錯即鎖、不補答、完成後只顯示結果");
    ok(!/t:"重做分層診斷"/.test(html), "老師專用已移除重做診斷入口");
    ok(/if\(stage!=="exit"\) return \[\];/.test(html),
      "只有出門票派題，分步與錯例不產生作答題");
    ok(/今日須作答 9 題（診斷 5 ＋ 出門票 4）/.test(html), "教材標示今日共 9 題");
    ok(/出門票 5–9（依層級）/.test(html) && /全程約 13–17 分鐘/.test(html),
      "時間預算列出逐題秒數實算的層級區間，不再寫死 7 分鐘");
    ok(!/題（示範）/.test(html), "配對表已去掉括號，不會產生孤字「範）」");
    const w2 = await boot(2);
    const scriptTags = w2.document.querySelectorAll("script").length;
    ok(scriptTags === 2, "HTML parser 解析出 2 個內嵌 script 且都正確閉合（" + scriptTags + "）");
  }

  console.log("\n===== " + pass + " 通過 / " + fail + " 失敗 =====（v4：診斷 5 題／9 分／不可重做；每層 4 題出門票）");
  process.exit(fail ? 1 : 0);
})();
