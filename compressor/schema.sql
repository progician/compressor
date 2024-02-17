DROP TABLE IF EXISTS tokens;

CREATE TABLE tokens (
    token VARCHAR(32) PRIMARY KEY NOT NULL,
    url VARCHAR(255) NOT NULL
);

CREATE INDEX tokens_url ON tokens (url);
