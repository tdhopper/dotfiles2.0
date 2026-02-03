# Home Network Inventory

## Tailscale Network

MagicDNS is enabled. Run `tailscale status` to discover the tailnet name. Devices are reachable via `<hostname>.<tailnet>.ts.net` or their Tailscale IPs.

## Devices

### pantherbane

- **Type**: Mac (Apple Silicon, arm64)
- **Hostname**: pantherbane.local

### synology (Synology NAS)

- **Type**: Synology NAS
- **Tailscale IP**: 100.86.145.18
- **SSH**: `ssh synology` (see `~/.ssh/config` for port, user `tdhopper`)
- **SSH Auth**: 1Password agent, IdentitiesOnly
- **Key services**: DSM web UI (typically port 5000/5001), file sharing, Docker/Container Manager, Surveillance Station (HomeCam app suggests cameras)

### dobro

- **Type**: Mac
- **Tailscale IP**: 100.80.29.92
- **LAN IP**: 192.168.68.84
- **SSH**: `ssh dobro` (default port 22, user `thopper`)
- **Caddy reverse proxy**: runs on dobro, serves `*.hopperhosted.com` with Cloudflare DNS-01 TLS
- **Caddyfile**: `~/Caddyfile` (tracked in yadm dotfiles)

## Caddy Reverse Proxy (on dobro)

Caddy on dobro provides HTTPS reverse proxy for internal services under `*.hopperhosted.com`. TLS certs are obtained via Cloudflare DNS-01 challenge using `CLOUDFLARE_API_TOKEN` env var.

### Proxied Services

| Subdomain | Backend | Notes |
|-----------|---------|-------|
| hopperhosted.com (apex) | Local MkDocs site (`~/repos/hopperhosted/site`) | Static file server |
| synology.hopperhosted.com | 192.168.68.89:5001 (HTTPS) | Synology DSM web UI |
| pihole.hopperhosted.com | 192.168.68.89:8765 | Pi-hole admin |
| photos.hopperhosted.com | 192.168.68.89:5443 | Synology Photos |
| drive.hopperhosted.com | 192.168.68.89:10003 | Synology Drive |
| files.hopperhosted.com / file.hopperhosted.com | 192.168.68.89:7001 | Synology File Station |
| download.hopperhosted.com | 192.168.68.89:8001 | Synology Download Station |
| webdav.hopperhosted.com | 192.168.68.89:5006 (HTTPS) | WebDAV |
| mail.hopperhosted.com | 192.168.68.89:21681 | Synology MailPlus |
| cam.hopperhosted.com | 192.168.68.89:9901 | Surveillance Station |
| audible.hopperhosted.com | 192.168.68.89:3000 | Audible app |
| jellyfin.hopperhosted.com | 192.168.68.84:8096 | Jellyfin media server (on dobro) |
| shiloh-companion.hopperhosted.com | 100.108.169.83:8888 | Shiloh Companion (Tailscale device) |

## Network Topology

```
Internet
  |
Router/Gateway (192.168.68.1)
  |
Local LAN (192.168.68.x)
  ├── pantherbane
  ├── synology NAS (likely wired)
  ├── dobro
  └── other local devices
  |
Tailscale overlay (100.x.x.x)
  ├── pantherbane
  ├── synology (100.86.145.18)
  └── dobro (100.80.29.92)
```

## DNS Configuration

- Local DNS server: 192.168.68.63 (likely the router or a Pi-hole/AdGuard)
- Fallback DNS: 1.1.1.3 (Cloudflare with family filtering)
- Tailscale MagicDNS: 100.100.100.100 (resolves `*.<tailnet>.ts.net`)
