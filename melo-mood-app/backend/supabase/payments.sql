-- Melo Mood · subscriptions & payments
-- Entitlement lives here, never in a table the user can write to: clients may only READ
-- their own subscription row; every write goes through edge functions with the service role.
-- `source` is ready for App Store / Google Play: their webhooks will write the same row,
-- so one account keeps its plan across web, iOS and Android.

create table if not exists subscriptions (
  user_id             uuid primary key references auth.users(id) on delete cascade,
  tier                text not null check (tier in ('glow','muse')),
  plan                text not null,                                   -- glow_m | glow_y | muse_m
  status              text not null check (status in ('active','past_due','canceled')),
  source              text not null default 'ecpay' check (source in ('ecpay','apple','google')),
  merchant_trade_no   text,                                            -- ECPay recurring order this row follows
  current_period_end  timestamptz,                                     -- access lasts until here, even after cancel
  canceled_at         timestamptz,
  updated_at          timestamptz not null default now()
);

-- one row per checkout attempt: maps ECPay's MerchantTradeNo back to the user and the plan
-- that the SERVER priced (the amount is never taken from the client or the callback)
create table if not exists checkouts (
  merchant_trade_no   text primary key,
  user_id             uuid not null references auth.users(id) on delete cascade,
  plan                text not null,
  amount              int  not null,
  created_at          timestamptz not null default now()
);

-- raw audit log of every ECPay callback, valid or not
create table if not exists payment_events (
  id                  bigserial primary key,
  merchant_trade_no   text,
  kind                text not null,                                   -- first | period | rejected
  rtn_code            text,
  rtn_msg             text,
  amount              int,
  raw                 jsonb not null,
  dedupe              text,                                            -- one key per real authorization: ECPay retries callbacks
  received_at         timestamptz not null default now()
);
create index if not exists payment_events_trade on payment_events(merchant_trade_no, received_at desc);
create unique index if not exists payment_events_dedupe on payment_events(dedupe) where dedupe is not null;

alter table subscriptions  enable row level security;
alter table checkouts      enable row level security;
alter table payment_events enable row level security;

drop policy if exists "read own subscription" on subscriptions;
create policy "read own subscription" on subscriptions for select using (auth.uid() = user_id);
-- checkouts and payment_events have no policies: only the service role can touch them.
