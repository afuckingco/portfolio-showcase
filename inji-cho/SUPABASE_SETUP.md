# Supabase Setup (MUST FOLLOW if using cloud sync)

Inji-cho works fully offline on localStorage. This guide is only needed if you want data synced to the cloud / shared across devices.

## 1. Create a project
1. Go to https://supabase.com and create a new project.
2. Note your Project URL and anon/public API key (Project Settings → API).

## 2. Run the schema

In the Supabase SQL editor, run:

```sql
-- Enable PostGIS for geographic queries
create extension if not exists postgis;

create table if not exists temples (
  id text primary key,
  name text not null,
  prefecture text,
  region text,
  lat double precision not null,
  lng double precision not null,
  notes text,
  address text,
  visited boolean default false,
  visit_date date,
  location geography(Point, 4326) generated always as (
    st_setsrid(st_makepoint(lng, lat), 4326)
  ) stored,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists temples_location_idx
  on temples using gist (location);

-- Phase 2: photo attachments
create table if not exists photos (
  id text primary key,
  temple_id text references temples(id) on delete cascade,
  url text not null,
  caption text,
  created_at timestamptz default now()
);

-- Row-Level Security
alter table temples enable row level security;
alter table photos enable row level security;

create policy "Allow all for authenticated users"
  on temples for all
  using (true)
  with check (true);

create policy "Allow all for authenticated users on photos"
  on photos for all
  using (true)
  with check (true);
```

> The default policies above are permissive for single-user/personal use. If you plan to share the app publicly, tighten these policies to scope rows by `auth.uid()`.

## 3. Configure the app

In `.env.local`:
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
VITE_USE_SUPABASE=true
```

Restart the dev server after changing these values.

## 4. Verify

1. Add a temple in the app.
2. Check the Supabase Table Editor → `temples` table — the row should appear.
3. Refresh the app — data should load from Supabase, not localStorage.

## 5. Migrating existing localStorage data

If you already have temples saved locally and want to move them to Supabase:
1. In the app (with `VITE_USE_SUPABASE=false`), click **Export JSON**.
2. Set `VITE_USE_SUPABASE=true` and restart.
3. Use **Import JSON** to re-import the backup — this writes each temple into Supabase via the same `createTemple` path.
