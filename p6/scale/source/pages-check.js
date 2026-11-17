/* 模擬 GitHub Pages：以 HTTP 協定載入上傳包，驗證全班使用情境（第13課） */
const puppeteer = require("puppeteer");
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = "/Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風/github-pages";
const MIME = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
               ".png": "image/png", ".md": "text/markdown; charset=utf-8" };
const wait = ms => new Promise(r => setTimeout(r, ms));

const server = http.createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split("?")[0]).replace(/^\/+/, "") || "index.html";
  const file = path.join(ROOT, rel);
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end("404"); return;
  }
  res.writeHead(200, { "Content-Type": MIME[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, "127.0.0.1", r));
  const PORT = server.address().port;
  const URL = "http://127.0.0.1:" + PORT + "/index.html?sharecode=TEST";
  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true, args: ["--no-sandbox", "--disable-gpu", "--font-render-hinting=none"]
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 900 });
  const errs = [], reqFail = [];
  page.on("pageerror", e => errs.push("pageerror: " + e.message));
  page.on("console", m => { if (m.type() === "error") errs.push("console: " + m.text()); });
  page.on("requestfailed", r => reqFail.push(r.url() + " → " + r.failure().errorText));
  page.on("response", r => { if (r.status() >= 400) reqFail.push(r.url() + " → HTTP " + r.status()); });

  let pass = 0, fail = 0;
  const ok = (cond, label) => { cond ? pass++ : fail++; console.log((cond ? "  ✓ " : "  ✗ ") + label); };

  console.log("【模擬 GitHub Pages｜認識比例尺 第13課】" + URL + "\n");
  await page.goto(URL, { waitUntil: "networkidle0" });
  await wait(600);

  const base = await page.evaluate(() => ({
    title: document.title,
    hasBZ: typeof window.BZ === "object",
    storage: (() => { try { localStorage.setItem("__t", "1"); const v = localStorage.getItem("__t"); localStorage.removeItem("__t"); return v === "1"; } catch (e) { return false; } })(),
    qrAbs: typeof assetUrl === "function" ? assetUrl("qrcode.min.js") : "",
    canvas: !!document.createElement("canvas").getContext("2d"),
    extScripts: Array.from(document.querySelectorAll("script[src],link[href]"))
      .map(n => n.src || n.href).filter(u => !u.startsWith("data:")),
    lesson: typeof CFG !== "undefined" ? CFG.lesson : "",
    key: typeof CFG !== "undefined" ? CFG.key : "",
    buddy: (document.getElementById("pixBuddySay") || {}).textContent || "",
    legacy: /比比|再試一次|再接再厲/.test(document.documentElement.innerHTML),
    figTypes: ["meaning", "unit", "ratio", "line", "zoom", "flow"]
      .map(t => ({ t: t, n: (FIG.draw({ t: t }, { stage: 0 }).match(/<(rect|text|path)/g) || []).length }))
  }));

  console.log("【1】HTTP 環境基本載入");
  ok(/認識比例尺/.test(base.title), "頁面標題正確：" + base.title);
  ok(base.lesson === "第13課｜認識比例尺", "課題為第13課「認識比例尺」");
  ok(/比例尺 ＝ 圖上距離 : 實際距離/.test(base.key), "本課核心定義正確");
  ok(/^尺尺：/.test(base.buddy) && !base.legacy,
    "線上版精靈統一署名「尺尺」，且無舊角色或重試原題提示");
  ok(base.hasBZ, "教材引擎 BZ 正常掛載");
  ok(base.storage, "localStorage 在 HTTP 協定下可讀寫（學生進度可保存）");
  ok(base.canvas, "Canvas 2D 可用（報告卡 PNG 可產生）");
  ok(base.extScripts.length === 0, "首頁沒有任何外部 script／link 連線（零外連）");
  ok(/^http:\/\/127\.0\.0\.1:.*qrcode\.min\.js\?sharecode=TEST$/.test(base.qrAbs),
    "QR 依附檔解析為絕對 URL 且沿用 sharecode：" + base.qrAbs);
  ok(base.figTypes.every(f => f.n >= 6), "六種像素圖解在真實瀏覽器皆可繪製：" +
    base.figTypes.map(f => f.t + "=" + f.n).join("、"));

  const qrRes = await page.evaluate(async u => {
    try { const r = await fetch(u); return { status: r.status, len: (await r.text()).length }; }
    catch (e) { return { status: 0, len: 0, err: String(e) }; }
  }, base.qrAbs);
  ok(qrRes.status === 200 && qrRes.len > 5000, "qrcode.min.js 可從網站根目錄載入（HTTP " + qrRes.status + "，" + qrRes.len + " bytes）");

  console.log("\n【2】全班使用流程");
  await page.evaluate(() => {
    BZ.UI.open("diag");
    const ans = BZ.DIAG.map(q => q.a[0]);
    document.querySelectorAll("#mBody .sc-item").forEach((it, i) => {
      it.querySelector(".sc-in").value = ans[i];
      it.querySelector('[data-a="ck"]').click();
    });
    const fin = document.querySelector('#mBody [data-a="fin"]');
    if (fin) fin.click();
  });
  await wait(1500);
  const lv = await page.evaluate(() => BZ.ST.diag.level);
  ok(lv === 3, "8 題診斷完成並分層（本次 ★★★）");
  const dg = await page.evaluate(() => ({ score: BZ.ST.diag.score, max: BZ.ST.diag.max,
                                           right: BZ.ST.diag.right, n: BZ.DIAG.length }));
  ok(dg.n === 8 && dg.score === 15 && dg.max === 15 && dg.right === 8,
    "加權分層：8 題全對得 15 / 15 分（不再只有「全對／非全對」）");
  await page.evaluate(() => BZ.go("practice"));
  await wait(300);
  ok(await page.evaluate(() =>
    document.querySelectorAll(".match-grid .match-box").length === 4 &&
    /今日只派 8 題/.test(document.body.textContent)), "練習頁顯示本層配對表（4 格、今日只派 8 題）");
  await page.evaluate(() => BZ.UI.open("steps"));
  await wait(250);
  ok(await page.evaluate(() => !!document.querySelector("#mBody .sc-item .sc-src") &&
    /教材依據/.test(document.getElementById("mBody").textContent)), "HTTP 環境下逐題教材依據正常顯示");
  ok(await page.evaluate(() => document.querySelectorAll("#mBody .sc-item .figsvg").length === 4),
    "HTTP 環境下本層 4 題分步像素圖解皆正常顯示");

  console.log("\n【3】學生報告與 PNG 圖片");
  await page.evaluate(() => BZ.UI.open("report"));
  await wait(300);
  ok(await page.evaluate(() => /我的學習報告/.test(document.getElementById("mTitle").textContent)), "學生可直接開啟「我的學習報告」");
  const png = await page.evaluate(() => {
    const b = document.querySelector('#cardSlot [data-a="card"]') || document.querySelector('[data-a="card"]');
    if (!b) return { ok: false, why: "找不到產生圖片按鈕" };
    b.click();
    const img = document.querySelector("#cardSlot img");
    return { ok: !!(img && img.src.slice(0, 22) === "data:image/png;base64,"),
             len: img ? img.src.length : 0,
             download: (() => { const a = document.querySelector("#cardDl");
               return !!(a && a.getAttribute("download") && a.href.slice(0, 22) === "data:image/png;base64,"); })() };
  });
  ok(png.ok, "點選後產生 PNG 報告卡（data URL " + png.len + " chars）" + (png.why || ""));
  ok(png.download, "提供「下載 PNG」按鈕供學生上傳給老師");

  console.log("\n【4】教材依據面板與章節邊界");
  await page.evaluate(() => BZ.UI.open("sources"));
  await wait(250);
  ok(await page.evaluate(() => /教材依據一覽/.test(document.getElementById("mBody").textContent) &&
    document.querySelectorAll("#mBody table tr").length === 25), "老師可開啟逐題教材依據對照表（25 列）");
  ok(await page.evaluate(() => !/正比例|反比例|體積|求實際距離|求圖上距離|第14課/.test(document.body.textContent)),
    "全班版沒有混入後續章節概念");

  console.log("\n【5】錯誤與資源");
  ok(reqFail.length === 0, "沒有任何 404／載入失敗" + (reqFail.length ? "：" + reqFail.join("；") : ""));
  ok(errs.length === 0, "零 JavaScript 錯誤" + (errs.length ? "：" + errs.join("；") : ""));

  console.log("\n===== " + pass + " 通過 / " + fail + " 失敗 =====\n");
  await browser.close();
  server.close();
  if (fail) process.exit(1);
})().catch(e => { console.error(e); server.close(); process.exit(1); });
