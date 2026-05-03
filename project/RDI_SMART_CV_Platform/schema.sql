-- ═══════════════════════════════════════════════════════════
--  RDI Smart CV Platform — PostgreSQL (Neon) Schema
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS users (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cvs (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_text    TEXT,
    parsed_json JSONB
);

CREATE TABLE IF NOT EXISTS profiles (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    final_data JSONB
);

-- Indexes for common lookup patterns
CREATE INDEX IF NOT EXISTS idx_cvs_user_id     ON cvs(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email      ON users(email);
