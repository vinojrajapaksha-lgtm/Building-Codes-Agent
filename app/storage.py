import hashlib
import os
import sqlite3
from datetime import datetime
from typing import Iterable, Tuple

DATABASE_PATH = os.environ.get("PDF_AGENT_DB", "data/index.sqlite")
STORAGE_DIR = os.environ.get("PDF_AGENT_STORAGE", "data/uploads")


def ensure_storage() -> None:
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    os.makedirs(STORAGE_DIR, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_storage()
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                page_count INTEGER NOT NULL,
                uploaded_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS content USING fts5(
                doc_id UNINDEXED,
                text
            )
            """
        )
        connection.commit()


def store_document(filename: str, content_bytes: bytes, page_count: int, text: str) -> int:
    ensure_storage()
    sha256 = hashlib.sha256(content_bytes).hexdigest()
    timestamp = datetime.utcnow().isoformat()
    stored_path = os.path.join(STORAGE_DIR, f"{sha256}.pdf")
    with open(stored_path, "wb") as handle:
        handle.write(content_bytes)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO documents (filename, stored_path, sha256, page_count, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (filename, stored_path, sha256, page_count, timestamp),
        )
        doc_id = cursor.lastrowid
        connection.execute(
            "INSERT INTO content (doc_id, text) VALUES (?, ?)",
            (doc_id, text),
        )
        connection.commit()
    return int(doc_id)


def search_documents(query: str, limit: int = 5) -> Iterable[Tuple[int, str, str]]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT documents.id, documents.filename, snippet(content, 1, '[', ']', '…', 10) AS snippet
            FROM content
            JOIN documents ON documents.id = content.doc_id
            WHERE content MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, limit),
        )
        return cursor.fetchall()


def list_documents() -> Iterable[sqlite3.Row]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, filename, sha256, page_count, uploaded_at
            FROM documents
            ORDER BY uploaded_at DESC
            """
        )
        return cursor.fetchall()
