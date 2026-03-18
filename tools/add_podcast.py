#!/usr/bin/env python3
"""
One-command pipeline: podcast name → search → scrape → enrich → embed → import

Usage:
  python3 tools/add_podcast.py "无人知晓"
  python3 tools/add_podcast.py "无人知晓" --confirm   # skip interactive prompt
  python3 tools/add_podcast.py --url https://www.xiaoyuzhoufm.com/podcast/60xxxxxx
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
TOOLS = Path(__file__).parent


# ── Step 1: Search Apple Podcasts API (public, no auth, returns RSS) ──────────

def search_apple_podcasts(name: str) -> list[dict]:
    """Search Apple Podcasts for podcasts by name. Returns list with RSS URLs."""
    encoded = urllib.parse.quote(name)
    url = f"https://itunes.apple.com/search?term={encoded}&country=cn&media=podcast&limit=10"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  ⚠ Apple Podcasts 搜索失败: {e}", file=sys.stderr)
        return []

    results = []
    for item in data.get("results", []):
        feed_url = item.get("feedUrl")
        if not feed_url:
            continue
        results.append({
            "title": item.get("collectionName", ""),
            "author": item.get("artistName", ""),
            "episode_count": item.get("trackCount", "?"),
            "rss": feed_url,
            "apple_id": str(item.get("collectionId", "")),
            "description": "",
        })
    return results


# ── Fallback: 小宇宙 HTML page (15 most recent episodes only) ─────────────────

def search_xiaoyuzhou_ddg(name: str) -> list[dict]:
    """Find 小宇宙 podcast via DuckDuckGo, returns podcast page ID."""
    encoded = urllib.parse.quote(f"{name} 小宇宙 site:xiaoyuzhoufm.com")
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ⚠ DDG 搜索失败: {e}", file=sys.stderr)
        return []
    ids = re.findall(r'xiaoyuzhoufm\.com/podcast/([a-f0-9]{24})', html)
    return [{"xiaoyuzhou_id": i} for i in dict.fromkeys(ids)]


def extract_id_from_url(url: str):
    """Extract podcast ID from a 小宇宙 URL like /podcast/6013f9..."""
    m = re.search(r'/podcast/([a-f0-9]{24})', url)
    return m.group(1) if m else None


def slug_from_title(title: str) -> str:
    """Generate a filesystem-safe slug from Chinese title."""
    # Remove punctuation, lowercase, hyphenate
    title = re.sub(r'[^\w\s\u4e00-\u9fff]', '', title)
    title = title.strip().replace(' ', '-').replace('　', '-')
    # Pinyin would be ideal but we keep it simple: use the title as-is (URL-safe)
    return title.lower()[:40] if title.isascii() else title[:20]


# ── Step 2: Run sub-pipeline ──────────────────────────────────────────────────

def run(cmd: list, desc: str) -> int:
    print(f"\n{'─'*50}", flush=True)
    print(f"▶ {desc}", flush=True)
    print(f"  $ {' '.join(str(c) for c in cmd)}", flush=True)
    print('─'*50, flush=True)
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Add a podcast to 答案之书 in one command")
    parser.add_argument("name", nargs="?", help="Podcast name to search (e.g. '无人知晓')")
    parser.add_argument("--url", help="Directly provide 小宇宙 podcast URL or ID")
    parser.add_argument("--rss", help="Directly provide RSS feed URL (skip search)")
    parser.add_argument("--slug", help="Custom slug for file naming (default: auto)")
    parser.add_argument("--confirm", action="store_true", help="Auto-confirm first search result")
    parser.add_argument("--limit", type=int, default=0, help="Limit enrichment to N episodes (0=all)")
    args = parser.parse_args()

    if not args.name and not args.url and not args.rss:
        parser.print_help()
        sys.exit(1)

    podcast_id = None
    rss_url = None
    podcast_title = args.name or "unknown"

    # ── Resolve podcast ID / RSS ──────────────────────────────────────────────
    if args.rss:
        rss_url = args.rss
        podcast_id = extract_id_from_url(args.rss) or args.slug or "podcast"
        print(f"✔ 使用指定 RSS: {rss_url}")

    elif args.url:
        podcast_id = extract_id_from_url(args.url)
        if not podcast_id:
            print(f"✗ 无法从 URL 中提取播客 ID: {args.url}")
            sys.exit(1)
        rss_url = f"https://feed.xiaoyuzhoufm.com/podcast/{podcast_id}"
        print(f"✔ 使用指定 URL，ID: {podcast_id}")

    else:
        # ── Search: Apple Podcasts first (has RSS), fallback to 小宇宙 ──────────
        print(f"\n🔍 搜索播客: {args.name!r}")
        print(f"  → 通过 Apple Podcasts 查找 RSS...")
        results = search_apple_podcasts(args.name)

        if not results:
            print(f"  ⚠ Apple Podcasts 未找到，尝试小宇宙直接搜索...")
            xyzm = search_xiaoyuzhou_ddg(args.name)
            if xyzm:
                pid = xyzm[0]["xiaoyuzhou_id"]
                rss_url = f"https://feed.xiaoyuzhoufm.com/podcast/{pid}"
                podcast_id = pid
                print(f"  ✔ 小宇宙 podcast ID: {pid}")
                print(f"  ✔ RSS (尝试): {rss_url}")
            else:
                print(f"\n✗ 未找到播客 {args.name!r}")
                print(f"  请手动指定 RSS：")
                print(f"    python3 tools/add_podcast.py --rss <RSS_URL>")
                sys.exit(1)
        else:
            # Show results and let user choose
            if args.confirm or len(results) == 1:
                chosen = results[0]
                print(f"  ✔ 自动选择: 《{chosen['title']}》 by {chosen['author']} ({chosen['episode_count']} 集)")
            else:
                print(f"\n找到 {len(results)} 个结果：")
                for i, r in enumerate(results):
                    print(f"  [{i+1}] 《{r['title']}》 by {r['author']}  ({r['episode_count']} 集)")
                while True:
                    choice = input(f"\n请选择 [1-{len(results)}] 或 q 退出: ").strip()
                    if choice.lower() == "q":
                        sys.exit(0)
                    if choice.isdigit() and 1 <= int(choice) <= len(results):
                        chosen = results[int(choice) - 1]
                        break
                    print("请输入有效序号")

            podcast_title = chosen["title"]
            rss_url = chosen["rss"]
            podcast_id = chosen["apple_id"] or slug_from_title(podcast_title)
            print(f"  ✔ RSS: {rss_url}")

    # ── Determine slug & file paths ───────────────────────────────────────────
    slug = args.slug or slug_from_title(podcast_title)
    scraped_path = ROOT / "data" / "scraped" / f"{slug}.json"
    enriched_path = ROOT / "data" / "enriched" / f"{slug}.json"

    print(f"\n📦 播客标识: {slug}")
    print(f"   抓取输出: {scraped_path.relative_to(ROOT)}")
    print(f"   增强输出: {enriched_path.relative_to(ROOT)}")

    # ── Pipeline ──────────────────────────────────────────────────────────────
    steps_done = []
    steps_failed = []

    # Step 1: Scrape RSS
    rc = run(
        [sys.executable, TOOLS / "scrape_rss.py",
         "--feed", rss_url,
         "--podcast-id", slug,
         "--out", scraped_path],
        f"[1/4] 抓取 RSS 节目列表 → {scraped_path.name}"
    )
    if rc != 0:
        print(f"\n✗ 抓取失败 (exit {rc})")
        sys.exit(rc)
    steps_done.append("scrape")

    # Step 2: Enrich
    enrich_cmd = [sys.executable, TOOLS / "enrich.py",
                  "--input", scraped_path,
                  "--out", enriched_path]
    if args.limit:
        enrich_cmd += ["--limit", str(args.limit)]
    rc = run(enrich_cmd, f"[2/4] LLM 增强 (summary + question_matches)")
    if rc != 0:
        print(f"\n✗ 增强失败 (exit {rc})，尝试继续后续步骤…")
        steps_failed.append("enrich")
    else:
        steps_done.append("enrich")

    # Step 3: Import DB
    rc = run(
        [sys.executable, TOOLS / "import_db.py", "--input", enriched_path],
        f"[3/4] 导入 SQLite 数据库"
    )
    if rc != 0:
        print(f"\n✗ 导入失败 (exit {rc})")
        steps_failed.append("import")
    else:
        steps_done.append("import")

    # Step 4: Embed
    rc = run(
        [sys.executable, TOOLS / "embed.py"],
        f"[4/4] 向量化 (RAG embeddings)"
    )
    if rc != 0:
        print(f"\n✗ 向量化失败 (exit {rc})")
        steps_failed.append("embed")
    else:
        steps_done.append("embed")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'═'*50}")
    print(f"✅ 完成步骤: {', '.join(steps_done)}")
    if steps_failed:
        print(f"⚠ 失败步骤: {', '.join(steps_failed)}")
    print(f"\n《{podcast_title}》已加入答案之书，重启服务即可搜索。")
    print(f"  python3 tools/server.py")
    print('═'*50)


if __name__ == "__main__":
    main()
