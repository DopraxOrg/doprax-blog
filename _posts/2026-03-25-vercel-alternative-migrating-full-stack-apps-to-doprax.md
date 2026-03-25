---
layout: post
title: "Vercel Alternative: Migrating Full-Stack Apps to Doprax"
date: 2026-03-25 08:38:51
author: n8n-bot
---

# Vercel Alternative: Migrating Full-Stack Apps to Doprax

If you’ve built a full-stack app on Vercel — Next.js, Remix, Astro, or even a custom Express + React stack — and now need more control, predictable pricing, real infrastructure ownership, or support for long-running processes, background jobs, or custom binaries, you’re not alone. Developers are increasingly hitting Vercel’s limits: cold starts on serverless functions, lack of persistent storage, opaque scaling behavior, and billing that spikes with traffic — not usage.

Doprax is a developer-first cloud platform built *for* the moment after “it works locally.” It’s not another static host or edge-rendering wrapper. It’s real infrastructure — VMs and containers — deployed in minutes, managed automatically, and priced hourly, pay-as-you-go. No abstraction tax. No vendor lock-in. Just your code, running where you choose.

Let’s walk through what migrating a full-stack app from Vercel to Doprax actually looks like — step by step, with zero hand-waving.

---

## Why Developers Choose Doprax Over Vercel (and Why It’s Not Just “Another Host”)

Vercel excels at frontend previews and edge-optimized static sites. But when your app evolves — adding WebSockets, Redis-backed queues, a PostgreSQL instance, scheduled cron jobs, or GPU-accelerated inference — Vercel’s architecture becomes a constraint, not an accelerator.

Here’s how Doprax differs — concretely:

| Feature | Vercel | Doprax |
|---|---|---|
| **Runtime model** | Stateless serverless functions (max 30s, no persistent memory) | Full Linux VMs (ProVM) *or* containerized App Spaces — both support long-lived processes, cron, systemd, custom daemons |
| **Storage & state** | External only (Vercel Storage, third-party DBs) | Built-in managed PostgreSQL & Redis (one-click), plus optional block storage volumes attached to ProVMs |
| **Networking** | Edge routing only; no inbound TCP/UDP beyond HTTP(S) | Full inbound/outbound TCP/UDP, configurable firewalls, private networking between services |
| **Pricing model** | Usage-based: function invocations × duration × memory × region | Hourly, transparent: $0.012/hr for a 1vCPU/1GB RAM ProVM (Hetzner), $0.024/hr for 2vCPU/4GB (UpCloud). You pay only while it runs. |
| **Custom binaries & tooling** | Not supported (no shell access, no `apt`, no Dockerfiles) | Full root access on ProVMs. Install FFmpeg, Rust, CUDA, WireGuard, or your own CLI tool — no approval needed. |
| **Multi-cloud deployment** | Single-cloud (AWS/GCP under the hood) | Deploy across Hetzner, DigitalOcean, OVH, Vultr, Gcore, and UpCloud — same CLI, same UI, same billing. |

This isn’t theoretical. Teams use Doprax to run:
- Real-time collaboration backends (WebSockets + Redis pub/sub),
- Scraping APIs with headless Chromium (via Puppeteer on ProVM),
- Self-hosted AI inference servers (Llama.cpp, Ollama, vLLM),
- Private VPN gateways and proxy clusters,
- And yes — production Next.js apps with ISR, API routes, and middleware — but with full control over caching headers, TLS config, and request timeouts.

The shift isn’t about rejecting abstractions — it’s about choosing *which* abstractions serve *your* stack, not someone else’s roadmap.

---

## Step-by-Step: Migrating a Next.js Full-Stack App

Let’s assume you have a standard Next.js 14+ app with:
- `app/` router
- API routes (`/app/api/...`)
- Server Components using `fetch()` to a local `/api` endpoint
- A simple PostgreSQL database (e.g., via Neon or Supabase)

Here’s how to move it to Doprax — end to end.

### ✅ Step 1: Provision Your Runtime Environment

Go to the Doprax dashboard → **App Spaces** → **Create New Space**.

Choose:
- Provider: `Hetzner` (lowest cost, great for dev/staging)
- Region: `Falkenstein` (EU) or `Helsinki` (low latency, high uptime)
- Size: `1vCPU / 2GB RAM` (enough for most Next.js apps under ~10k req/day)
- Stack: Select **Next.js (Node.js 20)** — this auto-configures Nginx, PM2, and build hooks.

No SSH keys. No `docker-compose.yml`. No `terraform` required.

> 💡 Pro tip: You can also deploy the *same* app as a **ProVM**, if you need custom init scripts, `systemd` services, or full disk control. The App Builder supports both.

### ✅ Step 2: Connect Your Git Repo & Configure Build

In the App Builder:
- Link your GitHub/GitLab repo.
- Set branch: `main`
- Set build command: `npm run build` (or `pnpm build`, `bun build`)
- Set start command: `npm start` (or `pnpm start`, `bun start`)

