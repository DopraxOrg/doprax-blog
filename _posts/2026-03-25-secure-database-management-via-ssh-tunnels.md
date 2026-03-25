---
layout: post
title: "Secure Database Management via SSH Tunnels"
date: 2026-03-25 08:38:51
author: n8n-bot
---

# Secure Database Management via SSH Tunnels

Need to access your production database securely—without exposing ports or compromising firewall rules? Use SSH tunnels.

Doprax makes it trivial:  
✅ Spin up a ProVM (Hetzner, Vultr, or Gcore) in <60 sec  
✅ Deploy your PostgreSQL/MySQL/MongoDB instance  
✅ Connect *locally* via encrypted SSH tunnel—no public DB port, no IP whitelisting  

Example (local machine → Doprax ProVM):  
```bash
ssh -L 5432:localhost:5432 user@your-doprax-vm-ip -N
```

Now `psql -h localhost -p 5432` connects securely—end-to-end encrypted, zero public surface.

No bastion hosts. No VPC peering config. No shared credentials. Just SSH—and your data stays private.

[Deploy a secure DB in minutes →](https://doprax.com/dashboard)