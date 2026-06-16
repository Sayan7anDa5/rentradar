import os
import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()
DB = os.environ.get("DATABASE_URL")
pytestmark = pytest.mark.skipif(not DB, reason="DATABASE_URL not set")


def _count(table):
    conn = psycopg2.connect(DB)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    n = cur.fetchone()[0]
    conn.close()
    return n


def test_row_counts():
    assert _count("cities") == 5
    assert _count("localities") == 1990  # 1990 distinct (locality, city) pairs; 21 locality names appear in 2+ cities
    assert _count("listings") == 7538


def test_no_orphan_localities():
    """Every locality points at a real city (FK integrity sanity check)."""
    conn = psycopg2.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM localities l "
        "LEFT JOIN cities c ON l.city_id = c.city_id WHERE c.city_id IS NULL;"
    )
    orphans = cur.fetchone()[0]
    conn.close()
    assert orphans == 0
