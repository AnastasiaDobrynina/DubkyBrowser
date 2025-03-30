CREATE TABLE IF NOT EXISTS users (
    login TEXT PRIMARY KEY,
    username TEXT  NOT NULL,
    password TEXTa NOT NULL,
    sex TEXT,
    age SMALLINT
)

CREATE TABLE IF NOT EXISTS texts (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    index_w2v JSON NOT NULL,
    norm_w2v INT NOT NULL,
    index_tfidf JSON NOT NULL,
    norm_tfidf INT NOT NULL
)

CREATE TABLE IF NOT EXISTS saved (
    user_login TEXT NOT NULL,
    text_id TEXT NOT NULL,
    qurey TEXT NOT NULL,
    PRIMARY KEY (user_login, text_id)
)

COPY texts(text, index_w2v, index_tfidf, norm_w2v, norm_tfidf)
FROM '/docker-entrypoint-initdb.d/dubky_data.csv'
DELIMITER ','
CSV HEADER;
