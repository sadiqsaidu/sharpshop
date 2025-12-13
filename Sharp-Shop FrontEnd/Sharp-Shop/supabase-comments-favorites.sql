-- Create comments table
CREATE TABLE IF NOT EXISTS comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  user_name TEXT NOT NULL,
  user_avatar TEXT,
  content TEXT NOT NULL,
  emoji_reaction TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create favorites table
CREATE TABLE IF NOT EXISTS favorites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
  UNIQUE(product_id, user_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_comments_product_id ON comments(product_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_favorites_product_id ON favorites(product_id);
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);

-- Enable Row Level Security
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow public read access on comments" ON comments;
DROP POLICY IF EXISTS "Allow public insert on comments" ON comments;
DROP POLICY IF EXISTS "Allow users to delete own comments" ON comments;
DROP POLICY IF EXISTS "Allow public read access on favorites" ON favorites;
DROP POLICY IF EXISTS "Allow public insert on favorites" ON favorites;
DROP POLICY IF EXISTS "Allow users to delete own favorites" ON favorites;

-- Create policies for comments
CREATE POLICY "Allow public read access on comments" 
  ON comments FOR SELECT USING (true);

CREATE POLICY "Allow public insert on comments" 
  ON comments FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow users to delete own comments" 
  ON comments FOR DELETE USING (true);

-- Create policies for favorites
CREATE POLICY "Allow public read access on favorites" 
  ON favorites FOR SELECT USING (true);

CREATE POLICY "Allow public insert on favorites" 
  ON favorites FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow users to delete own favorites" 
  ON favorites FOR DELETE USING (true);

-- Insert some sample comments
INSERT INTO comments (product_id, user_id, user_name, user_avatar, content, emoji_reaction) 
SELECT 
  p.id,
  'user_' || (random() * 1000)::int,
  CASE (random() * 5)::int
    WHEN 0 THEN 'Chioma'
    WHEN 1 THEN 'Emeka'
    WHEN 2 THEN 'Fatima'
    WHEN 3 THEN 'Tunde'
    WHEN 4 THEN 'Ngozi'
    ELSE 'Ade'
  END,
  'https://api.dicebear.com/7.x/avataaars/svg?seed=' || (random() * 1000)::int,
  CASE (random() * 4)::int
    WHEN 0 THEN 'This looks amazing! Is it still available?'
    WHEN 1 THEN 'What''s the exact condition?'
    WHEN 2 THEN 'Can you send more pictures?'
    WHEN 3 THEN 'Great price! 🔥'
    ELSE 'Interested! Can we negotiate?'
  END,
  CASE (random() * 6)::int
    WHEN 0 THEN '❤️'
    WHEN 1 THEN '🔥'
    WHEN 2 THEN '👍'
    WHEN 3 THEN '😍'
    WHEN 4 THEN '👀'
    ELSE NULL
  END
FROM products p
LIMIT 15;
