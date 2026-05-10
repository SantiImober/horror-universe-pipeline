import psycopg
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

PROCESSED_PATH = "data/processed"

def get_connection():
    return psycopg.connect(**DB_CONFIG)

def load_books(conn, df):
    """Carga libros a dim_books."""
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO dim_books (
                    id, title, author, first_publish_year,
                    number_of_pages, ratings_average, ratings_count
                ) VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (
                row["key"], row["title"], row["author"],
                int(row["first_publish_year"]) if pd.notna(row["first_publish_year"]) else None,
                int(row["number_of_pages"]) if pd.notna(row["number_of_pages"]) else None,
                float(row["ratings_average"]) if pd.notna(row["ratings_average"]) else None,
                int(row["ratings_count"])
            ))
    conn.commit()
    print(f"✅ {len(df)} libros cargados en dim_books")

if __name__ == "__main__":
    df = pd.read_csv(f"{PROCESSED_PATH}/books.csv")
    with get_connection() as conn:
        load_books(conn, df)