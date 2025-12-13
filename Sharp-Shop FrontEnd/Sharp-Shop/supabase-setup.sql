-- Create products table
CREATE TABLE IF NOT EXISTS products (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  trader_id TEXT NOT NULL,
  trader_name TEXT NOT NULL DEFAULT 'SharpShop Trader',
  name TEXT NOT NULL,
  price INTEGER NOT NULL,
  description TEXT NOT NULL,
  image_url TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'Electronics',
  stock_quantity INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT true,
  whatsapp_number TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create traders table
CREATE TABLE IF NOT EXISTS traders (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  username TEXT UNIQUE,
  bio TEXT,
  location TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable Row Level Security
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE traders ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Allow public read access on products" ON products;
DROP POLICY IF EXISTS "Allow public read access on traders" ON traders;

-- Create policies for public read access
CREATE POLICY "Allow public read access on products" 
  ON products FOR SELECT USING (true);

CREATE POLICY "Allow public read access on traders" 
  ON traders FOR SELECT USING (true);

-- Insert sample products
INSERT INTO products (trader_id, trader_name, name, price, description, image_url, category, stock_quantity, is_active, whatsapp_number) VALUES
  ('trader_001', 'SneakerHub NG', 'Nike Air Max 97', 85000, 'Brand new Nike Air Max 97 in Silver Bullet colorway. Size 42 available. Original box and receipt included. Perfect for sneaker enthusiasts looking for authentic footwear.', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80', 'Footwear', 5, true, '2348174930608'),
  ('trader_001', 'SneakerHub NG', 'iPhone 14 Pro Max', 750000, 'Factory unlocked iPhone 14 Pro Max, 256GB Deep Purple. Battery health 100%. Comes with charger and case. No scratches or dents.', 'https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=800&q=80', 'Electronics', 2, true, '2348174930608'),
  ('trader_002', 'VintageVibes Lagos', 'Vintage Denim Jacket', 25000, 'Classic oversized vintage denim jacket. Unisex, fits M-XL. Slight distressing for that authentic vintage look. Perfect for layering.', 'https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=800&q=80', 'Fashion', 8, true, '2348174930608'),
  ('trader_002', 'VintageVibes Lagos', 'MacBook Pro M2', 1200000, 'Apple MacBook Pro 14-inch M2 Pro chip, 16GB RAM, 512GB SSD. Space Gray. Used for only 3 months, in pristine condition with AppleCare+.', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80', 'Electronics', 1, true, '2348174930608'),
  ('trader_003', 'LuxeAccessories', 'Designer Sunglasses', 45000, 'Ray-Ban Aviator Classic sunglasses. Gold frame with green G-15 lenses. Comes with original case and cleaning cloth. 100% authentic.', 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800&q=80', 'Accessories', 0, true, '2348174930608'),
  ('trader_003', 'LuxeAccessories', 'Sony WH-1000XM5', 180000, 'Sony WH-1000XM5 wireless noise-canceling headphones in Black. Industry-leading ANC, 30-hour battery life. Barely used, with all accessories.', 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800&q=80', 'Electronics', 3, true, '2348174930608'),
  ('trader_001', 'SneakerHub NG', 'Adidas Yeezy Boost 350', 120000, 'Authentic Adidas Yeezy Boost 350 V2 ''Zebra''. Size 44. Deadstock with tags. Verified through CheckCheck app.', 'https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=800&q=80', 'Footwear', 2, true, '2348174930608'),
  ('trader_004', 'TimePiece Gallery', 'Luxury Watch Collection', 350000, 'Premium automatic watch with sapphire crystal. Swiss movement, stainless steel case. Water resistant to 100m. Perfect gift.', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80', 'Accessories', 4, true, '2348174930608');

-- Insert sample traders
INSERT INTO traders (id, name, username, bio, location) VALUES
  ('trader_001', 'SneakerHub NG', 'sneakerhubng_official', 'Premium sneakers and electronics. Authentic products only. 🇳🇬', 'Lagos, Nigeria'),
  ('trader_002', 'VintageVibes Lagos', 'vintagevibeslgos_official', 'Vintage fashion and tech. Quality you can trust. 🌟', 'Lagos, Nigeria'),
  ('trader_003', 'LuxeAccessories', 'luxeaccessories_official', 'Designer accessories and premium electronics. 💎', 'Abuja, Nigeria'),
  ('trader_004', 'TimePiece Gallery', 'timepiecegallery_official', 'Luxury watches and timepieces. Elegance redefined. ⌚', 'Port Harcourt, Nigeria');
