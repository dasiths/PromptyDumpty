# Website Deployment Guide

This guide covers deploying the PromptyDumpty website to **dumpty.dev** using **Cloudflare Pages**.

## Prerequisites

- Domain: `dumpty.dev` (registered with Cloudflare)
- Cloudflare account
- GitHub repository access

## Cloudflare Pages Deployment

### Step 1: Verify Domain Setup

Since `dumpty.dev` is registered with Cloudflare, your domain is already configured correctly:

1. Log into [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Verify `dumpty.dev` appears in your list of domains
3. Click on `dumpty.dev` to view the overview
4. Confirm DNS is active (status should show as "Active")

**Benefits of using Cloudflare as your registrar:**
- ✅ DNS is automatically configured
- ✅ No nameserver changes needed
- ✅ Instant propagation when adding custom domains
- ✅ At-cost pricing with no markup
- ✅ Integrated domain and hosting management

### Step 2: Create Cloudflare Pages Project

1. **Navigate to Pages**
   - In Cloudflare Dashboard, go to **Workers & Pages** → **Pages**
   - Click **Create application** → **Pages** → **Connect to Git**

2. **Connect GitHub Repository**
   - Click **Connect GitHub**
   - Authorize Cloudflare to access your repositories
   - Select the **PromptyDumpty** repository

3. **Configure Build Settings**
   - **Project name:** `promptydumpty-website` (or your preference)
   - **Production branch:** `main`
   - **Build command:** `cd website && npm install && npm run build`
   - **Build output directory:** `website/dist`
   - **Root directory (Path):** `/` (leave as default)
   - **Deploy command:** Leave empty or clear this field (not needed for static sites)
   - **Framework preset:** Vite (optional, auto-detected)

4. **Environment Variables** (if needed)
   - Click **Add variable** if you need any environment variables
   - For this static site, none are required

5. **Deploy**
   - Click **Save and Deploy**
   - Cloudflare will build and deploy your site
   - First deployment takes 2-5 minutes

### Step 3: Configure Custom Domain

1. **Add Custom Domain**
   - Once deployed, go to your Pages project
   - Click **Custom domains** tab
   - Click **Set up a custom domain**
   - Enter `dumpty.dev`
   - Click **Continue**

2. **DNS Configuration (Automatic!)**
   - Since `dumpty.dev` is registered with Cloudflare, DNS configuration is **instant and automatic**
   - Cloudflare creates a CNAME record pointing to your Pages project
   - No waiting for DNS propagation
   - No manual DNS record creation needed
   - Changes are live immediately!

3. **Add www subdomain** (optional but recommended)
   - Click **Set up a custom domain** again
   - Enter `www.dumpty.dev`
   - Cloudflare will create the DNS record automatically and instantly

4. **SSL/TLS Settings**
   - Cloudflare automatically provisions SSL certificates
   - In your domain's **SSL/TLS** settings, ensure mode is set to **Full** or **Full (strict)**
   - Enable **Always Use HTTPS** under SSL/TLS → Edge Certificates
   - SSL certificate is provisioned instantly since domain and hosting are both on Cloudflare

### Step 4: Verify Deployment

1. Visit `https://dumpty.dev` immediately (no DNS propagation wait needed!)
2. Verify the site loads correctly
3. Test all pages and navigation
4. Check that HTTPS is working (padlock icon in browser)

## Automatic Deployments

Cloudflare Pages automatically deploys when you push to GitHub:

- **Production deployments:** Any push to the `main` branch
- **Preview deployments:** Pull requests get their own preview URLs
- **Build logs:** Available in the Cloudflare Dashboard under your project

To trigger a deployment:
```bash
git add .
git commit -m "Update website"
git push origin main
```

Cloudflare will automatically:
1. Detect the push
2. Build the site
3. Deploy to production
4. Make it live at dumpty.dev

## Cloudflare Pages Features

### Performance
- ✅ Global CDN with 275+ locations
- ✅ HTTP/3 and QUIC support
- ✅ Brotli compression
- ✅ Automatic image optimization
- ✅ Smart routing and caching

### Security
- ✅ Free SSL certificates (auto-renewal)
- ✅ DDoS protection
- ✅ Web Application Firewall (WAF)
- ✅ Bot management

### Developer Experience
- ✅ Unlimited bandwidth (on Free plan!)
- ✅ Unlimited requests
- ✅ 500 builds per month (Free plan)
- ✅ Preview deployments for pull requests
- ✅ Rollback to previous deployments

## Alternative Hosting Options

If you need to use a different hosting provider:

### Netlify

1. Connect repository at [netlify.com](https://netlify.com)
2. Build command: `cd website && npm install && npm run build`
3. Publish directory: `website/dist`
4. Add custom domain in settings

### Vercel

1. Import project at [vercel.com](https://vercel.com)
2. Root directory: `website`
3. Build command: `npm run build`
4. Output directory: `dist`
5. Add custom domain in project settings

### GitHub Pages

1. **Build the Site Locally**
   ```bash
   cd website
   npm install
   npm run build
   ```

2. **Configure for GitHub Pages**
   
   Update `website/vite.config.js` if deploying to a repository path:
   ```js
   export default defineConfig({
     plugins: [react()],
     base: '/', // Use '/' for custom domain, or '/PromptyDumpty/' for repo path
   })
   ```

3. **Deploy Using GitHub Actions**
   
   Create `.github/workflows/deploy-website.yml`:
   ```yaml
   name: Deploy Website
   
   on:
     push:
       branches: [main]
       paths:
         - 'website/**'
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Setup Node
           uses: actions/setup-node@v3
           with:
             node-version: 18
             
         - name: Install and Build
           run: |
             cd website
             npm install
             npm run build
             
         - name: Deploy to GitHub Pages
           uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./website/dist
             cname: dumpty.dev
   ```

4. **Configure Repository**
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` / root
   - Save

5. **Configure DNS**
   ```
   Type: A
   Name: @
   Value: 185.199.108.153
   
   Type: A
   Name: @
   Value: 185.199.109.153
   
   Type: A
   Name: @
   Value: 185.199.110.153
   
   Type: A
   Name: @
   Value: 185.199.111.153
   
   Type: CNAME
   Name: www
   Value: <username>.github.io
   ```

## DNS Configuration with Cloudflare

Since `dumpty.dev` is registered with Cloudflare:

✅ **DNS is completely automatic!** When you add a custom domain in Pages, Cloudflare instantly creates the necessary DNS records.

✅ **No propagation delay** - Changes are live immediately since domain registration and DNS are integrated.

✅ **No manual configuration** - Cloudflare handles everything automatically.

**Verify DNS:**
```bash
dig dumpty.dev
```

You should see Cloudflare's IP addresses in the response.

**View DNS Records:**
- Go to **DNS** → **Records** in your Cloudflare Dashboard
- You'll see the CNAME record(s) created automatically by Pages

## Post-Deployment Optimization

### Performance Optimization

Cloudflare automatically handles most optimizations, but you can enhance further:

1. **Enable Auto Minify**
   - Go to **Speed** → **Optimization**
   - Enable JavaScript, CSS, and HTML minification

2. **Enable Rocket Loader** (optional)
   - Speeds up JavaScript loading
   - May need testing with React apps

3. **Configure Caching**
   - Go to **Caching** → **Configuration**
   - Set caching level to "Standard" or "Aggressive"

4. **Verify Performance**
   - Test with [PageSpeed Insights](https://pagespeed.web.dev/)
   - Test with [WebPageTest](https://www.webpagetest.org/)
   - Target: 90+ scores on both mobile and desktop

### Security Settings

1. **Always Use HTTPS**
   - Go to **SSL/TLS** → **Edge Certificates**
   - Enable **Always Use HTTPS**
   - Enable **Automatic HTTPS Rewrites**

2. **Enable HSTS** (optional, after testing)
   - In **SSL/TLS** → **Edge Certificates**
   - Enable **HTTP Strict Transport Security (HSTS)**

3. **Security Headers**
   - Cloudflare Pages automatically adds security headers
   - Check headers at [securityheaders.com](https://securityheaders.com)

### Monitoring

1. **Cloudflare Analytics**
   - Built-in analytics in your Cloudflare Dashboard
   - View traffic, performance, and security metrics

2. **Set Up Alerts** (optional)
   - Configure notifications for deployment failures
   - Set up health checks if needed

3. **External Monitoring** (optional)
   - [UptimeRobot](https://uptimerobot.com/) for uptime monitoring
   - [Sentry](https://sentry.io/) for error tracking

## Local Preview

Before deploying, always test locally:

```bash
cd website
npm install
npm run build
npm run preview
```

Visit `http://localhost:4173` to preview the production build.

## Troubleshooting

### Build Failures

**Check build logs:**
1. Go to your Pages project in Cloudflare Dashboard
2. Click on the failed deployment
3. View the build logs

**Common issues:**
- **Node version:** Cloudflare uses Node 18 by default (compatible with this project)
- **Build command:** Ensure it's `cd website && npm install && npm run build`
- **Output directory:** Must be `website/dist`
- **Path issues:** Make sure build command includes `cd website`

### Site Not Loading

**Verify deployment:**
```bash
# Check DNS
dig dumpty.dev

# Check HTTPS
curl -I https://dumpty.dev
```

**Steps:**
1. Ensure deployment shows as "Success" in Cloudflare Dashboard
2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
3. Try incognito/private browsing mode
4. Wait a few minutes for CDN cache to update

### Styles Not Working

**Causes:**
- Browser cache showing old version
- Tailwind CSS not building properly
- Build output directory incorrect

**Solutions:**
1. Check build logs for CSS processing errors
2. Verify `tailwind.config.js` exists in `website/` folder
3. Clear browser cache
4. Do a hard refresh

### Routing Issues (404 on page refresh)

Cloudflare Pages automatically handles SPA routing for React apps. If you see 404s:

1. Check that you're using React Router correctly
2. Ensure `index.html` is in the root of `website/dist`
3. Try adding a `_redirects` file (usually not needed):
   ```
   /* /index.html 200
   ```

### Custom Domain Not Working

**If dumpty.dev isn't resolving:**
1. Verify domain shows as "Active" in Cloudflare Dashboard
2. Ensure custom domain is added in Pages project settings
3. Check DNS records in **DNS** → **Records** (should see CNAME automatically created)
4. Try clearing browser cache or using incognito mode
5. Since domain is with Cloudflare, no DNS propagation wait is needed - issues are usually cache-related

**Check DNS records:**
- Go to **DNS** → **Records** in Cloudflare
- Should see a CNAME record for `dumpty.dev` pointing to your Pages project
- Record should be proxied (orange cloud icon)

### Deployment Not Triggering

**If pushes to main don't trigger builds:**
1. Verify GitHub connection in Pages settings
2. Check if GitHub webhook exists (Pages → Settings → GitHub webhook)
3. Manually trigger a deployment from Cloudflare Dashboard
4. Check GitHub webhook delivery logs

## Cloudflare Pages Pricing

**Free Tier** (more than sufficient for this project):
- ✅ Unlimited bandwidth
- ✅ Unlimited requests
- ✅ 500 builds per month
- ✅ 1 concurrent build
- ✅ Global CDN
- ✅ Free SSL certificates
- ✅ DDoS protection

**Paid Plans** ($20/month Pro):
- 5,000 builds per month
- 5 concurrent builds
- Advanced analytics
- Priority support

**For the PromptyDumpty website, the free tier is perfect!**

## Quick Reference

### Build Settings
```
Project name: promptydumpty-website
Production branch: main
Build command: cd website && npm install && npm run build
Build output directory: website/dist
Root directory (Path): / (default)
Deploy command: (leave empty)
Framework preset: Vite
Node version: 18 (default)
```

### Useful Commands
```bash
# Test locally before deploying
cd website
npm install
npm run build
npm run preview

# Check DNS
dig dumpty.dev

# Test HTTPS
curl -I https://dumpty.dev

# View build logs
# (Go to Cloudflare Dashboard → Pages → Your Project → Deployments)
```

### Important URLs
- **Cloudflare Dashboard:** https://dash.cloudflare.com
- **Pages Documentation:** https://developers.cloudflare.com/pages/
- **Your Pages Project:** https://dash.cloudflare.com → Workers & Pages → Pages
- **DNS Settings:** https://dash.cloudflare.com → Your Domain → DNS
