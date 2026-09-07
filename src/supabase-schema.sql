-- Impaginatore Storie ABF · schema Supabase (progetto mtcauaazprruxngbcspu)
-- Da incollare UNA volta in: Supabase → SQL Editor → New query → Run.
-- Crea: tabella foto, tabella storico impaginazioni, bucket privato "photos",
-- e regole di accesso: solo utenti loggati (l'account condiviso) leggono e scrivono.

create table if not exists public.photos (
  id     text primary key,
  path   text not null,
  added  bigint not null,
  used   integer not null default 0
);

create table if not exists public.layouts (
  id      text primary key,
  date    bigint not null,
  copy    text,
  stories jsonb not null,
  updated bigint not null
);

alter table public.photos  enable row level security;
alter table public.layouts enable row level security;

drop policy if exists "auth all" on public.photos;
create policy "auth all" on public.photos
  for all to authenticated using (true) with check (true);

drop policy if exists "auth all" on public.layouts;
create policy "auth all" on public.layouts
  for all to authenticated using (true) with check (true);

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('photos', 'photos', false, 8000000, array['image/jpeg','image/png','image/webp'])
on conflict (id) do nothing;

drop policy if exists "photos auth select" on storage.objects;
create policy "photos auth select" on storage.objects
  for select to authenticated using (bucket_id = 'photos');
drop policy if exists "photos auth insert" on storage.objects;
create policy "photos auth insert" on storage.objects
  for insert to authenticated with check (bucket_id = 'photos');
drop policy if exists "photos auth update" on storage.objects;
create policy "photos auth update" on storage.objects
  for update to authenticated using (bucket_id = 'photos');
drop policy if exists "photos auth delete" on storage.objects;
create policy "photos auth delete" on storage.objects
  for delete to authenticated using (bucket_id = 'photos');
