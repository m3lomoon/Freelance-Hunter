-- Melo Mood · Glow / Muse server features: real-voice synthesis, voice clones, AI usage.
-- Like subscriptions, none of these tables are user-writable: edge functions use the
-- service role. Users may read their own usage and clone row; journals are never stored.

-- one synthesized sentence per (voice, settings, text); shared by every user of that voice
create table if not exists tts_lines (
  voice_id    text not null,
  text_hash   text not null,                 -- sha256(model|speed|text)
  audio_path  text not null,                 -- object in the private "tts" bucket
  chars       int  not null,
  created_at  timestamptz not null default now(),
  primary key (voice_id, text_hash)
);

-- Muse: at most one ElevenLabs clone per user; the recording itself is not kept
create table if not exists voice_clones (
  user_id     uuid primary key references auth.users(id) on delete cascade,
  voice_id    text not null,
  consent_at  timestamptz not null,
  created_at  timestamptz not null default now()
);

-- monthly meters behind the fair-use caps
create table if not exists usage_monthly (
  user_id     uuid not null references auth.users(id) on delete cascade,
  month       text not null,                 -- YYYY-MM (Asia/Taipei)
  tts_chars   int  not null default 0,
  ai_calls    int  not null default 0,
  primary key (user_id, month)
);

alter table tts_lines     enable row level security;
alter table voice_clones  enable row level security;
alter table usage_monthly enable row level security;

drop policy if exists "read own clone" on voice_clones;
create policy "read own clone" on voice_clones for select using (auth.uid() = user_id);
drop policy if exists "read own usage" on usage_monthly;
create policy "read own usage" on usage_monthly for select using (auth.uid() = user_id);
-- tts_lines has no policies: only the service role reads or writes it.

-- atomic meter bump; only the service role may call it
create or replace function bump_usage(p_user uuid, p_month text, p_chars int, p_calls int)
returns usage_monthly
language sql
security definer
set search_path = public
as $$
  insert into usage_monthly (user_id, month, tts_chars, ai_calls)
  values (p_user, p_month, greatest(p_chars, 0), greatest(p_calls, 0))
  on conflict (user_id, month) do update
    set tts_chars = usage_monthly.tts_chars + greatest(excluded.tts_chars, 0),
        ai_calls  = usage_monthly.ai_calls  + greatest(excluded.ai_calls, 0)
  returning *;
$$;
revoke all on function bump_usage(uuid, text, int, int) from public, anon, authenticated;
grant execute on function bump_usage(uuid, text, int, int) to service_role;

-- private bucket for synthesized audio; served only through short-lived signed URLs
insert into storage.buckets (id, name, public)
values ('tts', 'tts', false)
on conflict (id) do nothing;
