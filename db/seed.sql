INSERT INTO books (isbn, title, author, genre, price, stock) VALUES
('978-0132350884', 'Clean Code', 'Robert C. Martin', 'Software Engineering', 33.99, 15),
('978-0201633610', 'Design Patterns', 'Erich Gamma', 'Software Engineering', 45.99, 8),
('978-0596007126', 'Head First Design Patterns', 'Eric Freeman', 'Software Engineering', 39.99, 12),
('978-020161622X', 'The Pragmatic Programmer', 'Andrew Hunt', 'Software Engineering', 42.99, 6),
('978-0134685991', 'Effective Java', 'Joshua Bloch', 'Programming', 38.99, 10),
('978-0596517748', 'JavaScript: The Good Parts', 'Douglas Crockford', 'Programming', 25.99, 20),
('978-1491950296', 'Programming Rust', 'Jim Blandy', 'Programming', 49.99, 5),
('978-0321125217', 'Domain-Driven Design', 'Eric Evans', 'Software Architecture', 52.99, 7),
('978-1492051725', 'Designing Data-Intensive Applications', 'Martin Kleppmann', 'Data Engineering', 44.99, 9),
('978-0137081073', 'The Clean Coder', 'Robert C. Martin', 'Software Engineering', 34.99, 11);

INSERT INTO customers (name, email, phone) VALUES
('Alice Johnson', 'alice@example.com', '555-0101'),
('Bob Smith', 'bob@example.com', '555-0102'),
('Charlie Brown', 'charlie@example.com', '555-0103'),
('Diana Prince', 'diana@example.com', '555-0104'),
('Eve Wilson', 'eve@example.com', '555-0105'),
('Frank Castle', 'frank@example.com', '555-0106');

INSERT INTO orders (customer_id, order_date, status) VALUES
(1, '2025-01-15 10:30:00', 'completed'),
(2, '2025-01-16 14:20:00', 'completed'),
(3, '2025-01-17 09:15:00', 'processing'),
(1, '2025-01-18 16:45:00', 'shipped');

INSERT INTO order_items (order_id, isbn, qty, price_at_purchase) VALUES
(1, '978-0132350884', 2, 33.99),
(1, '978-0596007126', 1, 39.99),
(2, '978-020161622X', 1, 42.99),
(2, '978-0134685991', 2, 38.99),
(3, '978-0596517748', 3, 25.99),
(4, '978-1492051725', 1, 44.99),
(4, '978-0321125217', 1, 52.99);