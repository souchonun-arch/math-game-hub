#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
遊戲總站 build.py
================
掃描波仔桌面嘅遊戲來源資料夾 → 產生 data/games.json → 將遊戲檔複製到 games/<section>/<slug>/index.html

用法：
    python3 scripts/build.py --dry-run    # 只睇報告，唔郁任何檔案
    python3 scripts/build.py              # 真的做

鐵律：桌面原檔絕對唔會被改動
    1. 來源檔一律以 'rb' 開啟只讀；寫入只去 repo 入面
    2. 執行前後對來源目錄做 (size, mtime_ns) 快照比對，有變動即中止
    3. 所有寫入路徑都要 resolve 後確認喺 repo 根目錄之內
    4. 已驗證無引用嘅素材檔（bank-p1.js 等）不複製
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO / "scripts"
DATA_DIR = REPO / "data"
GAMES_DIR = REPO / "games"

SOURCES_FILE = SCRIPTS_DIR / "sources.json"
SLUGS_FILE = DATA_DIR / "slugs.json"
OVERRIDES_FILE = DATA_DIR / "overrides.json"
TOPICS_FILE = DATA_DIR / "topics.json"
SECTIONS_FILE = DATA_DIR / "sections.json"
GAMES_JSON = DATA_DIR / "games.json"
SUGGESTED_FILE = DATA_DIR / "overrides.suggested.json"

TZ = timezone(timedelta(hours=8))

REF_RE = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)

# 呢啲字眼唔會進 slug（版本號、修飾語），確保改版時網址唔會變
VERSION_WORDS = re.compile(r"(v?\d+\.\d+|v\d+|華麗技能版|原始備份|\(.*?\)|（.*?）)", re.I)


def die(msg: str) -> "NoReturn":  # type: ignore[valid-type]
    print(f"\n❌ 中止：{msg}\n", file=sys.stderr)
    sys.exit(1)


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{path.name} 格式錯誤：{e}")


def ensure_inside_repo(path: Path, what: str = "寫入目標") -> Path:
    """所有寫入都必須喺 repo 入面，防止寫錯去桌面"""
    resolved = path.resolve()
    if not str(resolved).startswith(str(REPO.resolve()) + "/") and resolved != REPO.resolve():
        die(f"{what} 喺 repo 之外，拒絕執行：{resolved}")
    return resolved


def read_bytes(path: Path) -> bytes:
    """來源檔只讀：永遠唔會開寫入模式"""
    with open(path, "rb") as fh:
        return fh.read()


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot_tree(paths: list[Path]) -> dict[str, tuple[int, int]]:
    """對來源檔做 (size, mtime_ns) 快照，用嚟證明執行前後冇郁過原檔"""
    snap: dict[str, tuple[int, int]] = {}
    for p in paths:
        try:
            st = p.stat()
        except OSError:
            continue
        snap[str(p)] = (st.st_size, st.st_mtime_ns)
    return snap


def human_size(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.1f} MB"
    if n >= 1024:
        return f"{round(n / 1024)} KB"
    return f"{n} B"


def wifi_level(n: int) -> str:
    """>=8MB 紅燈、>=3MB 橙燈，其餘正常"""
    if n >= 8 * 1024 * 1024:
        return "heavy"
    if n >= 3 * 1024 * 1024:
        return "medium"
    return "light"


def extract_title(data: bytes) -> str:
    """由 HTML 攞 <title>，做唔到就用檔名"""
    try:
        text = data[:200_000].decode("utf-8", errors="ignore")
    except Exception:
        return ""
    m = TITLE_RE.search(text)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
        if title:
            return title
    return ""


def looks_like_template(ref: str) -> bool:
    """`chef${p+1}.png` 呢類模板變數要跳過"""
    return any(ch in ref for ch in ("{", "}", "$", "+", " "))


