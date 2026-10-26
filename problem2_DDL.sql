
CREATE DATABASE IF NOT EXISTS registration;
USE registration;

-- AUTHORS TABLE
CREATE TABLE IF NOT EXISTS AUTHOR (
    author_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    photo_filename VARCHAR(255) NULL,
    CONSTRAINT uq_author_name UNIQUE (name)
);

-- BOOKS TABLE
CREATE TABLE IF NOT EXISTS BOOK (
    book_id INT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    author_id INT NOT NULL,
    cover_filename VARCHAR(255) NULL,

    CONSTRAINT uq_book_title UNIQUE (title),

    CONSTRAINT fk_book_author
        FOREIGN KEY (author_id)
        REFERENCES AUTHOR(author_id)
        ON DELETE CASCADE
);
