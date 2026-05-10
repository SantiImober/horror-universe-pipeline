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

GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation",
    35: "Comedy", 80: "Crime", 99: "Documentary",
    18: "Drama", 10751: "Family", 14: "Fantasy",
    36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

def get_connection():
    return psycopg.connect(**DB_CONFIG)

def load_genres(conn):
    """Carga géneros a dim_genres."""
    with conn.cursor() as cur:
        for genre_id, genre_name in GENRE_MAP.items():
            cur.execute("""
                INSERT INTO dim_genres (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (genre_id, genre_name))
    conn.commit()
    print(f"✅ {len(GENRE_MAP)} géneros cargados en dim_genres")

def load_movies(conn, df):
    """Carga películas a dim_movies."""
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO dim_movies (
                    id, title, original_title, original_language,
                    overview, release_date, popularity,
                    vote_average, vote_count, poster_path
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (
                row["id"], row["title"], row["original_title"],
                row["original_language"], row["overview"],
                row["release_date"] if pd.notna(row["release_date"]) else None,
                row["popularity"], row["vote_average"],
                row["vote_count"], row["poster_path"]
            ))
    conn.commit()
    print(f"✅ {len(df)} películas cargadas en dim_movies")

def load_movie_genres(conn, df):
    """Carga relaciones película-género."""
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO movie_genres (movie_id, genre_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (int(row["movie_id"]), int(row["genre_id"])))
    conn.commit()
    print(f"✅ {len(df)} relaciones cargadas en movie_genres")

if __name__ == "__main__":
    df_movies = pd.read_csv(f"{PROCESSED_PATH}/movies.csv")
    df_movie_genres = pd.read_csv(f"{PROCESSED_PATH}/movie_genres.csv")

    with get_connection() as conn:
        load_genres(conn)
        load_movies(conn, df_movies)
        load_movie_genres(conn, df_movie_genres)