def find_attachments(html_path: Path, raw: bytes, cfg: dict) -> tuple[list[dict], list[str]]:
    """搵出 HTML 真正引用、而且喺同層搵到嘅依附檔"""
    allowed = set(cfg.get("attachExtensions", []))
    never = set(cfg.get("attachNeverCopy", []))
    try:
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        text = ""
    found: dict[str, Path] = {}
    unresolved: list[str] = []
    for ref in REF_RE.findall(text):
        ref = ref.strip()
        if not ref or ref.startswith(("data:", "#", "//", "http://", "https://", "mailto:", "javascript:")):
            continue
        if looks_like_template(ref):
            continue
        if ref.startswith("../") or ref.startswith("/"):
            unresolved.append(ref)
            continue
        cand = (html_path.parent / ref)
        try:
            cand = cand.resolve()
        except OSError:
            continue
        if not cand.exists() or not cand.is_file():
            continue
        if cand.name in never or cand.suffix.lower() not in allowed:
            continue
        found[cand.name] = cand
    deps = []
    for name in sorted(found):
        p = found[name]
        deps.append({"file": name, "bytes": p.stat().st_size})
    return deps, unresolved


def make_slug(relpath: str, title: str) -> str:
    """新遊戲先自動產生一個可用 slug（之後可以喺 slugs.json 改靚佢）"""
    stem = Path(relpath).stem
    stem = VERSION_WORDS.sub("", stem)
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", stem).strip("-").lower()
    if len(ascii_part) >= 4:
        return ascii_part[:48]
    digest = hashlib.sha1(relpath.encode("utf-8")).hexdigest()[:8]
    return f"game-{digest}"


def collect_source_files(cfg: dict) -> list[Path]:
    """掃描所有來源資料夾入面嘅檔案（用嚟做快照）"""
    root = Path(cfg["root"])
    if not root.is_dir():
        die(f"來源根目錄唔存在：{root}")
    files: list[Path] = []
    for src in cfg["sources"]:
        d = root / src["dir"]
        if not d.is_dir():
            print(f"⚠️  來源資料夾唔存在，已跳過：{d}")
            continue
        files.extend(p for p in d.rglob("*") if p.is_file())
    return files


def scan_games(cfg: dict, slugs: dict, overrides: dict) -> tuple[list[dict], list[dict]]:
    """掃描並回傳 (收錄嘅遊戲, 被排除嘅檔案)"""
    root = Path(cfg["root"])
    exclude_sub = cfg.get("excludeSubstrings", [])
    exclude_rel = set(cfg.get("excludeRelPaths", []))
    min_bytes = int(cfg.get("minBytes", 0))

    games: list[dict] = []
    excluded: list[dict] = []

    for src in cfg["sources"]:
        section = src["section"]
        d = root / src["dir"]
        if not d.is_dir():
            continue
        html_files = sorted(p for p in d.rglob("*.html") if p.is_file())
        seen_hash: dict[str, str] = {}  # sha256 -> 已收錄嘅相對路徑（用嚟踢走重複檔）

        for hp in html_files:
            rel = hp.relative_to(root).as_posix()

            # 排除規則
            hit = None
            if rel in exclude_rel:
                hit = "設定明確排除（重複檔/備份）"
            elif any(s in rel for s in exclude_sub):
                hit = "檔名含排除字眼（備份）"
            if hit is None and hp.stat().st_size < min_bytes:
                hit = f"細過 {min_bytes // 1024}KB（唔係遊戲主檔）"

            if hit:
                excluded.append({"rel": rel, "section": section, "reason": hit})
                continue

            raw = read_bytes(hp)
            digest = sha256_of(raw)
            if digest in seen_hash:
                excluded.append({"rel": rel, "section": section,
                                 "reason": f"與 {seen_hash[digest]} 內容完全相同"})
                continue
            seen_hash[digest] = rel

            if rel not in slugs:
                excluded.append({"rel": rel, "section": section,
                                 "reason": "新遊戲：slugs.json 未登記，需要人手確認 slug"})
                games.append(_build_entry(hp, rel, raw, digest, section, slugs, overrides, cfg, is_new=True))
                continue

            games.append(_build_entry(hp, rel, raw, digest, section, slugs, overrides, cfg, is_new=False))

    return games, excluded


