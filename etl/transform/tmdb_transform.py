import pandas as pd
import json
import os
from glob import glob

RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed"

def load_latest_raw():
    """Carga el archivo raw más reciente."""
    files = glob(f"{RAW_PATH}/tmdb_horror_movies_*.json")
    latest = max(files)
    print(f"Cargando: {latest}")
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)

def transform_movies(raw_data):
    """Limpia y normaliza los datos de películas."""
    df = pd.DataFrame(raw_data)

    # Seleccionar columnas útiles
    df = df[[
        "id", "title", "original_title", "original_language",
        "overview", "release_date", "popularity",
        "vote_average", "vote_count", "poster_path", "genre_ids"
    ]]

    # Limpiar nulos
    df["overview"] = df["overview"].fillna("")
    df["poster_path"] = df["poster_path"].fillna("")
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    # Separar géneros en tabla aparte
    genres_rows = []
    for _, row in df.iterrows():
        for genre_id in row["genre_ids"]:
            genres_rows.append({
                "movie_id": row["id"],
                "genre_id": genre_id
            })

    df_movie_genres = pd.DataFrame(genres_rows)
    df_movies = df.drop(columns=["genre_ids"])

    return df_movies, df_movie_genres

def save_processed(df_movies, df_movie_genres):
    """Guarda los datos procesados."""
    os.makedirs(PROCESSED_PATH, exist_ok=True)
    df_movies.to_csv(f"{PROCESSED_PATH}/movies.csv", index=False)
    df_movie_genres.to_csv(f"{PROCESSED_PATH}/movie_genres.csv", index=False)
    print(f"✅ {len(df_movies)} películas procesadas")
    print(f"✅ {len(df_movie_genres)} relaciones película-género procesadas")

if __name__ == "__main__":
    raw = load_latest_raw()
    df_movies, df_movie_genres = transform_movies(raw)
    save_processed(df_movies, df_movie_genres)
    print("\nPrimeras 3 películas:")
    print(df_movies[["id", "title", "release_date", "vote_average"]].head(3))