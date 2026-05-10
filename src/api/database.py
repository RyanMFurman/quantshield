from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from src.api.config import get_settings


class DatabaseUnavailable(RuntimeError):
    """Raised when database-backed routes are called without DB configuration."""


@contextmanager
def get_connection() -> Iterator[Any]:
    settings = get_settings()
    if not settings.database_url:
        raise DatabaseUnavailable("DATABASE_URL is not configured")

    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise DatabaseUnavailable("psycopg is not installed") from exc

    with psycopg.connect(settings.database_url, row_factory=dict_row) as conn:
        yield conn


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return list(cursor.fetchall())
