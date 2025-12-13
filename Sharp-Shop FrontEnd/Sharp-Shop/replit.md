# SharpShop - TikTok-Style E-Commerce Platform

## Overview

SharpShop is a mobile-first Progressive Web App (PWA) that provides a TikTok-style vertical scrolling shopping experience tailored for Nigerian traders. The application features an immersive, full-screen product showcase with snap-scroll navigation, designed specifically for Gen-Z users.

The frontend serves as a display layer for a headless WhatsApp CMS backend, where traders manage inventory via a WhatsApp bot. This creates a dynamic, real-time shopping experience with minimal overhead for small business owners.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Core Technology Stack:**
- **React 18** with **Vite** for fast development and optimized production builds
- **TypeScript** for type safety across the application
- **Tailwind CSS** for utility-first styling with custom design system
- **shadcn/ui** components (New York style) for consistent UI primitives
- **Framer Motion** for smooth animations and transitions
- **TanStack Query** (React Query) for server state management

**Design Pattern:**
The application implements a vertical feed pattern inspired by TikTok/Instagram Reels, featuring:
- Full-viewport product cards (100vh per product)
- CSS scroll-snap for mandatory single-product navigation
- Mobile-first responsive design with desktop "emulator mode" (max-width: 430px centered container)
- Overlay-based UI with gradient backgrounds for text readability over product images

**Routing:**
- Uses **Wouter** for lightweight client-side routing
- Single-page application structure with minimal route complexity

**Component Architecture:**
- Atomic design with reusable UI primitives from Radix UI
- Product-centric components: `ProductCard`, `StockIndicator`, `ActionButtons`, `ProductSkeleton`
- Separation of presentation and data-fetching logic

### Backend Architecture

**Server Framework:**
- **Express.js** with TypeScript for the API server
- HTTP server using Node's native `http` module with Vite middleware in development

**API Design:**
RESTful endpoints for product management:
- `GET /api/products` - Fetch all products
- `GET /api/products/:id` - Fetch single product
- `PATCH /api/products/:id/stock` - Update stock quantity

**Development vs Production:**
- Development: Vite dev server with HMR and middleware mode
- Production: Pre-built static assets served via Express

**Session Management:**
Basic infrastructure in place using `express-session` with potential for `connect-pg-simple` PostgreSQL session store (not actively implemented in current routes)

### Data Storage

**Database:**
- **PostgreSQL** configured via Drizzle ORM
- Connection managed through `DATABASE_URL` environment variable

**Schema Design (Drizzle):**

*Users Table:*
- `id` (UUID, auto-generated)
- `username` (unique text)
- `password` (text, hashed)

*Products Table:*
- `id` (UUID, auto-generated)
- `traderId` (foreign reference to user/trader)
- `name`, `price`, `description`, `imageUrl`
- `stockQuantity` (integer, default 0)
- `isActive` (boolean, default true)
- `whatsappNumber` (optional contact)

**Current Data Strategy:**
The application uses in-memory mock data during development (defined in `server/storage.ts`). The storage interface (`IStorage`) is designed to be swappable with a real database implementation.

**Migration Management:**
- Drizzle Kit configured for schema migrations
- Migrations output to `./migrations` directory
- Schema source: `./shared/schema.ts`

### Authentication & Authorization

**Current State:**
Authentication infrastructure is scaffolded but not actively enforced:
- User schema and insert validation defined via Zod
- No active authentication middleware on routes
- Passport.js dependencies present but not implemented

**Intended Pattern:**
Session-based authentication with:
- Local strategy (username/password)
- PostgreSQL session persistence via `connect-pg-simple`
- Rate limiting via `express-rate-limit`

### External Dependencies

**Third-Party UI Libraries:**
- **@radix-ui/** - Complete suite of accessible UI primitives (accordion, dialog, dropdown, popover, etc.)
- **shadcn/ui** - Pre-styled components built on Radix UI
- **lucide-react** - Icon library
- **react-icons** (specifically `SiWhatsapp` for WhatsApp branding)
- **embla-carousel-react** - Touch-friendly carousel component
- **vaul** - Drawer component library

**Data & Validation:**
- **zod** - Runtime schema validation
- **drizzle-zod** - Automatic Zod schema generation from Drizzle schemas
- **react-hook-form** with **@hookform/resolvers** - Form state management with Zod integration

**Styling & Animation:**
- **class-variance-authority** - Type-safe variant styling
- **clsx** & **tailwind-merge** - Conditional class merging
- **framer-motion** - Animation library for swipe gestures and transitions

**Developer Experience:**
- **@replit/** plugins for Vite (runtime error overlay, cartographer, dev banner)
- **tsx** - TypeScript execution for Node.js
- **esbuild** - Bundler for production server code

**External Services:**
- **WhatsApp Business API** (via web.whatsapp.com links) - Direct trader contact
- **Web Share API** - Native sharing functionality
- **Unsplash** - Product image CDN (currently used in mock data)

**Database & ORM:**
- **pg** - PostgreSQL client
- **drizzle-orm** - TypeScript ORM with type-safe query builder

**Potential Integrations (dependencies present but unused):**
- **Stripe** - Payment processing
- **OpenAI** / **@google/generative-ai** - AI features
- **nodemailer** - Email notifications
- **Multer** - File upload handling
- **JWT (jsonwebtoken)** - Token-based authentication
- **WebSocket (ws)** - Real-time updates
- **XLSX** - Spreadsheet import/export