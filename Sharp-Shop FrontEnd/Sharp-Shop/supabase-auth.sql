-- Update users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS email TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS role TEXT NOT NULL DEFAULT 'buyer',
ADD COLUMN IF NOT EXISTS full_name TEXT,
ADD COLUMN IF NOT EXISTS business_name TEXT;

-- Update traders table structure
ALTER TABLE traders
DROP COLUMN IF EXISTS name,
DROP COLUMN IF EXISTS username,
DROP COLUMN IF EXISTS location;

-- First check the actual type of users.id
DO $$ 
BEGIN
  -- Add user_id column with UUID type to match users.id
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'traders' AND column_name = 'user_id'
  ) THEN
    ALTER TABLE traders ADD COLUMN user_id UUID REFERENCES users(id);
  END IF;
  
  -- Add business_name
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'traders' AND column_name = 'business_name'
  ) THEN
    ALTER TABLE traders ADD COLUMN business_name TEXT NOT NULL DEFAULT '';
  END IF;
  
  -- Add whatsapp_number
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'traders' AND column_name = 'whatsapp_number'
  ) THEN
    ALTER TABLE traders ADD COLUMN whatsapp_number TEXT;
  END IF;
  
  -- Add address
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'traders' AND column_name = 'address'
  ) THEN
    ALTER TABLE traders ADD COLUMN address TEXT;
  END IF;
END $$;

-- Create index for user lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_traders_user_id ON traders(user_id);

-- Update RLS policies for users
DROP POLICY IF EXISTS "Allow public read access on users" ON users;
CREATE POLICY "Allow public read access on users" 
  ON users FOR SELECT USING (true);

CREATE POLICY "Allow public insert on users" 
  ON users FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow users to update own profile" 
  ON users FOR UPDATE USING (true); -- In real app, check auth.uid() = id

-- Update RLS policies for traders
DROP POLICY IF EXISTS "Allow public read access on traders" ON traders;
CREATE POLICY "Allow public read access on traders" 
  ON traders FOR SELECT USING (true);

CREATE POLICY "Allow public insert on traders" 
  ON traders FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow traders to update own profile" 
  ON traders FOR UPDATE USING (true);
