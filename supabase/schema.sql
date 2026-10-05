create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  full_name text,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.datasets (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  dataset_name text not null, row_count integer not null, column_count integer not null, created_at timestamptz not null default now()
);
create table if not exists public.analysis_runs (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  dataset_id uuid references public.datasets(id) on delete set null, algorithm text not null, number_of_clusters integer, silhouette_score numeric, created_at timestamptz not null default now()
);
alter table public.profiles enable row level security;
alter table public.datasets enable row level security;
alter table public.analysis_runs enable row level security;
create policy "own profile" on public.profiles for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "own datasets" on public.datasets for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own analyses" on public.analysis_runs for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
