#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《認識比例尺｜像素風》v3 升級（冪等錨點替換）
需求：診斷 3→8 題（依難度加權計分，滿分 15，解決「大家都 100 分」）；
      每層練習 3→8 題（分步 4＋錯例 2＋出門票 2）；時間預算 12→20 分鐘。
改的是本目錄的 build.py；跑完再執行 python3 build.py 產出 HTML。
"""
import pathlib
import ast

P = pathlib.Path("/Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風/build.py")
s = P.read_text("utf-8")
ORIG = s


def rep(old, new, label, all=False):
    global s
    if old not in s:
        raise SystemExit("❌ anchor 搵唔到：" + label)
    s = s.replace(old, new) if all else s.replace(old, new, 1)


def seg_src(start, end, new, label):
    """直接替換 build.py 原始碼中 DATA = r'''...''' 內的 JS 區段"""
    global s
    a = s.find(start)
    if a < 0:
        raise SystemExit("❌ segment 起點搵唔到：" + label)
    b = s.find(end, a + len(start))
    if b < 0:
        raise SystemExit("❌ segment 終點搵唔到：" + label)
    s = s[:a] + new + "\n" + s[b:]


# ══════════════════════════════════════════════════════════════════════
# 1. 資料區：CFG / DIAG(8) / DATA(24) / PLAN(陣列) / activeIds
# ══════════════════════════════════════════════════════════════════════
NEW_DATA = r'''const CFG = {
  unit:   "六上｜比例與比例尺（重點班）",
  lesson: "第13課｜認識比例尺",
  emoji:  "🗺",
  title:  "像素製圖師的縮尺密碼",
  story:  "像素王國要繪製一張校園地圖。製圖精靈「尺尺」說：圖上的 1 格，代表真正的 25 格。只要寫出「圖上距離 : 實際距離」，就能把整座王國收進地圖裡。請你先找出這張地圖的比例尺。",
  key:    "比例尺 ＝ 圖上距離 : 實際距離（先統一單位，再化成前項為 1 的最簡整數比）",
  standard: "澳門基本學力 B-2-15：認識比例尺，並能用比例尺解決實際問題。",
  encyc:  "數學小百科：比例尺 10 : 1 的前項大於後項，表示圖上距離是實際距離的 10 倍，屬於放大比例尺，常用於繪製鐘錶零件等細小物件的設計圖；地圖的比例尺則多為 1 : n 的縮小比例尺。",
  minutes: 20,
  demo:   { map:1, real:25 },
  hero:   { t:"meaning", map:1, real:25, cap:"像素校園：圖上 1 格代表實際 25 格" },
  colors: { primary:"#E14B3C", secondary:"#2E5CA8", accent:"#F5B731", bg:"#F3EFE1" }
};

/* 分層診斷：8 題（★3／★★3／★★★2），依難度配分 1／2／3 分，滿分 15 分。
   測的是本課前置能力（比的化簡、單位換算、前項化為 1），不是本課新知。
   加權得分讓同一層級內仍能看出程度差異，不再全部擠在滿分。 */
const DIAG = [
  { s:"比的化簡", d:1, t:"化簡比 12 : 18 ＝ 2 : （　）", a:["3"], sec:25,
    exp:"12 : 18 同除以 6 → 2 : 3", src:"《澳門新思維數學》第2課 比的性質（本課前置知識）" },
  { s:"單位換算", d:1, t:"3 米 ＝ （　）厘米", a:["300"], sec:25,
    exp:"1 米 ＝ 100 厘米，3 米 ＝ 300 厘米", src:"長度單位換算（本課前置知識）" },
  { s:"單位換算", d:1, t:"1 cm ＝ （　）mm", a:["10"], sec:20,
    exp:"1 cm ＝ 10 mm", src:"長度單位換算（本課前置知識）" },
  { s:"單位換算", d:2, t:"1 km ＝ （　）厘米", a:["100000"], sec:30,
    exp:"1 km ＝ 1000 m ＝ 100 000 cm", src:"課本 p.52 附加例題 1（前置：米與千米化為厘米）" },
  { s:"前項化為 1", d:2, t:"化簡比 25 : 4000 ＝ 1 : （　）", a:["160"], sec:40,
    exp:"25 : 4000 同除以 25 → 1 : 160", src:"課本 p.52 第13課第2題附加例題 3(a)（前置化簡）" },
  { s:"單位換算", d:2, t:"7.5 dm ＝ （　）mm", a:["750"], sec:35,
    exp:"1 dm ＝ 100 mm，7.5 dm ＝ 750 mm", src:"《澳門新思維數學習作》練習13 第40題（前置換算）" },
  { s:"前項化為 1", d:3, t:"把 1.1 : 36 300 化成前項是 1 的比，即 1 : （　）", a:["33000"], sec:50,
    exp:"1.1 : 36 300 同除以 1.1 → 1 : 33 000", src:"自編補充工作紙冊 第13課 計算題 2（前置化簡）" },
  { s:"前項化為 1", d:3, t:"化簡比 4.5 : 9000 ＝ 1 : （　）", a:["2000"], sec:45,
    exp:"4.5 : 9000 同除以 4.5 → 1 : 2000", src:"課本 p.52 第13課第2題附加例題 2（前置化簡）" }
];

const DATA = {
  /* 推演三步：意義 → 統一單位 → 化簡與三種比例尺 */
  derive: [
    { s:"比例尺表示圖上距離與實際距離的比：比例尺 ＝ 圖上距離 : 實際距離。",
      k:"前項一定是圖上距離，後項一定是實際距離；兩者的順序不能對調。",
      fig:{ t:"meaning", map:1, real:25, cap:"步驟 1：比例尺的意義" },
      src:"《澳門新思維數學》第13課 教學目標 1：認識比例尺的意義" },
    { s:"計算前先把兩個距離化成相同單位；通常把實際距離換算成厘米。",
      k:"1 m ＝ 100 cm；1 km ＝ 100 000 cm；1 cm ＝ 10 mm。單位不同不能直接寫比。",
      fig:{ t:"unit", cap:"步驟 2：先統一單位" },
      src:"課本 p.52 附加例題 1（24 m 化為 2400 cm）" },
    { s:"把比化成前項為 1 的最簡整數比，即為數值比例尺；線段比例尺用一格表示固定距離。",
      k:"5 : 2400 ＝ 1 : 480；每格 1 cm 代表 50 m 即 1 : 5000；10 : 1 是放大比例尺。",
      fig:{ t:"flow", cap:"步驟 3：寫比、化簡、寫出比例尺" },
      src:"《澳門新思維數學習作》練習13 第1、40題；進度表教學目標 3、4" }
  ],
  /* 分步列式：★／★★／★★★ 各 4 題，每題附教材依據與預估秒數 */
  steps: [
    { d:1, sec:45, src:"《澳門新思維數學習作》練習13 第1題（表格 1 cm : 25 cm）",
      t:"地圖上 1 cm 代表實際 25 cm，這幅圖的比例尺是 1 : （　）",
      a:["25"], hint:"比例尺 ＝ 圖上距離 : 實際距離；單位相同時直接寫比",
      exp:"1 : 25 已是前項為 1 的最簡整數比，不必換算。",
      fig:{ t:"meaning", map:1, real:25, cap:"圖上 1 格 : 實際 25 格" },
      redo:{ t:"地圖上 3 cm 代表實際 75 cm，比例尺是 1 : （　）", a:["25"],
             exp:"3 : 75 同除以 3 → 1 : 25" } },
    { d:1, sec:60, src:"課本 p.52 第13課第2題附加例題 1（正方形水池邊長 24 米）",
      t:"正方形水池實際邊長 24 米，先把 24 米化成 （　）厘米",
      a:["2400"], hint:"1 米 ＝ 100 厘米",
      exp:"24 × 100 ＝ 2400（厘米）。",
      fig:{ t:"unit", cap:"先統一單位：米 → 厘米" },
      redo:{ t:"草地實際長 90 米，化成 （　）厘米", a:["9000"],
             exp:"90 × 100 ＝ 9000（厘米）" } },
    { d:1, sec:50, src:"《澳門新思維數學習作》練習13 第1題表格變式（更換數字）",
      t:"地圖上 3 cm 代表實際 75 cm，這幅圖的比例尺是 1 : （　）",
      a:["25"], hint:"先寫出「圖上 : 實際」，再化成前項為 1 的比",
      exp:"3 : 75 同除以 3 → 1 : 25。",
      fig:{ t:"ratio", a:3, b:75, n:25, cap:"3 : 75 化簡為 1 : 25" },
      redo:{ t:"地圖上 6 cm 代表實際 150 cm，比例尺是 1 : （　）", a:["25"],
             exp:"6 : 150 同除以 6 → 1 : 25" } },
    { d:1, sec:50, src:"《澳門新思維數學習作》練習13 第1題表格變式（更換數字）",
      t:"地圖上 2 cm 代表實際 30 cm，這幅圖的比例尺是 1 : （　）",
      a:["15"], hint:"兩個距離單位相同，直接寫比再化簡",
      exp:"2 : 30 同除以 2 → 1 : 15。",
      fig:{ t:"ratio", a:2, b:30, n:15, cap:"2 : 30 化簡為 1 : 15" },
      redo:{ t:"地圖上 4 cm 代表實際 60 cm，比例尺是 1 : （　）", a:["15"],
             exp:"4 : 60 同除以 4 → 1 : 15" } },
    { d:2, sec:90, src:"課本 p.52 第13課第2題附加例題 1（圖上 5 厘米、實際 24 米）",
      t:"水池邊長 24 米（＝ 2400 厘米），圖上邊長 5 cm，比例尺是 1 : （　）",
      a:["480"], hint:"先寫 5 : 2400，再把前後項同除以 5",
      exp:"5 : 2400 ＝ 1 : 480。",
      fig:{ t:"ratio", a:5, b:2400, n:480, cap:"5 : 2400 化簡為 1 : 480" },
      redo:{ t:"草地長 90 米（＝ 9000 厘米），圖上長 4.5 cm，比例尺是 1 : （　）",
             a:["2000"], exp:"4.5 : 9000 同除以 4.5 → 1 : 2000" } },
    { d:2, sec:100, src:"自編補充工作紙冊 第13課 計算題 2（天橋 363 米／圖上 1.1 厘米）",
      t:"天橋實際長 363 米，圖上長 1.1 cm，比例尺是 1 : （　）",
      a:["33000"], hint:"363 米 ＝ 36 300 厘米，再寫 1.1 : 36 300",
      exp:"363 m ＝ 36 300 cm；1.1 : 36 300 ＝ 1 : 33 000。",
      fig:{ t:"ratio", a:1.1, b:36300, n:33000, cap:"1.1 : 36 300 ＝ 1 : 33 000" },
      redo:{ t:"甲、乙兩地實際距離 950 千米，圖上距離 19 cm，比例尺是 1 : （　）",
             a:["5000000"], exp:"950 km ＝ 95 000 000 cm；19 : 95 000 000 ＝ 1 : 5 000 000" } },
    { d:2, sec:95, src:"課本 p.52 第13課第2題附加例題 3(b)（圖上 12 cm、實際 90 米）",
      t:"草地實際長 90 米，圖上長 12 cm，比例尺是 1 : （　）",
      a:["750"], hint:"90 米 ＝ 9000 厘米，再寫 12 : 9000",
      exp:"90 m ＝ 9000 cm；12 : 9000 ＝ 1 : 750。",
      fig:{ t:"ratio", a:12, b:9000, n:750, cap:"12 : 9000 化簡為 1 : 750" },
      redo:{ t:"跑道實際長 45 米，圖上長 15 cm，比例尺是 1 : （　）", a:["300"],
             exp:"45 m ＝ 4500 cm；15 : 4500 ＝ 1 : 300" } },
    { d:2, sec:90, src:"課本 p.52 第13課第2題附加例題 3(a)（圖上 25 cm、實際 40 米）",
      t:"大廈實際高 40 米，圖上高 25 cm，比例尺是 1 : （　）",
      a:["160"], hint:"40 米 ＝ 4000 厘米，再寫 25 : 4000",
      exp:"40 m ＝ 4000 cm；25 : 4000 ＝ 1 : 160。",
      fig:{ t:"ratio", a:25, b:4000, n:160, cap:"25 : 4000 化簡為 1 : 160" },
      redo:{ t:"大樓實際高 120 米，圖上高 30 cm，比例尺是 1 : （　）", a:["400"],
             exp:"120 m ＝ 12 000 cm；30 : 12 000 ＝ 1 : 400" } },
    { d:3, sec:110, src:"工作紙 24.png 第⑦題（線段比例尺 0 50 100 150 200 m）",
      t:"線段比例尺每格 1 cm 代表 50 m，寫成數值比例尺是 1 : （　）",
      a:["5000"], hint:"先把 50 m 化成厘米，再寫成 1 cm : ？ cm",
      exp:"50 m ＝ 5000 cm，所以 1 : 5000。",
      fig:{ t:"line", step:50, unit:"m", cap:"線段比例尺：每格 1 cm 代表 50 m" },
      redo:{ t:"線段比例尺每格 1 cm 代表 100 km，寫成數值比例尺是 1 : （　）",
             a:["10000000"], exp:"100 km ＝ 10 000 000 cm → 1 : 10 000 000" } },
    { d:3, sec:125, src:"《澳門新思維數學習作》練習13 第40題（7.5 dm 代表 15 mm）",
      t:"設計圖上 7.5 dm 代表實際 15 mm，這張設計圖的比例尺是 （　） : 1",
      a:["50"], hint:"7.5 dm ＝ 750 mm；圖上距離比實際距離大，是放大比例尺",
      exp:"7.5 dm ＝ 750 mm；750 : 15 ＝ 50 : 1（前項大於後項，屬放大比例尺）。",
      fig:{ t:"zoom", cap:"放大比例尺：圖上比實際大" },
      redo:{ t:"設計圖上 2.4 cm 代表實際 8 mm，比例尺是 （　） : 1",
             a:["3"], exp:"2.4 cm ＝ 24 mm；24 : 8 ＝ 3 : 1" } },
    { d:3, sec:115, src:"工作紙 24.png 第⑦題變式（每格代表 200 m）",
      t:"線段比例尺每格 1 cm 代表 200 m，寫成數值比例尺是 1 : （　）",
      a:["20000"], hint:"200 m ＝ 20 000 cm，再寫成 1 : n",
      exp:"200 m ＝ 20 000 cm，所以 1 : 20 000。",
      fig:{ t:"line", step:200, unit:"m", cap:"線段比例尺：每格 1 cm 代表 200 m" },
      redo:{ t:"線段比例尺每格 1 cm 代表 500 m，寫成數值比例尺是 1 : （　）", a:["50000"],
             exp:"500 m ＝ 50 000 cm → 1 : 50 000" } },
    { d:3, sec:115, src:"《澳門新思維數學習作》練習13 第42題變式（更換數字）",
      t:"設計圖上 5 cm 代表實際 2.5 mm，這張設計圖的比例尺是 （　） : 1",
      a:["20"], hint:"5 cm ＝ 50 mm；圖上距離大於實際距離，屬放大比例尺",
      exp:"5 cm ＝ 50 mm；50 : 2.5 ＝ 20 : 1。",
      fig:{ t:"zoom", cap:"放大比例尺：前項大於後項" },
      redo:{ t:"設計圖上 4 cm 代表實際 5 mm，比例尺是 （　） : 1", a:["8"],
             exp:"4 cm ＝ 40 mm；40 : 5 ＝ 8 : 1" } }
  ],
  /* 錯例醫院：★／★★／★★★ 各 2 題；size 為病人所寫後項相對正確答案偏大或偏小 */
  clinic: [
    { d:1, size:"small", sec:55,
      src:"《澳門新思維數學》第13課 教學目標 1（比例尺的意義）",
      w:"「圖上 1 cm 代表實際 25 cm」，小明寫成比例尺 25 : 1",
      q:"這個寫法錯在哪裡？",
      opts:["前後項對調：正確為「圖上 : 實際 ＝ 1 : 25」",
            "應該把兩個距離相加", "比例尺一定要寫成分數", "這個寫法完全正確"],
      ans:0, exp:"比例尺的前項是圖上距離、後項是實際距離，順序不能對調；正確為 1 : 25。",
      redo:{ t:"圖上 1 cm 代表實際 25 cm，正確的比例尺是 1 : （　）", a:["25"],
             exp:"1 : 25，前項是圖上距離。" } },
    { d:1, size:"small", sec:55,
      src:"《澳門新思維數學習作》練習13 第1題表格變式（5 cm : 125 cm）",
      w:"「圖上 5 cm 代表實際 125 cm」，小美寫成比例尺 125 : 5",
      q:"這個寫法錯在哪裡？",
      opts:["沒有化成前項為 1 的最簡整數比，正確為 1 : 25",
            "只需把前後項對調", "應該把兩個距離相加", "這個寫法完全正確"],
      ans:0, exp:"5 : 125 同除以 5 → 1 : 25；比例尺要寫成前項為 1 的最簡整數比。",
      redo:{ t:"圖上 5 cm 代表實際 125 cm，正確的比例尺是 1 : （　）", a:["25"],
             exp:"5 : 125 ＝ 1 : 25" } },
    { d:2, size:"small", sec:65, src:"課本 p.52 第13課第2題附加例題 1",
      w:"水池實際邊長 24 m、圖上邊長 5 cm，小欣列式 5 : 24 ＝ 1 : 4.8",
      q:"這個列式錯在哪裡？",
      opts:["沒有先統一單位：24 m 應化成 2400 cm，正確為 1 : 480",
            "5 不可以放在前項", "應該把 5 和 24 相加", "這個列式完全正確"],
      ans:0, exp:"單位不同不能直接相比；24 m ＝ 2400 cm，5 : 2400 ＝ 1 : 480。",
      redo:{ t:"水池實際邊長 24 m、圖上 5 cm，正確的比例尺是 1 : （　）", a:["480"],
             exp:"5 : 2400 ＝ 1 : 480" } },
    { d:2, size:"small", sec:75,
      src:"自編補充工作紙冊 第13課 計算題 2（363 米／1.1 厘米）",
      w:"天橋實際長 363 m、圖上長 1.1 cm，小俊寫成 1.1 : 363 ＝ 1 : 330",
      q:"這個列式錯在哪裡？",
      opts:["單位未統一且化簡有誤；363 m ＝ 36 300 cm，正確為 1 : 33 000",
            "1.1 不可以是小數", "比例尺後項要小於 1000", "這個列式完全正確"],
      ans:0, exp:"363 m ＝ 36 300 cm；1.1 : 36 300 ＝ 1 : 33 000，不是 1 : 330。",
      redo:{ t:"天橋 363 m、圖上 1.1 cm，正確的比例尺是 1 : （　）", a:["33000"],
             exp:"1.1 : 36 300 ＝ 1 : 33 000" } },
    { d:3, size:"small", sec:80,
      src:"工作紙 24.png 第⑦題（0 50 100 150 200 m）",
      w:"線段比例尺每格 1 cm 代表 50 m，小琪寫成數值比例尺 1 : 50",
      q:"這個寫法錯在哪裡？",
      opts:["沒有把 50 m 化成厘米：50 m ＝ 5000 cm，正確為 1 : 5000",
            "線段比例尺不能換成數值比例尺", "應該寫成 50 : 1", "這個寫法完全正確"],
      ans:0, exp:"1 cm : 50 m ＝ 1 cm : 5000 cm ＝ 1 : 5000；兩個距離必須使用相同單位。",
      redo:{ t:"每格 1 cm 代表 50 m，正確的數值比例尺是 1 : （　）", a:["5000"],
             exp:"50 m ＝ 5000 cm → 1 : 5000" } },
    { d:3, size:"big", sec:85,
      src:"《澳門新思維數學習作》練習13 第40題；進度表教學目標 4（認識 10 : 1）",
      w:"設計圖上 7.5 dm 代表實際 15 mm，小志寫成比例尺 1 : 50",
      q:"這個寫法錯在哪裡？",
      opts:["弄錯放大與縮小：7.5 dm ＝ 750 mm，正確為 50 : 1",
            "7.5 不可以是小數", "設計圖不可能有比例尺", "這個寫法完全正確"],
      ans:0, exp:"7.5 dm ＝ 750 mm；750 : 15 ＝ 50 : 1。前項大於後項，表示圖上比實際大，屬放大比例尺。",
      redo:{ t:"設計圖上 7.5 dm 代表實際 15 mm，正確的比例尺是 （　） : 1", a:["50"],
             exp:"750 : 15 ＝ 50 : 1" } }
  ],
  /* 出門票：★／★★／★★★ 各 2 題，與本層主題一致 */
  exit: [
    { d:1, sec:70, src:"《澳門新思維數學習作》練習13 第1題（表格 5 cm : 125 cm）",
      t:"地圖上 5 cm 代表實際 125 cm，這幅地圖的比例尺是 1 : （　）", a:["25"],
      exp:"單位相同：5 : 125 同除以 5 → 1 : 25。",
      redo:{ t:"地圖上 2 cm 代表實際 50 cm，比例尺是 1 : （　）", a:["25"],
             exp:"2 : 50 ＝ 1 : 25" } },
    { d:1, sec:70, src:"《澳門新思維數學習作》練習13 第1題表格變式（更換數字）",
      t:"地圖上 2 cm 代表實際 40 cm，這幅地圖的比例尺是 1 : （　）", a:["20"],
      exp:"2 : 40 同除以 2 → 1 : 20。",
      redo:{ t:"地圖上 3 cm 代表實際 60 cm，比例尺是 1 : （　）", a:["20"],
             exp:"3 : 60 ＝ 1 : 20" } },
    { d:2, sec:105, src:"課本 p.52 第13課第2題附加例題 2（草地 90 米／圖上 4.5 厘米）",
      t:"草地實際長 90 米，圖上量得 4.5 cm，這幅圖的比例尺是 1 : （　）", a:["2000"],
      exp:"90 m ＝ 9000 cm；4.5 : 9000 ＝ 1 : 2000。",
      redo:{ t:"大廈高 40 米，圖上高 25 cm，比例尺是 1 : （　）", a:["160"],
             exp:"40 m ＝ 4000 cm；25 : 4000 ＝ 1 : 160" } },
    { d:2, sec:120, src:"自編補充工作紙冊 第13課 計算題 1（950 km／19 cm）",
      t:"甲、乙兩地實際距離 950 千米，圖上距離 19 cm，比例尺是 1 : （　）", a:["5000000"],
      exp:"950 km ＝ 95 000 000 cm；19 : 95 000 000 ＝ 1 : 5 000 000。",
      redo:{ t:"兩地實際距離 380 千米，圖上距離 19 cm，比例尺是 1 : （　）", a:["2000000"],
             exp:"380 km ＝ 38 000 000 cm；19 : 38 000 000 ＝ 1 : 2 000 000" } },
    { d:3, sec:135, src:"《澳門新思維數學習作》練習13 第42題（零件邊長 8 mm／圖上 2.4 cm）",
      t:"零件實際邊長 8 mm，設計圖上邊長 2.4 cm，這幅設計圖的比例尺是 （　） : 1", a:["3"],
      exp:"2.4 cm ＝ 24 mm；24 : 8 ＝ 3 : 1，屬放大比例尺。",
      redo:{ t:"設計圖上 5 cm 代表實際 2.5 mm，比例尺是 （　） : 1", a:["20"],
             exp:"5 cm ＝ 50 mm；50 : 2.5 ＝ 20 : 1" } },
    { d:3, sec:135, src:"工作紙 24.png 第⑧題（0 100 200 300 400 km）",
      t:"線段比例尺每格 1 cm 代表 100 km，寫成數值比例尺是 1 : （　）", a:["10000000"],
      exp:"100 km ＝ 10 000 000 cm，所以 1 : 10 000 000。",
      redo:{ t:"線段比例尺每格 1 cm 代表 250 km，寫成數值比例尺是 1 : （　）", a:["25000000"],
             exp:"250 km ＝ 25 000 000 cm → 1 : 25 000 000" } }
  ]
};

/* ═══ 本層主題鏈 ═══
   每層只派 8 題：分步 4 題＋錯例 2 題＋出門票 2 題，全部為本層難度、同一概念主題。
   其餘 16 題收進「解題鏈一覽」，僅供參考，不必作答。 */
const PLAN = {
  1:{ topic:"比例尺的意義：圖上距離 : 實際距離", steps:[0,1,2,3], clinic:[0,1], exit:[0,1],
      focus:"辨認前項是圖上距離、後項是實際距離；單位相同時直接化成前項為 1 的比" },
  2:{ topic:"先統一單位，再求比例尺", steps:[4,5,6,7], clinic:[2,3], exit:[2,3],
      focus:"把米或千米化成厘米，寫出「圖上 : 實際」並化簡為 1 : n" },
  3:{ topic:"線段比例尺與放大比例尺", steps:[8,9,10,11], clinic:[4,5], exit:[4,5],
      focus:"由線段比例尺讀出每格代表的距離並換算；辨認 10 : 1 放大比例尺" }
};
function planOf(){ return PLAN[lv()] || PLAN[2]; }
function activeIds(stage){
  const arr = stage==="steps"?DATA.steps : stage==="clinic"?DATA.clinic
            : stage==="exit"?DATA.exit : [];
  if(ST.all) return arr.map(function(_,i){return i;});
  const P=planOf();
  const picks = stage==="steps"?P.steps : stage==="clinic"?P.clinic : P.exit;
  return picks.slice();
}
function statPlan(stage){ return stat(stage, DATA[stage], activeIds(stage)); }
'''

seg_src("const CFG = {", "/* 徽章 */", NEW_DATA, "資料區 v3")

# 徽章說明
rep('d:"完成 3 題分層診斷"', 'd:"完成 8 題分層診斷"', "徽章 diag 說明")

# ══════════════════════════════════════════════════════════════════════
# 2. 新增 buildDiag v3：8 題、難度配分、加權分層（插在「15. 診斷完成」之前）
# ══════════════════════════════════════════════════════════════════════
NEW_DIAG_SECTION = r"""# ══════════════════════════════════════════════════════════════════════
# 14b. 診斷 v3：8 題、依難度配分、加權精準分層
# ══════════════════════════════════════════════════════════════════════
seg("function buildDiag(){", "/* ---------- 完成後：檢查係咪彈總結 ---------- */", r'''function buildDiag(){
  const box=document.createElement("div");
  box.innerHTML='<p class="sc-intro">🧭 先完成 <b>8 題分層診斷</b>，讓系統知道你的起點。'+
    '題目依難度配分：<b>★ 題 1 分、★★ 題 2 分、★★★ 題 3 分，滿分 15 分</b>。'+
    '這部分不計入練習成績、不提供提示；遇到不會的題目照樣填寫即可，純粹用來配對適合你的題目。</p>';
  DIAG.forEach(function(q,i){
    const r=ST.diag["q"+i]||{}; ST.diag["q"+i]=r;
    const row=document.createElement("div");
    row.className="sc-item"+(r.done?" sc-done":"");
    row.innerHTML='<div class="sc-q"><span class="sc-no">'+(i+1)+'</span>'+
      '<span class="sc-lv">'+esc(q.s)+'　'+stars(q.d||1)+'　'+(q.d||1)+' 分</span>'+
      '<span class="sc-qtext">'+q.t.replace(/（　）/g,'<input class="sc-in" type="text" inputmode="decimal">')+'</span>'+
      (q.sec?'<span class="sc-sec">⏱ 約 '+q.sec+' 秒</span>':'')+'</div>'+
      (q.src?'<div class="sc-src">📖 教材依據：'+esc(q.src)+'</div>':'')+
      '<div class="sc-btns"><button class="btn btn-primary btn-sm" data-a="ck">✓ 檢查</button></div>'+
      '<div class="sc-fb" id="dfb'+i+'"></div>';
    const inp=row.querySelector(".sc-in"), fb=row.querySelector(".sc-fb");
    row.querySelector('[data-a="ck"]').onclick=function(){
      if(r.done) return;
      if(norm(inp.value)===norm(q.a[0])){
        r.done=true; r.ok=true; fb.className="sc-fb sc-ok"; fb.innerHTML="✅ 正確！"+esc(q.exp||"");
        inp.disabled=true; row.classList.add("sc-done"); sndOk(); addXp(5); save();
      } else { fb.className="sc-fb sc-bad"; fb.innerHTML="❌ 答案不正確，請重新檢查。"; sndNo(); save(); }
    };
    box.appendChild(row);
  });
  const res=document.createElement("div"); res.id="diagRes"; box.appendChild(res);
  const bb=document.createElement("div"); bb.className="sc-btns"; bb.style.justifyContent="center";
  bb.innerHTML='<button class="btn btn-secondary" data-a="fin">✅ 完成診斷</button>';
  box.appendChild(bb);
  bb.querySelector('[data-a="fin"]').onclick=function(){
    let score=0, right=0, baseOk=0;
    const max=DIAG.reduce(function(s,q){ return s+(q.d||1); },0);
    DIAG.forEach(function(q,i){
      const r=ST.diag["q"+i];
      if(r&&r.ok){ score+=(q.d||1); right++; if((q.d||1)===1) baseOk++; }
    });
    /* 加權得分＋基礎題門檻：基礎題至少對 2 題，才允許進入較高層級 */
    const baseReady = baseOk>=2;
    let L2 = 1;
    if(score>=11 && baseReady) L2=3;
    else if(score>=6 && baseReady) L2=2;
    else L2=1;
    ST.diag.done=true; ST.diag.score=score; ST.diag.max=max;
    ST.diag.right=right; ST.diag.baseOk=baseOk; ST.diag.level=L2;
    try{ localStorage.setItem(LKEY, JSON.stringify({level:L2,score:score,max:max,right:right,ts:Date.now()})); }catch(e){}
    save();
    const Li=LV[L2];
    document.getElementById("diagRes").innerHTML=
      '<div class="sc-plan-bar" style="font-size:16px">🎯 你是 <b>'+Li.s+' '+Li.n+'</b>　'+
      '（診斷得分 <b>'+score+' / '+max+' 分</b>；答對 '+right+' / '+DIAG.length+' 題）<br>'+Li.tip+
      '<br><span class="sc-mute">8 題依難度配分，得分越接近滿分，代表已具備越多本課前置能力；同一層級內仍可從得分看出差異。</span></div>';
    toast("🎯 分層完成：" + Li.s + " " + Li.n);
    setTimeout(()=>go("explore"), 1400);
  };
  return box;
}

''', "buildDiag v3")

