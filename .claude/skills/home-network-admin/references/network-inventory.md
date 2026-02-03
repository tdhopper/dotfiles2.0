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
- **SSH**: `ssh dobro` (default port 22, user `thopper`)

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
