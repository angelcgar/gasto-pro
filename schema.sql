-- Tabla de usuarios

-- Eliminar la tabla de usuarios si existe
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;

-- Crear la tabla de usuarios
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    cash TEXT NOT NULL DEFAULT '0.00'
);

-- Tabla de transacciones (se usará más adelante)
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    amount TEXT NOT NULL,
    category TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

INSERT INTO categories (name) VALUES
  ('Food'),
  ('Transport'),
  ('Health'),
  ('Entertainment'),
  ('Utilities'),
  ('Education'),
  ('Savings'),
  ('Gifts'),
  ('Clothing'),
  ('Housing')
ON CONFLICT(name) DO NOTHING;
