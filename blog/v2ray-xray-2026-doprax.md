# V2Ray/Xray Server Setup on Doprax ProVM – Complete 2026 Tutorial  
**Unlimited Traffic + Reality Protocol (Hiddify or 3X-UI)**

Deploy a production-ready Xray server with **REALITY** protocol in under 10 minutes.  
No DevOps experience required. Unlimited bandwidth, 1 Gbps ports, clean dedicated IPs, and it spins up in <60 seconds.

**Why Doprax ProVM for this?**  
- Truly unlimited traffic (no TB caps, no overages)  
- Modern CPUs + 1 Gbps dedicated ports  
- Clean IPs perfect for proxy/VPN workloads  
- Pay-per-second billing + crypto payments  
- Deploy real infrastructure in minutes — without managing servers.

This guide uses **ProVM** (Doprax’s own high-performance infrastructure). P1 ($8.95/mo) or P2 ($12.95/mo) is more than enough for most setups.

---

## Prerequisites
- A free Doprax account → [doprax.com](https://www.doprax.com)
- Basic SSH knowledge
- (Optional but recommended) Your own domain for even better stealth (not required with REALITY)

---

## Step 1: Create Your ProVM (Exact Dashboard Flow)

1. Log in to the Doprax Dashboard  
2. Go to **My Virtual Machines** → **Create a Virtual Machine**  
3. **Provider**: Choose **ProVM** (recommended for unlimited traffic)  
4. **Location**: Any available (Germany, France, Poland, UK, or Canada)  
5. **OS Image**: **Ubuntu 24.04** (recommended) or Ubuntu 22.04  
6. **Size**:  
   - P1 (1 vCPU / 1 GB) – fine for personal use  
   - P2 (1 vCPU / 2 GB) – recommended for multiple users  
7. **Access Method**: **SSH Key** (strongly recommended for security)  
8. **Name**: e.g. `xray-reality-2026`  
9. Click **Create Virtual Machine**

Your VM will be ready in **under 60 seconds**.  
You will see the public IPv4 address and `root` username.

---

## Step 2: Connect to Your Server

```bash
ssh root@YOUR-PROVM-IP
```
Update the system first:
```
apt update && apt upgrade -y
```
## Step 3: Choose Your Installation Method

### Option A: Hiddify Panel (Easiest – Recommended)One-command install (official 2026 method):
```
bash <(curl https://i.hiddify.com/release)
```
After installation:
- The script will give you the admin panel URL (usually https://YOUR-IP:9000)
- Default username/password shown in terminal
- In the panel → create a new user → choose Reality protocol
- It auto-configures everything (VLESS + Reality + uTLS fingerprint)

Done. Your config URL is ready for clients.

### Option B: 3X-UI Panel (More Control)One-command install:
```
bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
```
During setup:
- Set panel port (default 2053 recommended)
- Choose username/password
- After login (http://YOUR-IP:port) (http://YOUR-IP:port), go to Inbounds → Add new
- Protocol: VLESS
- Port: 443
- Security: reality
- Fingerprint: chrome (or firefox)
- Dest: www.microsoft.com:443 (or any popular site)
- Short ID: generate one (8–16 hex chars)
- Save → scan the QR code or copy the link

### Option C: Manual Xray + REALITY (Advanced / Full Control)
```
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
```
Create /usr/local/etc/xray/config.json:

```
{
  "log": { "loglevel": "warning" },
  "inbounds": [{
    "port": 443,
    "protocol": "vless",
    "settings": {
      "clients": [{ "id": "YOUR-UUID-HERE", "flow": "xtls-rprx-vision" }],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "show": false,
        "dest": "www.microsoft.com:443",
        "xver": 0,
        "serverNames": ["www.microsoft.com"],
        "privateKey": "YOUR-PRIVATE-KEY-HERE",
        "shortIds": ["YOUR-SHORT-ID-HERE"]
      }
    }
  }],
  "outbounds": [{ "protocol": "freedom" }]
}
```
Generate keys & UUID:
```
xray uuid                  # → copy this as YOUR-UUID-HERE
xray x25519                # → copy privateKey and publicKey
```
Replace values, then start:
```
systemctl enable --now xray
```
## Step 4: Test Your Server
Use any modern client:
- HiddifyN / HiddifyNext (iOS/Android/Windows/Linux)
- v2rayN (Windows)
- Nekobox (Android)
- Streisand (macOS)

Import the config URL or QR code → connect → test speed and IP.Expected result: Full speed (limited only by your client connection) with zero throttling.
---
## Why This Setup Wins on Doprax ProVM
- Unlimited traffic → run it 24/7 with 100+ users without extra fees
- 1 Gbps port → real-world 500–900 Mbps speeds
- Clean IPs → high success rate with Reality
- Instant provisioning + hourly billing → test and destroy VMs in seconds
- Full root access + snapshots for backup
---
## Troubleshooting
Port 443 blocked? → ProVM opens all ports by default
"Connection refused"? → ufw allow 443 or systemctl restart xray
Slow speeds? → Try different fingerprint (chrome / firefox / random)
Need to change IP? → $4.50 one-time fee in dashboard











