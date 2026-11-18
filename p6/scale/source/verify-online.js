/* 線上版《認識比例尺》v4 實機驗證：HTTPS + 子目錄 + 兩份教材並存 */
const puppeteer = require("puppeteer");
const NEW_URL = "https://souchonun-arch.github.io/math-game-hub/p6/scale/";
const OLD_URL = "https://circle-shadow-area.app.workbuddy.host/?sharecode=LVOZUPT54H";
const wait = ms => new Promise(r => setTimeout(r, ms));
let pass = 0, fail = 0;
const ok = (c, m) => { if (c) { pass++; console.log("✅ " + m); } else { fail++; console.log("✗ " + m); } };

(async () => {
  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
    args: ["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"]
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 1 });
  const errs = [], bad = [];
  page.on("pageerror", e => errs.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error") errs.push("console: " + m.text()); });
  page.on("response", r => { if (r.status() >= 400) bad.push(r.status() + " " + r.url()); });
  page.on("requestfailed", r => bad.push("failed " + r.url()));

  await page.goto(NEW_URL, { waitUntil: "networkidle2" });
  await wait(900);

  const b = await page.evaluate(() => ({
    title: document.title,
    lesson: typeof CFG !== "undefined" ? CFG.lesson : "",
    minutes: typeof CFG !== "undefined" ? CFG.minutes : -1,
    diag: typeof DIAG !== "undefined" ? DIAG.length : -1,
    steps: typeof DATA !== "undefined" ? DATA.steps.length : -1,
    clinic: typeof DATA !== "undefined" ? DATA.clinic.length : -1,
    exit: typeof DATA !== "undefined" ? DATA.exit.length : -1,
    hasBZ: typeof BZ !== "undefined",
    asset: typeof assetUrl === "function" ? assetUrl("qrcode.min.js") : "",
    favicon: !!document.querySelector('link[rel="icon"]'),
    storage: (() => { try { localStorage.setItem("_t", "1"); localStorage.removeItem("_t"); return true; } catch (e) { return false; } })(),
    canvas: (() => { const c = document.createElement("canvas"); c.width = c.height = 10; const x = c.getContext("2d"); return !!x && c.toDataURL("image/png").indexOf("data:image/png") === 0; })()
  }));

  ok(/認識比例尺/.test(b.title), "頁面標題正確：" + b.title);
  ok(b.lesson === "第13課｜認識比例尺", "課題為第13課「認識比例尺」");
  ok(b.hasBZ, "教材引擎 BZ 正常掛載");
  ok(b.diag === 5, "診斷題數為 5 題（實際 " + b.diag + "）");
  ok(b.steps === 12 && b.clinic === 6 && b.exit === 12, "題庫 12／6／12（實際 " + b.steps + "／" + b.clinic + "／" + b.exit + "）");
  ok(b.minutes === 15, "時間預算 15 分鐘（實際 " + b.minutes + "）");
  ok(b.storage, "HTTPS origin 下 localStorage 可寫入");
  ok(b.canvas, "Canvas 可產生 PNG 報告卡");
  ok(b.favicon, "內嵌 favicon，避免 /favicon.ico 404");
  ok(b.asset.indexOf("/p6/scale/qrcode.min.js") > 0, "QR 資源解析到正確子目錄：" + b.asset);

  const qr = await page.evaluate(async () => {
    try { const r = await fetch(assetUrl("qrcode.min.js")); return r.status; } catch (e) { return 0; }
  });
  ok(qr === 200, "老師專用 QR 元件線上載入 HTTP 200（實際 " + qr + "）");

  /* 診斷 5 題全部答對 → 9 / 9 分 → ★★★ */
  const diagInfo = await page.evaluate(() => {
    BZ.UI.open("diag");
    const items = document.querySelectorAll("#mBody .sc-item");
    const ans = BZ.DIAG.map(q => q.a[0]);
    items.forEach((it, i) => {
      it.querySelector(".sc-in").value = ans[i];
      it.querySelector('[data-a="ck"]').click();
    });
    document.querySelector('#mBody [data-a="fin"]').click();
    return { count: items.length, score: BZ.ST.diag.score, max: BZ.ST.diag.max, level: BZ.level };
  });
  ok(diagInfo.count === 5 && diagInfo.score === 9 && diagInfo.max === 9 && diagInfo.level === 3,
    "線上完成 5 題診斷 → 9 / 9 分 → ★★★（實際 " + JSON.stringify(diagInfo) + "）");

  /* 診斷不可重做、答錯不補答 */
  const diagAgain = await page.evaluate(() => {
    BZ.UI.open("diag");
    const t = document.getElementById("mBody").textContent;
    return { locked: /分層診斷已完成，不可重做/.test(t), items: document.querySelectorAll("#mBody .sc-item").length };
  });
  ok(diagAgain.locked && diagAgain.items === 0, "診斷完成後不可重做，不再顯示作答題");

  /* 只派 4 題出門票；分步與錯例為參考示範 */
  const plan = await page.evaluate(() => {
    BZ.UI.close();
    const c = [BZ.activeIds("steps").length, BZ.activeIds("clinic").length, BZ.activeIds("exit").length];
    BZ.UI.open("steps");
    const demo = /參考示範/.test(document.getElementById("mBody").textContent) &&
      document.querySelectorAll("#mBody .sc-item").length === 0;
    BZ.UI.close();
    BZ.UI.open("exit");
    return { counts: c, demo: demo, exitItems: document.querySelectorAll("#mBody .sc-item").length };
  });
  ok(JSON.stringify(plan.counts) === "[0,0,4]" && plan.exitItems === 4,
    "每層只派 4 題出門票（實際 " + JSON.stringify(plan.counts) + "／" + plan.exitItems + " 題）");
  ok(plan.demo, "分步列式為參考示範頁，不產生作答題");

  /* 答錯即鎖、自動記入錯題本、提示自動出現 */
  const wrong = await page.evaluate(() => {
    const it = document.querySelector("#mBody .sc-item");
    it.querySelector(".sc-in").value = "999";
    it.querySelector('[data-act="check"]').click();
    const i = BZ.activeIds("exit")[0];
    const r = BZ.ST.exit[i] || {};
    return {
      locked: !!r.locked, wrongBook: BZ.ST.wrongBook.length,
      hint: !!document.querySelector("#mBody .sc-hint.on"),
      noRetry: !/再試一次/.test(document.getElementById("mBody").textContent)
    };
  });
  ok(wrong.locked && wrong.wrongBook === 1 && wrong.hint && wrong.noRetry,
    "出門票答錯即鎖、記入錯題本、提示自動出現（實際 " + JSON.stringify(wrong) + "）");

  /* PNG 報告卡 */
  const card = await page.evaluate(() => {
    BZ.UI.open("report");
    const wi = document.querySelector("#whoInput");
    if (wi) { wi.value = "線上驗證"; wi.dispatchEvent(new Event("input", { bubbles: true })); }
    const url = BZ.card();
    const dl = document.querySelector("#cardDl");
    return { png: url.indexOf("data:image/png") === 0, len: url.length, name: dl ? dl.getAttribute("download") : "" };
  });
  ok(card.png && card.len > 100000 && /認識比例尺_學習報告/.test(card.name),
    "線上可產生並下載 PNG 報告卡（" + card.len + " chars）");

  await page.screenshot({ path: "/tmp/scale-online-v4.png" });

  /* 兩份教材並存：舊《解比例》仍然可用 */
  const old = await browser.newPage();
  const oldErr = [];
  old.on("pageerror", e => oldErr.push(e.message));
  let oldStatus = 0, oldTitle = "";
  try {
    const r = await old.goto(OLD_URL, { waitUntil: "domcontentloaded", timeout: 30000 });
    oldStatus = r ? r.status() : 0;
    oldTitle = await old.title();
    await wait(500);
  } catch (e) { oldErr.push(String(e)); }
  ok(oldStatus === 200 && /解比例/.test(oldTitle),
    "舊《解比例》線上版仍為 HTTP 200、標題正確（" + oldStatus + " / " + oldTitle + "）");

  ok(bad.length === 0, "零 HTTP 4xx／5xx、零請求失敗" + (bad.length ? "：" + bad.join(", ") : ""));
  ok(errs.length === 0, "零 JavaScript 錯誤" + (errs.length ? "：" + errs.join(" | ") : ""));

  console.log("\n===== 線上實機 " + pass + " 通過 / " + fail + " 失敗 =====");
  await browser.close();
  if (fail) process.exit(1);
})().catch(e => { console.error(e); process.exit(1); });
