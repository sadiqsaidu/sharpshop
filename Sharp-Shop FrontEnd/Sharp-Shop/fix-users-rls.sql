-- Add RLS policies for users table to allow public operations
-- This is needed for authentication to work properly

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow public insert on users" ON users;
DROP POLICY IF EXISTS "Allow public select on users" ON users;
DROP POLICY IF EXISTS "Allow public update on users" ON users;

-- Create policies for public access to users table
-- These are needed for authentication operations
CREATE POLICY "Allow public insert on users" 
  ON users FOR INSERT 
  WITH CHECK (true);

CREATE POLICY "Allow public select on users" 
  ON users FOR SELECT 
  USING (true);

CREATE POLICY "Allow public update on users" 
  ON users FOR UPDATE 
  USING (true);
