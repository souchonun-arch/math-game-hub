# 數學遊戲總站

波仔嘅小學數學遊戲集中地。一個網址，學生自己揀嚟玩。

- 首頁：`https://<用戶名>.github.io/math-game-hub/`
- 三年級：`/p3/`
- 六年級：`/p6/`
- 數學思維挑戰：`/challenge/`

---

## 日常更新：三種方式，揀最方便嘅

### 方法 A — 叫我幫你更新（推薦，大檔必用）

1. 新遊戲嘅 `.html` 放入對應資料夾：
   - 三年級 → `~/Desktop/ＣＤＳＪ5/26-27學年/三數學/遊戲/`
   - 六年級 → `~/Desktop/ＣＤＳＪ5/26-27學年/六數學/遊戲/`
   - 思維挑戰 → `~/Desktop/ＣＤＳＪ5/26-27學年/六數學思維/`
2. 同我講一句「更新網站」
3. 我跑：
   ```bash
   python3 scripts/build.py --dry-run   # 先睇報告
   python3 scripts/build.py             # 真正做
   git add -A && git commit -m "更新遊戲" && git push
   ```

第一次收錄一款**新**遊戲時，`build.py` 會提示你喺兩個檔案加資料：
- `data/slugs.json` — 決定網址（加咗就永久唔好改）
- `data/overrides.json` — 中文顯示名、課題、搜尋關鍵字

改完再跑一次 `build.py` 就上架。

### 方法 B — 自己開後台上傳

開 `https://<用戶名>.github.io/math-game-hub/admin/`
- 密碼：`mathgames2026`（改法見下面）
- 需要先填一次 GitHub token（存喺 sessionStorage，關分頁即消失）
- 只支援**單一自包含 HTML 檔**；有外部圖檔／js 嘅遊戲請用方法 A
- 上傳 8MB 以上會出警告，25MB 以上直接拒絕

### 方法 C — 加一個新分區（例如第時做四年級）

1. `scripts/sources.json` 嘅 `sources` 加一筆：`{ "dir": "四數學/遊戲", "section": "p4" }`
2. `data/sections.json` 加一筆分區設定（id / title / desc / icon / 顏色）
3. 複製 `p3/index.html` 做 `p4/index.html`，改 `data-section="p4"`
4. 跑 `build.py`

**唔使改任何 JavaScript。**

---

## 目錄結構

```
├── index.html            首頁（三個入口）
├── p3/ p6/ challenge/    三個分區頁（同一套渲染邏輯）
├── admin/                管理後台
├── assets/css/hub.css    全站樣式
├── assets/js/hub.js      卡片／分類／搜尋／QR
├── assets/js/qrcode.js   QR 生成器（自托管，MIT）
├── assets/js/admin.js    後台邏輯（GitHub API）
├── data/games.json       ★ 自動產生，唔好手改
├── data/open.json        ★ 開放控制（全站／分區／逐款遊戲）
├── data/slugs.json       ★ 網址代號凍結表（手改）
├── data/overrides.json   ★ 顯示名／課題／關鍵字（手改）
├── data/topics.json      課題分類次序（手改）
├── data/sections.json    分區設定（手改）
├── assets/img/*.jpg      封面圖（已壓縮，每張約 90KB）
├── assets/img/src/       封面圖原檔（2MB／張，唔上傳，只供重新壓縮）
├── games/<分區>/<slug>/index.html  守門頁（1KB，查開放狀態）
├── games/<分區>/<slug>/play.html   ★ 遊戲本體 + 依附檔
├── scripts/build.py      掃描桌面 → 產生清單 → 複製檔案
├── scripts/gate_template.html     守門頁模板
└── scripts/make_covers.py 封面圖裁水印 + 壓縮
```

---

## 🔒 開放控制：想幾時開就幾時開

### 點用

開 `/admin/` → 解鎖 → **「1. 開放控制」** → 撳掣 → 等 1–2 分鐘生效。

三層，下面嗰層可以覆寫上面嗰層：

| 層 | 作用 | 例子 |
|---|---|---|
| **全站** | 一掣開閂成個網站 | 平時閂住，上堂前撳開 |
| **分區** | 逐個年級獨立控制 | 淨開三年級、閂住六年級 |
| **逐款遊戲** | 個別遊戲獨立控制 | 全站閂，但淨開《超市大亨》畀精英組 |

判定順序：**逐款遊戲 → 分區 → 全站**。搵到第一個明確嘅 `true`／`false` 就照佢，冇就跌落下一層。讀唔到 `open.json` 一律當**開放**（寧願漏鎖，都唔可以搞到上唔到堂）。

