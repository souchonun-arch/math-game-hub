#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《認識比例尺》v4 冪等升級腳本
改動：分層診斷 8→5 題（滿分 15→9、不可重做、答錯不補答）
      每層由 8 題（分步4/錯例2/出門票2）改為只派 4 題出門票
      分步列式與錯例醫院改為「參考示範、不必作答」
      總作答 16→9 題；時間預算 20→15 分鐘
只改 build.py 的原始碼；重跑安全（錨點找不到會即時中止）。
"""
import pathlib, ast, sys

P = pathlib.Path("/Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風/build.py")
s = P.read_text("utf-8")
ORIG = s


def rep(old, new, label, count=1):
    global s
    if old not in s:
        raise SystemExit("❌ 錨點搵唔到：" + label)
    if s.count(old) < count:
        raise SystemExit("❌ 錨點數量不足：%s（%d < %d）" % (label, s.count(old), count))
    s = s.replace(old, new, count)


def repa(old, new, label):
    global s
    if old not in s:
        raise SystemExit("❌ 全域錨點搵唔到：" + label)
    s = s.replace(old, new)


def seg(start, end, new, label):
    global s
    a = s.find(start)
    if a < 0:
        raise SystemExit("❌ 段起點搵唔到：" + label)
    b = s.find(end, a + len(start))
    if b < 0:
        raise SystemExit("❌ 段終點搵唔到：" + label)
    s = s[:a] + new + s[b:]


# ══════════════════════════════════════════════════════════════════════
# 1. 資料區：CFG / DIAG / exit / PLAN / activeIds / BADGES
# ══════════════════════════════════════════════════════════════════════
repa("尺尺：請先完成 8 題分層診斷。", "尺尺：請先完成 5 題分層診斷。", "精靈初始氣泡與品質閘")
rep("  minutes: 20,", "  minutes: 15,", "時間預算")

DIAG_NEW = r'''/* 分層診斷：5 題（★2／★★2／★★★1），依難度配分 1／2／3 分，滿分 9 分。
   測的是本課前置能力（比的化簡、單位換算、前項化為 1），不是本課新知。
   加權得分讓同一層級內仍能看出程度差異；每題只作答一次，答錯不補答，診斷不可重做。 */
const DIAG = [
  { s:"比的化簡", d:1, t:"化簡比 12 : 18 ＝ 2 : （　）", a:["3"], sec:25,
    exp:"12 : 18 同除以 6 → 2 : 3", src:"《澳門新思維數學》第2課 比的性質（本課前置知識）" },
  { s:"單位換算", d:1, t:"3 米 ＝ （　）厘米", a:["300"], sec:25,
    exp:"1 米 ＝ 100 厘米，3 米 ＝ 300 厘米", src:"長度單位換算（本課前置知識）" },
  { s:"單位換算", d:2, t:"1 km ＝ （　）厘米", a:["100000"], sec:30,
    exp:"1 km ＝ 1000 m ＝ 100 000 cm", src:"課本 p.52 附加例題 1（前置：米與千米化為厘米）" },
  { s:"前項化為 1", d:2, t:"化簡比 25 : 4000 ＝ 1 : （　）", a:["160"], sec:40,
    exp:"25 : 4000 同除以 25 → 1 : 160", src:"課本 p.52 第13課第2題附加例題 3(a)（前置化簡）" },
  { s:"前項化為 1", d:3, t:"把 1.1 : 36 300 化成前項是 1 的比，即 1 : （　）", a:["33000"], sec:50,
    exp:"1.1 : 36 300 同除以 1.1 → 1 : 33 000", src:"自編補充工作紙冊 第13課 計算題 2（前置化簡）" }
];

'''
seg("/* 分層診斷：8 題（★3／★★3／★★★2）", "const DATA = {", DIAG_NEW, "DIAG 5 題")

EXIT_NEW = r'''  /* 出門票：★／★★／★★★ 各 4 題，每層派 4 題，與本層主題一致 */
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
    { d:1, sec:70, src:"《澳門新思維數學習作》練習13 第1題表格變式（更換數字）",
      t:"地圖上 3 cm 代表實際 45 cm，這幅地圖的比例尺是 1 : （　）", a:["15"],
      exp:"3 : 45 同除以 3 → 1 : 15。",
      redo:{ t:"地圖上 6 cm 代表實際 90 cm，比例尺是 1 : （　）", a:["15"],
             exp:"6 : 90 ＝ 1 : 15" } },
    { d:1, sec:75, src:"《澳門新思維數學習作》練習13 第1題表格變式（更換數字）",
      t:"地圖上 4 cm 代表實際 120 cm，這幅地圖的比例尺是 1 : （　）", a:["30"],
      exp:"4 : 120 同除以 4 → 1 : 30。",
      redo:{ t:"地圖上 2 cm 代表實際 60 cm，比例尺是 1 : （　）", a:["30"],
             exp:"2 : 60 ＝ 1 : 30" } },
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
    { d:2, sec:105, src:"課本 p.52 第13課第2題附加例題 1（水池 24 米／圖上 5 厘米）",
      t:"水池實際邊長 24 米，圖上邊長 5 cm，這幅圖的比例尺是 1 : （　）", a:["480"],
      exp:"24 m ＝ 2400 cm；5 : 2400 ＝ 1 : 480。",
      redo:{ t:"草地實際長 48 米，圖上長 10 cm，比例尺是 1 : （　）", a:["480"],
             exp:"48 m ＝ 4800 cm；10 : 4800 ＝ 1 : 480" } },
    { d:2, sec:105, src:"課本 p.52 第13課第2題附加例題 3(b)（草地 90 米／圖上 12 厘米）",
      t:"草地實際長 90 米，圖上長 12 cm，這幅圖的比例尺是 1 : （　）", a:["750"],
      exp:"90 m ＝ 9000 cm；12 : 9000 ＝ 1 : 750。",
      redo:{ t:"跑道實際長 45 米，圖上長 6 cm，比例尺是 1 : （　）", a:["750"],
             exp:"45 m ＝ 4500 cm；6 : 4500 ＝ 1 : 750" } },
    { d:3, sec:135, src:"《澳門新思維數學習作》練習13 第42題（零件邊長 8 mm／圖上 2.4 cm）",
      t:"零件實際邊長 8 mm，設計圖上邊長 2.4 cm，這幅設計圖的比例尺是 （　） : 1", a:["3"],
      exp:"2.4 cm ＝ 24 mm；24 : 8 ＝ 3 : 1，屬放大比例尺。",
      redo:{ t:"設計圖上 5 cm 代表實際 2.5 mm，比例尺是 （　） : 1", a:["20"],
             exp:"5 cm ＝ 50 mm；50 : 2.5 ＝ 20 : 1" } },
    { d:3, sec:135, src:"工作紙 24.png 第⑧題（0 100 200 300 400 km）",
      t:"線段比例尺每格 1 cm 代表 100 km，寫成數值比例尺是 1 : （　）", a:["10000000"],
      exp:"100 km ＝ 10 000 000 cm，所以 1 : 10 000 000。",
      redo:{ t:"線段比例尺每格 1 cm 代表 250 km，寫成數值比例尺是 1 : （　）", a:["25000000"],
             exp:"250 km ＝ 25 000 000 cm → 1 : 25 000 000" } },
    { d:3, sec:140, src:"《澳門新思維數學習作》練習13 第40題（7.5 dm 代表 15 mm）",
      t:"設計圖上 7.5 dm 代表實際 15 mm，這張設計圖的比例尺是 （　） : 1", a:["50"],
      exp:"7.5 dm ＝ 750 mm；750 : 15 ＝ 50 : 1，屬放大比例尺。",
      redo:{ t:"設計圖上 5 cm 代表實際 2.5 mm，比例尺是 （　） : 1", a:["20"],
             exp:"5 cm ＝ 50 mm；50 : 2.5 ＝ 20 : 1" } },
    { d:3, sec:135, src:"工作紙 24.png 第⑦題變式（每格代表 200 m）",
      t:"線段比例尺每格 1 cm 代表 200 m，寫成數值比例尺是 1 : （　）", a:["20000"],
      exp:"200 m ＝ 20 000 cm，所以 1 : 20 000。",
      redo:{ t:"線段比例尺每格 1 cm 代表 500 m，寫成數值比例尺是 1 : （　）", a:["50000"],
             exp:"500 m ＝ 50 000 cm → 1 : 50 000" } }
  ]
};

'''
seg("  /* 出門票：★／★★／★★★ 各 2 題，與本層主題一致 */",
    "\n/* ═══ 本層主題鏈 ═══", EXIT_NEW, "exit 12 題")

PLAN_NEW = r'''/* ═══ 本層主題鏈 ═══
   每層只派 4 題出門票；分步列式與錯例醫院改為「參考示範、不必作答」。
   PLAN.steps／PLAN.clinic 保留為本層示範題索引，不計入作答量。 */
const PLAN = {
  1:{ topic:"比例尺的意義：圖上距離 : 實際距離", steps:[0,1,2,3], clinic:[0,1], exit:[0,1,2,3],
      focus:"辨認前項是圖上距離、後項是實際距離；單位相同時直接化成前項為 1 的比" },
  2:{ topic:"先統一單位，再求比例尺", steps:[4,5,6,7], clinic:[2,3], exit:[4,5,6,7],
      focus:"把米或千米化成厘米，寫出「圖上 : 實際」並化簡為 1 : n" },
  3:{ topic:"線段比例尺與放大比例尺", steps:[8,9,10,11], clinic:[4,5], exit:[8,9,10,11],
      focus:"讀出每格距離並換算；辨認 10 : 1 放大比例尺" }
};
function planOf(){ return PLAN[lv()] || PLAN[2]; }
function activeIds(stage){
  /* 只派出門票；分步與錯例為參考示範，不產生作答題 */
  if(stage!=="exit") return [];
  const arr=DATA.exit;
  if(ST.all) return arr.map(function(_,i){return i;});
  return planOf().exit.slice();
}
function statPlan(stage){ return stat(stage, DATA[stage], activeIds(stage)); }

'''
seg("/* ═══ 本層主題鏈 ═══", "/* 徽章 */", PLAN_NEW, "PLAN 與 activeIds")

repa("完成 8 題分層診斷", "完成 5 題分層診斷", "分層完成徽章")
repa("max:15", "max:9", "診斷滿分初始值")

# ══════════════════════════════════════════════════════════════════════
# 2. buildSteps / buildClinic 改為「參考示範、不必作答」
# ══════════════════════════════════════════════════════════════════════
STEPS_NEW = r'''r''' + "'''" + r'''function buildSteps(){
  const box=document.createElement("div");
  const L=LV[lv()], P=planOf();
  const ids=P.steps.slice();
  let h='<p class="sc-intro">📚 <b>分步列式（參考示範）</b>　本階段改為老師示範，<b>不必作答</b>；今日只須完成 4 題出門票。</p>'+
    '<div class="sc-plan-bar">🎯 你是 <b>'+L.s+' '+L.n+'</b>　→　本層主題：<b>'+esc(P.topic)+
    '</b>；以下 '+ids.length+' 題為本層解題鏈示範，讀一遍作法即可。</div>';
  ids.forEach(function(i,n){
    const it=DATA.steps[i];
    h+='<div class="card" style="box-shadow:none;border:2px solid var(--ink);margin:0 0 10px">'+
      '<div class="sc-q"><span class="sc-no">'+(n+1)+'</span>'+
      '<span class="sc-lv sc-star sc-d'+(it.d||2)+'">'+stars(it.d||2)+'</span>'+
      '<span class="sc-qtext">'+esc(it.t)+'</span>'+
      (it.sec?'<span class="sc-sec">⏱ 約 '+it.sec+' 秒</span>':'')+'</div>'+
      (it.src?'<div class="sc-src">📖 教材依據：'+esc(it.src)+'</div>':'')+
      '<div class="concept-box">✅ <b>答案：</b>'+esc((it.a||[]).join("、"))+
      '<br>💡 '+esc(it.exp||"")+'</div></div>';
  });
  h+='<div class="sc-btns" style="justify-content:center">'+
     '<button class="btn btn-primary btn-sm" data-a="toexit">🚪 前往出門票</button></div>';
  box.innerHTML=h;
  box.querySelector('[data-a="toexit"]').onclick=function(){ UI.open("exit"); };
  return box;
}
'''
seg('r\'\'\'function buildSteps(){', "''', \"buildSteps\")", STEPS_NEW, "buildSteps 示範頁")

CLINIC_NEW = r'''r''' + "'''" + r'''function buildClinic(){
  const box=document.createElement("div");
  const L=LV[lv()], P=planOf();
  const ids=P.clinic.slice();
  let h='<p class="sc-intro">🏥 <b>錯例醫院（參考示範）</b>　本階段改為老師示範，<b>不必作答</b>；讀一遍常見錯誤，出門票就不會踩同一個坑。</p>'+
    '<div class="sc-plan-bar">🎯 本層 <b>'+L.s+' '+L.n+'</b>　→　主題：<b>'+esc(P.topic)+
    '</b>；以下 '+ids.length+' 題為本層常見錯例示範。</div>';
  ids.forEach(function(i,n){
    const c=DATA.clinic[i];
    h+='<div class="card" style="box-shadow:none;border:2px solid var(--ink);margin:0 0 10px">'+
      '<div class="sc-q"><span class="sc-no">'+(n+1)+'</span>'+
      '<span class="sc-lv sc-star sc-d'+(c.d||2)+'">'+stars(c.d||2)+'</span>'+
      '<span class="sc-qtext">病人計算：<span class="wrong-expr">'+esc(c.w)+'</span></span>'+
      (c.sec?'<span class="sc-sec">⏱ 約 '+c.sec+' 秒</span>':'')+'</div>'+
      (c.src?'<div class="sc-src">📖 教材依據：'+esc(c.src)+'</div>':'')+
      '<div class="concept-box">🔍 <b>'+esc(c.q)+'</b><br>✅ 正確答案：<b>第 '+(c.ans+1)+' 項</b>　'+
      esc(c.opts[c.ans]||"")+'<br>💡 '+esc(c.exp||"")+'</div></div>';
  });
  h+='<div class="sc-btns" style="justify-content:center">'+
     '<button class="btn btn-primary btn-sm" data-a="toexit">🚪 前往出門票</button></div>';
  box.innerHTML=h;
  box.querySelector('[data-a="toexit"]').onclick=function(){ UI.open("exit"); };
  return box;
}
'''
seg('r\'\'\'function buildClinic(){', "''', \"buildClinic\")", CLINIC_NEW, "buildClinic 示範頁")

# ══════════════════════════════════════════════════════════════════════
# 3. 診斷：5 題、9 分、一次作答即鎖、不可重做
# ══════════════════════════════════════════════════════════════════════
DIAG_FN_NEW = r'''r''' + "'''" + r'''function buildDiag(){
  const box=document.createElement("div");
  /* 診斷已完成：只顯示結果，不可重做 */
  if(ST.diag.done){
    const Ld=LV[ST.diag.level]||LV[1];
    box.innerHTML='<div class="sc-plan-bar" style="font-size:16px">✅ <b>分層診斷已完成，不可重做。</b><br>'+
      '診斷得分 <b>'+(ST.diag.score||0)+' / '+(ST.diag.max||9)+' 分</b>　｜　層級 <b>'+Ld.s+' '+Ld.n+
      '</b>　｜　答對 '+(ST.diag.right||0)+' / '+DIAG.length+' 題<br>'+
      '<span class="sc-mute">每題只作答一次，答錯不補答；診斷結果已用於配對本層出門票。</span></div>'+
      '<div class="sc-btns" style="justify-content:center;margin-top:12px">'+
      '<button class="btn btn-primary btn-sm" data-a="toexp">🚪 前往練習</button></div>';
    box.querySelector('[data-a="toexp"]').onclick=function(){ UI.close(); go("explore"); };
    return box;
  }
  box.innerHTML='<p class="sc-intro">🧭 先完成 <b>5 題分層診斷</b>，讓系統知道你的起點。'+
    '題目依難度配分：<b>★ 題 1 分、★★ 題 2 分、★★★ 題 3 分，滿分 9 分</b>。'+
    '這部分不計入練習成績、不提供提示；<b>每題只作答一次，答錯不補答</b>，遇到不會的題目照樣填寫即可。</p>';
  DIAG.forEach(function(q,i){
    const r=ST.diag["q"+i]||{}; ST.diag["q"+i]=r;
    const row=document.createElement("div");
    row.className="sc-item"+(r.locked?" sc-done":"");
    row.innerHTML='<div class="sc-q"><span class="sc-no">'+(i+1)+'</span>'+
      '<span class="sc-lv">'+esc(q.s)+'　'+stars(q.d||1)+'　'+(q.d||1)+' 分</span>'+
      '<span class="sc-qtext">'+q.t.replace(/（　）/g,'<input class="sc-in" type="text" inputmode="decimal">')+'</span>'+
      (q.sec?'<span class="sc-sec">⏱ 約 '+q.sec+' 秒</span>':'')+'</div>'+
      (q.src?'<div class="sc-src">📖 教材依據：'+esc(q.src)+'</div>':'')+
      '<div class="sc-btns"><button class="btn btn-primary btn-sm" data-a="ck">✓ 檢查</button></div>'+
      '<div class="sc-fb" id="dfb'+i+'"></div>';
    const inp=row.querySelector(".sc-in"), fb=row.querySelector(".sc-fb");
    const btn=row.querySelector('[data-a="ck"]');
    function lockRow(msg,cls){
      inp.disabled=true; btn.disabled=true; btn.style.display="none";
      fb.className=cls; fb.innerHTML=msg; row.classList.add("sc-done");
    }
    if(r.locked||r.done||r.ok){
      r.locked=true;
      if(r.ok) lockRow("✅ 本題已作答，答案正確。","sc-fb sc-ok");
      else lockRow("❌ 本題已作答，答案不正確，不能補答。","sc-fb sc-bad");
    }
    btn.onclick=function(){
      if(r.locked||r.done||r.ok) return;
      r.locked=true;
      if(norm(inp.value)===norm(q.a[0])){
        r.ok=true; lockRow("✅ 正確！"+esc(q.exp||""),"sc-fb sc-ok");
        sndOk(); addXp(5);
      } else {
        r.ok=false; lockRow("❌ 答案不正確，本題已記錄，不能補答。","sc-fb sc-bad");
        sndNo();
      }
      save();
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
    /* 加權得分＋基礎題門檻：基礎題至少對 1 題，才允許進入較高層級 */
    const baseReady = baseOk>=1;
    let L2 = 1;
    if(score>=7 && baseReady) L2=3;
    else if(score>=4 && baseReady) L2=2;
    else L2=1;
    ST.diag.done=true; ST.diag.score=score; ST.diag.max=max;
    ST.diag.right=right; ST.diag.baseOk=baseOk; ST.diag.level=L2;
    try{ localStorage.setItem(LKEY, JSON.stringify({level:L2,score:score,max:max,right:right,ts:Date.now()})); }catch(e){}
    save();
    const Li=LV[L2];
    document.getElementById("diagRes").innerHTML=
      '<div class="sc-plan-bar" style="font-size:16px">🎯 你是 <b>'+Li.s+' '+Li.n+'</b>　'+
      '（診斷得分 <b>'+score+' / '+max+' 分</b>；答對 '+right+' / '+DIAG.length+' 題）<br>'+Li.tip+
      '<br><span class="sc-mute">5 題依難度配分，得分越接近滿分，代表已具備越多本課前置能力；同一層級內仍可從得分看出差異。診斷不可重做。</span></div>';
    toast("🎯 分層完成：" + Li.s + " " + Li.n);
    setTimeout(()=>go("explore"), 1400);
  };
  return box;
}
'''
seg('r\'\'\'function buildDiag(){', "''', \"buildDiag v3\")", DIAG_FN_NEW, "buildDiag v4")
rep("''', \"buildDiag v3\")", "''', \"buildDiag v4\")", "buildDiag 段標籤")

# ══════════════════════════════════════════════════════════════════════
# 4. 老師專用：移除「重做分層診斷」入口（診斷不可重做）
# ══════════════════════════════════════════════════════════════════════
rep('    {k:"reset",   i:"🔄", t:"重做分層診斷",   d:"重設層級（★／★★／★★★）"},\n',
    '', "移除重做診斷入口")
rep('      else if(it.k==="reset"){ ST.diag={done:false,score:0,max:9,right:0,baseOk:0,level:0}; DIAG.forEach(function(_,i){ ST.diag["q"+i]={}; }); try{localStorage.removeItem(LKEY);}catch(e){} save(); toast("🔄 已重設，請重新診斷"); go("diag"); }\n',
    '', "移除重做診斷分支")
rep('{k:"all",     i:"📚", t:"完成所有難度的題", d:"解除分層限制（學生自願）"}',
    '{k:"all",     i:"📚", t:"加做其他層級出門票", d:"學生自願，解除分層限制"}', "老師 all 入口描述")
rep('toast("📚 已解除限制")', 'toast("📚 已加開其他層級出門票")', "老師 all toast")

# ══════════════════════════════════════════════════════════════════════
# 4b. 出門票題沒有獨立 hint 欄位：答錯後以解題解釋作為提示
#     （維持「提示只在答錯後出現」，唯一作答題必須有提示）
# ══════════════════════════════════════════════════════════════════════
repa('esc(item.hint||"")', 'esc(item.hint||item.exp||"")', "提示內容 fallback")
repa('if(item.hint) hintEl.classList.add("on");',
     'if(item.hint||item.exp) hintEl.classList.add("on");', "重開頁面提示 fallback")
repa('if(item.hint){', 'if(item.hint||item.exp){', "答錯提示統計 fallback")

# ══════════════════════════════════════════════════════════════════════
# 5. 總結卡 / 學生報告 / 報告卡 / 文案 / 時間預算
# ══════════════════════════════════════════════════════════════════════
rep("'<div class=\"sum-box\"><div class=\"k\">② 分步列式</div><div class=\"v\">'+s1.done+'<small>/'+s1.total+'</small></div></div>'+\n    '<div class=\"sum-box\"><div class=\"k\">③ 錯例醫院</div><div class=\"v\">'+s3.done+'<small>/'+s3.total+'</small></div></div>'+",
    "'<div class=\"sum-box\"><div class=\"k\">② 分步列式</div><div class=\"v\" style=\"font-size:18px\">參考示範</div></div>'+\n    '<div class=\"sum-box\"><div class=\"k\">③ 錯例醫院</div><div class=\"v\" style=\"font-size:18px\">參考示範</div></div>'+",
    "總結卡示範格")
rep("今日須作答 16 題。</div>'+", "今日須作答 9 題（診斷 5 ＋ 出門票 4）。</div>'+", "總結卡題數")
repa("（診斷 5 ＋ 推演 2 ＋ 分步 5 ＋ 錯例 2.5 ＋ 出門票 4 ＋ 總結 1.5）",
     "（診斷 2.5 ＋ 推演 2 ＋ 示範瀏覽 2 ＋ 出門票 7 ＋ 總結 1.5）", "時間拆分")
repa("(ST.diag.max||15)", "(ST.diag.max||9)", "報告與報告卡診斷分母")
rep("今日只派 8 題練習。</div>'+", "今日只派 4 題出門票。</div>'+", "學生報告配題說明")
rep('"今日須作答 16 題（診斷 8 ＋ 本層練習 8）　｜　時間預算 "+CFG.minutes+" 分鐘"',
    '"今日須作答 9 題（診斷 5 ＋ 出門票 4）　｜　時間預算 "+CFG.minutes+" 分鐘"', "報告卡總題數")
rep('sec(y,"四、本層配對（今日只做 8 題）");',
    'sec(y,"四、本層配對（今日只做 4 題）");', "報告卡配對標題")

CARD_ROWS_NEW = r'''    [
      ["② 分步列式","本層 "+Pl.steps.length+" 題","參考示範、不必作答"],
      ["③ 錯例醫院","本層 "+Pl.clinic.length+" 題","參考示範、不必作答"],
      ["④ 出門票","第 "+listNo(Pl.exit)+" 題",s2.done+" / "+s2.total+" 已完成"]
'''
seg('    [\n      ["② 分步列式","第 "', "    ].forEach(function(r,i){", CARD_ROWS_NEW, "報告卡配對三行")

# 學生報告的薄弱點改由錯題錯因推導（分步題已不作答）
REPORT_WEAK_OLD = r'''  const weakMap={};
  DATA.steps.forEach((it,i)=>{ const r=ST.steps[i]; if(r&&r.wrong){ weakMap[it.t.slice(0,16)]=(weakMap[it.t.slice(0,16)]||0)+r.wrong; } });
  const weak=Object.keys(weakMap).sort((a,b)=>weakMap[b]-weakMap[a]);
  const wbs=ST.wrongBook.slice().sort((a,b)=>b.at-a.at);
  const cmap={}; wbs.forEach(w=>{ cmap[w.why]=(cmap[w.why]||0)+1; });
  const ckeys=Object.keys(cmap).sort((a,b)=>cmap[b]-cmap[a]);
  const advice = weak.length
'''
REPORT_WEAK_NEW = r'''  const wbs=ST.wrongBook.slice().sort((a,b)=>b.at-a.at);
  const cmap={}; wbs.forEach(w=>{ cmap[w.why]=(cmap[w.why]||0)+1; });
  const ckeys=Object.keys(cmap).sort((a,b)=>cmap[b]-cmap[a]);
  const weak=ckeys.slice();
  const advice = weak.length
'''
rep(REPORT_WEAK_OLD, REPORT_WEAK_NEW, "學生報告弱項改由錯因推導")

# 閘門／快捷列／標題／引入頁／練習頁文案
repa("8 題分層診斷", "5 題分層診斷", "診斷題數文案")
rep('diag:  ["🧭 分層診斷 —— 8 題定程度","依難度配分 1／2／3 分，滿分 15 分；加權得分決定你的層級。"],',
    'diag:  ["🧭 分層診斷 —— 5 題定程度","依難度配分 1／2／3 分，滿分 9 分；每題只答一次，答錯不補答。"],',
    "診斷彈窗標題")
rep('本課設有分層——先完成 8 題診斷，系統只會派發適合你程度的 <b>8 題練習</b>（分步 4 題、錯例 2 題、出門票 2 題），不必全部作答。未完成診斷前，練習不會開啟。',
    '本課設有分層——先完成 5 題診斷，系統只會派發適合你程度的 <b>4 題出門票</b>；分步列式與錯例醫院改為參考示範，不必作答。未完成診斷前，練習不會開啟。',
    "引入頁 UDL 提示")
rep('今日須作答 <b>16 題</b>（診斷 8 ＋ 本層練習 8）',
    '今日須作答 <b>9 題</b>（診斷 5 ＋ 出門票 4）', "引入頁總題數")
rep("　今日只派 <b>8 題</b>（分步 4 ＋ 錯例 2 ＋ 出門票 2），八題都練同一個概念；其他層級的題目不會出現在你的練習中。",
    "　今日只派 <b>4 題出門票</b>，四題都練同一個概念；分步列式與錯例醫院為參考示範，不必作答。",
    "練習頁配對說明")
rep('  const sIds=activeIds("steps"), cIds=activeIds("clinic"), eIds=activeIds("exit");',
    '  const sIds=Pl.steps, cIds=Pl.clinic, eIds=activeIds("exit");', "練習頁示範題索引")
rep('    ["② 分步列式",sIds.length+" 題","本層第 "+sIds.map(function(i){return i+1;}).join("、")+" 題（"+L.s+"）","約 "+secOf(DATA.steps,sIds)+" 分鐘"],\n    ["③ 錯例醫院",cIds.length+" 題","本層第 "+cIds.map(function(i){return i+1;}).join("、")+" 題","約 "+secOf(DATA.clinic,cIds)+" 分鐘"],',
    '    ["② 分步列式","示範 "+sIds.length+" 題","本層第 "+sIds.map(function(i){return i+1;}).join("、")+" 題（不必作答）","約 "+secOf(DATA.steps,sIds)+" 分鐘瀏覽"],\n    ["③ 錯例醫院","示範 "+cIds.length+" 題","本層第 "+cIds.map(function(i){return i+1;}).join("、")+" 題（不必作答）","約 "+secOf(DATA.clinic,cIds)+" 分鐘瀏覽"],',
    "練習頁配對表")
rep('steps: ["② 分步列式","我來試試：一步一步填寫算式"],',
    'steps: ["② 分步列式","參考示範：題目、答案與解題步驟（不必作答）"],', "主線按鈕描述 ②")
rep('clinic:["③ 錯例醫院","看列式：找出別人的錯誤"],',
    'clinic:["③ 錯例醫院","參考示範：看看別人錯在哪裡（不必作答）"],', "主線按鈕描述 ③")
rep('          const done = k==="steps"? statPlan("steps").done>=statPlan("steps").total\n                     : k==="exit"? statPlan("exit").done>0\n                     : k==="derive"? DATA.derive.every((_,j)=>ST.derive[j]&&ST.derive[j].v!==undefined)\n                     : k==="clinic"? statPlan("clinic").done>=statPlan("clinic").total\n                     : false;',
    '          const done = k==="steps"? false\n                     : k==="exit"? statPlan("exit").done>0\n                     : k==="derive"? DATA.derive.every((_,j)=>ST.derive[j]&&ST.derive[j].v!==undefined)\n                     : k==="clinic"? false\n                     : false;',
    "主線完成判定")

# ══════════════════════════════════════════════════════════════════════
# 6. 品質閘：題庫摘要、結構檢查、舊文案掃描
# ══════════════════════════════════════════════════════════════════════
rep('print("✅ 題庫：診斷 8 題（加權滿分 15）／分步 12 題／錯例 6 題／出門票 6 題；每層只派 8 題；時間預算 20 分鐘")',
    'print("✅ 題庫：診斷 5 題（加權滿分 9）／分步 12 題／錯例 6 題／出門票 12 題；每層只派 4 題出門票；時間預算 15 分鐘")',
    "題庫摘要")

MECH_OLD = r'''    ("診斷 8 題加權分層（滿分 15、基礎題門檻）",
     "const DIAG = [" in html and "ST.diag.max=max" in html and
     "score>=11 && baseReady" in html and "score>=6 && baseReady" in html and
     "baseOk>=2" in html),
    ("每層 8 題練習（分步 4／錯例 2／出門票 2）",
     "steps:[0,1,2,3]" in html and "steps:[4,5,6,7]" in html and
     "steps:[8,9,10,11]" in html and "exit:[4,5]" in html and
     "clinic:[4,5]" in html and "return picks.slice();" in html),
'''
MECH_NEW = r'''    ("診斷 5 題加權分層（滿分 9、基礎題門檻）",
     "const DIAG = [" in html and "ST.diag.max=max" in html and
     "score>=7 && baseReady" in html and "score>=4 && baseReady" in html and
     "baseOk>=1" in html and "max:9" in html),
    ("診斷不可重做（一次作答即鎖、答錯不補答）",
     "分層診斷已完成，不可重做" in html and "不能補答" in html and
     "r.locked=true" in html and "if(ST.diag.done){" in html and
     "重做分層診斷" not in html),
    ("每層只派 4 題出門票（分步／錯例為參考示範）",
     "exit:[0,1,2,3]" in html and "exit:[4,5,6,7]" in html and
     "exit:[8,9,10,11]" in html and 'if(stage!=="exit") return [];' in html and
     "參考示範" in html and "return planOf().exit.slice();" in html),
'''
rep(MECH_OLD, MECH_NEW, "MECH 三項")
# 角色錨點已由開頭的 repa 一併改為 5 題，無需額外替換

# 舊文案掃描（防止改漏一處）
OLD_WORDS = ["8 題分層診斷", "滿分 15 分", "16 題", "只派 8 題",
             "分步 4 ＋ 錯例 2 ＋ 出門票 2", 't:"重做分層診斷"',
             "今日只做 8 題", "score>=11", "score>=6 && baseReady",
             "baseOk>=2", "max:15", "20 分鐘"]
hits = [w for w in OLD_WORDS if w in s]
if hits:
    raise SystemExit("❌ 仍有舊題數／舊分層文案：%s" % hits)

# Python 語法檢查
try:
    ast.parse(s)
except SyntaxError as e:
    raise SystemExit("❌ build.py 語法錯誤：%s (line %d)" % (e.msg, e.lineno))

if s == ORIG:
    raise SystemExit("⚠️ 沒有任何改動（可能已升級過）")

P.write_text(s, "utf-8")
print("✅ upgrade-v4.py 完成：診斷 5 題／滿分 9／不可重做；每層 4 題出門票；分步與錯例改為參考示範")
