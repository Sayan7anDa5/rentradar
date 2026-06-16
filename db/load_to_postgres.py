"""Load data/rentals_clean.csv into the normalized Postgres schema.

Idempotent: truncates the three tables first, then inserts cities, localities,
and listings in foreign-key order. Reads DATABASE_URL from .env.
"""
import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

CSV_PATH = "data/rentals_clean.csv"


def load():
    load_dotenv()
    df = pd.read_csv(CSV_PATH)
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()

    # Idempotent reset.
    cur.execute("TRUNCATE listings, localities, cities RESTART IDENTITY CASCADE;")

    # 1. cities
    cities = sorted(df["city"].unique())
    execute_values(cur, "INSERT INTO cities (name) VALUES %s", [(c,) for c in cities])
    cur.execute("SELECT name, city_id FROM cities;")
    city_id = dict(cur.fetchall())

    # 2. localities (distinct locality+city pairs)
    pairs = df[["locality", "city"]].drop_duplicates()
    execute_values(
        cur,
        "INSERT INTO localities (name, city_id) VALUES %s",
        [(row.locality, city_id[row.city]) for row in pairs.itertuples()],
    )
    cur.execute("SELECT l.name, c.name, l.locality_id FROM localities l JOIN cities c ON l.city_id = c.city_id;")
    locality_id = {(name, cname): lid for name, cname, lid in cur.fetchall()}

    # 3. listings
    rows = [
        (
            locality_id[(r.locality, r.city)],
            r.house_type, r.area, r.beds, r.bathrooms, r.balconies,
            r.furnishing, r.area_rate, r.rent,
        )
        for r in df.itertuples()
    ]
    execute_values(
        cur,
        """INSERT INTO listings
           (locality_id, house_type, area, beds, bathrooms, balconies, furnishing, area_rate, rent)
           VALUES %s""",
        rows,
    )

    conn.commit()

    for table in ("cities", "localities", "listings"):
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        print(f"{table}: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    load()
