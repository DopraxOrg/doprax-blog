---
title: "How to Bypass Firewalls with DNS Tunneling (dnstt Tutorial)"
excerpt: "When VPNs fail, DNS tunneling provides a resilient, encrypted escape hatch using dnstt and Doprax."
---

# What Is dnstt?

While “admins” can block Youtube, social media, and VPN, there is a thing they won’t block: DNS traffic.

Most people treat DNS like a phone book, but it’s actually a series of small, hollowed-out envelopes.

We’ve been taught that if the front door is locked, you’re stuck outside. The reality is that the ventilation system is usually wide open.

# What Makes dnstt Great

In simple terms, dnstt is like a “secret tunnel” that works even when the front door, back door, and windows are all locked.

Here is why it’s considered a “magic trick” in the world of networking:

- It Hides in Plain Sight: To a firewall, your data doesn’t look like a VPN or a proxy; it looks like a series of standard DNS queries (the requests your computer makes to find websites like google.com). Since every network must allow DNS to function, this traffic almost always slips through unnoticed.
- Bypasses “Paywalls” and Captive Portals: Have you ever been at an airport or hotel where you have to pay for Wi-Fi? Usually, they block all internet access except for DNS. Because dnstt tunnels your data inside those DNS requests, you can often get full internet access for free.
- End-to-End Encryption: Unlike older DNS tunnels that were slow and leaky, dnstt uses modern Noise Protocol encryption. This means even though you are piggybacking on public DNS servers (like Google or Cloudflare), they can’t see what you’re actually doing.
- Highly Resilient: Because it can use DoH (DNS over HTTPS) or DoT (DNS over TLS), it wraps your tunnel in another layer of web encryption (HTTPS). This makes it nearly impossible for even advanced firewalls (like those used in highly censored countries) to distinguish your tunnel from regular web browsing.

# The Trade-off
The only “catch” is speed.

Because it has to chop your data into tiny pieces to fit inside DNS packets, it’s much slower than a normal VPN.

But when every other connection method is blocked, “slow” is infinitely better than “nothing.”

# dnstt Repo
There are several available repos on here. Here's one of them: https://github.com/bugfloyd/dnstt-deploy?tab=readme-ov-file