def _build_entry(hp: Path, rel: str, raw: bytes, digest: str, section: str,
                 slugs: dict, overrides: dict, cfg: dict, is_new: bool) -> dict:
    slug = slugs.get(rel) or make_slug(rel, rel)
    ov = overrides.get(slug, {})
    title_html = extract_title(raw)
    deps, unresolved = find_attachments(hp, raw, cfg)
    total = hp.stat().st_size + sum(d["bytes"] for d in deps)
    try:
        text = raw.decode("utf-8", errors="ignore")
    except Exception:
        text = ""
    needs_network = bool(re.search(r"""(?:src|href)\s*=\s*["']https?://""", text))

    return {
        "id": slug,
        "section": section,
        "title": ov.get("title") or title_html or hp.stem,
        "titleFromHtml": title_html,
        "topic": ov.get("topic") or "未分類",
        "keywords": ov.get("keywords") or [],
        "bytes": hp.stat().st_size,
        "totalBytes": total,
        "sizeText": human_size(total),
        "wifi": wifi_level(total),
        "depCount": len(deps),
        "needsNetwork": needs_network,
        "sha256": digest,
        "source": rel,
        "sourceAbs": str(hp),
        "entry": f"games/{section}/{slug}/",
        "file": "index.html",
        "deps": [d["file"] for d in deps],
        "unresolvedRefs": unresolved,
        "isNew": is_new,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="掃描遊戲來源並產生 games.json")
    ap.add_argument("--dry-run", action="store_true", help="只印報告，唔複製任何檔案")
    ap.add_argument("--root", help="暫時覆寫來源根目錄（通常唔使改）")
    args = ap.parse_args()

    cfg = load_json(SOURCES_FILE) or die(f"搵唔到 {SOURCES_FILE}")
    if args.root:
        cfg["root"] = args.root
    slugs_raw = load_json(SLUGS_FILE, {}) or {}
    slugs = {k: v for k, v in slugs_raw.items() if not k.startswith("_")}
    overrides_raw = load_json(OVERRIDES_FILE, {}) or {}
    overrides = {k: v for k, v in overrides_raw.items() if not k.startswith("_")}
    sections = [s for s in (load_json(SECTIONS_FILE, []) or []) if isinstance(s, dict)]

    print("=" * 66)
    print("  數學遊戲總站 — build.py" + ("  【DRY RUN 只睇唔郁】" if args.dry_run else ""))
    print("=" * 66)

    all_source_files = collect_source_files(cfg)
    before = snapshot_tree(all_source_files)
    print(f"來源根目錄：{cfg['root']}")
    print(f"已快照 {len(before)} 個來源檔案，執行完會再核對一次確保冇郁過\n")

    games, excluded = scan_games(cfg, slugs, overrides)

    prev = load_json(GAMES_JSON, None)
    prev_by_id = {g["id"]: g for g in prev.get("games", [])} if prev else {}

    for g in games:
        old = prev_by_id.get(g["id"])
        if old is None:
            g["status"] = "new"
        elif old.get("sha256") != g["sha256"]:
            g["status"] = "modified"
        else:
            g["status"] = "unchanged"

    missing = [gid for gid in prev_by_id if gid not in {g["id"] for g in games}]

    # ---- 報告 ----
    print("-" * 66)
    for sec in sections:
        sid = sec["id"]
        items = [g for g in games if g["section"] == sid]
        total = sum(g["totalBytes"] for g in items)
        print(f"\n{sec['icon']} {sec['title']}（{sid}）— {len(items)} 款、共 {human_size(total)}")
        for g in items:
            flag = {"new": "🆕 新增", "modified": "✏️  已改", "unchanged": "✅ 冇變"}[g["status"]]
            extra = []
            if g["depCount"]:
                extra.append(f"依附 {g['depCount']} 檔")
            if g["needsNetwork"]:
                extra.append("需外網")
            if g["isNew"]:
                extra.append("⚠️  未登記 slug")
            tail = ("  [" + "、".join(extra) + "]") if extra else ""
            print(f"   {flag}  {g['title']}  ({g['sizeText']}){tail}")
            print(f"          → {g['entry']}")

    if excluded:
        print("\n" + "-" * 66)
        print(f"已排除 {len(excluded)} 個檔案：")
        for e in excluded:
            print(f"   ⛔ {e['rel']}")
            print(f"      原因：{e['reason']}")

    if missing:
        print("\n" + "-" * 66)
        print(f"⚠️  {len(missing)} 款遊戲喺來源搵唔到（保留原有目錄，等你確認）：")
        for gid in missing:
            print(f"   ❓ {gid}")

    new_games = [g for g in games if g["isNew"]]
    if new_games:
        print("\n" + "-" * 66)
        print("🎯 發現新遊戲，等你決定 slug：")
        for g in new_games:
            print(f"   來源：{g['source']}")
            print(f"   建議 slug：{g['id']}")
            print(f"   → 請喺 data/slugs.json 加：「{g['source']}」: \"你揀嘅slug\"")
            print(f"   → 並喺 data/overrides.json 加顯示名同課題")

    total_all = sum(g["totalBytes"] for g in games)
    counts = {sec["id"]: len([g for g in games if g["section"] == sec["id"]]) for sec in sections}
    print("\n" + "=" * 66)
    print(f"收錄 {len(games)} 款、共 {human_size(total_all)}（{total_all:,} bytes）")
    print("分區數量：" + "  ".join(f"{k}={v}" for k, v in counts.items()))
    print("=" * 66)

    if args.dry_run:
        print("\n💡 DRY RUN 完成，冇郁過任何檔案。確認無誤後再跑：")
        print("     python3 scripts/build.py")
        return 0

    # ---- 真的寫 ----
    print("\n開始複製遊戲檔...")
    target_root = ensure_inside_repo(GAMES_DIR, "遊戲輸出目錄")
    written = 0
    for g in games:
        if g["isNew"]:
            print(f"   ⏭️  跳過未登記 slug 嘅新遊戲：{g['source']}")
            continue
        dest_dir = ensure_inside_repo(target_root / g["section"] / g["id"], "遊戲目錄")
        dest_dir.mkdir(parents=True, exist_ok=True)
        src = Path(g["sourceAbs"])
        try:
            text = src.read_bytes()
        except Exception as e:
            die(f"讀取失敗 {src}：{e}")
        (dest_dir / "index.html").write_bytes(text)
        written += 1
        for dep in g["deps"]:
            dep_src = src.parent / dep
            if not dep_src.exists():
                print(f"      ⚠️  依附檔唔見咗：{dep}")
                continue
            shutil.copy2(dep_src, dest_dir / dep)
            written += 1

    # ---- 寫 games.json ----
    out = {
        "updated": datetime.now(TZ).strftime("%Y-%m-%d %H:%M"),
        "count": len([g for g in games if not g["isNew"]]),
        "totalBytes": sum(g["totalBytes"] for g in games if not g["isNew"]),
        "games": [
            {k: v for k, v in g.items() if k not in ("sourceAbs", "isNew", "status")}
            for g in sorted(games, key=lambda x: (x["section"], x["title"]))
            if not g["isNew"]
        ],
    }
    ensure_inside_repo(GAMES_JSON, "games.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # ---- 核對原檔冇郁過 ----
    after = snapshot_tree(all_source_files)
    changed = [p for p in before if p in after and after[p] != before[p]]
    vanished = [p for p in before if p not in after]
    if changed or vanished:
        print("\n" + "!" * 66)
        for p in changed[:10]:
            print(f"   ⚠️  來源檔被改動：{p}")
        for p in vanished[:10]:
            print(f"   ⚠️  來源檔唔見咗：{p}")
        die("來源目錄有變動，已中止！請檢查上面嘅檔案")

    print(f"\n✅ 完成：寫咗 {written} 個檔案，games.json 已更新")
    print(f"   games.json：{GAMES_JSON}")
    print(f"   來源目錄核對通過：{len(before)} 個檔案全部原封不動（size + mtime 一致）")
    if new_games:
        print(f"\n⚠️  仲有 {len(new_games)} 款新遊戲未上架（等 slug 確認），睇返上面嘅指引")
    return 0


if __name__ == "__main__":
    sys.exit(main())
