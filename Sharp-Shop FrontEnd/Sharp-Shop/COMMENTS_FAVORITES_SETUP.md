# Comments and Favorites Setup Guide

## What's Been Done

✅ **Database Schema Created**
- `comments` table: Stores product comments with user info and emoji reactions
- `favorites` table: Stores user's favorited products (unique constraint prevents duplicates)
- Indexes added for better query performance
- Row Level Security (RLS) enabled with public read/write access

✅ **Backend API Routes Added**
- `GET /api/comments/:productId` - Get all comments for a product
- `POST /api/comments` - Add a new comment
- `DELETE /api/comments/:id` - Delete a comment
- `GET /api/favorites/:userId` - Get all favorites for a user
- `POST /api/favorites` - Add a product to favorites
- `DELETE /api/favorites` - Remove a product from favorites
- `GET /api/favorites/check/:productId/:userId` - Check if product is favorited

✅ **TypeScript Types Updated**
- Added `Comment`, `InsertComment`, `Favorite`, `InsertFavorite` types
- Updated storage interface with new methods
- Both SupabaseStorage and MemStorage implementations ready

## Setup Instructions

### Step 1: Run the SQL Script

1. Go to your Supabase dashboard: https://app.supabase.com
2. Navigate to **SQL Editor** → **New Query**
3. Copy the entire contents of `supabase-comments-favorites.sql`
4. Paste and click **Run**

This will:
- Create `comments` and `favorites` tables
- Add indexes for performance
- Enable Row Level Security
- Insert 15 sample comments across your products

### Step 2: Verify Tables Created

1. In Supabase dashboard, go to **Table Editor**
2. You should now see 5 tables total:
   - `products` ✓
   - `traders` ✓
   - `users` ✓
   - `comments` ✨ NEW
   - `favorites` ✨ NEW

3. Click on `comments` to see sample data

### Step 3: Restart Your Dev Server

```powershell
npm run dev
```

The API routes are now available!

## API Usage Examples

### Comments

**Get comments for a product:**
```typescript
const response = await fetch(`/api/comments/${productId}`);
const comments = await response.json();
```

**Add a comment:**
```typescript
await fetch('/api/comments', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    productId: 'prod_123',
    userId: 'user_456',
    userName: 'Chioma',
    userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=chioma',
    content: 'Looks great! Still available?',
    emojiReaction: '❤️' // optional
  })
});
```

**Delete a comment:**
```typescript
await fetch(`/api/comments/${commentId}`, {
  method: 'DELETE'
});
```

### Favorites

**Get user's favorites:**
```typescript
const response = await fetch(`/api/favorites/${userId}`);
const favorites = await response.json();
```

**Add to favorites:**
```typescript
await fetch('/api/favorites', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    productId: 'prod_123',
    userId: 'user_456'
  })
});
```

**Remove from favorites:**
```typescript
await fetch('/api/favorites', {
  method: 'DELETE',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    productId: 'prod_123',
    userId: 'user_456'
  })
});
```

**Check if favorited:**
```typescript
const response = await fetch(`/api/favorites/check/${productId}/${userId}`);
const { isFavorite } = await response.json();
```

## Frontend Integration

### Update use-favorites Hook

The existing `use-favorites.ts` hook can now be connected to the API instead of localStorage:

```typescript
// Example: Fetch favorites from API
const { data: favorites } = useQuery({
  queryKey: ['favorites', userId],
  queryFn: async () => {
    const res = await fetch(`/api/favorites/${userId}`);
    return res.json();
  }
});
```

### Update CommentSection Component

The `CommentSection.tsx` can now fetch real comments:

```typescript
const { data: comments } = useQuery({
  queryKey: ['comments', productId],
  queryFn: async () => {
    const res = await fetch(`/api/comments/${productId}`);
    return res.json();
  }
});
```

## Database Schema Details

### Comments Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| product_id | UUID | References products(id) |
| user_id | TEXT | User identifier |
| user_name | TEXT | Display name |
| user_avatar | TEXT | Avatar URL (optional) |
| content | TEXT | Comment text |
| emoji_reaction | TEXT | Emoji (optional) |
| created_at | TIMESTAMP | Auto-generated |

### Favorites Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| product_id | UUID | References products(id) |
| user_id | TEXT | User identifier |
| created_at | TIMESTAMP | Auto-generated |

**Constraint:** `UNIQUE(product_id, user_id)` prevents duplicate favorites

## Next Steps

1. **Run the SQL script** in Supabase dashboard
2. **Test the API endpoints** using browser DevTools or Postman
3. **Update frontend hooks** to use the new API instead of localStorage
4. **Update CommentSection** to fetch/display real comments from database
5. **Optional:** Add user authentication to link comments/favorites to real users

Enjoy your persistent comments and favorites! 🎉
