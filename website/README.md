# PromptyDumpty Website

Static website for [PromptyDumpty](https://dumpty.dev) - Universal package manager for AI agent artifacts.

## Tech Stack

- **Vite** - Fast build tool and dev server
- **React** - UI library
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework

## Development

Install dependencies:

```bash
npm install
```

Start development server:

```bash
npm run dev
```

The site will be available at `http://localhost:5173`

**Note:** If running in a dev container, use the `--host` flag:
```bash
npm run dev -- --host
```

## Build

Build for production:

```bash
npm run build
```

The built files will be in the `dist/` directory.

Preview the production build:

```bash
npm run preview
```

**Note:** If running in a dev container, use the `--host` flag:
```bash
npm run preview -- --host
```

## Deployment

The site is deployed to **Cloudflare Pages** at **dumpty.dev**.

### Quick Deployment to Cloudflare Pages

1. **Connect to GitHub**
   - Go to Cloudflare Dashboard → Workers & Pages → Pages
   - Connect your GitHub repository

2. **Configure Build**
   - Build command: `cd website && npm install && npm run build`
   - Build output directory: `website/dist`
   - Framework preset: Vite

3. **Add Custom Domain**
   - Add `dumpty.dev` in the Custom domains tab
   - DNS is configured automatically if domain is on Cloudflare

See `DEPLOYMENT.md` for detailed instructions.

### Alternative Hosting

This static site can also be deployed to:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

## Project Structure

```
website/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable components
│   │   └── Layout.jsx   # Main layout with nav and footer
│   ├── pages/           # Page components
│   │   ├── Home.jsx
│   │   ├── GettingStarted.jsx
│   │   ├── CreatingPackages.jsx
│   │   └── Documentation.jsx
│   ├── App.jsx          # Main app component with routes
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
└── package.json         # Dependencies and scripts
```

## License

MIT
