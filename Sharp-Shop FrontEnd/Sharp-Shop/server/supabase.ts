import { createClient } from '@supabase/supabase-js';

// Use SUPABASE_* for runtime (Heroku), fall back to VITE_SUPABASE_* for build/dev
const supabaseUrl = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_ANON_KEY || '';

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Missing Supabase environment variables. Using in-memory storage.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
