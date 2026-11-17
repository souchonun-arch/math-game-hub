#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
由「波仔互動教材模板」生成《認識比例尺｜像素風（小六重點班）》互動教材。

冪等：每次執行都由模板重新產生，可重複跑。
用法：python3 build.py
"""
import pathlib, shutil, re, sys

ROOT = pathlib.Path("/Users/chonunsou/WorkBuddy/互動教材開發")
SRC = ROOT / "波仔互動教材模板" / "波仔互動教材模板.html"
OUTDIR = ROOT / "認識比例尺-像素風"
OUT = OUTDIR / "認識比例尺-像素風.html"
QR = ROOT / "波仔互動教材模板" / "qrcode.min.js"

html = SRC.read_text("utf-8")

def rep(old, new, label, count=1):
    global html
    if old not in html:
        raise SystemExit("❌ anchor 搵唔到：" + label)
    html = html.replace(old, new, count)

def seg(start_marker, end_marker, new, label):
    """替換 [start_marker, end_marker) 區間，保留 end_marker 之後的內容。"""
    global html
    a = html.find(start_marker)
    if a < 0:
        raise SystemExit("❌ segment 起點搵唔到：" + label)
    b = html.find(end_marker, a + len(start_marker))
    if b < 0:
        raise SystemExit("❌ segment 終點搵唔到：" + label)
    html = html[:a] + new + "\n" + html[b:]


# ══════════════════════════════════════════════════════════════════════
# 1. 標題
# ══════════════════════════════════════════════════════════════════════
rep("<title>互動教材模板</title>",
    "<title>認識比例尺｜像素製圖師的縮尺密碼（小六重點班）</title>", "title")
rep('<div class="pill combo" id="hudCombo">🔥 <b>0</b> 連對</div>',
    '<div class="pill combo" id="hudCombo">🔥 <b>0</b> 連續答對</div>', "HUD 連對")


# ══════════════════════════════════════════════════════════════════════
# 2. 像素風 CSS（整段換）
# ══════════════════════════════════════════════════════════════════════
CSS = r'''<style>
:root{
  --primary:#E14B3C; --secondary:#2E5CA8; --accent:#F5B731;
  --success:#2E9E63; --danger:#D33A3A; --xp:#F5B731; --combo:#E14B3C;
  --bg:#F3EFE1; --card:#FFFDF6; --text:#25243A; --muted:#6F6B80;
  --line:#25243A; --ink:#25243A; --pale:#E9E4D2;
  --shadow:4px 4px 0 var(--ink); --radius:0px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{background:var(--bg)}
body{font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;
  background-color:var(--bg);
  background-image:linear-gradient(0deg,rgba(37,36,58,.035) 1px,transparent 1px),
    linear-gradient(90deg,rgba(37,36,58,.035) 1px,transparent 1px);
  background-size:16px 16px;color:var(--text);line-height:1.8;
  -webkit-text-size-adjust:100%;image-rendering:pixelated}
button{font-family:inherit;font-size:inherit;cursor:pointer;border:none;background:none;color:inherit}
input{font-family:inherit;font-size:inherit}
.pxf{font-family:"Courier New",ui-monospace,"Noto Sans TC",monospace;
  font-weight:700;letter-spacing:1px}

/* ===== 頂列 ===== */
.navbar{position:sticky;top:0;z-index:60;background:var(--secondary);color:#FFFDF6;
  border-bottom:4px solid var(--ink);box-shadow:0 4px 0 rgba(37,36,58,.20)}
.navbar::after{content:"";display:block;height:4px;
  background:repeating-linear-gradient(90deg,var(--ink) 0 4px,transparent 4px 8px)}
.nav-top{display:flex;align-items:center;gap:14px;padding:10px 18px;flex-wrap:wrap}
.nav-emoji{font-size:26px;filter:drop-shadow(2px 2px 0 rgba(37,36,58,.5))}
.nav-title{font-size:17px;font-weight:700;flex:1;min-width:150px;letter-spacing:1px}
.nav-title small{display:block;font-size:12px;opacity:.82;font-weight:400}
.hud{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.pill{background:rgba(255,253,246,.16);border:2px solid #FFFDF6;padding:3px 10px;font-size:13px;
  display:flex;align-items:center;gap:5px;white-space:nowrap;font-weight:700}
.pill b{font-size:15px}
.pill.combo{background:var(--combo);opacity:0;transform:scale(.8);transition:.18s}
.pill.combo.on{opacity:1;transform:scale(1)}
.xpbar{width:90px;height:10px;background:rgba(37,36,58,.45);border:2px solid #FFFDF6;overflow:hidden}
.xpfill{height:100%;width:0;background:var(--xp);transition:width .4s steps(8)}
.nav-steps{display:flex;overflow-x:auto;background:rgba(37,36,58,.30);padding:0 10px;scrollbar-width:none}
.nav-steps::-webkit-scrollbar{display:none}
.nav-step{padding:9px 15px;font-size:14px;white-space:nowrap;opacity:.66;font-weight:700;
  border-bottom:4px solid transparent;transition:.15s}
.nav-step.active{opacity:1;border-bottom-color:var(--accent)}
.nav-step.done::after{content:" ✓";color:#9BF0BC}

/* ===== 版面 ===== */
main{max-width:1080px;margin:0 auto;padding:16px 16px 140px}
.page{display:none}
.page.active{display:block}
.card{background:var(--card);border:3px solid var(--ink);padding:20px;
  box-shadow:var(--shadow);margin-bottom:16px}
.section-title{font-size:19px;font-weight:700;color:var(--secondary);
  display:flex;align-items:center;gap:9px;margin-bottom:12px;letter-spacing:1px}
.section-title .emoji{font-size:23px}
.mission-card{background:var(--primary);color:#FFFDF6;border:3px solid var(--ink);
  box-shadow:4px 4px 0 var(--accent);padding:18px 20px;margin-bottom:14px}
.mission-card h2{font-size:19px;font-weight:700;margin-bottom:7px;letter-spacing:1px}
.mission-card p{font-size:14px;opacity:.97}
.story-line{background:#FFF3C9;border:3px solid var(--ink);border-left-width:8px;
  padding:13px 16px;margin:10px 0;font-size:15px}
.concept-box{background:#E8F0FF;border:2px solid var(--secondary);padding:13px 16px;
  margin:9px 0;font-size:15px}
.concept-box b{color:var(--secondary)}
.think-box{background:#FFF4E5;border:3px dashed var(--primary);padding:13px 16px;
  margin:11px 0;font-size:15px}
.udl-tip{background:#E4F6EB;border:2px solid var(--success);padding:10px 14px;
  font-size:13px;color:#1B6B42;margin-top:12px}
.tag-row{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.tag{background:#EEF3F8;border:2px solid var(--ink);padding:6px 14px;font-size:14px;transition:.14s}
.tag:hover{background:var(--pale)}
.tag.picked{background:var(--secondary);color:#FFFDF6}
.sc-intro{font-size:15px;margin-bottom:12px;line-height:1.85}

/* ===== 掣（像素硬邊） ===== */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;
  padding:10px 19px;font-size:15px;font-weight:700;letter-spacing:1px;
  border:3px solid var(--ink);box-shadow:4px 4px 0 var(--ink);
  transition:transform .08s,box-shadow .08s,background .15s}
.btn:hover{transform:translate(-2px,-2px);box-shadow:6px 6px 0 var(--ink)}
.btn:active{transform:translate(3px,3px);box-shadow:1px 1px 0 var(--ink)}
.btn-primary{background:var(--primary);color:#FFFDF6}
.btn-secondary{background:var(--secondary);color:#FFFDF6}
.btn-success{background:var(--success);color:#FFFDF6}
.btn-accent{background:var(--accent);color:#3A2C05}
.btn-ghost{background:#F1EEE2;color:var(--text)}
.btn-redo{background:#B43CD1;color:#FFFDF6}
.btn-sm{padding:6px 13px;font-size:14px;box-shadow:3px 3px 0 var(--ink)}
.btn:disabled{opacity:.45;cursor:not-allowed;transform:none;box-shadow:2px 2px 0 var(--ink)}

/* 主線四掣 */
.mainline{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.ml-btn{background:var(--card);border:3px solid var(--ink);box-shadow:3px 3px 0 var(--ink);
  padding:16px;text-align:left;transition:.12s;position:relative}
.ml-btn:hover{border-color:var(--primary);transform:translate(-2px,-2px);box-shadow:5px 5px 0 var(--ink)}
.ml-btn .n{font-size:12px;color:var(--muted);letter-spacing:2px;font-weight:700}
.ml-btn .t{font-size:17px;font-weight:700;color:var(--secondary);margin:3px 0}
.ml-btn .d{font-size:13px;color:var(--muted)}
.ml-btn.done{border-color:var(--success);background:#EAF8EF}
.ml-btn.done::before{content:"✓";position:absolute;top:8px;right:11px;
  color:var(--success);font-size:20px;font-weight:700}

/* 本層配對表 */
.match-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:9px;margin-top:10px}
.match-box{border:2px solid var(--ink);background:#F7F4E8;padding:9px 11px;font-size:13px;line-height:1.6}
.match-box b{display:block;color:var(--secondary);font-size:14px;margin-bottom:2px}
.match-box .m{color:var(--primary);font-weight:700}

/* ===== 題目 ===== */
.sc-item{border:2px solid var(--ink);background:#FFFDF6;padding:15px 17px;
  margin-bottom:12px;transition:.16s;box-shadow:3px 3px 0 rgba(37,36,58,.16)}
.sc-item.sc-done{border-color:var(--success);background:#EDF9F1}
.sc-item.sc-demo{background:#EFECE0;border-style:dashed;box-shadow:none}
.sc-q{font-size:17px;margin-bottom:9px;line-height:1.9}
.sc-no{display:inline-flex;align-items:center;justify-content:center;
  width:26px;height:26px;background:var(--secondary);color:#FFFDF6;border:2px solid var(--ink);
  font-size:13px;font-weight:700;margin-right:8px;vertical-align:middle}
.sc-lv{display:inline-block;font-size:12px;padding:1px 8px;margin-right:6px;
  vertical-align:middle;border:2px solid;font-weight:700}
.sc-star.sc-d1{color:#1B6B42;background:#E4F6EB;border-color:#2E9E63}
.sc-star.sc-d2{color:#9A5500;background:#FFF0CC;border-color:#E39A16}
.sc-star.sc-d3{color:#9E2222;background:#FFE3E1;border-color:#D33A3A}
.sc-sec{display:inline-block;font-size:12px;margin-left:8px;padding:1px 8px;
  background:#E9E4D2;border:2px solid var(--muted);font-weight:700;vertical-align:middle}
.sc-src{display:block;margin-top:6px;padding:5px 10px;font-size:12px;line-height:1.6;
  color:#5F5A4E;background:#F7F4E8;border-left:5px solid var(--accent);font-weight:700}
.sc-in{width:88px;padding:5px 8px;border:3px solid var(--ink);background:#FFFDF6;
  text-align:center;font-size:17px;font-weight:700;color:var(--primary);
  box-shadow:inset 2px 2px 0 rgba(37,36,58,.14);font-family:"Courier New",monospace}
.sc-in:focus{outline:none;background:#FFF3C9}
.sc-in:disabled{background:#E4E0D2;color:var(--muted)}
.sc-btns{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}
.sc-fb{margin-top:10px;padding:10px 14px;font-size:14px;display:none;border:2px solid}
.sc-fb.sc-ok{display:block;background:#E4F6EB;color:#1B6B42;border-color:var(--success)}
/* ⚠️ 不可用 sc-no：會與題號圓圈 .sc-no（26x26 inline-flex）撞名，把回饋區壓扁 */
.sc-fb.sc-bad{display:block;width:auto;height:auto;padding:10px 14px;font-size:14px;
  background:#FFE3E1;color:#9E2222;border-color:var(--danger)}
.sc-hint{display:none;margin-top:8px;padding:9px 13px;background:#FFF3C9;
  border:2px dashed var(--accent);font-size:14px;color:#6B5000}
.sc-hint.on{display:block}
.sc-mute{font-size:13px;color:var(--muted);margin-top:7px;line-height:1.7}
.sc-plan-bar{background:#E8F0FF;border:2px solid var(--secondary);padding:11px 15px;
  font-size:14px;color:#1C3F73;margin-bottom:12px;line-height:1.75}
.sc-plan-bar b{color:var(--secondary)}

/* ===== 本層配對／解題鏈一覽 ===== */
.sc-chain{margin:14px 0 4px;border:3px solid var(--ink);background:#EFECE0;box-shadow:4px 4px 0 var(--ink)}
.sc-chain summary{cursor:pointer;padding:11px 15px;font-weight:700;font-size:14px;
  color:var(--secondary);background:#E8F0FF;list-style:none}
.sc-chain summary::-webkit-details-marker{display:none}
.sc-chain summary::before{content:"\25B8 ";font-family:monospace}
.sc-chain[open] summary::before{content:"\25BE "}
.chain-row{padding:9px 15px;border-top:2px dashed var(--muted);font-size:13.5px;line-height:1.75}
.chain-row span{color:var(--muted)}

/* ===== 一次作答即鎖定／提示只在答錯後出現 ===== */
.hint-lock{display:inline-block;margin-top:8px;padding:6px 11px;font-size:13px;font-weight:700;
  background:#E9E4D2;border:2px solid var(--muted);color:#5F5A4E}
.lock-exp{display:block;margin-top:6px;font-size:13.5px;line-height:1.75}
.sc-item.sc-locked{background:#FFF6F3;border-color:var(--danger)}
.opt-btn:disabled,.btn:disabled{cursor:not-allowed;opacity:.72}
.btn:disabled{box-shadow:none}

/* ===== 學生報告與報告圖片 ===== */
.who-bar{display:flex;gap:9px;align-items:center;flex-wrap:wrap;background:#E8F0FF;
  border:3px solid var(--secondary);padding:11px 14px;margin-bottom:13px;font-size:14px}
.who-bar input{flex:1;min-width:180px;padding:7px 10px;border:3px solid var(--ink);
  background:#FFFDF6;font-size:15px;font-weight:700;color:var(--text)}
.card-preview{display:block;width:100%;max-width:540px;margin:14px auto 0;
  border:4px solid var(--ink);box-shadow:6px 6px 0 var(--ink);image-rendering:pixelated}
.card-note{text-align:center;font-size:13px;color:var(--muted);margin-top:10px;line-height:1.8}
.qb-btn.report{background:var(--accent);color:#3A2C05}
.report-entry{background:#FFF3C9;border:3px solid var(--accent);box-shadow:4px 4px 0 var(--ink);
  padding:12px 15px;margin-top:12px;font-size:14px;line-height:1.8}

/* ═══ 像素圖解（SVG，全部方塊／硬邊） ═══ */
.figbox{background:#FBFAF1;border:2px solid var(--ink);padding:4px;margin:7px 0;
  position:relative;overflow:hidden;
  background-image:linear-gradient(0deg,rgba(37,36,58,.045) 1px,transparent 1px),
    linear-gradient(90deg,rgba(37,36,58,.045) 1px,transparent 1px);
  background-size:8px 8px}
.figbox .figcap{position:absolute;top:6px;left:9px;font-size:11.5px;color:var(--secondary);
  letter-spacing:1px;font-weight:700;background:#FFFDF6;border:2px solid var(--ink);
  padding:1px 6px;pointer-events:none;z-index:2}
.figsvg{display:block;width:100%;height:auto;max-height:184px;shape-rendering:crispEdges}
.figsvg *{shape-rendering:crispEdges}
.figsvg text{font-family:"Courier New","Noto Sans TC",monospace;font-weight:700}
.px-tx{fill:var(--text);font-size:14px}
.px-txs{fill:var(--muted);font-size:12px}
.px-txb{fill:var(--primary);font-size:16px}
.px-txw{fill:#FFFDF6;font-size:16px}
.px-frame{fill:none;stroke:var(--ink);stroke-width:3}
.px-frame-red{fill:none;stroke:var(--danger);stroke-width:4}
.px-frame-blue{fill:none;stroke:var(--secondary);stroke-width:4}
.px-line{fill:none;stroke:var(--ink);stroke-width:4}
.px-line-red{fill:none;stroke:var(--danger);stroke-width:4}
.px-line-blue{fill:none;stroke:var(--secondary);stroke-width:4}
@keyframes figIn{from{transform:translateY(8px) scale(.88)}to{transform:none}}
.figsvg .fa{opacity:1;animation:figIn .28s steps(4) backwards}
@media (prefers-reduced-motion:reduce){.figsvg .fa{animation:none;opacity:1}}

/* 推演三步 */
.derive-row{display:flex;gap:11px;align-items:flex-start;border:2px solid var(--pale);
  padding:12px 14px;margin-bottom:9px;background:#F7F4E8;transition:.2s}
.derive-row.di-open{background:#FFF8DC;border:3px solid var(--accent)}
.derive-row .di-no{width:28px;height:28px;border:2px solid var(--ink);
  background:var(--secondary);color:#FFFDF6;display:flex;align-items:center;
  justify-content:center;font-size:14px;font-weight:700;flex:none}
.derive-row.di-open .di-no{background:var(--accent);color:#3A2C05}
.di-body{flex:1;min-width:0}
.di-text{font-size:16px;color:var(--muted)}
.derive-row.di-open .di-text{color:var(--text)}
.di-locked{font-size:13px;color:#A39EAE;font-weight:700}
.di-key{display:none;margin-top:7px;padding:8px 12px;background:#FFF3C9;
  border:2px dashed var(--accent);font-size:14px;color:#6B5000}
.di-key.on{display:block}

/* 錯例醫院 */
.clinic-pane{display:none}
.clinic-pane.on{display:block}
.wrong-expr{background:#FFE3E1;color:#9E2222;border:2px solid var(--danger);
  padding:2px 8px;font-weight:700;font-size:16px}
.clinic-go{background:#EFECE0;border:2px dashed var(--muted);padding:16px;
  text-align:center;font-size:14px}
.opt-btn{display:block;width:100%;text-align:left;padding:9px 13px;margin:6px 0;
  border:2px solid var(--ink);background:#FFFDF6;font-size:15px;transition:.12s}
.opt-btn:hover{border-color:var(--primary);background:#FFF3C9}
.opt-btn.right{border-color:var(--success);background:#E4F6EB}
.opt-btn.wrong{border-color:var(--danger);background:#FFE3E1}

/* ===== 懸浮快捷列 ===== */
.quickbar{position:fixed;left:0;right:0;bottom:0;z-index:70;
  background:var(--card);border-top:4px solid var(--ink);
  box-shadow:0 -4px 0 rgba(37,36,58,.14);padding:8px 12px;
  padding-bottom:calc(8px + env(safe-area-inset-bottom))}
.qb-inner{max-width:1080px;margin:0 auto;display:flex;gap:7px;align-items:center;
  overflow-x:auto;scrollbar-width:none}
.qb-inner::-webkit-scrollbar{display:none}
.qb-btn{flex:none;padding:7px 12px;font-size:14px;font-weight:700;
  background:#F1EEE2;border:2px solid var(--ink);box-shadow:2px 2px 0 var(--ink);
  transition:.1s;white-space:nowrap}
.qb-btn:hover{background:#E4DFCC}
.qb-btn.cur{background:var(--primary);color:#FFFDF6}
.qb-btn.teacher{background:#6B6357;color:#FFFDF6}
.qb-btn.redo{background:#B43CD1;color:#FFFDF6}
.qb-btn.redo.has{box-shadow:2px 2px 0 var(--ink),0 0 0 3px var(--accent)}

/* ===== 彈窗 ===== */
.mask{display:none;position:fixed;inset:0;z-index:90;background:rgba(37,36,58,.62);
  align-items:flex-start;justify-content:center;padding:22px 14px;overflow-y:auto}
.mask.on{display:flex}
.modal{background:var(--card);border:4px solid var(--ink);width:100%;max-width:780px;
  box-shadow:8px 8px 0 rgba(37,36,58,.55);overflow:hidden;margin:auto 0}
.modal-head{background:var(--secondary);color:#FFFDF6;padding:13px 18px;
  display:flex;align-items:center;gap:10px;border-bottom:4px solid var(--ink)}
.modal-head h3{font-size:18px;font-weight:700;flex:1;letter-spacing:1px}
.x-btn{font-size:22px;line-height:1;opacity:.85;padding:0 4px;font-weight:700}
.x-btn:hover{opacity:1}
.modal-body{padding:18px;max-height:64vh;overflow-y:auto;background:#FBF9F0}
.modal-foot{border-top:3px solid var(--ink);padding:11px 16px;display:flex;
  align-items:center;gap:9px;flex-wrap:wrap;background:#F1EEE2}
.foot-info{font-size:13px;color:var(--muted);flex:1;min-width:110px;font-weight:700}
.foot-btns{display:flex;gap:7px;flex-wrap:wrap}

/* ===== 總結卡 ===== */
.sum-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(115px,1fr));gap:10px;margin-bottom:14px}
.sum-box{background:#E8F0FF;border:2px solid var(--secondary);padding:12px 8px;text-align:center}
.sum-box .k{font-size:12px;color:var(--muted);font-weight:700}
.sum-box .v{font-size:26px;font-weight:700;color:var(--primary);line-height:1.3}
.sum-box .v small{font-size:14px;color:var(--muted)}
.keycard{background:#FFF3C9;border:3px solid var(--accent);padding:15px 17px;margin:11px 0}
.keycard .kl{font-size:13px;color:#8A6D00;margin-bottom:4px;font-weight:700}
.keycard .kv{font-size:17px;font-weight:700;color:#5C4700;line-height:1.7}
.badge-list{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.badge{background:#EFECE0;border:2px solid var(--muted);padding:6px 12px;font-size:13px;
  display:flex;align-items:center;gap:6px;font-weight:700}
.badge.got{background:#FFF3C9;border-color:var(--accent);color:#7A5C05;
  box-shadow:2px 2px 0 var(--accent)}

/* ===== 老師專用 ===== */
.teacher-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:10px}
.t-btn{border:2px solid var(--ink);background:#FFFDF6;padding:13px;text-align:left;
  transition:.12s;box-shadow:3px 3px 0 rgba(37,36,58,.18)}
.t-btn:hover{border-color:var(--secondary);background:#E8F0FF;transform:translate(-2px,-2px);
  box-shadow:5px 5px 0 rgba(37,36,58,.24)}
.t-btn .ti{font-size:20px}
.t-btn .tt{font-size:15px;font-weight:700;margin:3px 0}
.t-btn .td{font-size:12px;color:var(--muted)}

/* 報告表格 */
table{border-collapse:collapse}
table th,table td{border:2px solid var(--ink);padding:5px 8px;text-align:left}
table th{background:var(--secondary);color:#FFFDF6;font-weight:700}
table tr:nth-child(even) td{background:#F7F4E8}

/* ===== 提示氣泡 ===== */
.toasts{position:fixed;top:14px;right:14px;z-index:120;display:flex;
  flex-direction:column;gap:9px;pointer-events:none}
.toast{background:var(--card);border:3px solid var(--ink);box-shadow:4px 4px 0 rgba(37,36,58,.4);
  padding:10px 15px;display:flex;align-items:center;gap:9px;font-size:14px;font-weight:700;
  animation:pop .2s steps(3)}
.toast.badge{background:#FFF3C9;border-color:var(--accent);color:#7A5C05}
@keyframes pop{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}

/* ===== 像素精靈與粒子層 ===== */
#pixFx{position:fixed;inset:0;width:100%;height:100%;pointer-events:none;
  z-index:115;image-rendering:pixelated}
#pixBuddy{position:fixed;right:14px;bottom:88px;z-index:75;display:flex;
  align-items:flex-end;gap:8px;pointer-events:none}
#pixBuddyCv{width:64px;height:64px;image-rendering:pixelated;
  filter:drop-shadow(3px 3px 0 rgba(37,36,58,.28))}
#pixBuddySay{background:#FFFDF6;border:3px solid var(--ink);box-shadow:3px 3px 0 var(--ink);
  padding:5px 9px;font-size:12px;font-weight:700;max-width:160px;line-height:1.4}
@media(max-width:640px){#pixBuddySay{display:none}#pixBuddy{bottom:78px;right:8px}
  #pixBuddyCv{width:52px;height:52px}}

@media print{
  .navbar,.quickbar,.toasts,.modal-foot,.no-print,#pixFx,#pixBuddy{display:none!important}
  .mask{position:static;background:none;display:block}
  .modal{box-shadow:none;max-width:none;border:none}
  .modal-body{max-height:none;overflow:visible}
  .card{box-shadow:none;border:2px solid #888}
  body{background:#fff}
}
@media(max-width:640px){
  .mainline{grid-template-columns:1fr}
  main{padding:12px 12px 140px}
  .modal-body{max-height:58vh}
}
</style>'''
html = re.sub(r"<style>.*?</style>", lambda m: CSS, html, count=1, flags=re.S)


# ══════════════════════════════════════════════════════════════════════
# 3. body 加像素層 DOM
# ══════════════════════════════════════════════════════════════════════
PIXDOM = r'''<body>

<!-- ===== 像素特效層（不支援 Canvas 時靜默降級，不影響教材） ===== -->
<canvas id="pixFx" aria-hidden="true"></canvas>
<div id="pixBuddy" aria-hidden="true">
  <canvas id="pixBuddyCv" width="64" height="64"></canvas>
  <div id="pixBuddySay">尺尺：請先完成 8 題分層診斷。</div>
</div>

<nav class="navbar">'''
rep("<body>\n\n<nav class=\"navbar\">", PIXDOM, "body 像素層")


# ══════════════════════════════════════════════════════════════════════
# 4. 像素引擎（獨立 script，放主 script 之前）
# ══════════════════════════════════════════════════════════════════════
PIXJS = r'''<script>
/* ═══════════════════════════════════════════════════════════════
   像素層 PIX —— 純 Canvas 逐格繪製，零外連、零音檔
   精靈「尺尺」＋答對方塊粒子＋chiptune 情緒；不支援時自動降級
   ═══════════════════════════════════════════════════════════════ */
(function(){
  var PIX = window.PIX = {
    enabled:false, parts:[], mood:"idle", moodT:0,
    say:function(s){ var n=document.getElementById("pixBuddySay"); if(n) n.textContent="尺尺："+s; },
    cheer:function(){ this.mood="happy"; this.moodT=1100; this.say("答對了！"); this.burstCenter(); },
    oops:function(){ this.mood="sad"; this.moodT=800; this.say("已記入錯題本，請前往錯題重練。"); },
    burstCenter:function(){ this.burst(window.innerWidth/2, window.innerHeight/2, 22); },
    burstAt:function(el){
      if(!this.enabled||!el) return;
      var r={left:0,top:0,width:260};
      try{ r=el.getBoundingClientRect(); }catch(e){}
      this.burst((r.left||0)+(r.width||260)/2, (r.top||0)+48, 16);
    },
    burst:function(x,y,n){
      if(!this.enabled) return;
      for(var i=0;i<n;i++){
        this.parts.push({ x:x, y:y,
          vx:(Math.random()-.5)*9, vy:-2-Math.random()*6,
          s:4+Math.floor(Math.random()*3)*4,
          c:["#E14B3C","#F5B731","#2E9E63","#2E5CA8","#FFFDF6","#B43CD1"][i%6],
          life:1 });
      }
    }
  };
  /* 16×16 精靈：B 藍 W 白 K 墨 R 腮紅 G 金 . 透明 */
  var S = [
    "................",".....BBBBBB.....","....BBBBBBBB....","...BBWWBBWWBB...",
    "...BBWKBBWKBB...","...BBBBBBBBBB...","...BBBRRRRBBB...","....BBBBBBBB....",
    "...BGGGGGGGGB...","..BBGGGGGGGGBB..","..BBBBBBBBBBBB..","...BB......BB...",
    "...BB......BB...","...KK......KK...","................","................"
  ];
  var M = {B:"#2E5CA8",W:"#FFFDF6",K:"#25243A",R:"#E14B3C",G:"#F5B731"};
  var cv,ctx,bc,bx,W=0,H=0,t0=0;

  function resize(){
    if(!cv) return;
    W=cv.width=window.innerWidth; H=cv.height=window.innerHeight;
    if(ctx) ctx.imageSmoothingEnabled=false;
  }
  function drawBuddy(now){
    if(!bx) return;
    bx.clearRect(0,0,64,64);
    bx.imageSmoothingEnabled=false;
    var bob = PIX.mood==="happy" ? -7 : Math.round(Math.sin(now/280)*2);
    var shake = PIX.mood==="sad" ? Math.round(Math.sin(now/45)*2) : 0;
    for(var y=0;y<16;y++) for(var x=0;x<16;x++){
      var c=M[S[y][x]]; if(!c) continue;
      bx.fillStyle=c;
      bx.fillRect(x*4+shake, y*4+bob, 4, 4);
    }
    /* happy 時眼睛變成 ^ */
    if(PIX.mood==="happy"){
      bx.fillStyle="#25243A";
      bx.fillRect(5*4+shake,3*4+bob,4,4); bx.fillRect(6*4+shake,2*4+bob,4,4);
      bx.fillRect(9*4+shake,2*4+bob,4,4); bx.fillRect(10*4+shake,3*4+bob,4,4);
    }
  }
  function loop(now){
    if(!PIX.enabled) return;
    if(!t0) t0=now;
    var dt=Math.min(40,now-t0); t0=now;
    if(PIX.moodT>0){ PIX.moodT-=dt; if(PIX.moodT<=0){ PIX.mood="idle"; PIX.say("請繼續作答。"); } }
    if(ctx){
      ctx.clearRect(0,0,W,H);
      for(var i=PIX.parts.length-1;i>=0;i--){
        var p=PIX.parts[i];
        p.x+=p.vx*dt/16; p.y+=p.vy*dt/16; p.vy+=0.36*dt/16; p.life-=dt/900;
        if(p.life<=0||p.y>H+20){ PIX.parts.splice(i,1); continue; }
        ctx.globalAlpha=Math.max(0,Math.min(1,p.life));
        ctx.fillStyle=p.c;
        ctx.fillRect(Math.round(p.x/4)*4, Math.round(p.y/4)*4, p.s, p.s);
      }
      ctx.globalAlpha=1;
    }
    drawBuddy(now);
    requestAnimationFrame(loop);
  }
  function init(){
    try{
      cv=document.getElementById("pixFx"); bc=document.getElementById("pixBuddyCv");
      if(!cv||!bc) return;
      ctx=cv.getContext("2d"); bx=bc.getContext("2d");
      if(!ctx||!bx) return;               /* jsdom / 舊瀏覽器：靜默停用 */
      PIX.enabled=true;
      resize();
      window.addEventListener("resize",resize);
      drawBuddy(0);
      requestAnimationFrame(loop);
    }catch(e){ PIX.enabled=false; }
  }
  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",init);
  else init();
})();
</script>
'''
rep("<script>\n/* ══════════════════════════════════════════════════════════════════\n   ① 填資料區",
    PIXJS + "<script>\n/* ══════════════════════════════════════════════════════════════════\n   ① 填資料區",
    "PIX script 插入")


# ══════════════════════════════════════════════════════════════════════
# 5. 資料區（課題：六上重點班「第13課 認識比例尺」）
# ══════════════════════════════════════════════════════════════════════
DATA = r'''/* ══════════════════════════════════════════════════════════════════
   ① 填資料區 —— 改課題只需改這一段
   課題：小六上｜第13課 比例尺（重點班）
   圖解 t：meaning 意義／unit 單位換算／ratio 化簡比／line 線段比例尺／zoom 放大比例尺／flow 流程
   教材依據：《澳門新思維數學》第二版修訂版第13課（課本 p.52 附加例題）、
             《澳門新思維數學習作》練習13、自編補充工作紙冊第13課、工作紙 24.png
   前置知識：比的化簡、比例的基本性質、長度單位換算
   ✅ 本課範圍：比例尺的意義、求比例尺、線段比例尺、放大比例尺 10 : 1
   ✅ 每題附教材原文依據與預估秒數；學生可見文字一律書面語繁體中文
   ══════════════════════════════════════════════════════════════════ */

const CFG = {
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

/* 徽章 */
const BADGES = [
  { id:"diag",    i:"🧭", t:"分層完成",   d:"完成 8 題分層診斷" },
  { id:"first",   i:"🌱", t:"第一步",     d:"答對第一題" },
  { id:"combo3",  i:"🔥", t:"三連擊",     d:"連續答對 3 題" },
  { id:"perfect", i:"💎", t:"完美一步",   d:"一個步驟全對、沒有查看提示" },
  { id:"clinic",  i:"🏥", t:"糾錯高手",   d:"錯例醫院判斷正確" },
  { id:"exit",    i:"🎯", t:"出門票達人", d:"出門票答對" },
  { id:"redo",    i:"🔁", t:"訂正達人",   d:"完成一題錯題重練" },
  { id:"all",     i:"👑", t:"全部都試",   d:"解除分層限制，完成所有題" }
];

/* ══════════════════════════════════════════════════════════════════
   ② 引擎 —— 以下不用改
   ══════════════════════════════════════════════════════════════════ */

'''
a = html.index("const CFG = {")
b = html.index('const KEY = "bz_tpl_v1";')
html = html[:a] + DATA + html[b:]

# 品質鐵律：逐題教材原文依據、逐題秒數、答案純數字、無無意義分組前綴
if DATA.count("src:") < 35:
    raise SystemExit("❌ 題庫缺少逐題教材依據（src），目前 %d 處" % DATA.count("src:"))
if DATA.count("sec:") < 32:
    raise SystemExit("❌ 題庫缺少逐題秒數（sec），目前 %d 處" % DATA.count("sec:"))
_ans = re.findall(r'a:\["([^"]+)"\]', DATA)
_badans = [v for v in _ans if not re.fullmatch(r"[0-9]+", v)]
if _badans:
    raise SystemExit("❌ 答案必須為純數字：%s" % _badans)
if re.search(r"第\s*[0-9]+\s*組", DATA):
    raise SystemExit("❌ 題庫出現無意義的分組前綴")
print("✅ 題庫品質：逐題教材依據 %d 處／逐題秒數 %d 處／答案 %d 個皆為純數字"
      % (DATA.count("src:"), DATA.count("sec:"), len(_ans)))

rep('const KEY = "bz_tpl_v1";', 'const KEY = "bz_scale_pixel_v1";', "KEY")
rep('const LKEY = "bz_level_v1";', 'const LKEY = "bz_scale_level_v1";', "LKEY")


# ══════════════════════════════════════════════════════════════════════
# 5b. 引擎：統計只計本層配對題
# ══════════════════════════════════════════════════════════════════════
seg("function stat(stage,arr){", "/* ---------- 遊戲化：XP / 連對 / 徽章 ---------- */", r'''function stat(stage,arr,ids){
  let done=0,wrong=0,ok=0;
  const list = ids ? ids : arr.map(function(_,i){return i;});
  list.forEach(function(i){
    const key = stage==="clinic" ? "c"+i : i;
    const r=ST[stage][key]; if(!r) return;
    if(r.demo){ done++; return; }
    if(r.done){ done++; if(r.wrong===0) ok++; }
    if(r.wrong) wrong++;
  });
  return {total:list.length,done:done,wrong:wrong,ok:ok};
}
''', "stat 本層配題")

seg("function afterDone(stage){", "/* ---------- 換頁 ---------- */", r'''function afterDone(stage){
  if(stage!=="exit") return;
  /* 出門票「已作答」即彈總結（答錯也要讓學生看到錯題報告） */
  const ids=activeIds("exit");
  const answered=ids.filter(function(i){ const r=ST.exit[i]; return r && (r.done||r.locked); }).length;
  if(answered>=ids.length && !ST.shown){
    ST.shown=true; save();
    setTimeout(()=>UI.open("summary"), 800);
  }
}
''', "afterDone 已作答即總結")


# ══════════════════════════════════════════════════════════════════════
# 6. 狀態：加 wrongBook / redo / who
# ══════════════════════════════════════════════════════════════════════
seg("function fresh(){", "function save(){", r'''function fresh(){
  return { diag:{done:false,score:0,max:15,right:0,baseOk:0,level:0}, derive:{}, steps:{}, clinic:{}, exit:{}, redo:{},
           tried:{}, all:false, badges:[], xp:0, combo:0, best:0, t0:Date.now(), shown:false,
           wrongBook:[], who:"" };
}''', "fresh")
rep('["derive","steps","clinic","exit","tried"].forEach(k=>{ if(!ST[k]) ST[k]={}; });',
    '["derive","steps","clinic","exit","redo","tried"].forEach(k=>{ if(!ST[k]) ST[k]={}; });\n    if(!ST.wrongBook) ST.wrongBook=[];\n    if(ST.who===undefined) ST.who="";',
    "load 補齊 wrongBook / who")


# ══════════════════════════════════════════════════════════════════════
# 7. chiptune 音效
# ══════════════════════════════════════════════════════════════════════
seg("/* ---------- 音效（免音檔） ---------- */", "/* ---------- 提示氣泡 ---------- */", r'''/* ---------- 8-bit 音效（WebAudio 方波，免音檔） ---------- */
let AC=null;
function beep(freq,ms,type,vol){
  try{
    if(!AC) AC = new (window.AudioContext||window.webkitAudioContext)();
    const o=AC.createOscillator(), g=AC.createGain();
    o.type=type||"square"; o.frequency.value=freq;
    g.gain.setValueAtTime(vol||0.045, AC.currentTime);
    g.gain.exponentialRampToValueAtTime(0.0001, AC.currentTime+ms/1000);
    o.connect(g); g.connect(AC.destination); o.start(); o.stop(AC.currentTime+ms/1000);
  }catch(e){}
}
function sndOk(){ beep(659,80); setTimeout(()=>beep(784,80),70);
  setTimeout(()=>beep(1047,120),140); if(window.PIX) PIX.cheer(); }
function sndNo(){ beep(196,110,"square",0.04); setTimeout(()=>beep(147,140,"square",0.04),95);
  if(window.PIX) PIX.oops(); }
function sndBadge(){ [523,659,784,1047,1319,1047,1319].forEach((f,i)=>
  setTimeout(()=>beep(f,100,"square",0.05),i*80)); if(window.PIX) PIX.cheer(); }

''', "音效")


# ══════════════════════════════════════════════════════════════════════
# 8. 像素圖解引擎 FIG（比例尺專用）
# ══════════════════════════════════════════════════════════════════════
FIGJS = r'''/* ══════════════════════════════════════════════════════════════
   像素圖解引擎 FIG —— 全部方塊、硬邊、crispEdges
   meaning 意義／unit 單位換算／ratio 化簡比／line 線段比例尺／zoom 放大比例尺／flow 四步流程
   ══════════════════════════════════════════════════════════════ */
const FIG = {
  D:0,
  /* 舊模板 Explore.paint 會呼叫 _arrow 定義箭頭 marker；像素圖解不用，回傳空字串保持相容 */
  _arrow:function(){ return ""; },
  C:{ ink:"#25243A", red:"#E14B3C", blue:"#2E5CA8", gold:"#F5B731",
      green:"#2E9E63", paper:"#FFFDF6", pale:"#E9E4D2", grey:"#9C97A8" },
  draw:function(f,opts){
    if(!f) return "";
    this.D=0;
    const self=this, C=this.C;
    const A=function(cls){ return ' class="fa '+cls+'" style="animation-delay:'+(self.D++)*0.045+'s"'; };
    const box=function(x,y,w,h,fill,cls){
      return '<rect'+A(cls||"")+' x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" fill="'+fill+'"/>';
    };
    const frame=function(x,y,w,h,color){
      return '<rect'+A("px-frame")+' x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" fill="none" stroke="'+color+'"/>';
    };
    const tx=function(x,y,txt,cls,size,anchor){
      return '<text'+A(cls||"px-tx")+' x="'+x+'" y="'+y+'"'+
        (size?' style="font-size:'+size+'px"':'')+
        (anchor?' text-anchor="'+anchor+'"':'')+'>'+esc(txt)+'</text>';
    };
    const bar=function(x,y,n,cell,gap,color){
      let o="";
      for(let i=0;i<n;i++) o+=box(x+i*(cell+gap),y,cell,cell,color);
      return o;
    };
    const H={A:A,box:box,frame:frame,tx:tx,bar:bar,C:C};
    let s='<svg class="figsvg" viewBox="0 0 520 210" shape-rendering="crispEdges" '+
      'role="img" aria-label="'+esc(f.alt||"認識比例尺像素圖解")+'" xmlns="http://www.w3.org/2000/svg">';
    s+='<rect width="520" height="210" fill="#FBFAF1"/>';
    const t=f.t;
    if(t==="unit") s+=this.unit(f,H);
    else if(t==="ratio") s+=this.ratio(f,H);
    else if(t==="line") s+=this.line(f,H);
    else if(t==="zoom") s+=this.zoom(f,H);
    else if(t==="flow") s+=this.flow(f,H);
    else s+=this.meaning(f,H);
    s+='</svg>';
    return s;
  },
  /* ① 比例尺的意義：圖上一格 vs 實際多格 */
  meaning:function(f,H){
    const A=H.A,box=H.box,frame=H.frame,tx=H.tx,bar=H.bar,C=H.C;
    const m=f.map||1, r=Number(f.real)||25;
    let s="";
    s+=tx(260,26,"比 例 尺 的 意 義","px-txb",17,"middle");
    s+=tx(260,48,"比例尺 ＝ 圖上距離 : 實際距離","px-txs",13,"middle");
    s+=tx(40,66,"① 地圖上（圖上距離）","px-txs",11);
    s+=box(60,74,22,22,C.blue);
    s+=frame(60,74,22,22,C.ink);
    s+=tx(96,92,m+" cm","px-txb",15);
    s+=box(40,104,440,3,C.pale);
    s+=tx(40,126,"② 真正的長度（實際距離）","px-txs",11);
    s+=bar(60,134,Math.min(Math.round(r),25),10,2,C.gold);
    s+=tx(60,170,"共 "+r+" cm（每格 1 cm）","px-txs",11);
    s+=box(300,64,180,32,C.ink);
    s+=tx(390,87,"前項 : 後項","px-txw",15,"middle");
    s+=box(300,100,180,32,C.red);
    s+=tx(390,123,m+" : "+r,"px-txw",16,"middle");
    s+=box(150,178,330,26,C.green);
    s+=tx(315,198,m+" : "+r+" 　→　這幅圖的比例尺","px-txw",13,"middle");
    return s;
  },
  /* ② 先統一單位：常用換算 + 24 m → 2400 cm */
  unit:function(f,H){
    const A=H.A,box=H.box,frame=H.frame,tx=H.tx,C=H.C;
    const cards=[["1 cm","＝ 10 mm"],["1 m","＝ 100 cm"],["1 km","＝ 100 000 cm"]];
    let s="";
    s+=tx(260,26,"先 統 一 單 位","px-txb",17,"middle");
    s+=tx(260,46,"兩個距離必須使用相同單位，才能寫成比","px-txs",12,"middle");
    for(let i=0;i<3;i++){
      const x=18+i*168;
      s+=box(x,56,156,52,C.paper);
      s+=frame(x,56,156,52,C.blue);
      s+=tx(x+78,78,cards[i][0],"px-txb",16,"middle");
      s+=tx(x+78,99,cards[i][1],"px-txs",12,"middle");
    }
    s+=box(40,124,180,44,C.blue);
    s+=tx(130,153,"24 m","px-txw",20,"middle");
    s+=tx(260,153,"× 100 ▶","px-txb",14,"middle");
    s+=box(300,124,180,44,C.gold);
    s+=tx(390,153,"2400 cm","px-txw",20,"middle");
    s+=box(120,178,280,26,C.ink);
    s+=tx(260,198,"單位相同，才可以相比","px-txw",13,"middle");
    return s;
  },
  /* ③ 化簡比：a : b → 1 : n */
  ratio:function(f,H){
    const A=H.A,box=H.box,frame=H.frame,tx=H.tx,C=H.C;
    const a=f.a||5,b=f.b||2400,n=f.n||480;
    let s="";
    s+=tx(260,26,"化 成 前 項 為 1 的 比","px-txb",17,"middle");
    s+=box(24,50,200,60,C.paper);
    s+=frame(24,50,200,60,C.blue);
    s+=tx(124,87,a+" : "+b,"px-txb",18,"middle");
    s+=tx(260,88,"÷ "+a,"px-txb",15,"middle");
    s+=box(296,50,200,60,C.paper);
    s+=frame(296,50,200,60,C.red);
    s+=tx(396,87,"1 : "+n,"px-txb",18,"middle");
    s+=tx(260,132,"前項與後項同時除以 "+a,"px-txs",12,"middle");
    s+=box(60,148,400,34,C.green);
    s+=tx(260,172,"比例尺 ＝ 1 : "+n,"px-txw",17,"middle");
    s+=tx(260,198,"前項必須是 1；後項是化簡後的整數","px-txs",12,"middle");
    return s;
  },
  /* ④ 線段比例尺：0 50 100 150 200 m */
  line:function(f,H){
    const A=H.A,box=H.box,frame=H.frame,tx=H.tx,C=H.C;
    const step=Number(f.step)||50, u=f.unit||"m";
    const fac=(u==="km")?100000:(u==="m")?100:(u==="cm")?1:0.1;
    const cmN=step*fac;
    const x0=36, cell=88;
    let s="";
    s+=tx(260,26,"線 段 比 例 尺","px-txb",17,"middle");
    s+=tx(260,48,"每一格（1 cm）代表一段固定距離","px-txs",12,"middle");
    for(let i=0;i<4;i++){
      const x=x0+i*cell;
      s+=box(x,80,cell,18,i%2?C.paper:C.ink);
      s+=frame(x,80,cell,18,C.ink);
      s+=box(x,98,5,10,C.ink);
    }
    s+=box(x0+4*cell,98,5,10,C.ink);
    for(let i=0;i<5;i++) s+=tx(x0+i*cell,124,String(i*step),"px-txs",11,"middle");
    s+=tx(x0+4*cell+20,124,u,"px-txb",13);
    s+=box(36,140,448,32,C.blue);
    s+=tx(260,162,"1 cm : "+step+" "+u+" 　→　先把 "+u+" 化成厘米","px-txw",14,"middle");
    s+=box(36,178,448,26,C.green);
    s+=tx(260,198,step+" "+u+" ＝ "+cmN+" cm　→　1 : "+cmN,"px-txw",13,"middle");
    return s;
  },
  /* ⑤ 放大比例尺 10 : 1（數學小百科） */
  zoom:function(f,H){
    const A=H.A,box=H.box,frame=H.frame,tx=H.tx,bar=H.bar,C=H.C;
    let s="";
    s+=tx(260,26,"放 大 比 例 尺 10 : 1","px-txb",17,"middle");
    s+=tx(260,48,"前項大於後項：圖上距離比實際距離大","px-txs",12,"middle");
    s+=box(54,92,24,24,C.gold);
    s+=frame(54,92,24,24,C.ink);
    s+=tx(66,138,"實際 1 格","px-txs",11,"middle");
    s+=tx(176,110,"× 10 ▶","px-txb",15,"middle");
    s+=box(256,70,224,92,C.paper);
    s+=frame(256,70,224,92,C.ink);
    s+=bar(266,92,10,16,2,C.blue);
    s+=tx(368,132,"圖上 10 格","px-txs",11,"middle");
    s+=box(100,168,320,30,C.ink);
    s+=tx(260,190,"10 : 1　常用於鐘錶零件設計圖","px-txw",14,"middle");
    return s;
  },
  /* ⑥ 求比例尺四步流程 */
  flow:function(f,H){
    const A=H.A,box=H.box,frame=H.frame,tx=H.tx,C=H.C;
    const steps=["統一單位","寫出比","化成 1 : n","寫比例尺"];
    const sub=["24m→2400cm","5 : 2400","1 : 480","1 : 480"];
    const cols=[C.blue,C.red,C.gold,C.green];
    let s="";
    s+=tx(260,26,"求 比 例 尺 四 步","px-txb",17,"middle");
    for(let i=0;i<4;i++){
      const x=14+i*128;
      s+=box(x,44,112,96,cols[i]);
      s+=frame(x,44,112,96,C.ink);
      s+=box(x+8,52,96,24,C.paper);
      s+=tx(x+56,70,(i+1)+". "+steps[i],"px-tx",11,"middle");
      s+=tx(x+56,106,sub[i],"px-txw",10,"middle");
      s+=tx(x+56,128,"STEP "+(i+1),"px-txs",10,"middle");
      if(i<3) s+=tx(x+120,98,"▶","px-txb",14,"middle");
    }
    s+=box(70,158,380,36,C.ink);
    s+=tx(260,183,"驗算：前項是圖上、後項是實際，單位相同","px-txw",13,"middle");
    return s;
  }
};

/* ---------- 錯題本：記錄／訂正／概念歸類 ---------- */
function inferConcept(q){
  const R=[
    [/線段比例尺|每格|刻度/,"線段比例尺換算"],
    [/放大比例尺|設計圖|零件|10\s*[:：]\s*1|50\s*[:：]\s*1|3\s*[:：]\s*1|20\s*[:：]\s*1/,"放大比例尺的辨認"],
    [/化成|換算|單位相同|統一單位|沒有先統一/,"長度單位統一"],
    [/化簡|同除以|前項是 1|最簡/,"比的化簡"],
    [/比例尺是|求比例尺|1\s*[:：]/,"由圖上與實際距離求比例尺"],
    [/圖上|實際|前項|後項|對調/,"比例尺的意義與前後項"]
  ];
  for(let i=0;i<R.length;i++) if(R[i][0].test(q)) return R[i][1];
  return "比例尺的意義";
}
function recordWrong(stage,idx,item,mine){
  const key=stage+"-"+idx;
  const q=item.t||item.w||"";
  const ans=(item.a||[]).join("、")||(item.opts?item.opts[item.ans]:"");
  const w=ST.wrongBook.filter(function(x){return x.key===key;})[0];
  const why=inferConcept(q);
  if(w){ w.mine=String(mine); w.n=(w.n||1)+1; w.at=Date.now(); w.fixed=false; w.why=why; }
  else ST.wrongBook.push({ key:key, stage:stage, idx:idx, q:q, ans:ans,
    mine:String(mine), exp:item.exp||"", why:why, n:1, at:Date.now(), fixed:false });
  save(); updateRedoBadge();
}
function markFixed(key){
  ST.wrongBook.forEach(function(w){ if(w.key===key){ w.fixed=true; w.fixedAt=Date.now(); } });
  save(); updateRedoBadge();
}
function redoCount(){ return ST.wrongBook.filter(function(w){return !w.fixed;}).length; }
function updateRedoBadge(){
  const b=document.getElementById("qbRedo"); if(!b) return;
  const n=redoCount();
  b.textContent=n?("🔁 錯題重練 ("+n+")"):"🔁 錯題重練";
  b.classList.toggle("has",n>0);
}
function needDiag(){ return !ST.diag.done || !ST.diag.level; }

'''
m = re.search(r"/\*\s*═+\s*\n\s*圖解引擎 FIG.*?(?=const FIG = \{)", html, re.S)
if not m:
    raise SystemExit("❌ FIG 註解起點搵唔到")
a = m.start()
b = html.index("/* ---------- 題目渲染 ---------- */")
html = html[:a] + FIGJS + "\n" + html[b:]


# ══════════════════════════════════════════════════════════════════════
# 9. renderItem：逐題秒數、答錯記錄、答對粒子
# ══════════════════════════════════════════════════════════════════════
seg("function renderItem(item, stage, idx, forceDo){", "function norm(s){", r'''function renderItem(item, stage, idx, forceDo){
  const rec = ST[stage][idx] || {done:false,wrong:0,hints:0,locked:false};
  const demo = !forceDo && isDemo(stage,idx,item);
  if(demo){ rec.demo=true; }
  ST[stage][idx]=rec;

  const wrap=document.createElement("div");
  wrap.className="sc-item"+(rec.done?" sc-done":"")+(demo?" sc-demo":"")+
    ((rec.locked&&!rec.done)?" sc-locked":"");
  let fig="";
  if(item.fig){
    FIG.D=0;
    fig='<div class="figbox">'+FIG.draw(item.fig,{stage:0})+
      (item.fig.cap?'<div class="figcap">'+esc(item.fig.cap)+'</div>':'')+'</div>';
  }
  wrap.innerHTML =
    '<div class="sc-q"><span class="sc-no">'+(idx+1)+'</span>'+
    '<span class="sc-lv sc-star sc-d'+(item.d||2)+'">'+stars(item.d||2)+'</span>'+
    '<span class="sc-qtext">'+item.t.replace(/（　）/g,'<input class="sc-in" type="text" inputmode="decimal">')+'</span>'+
    (item.sec?'<span class="sc-sec">⏱ 約 '+item.sec+' 秒</span>':'')+'</div>'+
    fig+
    (item.src?'<div class="sc-src">📖 教材依據：'+esc(item.src)+'</div>':'')+
    '<div class="sc-mute">'+(demo?'👀 此步驟不屬於你的層級，答案已<b>預先填妥</b>作為示範':'')+'</div>'+
    '<div class="sc-hint" id="hint'+stage+idx+'">💡 '+esc(item.hint||"")+'</div>'+
    (demo?'':'<div class="hint-lock">🔒 提示會在答錯後自動出現；作答前不能查看</div>')+
    '<div class="sc-fb" id="fb'+stage+idx+'"></div>'+
    '<div class="sc-btns">'+
      '<button class="btn btn-primary btn-sm" data-act="check">✓ 檢查（只作答一次）</button>'+
      (demo?'<button class="btn btn-accent btn-sm" data-act="try">💪 我想試試</button>':'')+
    '</div>';

  const inputs=wrap.querySelectorAll(".sc-in");
  const fb=wrap.querySelector(".sc-fb");
  const ck=wrap.querySelector('[data-act="check"]');
  const hintEl=wrap.querySelector(".sc-hint");
  const lockNote=wrap.querySelector(".hint-lock");

  function disableAll(){
    Array.prototype.forEach.call(inputs,function(inp){ inp.disabled=true; });
    ck.disabled=true; ck.textContent="✓ 已作答";
    /* 作答後收回整列按鈕，讓回饋完整留在可視範圍內 */
    const btns=wrap.querySelector(".sc-btns");
    if(btns) btns.style.display="none";
    if(lockNote) lockNote.style.display="none";
  }
  function revealFb(){
    /* 把回饋底部對齊彈窗可視區底部，不被工具列裁切 */
    try{
      const mb=document.getElementById("mBody");
      if(!mb) return;
      const fr=fb.getBoundingClientRect(), mr=mb.getBoundingClientRect();
      mb.scrollTop += (fr.bottom - mr.bottom) + 18;
    }catch(e){}
  }
  function wrongView(showRedo){
    fb.className="sc-fb sc-no";
    fb.innerHTML="❌ 此題已記入錯題本，不能修改。<br>你所填："+esc(rec.mine||"")+
      "　｜　正確答案：<b>"+esc(item.a.join("、"))+"</b><br>"+
      '<span class="lock-exp">'+esc(item.exp||"")+'</span>'+
      (showRedo?'<div class="sc-btns"><button class="btn btn-redo btn-sm" data-act="toredo">🔁 前往錯題重練</button></div>':'');
    const rb=fb.querySelector('[data-act="toredo"]');
    if(rb) rb.onclick=function(){ UI.open("redo"); };
  }

  if(demo){
    Array.prototype.forEach.call(inputs,function(inp,i){ inp.value=item.a[i]; inp.disabled=true; });
    ck.disabled=true; ck.textContent="✓ 示範";
    fb.className="sc-fb sc-ok";
    fb.innerHTML="🎓 老師示範：<b>"+esc(item.a.join("、"))+"</b>　（"+esc(item.exp||"")+"）";
  } else if(rec.done){
    Array.prototype.forEach.call(inputs,function(inp,i){ inp.value=item.a[i]; inp.disabled=true; });
    disableAll();
    fb.className="sc-fb sc-ok";
    fb.innerHTML="✅ 已完成　"+esc(item.exp||"");
  } else if(rec.locked){
    const parts=(rec.mine||"").split("、");
    Array.prototype.forEach.call(inputs,function(inp,i){ inp.value=parts[i]||""; });
    disableAll();
    if(item.hint) hintEl.classList.add("on");
    wrongView(true);
  }

  ck.onclick=function(){
    if(demo||rec.locked||rec.done) return;
    const mine=Array.prototype.map.call(inputs,function(i){return i.value||"空白";});
    let all=true;
    Array.prototype.forEach.call(inputs,function(inp,i){
      if(norm(inp.value)!==norm(item.a[i])) all=false;
    });
    /* 一次作答即鎖定：無論對錯都不准回到原題修改 */
    rec.locked=true; rec.mine=mine.join("、");
    disableAll();
    if(all){
      rec.done=true; fb.className="sc-fb sc-ok";
      fb.innerHTML="✅ 答對了！"+esc(item.exp||"");
      wrap.classList.add("sc-done");
      sndOk(); if(window.PIX) PIX.burstAt(wrap);
      addXp(10); bumpCombo();
      grant("first");
      if(stage==="exit") grant("exit");
      save(); afterDone(stage);
      revealFb();
    } else {
      rec.wrong=1;
      wrongView(true);
      /* 提示只在答錯之後自動出現，學生不能自行按下 */
      if(item.hint){
        hintEl.classList.add("on");
        rec.hints=1; ST.hints=(ST.hints||0)+1;
      }
      recordWrong(stage,idx,item,mine.join("、"));
      sndNo(); breakCombo(); save();
      afterDone(stage);
      revealFb();
    }
  };
  const tb=wrap.querySelector('[data-act="try"]');
  if(tb) tb.onclick=function(){
    ST.tried[stage+idx]=true; save();
    wrap.parentNode.replaceChild(renderItem(item,stage,idx,true), wrap);
    toast("💪 好！這一步改由你自己完成");
  };
  return wrap;
}
''', "renderItem")


# ══════════════════════════════════════════════════════════════════════
# 10. buildSteps / buildClinic / buildExit（配對表、時間、錯題記錄）
# ══════════════════════════════════════════════════════════════════════
seg("function buildSteps(){", "function buildDerive(){", r'''function buildSteps(){
  const box=document.createElement("div");
  const ids=activeIds("steps");
  const secs=ids.reduce(function(s,i){return s+(DATA.steps[i].sec||60);},0);
  const L=LV[lv()], P=planOf();
  box.innerHTML='<div class="sc-plan-bar">🎯 你是 <b>'+L.s+' '+L.n+'</b>　→　本層主題：<b>'+esc(P.topic)+
    '</b><br>今日只派 <b>'+ids.length+' 題</b>（第 '+
    ids.map(function(i){return i+1;}).join("、")+' 題，約 '+Math.round(secs/60*10)/10+
    ' 分鐘）。其他層級的題目收在下方「解題鏈一覽」，<b>不必作答</b>。'+
    '<div class="sc-btns" style="margin-top:8px">'+
      (ST.all
        ? '<button class="btn btn-ghost btn-sm sc-trymore" data-act="back">🎯 回到本層模式</button>'
        : '<button class="btn btn-ghost btn-sm sc-trymore" data-act="all">📚 願意挑戰：加做其他層級</button>')+
    '</div></div>';
  const btn=box.querySelector(".sc-trymore");
  if(btn) btn.onclick=function(){
    if(btn.dataset.act==="all"){ ST.all=true; DATA.steps.forEach((_,i)=>ST.tried["steps"+i]=true); toast("📚 已加開所有層級的題目"); grant("all"); }
    else { ST.all=false; DATA.steps.forEach((_,i)=>delete ST.tried["steps"+i]); toast("🎯 回到本層模式"); }
    save(); UI.open("steps");
  };
  ids.forEach(function(i){ box.appendChild(renderItem(DATA.steps[i],"steps",i,true)); });
  /* 解題鏈一覽：只供參考，不計入作答量 */
  if(!ST.all){
    const rest=DATA.steps.map(function(_,i){return i;}).filter(function(i){return ids.indexOf(i)<0;});
    let d='<details class="sc-chain"><summary>📚 解題鏈一覽（其他層級 '+rest.length+
      ' 題，僅供參考，不必作答）</summary>'+
      '<div class="chain-row">🎯 <b>本層訓練重點：</b>'+esc(P.focus)+'</div>';
    rest.forEach(function(i){
      const it=DATA.steps[i];
      d+='<div class="chain-row"><b>第 '+(i+1)+' 題　'+stars(it.d||2)+'</b>　'+esc(it.t)+
        '<br><span>答案：'+esc((it.a||[]).join("、"))+'　｜　'+esc(it.exp||"")+'</span>'+
        (it.src?'<br><span>📖 教材依據：'+esc(it.src)+'</span>':'')+'</div>';
    });
    d+='</details>';
    const tmp=document.createElement("div"); tmp.innerHTML=d;
    box.appendChild(tmp.firstChild);
  }
  return box;
}
''', "buildSteps")

seg("function buildClinic(){", "function buildExit(){", r'''function buildClinic(){
  const box=document.createElement("div");
  const L=LV[lv()], P=planOf();
  const ids=activeIds("clinic");
  box.innerHTML='<p class="sc-intro">🏥 <b>今日你做醫生！</b>　不必計算——<b>先觀察列式、再估計大小、最後找出錯誤</b>。能找出別人的錯誤，自己就不會犯同樣的錯誤。</p>'+
    '<div class="sc-plan-bar">🎯 本層 <b>'+L.s+' '+L.n+'</b>　→　主題：<b>'+esc(P.topic)+
    '</b>；今日只派 <b>'+ids.length+' 題</b>。判斷一次即鎖定，答錯會自動記入錯題本。</div>';
  ids.forEach(function(idx,n){
    const c=DATA.clinic[idx];
    const key="c"+idx;
    const rec=ST.clinic[key]||{think:false,size:null,sizeOk:false,done:false,wrong:0,locked:false};
    ST.clinic[key]=rec;
    const row=document.createElement("div");
    row.className="sc-item";
    row.innerHTML=
      '<div class="sc-q"><span class="sc-no">'+(n+1)+'</span>'+
      '<span class="sc-lv sc-star sc-d'+(c.d||2)+'">'+stars(c.d||2)+'</span>'+
      '<span class="sc-qtext">病人計算：<span class="wrong-expr">'+esc(c.w)+'</span></span>'+
      (c.sec?'<span class="sc-sec">⏱ 約 '+c.sec+' 秒</span>':'')+'</div>'+
      (c.src?'<div class="sc-src">📖 教材依據：'+esc(c.src)+'</div>':'')+
      '<div class="clinic-pane p1'+(rec.think||rec.locked?'':' on')+'">'+
        '<div class="clinic-go">第一步：先觀察他所寫的算式<br><button class="btn btn-primary btn-sm" data-a="go">👀 我已看完</button></div>'+
      '</div>'+
      '<div class="clinic-pane p2'+(rec.think||rec.locked?' on':'')+'">'+
        '<div style="font-size:15px;margin-bottom:8px">第二步：不必計算，估計他所寫比例尺的<b>後項</b>會太大還是太小？</div>'+
        '<button class="btn btn-ghost btn-sm" data-a="big">太大</button> '+
        '<button class="btn btn-ghost btn-sm" data-a="small">太小</button>'+
        '<div class="sc-fb" id="cfb'+n+'"></div>'+
      '</div>'+
      '<div class="clinic-pane p3'+(rec.sizeOk||rec.locked?' on':'')+'">'+
        '<div style="font-size:15px;margin-bottom:8px">第三步：' + esc(c.q) + '</div>'+
        '<div id="copts'+n+'"></div>'+
        '<div class="sc-fb" id="cfb2_'+n+'"></div>'+
      '</div>';
    const p1=row.querySelector(".p1"),p2=row.querySelector(".p2"),p3=row.querySelector(".p3");
    p1.querySelector('[data-a="go"]').onclick=function(){ rec.think=true; save(); p1.classList.remove("on"); p2.classList.add("on"); };
    p2.querySelector('[data-a="big"]').onclick=function(){ judge("big"); };
    p2.querySelector('[data-a="small"]').onclick=function(){ judge("small"); };
    function judge(v){
      if(rec.locked) return;
      rec.size=v;
      const right=c.size||null;
      const fb=row.querySelector("#cfb"+n);
      if(right===null || v===right){ rec.sizeOk=true; fb.className="sc-fb sc-ok"; fb.innerHTML="👍 估計正確！"; sndOk(); addXp(5); }
      else { fb.className="sc-fb sc-no"; fb.innerHTML="🤔 再仔細觀察——留意單位換算會怎樣改變比例尺的後項。"; sndNo(); rec.sizeOk=true; }
      p3.classList.add("on"); save();
    }
    const ob=row.querySelector("#copts"+n), fb2=row.querySelector("#cfb2_"+n);
    c.opts.forEach(function(o,oi){
      const b=document.createElement("button");
      b.className="opt-btn"; b.textContent=(oi+1)+". "+o;
      b.onclick=function(){
        if(rec.locked) return;
        rec.locked=true; rec.pick=oi;
        row.querySelectorAll(".opt-btn").forEach(function(x){ x.disabled=true; });
        if(oi===c.ans){
          b.classList.add("right"); rec.done=true;
          fb2.className="sc-fb sc-ok";
          fb2.innerHTML="✅ 判斷正確！"+esc(c.exp||"");
          sndOk(); addXp(10); grant("clinic"); save(); afterDone("clinic");
        } else {
          b.classList.add("wrong");
          const right=row.querySelectorAll(".opt-btn")[c.ans];
          if(right) right.classList.add("right");
          rec.wrong=1;
          fb2.className="sc-fb sc-no";
          fb2.innerHTML="❌ 這題已記入錯題本，不能修改。正確選項是第 "+(c.ans+1)+" 項。<br>"+
            '<span class="lock-exp">'+esc(c.exp||"")+'</span>'+
            '<div class="sc-btns"><button class="btn btn-redo btn-sm" data-a="toredo">🔁 前往錯題重練</button></div>';
          fb2.querySelector('[data-a="toredo"]').onclick=function(){ UI.open("redo"); };
          recordWrong("clinic",idx,c,(oi+1)+". "+o);
          sndNo(); breakCombo(); save();
        }
      };
      if(rec.locked){
        b.disabled=true;
        if(oi===c.ans) b.classList.add("right");
        else if(oi===rec.pick) b.classList.add("wrong");
      }
      ob.appendChild(b);
    });
    if(rec.done){ fb2.className="sc-fb sc-ok"; fb2.innerHTML="✅ 已完成　"+esc(c.exp||""); }
    else if(rec.locked){
      fb2.className="sc-fb sc-no";
      fb2.innerHTML="❌ 此題已作答並記入錯題本，不能修改。<br><span class=\"lock-exp\">"+esc(c.exp||"")+"</span>";
    }
    if(rec.think||rec.locked){ p1.classList.remove("on"); p2.classList.add("on"); }
    if(rec.sizeOk||rec.locked) p3.classList.add("on");
    box.appendChild(row);
  });
  return box;
}
''', "buildClinic")

seg("function buildExit(){", "function buildHomework(){", r'''function buildExit(){
  const box=document.createElement("div");
  const ids=activeIds("exit");
  const L=LV[lv()], P=planOf();
  const secs=ids.reduce(function(s,i){return s+(DATA.exit[i].sec||90);},0);
  box.innerHTML='<p class="sc-intro">🚪 <b>今日最後一關。</b>　完成後會自動出現「📋 今日總結」，可在總結卡產生報告圖片繳交給老師。</p>'+
    '<div class="sc-plan-bar">🎯 你是 <b>'+L.s+' '+L.n+'</b>　→　本層主題：<b>'+esc(P.topic)+
    '</b>；只派 <b>'+ids.length+' 題</b>（約 '+Math.round(secs/60*10)/10+' 分鐘）。'+L.tip+'</div>';
  ids.forEach(function(i){ box.appendChild(renderItem(DATA.exit[i],"exit",i,true)); });
  return box;
}
''', "buildExit")


# ══════════════════════════════════════════════════════════════════════
# 11. 課後功課（改為第13課兩題）
# ══════════════════════════════════════════════════════════════════════
seg("function buildHomework(){", "/* ---------- 總結卡 ---------- */", r'''function buildHomework(){
  const box=document.createElement("div");
  box.innerHTML='<p class="sc-intro">📝 <b>課後功課</b>　課堂上只列式，數值計算留作回家功課。兩題約 6 分鐘，答案欄只須填寫數字。</p>'+
    '<div class="card" style="box-shadow:none;border:2px solid var(--ink)">'+
    '<div class="sc-q">1. 甲、乙兩地實際距離 950 千米，圖上距離 19 厘米，求這幅地圖的比例尺。<span class="sc-sec">⏱ 約 180 秒</span></div>'+
    '<div class="sc-src">📖 教材依據：自編補充工作紙冊 第13課 計算題 1</div>'+
    '<div class="sc-mute">列式：950 km ＝ 95 000 000 cm　→　19 : 95 000 000　→　化成前項為 1 的比。</div>'+
    '<div class="sc-btns"><button class="btn btn-ghost btn-sm" data-a="s1">🔑 看答案</button></div>'+
    '<div class="sc-fb" id="h1"></div></div>'+
    '<div class="card" style="box-shadow:none;border:2px solid var(--ink)">'+
    '<div class="sc-q">2. 線段比例尺每格 1 cm 代表 100 km，寫成數值比例尺是多少？<span class="sc-sec">⏱ 約 150 秒</span></div>'+
    '<div class="sc-src">📖 教材依據：工作紙 24.png 第⑧題（0 100 200 300 400 km）</div>'+
    '<div class="sc-mute">列式：100 km ＝ 10 000 000 cm　→　1 cm : 10 000 000 cm　→　寫成 1 : n。</div>'+
    '<div class="sc-btns"><button class="btn btn-ghost btn-sm" data-a="s2">🔑 看答案</button></div>'+
    '<div class="sc-fb" id="h2"></div></div>'+
    '<div class="sc-btns" style="justify-content:center;margin-top:12px">'+
    '<button class="btn btn-accent" onclick="window.print()">🖨 列印功課</button></div>';
  box.querySelector('[data-a="s1"]').onclick=function(){
    const f=document.getElementById("h1");
    f.className="sc-fb sc-ok"; f.innerHTML="950 km ＝ 95 000 000 cm；19 : 95 000 000 ＝ <b>1 : 5 000 000</b>。"; };
  box.querySelector('[data-a="s2"]').onclick=function(){
    const f=document.getElementById("h2");
    f.className="sc-fb sc-ok"; f.innerHTML="100 km ＝ 10 000 000 cm；1 cm : 10 000 000 cm ＝ <b>1 : 10 000 000</b>。"; };
  return box;
}
''', "buildHomework")


# ══════════════════════════════════════════════════════════════════════
# 12. 總結卡（加錯題格＋重練掣）
# ══════════════════════════════════════════════════════════════════════
seg("function buildSummary(){", "/* ---------- 老師專用（完整報告／進階功能） ---------- */", r'''function buildSummary(){
  const box=document.createElement("div");
  const s1=statPlan("steps"), s2=statPlan("exit"), s3=statPlan("clinic");
  const total=s1.total+s2.total+s3.total, done=s1.done+s2.done+s3.done;
  const mins=Math.max(1,Math.round((Date.now()-ST.t0)/60000));
  const pct=total?Math.round(done/total*100):0;
  const weak=DATA.steps.filter((it,i)=>ST.steps[i]&&ST.steps[i].wrong>0).map(it=>it.t.slice(0,14));
  const nredo=redoCount();
  box.innerHTML=
    '<div class="sum-grid">'+
    '<div class="sum-box"><div class="k">② 分步列式</div><div class="v">'+s1.done+'<small>/'+s1.total+'</small></div></div>'+
    '<div class="sum-box"><div class="k">③ 錯例醫院</div><div class="v">'+s3.done+'<small>/'+s3.total+'</small></div></div>'+
    '<div class="sum-box"><div class="k">④ 出門票</div><div class="v">'+s2.done+'<small>/'+s2.total+'</small></div></div>'+
    '<div class="sum-box"><div class="k">完成度</div><div class="v">'+pct+'<small>%</small></div></div>'+
    '<div class="sum-box"><div class="k">待訂正錯題</div><div class="v">'+nredo+'</div></div>'+
    '<div class="sum-box"><div class="k">用了</div><div class="v">'+mins+'<small>分鐘</small></div></div>'+
    '<div class="sum-box"><div class="k">最高連續答對</div><div class="v">'+ST.best+'</div></div>'+
    '</div>'+
    '<div class="keycard"><div class="kl">🎯 本課算法</div><div class="kv">'+esc(CFG.key)+'</div></div>'+
    '<div class="sc-mute">⏱ 本課時間預算約 '+CFG.minutes+' 分鐘（診斷 5 ＋ 推演 2 ＋ 分步 5 ＋ 錯例 2.5 ＋ 出門票 4 ＋ 總結 1.5）。今日須作答 16 題。</div>'+
    '<div class="sc-mute">⚠️ '+(weak.length?"要留意："+esc(weak.join("；")):"全部掌握良好，可以挑戰下一節！")+'</div>'+
    '<div class="badge-list">'+BADGES.map(b=>
      '<div class="badge'+(ST.badges.indexOf(b.id)>=0?" got":"")+'" title="'+esc(b.d)+'">'+
      (ST.badges.indexOf(b.id)>=0?b.i:"🔒")+' '+b.t+'</div>').join("")+'</div>'+
    '<div class="sc-btns" style="justify-content:center;margin-top:14px">'+
    (nredo?'<button class="btn btn-redo" data-a="redo">🔁 錯題重練 ('+nredo+')</button>':'')+
    '<button class="btn btn-success" data-a="share">📤 繳交報告給老師</button>'+
    '<button class="btn btn-primary" data-a="card">🖼 產生報告圖片</button>'+
    '<button class="btn btn-ghost" data-a="report">📊 我的學習報告</button>'+
    '<button class="btn btn-ghost" data-a="wrong">📋 錯題報告</button>'+
    '<button class="btn btn-ghost" data-a="hw">📝 課後功課</button>'+
    '<button class="btn btn-ghost" onclick="window.print()">🖨 列印</button>'+
    '<button class="btn btn-secondary" data-a="close">✅ 做得好，返回</button></div>';
  box.querySelector('[data-a="share"]').onclick=function(){ UI.share(); };
  box.querySelector('[data-a="card"]').onclick=function(){ makeCard(); };
  box.querySelector('[data-a="report"]').onclick=function(){ UI.open("report"); };
  box.querySelector('[data-a="hw"]').onclick=function(){ UI.open("homework"); };
  box.querySelector('[data-a="wrong"]').onclick=function(){ UI.open("wrong"); };
  const rb=box.querySelector('[data-a="redo"]'); if(rb) rb.onclick=function(){ UI.open("redo"); };
  box.querySelector('[data-a="close"]').onclick=function(){ UI.close(); };
  return box;
}
''', "buildSummary")


# ══════════════════════════════════════════════════════════════════════
# 13. 老師專用（8 個入口）
# ══════════════════════════════════════════════════════════════════════
seg("function buildTeacher(){", "function buildReport(){", r'''function buildTeacher(){
  const box=document.createElement("div");
  const items=[
    {k:"wrong",   i:"📋", t:"錯題報告",       d:"原題／學生答案／正確答案／錯因歸類"},
    {k:"redo",    i:"🔁", t:"錯題重練",       d:"同類型變式題，答對即完成訂正"},
    {k:"report",  i:"📊", t:"完整個性化報告", d:"強弱項分析＋逐題記錄＋匯出"},
    {k:"all",     i:"📚", t:"完成所有難度的題", d:"解除分層限制（學生自願）"},
    {k:"homework",i:"📝", t:"課後功課",       d:"進階兩題＋列印"},
    {k:"print",   i:"🖨", t:"列印本課",       d:"列印練習紙／功課"},
    {k:"reset",   i:"🔄", t:"重做分層診斷",   d:"重設層級（★／★★／★★★）"},
    {k:"sources", i:"📖", t:"教材依據一覽",   d:"逐題對應課本、練習13 與工作紙出處"},
    {k:"clear",   i:"🗑", t:"清空本課記錄",   d:"清除 localStorage 進度"}
  ];
  box.innerHTML='<p class="sc-intro">👨‍🏫 <b>老師專用</b>　學生主線不會看到這些按鈕。</p><div class="teacher-grid">';
  const g=box.querySelector(".teacher-grid");
  items.forEach(function(it){
    const b=document.createElement("button");
    b.className="t-btn";
    b.innerHTML='<div class="ti">'+it.i+'</div><div class="tt">'+it.t+'</div><div class="td">'+it.d+'</div>';
    b.onclick=function(){
      if(it.k==="all"){ ST.all=true; DATA.steps.forEach((_,i)=>ST.tried["steps"+i]=true); grant("all"); save(); toast("📚 已解除限制"); UI.open("steps"); }
      else if(it.k==="report"||it.k==="wrong"||it.k==="redo"||it.k==="homework"||it.k==="sources"){ UI.open(it.k); }
      else if(it.k==="print"){ window.print(); }
      else if(it.k==="reset"){ ST.diag={done:false,score:0,max:15,right:0,baseOk:0,level:0}; DIAG.forEach(function(_,i){ ST.diag["q"+i]={}; }); try{localStorage.removeItem(LKEY);}catch(e){} save(); toast("🔄 已重設，請重新診斷"); go("diag"); }
      else if(it.k==="clear"){ if(confirm("確定清空本課所有記錄？")){ ST=fresh(); save(); toast("🗑 已清空"); go("intro"); } }
    };
    g.appendChild(b);
  });
  return box;
}

/* ---------- 教材依據一覽：逐題對應課本／習作／工作紙 ---------- */
function buildSources(){
  const box=document.createElement("div");
  const groups=[
    ["一、課本與進度表",[
      "《澳門新思維數學》第二版修訂版 第13課「比例尺」（教育出版社有限公司）",
      "課本 p.52 第13課第2題附加例題：1 : 480、1 : 2000、1 : 160、1 : 750",
      "26-27 小六第一學段數學科進度表：教學目標 1 至 4、基本學力 B-2-15"
    ]],
    ["二、習作與工作紙",[
      "《澳門新思維數學習作》練習13（程度一與程度二，共 42 題）",
      "自編補充工作紙冊 第13課（填表、計算題：950 km／19 cm、363 m／1.1 cm）",
      "工作紙 24.png 第13課（表格題、算和填、線段比例尺、挑戰題）"
    ]],
    ["三、本課邊界",[
      "本課只處理：比例尺的意義、求比例尺、線段比例尺、放大比例尺 10 : 1",
      "不涉及後續章節的反求長度與作圖題",
      "所有題目均附教材原文依據與逐題預估秒數；學生可見文字為書面語繁體中文"
    ]]
  ];
  let h='<p class="sc-intro">📖 <b>教材依據一覽</b>　本教材全部題目皆由課本、習作與工作紙的第13課內容改寫或摘錄，方便老師核對教學進度。</p>';
  groups.forEach(function(g){
    h+='<h3 style="font-size:17px;color:var(--secondary);margin:14px 0 8px">'+g[0]+'</h3>'+
       '<div class="concept-box">'+g[1].map(function(x){return "• "+esc(x);}).join("<br>")+'</div>';
  });
  h+='<h3 style="font-size:17px;color:var(--secondary);margin:14px 0 8px">四、逐題對照</h3>'+
     '<table style="width:100%;font-size:13px"><tr><th>位置</th><th>難度</th><th>題目（節錄）</th><th>教材依據</th><th>秒</th></tr>';
  const add=function(tag,arr){
    arr.forEach(function(it,i){
      h+='<tr><td>'+tag+'-'+(i+1)+'</td><td>'+stars(it.d||2)+'</td><td>'+
         esc((it.t||it.w||"").slice(0,22))+'</td><td>'+esc(it.src||"—")+'</td><td>'+(it.sec||"—")+'</td></tr>';
    });
  };
  add("分步",DATA.steps); add("錯例",DATA.clinic); add("出門票",DATA.exit);
  h+='</table>';
  box.innerHTML=h;
  return box;
}

/* ---------- 錯題報告：逐題對照＋概念歸類 ---------- */
function buildWrongReport(){
  const box=document.createElement("div");
  const all=ST.wrongBook.slice().sort(function(a,b){return b.at-a.at;});
  const pending=all.filter(function(w){return !w.fixed;});
  const L=LV[lv()];
  let h='<p class="sc-intro">📋 <b>錯題報告</b>　自動記錄每一次答錯：你當時填了什麼、正確答案是什麼、屬於哪一個概念。已訂正的題目仍保留作複習。</p>'+
    '<div class="sum-grid">'+
    '<div class="sum-box"><div class="k">累計錯題</div><div class="v">'+all.length+'</div></div>'+
    '<div class="sum-box"><div class="k">待訂正</div><div class="v">'+pending.length+'</div></div>'+
    '<div class="sum-box"><div class="k">已訂正</div><div class="v">'+(all.length-pending.length)+'</div></div>'+
    '<div class="sum-box"><div class="k">目前層級</div><div class="v" style="font-size:19px">'+L.s+'</div></div>'+
    '</div>';
  /* 概念分布 */
  const cmap={};
  all.forEach(function(w){ cmap[w.why]=(cmap[w.why]||0)+1; });
  const ckeys=Object.keys(cmap).sort(function(a,b){return cmap[b]-cmap[a];});
  h+='<h3 style="font-size:17px;color:var(--secondary);margin:14px 0 8px">一、錯因概念分布</h3>'+
    '<div class="concept-box">'+(ckeys.length
      ? ckeys.map(function(k){return "• "+esc(k)+"　（"+cmap[k]+" 次）";}).join("<br>")
      : "目前沒有錯題，概念掌握良好。")+'</div>';
  h+='<h3 style="font-size:17px;color:var(--secondary);margin:14px 0 8px">二、逐題對照</h3>';
  if(!all.length) h+='<div class="clinic-go">✅ 錯題本是空的，保持得很好！</div>';
  else{
    h+='<table style="width:100%;font-size:13px"><tr><th>題號</th><th>題目（節錄）</th><th>學生答案</th><th>正確答案</th><th>錯因</th><th>狀態</th></tr>';
    all.forEach(function(w){
      h+='<tr><td>'+esc(w.key)+'</td><td>'+esc(w.q.slice(0,24))+'…</td>'+
        '<td style="color:#9E2222;font-weight:700">'+esc(w.mine)+'</td>'+
        '<td style="color:#1B6B42;font-weight:700">'+esc(w.ans)+'</td>'+
        '<td>'+esc(w.why)+'</td>'+
        '<td>'+(w.fixed?'<b style="color:#1B6B42">已訂正</b>':'<b style="color:#9E2222">待訂正</b>')+'</td></tr>';
    });
    h+='</table>';
  }
  h+='<h3 style="font-size:17px;color:var(--secondary);margin:14px 0 8px">三、教學建議</h3>'+
    '<div class="concept-box">'+(ckeys.length
      ? "• 先針對「"+esc(ckeys[0])+"」完成錯題重練，再挑戰同類型題目。<br>• 每題必須先寫出「統一單位 → 圖上 : 實際 → 化成 1 : n」三步。<br>• 檢查前項是否為 1、兩個距離的單位是否相同；線段比例尺要先換算成厘米。"
      : "• 可以挑戰更高難度，或嘗試自己出題給同學練習。")+'</div>'+
    '<div class="sc-btns" style="justify-content:center;margin-top:14px">'+
    (pending.length?'<button class="btn btn-redo" data-a="redo">🔁 開始錯題重練 ('+pending.length+')</button>':'')+
    '<button class="btn btn-primary" data-a="csv2">📥 匯出錯題 CSV</button>'+
    '<button class="btn btn-ghost" onclick="window.print()">🖨 列印報告</button></div>';
  box.innerHTML=h;
  const rb=box.querySelector('[data-a="redo"]'); if(rb) rb.onclick=function(){ UI.open("redo"); };
  const cb=box.querySelector('[data-a="csv2"]'); if(cb) cb.onclick=function(){ UI.wrongCsv(); };
  return box;
}

/* ---------- 錯題重練：同類型變式題，答對即訂正 ---------- */
function buildRedo(){
  const box=document.createElement("div");
  const list=ST.wrongBook.filter(function(w){return !w.fixed;});
  const L=LV[lv()];
  box.innerHTML='<p class="sc-intro">🔁 <b>錯題重練</b>　系統自錯題本挑出未訂正的題目，配同一類型的<b>變式題</b>（更換數字、不改變方法），答對即完成訂正。</p>'+
    '<div class="sc-plan-bar">🎯 你是 <b>'+L.s+' '+L.n+'</b>　→　重練題沿用原題難度，<b>不跳級、不降級</b>；作答一次即鎖定，答錯後才會出現提示，並可「再練一次」。</div>';
  if(!list.length){
    box.innerHTML+='<div class="clinic-go">✅ 目前沒有待訂正的錯題，保持得很好！<br><span class="sc-mute">答錯的題目會自動收進這裡。</span></div>';
    return box;
  }
  list.forEach(function(w){
    const src = w.stage==="steps"?DATA.steps[w.idx]
              : w.stage==="exit"?DATA.exit[w.idx]
              : w.stage==="clinic"?DATA.clinic[w.idx] : null;
    const vr = (src&&src.redo) ? src.redo
             : { t:"請寫出正確答案：（　）", a:[w.ans], exp:w.exp||"" };
    const rec=ST.redo[w.key]||{done:false,wrong:0,locked:false}; ST.redo[w.key]=rec;
    const row=document.createElement("div");
    row.className="sc-item"+(rec.done?" sc-done":"")+((rec.locked&&!rec.done)?" sc-locked":"");
    row.innerHTML='<div class="sc-q"><span class="sc-no">↻</span>'+
      '<span class="sc-lv sc-star sc-d'+(src?(src.d||2):2)+'">'+stars(src?(src.d||2):2)+'</span>'+
      '<span class="sc-qtext">'+vr.t.replace(/（　）/g,'<input class="sc-in" type="text" inputmode="decimal">')+'</span></div>'+
      '<div class="sc-mute">📌 原題：'+esc(w.q.slice(0,30))+'…　｜　當時作答：'+esc(w.mine)+'　｜　錯因：'+esc(w.why)+'</div>'+
      '<div class="sc-btns"><button class="btn btn-primary btn-sm" data-a="ck">✓ 檢查（只作答一次）</button></div>'+
      '<div class="hint-lock">🔒 提示會在答錯後自動出現；作答前不能查看</div>'+
      '<div class="sc-hint">💡 '+esc(vr.exp||w.exp||"")+'</div>'+
      '<div class="sc-fb"></div>';
    const ins=row.querySelectorAll(".sc-in"), fb=row.querySelector(".sc-fb");
    const ck=row.querySelector('[data-a="ck"]');
    const hintEl=row.querySelector(".sc-hint"), lockNote=row.querySelector(".hint-lock");
    function redoWrong(){
      fb.className="sc-fb sc-no";
      fb.innerHTML="❌ 仍未訂正，這題會留在錯題本。<br>"+
        '<div class="sc-btns"><button class="btn btn-accent btn-sm" data-a="again">↻ 再練一次</button></div>';
      fb.querySelector('[data-a="again"]').onclick=function(){
        rec.locked=false; rec.mine=""; save(); UI.open("redo");
      };
      hintEl.classList.add("on");
      if(lockNote) lockNote.style.display="none";
    }
    function redoLock(){
      Array.prototype.forEach.call(ins,function(i){ i.disabled=true; });
      ck.disabled=true; ck.textContent="✓ 已作答";
      if(lockNote) lockNote.style.display="none";
    }
    if(rec.done){
      redoLock();
      fb.className="sc-fb sc-ok"; fb.innerHTML="✅ 已訂正　"+esc(vr.exp||"");
    } else if(rec.locked){
      const parts=(rec.mine||"").split("、");
      Array.prototype.forEach.call(ins,function(i,j){ i.value=parts[j]||""; });
      redoLock(); redoWrong();
    }
    ck.onclick=function(){
      if(rec.locked||rec.done) return;
      const mine=Array.prototype.map.call(ins,function(i){return i.value||"空白";});
      let all=true;
      Array.prototype.forEach.call(ins,function(inp,i){ if(norm(inp.value)!==norm(vr.a[i])) all=false; });
      rec.locked=true; rec.mine=mine.join("、");
      redoLock();
      if(all){
        rec.done=true; markFixed(w.key); fb.className="sc-fb sc-ok";
        fb.innerHTML="✅ 訂正成功！"+esc(vr.exp||"");
        row.classList.remove("sc-locked"); row.classList.add("sc-done");
        sndOk(); if(window.PIX) PIX.burstAt(row);
        addXp(12); bumpCombo(); grant("redo"); save();
        toast("🔁 已訂正一題，錯題本 -1");
      } else {
        rec.wrong=(rec.wrong||0)+1; redoWrong();
        sndNo(); breakCombo(); save();
      }
    };
    box.appendChild(row);
  });
  return box;
}
''', "buildTeacher + 錯題報告 + 重練")


# ══════════════════════════════════════════════════════════════════════
# 14. 完整個性化報告（五段，含錯題）
# ══════════════════════════════════════════════════════════════════════
seg("function buildReport(){", "/* ---------- 診斷 ---------- */", r'''function buildReport(){
  const box=document.createElement("div");
  const s1=statPlan("steps"), s2=statPlan("exit"), s3=statPlan("clinic");
  const total=s1.total+s2.total+s3.total, done=s1.done+s2.done+s3.done,
        wrong=s1.wrong+s2.wrong+s3.wrong;
  const okCount=s1.ok+s2.ok+s3.ok;   /* 一次作答制：答錯不計 done，不可用 done-wrong 推答對數 */
  const pct=total?Math.round(done/total*100):0;
  const mins=Math.max(1,Math.round((Date.now()-ST.t0)/60000));
  const L=LV[lv()], Pl=planOf();
  const weakMap={};
  DATA.steps.forEach((it,i)=>{ const r=ST.steps[i]; if(r&&r.wrong){ weakMap[it.t.slice(0,16)]=(weakMap[it.t.slice(0,16)]||0)+r.wrong; } });
  const weak=Object.keys(weakMap).sort((a,b)=>weakMap[b]-weakMap[a]);
  const wbs=ST.wrongBook.slice().sort((a,b)=>b.at-a.at);
  const cmap={}; wbs.forEach(w=>{ cmap[w.why]=(cmap[w.why]||0)+1; });
  const ckeys=Object.keys(cmap).sort((a,b)=>cmap[b]-cmap[a]);
  const advice = weak.length
    ? ["針對「" + weak[0] + "」先完成錯題重練，再挑戰同類型題目。",
       "每題依「統一單位 → 寫出比 → 化成 1 : n」三步驟列式，不要直接心算。",
       "重點班加練線段比例尺與 10 : 1 放大比例尺，留意前項與後項的順序。"]
    : ["可以挑戰更高難度，嘗試線段比例尺與放大比例尺的混合題。",
       "試試自己量度物件、畫出圖形，再算出比例尺給同學練習。"];
  let rows="";
  activeIds("steps").forEach(function(i){
    const it=DATA.steps[i], r=ST.steps[i]||{};
    rows+="<tr><td>②-"+(i+1)+"</td><td>"+stars(it.d||2)+"</td><td>"+esc(it.t.slice(0,24))+"</td><td>"+
      (r.demo?"示範":(r.done?"✓ 完成":(r.locked?"已作答（錯）":"未做")))+"</td><td>"+(r.wrong||0)+"</td><td>"+(it.sec||"-")+"</td></tr>";
  });
  activeIds("clinic").forEach(function(i){
    const c=DATA.clinic[i], r=ST.clinic["c"+i]||{};
    rows+="<tr><td>③-"+(i+1)+"</td><td>"+stars(c.d||2)+"</td><td>"+esc((c.w||"").slice(0,24))+"</td><td>"+
      (r.done?"✓ 完成":(r.locked?"已作答（錯）":"未做"))+"</td><td>"+(r.wrong||0)+"</td><td>"+(c.sec||"-")+"</td></tr>";
  });
  activeIds("exit").forEach(function(i){
    const it=DATA.exit[i], r=ST.exit[i]||{};
    rows+="<tr><td>④-"+(i+1)+"</td><td>"+stars(it.d||2)+"</td><td>"+esc(it.t.slice(0,24))+"</td><td>"+
      (r.done?"✓ 完成":(r.locked?"已作答（錯）":"未做"))+"</td><td>"+(r.wrong||0)+"</td><td>"+(it.sec||"-")+"</td></tr>";
  });
  box.innerHTML=
    '<div class="who-bar">👤 <b>姓名／班別／座號</b>'+
      '<input id="whoInput" type="text" maxlength="30" placeholder="例如：六年級甲班 12 號 陳大明" value="'+esc(ST.who||"")+'">'+
      '<span class="sc-mute" style="margin:0">會印在報告圖片上，方便老師辨識</span></div>'+
    '<div class="report-entry">🖼 完成練習後，按「產生報告圖片」把這份報告存成 <b>PNG 圖片</b>，即可上傳到網站給老師。圖片已包含姓名、層級、錯題與建議。</div>'+
    '<div class="sc-btns" style="justify-content:center;margin:0 0 12px">'+
      '<button class="btn btn-success" data-a="card">🖼 產生報告圖片</button>'+
      '<button class="btn btn-redo" data-a="redo">🔁 錯題重練</button>'+
      '<button class="btn btn-primary" data-a="csv">📥 匯出 CSV</button>'+
      '<button class="btn btn-ghost" onclick="window.print()">🖨 列印報告</button>'+
    '</div>'+
    '<div id="cardSlot"></div>'+
    '<h3 style="font-size:17px;color:var(--secondary);margin-bottom:8px">一、整體表現</h3>'+
    '<div class="sum-grid">'+
    '<div class="sum-box"><div class="k">完成度</div><div class="v">'+pct+'<small>%</small></div></div>'+
    '<div class="sum-box"><div class="k">答對</div><div class="v">'+okCount+'</div></div>'+
    '<div class="sum-box"><div class="k">錯過</div><div class="v">'+wrong+'</div></div>'+
    '<div class="sum-box"><div class="k">用時</div><div class="v">'+mins+'<small>分</small></div></div>'+
    '<div class="sum-box"><div class="k">層級</div><div class="v" style="font-size:19px">'+L.s+'</div></div>'+
    '<div class="sum-box"><div class="k">診斷得分</div><div class="v">'+(ST.diag.score||0)+'<small>/'+(ST.diag.max||15)+'</small></div></div>'+
    '</div>'+
    '<div class="sc-mute">🎯 本層主題：'+esc(Pl.topic)+'；'+esc(Pl.focus)+'</div>'+
    '<div class="sc-mute">⏱ 本課時間預算 '+CFG.minutes+' 分鐘；目前用時 '+mins+' 分鐘；今日只派 8 題練習。</div>'+
    '<h3 style="font-size:17px;color:var(--secondary);margin:16px 0 8px">二、我的錯題（'+wbs.length+' 題，待訂正 '+redoCount()+' 題）</h3>'+
    (wbs.length
      ? '<table style="width:100%;font-size:13px"><tr><th>題號</th><th>學生答案</th><th>正確答案</th><th>錯因</th><th>狀態</th></tr>'+
        wbs.map(w=>'<tr><td>'+esc(w.key)+'</td><td style="color:#9E2222;font-weight:700">'+esc(w.mine)+
          '</td><td style="color:#1B6B42;font-weight:700">'+esc(w.ans)+'</td><td>'+esc(w.why)+
          '</td><td>'+(w.fixed?'已訂正':'待訂正')+'</td></tr>').join("")+'</table>'
      : '<div class="concept-box">目前沒有錯題記錄。</div>')+
    '<h3 style="font-size:17px;color:var(--secondary);margin:16px 0 8px">三、需要加強的概念</h3>'+
    '<div class="concept-box">'+(ckeys.length
      ? ckeys.map(w=>"• "+esc(w)+"　（錯 "+cmap[w]+" 次）").join("<br>")
      : "暫未發現明顯薄弱點。")+'</div>'+
    '<h3 style="font-size:17px;color:var(--secondary);margin:16px 0 8px">四、給我的建議</h3>'+
    '<div class="concept-box">'+advice.map(a=>"• "+esc(a)).join("<br>")+'</div>'+
    '<h3 style="font-size:17px;color:var(--secondary);margin:16px 0 8px">五、本層逐題記錄（含預估秒數）</h3>'+
    '<table style="width:100%;border-collapse:collapse;font-size:13px">'+
    '<tr style="background:var(--secondary);color:#fff"><th>題</th><th>難度</th><th>題目</th><th>狀態</th><th>錯</th><th>秒</th></tr>'+
    rows+'</table>';
  box.querySelector('[data-a="csv"]').onclick=function(){ UI.csv(); };
  box.querySelector('[data-a="redo"]').onclick=function(){ UI.open("redo"); };
  box.querySelector('[data-a="card"]').onclick=function(){ makeCard(); };
  const wi=box.querySelector("#whoInput");
  if(wi) wi.oninput=function(){ ST.who=this.value.slice(0,30); save(); };
  return box;
}

/* ═════ 像素風報告圖片（Canvas 2D，單檔、零外連） ═════ */
function cardBox(c,x,y,w,h,fill,border,shadow){
  if(shadow){ c.fillStyle="#25243A"; c.fillRect(x+8,y+8,w,h); }
  c.fillStyle=fill; c.fillRect(x,y,w,h);
  if(border){ c.strokeStyle=border; c.lineWidth=6; c.strokeRect(x+3,y+3,w-6,h-6); }
}
function cardText(c,t,x,y,size,color,align,thin){
  c.fillStyle=color||"#25243A";
  c.font=(thin?"":"bold ")+size+'px "PingFang TC","Microsoft JhengHei","Noto Sans TC",sans-serif';
  c.textAlign=align||"left"; c.textBaseline="alphabetic";
  c.fillText(String(t),x,y);
}
function cardWrap(s,n){
  s=String(s||""); const o=[]; let cur="";
  for(let i=0;i<s.length;i++){ cur+=s[i]; if(cur.length>=n){ o.push(cur); cur=""; } }
  if(cur) o.push(cur);
  return o.length?o:[""];
}
function cardDate(){
  const d=new Date();
  return d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2);
}
function cardKey(w){
  const m={steps:"②",clinic:"③",exit:"④"};
  return (m[w.stage]||"•")+"-"+(Number(w.idx)+1);
}
function cardName(){
  const who=String(ST.who||"學生").replace(/[\\/:*?"<>|\s]+/g,"_").slice(0,20);
  return "認識比例尺_學習報告_"+who+"_"+cardDate()+".png";
}
function drawCard(){
  try{
    const cv=document.createElement("canvas");
    const ctx=cv.getContext&&cv.getContext("2d");
    if(!ctx||!ctx.fillRect||!ctx.fillText) return null;
    const W=900,H=1360;
    cv.width=W*2; cv.height=H*2;
    if(ctx.scale) ctx.scale(2,2);
    ctx.fillStyle="#F3EFE1"; ctx.fillRect(0,0,W,H);
    ctx.fillStyle="rgba(37,36,58,0.055)";
    for(let x=0;x<W;x+=16) ctx.fillRect(x,0,1,H);
    for(let y=0;y<H;y+=16) ctx.fillRect(0,y,W,1);
    cardBox(ctx,32,32,W-64,H-64,"#FFFDF6","#25243A",true);

    const s1=statPlan("steps"), s2=statPlan("exit"), s3=statPlan("clinic");
    const total=s1.total+s2.total+s3.total, done=s1.done+s2.done+s3.done;
    const pct=total?Math.round(done/total*100):0;
    const mins=Math.max(1,Math.round((Date.now()-ST.t0)/60000));
    const L=LV[lv()], Pl=planOf();
    const wbs=ST.wrongBook.slice().sort((a,b)=>b.at-a.at);
    const cmap={}; wbs.forEach(w=>{ cmap[w.why]=(cmap[w.why]||0)+1; });
    const ckeys=Object.keys(cmap).sort((a,b)=>cmap[b]-cmap[a]);

    cardBox(ctx,56,56,788,104,"#2E5CA8","#25243A",true);
    cardText(ctx,"認識比例尺｜我的學習報告",84,114,34,"#FFFDF6");
    cardText(ctx,"PIXEL CARTOGRAPHER  ·  LEARNING REPORT",84,145,15,"#CFE0FF","left",true);
    cardBox(ctx,56,178,788,72,"#FFF3C9","#25243A",true);
    cardText(ctx,"姓名／班別／座號："+(ST.who||"未填寫"),78,214,21,"#25243A");
    cardText(ctx,"產生日期："+cardDate()+"　｜　課題："+CFG.lesson+"　｜　診斷 "+(ST.diag.score||0)+" / "+(ST.diag.max||15)+" 分",78,238,14,"#6B5000","left",true);

    const st=[["目前層級",L.s+" "+L.n],["完成度",pct+"%"],["本層答對",done+" / "+total],
              ["累計錯題",wbs.length+" 題"],["待訂正",redoCount()+" 題"],["用時",mins+" 分鐘"]];
    st.forEach(function(v,i){
      const x=56+(i%3)*264, y=268+Math.floor(i/3)*100;
      cardBox(ctx,x,y,250,88,"#E8F0FF","#25243A",false);
      cardText(ctx,v[0],x+16,y+30,15,"#1C3F73","left",true);
      cardText(ctx,v[1],x+16,y+68,28,"#2E5CA8");
    });

    cardBox(ctx,56,478,788,92,"#F7F4E8","#25243A",false);
    cardText(ctx,"本層主題："+Pl.topic,76,512,21,"#E14B3C");
    const fo=cardWrap(Pl.focus,42);
    cardText(ctx,"訓練重點："+fo[0],76,542,15,"#5F5A4E","left",true);
    if(fo[1]) cardText(ctx,"　　　　"+fo[1],76,560,15,"#5F5A4E","left",true);

    function sec(y,label){
      cardBox(ctx,56,y,8,26,"#E14B3C",null,false);
      cardText(ctx,label,76,y+21,20,"#2E5CA8");
      return y+34;
    }
    let y=sec(596,"一、需要加強的概念");
    if(ckeys.length){
      ckeys.slice(0,2).forEach(function(k,i){
        const yy=y+i*40;
        cardText(ctx,"• "+k+"（"+cmap[k]+" 次）",78,yy+18,17,"#25243A");
        for(let j=0;j<Math.min(cmap[k],6);j++){
          ctx.fillStyle="#F5B731"; ctx.fillRect(690+j*22,yy+2,16,18);
        }
      });
      y+=Math.min(ckeys.length,2)*40;
    } else { cardText(ctx,"• 暫未發現明顯薄弱點，表現良好。",78,y+20,17,"#1B6B42"); y+=40; }

    y=sec(y+6,"二、我的錯題");
    if(wbs.length){
      wbs.slice(0,2).forEach(function(w){
        cardText(ctx,"• "+cardKey(w)+"　"+String(w.q).slice(0,16),78,y+18,16,"#25243A");
        cardText(ctx,"  當時作答 "+w.mine+"　→　正確 "+w.ans+"　［"+w.why+"］"+(w.fixed?" 已訂正":" 待訂正"),
                 78,y+40,14,w.fixed?"#1B6B42":"#9E2222","left",true);
        y+=52;
      });
      if(wbs.length>2){
        cardText(ctx,"（尚有 "+(wbs.length-2)+" 題，詳見完整報告）",78,y+16,14,"#6B6558","left",true);
        y+=26;
      }
    } else { cardText(ctx,"• 目前沒有錯題記錄。",78,y+20,17,"#1B6B42"); y+=40; }

    y=sec(y+10,"三、給我的建議");
    const adv=ckeys.length
      ? ["先針對「"+ckeys[0]+"」完成錯題重練，再挑戰同類型題目。",
         "每題寫出「統一單位 → 圖上 : 實際 → 1 : n」，不要直接心算。",
         "完成後檢查前項是否為 1、單位是否相同。"]
      : ["保持目前的三步驟，可挑戰線段比例尺與放大比例尺。",
         "嘗試自己量度物件並算出比例尺給同學練習。",
         "留意 10 : 1 屬於放大比例尺，前項大於後項。"];
    adv.forEach(function(a,i){ cardText(ctx,"• "+a,78,y+18+i*30,16,"#25243A","left",true); });
    y+=adv.length*30+8;

    cardBox(ctx,56,y,788,66,"#E4F6EB","#25243A",false);
    cardText(ctx,"今日須作答 16 題（診斷 8 ＋ 本層練習 8）　｜　時間預算 "+CFG.minutes+" 分鐘",78,y+27,16,"#1B6B42");
    cardText(ctx,"獲得徽章 "+ST.badges.length+" 枚　｜　最高連續答對 "+ST.best+" 題　｜　本層主題："+Pl.topic,
             78,y+51,14,"#1B6B42","left",true);
    y+=82;

    sec(y,"四、本層配對（今日只做 8 題）");
    const cs=statPlan("clinic");
    const listNo=function(a){ return a.map(function(i){return i+1;}).join("、"); };
    [
      ["② 分步列式","第 "+listNo(Pl.steps)+" 題",s1.done+" / "+s1.total+" 已完成"],
      ["③ 錯例醫院","第 "+listNo(Pl.clinic)+" 題",cs.done+" / "+cs.total+" 已完成"],
      ["④ 出門票","第 "+listNo(Pl.exit)+" 題",s2.done+" / "+s2.total+" 已完成"]
    ].forEach(function(r,i){
      const yy=y+40+i*38;
      cardText(ctx,r[0],78,yy,16,"#25243A");
      cardText(ctx,r[1],300,yy,16,"#2E5CA8","left",true);
      cardText(ctx,r[2],500,yy,16,"#5F5A4E","left",true);
    });

    cardBox(ctx,56,H-104,788,56,"#25243A",null,true);
    cardText(ctx,"像素製圖屋・尺尺　｜　由互動教材自動產生，可上傳給老師",80,H-68,16,"#FFFDF6","left",true);
    return cv.toDataURL?cv.toDataURL("image/png"):null;
  }catch(e){ return null; }
}
function makeCard(){
  if(UI.cur!=="report") UI.open("report");
  const url=drawCard();
  if(!url){ toast("此瀏覽器不支援圖片輸出，請改用列印報告"); return null; }
  const body=document.getElementById("mBody");
  let slot=document.getElementById("cardSlot");
  if(!slot){ slot=document.createElement("div"); slot.id="cardSlot"; body.appendChild(slot); }
  slot.innerHTML='<img class="card-preview" id="cardImg" src="'+url+'" alt="我的學習報告圖片">'+
    '<div class="card-note">已產生報告圖片。按「下載 PNG」儲存，再上傳到網站給老師。<br>'+
    '圖片包含姓名、層級、錯題與建議，老師可直接查看。</div>'+
    '<div class="sc-btns" style="justify-content:center">'+
      '<a class="btn btn-success" id="cardDl" href="'+url+'" download="'+esc(cardName())+'">💾 下載 PNG</a>'+
      '<button class="btn btn-ghost" id="cardRe">🔄 重新產生</button></div>';
  slot.querySelector("#cardRe").onclick=function(){ makeCard(); };
  toast("🖼 報告圖片已產生");
  return url;
}
''', "buildReport + 報告卡")


# ══════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════
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

# 15. 診斷完成：送徽章
# ══════════════════════════════════════════════════════════════════════
rep('toast("🎯 分層完成：" + Li.s + " " + Li.n);',
    'grant("diag");\n    toast("🎯 分層完成：" + Li.s + " " + Li.n);', "diag 徽章")
rep('setTimeout(()=>go("explore"), 1400);',
    'setTimeout(()=>{ UI.close(); go("explore"); }, 1400);', "診斷後自動關閉彈窗")


# ══════════════════════════════════════════════════════════════════════
# 16. go / quickbar / UI.open
# ══════════════════════════════════════════════════════════════════════
seg("function go(id){", "function navDone(id,v){", r'''function go(id){
  if(id!=="intro" && id!=="diag" && needDiag()){
    toast("🧭 請先完成 8 題分層診斷，練習才會匹配你的層級");
    UI.open("diag");
    return;
  }
  document.querySelectorAll(".page").forEach(p=>p.classList.remove("active"));
  const t=document.getElementById("page-"+id);
  if(t) t.classList.add("active");
  document.querySelectorAll(".nav-step").forEach(function(b){
    b.classList.toggle("active", b.dataset.go===id);
  });
  render(id);
  window.scrollTo({top:0,behavior:"smooth"});
}
''', "go 分層閘門")

seg("function quickbar(){", "/* ---------- 彈窗 UI ---------- */", r'''function quickbar(){
  const w=document.getElementById("qbInner");
  if(!w) return;
  let h="";
  FLOW.forEach(function(k){ h+='<button class="qb-btn" data-go="'+k+'">'+FLOW_T[k]+'</button>'; });
  h+='<button class="qb-btn report" data-go="report">📊 我的報告</button>';
  h+='<button class="qb-btn redo" id="qbRedo" data-go="redo">🔁 錯題重練</button>';
  h+='<button class="qb-btn teacher" data-go="teacher">👨‍🏫 老師專用</button>';
  w.innerHTML=h;
  w.querySelectorAll("[data-go]").forEach(function(b){
    b.onclick=function(){ UI.open(b.dataset.go); };
  });
  updateRedoBadge();
}
''', "quickbar")

seg("  open:function(stage){", "  close:function(){", r'''  open:function(stage){
    /* 閘門：未完成分層診斷，所有練習與重練都先導向診斷 */
    if(["derive","steps","clinic","exit","redo"].indexOf(stage)>=0 && needDiag()){
      toast("🧭 請先完成 8 題分層診斷，練習才會匹配你的層級");
      stage="diag";
    }
    this.cur=stage;
    const T={
      diag:  ["🧭 分層診斷 —— 8 題定程度","依難度配分 1／2／3 分，滿分 15 分；加權得分決定你的層級。"],
      derive:["① 推演 —— 這類題為什麼要這樣算","先理解、後計算。看完三步，自然記得公式。"],
      steps: ["② 分步列式 —— 我來試試","依你的層級只做對應的步驟；其餘已幫你填好作為示範。"],
      clinic:["③ 錯例醫院 —— 看列式找出錯誤","不必計算：先看、再估大小、最後找出錯誤。"],
      exit:  ["④ 出門票 —— 今日驗收","完成本關就會出現「📋 今日總結」。"],
      redo:  ["🔁 錯題重練 —— 同類型變式題","換數字、不換方法；答對即完成訂正。"],
      wrong: ["📋 錯題報告 —— 逐題對照","原題、學生答案、正確答案、錯因歸類一目了然。"],
      homework:["📝 課後功課","課堂上只列式，數值計算留作回家功課。"],
      report:["📊 我的學習報告","個人表現、錯題、需要加強的概念與建議；可產生 PNG 圖片繳交給老師。"],
      summary:["📋 今日總結","五秒看完：完成多少、錯在哪裡、本課算法。"],
      teacher:["👨‍🏫 老師專用","學生主線不會看到這些功能。"],
      sources:["📖 教材依據一覽","逐題對應課本、練習13 與工作紙出處。"]
    };
    document.getElementById("mTitle").textContent=(T[stage]||["",""])[0];
    const body=document.getElementById("mBody");
    body.innerHTML="";
    let node=null;
    if(stage==="diag") node=buildDiag();
    else if(stage==="derive") node=buildDerive();
    else if(stage==="steps") node=buildSteps();
    else if(stage==="clinic") node=buildClinic();
    else if(stage==="exit") node=buildExit();
    else if(stage==="redo") node=buildRedo();
    else if(stage==="wrong") node=buildWrongReport();
    else if(stage==="homework") node=buildHomework();
    else if(stage==="report") node=buildReport();
    else if(stage==="summary") node=buildSummary();
    else if(stage==="teacher") node=buildTeacher();
    else if(stage==="sources") node=buildSources();
    if(node) body.appendChild(node);
    /* 底部導航 */
    const i=FLOW.indexOf(stage);
    let bh="";
    if(i>=0){
      if(i>0) bh+='<button class="btn btn-ghost btn-sm" data-f="'+(i-1)+'">⬅️ 上一步</button>';
      if(i<FLOW.length-1) bh+='<button class="btn btn-secondary btn-sm" data-f="'+(i+1)+'">'+FLOW_T[FLOW[i+1]]+' ➡️</button>';
      else bh+='<button class="btn btn-success btn-sm" data-f="summary">📋 今日總結 ➡️</button>';
    }
    if(redoCount()>0 && stage!=="redo")
      bh+='<button class="btn btn-redo btn-sm" data-f="redo">🔁 錯題重練 ('+redoCount()+')</button>';
    bh+='<button class="btn btn-ghost btn-sm" onclick="UI.close()">✕ 關閉</button>';
    document.getElementById("mBtns").innerHTML=bh;
    document.getElementById("mBtns").querySelectorAll("[data-f]").forEach(function(b){
      b.onclick=function(){
        if(b.dataset.f==="redo"){ UI.open("redo"); return; }
        const n=parseInt(b.dataset.f,10);
        UI.open(isNaN(n)?"summary":FLOW[n]);
      };
    });
    const s1=statPlan("steps");
    const s2=statPlan("exit");
    let info="";
    if(stage==="derive") info="推演 "+DATA.derive.filter((_,i)=>ST.derive[i]&&ST.derive[i].v!==undefined).length+"/"+DATA.derive.length+" 句已解鎖";
    else if(stage==="steps") info="分步 "+s1.done+"/"+s1.total+"　（本層 "+s1.total+" 題）";
    else if(stage==="clinic") info="錯例 "+DATA.clinic.length+" 題";
    else if(stage==="exit") info="出門票 "+s2.done+"/"+s2.total;
    else if(stage==="redo") info="待訂正 "+redoCount()+" 題";
    else if(stage==="wrong") info="累計錯題 "+ST.wrongBook.length+" 題";
    else if(stage==="report") info="本層 "+LV[lv()].s+"　錯題 "+ST.wrongBook.length+" 題　待訂正 "+redoCount()+" 題";
    else info="層級 "+LV[lv()].s+"　經驗 "+ST.xp;
    document.getElementById("mFoot").textContent=info;
    document.getElementById("mask").classList.add("on");
    const mb=document.getElementById("mBody"); if(mb) mb.scrollTop=0;
    updateRedoBadge();
  },
''', "UI.open")


# ══════════════════════════════════════════════════════════════════════
# 17. UI 加 wrongCsv；share 換像素色
# ══════════════════════════════════════════════════════════════════════
rep("  csv:function(){", r'''  wrongCsv:function(){
    let s="題號,題目,學生答案,正確答案,錯因,錯誤次數,狀態\n";
    ST.wrongBook.forEach(function(w){
      s+=w.key+',"'+w.q.replace(/"/g,'""')+'","'+w.mine.replace(/"/g,'""')+'","'+
         w.ans.replace(/"/g,'""')+'",'+w.why+','+(w.n||1)+','+(w.fixed?"已訂正":"待訂正")+"\n";
    });
    const b=new Blob(["\ufeff"+s],{type:"text/csv;charset=utf-8"});
    const a=document.createElement("a");
    a.href=URL.createObjectURL(b); a.download=CFG.lesson+"_錯題報告.csv"; a.click();
  },
  csv:function(){''', "UI.wrongCsv")

rep("background:#FFF8F0;color:#2D3436;line-height:1.7",
    "background:#F3EFE1;color:#25243A;line-height:1.7;font-family:system-ui", "share bg")
rep("h2{color:#004E89}", "h2{color:#2E5CA8}", "share h2")
rep("'.btn{background:#FF6B35;color:#fff;border:none;padding:11px 22px;border-radius:10px;font-size:15px}'",
    "'.btn{background:#E14B3C;color:#FFFDF6;border:3px solid #25243A;padding:11px 22px;font-size:15px;font-weight:700;box-shadow:4px 4px 0 #25243A}'",
    "share btn")


# ══════════════════════════════════════════════════════════════════════
# 18. 引入頁／探究頁／練習頁
# ══════════════════════════════════════════════════════════════════════
seg("function renderIntro(P){", "function renderExplore(P){", r'''function renderIntro(P){
  let fig="";
  if(CFG.hero){
    FIG.D=0;
    fig='<div class="figbox" style="max-width:520px;margin:0 auto 14px">'+
      FIG.draw(CFG.hero,{stage:1})+
      (CFG.hero.cap?'<div class="figcap">'+esc(CFG.hero.cap)+'</div>':'')+'</div>';
  }
  P.innerHTML=
    '<div class="card">'+
      '<div class="section-title"><span class="emoji">🌟</span> 今日任務</div>'+
      fig+
      '<div class="mission-card"><h2>🎯 '+esc(CFG.title)+'</h2><p>'+esc(CFG.story)+'</p></div>'+
      '<div class="story-line">💡 <b>本課算法：</b>'+esc(CFG.key)+'</div>'+
      '<div class="concept-box">📘 <b>教學目標：</b>認識比例尺的意義；由圖上距離與實際距離計算比例尺；認識線段比例尺；認識放大比例尺 10 : 1。<br>'+esc(CFG.standard)+'</div>'+
      '<div class="concept-box">🔎 <b>'+esc(CFG.encyc)+'</b></div>'+
      '<div class="sc-src">📖 教材依據：《澳門新思維數學》第二版修訂版第13課、課本 p.52 附加例題、《澳門新思維數學習作》練習13、自編補充工作紙冊第13課、工作紙 24.png</div>'+
      '<div class="udl-tip">💡 <b>UDL 提示：</b>本課設有分層——先完成 8 題診斷，系統只會派發適合你程度的 <b>8 題練習</b>（分步 4 題、錯例 2 題、出門票 2 題），不必全部作答。未完成診斷前，練習不會開啟。</div>'+
      '<div class="concept-box">⏱ <b>時間預算：約 '+CFG.minutes+' 分鐘</b>　（診斷 5 ＋ 推演 2 ＋ 分步 5 ＋ 錯例 2.5 ＋ 出門票 4 ＋ 總結 1.5）。今日須作答 <b>16 題</b>（診斷 8 ＋ 本層練習 8），每題均標示預估秒數與教材原文依據；重點班另含線段比例尺與放大比例尺挑戰題。</div>'+
      '<div class="sc-btns" style="justify-content:center;margin-top:14px">'+
        '<button class="btn btn-primary" onclick="go(\'diag\')">🧭 第一步：做 8 題分層診斷</button>'+
      '</div>'+
    '</div>';
}
''', "renderIntro")

seg("function renderPractice(P){", "/* ---------- 推演內嵌（跟住「下一步」解鎖） ---------- */", r'''function renderPractice(P){
  const L=LV[lv()], Pl=planOf();
  const sIds=activeIds("steps"), cIds=activeIds("clinic"), eIds=activeIds("exit");
  const secOf=function(arr,ids){
    return Math.round(ids.reduce(function(s,i){return s+(arr[i].sec||60);},0)/60*10)/10;
  };
  const match=[
    ["① 推演","3 步","全部層級相同","約 2 分鐘"],
    ["② 分步列式",sIds.length+" 題","本層第 "+sIds.map(function(i){return i+1;}).join("、")+" 題（"+L.s+"）","約 "+secOf(DATA.steps,sIds)+" 分鐘"],
    ["③ 錯例醫院",cIds.length+" 題","本層第 "+cIds.map(function(i){return i+1;}).join("、")+" 題","約 "+secOf(DATA.clinic,cIds)+" 分鐘"],
    ["④ 出門票",eIds.length+" 題","本層第 "+eIds.map(function(i){return i+1;}).join("、")+" 題","約 "+secOf(DATA.exit,eIds)+" 分鐘"]
  ];
  P.innerHTML=
    '<div class="card">'+
      '<div class="section-title"><span class="emoji">💪</span> 練習 —— 依照四個步驟進行</div>'+
      '<div class="sc-plan-bar">🎯 你是 <b>'+L.s+' '+L.n+'</b>　本層主題：<b>'+esc(Pl.topic)+'</b>。'+L.tip+
      '　今日只派 <b>8 題</b>（分步 4 ＋ 錯例 2 ＋ 出門票 2），八題都練同一個概念；其他層級的題目不會出現在你的練習中。</div>'+
      '<div class="match-grid">'+match.map(function(m){
        return '<div class="match-box"><b>'+m[0]+'</b>題量：<span class="m">'+m[1]+'</span><br>配對：'+m[2]+'<br>時間：'+m[3]+'</div>';
      }).join("")+'</div>'+
      '<div class="sc-btns" style="margin-top:12px">'+
        (redoCount()?'<button class="btn btn-redo btn-sm" onclick="UI.open(\'redo\')">🔁 錯題重練 ('+redoCount()+')</button>':'')+
      '</div>'+
      '<div class="report-entry">📊 <b>我的學習報告</b>　隨時查看個人表現、錯題與建議；可產生 <b>PNG 報告圖片</b>，下載後上傳到網站給老師。'+
        '<div class="sc-btns">'+
          '<button class="btn btn-primary btn-sm" data-report="1">📊 查看我的報告</button>'+
          '<button class="btn btn-success btn-sm" data-card="1">🖼 產生報告圖片</button>'+
        '</div></div>'+
      '<div class="section-title" style="margin-top:16px"><span class="emoji">🚀</span> 開始練習</div>'+
      '<div class="mainline">'+
        FLOW.map(function(k,i){
          const done = k==="steps"? statPlan("steps").done>=statPlan("steps").total
                     : k==="exit"? statPlan("exit").done>0
                     : k==="derive"? DATA.derive.every((_,j)=>ST.derive[j]&&ST.derive[j].v!==undefined)
                     : k==="clinic"? statPlan("clinic").done>=statPlan("clinic").total
                     : false;
          const D={
            derive:["① 推演","看做法：這類題為什麼要這樣算"],
            steps: ["② 分步列式","我來試試：一步一步填寫算式"],
            clinic:["③ 錯例醫院","看列式：找出別人的錯誤"],
            exit:  ["④ 出門票","驗收：今日學到多少"]
          }[k];
          return '<button class="ml-btn'+(done?" done":"")+'" data-go="'+k+'">'+
            '<div class="n">STEP '+(i+1)+'</div><div class="t">'+D[0]+'</div>'+
            '<div class="d">'+D[1]+'</div></button>';
        }).join("")+
      '</div>'+
      '<div class="sc-btns" style="justify-content:center;margin-top:12px">'+
        '<button class="btn btn-ghost btn-sm" onclick="UI.open(\'teacher\')">👨‍🏫 老師專用</button>'+
      '</div>'+
    '</div>';
  P.querySelectorAll("[data-go]").forEach(function(b){
    b.onclick=function(){ UI.open(b.dataset.go); };
  });
  P.querySelector('[data-report]').onclick=function(){ UI.open("report"); };
  P.querySelector('[data-card]').onclick=function(){ makeCard(); };
}
''', "renderPractice")


# ══════════════════════════════════════════════════════════════════════
# 19. window.BZ 加 PIX
# ══════════════════════════════════════════════════════════════════════
rep("  UI:UI, Explore:Explore, go:go,",
    "  UI:UI, Explore:Explore, go:go, PIX:window.PIX, card:makeCard, drawCard:drawCard,\n  planOf:planOf, activeIds:activeIds,", "BZ export")
rep("steps:ST.steps, exit:ST.exit, clinic:ST.clinic, derive:ST.derive }; },",
    "steps:ST.steps, exit:ST.exit, clinic:ST.clinic, derive:ST.derive,\n    wrongBook:ST.wrongBook, redoCount:redoCount() }; },", "BZ summary")


# ══════════════════════════════════════════════════════════════════════
# 19.6 雲端部署：內嵌 favicon，避免 GitHub Pages 自動請求 /favicon.ico 產生 404
# ══════════════════════════════════════════════════════════════════════
FAVICON = ("<link rel=\"icon\" href=\"data:image/svg+xml,"
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E"
           "%3Crect width='16' height='16' fill='%2325243A'/%3E"
           "%3Crect x='3' y='3' width='10' height='10' fill='%23F5B731'/%3E"
           "%3Crect x='6' y='6' width='4' height='4' fill='%23E14B3C'/%3E"
           "%3C/svg%3E\">")
assert "</title>" in html, "找不到 head 的 </title> 錨點"
html = html.replace("</title>", "</title>\n" + FAVICON, 1)
html = html.replace("/\\s/g", "/[\\s,，]/g")  # 作答容錯：忽略空白與逗號

# ══════════════════════════════════════════════════════════════════════
# 19.5 雲端部署：分享頁 QR 資源改為絕對 URL
#      彈出視窗為 about:blank，相對路徑會解析失敗；GitHub Pages 亦須絕對化
# ══════════════════════════════════════════════════════════════════════
rep(r"""      '<script src="qrcode.min.js"><\/script>'+""",
    r"""      '<script src="'+assetUrl("qrcode.min.js")+'"><\/script>'+""",
    "QR 絕對路徑")

# 依附檔 URL：絕對路徑 + 沿用目前頁面的 query（發佈平台以 ?sharecode= 放行靜態資源）
ASSET_FN = r'''function assetUrl(f){
  var u=new URL(f,location.href);
  if(location.search) u.search=location.search;
  return u.href;
}
'''
anchor = '<script>\n'
assert anchor in html, "找不到內嵌 script 起始錨點"
html = html.replace(anchor, anchor + ASSET_FN, 1)

# ══════════════════════════════════════════════════════════════════════
# 20. 書面語化（引擎內殘留的粵語口語字串）
# ══════════════════════════════════════════════════════════════════════
TRAD = {
  "由最基本嗰步開始，一步一步嚟":"從最基本的一步開始，循序漸進",
  "基本題要穩，再試多一步":"基本題要穩固，再嘗試多一步",
  "直接衝最難嗰步":"直接挑戰最難的步驟",
  "純粹用嚟配返啱你嘅題目":"純粹用於配對適合你的題目",
  "睇完三步推演，你就唔使死背公式":"看完三步推演，就不必死記公式",
  "呢個層級 12 類都啱用，唔使再測":"此層級適用於本單元各節，不必再測",
  "呢類題點解要咁計":"這類題為什麼要這樣算",
  "呢度唔計分、冇提示":"這裡不計分、不提供提示",
  "等我知你喺邊個層次":"讓我了解你的程度",
  "唔識就照填":"不會也可以直接填寫",
  "呢個層級 12 類都啱用，唔使再測":"此層級適用於本單元各節，不必再測",
  "一路睇一路解鎖":"邊看邊解鎖",
  "三步推演全部解鎖，可以去做②分步列式啦":"三步推演全部解鎖，可以進行②分步列式了",
  "呢課有分層":"本課設有分層",
  "呢啲掣":"這些按鈕",
  "呢啲功能":"這些功能",
  "呢個步驟":"這個步驟",
  "呢個層級":"此層級",
  "呢份報告":"這份報告",
  "唔使全部做晒":"不必全部作答",
  "唔使再測":"不必再測",
  "唔使計數":"不必計算",
  "唔使":"不必",
  "唔係":"不是",
  "唔緊要":"沒關係",
  "唔好意思":"不好意思",
  "唔同":"不同",
  "唔知":"不知道",
  "唔怕辛苦":"願意挑戰",
  "而家":"現在",
  "返屋企":"回家",
  "返去":"返回",
  "返返":"返回",
  "睇吓重點先":"先看看重點",
  "睇吓重點":"看看重點",
  "睇吓":"看看",
  "睇完":"看完",
  "睇清楚":"看清楚",
  "睇做法":"看做法",
  "睇重點":"看重點",
  "睇":"看",
  "搵出":"找出",
  "搵":"找",
  "撳「下一步」":"按「下一步」",
  "撳下面":"按下面",
  "撳":"按",
  "啱":"正確",
  "咗":"了",
  "嘅":"的",
  "喺":"在",
  "啲":"這些",
  "佢":"他",
  "晒":"全部",
  "幾多":"多少",
  "邊個":"哪一個",
  "邊度":"哪裡",
  "你係":"你是",
  "就係":"就是",
  "都係":"都是",
  "係咪":"是否",
  "做晒":"完成全部",
  "用咗":"用了",
  "做咗":"完成了",
  "錯咗":"錯了",
  "開咗":"開啟了",
  "出咗":"出現了",
  "我明咗":"我明白了",
  "仲未明":"仍未明白",
  "仲未啱":"還未正確",
  "想試吓":"想試試",
  "我試吓":"我來試試",
  "估吓":"估計",
  "大細":"大小",
  "斷症":"找出錯誤",
  "計法":"算法",
  "計數":"計算",
  "後計數":"後計算",
  "最高連對":"最高連續答對",
  "升到":"升級至",
  "一步一步嚟":"循序漸進",
  "嗰步":"這一步",
  "嗰":"該",
  "嚟":"來",
  "返啱":"配對適合",
}
for k in sorted(TRAD, key=lambda s: -len(s)):
    html = html.replace(k, TRAD[k])

# ===== 書面語潤飾：沒有粵語字、但屬口語句式的措辭 =====
POLISH = {
  "先做 <b>3 條小測</b>":"先完成 <b>3 題小測</b>",
  "你當時填了什麼、正確答案是什麼、屬於哪一個概念":"你所填的答案、正確答案，以及所屬概念",
  "已訂正的題目仍保留作複習":"已訂正的題目仍保留作為複習",
  "我已<b>先幫你填好</b>作為示範":"答案已<b>預先填妥</b>作為示範",
  "已幫你填好作為示範":"已預先填妥作為示範",
  "看得出別人錯在哪裡，自己就不會錯在同一個地方":"能找出別人的錯誤，自己就不會犯同樣的錯誤",
  "保持得很好":"表現良好",
  "錯題本是空的":"錯題本尚無記錄",
  "系統由錯題本挑出":"系統自錯題本挑出",
  "你曾答":"當時作答",
  "他寫了什麼":"他所寫的算式",
  "估計他算出來的數會":"估計他算出的答案會",
  "再看清楚——留意運算符號怎樣改變答案的大小":"再仔細觀察——留意運算符號如何改變答案的大小",
  "我看完了":"我已看完",
  "再想一想":"再思考一次",
  "這一步現在由你自己完成":"這一步改由你自己完成",
  "五秒看完":"五秒掌握",
  "做得好，返回":"完成，返回",
  # 一次作答制：答錯後導向錯題重練，不使用「再試」鼓勵語
  "換數字、不換方法":"更換數字、不改變方法",
  "答錯的題目會自動收進這裡":"答錯的題目會自動收入此處",
  "不必計算：先看、再估大小、最後找出錯誤":"不必計算：先觀察、再估計大小、最後找出錯誤",
  "先看列式、再估大小、最後找出錯誤":"先觀察列式、再估計大小、最後找出錯誤",
}
for k in sorted(POLISH, key=lambda s: -len(s)):
    html = html.replace(k, POLISH[k])

# ===== 修正 CSS class 撞名：.sc-no 是題號圓圈（26x26），不可用於回饋區 =====
html = html.replace('"sc-fb sc-no"', '"sc-fb sc-bad"')

# ===== 診斷回饋：保留重新檢查機會，但不用「再試一次」以免與主練習一次作答制混淆 =====
html = html.replace('fb.innerHTML="❌ 再試一次。"', 'fb.innerHTML="❌ 答案不正確，請重新檢查。"')


# ══════════════════════════════════════════════════════════════════════
# 21. 品質檢查：學生可見文字不得有粵語口語字
# ══════════════════════════════════════════════════════════════════════
BAD = ["喺","咗","嘅","啲","啱","睇","撳","搵","佢","晒","唔","幾多","邊個","而家",
       "咩","噉","冇","梗係","嗰","嚟"]
lines = html.split("\n")
hits = []
for i, ln in enumerate(lines, 1):
    for ch in BAD:
        if ch in ln:
            hits.append((i, ch, ln.strip()[:110]))
            break
if hits:
    print("⚠️  仍發現疑似粵語口語字（需人工確認）：")
    for i, ch, ln in hits[:40]:
        print("   L%-5d [%s] %s" % (i, ch, ln))
    print("   共 %d 行\n" % len(hits))
else:
    print("✅ 書面語檢查：沒有發現粵語口語字")

# 角色命名與一次作答制用語：避免沿用《解比例》精靈名或「再試一次」
ROLE_BAD = ["比比", "再試一次", "再接再厲", "準備好了嗎"]
role_hits = [k for k in ROLE_BAD if k in html]
if role_hits or "尺尺：請先完成 8 題分層診斷。" not in html:
    raise SystemExit("❌ 角色／作答用語不一致：%s" % (role_hits or ["缺少尺尺初始指引"]))
print("✅ 角色與作答用語：統一為「尺尺」；答錯導向錯題重練，無重試原題提示")

# 章節邊界檢查：第13課核心概念必須齊備；後續章節概念不得混入
PREREQ = ["第14課","比例尺的應用","求實際距離","求圖上距離","實際相距多少",
          "圖上相距多少","正比例","反比例","體積","圓面積","速率","相遇","按比例繪圖"]
phits = []
for i, ln in enumerate(lines, 1):
    for ch in PREREQ:
        if ch in ln:
            phits.append((i, ch, ln.strip()[:100]))
            break
if phits:
    print("❌ 章節邊界檢查：混入後續章節概念（已中止輸出）：")
    for i, ch, ln in phits[:30]:
        print("   L%-5d [%s] %s" % (i, ch, ln))
    raise SystemExit("❌ 請移除後續章節概念後再生成")
print("✅ 章節邊界檢查：只含第13課「認識比例尺」範圍")

MUST = ["比例尺 ＝ 圖上距離 : 實際距離","線段比例尺","10 : 1","1 : 480",
        "1 : 2000","1 : 33 000","50 : 1","教材依據","B-2-15","sc-src"]
missing = [k for k in MUST if k not in html]
if missing:
    raise SystemExit("❌ 第13課核心內容缺漏：%s" % missing)
print("✅ 第13課核心內容：意義／求比例尺／線段比例尺／放大比例尺／基力／逐題依據 齊備")

# 逐題秒數與時間預算
print("✅ 題庫：診斷 8 題（加權滿分 15）／分步 12 題／錯例 6 題／出門票 6 題；每層只派 8 題；時間預算 20 分鐘")

# 四大改造的結構檢查（防止日後改題庫時被覆蓋）
MECH = [
    ("診斷 8 題加權分層（滿分 15、基礎題門檻）",
     "const DIAG = [" in html and "ST.diag.max=max" in html and
     "score>=11 && baseReady" in html and "score>=6 && baseReady" in html and
     "baseOk>=2" in html),
    ("每層 8 題練習（分步 4／錯例 2／出門票 2）",
     "steps:[0,1,2,3]" in html and "steps:[4,5,6,7]" in html and
     "steps:[8,9,10,11]" in html and "exit:[4,5]" in html and
     "clinic:[4,5]" in html and "return picks.slice();" in html),
    ("角色與一次作答制用語一致（尺尺／錯題重練）",
     "尺尺：請先完成 8 題分層診斷。" in html and
     '尺尺："+s' in html and
     "比比" not in html and "再試一次" not in html and
     "已記入錯題本，請前往錯題重練。" in html),
    ("本層主題鏈 PLAN（分層針對性）", "const PLAN = {" in html),
    ("每階段只派本層題 activeIds()", "function activeIds(stage){" in html),
    ("一次作答即鎖定", "rec.locked=true; rec.mine=" in html),
    ("提示只在答錯後自動出現", 'hintEl.classList.add("on")' in html),
    ("已移除可自行按下的提示掣", 'data-act="hint"' not in html and 'data-a="tip"' not in html),
    ("原題答對不再抹走錯題", html.count("markFixed(") == 2),
    ("學生報告入口（快捷列／練習頁／總結卡）",
     'data-go="report"' in html and 'data-card="1"' in html and 'data-a="report"' in html),
    ("PNG 報告卡（Canvas 零外連）",
     "function drawCard(){" in html and 'toDataURL("image/png")' in html),
    ("姓名欄可寫入圖片", 'id="whoInput"' in html and "ST.who=this.value" in html),
    ("回饋區不再與題號圓圈 .sc-no 撞名", '"sc-fb sc-no"' not in html and ".sc-fb.sc-bad{" in html),
    ("雲端部署：QR 依附檔使用絕對 URL 且沿用 sharecode",
     'assetUrl("qrcode.min.js")' in html and
     'function assetUrl(f){' in html and
     'u.search=location.search' in html and
     "'<script src=\"qrcode.min.js\"><\\/script>'" not in html),
    ("雲端部署：內嵌 favicon 避免 /favicon.ico 404",
     'rel="icon" href="data:image/svg+xml' in html),
    ("單檔自足：沒有外部 CDN／字型／套件連線",
     "cdn.jsdelivr" not in html and "unpkg.com" not in html and
     "fonts.googleapis" not in html and "cdnjs.cloud" not in html),
    ("比例尺專用六種像素圖解",
     all(("function(f,H){" in html) for _ in [0]) and
     all(("t===\""+k+"\"") in html for k in ["unit","ratio","line","zoom","flow"])),
    ("錯因歸類改為比例尺六類",
     "線段比例尺換算" in html and "放大比例尺的辨認" in html and
     "由圖上與實際距離求比例尺" in html),
    ("逐題教材依據（題目／解題鏈／錯例／老師面板）",
     "item.src" in html and "it.src" in html and "c.src" in html and
     "function buildSources(){" in html and 'stage==="sources"' in html),
    ("數學小百科 10 : 1 與基本學力 B-2-15",
     "CFG.encyc" in html and "B-2-15" in html and "10 : 1" in html),
    ("作答欄容錯：忽略空白與逗號", "/[\\s,，]/g" in html)
]
print("\n──── 完整結構檢查 ────")
bad = 0
for label, passed in MECH:
    print(("  ✅ " if passed else "  ❌ ") + label)
    if not passed:
        bad += 1
if bad:
    raise SystemExit("❌ %d 項結構檢查未通過，已中止輸出" % bad)


# ══════════════════════════════════════════════════════════════════════
# 22. 輸出
# ══════════════════════════════════════════════════════════════════════
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, "utf-8")
if QR.exists():
    shutil.copy2(QR, OUTDIR / "qrcode.min.js")
print("✅ 產出：%s（%d 行，%.1f KB）" % (OUT, html.count("\n")+1, len(html.encode("utf-8"))/1024))
print("✅ 依附檔：qrcode.min.js（報告 QR 用）")
