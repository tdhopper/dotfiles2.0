---
name: home-network-admin
description: Manage and troubleshoot Tim's home network, SSH into devices, administer the Synology NAS, and work with Tailscale. Use when the user wants to (1) SSH into or run commands on remote machines (synology, dobro), (2) manage the Synology NAS (files, packages, Docker, backups, Surveillance Station), (3) troubleshoot network connectivity or DNS, (4) check Tailscale status or manage the tailnet, (5) transfer files between machines, (6) check device health or disk usage, (7) manage the Caddy reverse proxy on dobro (*.hopperhosted.com), (8) any home server or home network administration task.
---

# Home Network Admin

Administer Tim's home network: devices connected over Tailscale, with a Synology NAS and Macs accessible via SSH.

Read [references/network-inventory.md](references/network-inventory.md) for the full device list, IPs, SSH config, and network topology before performing any task.

## SSH Access

SSH configs are defined in `~/.ssh/config`. Use the short aliases:

- `ssh synology` - Synology NAS (custom port, user tdhopper)
- `ssh dobro` - Mac (default port, user thopper)

SSH keys are managed via 1Password agent. If SSH fails with auth errors, verify 1Password is unlocked and the SSH agent is running.

## Synology NAS Administration

The Synology runs DSM. Common admin tasks via SSH:

- **Packages**: `synopkg list` (installed), `synopkg status <pkg>`, `synopkg start/stop <pkg>`
- **Docker/Container Manager**: `sudo docker ps`, `sudo docker logs <container>`, `sudo docker compose` (compose files often in `/volume1/docker/`)
- **Disk/volume health**: `df -h`, `cat /proc/mdstat`, `synodisk --enum`
- **Shared folders**: typically under `/volume1/`
- **DSM web UI**: `https://synology:5001` or `https://100.86.145.18:5001`
- **Logs**: `/var/log/` and DSM log center

For destructive operations (deleting files, stopping services, modifying configs), confirm with the user first.

## Tailscale

Tailscale connects all devices over a WireGuard mesh. Run `tailscale status` to discover the tailnet name and device list.

- On macOS, the `tailscale` CLI may not be on PATH. Use: `/Applications/Tailscale.app/Contents/MacOS/Tailscale`
- Check status: `tailscale status` (or the full path above)
- Verify connectivity: `tailscale ping <hostname>`
- All devices are reachable via MagicDNS (e.g., `synology.<tailnet>.ts.net`)

## Caddy Reverse Proxy (on dobro)

Caddy runs on dobro, providing HTTPS reverse proxy for `*.hopperhosted.com`. The Caddyfile is at `~/Caddyfile` (tracked in yadm). TLS uses Cloudflare DNS-01 challenge.

See [references/network-inventory.md](references/network-inventory.md) for the full list of proxied subdomains and backends.

- **Manage Caddy on dobro**: `ssh dobro` then `brew services restart caddy`, `caddy reload --config ~/Caddyfile`
- **Logs**: `journalctl -u caddy` or `brew services info caddy` depending on how it's managed
- **Edit Caddyfile locally**: it's tracked in yadm dotfiles at `~/Caddyfile`

## File Transfer

- Between local and remote hosts: `rsync` using the SSH aliases
- Example: `rsync -avz ~/files/ synology:/volume1/backup/files/`
- For large transfers, prefer `rsync` with `--progress`
- **`scp` to synology does NOT work** — the sftp subsystem is disabled in its sshd. Use rsync or tar-over-ssh.
- **rsync-to-synology gotcha**: Synology's patched rsync only allows rsync-over-SSH on the port set in DSM → Control Panel → File Services → rsync → "SSH encryption port". That field must match the real sshd port (27571). If it drifts (e.g. reset to 22 by a DSM update), rsync fails with "Permission denied, please try again" even though plain ssh works, and `rsync --server` run manually on the NAS reports "rsync service is no running (code 43)". Fixed 2026-07-03 by setting the field to 27571.

## Troubleshooting

1. **Can't SSH**: Check 1Password is unlocked, verify Tailscale is connected (`tailscale status`), ping the Tailscale IP
2. **DNS issues**: Check if MagicDNS resolves (`dig @100.100.100.100 synology.<tailnet>.ts.net`), fall back to Tailscale IPs directly
3. **NAS unresponsive**: Try ping, check DSM web UI, SSH may still work even if DSM is sluggish
4. **Slow network**: Check if traffic is going through Tailscale relay (`tailscale status` shows DERP relay vs direct connection)
