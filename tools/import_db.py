#!/usr/bin/env python3
"""
Import enriched episode JSON into SQLite with FTS5 full-text search.

Usage:
  python3 tools/import_db.py --input data/enriched/zhi-xing-xiao-jiu-guan.json
  python3 tools/import_db.py --input data/enriched/*.json  # multiple files

The DB is created at: data/podcast.db (configurable via --db)
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path


SCHEMA = """
-- Podcasts
CREATE TABLE IF NOT EXISTS podcasts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slug        TEXT UNIQUE NOT NULL,   -- e.g. "zhi-xing-xiao-jiu-guan"
    title       TEXT NOT NULL,
    description TEXT,
    author      TEXT,
    language    TEXT DEFAULT 'zh',
    rss_url     TEXT,
    episode_count INTEGER DEFAULT 0
);

-- Episodes
CREATE TABLE IF NOT EXISTS episodes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    podcast_id       INTEGER NOT NULL REFERENCES podcasts(id),
    guid             TEXT UNIQUE NOT NULL,
    episode_number   INTEGER,
    title            TEXT NOT NULL,
    publish_date     TEXT,             -- YYYY-MM-DD
    duration_minutes INTEGER,
    episode_url      TEXT,
    audio_url        TEXT,
    description      TEXT,            -- original shownotes
    summary          TEXT,            -- LLM-generated 2-3 sentence summary
    question_matches TEXT,            -- JSON array of user question strings
    tags             TEXT,            -- JSON array of "namespace:value" tags
    enriched         INTEGER DEFAULT 0  -- 1 if LLM enrichment done
);

-- FTS5 virtual table for full-text search
-- Searches across: title, summary, question_matches, description
CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
    guid UNINDEXED,
    title,
    summary,
    question_matches,
    description,
    content='episodes',
    content_rowid='id',
    tokenize='unicode61'
);

-- Keep FTS in sync
CREATE TRIGGER IF NOT EXISTS episodes_ai AFTER INSERT ON episodes BEGIN
    INSERT INTO episodes_fts(rowid, guid, title, summary, question_matches, description)
    VALUES (new.id, new.guid, new.title, COALESCE(new.summary,''),
            COALESCE(new.question_matches,''), COALESCE(new.description,''));
END;

CREATE TRIGGER IF NOT EXISTS episodes_ad AFTER DELETE ON episodes BEGIN
    INSERT INTO episodes_fts(episodes_fts, rowid, guid, title, summary, question_matches, description)
    VALUES ('delete', old.id, old.guid, old.title, COALESCE(old.summary,''),
            COALESCE(old.question_matches,''), COALESCE(old.description,''));
END;

CREATE TRIGGER IF NOT EXISTS episodes_au AFTER UPDATE ON episodes BEGIN
    INSERT INTO episodes_fts(episodes_fts, rowid, guid, title, summary, question_matches, description)
    VALUES ('delete', old.id, old.guid, old.title, COALESCE(old.summary,''),
            COALESCE(old.question_matches,''), COALESCE(old.description,''));
    INSERT INTO episodes_fts(rowid, guid, title, summary, question_matches, description)
    VALUES (new.id, new.guid, new.title, COALESCE(new.summary,''),
            COALESCE(new.question_matches,''), COALESCE(new.description,''));
END;
"""


def get_or_create_podcast(conn: sqlite3.Connection, slug: str, meta: dict) -> int:
    cur = conn.execute("SELECT id FROM podcasts WHERE slug = ?", (slug,))
    row = cur.fetchone()
    if row:
        return row[0]
    conn.execute(
        "INSERT INTO podcasts (slug, title, description, author, language, rss_url) VALUES (?,?,?,?,?,?)",
        (slug, meta.get("title",""), meta.get("description",""),
         meta.get("author",""), meta.get("language","zh"), ""),
    )
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def import_file(conn: sqlite3.Connection, path: Path) -> tuple[int, int]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    slug = data.get("podcast_id", path.stem)
    podcast_id = get_or_create_podcast(conn, slug, data.get("podcast", {}))

    inserted = 0
    updated = 0
    for ep in data.get("episodes", []):
        guid = ep["guid"]
        qm = ep.get("question_matches")
        tags = ep.get("tags")
        enriched = 1 if qm else 0

        existing = conn.execute("SELECT id, enriched FROM episodes WHERE guid=?", (guid,)).fetchone()
        if existing:
            if enriched and not existing[1]:
                # Upgrade with enrichment
                conn.execute("""
                    UPDATE episodes SET summary=?, question_matches=?, tags=?, enriched=1
                    WHERE guid=?
                """, (ep.get("summary"), json.dumps(qm, ensure_ascii=False) if qm else None,
                      json.dumps(tags, ensure_ascii=False) if tags else None, guid))
                updated += 1
            continue

        conn.execute("""
            INSERT INTO episodes
            (podcast_id, guid, episode_number, title, publish_date, duration_minutes,
             episode_url, audio_url, description, summary, question_matches, tags, enriched)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            podcast_id,
            guid,
            ep.get("episode_number"),
            ep.get("title", ""),
            ep.get("publish_date"),
            ep.get("duration_minutes"),
            ep.get("episode_url", ""),
            ep.get("audio_url", ""),
            ep.get("description", ""),
            ep.get("summary"),
            json.dumps(qm, ensure_ascii=False) if qm else None,
            json.dumps(tags, ensure_ascii=False) if tags else None,
            enriched,
        ))
        inserted += 1

    # Update episode count
    conn.execute("""
        UPDATE podcasts SET episode_count = (
            SELECT COUNT(*) FROM episodes WHERE podcast_id = ?
        ) WHERE id = ?
    """, (podcast_id, podcast_id))

    return inserted, updated


def main():
    parser = argparse.ArgumentParser(description="Import enriched episode JSON into SQLite")
    parser.add_argument("--input", nargs="+", required=True, help="Enriched JSON file(s)")
    parser.add_argument("--db", default="data/podcast.db", help="SQLite database path")
    args = parser.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    conn.commit()

    total_inserted = total_updated = 0
    for pattern in args.input:
        for path in Path(".").glob(pattern) if "*" in pattern else [Path(pattern)]:
            print(f"Importing {path}…", file=sys.stderr)
            ins, upd = import_file(conn, path)
            conn.commit()
            print(f"  +{ins} inserted, ~{upd} updated", file=sys.stderr)
            total_inserted += ins
            total_updated += upd

    conn.close()
    print(f"\nDB: {db_path}")
    print(f"Total: +{total_inserted} inserted, ~{total_updated} updated")


if __name__ == "__main__":
    main()
