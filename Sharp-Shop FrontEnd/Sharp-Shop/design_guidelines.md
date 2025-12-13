# SharpShop Frontend Design Guidelines

## Design Approach
**Reference-Based: TikTok/Instagram Reels Vertical Scrolling Pattern**

This application draws inspiration from TikTok's immersive vertical scrolling experience, adapted for e-commerce. The design prioritizes full-screen visual impact with minimal UI chrome, allowing products to speak for themselves while maintaining high conversion through strategic placement of action elements.

---

## Core Design Principles

1. **Immersive Product Showcase**: Each product occupies 100% of the viewport height
2. **Frictionless Discovery**: Vertical scroll-snap navigation (one product at a time)
3. **Gen-Z Visual Language**: Bold, high-contrast, mobile-native design
4. **Information Hierarchy**: Critical data (price, stock) always visible, secondary info expandable

---

## Layout System

### Viewport Strategy
- **Mobile**: Full viewport width and height (100vw × 100vh per product)
- **Desktop**: Emulator mode - centered container (max-width: 430px) with backdrop blur or dark overlay outside the container
- **Scroll Behavior**: CSS scroll-snap (y-mandatory) - users snap to exactly one product card at a time

### Spacing Primitives
Use Tailwind units: **2, 4, 6, 8** for consistent spacing
- Component padding: p-4 to p-6
- Element gaps: gap-2 to gap-4
- Bottom safe area: pb-8 to pb-12 (accounts for mobile navigation bars)

---

## Typography

### Hierarchy
1. **Product Name**: Bold, large (text-2xl to text-3xl), white, high letter-spacing for impact
2. **Price**: Extra bold (text-3xl to text-4xl), white, use ₦ symbol prominently
3. **Stock Indicator**: Medium weight (text-sm to text-base), white with background badge for visibility
4. **Description**: Regular weight (text-sm), white, with "...more" truncation

### Font Selection
- Primary: System font stack optimized for Nigerian market (SF Pro Display, Segoe UI, Roboto)
- Weight range: 400 (regular), 600 (semibold), 700 (bold), 800 (extrabold for prices)

---

## Visual Hierarchy & Overlay System

### Background Layer
- Full-screen product image (object-cover, object-center)
- Aspect ratio: Fill entire viewport regardless of image dimensions

### Gradient Overlay
- Linear gradient from transparent (top 60%) to black/dark (bottom 40%)
- Purpose: Ensure white text readability over any image
- Opacity: Gradient should be subtle but effective (rgba(0,0,0,0) to rgba(0,0,0,0.8))

### Floating UI Positioning
All interactive elements and text float at the **bottom third** of the screen:
- Product info cluster: Bottom 25-30% of viewport
- Action buttons: Fixed bottom row with safe-area padding
- Vertical stacking order (bottom to top): Buttons → Stock → Price → Name

---

## Component Library

### ProductCard
**Structure**: Full-screen container with layered content
- Background: Product image (100vh)
- Overlay: Gradient mask
- Content zone: Absolute positioned at bottom

**Elements**:
1. Product Name: Top of content cluster, bold white text with subtle text-shadow for legibility
2. Price Tag: Prominent ₦ format (e.g., ₦45,000), use comma separators
3. Stock Indicator: Badge-style with background (e.g., "Only 2 left", "Sold Out")
4. Description: Truncated to 2-3 lines with "...more" expander that reveals full text in modal or expanded state

### Action Buttons
**Layout**: Horizontal row at bottom with equal spacing
1. **Buy Now**: Primary CTA, full visual weight, blurred background (backdrop-blur-md with bg-white/20)
2. **Share**: Secondary style, native Web Share API icon
3. **WhatsApp**: Direct chat link, branded green accent

**Button Treatment**:
- All buttons on images: Blurred backgrounds (backdrop-blur-md)
- No custom hover states needed (Button component handles this)
- High contrast against gradient overlay

### Stock Status Indicators
**Critical Visibility Requirements**:
- "In Stock": Subtle green badge
- "Low Stock" (≤3 items): Amber/orange badge with quantity
- "Sold Out": Prominent red badge, disable Buy button

**Real-time Ready**: Design assumes instant state changes without page refresh

---

## Loading States
Use skeleton screens matching ProductCard structure:
- Shimmer effect on gradient background
- Placeholder blocks for name, price, button positions
- Smooth fade-in when product data loads

---

## Images

### Product Images
- **Placement**: Full viewport background for each product card
- **Requirements**: High-quality product photos, minimum 1080px width
- **Fallback**: Gradient placeholder if image fails to load
- **Treatment**: No filters or overlays on images themselves (only bottom gradient)

### Mock Data Image Sources
Use Unsplash with product-relevant keywords:
- Shoes: `https://source.unsplash.com/featured/?sneakers,shoes`
- Electronics: `https://source.unsplash.com/featured/?phone,gadget`
- Fashion: `https://source.unsplash.com/featured/?fashion,clothing`

---

## Animations

**Minimal, Purposeful Motion**:
- Swipe transitions: Smooth scroll snap (native CSS, no custom animations)
- Description expansion: Simple slide-down with Framer Motion
- Stock status changes: Subtle pulse on badge when stock updates
- Button press: Native touch feedback

**Avoid**: Heavy parallax, distracting transitions, auto-play carousels

---

## Desktop Emulator Mode

### Container
- Max-width: 430px
- Centered horizontally and vertically
- Box shadow for depth

### Backdrop
- Full viewport dark overlay (bg-black/80) OR
- Backdrop blur effect (backdrop-blur-xl)
- Prevents desktop layout feeling "stretched"

---

## Accessibility Considerations

- High contrast text (white on dark gradient)
- Touch targets minimum 44px × 44px for all buttons
- Disabled state for "Sold Out" products (reduced opacity, no pointer events)
- Native scroll behavior respects user motion preferences
- Screen reader: Announce stock status changes dynamically