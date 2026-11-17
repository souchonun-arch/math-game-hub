#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3 收尾：統計口徑納入錯例醫院，讓「今日 8 題」與報告分母一致。
   錯例的 ST key 是 "c"+idx，故 stat() 需對 clinic 使用該 key。"""
import pathlib

P = pathlib.Path("/Users/chonunsou/WorkBuddy/互動教材開發/認識比例尺-像素風/build.py")
s = P.read_text("utf-8")
orig = s


def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit("❌ anchor 搵唔到：" + label)
    if s.count(old) != 1:
        raise SystemExit("❌ anchor 唔唯一（%d 處）：%s" % (s.count(old), label))
    s = s.replace(old, new, 1)


rep('''  list.forEach(function(i){
    const r=ST[stage][i]; if(!r) return;''',
    '''  list.forEach(function(i){
    const key = stage==="clinic" ? "c"+i : i;
    const r=ST[stage][key]; if(!r) return;''',
    "stat 支援 clinic 的 c+idx key")

rep('''    const s1=statPlan("steps"), s2=statPlan("exit");
    const total=s1.total+s2.total, done=s1.done+s2.done;
    const pct=total?Math.round(done/total*100):0;''',
    '''    const s1=statPlan("steps"), s2=statPlan("exit"), s3=statPlan("clinic");
    const total=s1.total+s2.total+s3.total, done=s1.done+s2.done+s3.done;
    const pct=total?Math.round(done/total*100):0;''',
    "drawCard 8 題統計")

rep('''  const s1=statPlan("steps"), s2=statPlan("exit");
  const total=s1.total+s2.total, done=s1.done+s2.done, wrong=s1.wrong+s2.wrong;
  const okCount=s1.ok+s2.ok;   /* 一次作答制：答錯不計 done，不可用 done-wrong 推答對數 */''',
    '''  const s1=statPlan("steps"), s2=statPlan("exit"), s3=statPlan("clinic");
  const total=s1.total+s2.total+s3.total, done=s1.done+s2.done+s3.done,
        wrong=s1.wrong+s2.wrong+s3.wrong;
  const okCount=s1.ok+s2.ok+s3.ok;   /* 一次作答制：答錯不計 done，不可用 done-wrong 推答對數 */''',
    "buildReport 8 題統計")

rep('''  const s1=statPlan("steps"), s2=statPlan("exit");
  const total=s1.total+s2.total, done=s1.done+s2.done;
  const mins=Math.max(1,Math.round((Date.now()-ST.t0)/60000));''',
    '''  const s1=statPlan("steps"), s2=statPlan("exit"), s3=statPlan("clinic");
  const total=s1.total+s2.total+s3.total, done=s1.done+s2.done+s3.done;
  const mins=Math.max(1,Math.round((Date.now()-ST.t0)/60000));''',
    "buildSummary 8 題統計")

rep('''    '<div class="sum-box"><div class="k">② 分步列式</div><div class="v">'+s1.done+'<small>/'+s1.total+'</small></div></div>'+
    '<div class="sum-box"><div class="k">④ 出門票</div><div class="v">'+s2.done+'<small>/'+s2.total+'</small></div></div>'+''',
    '''    '<div class="sum-box"><div class="k">② 分步列式</div><div class="v">'+s1.done+'<small>/'+s1.total+'</small></div></div>'+
    '<div class="sum-box"><div class="k">③ 錯例醫院</div><div class="v">'+s3.done+'<small>/'+s3.total+'</small></div></div>'+
    '<div class="sum-box"><div class="k">④ 出門票</div><div class="v">'+s2.done+'<small>/'+s2.total+'</small></div></div>'+''',
    "總結卡加錯例格")

rep('''                     : Object.keys(ST.clinic).some(x=>ST.clinic[x]&&ST.clinic[x].done);''',
    '''                     : k==="clinic"? statPlan("clinic").done>=statPlan("clinic").total
                     : false;''',
    "renderPractice 完成判定")

rep('''  activeIds("exit").forEach(function(i){
    const it=DATA.exit[i], r=ST.exit[i]||{};''',
    '''  activeIds("clinic").forEach(function(i){
    const c=DATA.clinic[i], r=ST.clinic["c"+i]||{};
    rows+="<tr><td>③-"+(i+1)+"</td><td>"+stars(c.d||2)+"</td><td>"+esc((c.w||"").slice(0,24))+"</td><td>"+
      (r.done?"✓ 完成":(r.locked?"已作答（錯）":"未做"))+"</td><td>"+(r.wrong||0)+"</td><td>"+(c.sec||"-")+"</td></tr>";
  });
  activeIds("exit").forEach(function(i){
    const it=DATA.exit[i], r=ST.exit[i]||{};''',
    "報告逐題記錄加錯例 2 題")

P.write_text(s, "utf-8")
print("✅ build.py 統計口徑已統一為 8 題（分步 4＋錯例 2＋出門票 2）")
print("   %d → %d chars" % (len(orig), len(s)))
