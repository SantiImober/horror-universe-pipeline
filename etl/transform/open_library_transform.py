import pandas as pd
import json
import os
from glob import glob

RAW_PATH = "data/raw"
PROCESSED_PATH = "data/processed"

def load_latest_raw():
    files = glob(f"{RAW_PATH}/open_library_horror_books_*.json")
    latest = max(files)
    print(f"Cargando: {latest}")
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)

def transform_books(raw_data):
    df = pd.DataFrame(raw_data)

    # Seleccionar columnas útiles
    df = df[["key", "title", "author_name", "first_publish_year",
             "number_of_pages_median", "ratings_average", "ratings_count"]]

    # Limpiar autor — viene como lista, tomamos el primero
    df["author"] = df["author_name"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else "Unknown"
    )

    # Limpiar nulos
    df["first_publish_year"] = pd.to_numeric(df["first_publish_year"], errors="coerce")
    df["number_of_pages_median"] = pd.to_numeric(df["number_of_pages_median"], errors="coerce")
    df["ratings_average"] = pd.to_numeric(df["ratings_average"], errors="coerce")
    df["ratings_count"] = pd.to_numeric(df["ratings_count"], errors="coerce").fillna(0).astype(int)

    # Renombrar y seleccionar columnas finales
    df = df.rename(columns={"number_of_pages_median": "number_of_pages"})
    df = df[["key", "title", "author", "first_publish_year",
             "number_of_pages", "ratings_average", "ratings_count"]]

    # Eliminar duplicados por key
    df = df.drop_duplicates(subset="key")

    return df

def save_processed(df):
    os.makedirs(PROCESSED_PATH, exist_ok=True)
    df.to_csv(f"{PROCESSED_PATH}/books.csv", index=False)
    print(f"✅ {len(df)} libros procesados")

if __name__ == "__main__":
    raw = load_latest_raw()
    df = transform_books(raw)
    save_processed(df)
    print("\nPrimeros 3 libros:")
    print(df[["title", "author", "ratings_average"]].head(3))