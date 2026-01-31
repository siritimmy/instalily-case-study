# PartSelect Assistant - NextJS Frontend

Modern chat interface for the PartSelect assistant, built with Next.js 14, TypeScript, and Tailwind CSS.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## Project Structure

```
instalily-nextjs/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main chat page
│   ├── globals.css          # Global styles
│   └── api/
│       ├── chat/
│       │   └── route.ts     # Proxy to FastAPI
│       └── health/
│           └── route.ts     # Health check
├── components/
│   ├── ChatWindow.tsx       # Main chat interface
│   ├── MessageBubble.tsx    # Message display
│   ├── PartCard.tsx         # Product card
│   └── LoadingIndicator.tsx # Loading animation
├── lib/
│   ├── api.ts               # API client
│   └── types.ts             # TypeScript types
└── public/                  # Static assets
```

## Components

### ChatWindow
Main chat interface component with:
- Message history
- Real-time input
- Loading states
- Auto-scroll to latest message
- Enter-to-send keyboard support

### MessageBubble
Displays individual messages with:
- Markdown rendering
- User/Assistant styling
- Product card integration
- Proper spacing and bubbles

### PartCard
Product display card with:
- Product images
- Part number and manufacturer
- Price and stock status
- Link to PartSelect.com
- Hover effects

### LoadingIndicator
Animated loading indicator showing:
- Animated dots
- "Thinking..." message

## Styling

Using **Tailwind CSS** with PartSelect branding colors:
- Primary Blue: `#003366` (partselect-blue)
- CTA Orange: `#FF6600` (partselect-orange)
- Light Gray: `#F5F5F5` (partselect-gray)

## Environment Variables

Create `.env.local`:
```
FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

## API Integration

The frontend communicates with the FastAPI backend through:

1. **NextJS API Route** (`/api/chat`)
   - Proxies requests to FastAPI
   - Handles CORS
   - Returns structured JSON

2. **FastAPI Backend** (`http://localhost:8000`)
   - Processes chat with Pydantic AI agent
   - Returns message + parts array

## Build & Deploy

Development:
```bash
npm run dev
```

Build for production:
```bash
npm run build
npm start
```

Vercel deployment:
```bash
vercel deploy
```

## Features

✅ Real-time chat interface
✅ Product display with images
✅ Markdown support
✅ Loading states
✅ Error handling
✅ Responsive design
✅ PartSelect branding
✅ TypeScript support
✅ Tailwind CSS styling

## Performance

- Uses client-side state management with hooks
- Auto-scroll optimized with refs
- Image fallback handling
- Responsive grid layout
- CSS-based animations

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Tips

### Adding New Components
1. Create in `components/` directory
2. Use TypeScript interfaces from `lib/types.ts`
3. Import and use in ChatWindow or other components

### Styling
- Use Tailwind classes for styling
- Custom colors defined in `tailwind.config.ts`
- Global styles in `app/globals.css`

### API Changes
- Update types in `lib/types.ts`
- Modify API calls in `lib/api.ts`
- Update NextJS route handler in `app/api/chat/route.ts`

## Testing

No test suite yet. To add:
```bash
npm install -D @testing-library/react jest @testing-library/jest-dom
```

Then create `.test.tsx` files for components.

## Troubleshooting

**Chat not sending:**
- Check backend is running on port 8000
- Check browser console for errors
- Verify FASTAPI_URL is correct

**No product images:**
- Check image URLs from backend
- Images may require CORS headers from PartSelect

**Styling looks wrong:**
- Clear `.next` folder: `rm -rf .next`
- Rebuild: `npm run build`

**Type errors:**
```bash
npm run build
```

## Next Steps

1. Add conversation history persistence
2. Implement streaming responses
3. Add message editing/deletion
4. Add search/filter for chat history
5. Add user authentication
6. Add analytics
7. Optimize for mobile
