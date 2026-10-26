USE registration;

INSERT INTO AUTHOR (author_id, name, country)
VALUES
(1, 'Ahmed Khaled Tawfik', 'Egypt'),
(2, 'Naguib Mahfouz', 'Egypt'),
(3, 'William Shakespeare', 'England');

INSERT INTO BOOK (book_id, title, price, author_id)
VALUES
(1, 'Utopia', 150.00, 1),
(2, 'The Blue Elephant', 200.00, 1),
(3, 'Palace Walk', 180.00, 2),
(4, 'The Thief and the Dogs', 160.00, 2),
(5, 'Hamlet', 120.00, 3),
(6, 'Macbeth', 130.00, 3);