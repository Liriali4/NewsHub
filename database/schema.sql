-- ========================================
-- NewsHub — SQLite Database Schema
-- Utilizadores, Preferências, Favoritos
-- ========================================

-- Tabela: users
-- Armazena os utilizadores registados
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Index para buscar por email (autenticação)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);


-- Tabela: preferences
-- Categorias preferidas de cada utilizador (relação 1:N)
-- Utiliza cascade delete para remover automaticamente ao apagar utilizador
CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, category)  -- um utilizador não pode ter a mesma categoria duas vezes
);

-- Index para busca rápida por utilizador
CREATE INDEX IF NOT EXISTS idx_preferences_user ON preferences(user_id);


-- Tabela: favorites
-- Artigos guardados por cada utilizador
-- URL é única por utilizador (não pode duplicar)
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    url_to_image TEXT,
    source_name TEXT,
    published_at TEXT,
    category TEXT,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, url)  -- um utilizador não pode guardar o mesmo artigo duas vezes
);

-- Indexes para buscas rápidas
CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_saved ON favorites(saved_at DESC);
