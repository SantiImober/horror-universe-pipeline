import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import psycopg
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# ── HELPERS ───────────────────────────────────────────
def log(task, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{task}] {msg}")

# ── EXTRACT (en paralelo) ─────────────────────────────
async def extract_tmdb():
    log("EXTRACT", "🎬 Iniciando extracción TMDB...")
    loop = asyncio.get_event_loop()
    from etl.extract.tmdb import extract_all_movies
    filename = await loop.run_in_executor(None, lambda: extract_all_movies(max_pages=10))
    log("EXTRACT", f"✅ TMDB completado → {filename}")
    return filename

async def extract_open_library():
    log("EXTRACT", "📚 Iniciando extracción Open Library...")
    loop = asyncio.get_event_loop()
    from etl.extract.open_library import extract_all_books
    filename = await loop.run_in_executor(None, lambda: extract_all_books(max_pages=5))
    log("EXTRACT", f"✅ Open Library completado → {filename}")
    return filename

# ── TRANSFORM ─────────────────────────────────────────
def transform_tmdb():
    log("TRANSFORM", "🔧 Transformando películas...")
    from etl.transform.tmdb_transform import load_latest_raw, transform_movies, save_processed
    raw = load_latest_raw()
    df_movies, df_genres = transform_movies(raw)
    save_processed(df_movies, df_genres)
    log("TRANSFORM", "✅ Películas transformadas")

def transform_books():
    log("TRANSFORM", "🔧 Transformando libros...")
    from etl.transform.open_library_transform import load_latest_raw, transform_books, save_processed
    raw = load_latest_raw()
    df = transform_books(raw)
    save_processed(df)
    log("TRANSFORM", "✅ Libros transformados")

# ── LOAD ──────────────────────────────────────────────
def load_tmdb():
    log("LOAD", "📥 Cargando películas a Postgres...")
    from etl.load.tmdb_load import load_genres, load_movies, load_movie_genres
    df_movies = pd.read_csv("data/processed/movies.csv")
    df_movie_genres = pd.read_csv("data/processed/movie_genres.csv")
    with psycopg.connect(**DB_CONFIG) as conn:
        load_genres(conn)
        load_movies(conn, df_movies)
        load_movie_genres(conn, df_movie_genres)
    log("LOAD", "✅ Películas cargadas")

def load_books():
    log("LOAD", "📥 Cargando libros a Postgres...")
    from etl.load.open_library_load import load_books as load_books_db
    df = pd.read_csv("data/processed/books.csv")
    with psycopg.connect(**DB_CONFIG) as conn:
        load_books_db(conn, df)
    log("LOAD", "✅ Libros cargados")

# ── PIPELINE PRINCIPAL ────────────────────────────────
async def main():
    start = datetime.now()
    print("\n" + "="*50)
    print("   HORROR UNIVERSE PIPELINE")
    print("="*50 + "\n")

    # Extract en paralelo
    log("PIPELINE", "Arrancando extracciones en paralelo...")
    await asyncio.gather(
        extract_tmdb(),
        extract_open_library()
    )

    # Transform secuencial (depende del extract)
    log("PIPELINE", "Arrancando transformaciones...")
    transform_tmdb()
    transform_books()

    # Load secuencial (depende del transform)
    log("PIPELINE", "Arrancando carga a Postgres...")
    load_tmdb()
    load_books()

    elapsed = (datetime.now() - start).seconds
    print("\n" + "="*50)
    print(f"   ✅ PIPELINE COMPLETADO en {elapsed}s")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())