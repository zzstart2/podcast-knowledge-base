#!/usr/bin/env python3
"""播客知识库 Web 服务器 — python3 tools/server.py"""

import json
import os
import sqlite3
import struct
import sys
import urllib.parse
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from search import DataLoader, QueryEngine

PORT = int(os.environ.get("PORT", 3000))
UI_DIR = ROOT / "ui"
DB_PATH = ROOT / "data" / "podcast.db"

# Load .env for API keys
def _load_dotenv():
    try:
        with open(ROOT / ".env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass
_load_dotenv()

# Try to import numpy for vector search
try:
    import numpy as np
    _NUMPY = True
except ImportError:
    _NUMPY = False


# ── Embedding helpers ─────────────────────────────────────────────────────────

def _unpack(blob: bytes):
    n = len(blob) // 4
    return struct.unpack(f"{n}f", blob)

def _embed_query(text: str):
    """Call MiniMax embedding API for a single query string."""
    key = os.environ.get("MINIMAX_API_KEY")
    if not key:
        return None
    try:
        payload = json.dumps({"model": "embo-01", "texts": [text], "type": "query"}).encode()
        req = urllib.request.Request(
            "https://api.minimax.chat/v1/embeddings",
            data=payload,
            headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return data.get("vectors", [None])[0]
    except Exception:
        return None

def _cosine_scores(query_vec, rows):
    """Return cosine similarity scores for each row that has an embedding."""
    if not _NUMPY:
        return {}
    q = np.array(query_vec, dtype=np.float32)
    q /= np.linalg.norm(q) + 1e-9
    scores = {}
    for row in rows:
        blob = row["embedding"]
        if blob:
            v = np.array(_unpack(blob), dtype=np.float32)
            v /= np.linalg.norm(v) + 1e-9
            scores[row["guid"]] = float(np.dot(q, v))
    return scores


# ── Vector search ─────────────────────────────────────────────────────────────

def _vector_search(conn: sqlite3.Connection, query_vec, limit: int) -> list[dict]:
    """Fetch all embedded episodes and rank by cosine similarity."""
    rows = conn.execute("""
        SELECT e.*, p.title as podcast_title, p.slug as podcast_slug
        FROM episodes e JOIN podcasts p ON p.id = e.podcast_id
        WHERE e.embedding IS NOT NULL
    """).fetchall()

    scores = _cosine_scores(query_vec, rows)
    if not scores:
        return []

    ranked = sorted(rows, key=lambda r: scores.get(r["guid"], 0), reverse=True)[:limit]
    return [_row_to_dict(r, scores.get(r["guid"], 0)) for r in ranked]


# ── Keyword fallback ──────────────────────────────────────────────────────────

def _keyword_search(conn: sqlite3.Connection, query: str, limit: int) -> list[dict]:
    space_terms = [t.strip() for t in query.split() if t.strip()]
    bigrams = []
    for t in space_terms:
        if len(t) >= 2:
            bigrams += [t[i:i+2] for i in range(len(t)-1)]
    terms = list(dict.fromkeys(bigrams)) if (len(space_terms) == 1 and len(space_terms[0]) >= 4) else space_terms
    if not terms:
        return []

    def cond(term):
        like = f"%{term}%"
        return ("(e.title LIKE ? OR COALESCE(e.question_matches,'') LIKE ? OR "
                "COALESCE(e.summary,'') LIKE ? OR e.description LIKE ?)",
                [like, like, like, like])

    all_conds = [cond(t) for t in terms]
    where = " OR ".join(c[0] for c in all_conds)
    params = [p for c in all_conds for p in c[1]]
    score_expr = " + ".join(c[0] for c in all_conds)

    sql = f"""
        SELECT e.*, p.title as podcast_title, p.slug as podcast_slug,
               ({score_expr}) as score
        FROM episodes e JOIN podcasts p ON p.id = e.podcast_id
        WHERE {where}
        ORDER BY enriched DESC, score DESC, publish_date DESC
        LIMIT ?
    """
    rows = conn.execute(sql, params + params + [limit]).fetchall()
    return [_row_to_dict(r) for r in rows]


def _row_to_dict(row, score: float = 0.0) -> dict:
    qm_raw = row["question_matches"]
    tags_raw = row["tags"]
    return {
        "guid": row["guid"],
        "episode_number": row["episode_number"],
        "title": row["title"],
        "publish_date": row["publish_date"],
        "duration_minutes": row["duration_minutes"],
        "episode_url": row["episode_url"],
        "summary": row["summary"],
        "question_matches": json.loads(qm_raw) if qm_raw else [],
        "tags": json.loads(tags_raw) if tags_raw else [],
        "enriched": bool(row["enriched"]),
        "podcast_title": row["podcast_title"],
        "podcast_slug": row["podcast_slug"],
        "score": round(score, 4),
    }


# ── Main search entry point ───────────────────────────────────────────────────

def db_search(query: str, limit: int = 10) -> list[dict]:
    if not DB_PATH.exists() or not query:
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Check if any embeddings exist
    has_embeddings = conn.execute(
        "SELECT COUNT(*) FROM episodes WHERE embedding IS NOT NULL"
    ).fetchone()[0] > 0

    if has_embeddings and _NUMPY:
        query_vec = _embed_query(query)
        if query_vec:
            results = _vector_search(conn, query_vec, limit)
            conn.close()
            return results

    # Fallback: keyword search
    results = _keyword_search(conn, query, limit)
    conn.close()
    return results


def _ep(e):
    return {
        "id": e.id, "podcast_id": e.podcast_id,
        "episode_number": e.episode_number, "title": e.title,
        "air_date": e.air_date, "duration_seconds": e.duration_seconds,
        "host_ids": e.host_ids, "guest_ids": e.guest_ids,
        "tags": e.tags, "summary": e.summary,
        "key_concepts": e.key_concepts, "status": e.status,
        "quality": e.quality, "body": e.body,
    }


def _person(p):
    return {"id": p.id, "name": p.name, "bio": p.bio,
            "affiliations": p.affiliations, "tags": p.tags}


class Handler(BaseHTTPRequestHandler):
    # Load data once at class level
    _loader = DataLoader(ROOT)
    _podcasts, _people, _episodes = _loader.load_all()
    _engine = QueryEngine(_podcasts, _people, _episodes)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path, qs = parsed.path, urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self._serve_file(UI_DIR / "answer-book.html", "text/html; charset=utf-8")
        elif path == "/api/episodes":
            if not DB_PATH.exists():
                self._json([])
                return
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            offset = int(qs.get("offset", [0])[0])
            limit = int(qs.get("limit", [50])[0])
            rows = conn.execute("""
                SELECT e.guid, e.episode_number, e.title, e.publish_date,
                       e.duration_minutes, e.episode_url, e.summary, e.enriched,
                       e.tags, p.title as podcast_title
                FROM episodes e JOIN podcasts p ON p.id = e.podcast_id
                ORDER BY e.publish_date DESC
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
            enriched_count = conn.execute("SELECT COUNT(*) FROM episodes WHERE enriched=1").fetchone()[0]
            conn.close()
            self._json({
                "total": total,
                "enriched": enriched_count,
                "offset": offset,
                "items": [{
                    "guid": r["guid"],
                    "episode_number": r["episode_number"],
                    "title": r["title"],
                    "publish_date": r["publish_date"],
                    "duration_minutes": r["duration_minutes"],
                    "episode_url": r["episode_url"],
                    "summary": r["summary"],
                    "enriched": bool(r["enriched"]),
                    "tags": json.loads(r["tags"]) if r["tags"] else [],
                    "podcast_title": r["podcast_title"],
                } for r in rows],
            })
        elif path == "/api/data":
            # Single endpoint: all data for initial load
            self._json({
                "podcasts": {pid: {"id": p.id, "name": p.name,
                                   "total_episodes": p.total_episodes}
                             for pid, p in self._podcasts.items()},
                "people": {pid: _person(p) for pid, p in self._people.items()},
                "episodes": [_ep(e) for e in self._episodes],
            })
        elif path == "/api/search":
            tags = qs.get("tag", [])
            person = qs.get("person", [None])[0]
            text = qs.get("text", [None])[0]
            person_id = self._engine.resolve_person(person) if person else None
            results = self._engine.filter(
                tags=tags or None, person_id=person_id, text=text,
            )
            self._json([_ep(e) for e in results])
        elif path == "/api/ask":
            q = qs.get("q", [None])[0] or ""
            limit = int(qs.get("limit", [10])[0])
            self._json(db_search(q, limit))
        else:
            self.send_error(404)

    def _serve_file(self, path, content_type):
        try:
            content = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)

    def _json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # quiet


if __name__ == "__main__":
    server = HTTPServer(("", PORT), Handler)
    print(f"▶  http://localhost:{PORT}")
    server.serve_forever()
