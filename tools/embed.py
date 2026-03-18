#!/usr/bin/env python3
"""
Generate embeddings for enriched episodes and store in SQLite.

Usage:
  python3 tools/embed.py              # embed all un-embedded episodes
  python3 tools/embed.py --force      # re-embed everything
  python3 tools/embed.py --limit 10   # only first N

Requires: MINIMAX_API_KEY in .env, numpy installed, data/podcast.db exists.
"""

import argparse
import json
import os
import sqlite3
import struct
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "data" / "podcast.db"

EMBEDDING_MODEL = "embo-01"


# ── .env loader ───────────────────────────────────────────────────────────────

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


# ── SQLite schema migration ───────────────────────────────────────────────────

def ensure_schema(conn: sqlite3.Connection):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(episodes)").fetchall()]
    if "embedding" not in cols:
        conn.execute("ALTER TABLE episodes ADD COLUMN embedding BLOB")
        conn.commit()
        print("Added 'embedding' column to episodes table", file=sys.stderr)
    # Metadata table: tracks which model + dimension was used for stored embeddings
    conn.execute("""
        CREATE TABLE IF NOT EXISTS embedding_meta (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.commit()


def get_stored_model(conn: sqlite3.Connection):
    row = conn.execute(
        "SELECT value FROM embedding_meta WHERE key='model'"
    ).fetchone()
    return row[0] if row else None


def set_embedding_meta(conn: sqlite3.Connection, model: str, dim: int):
    conn.execute("INSERT OR REPLACE INTO embedding_meta VALUES ('model', ?)", (model,))
    conn.execute("INSERT OR REPLACE INTO embedding_meta VALUES ('dim', ?)", (str(dim),))
    conn.commit()


# ── Embedding helpers ─────────────────────────────────────────────────────────

def pack_embedding(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)

def unpack_embedding(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


# ── MiniMax embedding API ─────────────────────────────────────────────────────

def embed_batch(texts: list[str], text_type: str = "db") -> list[list[float]]:
    """Embed a batch of texts (max ~512). type='db' for docs, 'query' for queries."""
    key = os.environ["MINIMAX_API_KEY"]
    payload = json.dumps({
        "model": "embo-01",
        "texts": texts,
        "type": text_type,
    }).encode()
    req = urllib.request.Request(
        "https://api.minimax.chat/v1/embeddings",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    vectors = data.get("vectors")
    if not vectors:
        raise RuntimeError(f"No vectors in response: {json.dumps(data)[:200]}")
    return vectors


def build_doc_text(ep: dict) -> str:
    """Build the text to embed for an episode."""
    parts = [ep.get("title", "")]
    if ep.get("summary"):
        parts.append(ep["summary"])
    qm = ep.get("question_matches")
    if qm:
        if isinstance(qm, str):
            qm = json.loads(qm)
        parts.extend(qm)
    return " | ".join(p for p in parts if p)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Generate embeddings for episodes")
    parser.add_argument("--db", default=str(DB_PATH))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--batch-size", type=int, default=20)
    args = parser.parse_args()

    if not os.environ.get("MINIMAX_API_KEY"):
        print("ERROR: MINIMAX_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)

    # Check embedding model consistency
    stored_model = get_stored_model(conn)
    if stored_model and stored_model != EMBEDDING_MODEL:
        if args.force:
            print(
                f"[warn] Stored model ({stored_model!r}) differs from current model "
                f"({EMBEDDING_MODEL!r}). --force specified: all embeddings will be "
                f"re-generated with the new model.",
                file=sys.stderr,
            )
        else:
            print(
                f"ERROR: Stored embeddings were generated with model {stored_model!r}, "
                f"but current model is {EMBEDDING_MODEL!r}.\n"
                f"Re-run with --force to discard old embeddings and re-generate everything.",
                file=sys.stderr,
            )
            conn.close()
            sys.exit(1)

    # Fetch episodes to embed
    if args.force:
        rows = conn.execute("SELECT * FROM episodes WHERE enriched=1").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM episodes WHERE enriched=1 AND (embedding IS NULL)"
        ).fetchall()

    if args.limit:
        rows = rows[:args.limit]

    total = len(rows)
    print(f"Episodes to embed: {total}", file=sys.stderr)
    if total == 0:
        print("Nothing to do.", file=sys.stderr)
        return

    done = 0
    for i in range(0, total, args.batch_size):
        batch = rows[i:i + args.batch_size]
        texts = [build_doc_text(dict(r)) for r in batch]

        for attempt in range(3):
            try:
                vectors = embed_batch(texts, text_type="db")
                break
            except urllib.error.HTTPError as e:
                body = e.read().decode()
                if e.code == 429:
                    wait = 10 * (attempt + 1)
                    print(f"  Rate limited, waiting {wait}s…", file=sys.stderr)
                    time.sleep(wait)
                else:
                    raise RuntimeError(f"HTTP {e.code}: {body[:200]}")
        else:
            print(f"  Failed batch starting at {i}, skipping", file=sys.stderr)
            continue

        for ep_row, vec in zip(batch, vectors):
            blob = pack_embedding(vec)
            conn.execute(
                "UPDATE episodes SET embedding=? WHERE guid=?",
                (blob, ep_row["guid"]),
            )
        conn.commit()

        # Record model + dim after first successful batch
        if done == 0 and vectors:
            set_embedding_meta(conn, EMBEDDING_MODEL, len(vectors[0]))

        done += len(batch)
        print(f"[{done}/{total}] embedded", file=sys.stderr)
        time.sleep(0.3)

    conn.close()
    print(f"\nDone. {done} episodes embedded.", file=sys.stderr)


if __name__ == "__main__":
    main()
