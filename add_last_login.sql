-- Aggiungi la colonna last_login alla tabella users
ALTER TABLE users ADD COLUMN last_login DATETIME NULL AFTER updated_at;

