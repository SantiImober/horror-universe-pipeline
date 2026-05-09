-- ============================================
-- HORROR UNIVERSE PIPELINE - Schema
-- ============================================

CREATE TABLE IF NOT EXISTS dim_movies (
    id              INTEGER PRIMARY KEY,
    title           VARCHAR(500),
    original_title  VARCHAR(500),
    original_language VARCHAR(10),
    overview        TEXT,
    release_date    DATE,
    popularity      NUMERIC(10,4),
    vote_average    NUMERIC(4,3),
    vote_count      INTEGER,
    poster_path     VARCHAR(200),
    extracted_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_genres (
    id      INTEGER PRIMARY KEY,
    name    VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id    INTEGER REFERENCES dim_movies(id),
    genre_id    INTEGER REFERENCES dim_genres(id),
    PRIMARY KEY (movie_id, genre_id)
);