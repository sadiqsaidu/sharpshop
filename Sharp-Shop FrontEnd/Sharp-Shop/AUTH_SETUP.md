# Authentication Setup Guide

## Overview
SharpShop now has a complete role-based access control (RBAC) system with authentication for Buyers and Sellers.

## Database Setup

1. **Run the SQL migration script in Supabase SQL Editor:**
   ```bash
   # Execute the contents of supabase-auth.sql in your Supabase project
   ```

2. **The migration adds:**
   - `email`, `role`, `full_name`, `business_name` columns to the `users` table
   - Updates the `traders` table with `user_id`, `business_name`, `whatsapp_number`, `address`
   - Creates necessary indexes for performance
   - Sets up Row Level Security (RLS) policies

## Features

### User Roles
- **Buyer**: Browse products, add favorites, comment, and like products
- **Seller**: All buyer features + ability to create trader profiles with business information

### Authentication Flow

1. **Registration**:
   - Users choose between Buyer or Seller during signup
   - Buyers provide: username, email (optional), full name (optional), password
   - Sellers provide: username, email (optional), business name, WhatsApp number (optional), address (optional), password
   - Passwords are hashed using `bcryptjs` with 10 salt rounds
   - Seller accounts automatically create a linked trader profile

2. **Login**:
   - Username and password authentication
   - Session-based authentication using express-session
   - Sessions stored in memory (can be upgraded to database storage for production)

3. **Session Management**:
   - Sessions last 7 days
   - Secure cookies in production
   - Automatic session restoration on page reload

## API Endpoints

### Authentication Routes
- `POST /api/register` - Create new user account
- `POST /api/login` - Authenticate user
- `POST /api/logout` - End user session
- `GET /api/user` - Get current authenticated user

### Request/Response Examples

**Register (Buyer)**:
```json
POST /api/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "role": "buyer",
  "fullName": "John Doe"
}
```

**Register (Seller)**:
```json
POST /api/register
{
  "username": "tech_store",
  "email": "store@example.com",
  "password": "securePassword123",
  "role": "seller",
  "businessName": "Tech Store NG",
  "whatsappNumber": "2348123456789",
  "address": "Lagos, Nigeria"
}
```

**Login**:
```json
POST /api/login
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

## Frontend Components

### AuthContext (`client/src/contexts/AuthContext.tsx`)
- React context for managing authentication state
- Provides `user`, `login`, `register`, `logout`, `isLoading`
- Automatically checks authentication on app load

### AuthModal (`client/src/components/AuthModal.tsx`)
- Beautiful overlay modal with blur backdrop
- Switches between Login and Signup modes
- Role selection for Buyers vs Sellers
- Dynamic form fields based on selected role
- Form validation and error handling
- Smooth animations using Framer Motion

### Usage Example:
```tsx
import { useAuth } from '@/contexts/AuthContext';
import { AuthModal } from '@/components/AuthModal';

function MyComponent() {
  const { user, logout } = useAuth();
  const [showAuth, setShowAuth] = useState(false);

  return (
    <>
      {user ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <button onClick={() => setShowAuth(true)}>Login</button>
      )}
      <AuthModal isOpen={showAuth} onClose={() => setShowAuth(false)} />
    </>
  );
}
```

## Security Features

- **Password Hashing**: bcryptjs with 10 salt rounds
- **Session Security**: HTTP-only cookies, secure flag in production
- **Input Validation**: Zod schemas for type-safe validation
- **CSRF Protection**: Can be added via csurf middleware (optional)
- **RLS Policies**: Supabase Row Level Security for data access control

## Environment Variables

Required in `.env`:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
SESSION_SECRET=your_random_secret_key_here
```

## Next Steps

1. **Execute the SQL migration** in Supabase
2. **Test the authentication flow**:
   - Register as a buyer
   - Register as a seller
   - Login/logout
   - Check session persistence
3. **Optional enhancements**:
   - Add password reset functionality
   - Implement email verification
   - Add OAuth providers (Google, Facebook)
   - Upgrade session store to PostgreSQL for production
   - Add rate limiting to prevent brute force attacks

## Production Considerations

- Replace MemoryStore with connect-pg-simple for session storage
- Enable HTTPS and set `secure: true` for cookies
- Add rate limiting middleware
- Implement proper error logging
- Add email verification for new accounts
- Consider adding 2FA for seller accounts
- Regular security audits

## Testing

Test the authentication flow:
1. Open the app
2. Click "Login" button in the header
3. Switch to "Sign up" mode
4. Select "Seller" role
5. Fill in business information
6. Register and verify the session persists
7. Logout and login again
