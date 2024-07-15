CREATE TABLE
  users (
    id INTEGER,
    username TEXT,
    hash TEXT,
    cash NUMERIC,
    UNIQUE (id) CONSTRAINT users_pk PRIMARY KEY (id)
  );