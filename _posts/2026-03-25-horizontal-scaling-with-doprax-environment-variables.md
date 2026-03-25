---
layout: post
title: "Horizontal Scaling with Doprax Environment Variables"
date: 2026-03-25 08:38:53
author: n8n-bot
---

# Horizontal Scaling with Doprax Environment Variables

Horizontal scaling on Doprax is simple: deploy multiple identical instances of your service (e.g., via App Spaces or ProVM), and use **Environment Variables** — configured once in the **Environment Variables tab** of your App Builder or Main Service — to keep them in sync.

No manual config drift. No SSH into each node. Just define `DATABASE_URL`, `REDIS_HOST`, `API_KEY`, or any custom variable — and it’s instantly available across all running replicas.

Because environment variables are decoupled from infrastructure, you scale up (or down) without reconfiguring code or redeploying. Add 10 more instances? They inherit the same vars — automatically.

✅ Works across App Spaces, ProVM, and AI Agent deployments  
✅ Syncs instantly — no restarts needed for most services  
✅ Securely encrypted at rest and in transit  

[Learn how to set environment variables in the App Builder](/docs/app-builder/environment-variables)  
[See horizontal scaling in action with a load-balanced Node.js app](/docs/guides/horizontal-scaling)  

Deploy more. Configure less.