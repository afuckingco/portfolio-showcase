// ===== Supabase Database Client (CRUD) with localStorage fallback =====
import { FEATURE_FLAGS } from '../utils/constants.js';
import * as localDb from './storage.js';
import { generateId } from '../utils/helpers.js';
import { buildSeedTemples } from './seed.js';

const SEED_INSTALLED_KEY = 'injicho_seed_v1';

function maybeInstallSeed() {
  try {
    if (localStorage.getItem(SEED_INSTALLED_KEY)) return;
    const existing = localDb.loadTemples();
    if (existing.length > 0) {
      localStorage.setItem(SEED_INSTALLED_KEY, '1');
      return;
    }
    localDb.saveTemples(buildSeedTemples());
    localStorage.setItem(SEED_INSTALLED_KEY, '1');
  } catch (e) {
    console.warn('Seed install skipped:', e);
  }
}

let supabase = null;

async function getClient() {
  if (!FEATURE_FLAGS.USE_SUPABASE) return null;
  if (supabase) return supabase;

  const url = import.meta.env.VITE_SUPABASE_URL;
  const key = import.meta.env.VITE_SUPABASE_ANON_KEY;
  if (!url || !key) {
    console.warn('Supabase env vars missing, falling back to localStorage');
    return null;
  }

  const { createClient } = await import('@supabase/supabase-js');
  supabase = createClient(url, key);
  return supabase;
}

export async function fetchTemples() {
  if (!FEATURE_FLAGS.USE_SUPABASE) maybeInstallSeed();
  const client = await getClient();
  if (!client) return localDb.loadTemples();

  const { data, error } = await client
    .from('temples')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Supabase fetch error, falling back to localStorage:', error);
    return localDb.loadTemples();
  }
  return data;
}

export async function createTemple(temple) {
  const client = await getClient();
  const withId = { ...temple, id: temple.id || generateId(), createdAt: new Date().toISOString() };

  if (!client) {
    const temples = localDb.loadTemples();
    temples.push(withId);
    localDb.saveTemples(temples);
    return withId;
  }

  const { data, error } = await client.from('temples').insert([withId]).select().single();
  if (error) throw error;
  return data;
}

export async function updateTemple(id, updates) {
  const client = await getClient();

  if (!client) {
    const temples = localDb.loadTemples();
    const idx = temples.findIndex((t) => t.id === id);
    if (idx === -1) throw new Error('Temple not found');
    temples[idx] = { ...temples[idx], ...updates, updatedAt: new Date().toISOString() };
    localDb.saveTemples(temples);
    return temples[idx];
  }

  const { data, error } = await client
    .from('temples')
    .update({ ...updates, updated_at: new Date().toISOString() })
    .eq('id', id)
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function deleteTemple(id) {
  const client = await getClient();

  if (!client) {
    const temples = localDb.loadTemples().filter((t) => t.id !== id);
    localDb.saveTemples(temples);
    return true;
  }

  const { error } = await client.from('temples').delete().eq('id', id);
  if (error) throw error;
  return true;
}

export async function isSupabaseEnabled() {
  const client = await getClient();
  return client !== null;
}
