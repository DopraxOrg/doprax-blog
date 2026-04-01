# A Guide to Internet Ports: What They Are, Why They Matter, and Which Ones You'll Actually Use

Ports are basically the traffic directors of the internet.
They're invisible, essential, and they shape how every app, service, and connection works.
If an IP address is a building's street address, a port is the specific apartment number or office suite inside it.
Without ports, your browser wouldn't know whether to hand an incoming packet to your email client, your web server, or your SSH session.

Let's explain ports for real.

# How Ports Work (in 30 seconds)
Every network connection uses a source port (chosen randomly by your device) and a destination port (assigned to a service).
Ports are 16-bit integers: 0 to 65535.

- 0–1023: Well-known ports - standardized, reserved for core protocols.
- 1024–49151: Registered ports - assigned by IANA to specific apps/services (e.g., Docker, Redis, Prometheus).
- 49152–65535: Dynamic/private ports - used temporarily by clients (e.g., your browser opening port 54217 to fetch a webpage).

⚠️ Note: Port numbers alone don't guarantee security or functionality. A port is just a number. What listens on it (and how it's configured) determines behavior.

---

# The Most Important Ports (and What They Actually Do)
| Port | Protocol | Common Use | Reality Check |
| --- | --- | --- | --- |
| 22 | TCP | SSH | The universal keyhole into Linux servers. Used for remote shell, SFTP, Git over SSH, and secure automation. Still the most critical port for infra work. |
| 80 | TCP | HTTP | Unencrypted web traffic. Rarely used directly in production today — mostly redirects to HTTPS or serves health checks. |
| 443 | TCP | HTTPS | Encrypted web traffic. Powers every modern site, API, dashboard, and SaaS login. The de facto standard for anything user-facing. |
| 25 | TCP | SMTP (outbound mail) | Legacy email relay. Blocked by most cloud providers (including Hetzner, DigitalOcean, AWS) to prevent spam. Not for sending from apps — use authenticated SMTP over 587 or a transactional email service instead. |
| 465 / 587 | TCP | SMTPS / Submission | Secure email submission. 465 is deprecated but widely supported; 587 is the IETF-standard port for authenticated, encrypted email sending. Still often blocked by default — check your provider’s firewall. |
| 3306 | TCP | MySQL | Default port for MySQL database access. Never expose publicly — always restrict via firewall or VPC peering. |
| 5432 | TCP | PostgreSQL | Same as above — standard, but never public. Use private networking or SSH tunneling. |
| 6379 | TCP | Redis | In-memory data store. Like databases, keep it internal unless you’re running a managed, auth-protected Redis-as-a-service. |
| 8080 / 8000 / 3000 | TCP | HTTP (alt) | Developer defaults: npm start, python -m http.server, docker run -p 8080:80. Not for production — use 80/443 with a reverse proxy (Caddy, Nginx, Traefik). |
| 2376 / 2377 | TCP | Docker Engine / Swarm | Used for remote Docker daemon access. Requires TLS and strict auth — disable unless you need remote management. |

---
# Why Some Ports Are Blocked (and What to Do)
Cloud providers, especially those prioritizing shared infrastructure hygiene (like Hetzner, OVH, Vultr), block certain ports by default:
- 25, 465, 587: To prevent spam botnets from hijacking new VMs.
- 23 (Telnet), 110 (POP3), 143 (IMAP): Obsolete, insecure, rarely needed - disabled by design.
- Any port < 1024: Often restricted unless you explicitly request elevated privileges (e.g., binding to port 80 as non-root via CAP_NET_BIND_SERVICE).

# What you can do:
Use your provider's firewall UI or CLI to open only the ports you need - e.g., allow 443/tcp and 22/tcp, deny everything else.
Prefer reverse proxies (Caddy, Nginx) over exposing apps directly on high-numbered ports.
For email: route through Mailgun, SendGrid, or your domain's MX-configured relay - not raw port 25.

# Pro Tips for Real-World Use
- Never expose databases or Redis publicly - even with passwords. Use private networks, VPC peering, or SSH tunnels.
- Use nmap -sT -p 1–1000 your-server-ip to audit open ports - then close everything you didn't intentionally open.
- Prefer localhost:3000 + caddy over 0.0.0.0:3000 - bind to loopback unless you require external access.

# One Last Thing: Ports = Contracts
A port number is just a convention - a shared agreement between client and server. What makes it useful is what's listening, how it's secured, and who's allowed to talk to it.
So before you open port 5432, ask:
- Is this database behind a private network?
- Does it require strong auth (not just a password)?
- Is it patched? Is it logging? Is it backed up?

Ports open doors. Good infrastructure decides who gets a key, what's behind the door, and whether the door even needs to be open at all.
