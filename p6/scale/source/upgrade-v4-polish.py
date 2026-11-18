#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v4 最後潤飾：實機目測後的文字一致性與斷行修正（幂等版）。

可重複執行：每一項若已是新值就跳過，若仍是任一舊值就升級，兩者都沒有才報錯。

1. 示範頁標題／副標仍寫「我來試試」→ 改為「參考示範」
2. 出門票 plan-bar 的 L.tip 擠出孤字「驟」→ 獨立成行
3. 分步示範 plan-bar「可。」孤字 → 縮短
4. 引入頁數學小百科被精靈氣泡遮住 → 縮短文案＋預留右側空間＋在分號處斷行
5. 引入頁 UDL 提示尾句只剩孤字「啟。」→ 濃縮為一行
6. 配對表「（不必作答）」擠迫 → 縮為「（示範）」→ 再去掉括號，消除孤字「範）」
7. 引入頁／總結卡時間預算寫死「出門票 7 分鐘」→ 改為逐題秒數實算的 5–9 分鐘層級區間
8. 品質閘由「只印字」改為真正核算各層出門票秒數、核對印出區間、檢查 20 分鐘上限
"""
import ast
import pathlib

P = pathlib.Path("/Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風/build.py")
s = P.read_text("utf-8")
ORIG = s

# (可接受的舊值清單, 新值, 標籤, 是否全域替換)
MIGRATIONS = [
    (
        ['encyc:  "數學小百科：比例尺 10 : 1 的前項大於後項，表示圖上距離是實際距離的 10 倍，屬於放大比例尺，常用於繪製鐘錶零件等細小物件的設計圖；地圖的比例尺則多為 1 : n 的縮小比例尺。",'],
        'encyc:  "數學小百科：比例尺 10 : 1 的前項大於後項，表示圖上距離是實際距離的 10 倍，屬放大比例尺，常用於繪製細小零件；地圖則多為 1 : n 的縮小比例尺。",',
        "數學小百科縮短", False,
    ),
    (
        ["'</b>；以下 '+ids.length+' 題為本層解題鏈示範，讀一遍作法即可。</div>';"],
        "'</b>；以下 '+ids.length+' 題為本層解題鏈示範。</div>';",
        "分步示範 plan-bar", False,
    ),
    (
        ["'</b>；只派 <b>'+ids.length+' 題</b>（約 '+Math.round(secs/60*10)/10+' 分鐘）。'+L.tip+'</div>';"],
        "'</b>；只派 <b>'+ids.length+' 題</b>（約 '+Math.round(secs/60*10)/10+' 分鐘）。<br>'+L.tip+'</div>';",
        "出門票 plan-bar 斷行", False,
    ),
    (
        ['      steps: ["② 分步列式 —— 我來試試","依你的層級只做對應的步驟；其餘已幫你填好作為示範。"],'],
        '      steps: ["② 分步列式 —— 參考示範","本層解題鏈示範，不必作答；今日只須完成 4 題出門票。"],',
        "分步彈窗標題", False,
    ),
    (
        ['      clinic:["③ 錯例醫院 —— 看列式找出錯誤","不必計算：先看、再估大小、最後找出錯誤。"],'],
        '      clinic:["③ 錯例醫院 —— 參考示範","本層常見錯例示範，不必作答。"],',
        "錯例彈窗標題", False,
    ),
    (
        ['+" 題（不必作答）","約 "', '+" 題（示範）","約 "'],
        '+" 題","約 "',
        "配對表用語（去括號，避免孤字「範）」）", True,
    ),
    (
        ['            steps: ["② 分步列式","參考示範：題目、答案與解題步驟（不必作答）"],'],
        '            steps: ["② 分步列式","參考示範：題目、答案與解法"],',
        "主線 ② 描述", False,
    ),
    (
        ['            clinic:["③ 錯例醫院","參考示範：看看別人錯在哪裡（不必作答）"],'],
        '            clinic:["③ 錯例醫院","參考示範：看看別人錯在哪裡"],',
        "主線 ③ 描述", False,
    ),
    (
        ["　今日只派 <b>4 題出門票</b>，四題都練同一個概念；分步列式與錯例醫院為參考示範，不必作答。"],
        "　今日只派 <b>4 題出門票</b>，四題同屬本層概念；分步與錯例為參考示範。",
        "練習頁配對說明", False,
    ),
    (
        [
            '      \'<div class="concept-box">🔎 <b>\'+esc(CFG.encyc)+\'</b></div>\'+',
            '      \'<div class="concept-box" style="padding-right:150px">🔎 <b>\'+esc(CFG.encyc)+\'</b></div>\'+',
        ],
        '      \'<div class="concept-box" style="padding-right:150px">🔎 <b>\'+esc(CFG.encyc).replace("；","；<br>")+\'</b></div>\'+',
        "小百科預留氣泡空間並在分號斷行", False,
    ),
    (
        ["'<div class=\"udl-tip\">💡 <b>UDL 提示：</b>本課設有分層——先完成 5 題診斷，系統只會派發適合你程度的 <b>4 題出門票</b>；分步列式與錯例醫院改為參考示範，不必作答。未完成診斷前，練習不會開啟。</div>'+"],
        "'<div class=\"udl-tip\">💡 <b>UDL 提示：</b>先完成 5 題診斷，系統只派適合你程度的 <b>4 題出門票</b>；分步與錯例為參考示範。未完成診斷前，練習不會開啟。</div>'+",
        "UDL 提示去孤字", False,
    ),
    (
        ["（診斷 2.5 ＋ 推演 2 ＋ 示範瀏覽 2 ＋ 出門票 7 ＋ 總結 1.5）。今日須作答 <b>9 題</b>"],
        "（診斷 2.5 ＋ 推演 2 ＋ 示範瀏覽 2 ＋ 出門票 5–9（依層級） ＋ 總結 1.5，全程約 13–17 分鐘）。今日須作答 <b>9 題</b>",
        "引入頁時間預算改為層級區間", False,
    ),
    (
        ["（診斷 2.5 ＋ 推演 2 ＋ 示範瀏覽 2 ＋ 出門票 7 ＋ 總結 1.5）。今日須作答 9 題"],
        "（診斷 2.5 ＋ 推演 2 ＋ 示範瀏覽 2 ＋ 出門票 5–9（依層級） ＋ 總結 1.5）。今日須作答 9 題",
        "總結卡時間預算改為層級區間", False,
    ),
]

applied, skipped = [], []
for olds, new, label, all_occ in MIGRATIONS:
    if new in s:
        skipped.append(label)
        continue
    hit = next((o for o in olds if o in s), None)
    if hit is None:
        raise SystemExit("❌ 錨點搵唔到（新舊值皆不存在）：" + label)
    s = s.replace(hit, new) if all_occ else s.replace(hit, new, 1)
    applied.append(label)

# 品質檢查：不得殘留舊用語
for bad in ["② 分步列式 —— 我來試試", "看列式找出錯誤", "讀一遍作法即可", "四題都練同一個概念",
            "題（不必作答）", "題（示範）", "鐘錶零件等細小物件", "本課設有分層——先完成 5 題診斷",
            "出門票 7 ＋ 總結"]:
    if bad in s:
        raise SystemExit("❌ 仍有舊用語：" + bad)

# 品質檢查：時間預算品質閘必須真正核算逐題秒數
if "時間預算核算" not in s or "_exit_secs" not in s:
    raise SystemExit("❌ 時間預算品質閘仍只是印字，沒有核算逐題秒數")

# 品質檢查：所有新值都必須在
for _, new, label, _ in MIGRATIONS:
    if new not in s:
        raise SystemExit("❌ 新值缺失：" + label)

try:
    ast.parse(s)
except SyntaxError as e:
    raise SystemExit("❌ build.py 語法錯誤：%s (line %d)" % (e.msg, e.lineno))

if s != ORIG:
    P.write_text(s, "utf-8")
print("✅ upgrade-v4-polish.py：幂等檢查完成（新套用 %d 項／已存在 %d 項）" % (len(applied), len(skipped)))
for x in applied:
    print("   • 套用：" + x)
