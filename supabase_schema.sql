-- ============================================================
--  Period Pallete  · Supabase SQL Schema  (safe to re-run anytime)
--  Drops all existing policies before recreating them.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Tables (CREATE IF NOT EXISTS — safe to re-run) ──────────

CREATE TABLE IF NOT EXISTS profiles (
    id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name          TEXT,
    dob           DATE,
    cycle_length  INT DEFAULT 28,
    period_length INT DEFAULT 5,
    language      TEXT DEFAULT 'English',
    region        TEXT DEFAULT 'United States',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cycle_logs (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    log_date   DATE NOT NULL,
    type       TEXT NOT NULL CHECK (type IN ('period','ovulation','spotting')),
    notes      TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS symptom_logs (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    log_date   DATE NOT NULL,
    log_time   TIME,
    category   TEXT NOT NULL,
    name       TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notes (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title      TEXT NOT NULL,
    content    TEXT,
    category   TEXT DEFAULT 'General',
    cycle_day  INT,
    tags       TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skin_logs (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    log_date   DATE NOT NULL,
    rating     INT CHECK (rating BETWEEN 1 AND 10),
    notes      TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role       TEXT NOT NULL CHECK (role IN ('user','assistant')),
    content    TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Enable RLS ───────────────────────────────────────────────

ALTER TABLE profiles      ENABLE ROW LEVEL SECURITY;
ALTER TABLE cycle_logs    ENABLE ROW LEVEL SECURITY;
ALTER TABLE symptom_logs  ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes         ENABLE ROW LEVEL SECURITY;
ALTER TABLE skin_logs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- ── Drop ALL existing policies first (safe re-run) ───────────

DO $$ DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT policyname, tablename
        FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename IN (
            'profiles','cycle_logs','symptom_logs',
            'notes','skin_logs','chat_messages'
          )
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I', r.policyname, r.tablename);
    END LOOP;
END $$;

-- ── Recreate policies ────────────────────────────────────────

-- profiles: split into SELECT / INSERT / UPDATE so fresh sessions can insert
CREATE POLICY "profiles_select" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "profiles_insert" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "profiles_update" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- all other tables: single FOR ALL policy is fine
CREATE POLICY "cycle_logs_all"    ON cycle_logs    FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "symptom_logs_all"  ON symptom_logs  FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "notes_all"         ON notes         FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "skin_logs_all"     ON skin_logs     FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "chat_messages_all" ON chat_messages FOR ALL USING (auth.uid() = user_id);
