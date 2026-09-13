-- Melo Mood · Supabase schema (Postgres)
-- Run with: supabase db push  (or paste into the SQL editor)

create extension if not exists "pgcrypto";

-- ---------- profiles ----------
create table if not exists profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  name          text not null default '',
  goals         text[] not null default '{}',          -- wealth | music | love | health | confidence | creative
  tone          text not null default 'gentle',        -- gentle | firm | baddie
  plan          text not null default 'free',          -- free | glow | muse
  voice_id      text,                                  -- ElevenLabs voice id (null until cloned)
  voice_sample  text,                                  -- storage path of the consent recording
  voice_consent_at timestamptz,                        -- explicit consent timestamp (required for cloning)
  created_at    timestamptz not null default now()
);

-- ---------- journal ----------
create table if not exists journal_entries (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references profiles(id) on delete cascade,
  entry_date  date not null,
  mood        smallint not null check (mood between 1 and 5),
  gratitude   text[] not null default '{}',
  note        text not null default '',
  tags        text[] not null default '{}',
  created_at  timestamptz not null default now(),
  unique (user_id, entry_date)
);
create index if not exists journal_user_date on journal_entries(user_id, entry_date desc);

-- ---------- generated scripts ----------
create table if not exists scripts (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references profiles(id) on delete cascade,
  kind        text not null check (kind in ('manifest','sleep')),
  goal        text,
  tone        text,
  minutes     smallint,
  lines       jsonb not null,                          -- [{t, kind, pause}]
  source      text not null default 'template',        -- template | claude
  audio_path  text,                                    -- storage path once synthesized
  created_at  timestamptz not null default now()
);

-- ---------- sessions (listening) ----------
create table if not exists sessions (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references profiles(id) on delete cascade,
  script_id   uuid references scripts(id) on delete set null,
  kind        text not null,
  minutes     smallint not null,
  completed   boolean not null default false,
  started_at  timestamptz not null default now()
);

-- ---------- TTS cache: one synthesis per (voice, sentence) ----------
create table if not exists tts_cache (
  voice_id    text not null,
  text_hash   text not null,                           -- sha256 of normalized sentence
  audio_path  text not null,
  chars       int  not null,
  created_at  timestamptz not null default now(),
  primary key (voice_id, text_hash)
);

-- ---------- RLS ----------
alter table profiles        enable row level security;
alter table journal_entries enable row level security;
alter table scripts         enable row level security;
alter table sessions        enable row level security;

create policy "own profile"  on profiles        for all using (auth.uid() = id)      with check (auth.uid() = id);
create policy "own journal"  on journal_entries for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own scripts"  on scripts         for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own sessions" on sessions        for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- tts_cache is only touched by edge functions with the service role key.

-- ---------- storage buckets ----------
-- voice-samples (private): consent recordings, deletable by user
-- audio (private, signed URLs): synthesized scripts + cache
insert into storage.buckets (id, name, public) values ('voice-samples','voice-samples',false) on conflict do nothing;
insert into storage.buckets (id, name, public) values ('audio','audio',false) on conflict do nothing;

-- ---------- streak helper ----------
create or replace function current_streak(uid uuid) returns int language sql stable as $$
  with days as (
    select distinct entry_date d from journal_entries where user_id = uid
    union
    select distinct started_at::date from sessions where user_id = uid
  ), numbered as (
    select d, row_number() over (order by d desc) - 1 as n from days
  )
  select count(*)::int from numbered where d = current_date - n;
$$;
