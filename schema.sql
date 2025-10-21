-- Schema for BlogAPI database

-- Xóa tables và indexes cũ nếu có
DROP TABLE IF EXISTS blogs;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS token_blacklist;
DROP INDEX IF EXISTS ix_blogs_id;
DROP INDEX IF EXISTS ix_users_username;
DROP INDEX IF EXISTS ix_users_id;
DROP INDEX IF EXISTS ix_token_blacklist_token;
DROP INDEX IF EXISTS ix_token_blacklist_id;

-- Tạo tables
CREATE TABLE blogs (
    id INTEGER NOT NULL,
    title VARCHAR,
    content VARCHAR,
    created_at DATETIME,
    updated_at DATETIME,
    PRIMARY KEY (id)
);

CREATE TABLE users (
    id INTEGER NOT NULL,
    username VARCHAR,
    hashed_password VARCHAR,
    PRIMARY KEY (id)
);

CREATE TABLE token_blacklist (
    id INTEGER NOT NULL,
    token VARCHAR,
    created_at DATETIME,
    PRIMARY KEY (id)
);

-- Tạo indexes
CREATE INDEX ix_blogs_id ON blogs (id);
CREATE INDEX ix_users_id ON users (id);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE INDEX ix_token_blacklist_id ON token_blacklist (id);
CREATE UNIQUE INDEX ix_token_blacklist_token ON token_blacklist (token);