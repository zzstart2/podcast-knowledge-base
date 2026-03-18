#!/usr/bin/env python3
"""
RSS scraper for 小宇宙 podcasts.
Usage: python3 tools/scrape_rss.py --feed <rss_url> --podcast-id <id> --out <output.json>

Example:
  python3 tools/scrape_rss.py \
    --feed https://feed.xyzfm.space/j8yp8gxkmgqr \
    --podcast-id zhi-xing-xiao-jiu-guan \
    --out data/scraped/zhi-xing-xiao-jiu-guan.json
"""

import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser


# ── HTML stripping ────────────────────────────────────────────────────────────

class _MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return " ".join(self.fed)

def strip_html(html: str) -> str:
    s = _MLStripper()
    s.feed(html)
    return re.sub(r"\s+", " ", s.get_data()).strip()


# ── Duration parsing ──────────────────────────────────────────────────────────

def duration_to_minutes(dur: str):
    """Convert HH:MM:SS or MM:SS string to integer minutes."""
    if not dur:
        return None
    parts = dur.strip().split(":")
    try:
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h, m, s = 0, parts[0], parts[1]
        else:
            return None
        return h * 60 + m + (1 if s >= 30 else 0)
    except ValueError:
        return None


# ── Date normalising ──────────────────────────────────────────────────────────

def parse_date(rfc2822: str):
    """Return YYYY-MM-DD from RFC 2822 pubDate."""
    if not rfc2822:
        return None
    # Try several strptime formats
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
    ):
        try:
            dt = datetime.strptime(rfc2822.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Fallback: grab first YYYY-MM-DD-ish pattern
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", rfc2822)
    if m:
        return m.group(0)
    return None


# ── XML namespace helper ──────────────────────────────────────────────────────

NS = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "content": "http://purl.org/rss/1.0/modules/content/",
}

def _text(el, tag, ns_key=None):
    if ns_key:
        child = el.find(f"{{{NS[ns_key]}}}{tag}")
    else:
        child = el.find(tag)
    return child.text.strip() if child is not None and child.text else None


# ── Core fetch & parse ────────────────────────────────────────────────────────

def fetch_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "podcast-lib/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_feed(raw: bytes) -> tuple[dict, list[dict]]:
    root = ET.fromstring(raw)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("No <channel> element found in RSS feed")

    podcast_meta = {
        "title": _text(channel, "title"),
        "description": strip_html(_text(channel, "description") or ""),
        "author": _text(channel, "author", "itunes"),
        "language": _text(channel, "language"),
        "link": _text(channel, "link"),
    }

    episodes = []
    skipped = 0
    for item in channel.findall("item"):
        try:
            guid = _text(item, "guid") or ""

            # Episode URL (link tag)
            link = _text(item, "link") or ""
            # Clean utm params
            link = re.sub(r"\?utm_source=.*$", "", link)

            # Audio enclosure
            enc = item.find("enclosure")
            audio_url = enc.attrib.get("url", "") if enc is not None else ""
            _len_str = (enc.attrib.get("length") or "0") if enc is not None else "0"
            audio_size = int(_len_str) if _len_str.strip().isdigit() else 0

            # Duration
            dur_raw = _text(item, "duration", "itunes") or ""
            duration_min = duration_to_minutes(dur_raw)

            # Description: prefer content:encoded, fall back to description
            desc_html = _text(item, "encoded", "content") or _text(item, "description") or ""
            description = strip_html(desc_html)

            # Episode number from title (e.g. "E227 …" → 227)
            title = _text(item, "title") or ""
            ep_num = None
            m = re.match(r"E(\d+)", title)
            if m:
                ep_num = int(m.group(1))

            episodes.append({
                "guid": guid,
                "episode_number": ep_num,
                "title": title,
                "publish_date": parse_date(_text(item, "pubDate") or ""),
                "duration_minutes": duration_min,
                "duration_raw": dur_raw,
                "description": description,
                "episode_url": link,
                "audio_url": audio_url,
                "audio_size_bytes": audio_size,
            })
        except Exception as exc:
            title_hint = ""
            try:
                title_hint = _text(item, "title") or "(no title)"
            except Exception:
                pass
            print(f"  [warn] skipped malformed item {title_hint!r}: {exc}", file=sys.stderr)
            skipped += 1

    # Sort oldest → newest
    episodes.sort(key=lambda e: (e["publish_date"] or ""))

    if skipped:
        print(f"  [warn] {skipped} malformed item(s) were skipped", file=sys.stderr)

    return podcast_meta, episodes


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scrape podcast episodes from RSS feed")
    parser.add_argument("--feed", required=True, help="RSS feed URL")
    parser.add_argument("--podcast-id", required=True, help="Slug identifier for the podcast")
    parser.add_argument("--out", required=True, help="Output JSON file path")
    args = parser.parse_args()

    print(f"Fetching RSS feed: {args.feed}", file=sys.stderr)
    raw = fetch_feed(args.feed)
    print(f"Downloaded {len(raw):,} bytes", file=sys.stderr)

    podcast_meta, episodes = parse_feed(raw)
    print(f"Parsed {len(episodes)} episodes", file=sys.stderr)

    output = {
        "podcast_id": args.podcast_id,
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": args.feed,
        "podcast": podcast_meta,
        "episode_count": len(episodes),
        "episodes": episodes,
    }

    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Saved to {args.out}", file=sys.stderr)

    # Print quick summary
    print(f"\nPodcast: {podcast_meta['title']}")
    print(f"Episodes: {len(episodes)}")
    if episodes:
        print(f"Date range: {episodes[0]['publish_date']} → {episodes[-1]['publish_date']}")
        print(f"\nFirst 3 episodes:")
        for ep in episodes[:3]:
            print(f"  [{ep['publish_date']}] {ep['title']} ({ep['duration_minutes']}min)")
        print(f"\nLast 3 episodes:")
        for ep in episodes[-3:]:
            print(f"  [{ep['publish_date']}] {ep['title']} ({ep['duration_minutes']}min)")


if __name__ == "__main__":
    main()
