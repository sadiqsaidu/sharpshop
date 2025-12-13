-- Create likes table
CREATE TABLE IF NOT EXISTS likes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  UNIQUE(product_id, user_id)
);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_likes_product_id ON likes(product_id);
CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);

-- Enable Row Level Security
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow public read access on likes" ON likes;
DROP POLICY IF EXISTS "Allow public insert on likes" ON likes;
DROP POLICY IF EXISTS "Allow users to delete own likes" ON likes;

-- Create policies for likes
CREATE POLICY "Allow public read access on likes" 
  ON likes FOR SELECT USING (true);

CREATE POLICY "Allow public insert on likes" 
  ON likes FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow users to delete own likes" 
  ON likes FOR DELETE USING (true);

-- Insert some sample likes for existing products
INSERT INTO likes (product_id, user_id)
SELECT 
  p.id,
  'user_' || floor(random() * 1000)::text
FROM products p
CROSS JOIN generate_series(1, floor(random() * 5)::int + 1)
ON CONFLICT (product_id, user_id) DO NOTHING;
