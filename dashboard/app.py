import streamlit as st
import pandas as pd
import psycopg
import plotly.express as px
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

@st.cache_data
def get_data(query):
    with psycopg.connect(**DB_CONFIG) as conn:
        return pd.read_sql(query, conn)

# ── CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="Horror Universe Dashboard",
    page_icon="🎃",
    layout="wide"
)

st.title("🎃 Horror Universe Dashboard")
st.markdown("*Pipeline de datos — TMDB + Open Library*")

# ── MÉTRICAS GENERALES ────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_movies = get_data("SELECT COUNT(*) as n FROM dim_movies")
total_books = get_data("SELECT COUNT(*) as n FROM dim_books")
avg_rating_movies = get_data("SELECT ROUND(AVG(vote_average)::numeric, 2) as avg FROM dim_movies")
avg_rating_books = get_data("SELECT ROUND(AVG(ratings_average)::numeric, 2) as avg FROM dim_books WHERE ratings_count > 10")

col1.metric("🎬 Películas", total_movies["n"][0])
col2.metric("📚 Libros", total_books["n"][0])
col3.metric("⭐ Rating promedio películas", avg_rating_movies["avg"][0])
col4.metric("⭐ Rating promedio libros", avg_rating_books["avg"][0])

st.divider()

# ── PELÍCULAS ─────────────────────────────────────────
st.header("🎬 Películas de Terror")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 por Rating")
    df = get_data("""
        SELECT title, vote_average, vote_count, release_date
        FROM dim_movies
        WHERE vote_count > 100
        ORDER BY vote_average DESC
        LIMIT 10
    """)
    fig = px.bar(df, x="vote_average", y="title", orientation="h",
                 color="vote_average", color_continuous_scale="Reds",
                 title="Top 10 películas por rating")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Películas por Década")
    df = get_data("""
        SELECT 
            (EXTRACT(YEAR FROM release_date)::int / 10 * 10) as decade,
            COUNT(*) as total
        FROM dim_movies
        WHERE release_date IS NOT NULL
        GROUP BY decade
        ORDER BY decade
    """)
    df["decade"] = df["decade"].astype(str) + "s"
    fig = px.bar(df, x="decade", y="total",
                 color="total", color_continuous_scale="Reds",
                 title="Películas por década")
    st.plotly_chart(fig, use_container_width=True)

# ── GÉNEROS ───────────────────────────────────────────
st.subheader("Géneros más frecuentes en películas de terror")
df = get_data("""
    SELECT g.name, COUNT(*) as total
    FROM movie_genres mg
    JOIN dim_genres g ON mg.genre_id = g.id
    GROUP BY g.name
    ORDER BY total DESC
""")
fig = px.pie(df, values="total", names="name",
             color_discrete_sequence=px.colors.sequential.Reds_r,
             title="Distribución de géneros")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── LIBROS ────────────────────────────────────────────
st.header("📚 Libros de Terror")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 libros por Rating")
    df = get_data("""
        SELECT title, author, ratings_average, ratings_count
        FROM dim_books
        WHERE ratings_count > 10
        ORDER BY ratings_average DESC
        LIMIT 10
    """)
    fig = px.bar(df, x="ratings_average", y="title", orientation="h",
                 color="ratings_average", color_continuous_scale="Reds",
                 title="Top 10 libros por rating")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Autores más prolíficos")
    df = get_data("""
        SELECT author, COUNT(*) as total_books
        FROM dim_books
        WHERE author != 'Unknown'
        GROUP BY author
        ORDER BY total_books DESC
        LIMIT 10
    """)
    fig = px.bar(df, x="total_books", y="author", orientation="h",
                 color="total_books", color_continuous_scale="Reds",
                 title="Top 10 autores con más libros")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data source: TMDB API + Open Library API | Pipeline: Python + PostgreSQL")