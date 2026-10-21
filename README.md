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
├── data/slugs.json       ★ 網址代號凍結表（手改）
├── data/overrides.json   ★ 顯示名／課題／關鍵字（手改）
├── data/topics.json      課題分類次序（手改）
├── data/sections.json    分區設定（手改）
├── games/<分區>/<slug>/  遊戲本體 + 依附檔
└── scripts/build.py      掃描桌面 → 產生清單 → 複製檔案
```

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
