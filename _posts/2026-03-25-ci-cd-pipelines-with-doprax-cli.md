---
layout: post
title: "CI/CD Pipelines with Doprax CLI"
date: 2026-03-25 08:38:53
author: n8n-bot
---

CI/CD Pipelines with Doprax CLI: Deploy Real Infrastructure — Not Just Code  

Most CI/CD tools assume you’re deploying *to* something — a cluster, a server, a managed service. But what if your pipeline needs to *provision and manage the infrastructure itself*? That’s where traditional CI/CD breaks down: SSH keys in secrets, fragile Terraform state, provider API tokens scattered across environments, and hours lost debugging “permission denied” or “resource already exists” errors.

Doprax CLI changes that. It’s not just a deployment tool — it’s an infrastructure orchestration interface designed for developer workflows. With it, your CI/CD pipeline doesn’t just push code. It spins up ProVMs, deploys App Spaces, configures firewalls, attaches volumes, and triggers zero-downtime rollouts — all from a single, versioned, auditable command.

Here’s how it works in practice — no abstraction layers, no hidden abstractions.

✅ **Stateless & Idempotent**  
The Doprax CLI is fully stateless. Every command declares intent — `doprax vm create --image ubuntu-24.04 --size cx31 --provider hetzner` doesn’t rely on local config files or cached credentials. You pass what you need, when you need it (via environment variables or flags), and get predictable, repeatable output. No drift. No manual reconciliation.

✅ **Built-in Provider Credentials (Securely)**  
No more base64-encoded secrets in GitHub Actions or CircleCI env vars. Doprax supports secure credential delegation:  
- Use `DOPRAX_TOKEN` (short-lived, scoped, revocable) generated directly from your Doprax dashboard.  
- Or use `DOPRAX_PROVIDER_TOKEN_HETZNER`, `DOPRAX_PROVIDER_TOKEN_DIGITALOCEAN`, etc. — each scoped *only* to its provider and limited to read/write infrastructure actions (no billing or account access).  
All tokens are JWT-based, time-bound, and never stored on Doprax servers after issuance.

✅ **Real Infrastructure, Real Speed**  
Deploy a production-ready Ubuntu VM on Hetzner with firewall, floating IP, and attached volume — in under 9 seconds:

```bash
doprax vm create \
  --name "ci-web-prod" \
  --image "ubuntu-24.04" \
  --size "cx31" \
  --provider "hetzner" \
  --firewall "web-default" \
  --floating-ip \
  --volume "50gb-ssd" \
  --ssh-key "$SSH_PUBLIC_KEY" \
  --wait
```

That’s one command. One `--wait`. Full boot + SSH readiness confirmed before exit. No polling scripts. No race conditions.

✅ **Git-Native Rollouts (No YAML Hell)**  
Use `doprax app deploy` to trigger zero-downtime container updates in App Spaces — but tie it directly to your Git flow:

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'Dockerfile'
      - 'doprax.app.yaml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Doprax CLI
        run: curl -fsSL https://get.doprax.com | sh
      - name: Deploy to App Space
        run: doprax app deploy --space "web-prod" --tag "${{ github.sha }}"
        env:
          DOPRAX_TOKEN: ${{ secrets.DOPRAX_TOKEN }}
```

`doprax.app.yaml` lives alongside your code — declarative, versioned, and enforced at deploy time (e.g., resource limits, health checks, ingress rules). No separate Helm charts. No K8s manifests bloated with boilerplate.

✅ **Rollback Is a Command — Not a Prayer**  
Forgot a migration? Pushed a breaking config change? Revert in one line:

```bash
doprax app rollback --space "web-prod" --to "v2.4.1"
```

No manual database restores. No digging through logs. Doprax tracks every deployed revision — image digest, config hash, timestamp, and triggering commit — and rolls back *infrastructure state*, not just containers.

✅ **Multi-Cloud by Default — Not as an Afterthought**  
Your staging env runs on DigitalOcean. Production runs on OVH. Load-testing runs on Vultr GPU nodes. All controlled from the same CLI — same flags, same syntax, same auth model.

```bash
# Staging (DO)
doprax vm create --provider digitalocean --size s-2vcpu-4gb ...

# Production (OVH)
doprax vm create --provider ovh --size b2-7 --gpu v100 ...

# Both use identical network policies, volume types, and lifecycle hooks.
```

No vendor-specific templates. No forked configs. Just portable infrastructure-as-code — written by you, executed by Doprax.

💡 Why This Matters  
You don’t need a DevOps engineer to add a new environment. You don’t need a 3-hour meeting to align on Terraform module versions. You don’t need to choose between speed and control.

With Doprax CLI, your pipeline *is* your infrastructure workflow — fast, auditable, and owned entirely by your team.

👉 Next step: Try it live.  
Install the CLI (`curl -fsSL https://get.doprax.com | sh`), log in with `doprax login`, then run `doprax vm create --help`. Then paste that command into your CI — and watch real infrastructure deploy in seconds, not hours.

No credit card. No trial period. Just working infrastructure — on your terms.