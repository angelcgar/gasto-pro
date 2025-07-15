-- Tabla de usuarios

-- Eliminar la tabla de usuarios si existe
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;

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
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type TEXT NOT NULL, -- 'income' o 'expense'
    FOREIGN KEY (user_id) REFERENCES users(id)
);
