#!/usr/bin/env python3
"""
LLM enrichment pipeline — generates question_matches + summary for each episode.

Supports Anthropic, OpenAI, and MiniMax APIs (auto-detects from env).

Usage:
  # Enrich all episodes (auto-resume if interrupted)
  python3 tools/enrich.py --input data/scraped/zhi-xing-xiao-jiu-guan.json \
                           --out data/enriched/zhi-xing-xiao-jiu-guan.json

  # Test with first 3 episodes only
  python3 tools/enrich.py --input data/scraped/zhi-xing-xiao-jiu-guan.json \
                           --out data/enriched/zhi-xing-xiao-jiu-guan.json \
                           --limit 3

  # Force re-enrich all (ignore existing)
  python3 tools/enrich.py ... --force

Environment variables (set in .env or shell):
  ANTHROPIC_API_KEY   — use Claude
  OPENAI_API_KEY      — use OpenAI
  MINIMAX_API_KEY     — use MiniMax (preferred when set)
  LLM_MODEL           — override model (default per provider)
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


# ── .env loader (no python-dotenv needed) ─────────────────────────────────────

def load_dotenv(path=".env"):
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass


# ── LLM client (no SDK, just HTTP) ────────────────────────────────────────────

def call_anthropic(prompt: str, model: str) -> str:
    api_key = os.environ["ANTHROPIC_API_KEY"]
    payload = json.dumps({
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())["content"][0]["text"]


def call_openai_compat(prompt: str, model: str, api_key: str, base_url: str) -> str:
    """Generic OpenAI-compatible chat completion."""
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }).encode()
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


def call_llm(prompt: str) -> str:
    if os.environ.get("MINIMAX_API_KEY"):
        model = os.environ.get("LLM_MODEL", "MiniMax-Text-01")
        return call_openai_compat(prompt, model,
                                  os.environ["MINIMAX_API_KEY"],
                                  "https://api.minimax.chat/v1")
    elif os.environ.get("ANTHROPIC_API_KEY"):
        model = os.environ.get("LLM_MODEL", "claude-haiku-4-5-20251001")
        return call_anthropic(prompt, model)
    elif os.environ.get("OPENAI_API_KEY"):
        model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
        return call_openai_compat(prompt, model,
                                  os.environ["OPENAI_API_KEY"],
                                  "https://api.openai.com/v1")
    else:
        raise RuntimeError(
            "No API key found. Set MINIMAX_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY in .env"
        )


# ── Enrichment prompt ──────────────────────────────────────────────────────────

def _load_prompt_template() -> str:
    """Load prompt template from prompts/enrich.md (falls back to built-in if missing)."""
    path = PROMPTS_DIR / "enrich.md"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise RuntimeError(
            f"Prompt file not found: {path}\n"
            "Expected: prompts/enrich.md in the project root."
        )

# Loaded once at import time
PROMPT_TEMPLATE = _load_prompt_template()


def build_prompt(episode: dict) -> str:
    # Truncate description to ~1500 chars to save tokens
    desc = episode.get("description", "")
    if len(desc) > 1500:
        desc = desc[:1500] + "…"
    # Simple replacement (avoids escaping issues with JSON braces in the template)
    return (
        PROMPT_TEMPLATE
        .replace("{title}", episode.get("title", ""))
        .replace("{description}", desc)
    )


def parse_enrichment(raw: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    raw = raw.strip()
    # Strip ```json ... ``` wrapper if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        raw = "\n".join(lines).strip()
    try:
        data = json.loads(raw)
        assert isinstance(data.get("question_matches"), list)
        assert isinstance(data.get("summary"), str)
        return data
    except (json.JSONDecodeError, AssertionError) as e:
        raise ValueError(f"Failed to parse enrichment JSON: {e}\nRaw:\n{raw[:300]}")


# ── Main pipeline ──────────────────────────────────────────────────────────────

def enrich_episode(episode: dict, retries: int = 3) -> dict:
    prompt = build_prompt(episode)
    last_err = None
    for attempt in range(retries):
        try:
            raw = call_llm(prompt)
            enrichment = parse_enrichment(raw)
            return {**episode, **enrichment}
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 429:
                wait = 20 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s…", file=sys.stderr)
                time.sleep(wait)
            else:
                raise RuntimeError(f"HTTP {e.code}: {body[:200]}")
            last_err = e
        except ValueError as e:
            print(f"  Parse error (attempt {attempt+1}): {e}", file=sys.stderr)
            last_err = e
            time.sleep(2)
    raise RuntimeError(f"Failed after {retries} attempts: {last_err}")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Enrich podcast episodes with LLM-generated metadata")
    parser.add_argument("--input", required=True, help="Scraped JSON input file")
    parser.add_argument("--out", required=True, help="Enriched JSON output file")
    parser.add_argument("--limit", type=int, default=0, help="Only process first N episodes (0 = all)")
    parser.add_argument("--force", action="store_true", help="Re-enrich even if already done")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between API calls (seconds)")
    args = parser.parse_args()

    # Load input
    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)
    episodes = data["episodes"]

    # Load existing enriched output (for resume)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, dict] = {}
    if out_path.exists() and not args.force:
        with open(out_path, encoding="utf-8") as f:
            existing_data = json.load(f)
        existing = {ep["guid"]: ep for ep in existing_data.get("episodes", [])}
        print(f"Resuming: {len(existing)} episodes already enriched", file=sys.stderr)

    # Filter episodes to process
    to_process = episodes if not args.limit else episodes[:args.limit]

    enriched = []
    skipped = 0
    for i, ep in enumerate(to_process):
        guid = ep["guid"]
        if guid in existing and not args.force:
            enriched.append(existing[guid])
            skipped += 1
            continue

        print(f"[{i+1}/{len(to_process)}] {ep['title'][:60]}…", file=sys.stderr)
        try:
            result = enrich_episode(ep)
            enriched.append(result)
            # Save after every episode (safe against interruption)
            out_data = {**data, "episodes": enriched}
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(out_data, f, ensure_ascii=False, indent=2)
            if args.delay:
                time.sleep(args.delay)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            # Save what we have and exit
            out_data = {**data, "episodes": enriched}
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(out_data, f, ensure_ascii=False, indent=2)
            sys.exit(1)

    print(f"\nDone: {len(enriched) - skipped} enriched, {skipped} skipped", file=sys.stderr)
    print(f"Output: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
