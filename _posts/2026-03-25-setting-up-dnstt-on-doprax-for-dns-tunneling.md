---
layout: post
title: "Setting up DNSTT on Doprax for DNS Tunneling"
date: 2026-03-25 08:38:49
author: n8n-bot
---

# Setting Up DNSTT on Doprax for DNS Tunneling

DNSTT (DNS Tunneling Tool) lets you route encrypted traffic over DNS — ideal for constrained or filtered networks. On Doprax, you deploy it in minutes — no manual server setup, no SSH config.

### ✅ What You’ll Need  
- A Doprax account  
- A domain with full DNS control (to point `*.tunnel.yourdomain.com` to your Doprax ProVM’s IP)  
- Basic familiarity with `dnstt-server` and `dnstt-client` (open-source, MIT-licensed)

### 🚀 How to Deploy  
1. In the Doprax dashboard, launch a **ProVM** (Hetzner, Vultr, or OVH recommended for low-latency DNS).  
2. In the **App Builder**, select *Custom Docker* and paste the official [`dnstt-server`](https://github.com/zeyu2001/dnstt) image:  
   ```dockerfile
   zeyu2001/dnstt-server:latest
   ```  
3. Set required **Environment Variables** (on the *Environment Variables tab*):  
   - `DNSTT_PRIVATE_KEY` — your generated Ed25519 private key (base64-encoded)  
   - `DNSTT_DOMAIN` — e.g., `tunnel.yourdomain.com`  
   - `DNSTT_PORT` — `53` (or `5353` if port 53 is blocked)  
4. Enable **UDP port 53** (or custom port) in *Firewall Settings*.  
5. Click *Deploy*. Done.

Your DNSTT server is live in <60 seconds. Use `dnstt-client` anywhere with your public key and domain to tunnel traffic securely.

For advanced use (TLS fallback, DoH/DoT proxy mode), see our [DNSTT Advanced Patterns](/docs/dnstt-advanced) guide.

→ [Launch your first DNSTT ProVM now](https://app.doprax.com/new/provm)