Doprax detects Next.js automatically and sets optimal defaults:
- `.next/` output directory
- `PORT` and `NODE_ENV=production` injected
- Automatic cache reuse across builds (node_modules, `.next/cache`)

Unlike Vercel’s “build isolation,” Doprax caches intelligently — cutting average build time by 40–60% for repeat deploys.

### ✅ Step 3: Add Your Database (Optional but Recommended)

Click **Add Service** → **PostgreSQL**.

Choose:
- Version: `15`
- Size: `1vCPU / 2GB RAM / 25GB SSD` ($0.028/hr)
- Enable backups: ✅

Doprax generates a connection string like:
```
postgresql://doprax_user:abc123@postgres-xyz123.doprax.internal:5432/myapp
```

✅ This URL is only reachable *within your private network* — no public exposure.

Update your Next.js `lib/db.ts` or `prisma/schema.prisma` to use it. No firewall rules. No VPC peering setup. It just works.

### ✅ Step 4: Set Environment Variables (Securely)

Go to the **Environment Variables tab** in your App Space.

Add:
- `DATABASE_URL` → paste the PostgreSQL connection string
- `NEXT_PUBLIC_API_URL` → `https://your-app.doprax.app/api` (or your custom domain)
- `SECRET_KEY` → generate with `openssl rand -base64 32`

All values are encrypted at rest and injected at runtime — never exposed in build logs.

### ✅ Step 5: Deploy & Verify

Click **Deploy Now**.

Within 90 seconds:
- Code pulled
- Dependencies installed
- Build completed
- App started
- Health check passed
- HTTPS certificate provisioned (via Let’s Encrypt, auto-renewed)

Visit `https://your-app.doprax.app`. Your app loads — identical UX, but now running on *your* infrastructure.

You’ll see:
- Real-time logs in the dashboard (including `console.log()` from API routes and Server Components)
- CPU/RAM/network metrics per-second
- One-click SSH access (if needed)
- Instant rollback to any previous deploy

No waiting for “edge cache warmup.” No guessing why a route 504’d. No digging through Vercel’s opaque function logs.

---

## What About Custom Backends? (Express, Fastify, Nest, etc.)

Doprax doesn’t force Next.js. You can migrate *any* Node.js full-stack app — or Python (FastAPI, Django), Go (Fiber, Gin), Rust (Axum), or PHP (Laravel) — using the same flow.

Just select the right base image in the App Builder:
- `Node.js (Express)`
- `Python (uvicorn)`
- `Go (binary)`
- `Custom Dockerfile`

Then point the build command to your entrypoint and set the port.

Example: Migrating a Fastify + PostgreSQL backend:
- Build command: `npm ci && npm run build`
- Start command: `node dist/index.js`
- Port: `3000`
- Environment: `DATABASE_URL`, `PORT=3000`

That’s it. Doprax handles reverse proxying, TLS, health checks, and zero-downtime rolling updates.

---

## Cost Comparison: Vercel Pro vs. Doprax ProVM (Real Numbers)

Let’s compare a realistic staging environment:

| Resource | Vercel Pro (Starter) | Doprax (Hetzner) |
|---|---|---|
| Compute (1vCPU / 2GB RAM equivalent) | $20/mo base + $0.0000125/request × 500k req/mo = **$46.25** | **$8.64/mo** (24/7) or **$0.43/mo** (1hr/day) |
| PostgreSQL (managed) | $25/mo (Neon Pro) | $20.16/mo (1vCPU/2GB/25GB) |
| Bandwidth (100GB) | Included | Included |
| Custom domain + HTTPS | Included | Included |
| **Total (staging, 24/7)** | **$71.25/mo** | **$28.80/mo** |
| **Total (dev, 1hr/day)** | Still $20/mo (minimum) | **$0.43/mo** |

💡 On Doprax, you pay only for what you *run*. Spin down your staging VM overnight? You stop paying. Scale up for load testing? Pay only for those extra hours. No minimums. No surprise invoices.

---

## You Own It. Really.

Vercel gives you a URL and logs. Doprax gives you infrastructure — with full sovereignty.

- Your app runs on *your* VM or container, not a shared tenant.
- You choose the provider, region, kernel version, and OS patch cadence.
- You can SSH in, `strace` a process, `tcpdump` traffic, or attach `gdb`.
- You export data anytime — no lock-in, no proprietary format.
- You deploy the same way to Hetzner *and* UpCloud — no rewrite needed.

This isn’t “infrastructure as code” that takes weeks to learn. It’s infrastructure as *click* — then *control*.

---

## Ready to Migrate?

Migrating your full-stack app from Vercel to Doprax takes less than 10 minutes — and pays for itself in predictability, performance, and peace of mind.

👉 **[Deploy your first App Space now](https://app.doprax.com/spaces/new)**  
No credit card. No trial period. Just real infrastructure — ready when you are.

Need help? Join our [Discord](https://discord.gg/doprax) or [Telegram](https://t.me/doprax) — real engineers answer questions, not bots. We’ll help you migrate — free.

And if you’re building something open source, let us know. We sponsor OSS projects with free infrastructure. Because better tools shouldn’t come with trade-offs.