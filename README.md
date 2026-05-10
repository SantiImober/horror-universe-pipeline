    # 🎃 Horror Universe Pipeline

End-to-end data engineering pipeline que extrae, transforma y carga datos de películas y libros de terror desde APIs públicas hacia un Data Warehouse en PostgreSQL, con visualización en Streamlit.

---

## 🏗️ Arquitectura
TMDB API ──────────┐
├──► Extract (async) ──► Transform ──► PostgreSQL ──► Streamlit
Open Library API ──┘

**Flujo de datos:**
1. **Extract** — dos fuentes de datos corriendo en paralelo con `asyncio`
2. **Transform** — limpieza, normalización y tipado con `pandas`
3. **Load** — inserción en PostgreSQL con manejo de duplicados (`ON CONFLICT DO NOTHING`)
4. **Dashboard** — visualización interactiva con `Streamlit` + `Plotly`

---

## 🗄️ Modelo de Datos
dim_movies          dim_genres          dim_books
──────────          ──────────          ──────────
id (PK)             id (PK)             id (PK)
title               name                title
original_title                          author
original_language   movie_genres        first_publish_year
overview            ────────────        number_of_pages
release_date        movie_id (FK)       ratings_average
popularity          genre_id (FK)       ratings_count
vote_average
vote_count
poster_path

`movie_genres` es una tabla de relación muchos a muchos — una película puede tener múltiples géneros.

---

## 📡 Fuentes de Datos

| API | Datos | Auth |
|---|---|---|
| [TMDB](https://www.themoviedb.org/documentation/api) | Películas de terror, ratings, popularidad, géneros | API Key gratuita |
| [Open Library](https://openlibrary.org/developers/api) | Libros de terror, autores, ratings | Sin auth |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.14 |
| Orquestación | asyncio (extracción paralela) |
| Transformación | pandas |
| Base de datos | PostgreSQL 16 |
| Conector DB | psycopg3 |
| Dashboard | Streamlit + Plotly |
| Control de versiones | Git + GitHub |

---

## 📁 Estructura del Proyecto
horror-universe-pipeline/
│
├── etl/
│   ├── extract/          # Conexión y descarga desde APIs
│   │   ├── tmdb.py
│   │   └── open_library.py
│   ├── transform/        # Limpieza y normalización
│   │   ├── tmdb_transform.py
│   │   └── open_library_transform.py
│   └── load/             # Inserción en PostgreSQL
│       ├── tmdb_load.py
│       └── open_library_load.py
│
├── dags/
│   └── horror_pipeline.py  # Orquestador principal con asyncio
│
├── dashboard/
│   └── app.py              # Dashboard Streamlit
│
├── warehouse/
│   └── schema.sql          # DDL de las tablas
│
├── data/
│   ├── raw/                # JSONs crudos de las APIs
│   └── processed/          # CSVs post-transformación
│
├── .env                    # Credenciales (no versionado)
├── requirements.txt
└── README.md

---

## 🚀 Cómo correr el proyecto

### 1. Clonar el repo
```bash
git clone https://github.com/SantiImober/horror-universe-pipeline.git
cd horror-universe-pipeline
```

### 2. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crear un archivo `.env` en la raíz con:
TMDB_API_KEY=tu_api_key
TMDB_TOKEN=tu_token
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=horror_universe
DB_USER=postgres
DB_PASSWORD=tu_password

### 5. Crear las tablas en PostgreSQL
```bash
psql -U postgres -h 127.0.0.1 -d horror_universe -f warehouse/schema.sql
```

### 6. Correr el pipeline completo
```bash
python dags/horror_pipeline.py
```

### 7. Levantar el dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📊 Dashboard

El dashboard muestra:
- Métricas generales del dataset
- Top 10 películas por rating (con mínimo de votos)
- Distribución de películas por década
- Géneros más frecuentes en el terror
- Top 10 libros por rating
- Autores más prolíficos del género

---

## 🔑 Decisiones técnicas

**¿Por qué asyncio para la extracción?**
Las llamadas a APIs son operaciones I/O bound — el programa pasa la mayor parte del tiempo esperando respuestas HTTP. asyncio permite correr ambas extracciones en paralelo sin bloquear el hilo principal, reduciendo el tiempo total del pipeline.

**¿Por qué guardar raw antes de transformar?**
Si la transformación falla, no es necesario volver a llamar a las APIs. El raw actúa como landing zone — principio estándar en data engineering.

**¿Por qué ON CONFLICT DO NOTHING?**
Hace el pipeline idempotente — se puede correr múltiples veces sin duplicar datos. Fundamental en pipelines de producción.

---

## 👤 Autor

Santiago Imoberdoff — [GitHub](https://github.com/SantiImober)# horror-universe-pipeline
End-to-end data engineering pipeline — Horror movies &amp; books