### 鎖到幾嚴

每款遊戲真正嘅檔案係 `play.html`，而 `index.html` 只係一個 **1KB 守門頁**：

1. 學生撳卡片 → 入到守門頁
2. 守門頁讀 `data/open.json`
3. 開放 → 自動跳去 `play.html`（學生完全唔覺）
4. 未開放 → 停低顯示「🔒 老師仲未開放」+ 你可自訂嘅句子

所以**學生用你畀過嘅任何網址**（首頁、分區頁、遊戲頁、QR Code）都會被擋。
唯一漏洞：直接打 `play.html` —— 小學生唔會知，而且你隨時可以改用 GitHub Pages 全站落線。

### 手改都得

唔開後台都可以直接改 `data/open.json`：

```json
{
  "all": false,
  "sections": { "p3": true },
  "games": { "supermarket-tycoon": true },
  "message": "星期五堂上先開放"
}
```

上面嘅意思：全站關，但三年級開、加埋《超市大亨》開。

---

## 封面圖與「🔥 NEW」火焰標籤

### 封面圖點運作

每張卡片嘅封面圖檔名**就係遊戲 slug**：

```
assets/img/<slug>.jpg        例如 assets/img/supermarket-tycoon.jpg
assets/img/sec-<分區>.jpg    例如 assets/img/sec-p3.jpg
```

前端直接用 `g.id` 拼路徑，**所以加新遊戲唔使改任何資料檔**。
冇封面圖嘅遊戲（例如你透過後台上傳嘅）會自動退回「漸層 + 課題 emoji」，唔會爛版。

想換某一張封面：把新圖放入 `assets/img/src/<slug>.png`，再跑
```bash
python3 scripts/make_covers.py
```
（腳本會裁走右下角 AI 水印、縮到 800px 闊、存成 JPEG）

### 「最新」點判斷

`build.py` 會讀**來源檔嘅修改日期**，寫入 `games.json` 嘅 `updatedAt`。
`scripts/sources.json` 有個 `newDays`（預設 30）：來源檔喺 30 日內改過，卡片就自動著火 + 掛 NEW 角標，過期自動熄。

想收窄到只標最近幾款，改 `newDays` 一個數字就得：
```json
"newDays": 7
```
（7 日 → 得最近一星期改過嘅遊戲著火；想全部熄就設 0）

**個別遊戲想強制著火或熄火**，喺 `data/overrides.json` 該 slug 下面加：
```json
"supermarket-tycoon": {
  "title": "超市大亨爭霸戰 · 折扣與賺賠",
  "new": true
}
```
`true` = 永遠著火，`false` = 永遠唔著火，唔寫 = 跟 `newDays` 自動判斷。
改完跑一次 `build.py` 生效。

`addedAt`（首次收錄日）會由上一版 `games.json` 繼承，所以**永遠唔會變**，將來想做「最新上架」排序都靠得住。

## 重要原則

- **桌面原檔永遠唔會被改動**。`build.py` 只讀來源，寫入只去 repo；執行前後會做 size + mtime 快照比對，有變動即中止。
- **`data/games.json` 由腳本產生**，直接改會被下次 build 覆蓋。要改顯示資料，改 `overrides.json`。
- **slug 一經上架就唔好改**，學生可能已經收藏咗條 link。
- 網址結構固定 `games/<分區>/<slug>/`，所以日後搬去其他平台（Cloudflare Pages 等）都唔使改任何檔案。

## 改後台密碼

打開 `assets/js/admin.js`，搵 `var PASSWORD = 'mathgames2026';` 改成你嘅密碼，再 commit。
提醒：純靜態網站嘅密碼閘只係防誤觸，唔係真正安全機制；真正嘅鎖係 GitHub token。

## 常見問題

**Q：卡片冇出現／白畫面？**
直接開檔案（`file://`）會因為 CORS 載入唔到 JSON。本機測試要開伺服器：
```bash
python3 -m http.server 8000
```

**Q：上傳完見到 404？**
GitHub Pages 要 1–2 分鐘重新發佈，等一陣再試。仲有問題就去 repo 嘅 Actions／Pages 頁睇下建置狀態。

**Q：某個遊戲載入好慢？**
8MB 以上嘅遊戲喺手機 4G 會慢，卡片已有 Wi-Fi 提示。真係要瘦身就同我講，我會將 PNG 轉 WebP（只改 repo 副本，唔郁桌面原檔）。
