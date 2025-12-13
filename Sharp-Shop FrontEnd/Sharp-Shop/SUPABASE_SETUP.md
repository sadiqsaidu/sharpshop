# Supabase Setup Instructions

## Step 1: Execute SQL in Supabase Dashboard

1. Go to your Supabase dashboard: https://app.supabase.com
2. Select your project: **fywblsxaiayxdmklwvax**
3. Navigate to **SQL Editor** in the left sidebar
4. Click **New Query**
5. Copy the entire contents of `supabase-setup.sql` and paste it into the editor
6. Click **Run** to execute the script

This will create:
- `products` table with 8 sample products
- `traders` table with 4 sample traders
- `users` table (for future authentication)
- Row Level Security (RLS) policies for public read access

## Step 2: Verify Tables Created

1. In the Supabase dashboard, navigate to **Table Editor**
2. You should see three new tables:
   - `products`
   - `traders`
   - `users`
3. Click on `products` and verify you see 8 rows of sample data
4. Click on `traders` and verify you see 4 rows of trader data

## Step 3: Restart Your Dev Server

1. Stop your current dev server (Ctrl+C)
2. Run: `npm run dev`
3. The app will now automatically use Supabase for data storage!

## Step 4: Test the Integration

1. Open http://localhost:5000
2. You should see the same products, but now loaded from Supabase
3. Check your browser's Network tab to see API calls to Supabase
4. Try filtering by category - data should load from your cloud database

## Troubleshooting

### If products don't load:
1. Check the browser console for errors
2. Verify your `.env` file has the correct credentials:
   ```
   VITE_SUPABASE_URL=https://fywblsxaiayxdmklwvax.supabase.co
   VITE_SUPABASE_ANON_KEY=your_anon_key
   ```
3. Make sure you ran the SQL setup script completely
4. Check the Supabase dashboard → API → API Settings to verify your credentials

### If you see "Failed to fetch":
1. Check your internet connection
2. Verify the Supabase project is active
3. Check the RLS policies are enabled (should allow public read access)

## Next Steps (Optional)

Once basic integration is working, you can:
1. **Add image upload** - Use Supabase Storage for product images
2. **Enable authentication** - Set up user login/signup
3. **Real-time updates** - Use Supabase subscriptions for live data
4. **Persist favorites** - Store user favorites in the database
5. **Add comments** - Create a comments table linked to products
