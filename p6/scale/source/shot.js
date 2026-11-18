/* 《認識比例尺｜像素風》實機視覺驗證：
   本機 Chrome 截關鍵畫面＋真正產生 PNG 報告卡＋六種像素圖解巡檢 */
const puppeteer = require("puppeteer");
const fs = require("fs");

const FILE = "file:///Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風/認識比例尺-像素風.html";
const OUT = "/tmp";
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
    args: ["--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--font-render-hinting=none"]
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 1 });
  const errs = [];
  page.on("pageerror", e => errs.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error") errs.push("console: " + m.text()); });

  await page.goto(FILE, { waitUntil: "load" });
  await wait(900);
  await page.screenshot({ path: OUT + "/scale-1-intro.png", fullPage: true });

  /* 六種像素圖解巡檢：直接把六張 SVG 鋪在頁面上目測 */
  const figs = await page.evaluate(() => {
    const types = ["meaning", "unit", "ratio", "line", "zoom", "flow"];
    const out = {};
    let gallery = '<div style="font:bold 20px sans-serif;padding:8px">第13課 六種像素圖解</div>';
    types.forEach(function (t) {
      const f = t === "ratio" ? { t: t, a: 5, b: 2400, n: 480 }
        : t === "line" ? { t: t, step: 50, unit: "m" }
          : { t: t, map: 1, real: 25, cap: t };
      const svg = FIG.draw(f, { stage: 0 });
      out[t] = {
        shapes: (svg.match(/<(rect|text|path)/g) || []).length,
        bad: /undefined|NaN/.test(svg),
        len: svg.length
      };
      gallery += '<div style="display:inline-block;width:47%;margin:8px;border:3px solid #25243A;background:#FFFDF6;vertical-align:top">' +
        '<div style="font:bold 15px sans-serif;padding:6px;background:#2E5CA8;color:#fff">' + t +
        '　' + out[t].shapes + ' 個元件</div>' + svg + '</div>';
    });
    const d = document.createElement("div");
    d.id = "figGallery";
    d.style.cssText = "position:fixed;inset:0;z-index:9999;background:#F3EFE1;overflow:auto;padding:12px";
    d.innerHTML = gallery;
    document.body.appendChild(d);
    return out;
  });
  console.log("六種像素圖解：", JSON.stringify(figs));
  await wait(300);
  await page.screenshot({ path: OUT + "/scale-9-figures.png" });
  await page.evaluate(() => { const d = document.getElementById("figGallery"); if (d) d.remove(); });

  /* 完成診斷 → 練習頁 */
  await page.evaluate(() => {
    BZ.UI.open("diag");
    const ans = BZ.DIAG.map(q => q.a[0]);
    document.querySelectorAll("#mBody .sc-item").forEach((it, i) => {
      it.querySelector(".sc-in").value = ans[i];
      it.querySelector('[data-a="ck"]').click();
    });
    document.querySelector('#mBody [data-a="fin"]').click();
  });
  await wait(1700);
  await page.evaluate(() => BZ.go("practice"));
  await wait(400);
  await page.screenshot({ path: OUT + "/scale-2-practice.png", fullPage: true });

  /* 分步列式：本層 4 題參考示範＋教材依據 */
  await page.evaluate(() => BZ.UI.open("steps"));
  await wait(500);
  await page.screenshot({ path: OUT + "/scale-3-steps.png" });
  const srcInfo = await page.evaluate(() => {
    const el = document.querySelector("#mBody .sc-src");
    if (!el) return { exists: false };
    const r = el.getBoundingClientRect();
    return { exists: true, width: Math.round(r.width), height: Math.round(r.height), text: el.textContent.slice(0, 40) };
  });
  console.log("教材依據列：", JSON.stringify(srcInfo));

  /* 答錯 → 一次鎖定＋提示自動出現（改用出門票驗證） */
  await page.evaluate(() => {
    BZ.UI.close();
    BZ.UI.open("exit");
    const it = document.querySelector("#mBody .sc-item");
    it.querySelector(".sc-in").value = "999";
    it.querySelector('[data-act="check"]').click();
  });
  await wait(400);
  await page.screenshot({ path: OUT + "/scale-4-locked.png" });
  const fbInfo = await page.evaluate(() => {
    const fb = document.querySelector("#mBody .sc-fb");
    const r = fb ? fb.getBoundingClientRect() : null;
    const mb = document.getElementById("mBody");
    const mr = mb ? mb.getBoundingClientRect() : null;
    return {
      width: r ? Math.round(r.width) : 0,
      height: r ? Math.round(r.height) : 0,
      fullyVisible: !!(r && mr && r.top >= mr.top && r.bottom <= mr.bottom),
      redoBtn: !!document.querySelector('#mBody .sc-fb [data-act="toredo"]'),
      outerBtnsHidden: (() => {
        const b = document.querySelector("#mBody .sc-item > .sc-btns");
        return !b || getComputedStyle(b).display === "none";
      })()
    };
  });
  const fbOk = fbInfo.width > 500 && fbInfo.height >= 100 && fbInfo.fullyVisible &&
    fbInfo.redoBtn && fbInfo.outerBtnsHidden;
  console.log("回饋區可見性：", fbOk ? "✅ 完整可見、按鈕已收回" : "❌ 仍有裁切", JSON.stringify(fbInfo));

  /* 錯題報告 */
  await page.evaluate(() => BZ.UI.open("wrong"));
  await wait(400);
  await page.screenshot({ path: OUT + "/scale-5-wrong.png" });

  /* 老師專用 → 教材依據一覽 */
  await page.evaluate(() => BZ.UI.open("sources"));
  await wait(400);
  await page.screenshot({ path: OUT + "/scale-8-sources.png" });

  /* 學生個人報告 → 真正產生 PNG 報告卡 */
  const card = await page.evaluate(() => {
    BZ.UI.open("report");
    const wi = document.querySelector("#whoInput");
    wi.value = "六年級甲班 12 號 陳大明";
    wi.dispatchEvent(new Event("input", { bubbles: true }));
    return BZ.card();
  });
  fs.writeFileSync(OUT + "/scale-6-card.png", Buffer.from(card.split(",")[1], "base64"));
  await wait(500);
  await page.screenshot({ path: OUT + "/scale-7-report.png", fullPage: true });

  /* 讀取實際運算狀態 */
  const state = await page.evaluate(() => ({
    level: BZ.level,
    diagScore: BZ.ST.diag.score + " / " + BZ.ST.diag.max,
    planCounts: [BZ.activeIds("steps").length, BZ.activeIds("clinic").length, BZ.activeIds("exit").length],
    xp: BZ.ST.xp,
    who: BZ.ST.who,
    wrongBook: BZ.ST.wrongBook.length,
    redoCount: BZ.summary().redoCount,
    pixEnabled: window.PIX.enabled,
    exitLocked: (() => {
      const i = BZ.activeIds("exit")[0];
      return !!(BZ.ST.exit[i] && BZ.ST.exit[i].locked);
    })(),
    cardDataUrlLen: (document.querySelector("#cardImg") || {}).src ? document.querySelector("#cardImg").src.length : 0,
    downloadName: (document.querySelector("#cardDl") || {}).getAttribute
      ? document.querySelector("#cardDl").getAttribute("download") : "",
    plan: BZ.planOf().topic,
    visibleItems: document.querySelectorAll("#mBody .sc-item").length,
    figVisible: (() => {
      const el = document.querySelector("#mBody .figsvg .fa") || document.querySelector("#page-intro .figsvg .fa");
      if (!el) return "no-svg-in-current-view";
      return getComputedStyle(el).opacity;
    })(),
    docHeight: document.documentElement.scrollHeight
  }));
  console.log("實機狀態：", JSON.stringify(state));
  console.log("報告卡 PNG：", fs.statSync(OUT + "/scale-6-card.png").size, "bytes");
  console.log("JS 錯誤：", errs.length ? errs.join(" | ") : "無");
  await browser.close();
})();
