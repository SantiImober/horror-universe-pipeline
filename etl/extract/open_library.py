import requests
import json
import os
from datetime import datetime

RAW_PATH = "data/raw"

BASE_URL = "https://openlibrary.org/search.json"

def get_horror_books(page=1, limit=100):
    """Trae libros de terror desde Open Library."""
    params = {
        "subject": "horror",
        "sort": "rating",
        "limit": limit,
        "page": page,
        "fields": "key,title,author_name,first_publish_year,number_of_pages_median,ratings_average,ratings_count,subject"
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json()

def extract_all_books(max_pages=5):
    """Extrae múltiples páginas y guarda raw en disco."""
    all_books = []

    for page in range(1, max_pages + 1):
        print(f"Extrayendo página {page}/{max_pages}...")
        data = get_horror_books(page=page)
        all_books.extend(data.get("docs", []))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RAW_PATH}/open_library_horror_books_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(all_books)} libros guardados en {filename}")
    return filename

if __name__ == "__main__":
    extract_all_books(max_pages=5)