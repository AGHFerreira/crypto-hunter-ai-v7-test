-- Run in Supabase SQL Editor. RLS is mandatory: never disable it.
create table if not exists public.puzzles (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  title text not null check (char_length(title) between 1 and 120),
  source_url text not null,
  clues text not null default '',
  created_at timestamptz not null default now()
);
create table if not exists public.cases (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  scenario text not null check (scenario in ('wallet','exchange','file','seed')),
  backup text not null check (backup in ('unknown','yes','no')),
  description text not null check (char_length(description) between 1 and 1000),
  status text not null default 'new' check (status in ('new','review','closed')),
  created_at timestamptz not null default now()
);
alter table public.puzzles enable row level security;
alter table public.cases enable row level security;
-- Do not grant anonymous access. Each user can access only their own records.
create policy "puzzles_select_own" on public.puzzles for select to authenticated using ((select auth.uid()) = owner_id);
create policy "puzzles_insert_own" on public.puzzles for insert to authenticated with check ((select auth.uid()) = owner_id);
create policy "puzzles_delete_own" on public.puzzles for delete to authenticated using ((select auth.uid()) = owner_id);
create policy "cases_select_own" on public.cases for select to authenticated using ((select auth.uid()) = owner_id);
create policy "cases_insert_own" on public.cases for insert to authenticated with check ((select auth.uid()) = owner_id and status = 'new');
-- No update/delete for cases in the client. Admin workflows require a separate secure backend.
grant select,insert,delete on public.puzzles to authenticated;
grant select,insert on public.cases to authenticated;