"""

rep("# 15. 診斷完成：送徽章", NEW_DIAG_SECTION + "# 15. 診斷完成：送徽章", "插入 buildDiag v3 區段")

# ══════════════════════════════════════════════════════════════════════
# 3. 狀態、閘門、標題、文案
# ══════════════════════════════════════════════════════════════════════
rep('<div id="pixBuddySay">尺尺：請先完成 3 題分層診斷。</div>',
    '<div id="pixBuddySay">尺尺：請先完成 8 題分層診斷。</div>',
    "初始精靈氣泡")

rep('if role_hits or "尺尺：請先完成 3 題分層診斷。" not in html:',
    'if role_hits or "尺尺：請先完成 8 題分層診斷。" not in html:',
    "品質閘角色錨點")

rep('"尺尺：請先完成 3 題分層診斷。" in html and',
    '"尺尺：請先完成 8 題分層診斷。" in html and',
    "MECH 角色錨點")

rep("return { diag:{done:false,score:0,level:0}, derive:{}",
    "return { diag:{done:false,score:0,max:15,right:0,baseOk:0,level:0}, derive:{}",
    "fresh() diag 狀態")

rep('toast("🧭 請先完成 3 題分層診斷，練習才會匹配你的層級");',
    'toast("🧭 請先完成 8 題分層診斷，練習才會匹配你的層級");',
    "分層閘門提示", all=True)

rep('diag:  ["🧭 分層診斷 —— 3 題定程度","答對題數決定你做哪一個層次的題目。"],',
    'diag:  ["🧭 分層診斷 —— 8 題定程度","依難度配分 1／2／3 分，滿分 15 分；加權得分決定你的層級。"],',
    "診斷彈窗標題")

rep('exit:  ["④ 出門票 —— 今日驗收","完成這題就會出現「📋 今日總結」。"]',
    'exit:  ["④ 出門票 —— 今日驗收","完成本關就會出現「📋 今日總結」。"]',
    "出門票標題")

rep("ST.diag={done:false,score:0,level:0,q0:{},q1:{},q2:{}};",
    'ST.diag={done:false,score:0,max:15,right:0,baseOk:0,level:0}; DIAG.forEach(function(_,i){ ST.diag["q"+i]={}; });',
    "老師重做診斷")

# 引入頁
rep("先完成 3 題診斷，系統只會派發適合你程度的 <b>3 題練習</b>（分步、錯例、出門票各 1 題）",
    "先完成 8 題診斷，系統只會派發適合你程度的 <b>8 題練習</b>（分步 4 題、錯例 2 題、出門票 2 題）",
    "引入頁 UDL 提示")

rep("⏱ <b>時間預算：約 '+CFG.minutes+' 分鐘</b>　（診斷 2.5 ＋ 推演 2 ＋ 本層練習 3 ＋ 錯例 1.5 ＋ 出門票 1.5 ＋ 總結 1.5）。今日須作答 <b>6 題</b>（診斷 3 ＋ 本層練習 3）",
    "⏱ <b>時間預算：約 '+CFG.minutes+' 分鐘</b>　（診斷 5 ＋ 推演 2 ＋ 分步 5 ＋ 錯例 2.5 ＋ 出門票 4 ＋ 總結 1.5）。今日須作答 <b>16 題</b>（診斷 8 ＋ 本層練習 8）",
    "引入頁時間預算")

rep("🧭 第一步：做 3 題分層診斷", "🧭 第一步：做 8 題分層診斷", "引入頁診斷按鈕")

# 練習頁
rep("今日只派 <b>3 題</b>（分步 1 ＋ 錯例 1 ＋ 出門票 1），三題都練同一個概念",
    "今日只派 <b>8 題</b>（分步 4 ＋ 錯例 2 ＋ 出門票 2），八題都練同一個概念",
    "練習頁配對說明")

rep('"③ 錯例醫院",cIds.length+" 題","本層第 "+cIds.map(function(i){return i+1;}).join("、")+" 題","約 1.5 分鐘"',
    '"③ 錯例醫院",cIds.length+" 題","本層第 "+cIds.map(function(i){return i+1;}).join("、")+" 題","約 "+secOf(DATA.clinic,cIds)+" 分鐘"',
    "練習頁錯例時間動態化")

# 總結卡
rep("⏱ 本課時間預算約 '+CFG.minutes+' 分鐘（診斷 2.5 ＋ 推演 2 ＋ 本層練習 3 ＋ 錯例 1.5 ＋ 出門票 1.5 ＋ 總結 1.5）。今日須作答 6 題。",
    "⏱ 本課時間預算約 '+CFG.minutes+' 分鐘（診斷 5 ＋ 推演 2 ＋ 分步 5 ＋ 錯例 2.5 ＋ 出門票 4 ＋ 總結 1.5）。今日須作答 16 題。",
    "總結卡時間預算")

# 學生報告頁
rep("今日只派 3 題練習。", "今日只派 8 題練習。", "報告頁題數")

rep("'<div class=\"sum-box\"><div class=\"k\">層級</div><div class=\"v\" style=\"font-size:19px\">'+L.s+'</div></div>'+",
    "'<div class=\"sum-box\"><div class=\"k\">層級</div><div class=\"v\" style=\"font-size:19px\">'+L.s+'</div></div>'+\n" +
    "    '<div class=\"sum-box\"><div class=\"k\">診斷得分</div><div class=\"v\">'+(ST.diag.score||0)+'<small>/'+(ST.diag.max||15)+'</small></div></div>'+",
    "報告頁新增診斷得分格")

# ══════════════════════════════════════════════════════════════════════
# 4. PNG 報告卡
# ══════════════════════════════════════════════════════════════════════
rep('cardText(ctx,"產生日期："+cardDate()+"　｜　課題："+CFG.lesson,78,238,14,"#6B5000","left",true);',
    'cardText(ctx,"產生日期："+cardDate()+"　｜　課題："+CFG.lesson+"　｜　診斷 "+(ST.diag.score||0)+" / "+(ST.diag.max||15)+" 分",78,238,14,"#6B5000","left",true);',
    "報告卡顯示診斷得分")

rep('cardText(ctx,"今日須作答 6 題（診斷 3 ＋ 本層練習 3）　｜　時間預算 "+CFG.minutes+" 分鐘",78,y+27,16,"#1B6B42");',
    'cardText(ctx,"今日須作答 16 題（診斷 8 ＋ 本層練習 8）　｜　時間預算 "+CFG.minutes+" 分鐘",78,y+27,16,"#1B6B42");',
    "報告卡題數")

OLD_PAIR = '''    sec(y,"四、本層配對（今日只做 3 題）");
    const cr=ST.clinic["c"+Pl.clinic]||{};
    [
      ["② 分步列式","第 "+(Pl.steps+1)+" 題",s1.done?"已完成":(s1.wrong?"已作答（錯）":"未作答")],
      ["③ 錯例醫院","第 "+(Pl.clinic+1)+" 題",cr.done?"已完成":(cr.locked?"已作答（錯）":"未作答")],
      ["④ 出門票","第 "+(Pl.exit+1)+" 題",s2.done?"已完成":(s2.wrong?"已作答（錯）":"未作答")]
    ].forEach(function(r,i){'''
NEW_PAIR = '''    sec(y,"四、本層配對（今日只做 8 題）");
    const cs=statPlan("clinic");
    const listNo=function(a){ return a.map(function(i){return i+1;}).join("、"); };
    [
      ["② 分步列式","第 "+listNo(Pl.steps)+" 題",s1.done+" / "+s1.total+" 已完成"],
      ["③ 錯例醫院","第 "+listNo(Pl.clinic)+" 題",cs.done+" / "+cs.total+" 已完成"],
      ["④ 出門票","第 "+listNo(Pl.exit)+" 題",s2.done+" / "+s2.total+" 已完成"]
    ].forEach(function(r,i){'''
rep(OLD_PAIR, NEW_PAIR, "報告卡本層配對表")

# ══════════════════════════════════════════════════════════════════════
# 5. 品質閘
# ══════════════════════════════════════════════════════════════════════
rep('if DATA.count("src:") < 20:', 'if DATA.count("src:") < 35:', "品質閘 src 數量")
rep('if DATA.count("sec:") < 17:', 'if DATA.count("sec:") < 32:', "品質閘 sec 數量")

rep('print("✅ 題庫：診斷 3 題／分步 6 題／錯例 5 題／出門票 3 題；每層只派 3 題；時間預算 12 分鐘")',
    'print("✅ 題庫：診斷 8 題（加權滿分 15）／分步 12 題／錯例 6 題／出門票 6 題；每層只派 8 題；時間預算 20 分鐘")',
    "品質閘輸出文案")

rep('MECH = [\n    ("角色與一次作答制用語一致（尺尺／錯題重練）",',
    '''MECH = [
    ("診斷 8 題加權分層（滿分 15、基礎題門檻）",
     "const DIAG = [" in html and "ST.diag.max=max" in html and
     "score>=11 && baseReady" in html and "score>=6 && baseReady" in html and
     "baseOk>=2" in html),
    ("每層 8 題練習（分步 4／錯例 2／出門票 2）",
     "steps:[0,1,2,3]" in html and "steps:[4,5,6,7]" in html and
     "steps:[8,9,10,11]" in html and "exit:[4,5]" in html and
     "clinic:[4,5]" in html and "return picks.slice();" in html),
    ("角色與一次作答制用語一致（尺尺／錯題重練）",''',
    "MECH 新增 v3 兩項")

# ══════════════════════════════════════════════════════════════════════
# 6. 檢查與寫回
# ══════════════════════════════════════════════════════════════════════
ast.parse(s)                       # Python 語法
if s == ORIG:
    raise SystemExit("❌ 沒有任何改動，請檢查錨點")
for bad in ["分鐘（診斷 2.5", "只派 <b>3 題</b>", "做 3 題分層診斷",
            'd:"完成 3 題分層診斷"', "先完成 3 題診斷", "3 題定程度",
            "今日須作答 6 題", "只派 3 題練習", "請先完成 3 題分層診斷"]:
    if bad in s:
        raise SystemExit("❌ 仍有舊題數文案：" + bad)
P.write_text(s, "utf-8")
print("✅ build.py 已升級為 v3：診斷 8 題加權（滿分 15）／每層 8 題／20 分鐘")
print("   改動字元數：%d → %d" % (len(ORIG), len(s)))
