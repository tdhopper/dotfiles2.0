# Home Network Inventory

## Tailscale Network

MagicDNS is enabled. Run `tailscale status` to discover the tailnet name. Devices are reachable via `<hostname>.<tailnet>.ts.net` or their Tailscale IPs.

## Devices

### pantherbane

- **Type**: Mac (Apple Silicon, arm64)
- **Hostname**: pantherbane.local

### synology (Synology NAS)

- **Type**: Synology NAS
- **Hostname**: HopperNAS (SMB name: HOPPERNAS)
- **LAN IP**: 192.168.68.63 — this is also the local DNS / Pi-hole host. **NOT `.89`** (an earlier version of this doc said `.89`; that address is a different, unrelated host and does not run the NAS services).
- **Tailscale IP**: 100.86.145.18
- **SSH**: `ssh synology` (see `~/.ssh/config` for port, user `tdhopper`)
- **SSH Auth**: 1Password agent, IdentitiesOnly
- **Key services**: DSM web UI (5001 HTTPS), file sharing (SMB + NFS), Docker/Container Manager, Surveillance Station, Pi-hole (:8765). Also runs a **Jellyfin in Docker** (container IP 172.19.0.2:8096) — this is the instance served at `jellyfin.hopperhosted.com`, and is **separate from the Jellyfin app running on dobro**.
- **NFS**: exports `/volume1/docker`. The export is locked to specific client IPs (DSM → Control Panel → Shared Folder → `docker` → Edit → NFS Permissions). dobro mounts this for its Jellyfin media — if a client's LAN IP drifts (DHCP), update the NFS rule or the mount breaks with "Permission denied". Synology tools live in `/usr/syno/sbin` & `/usr/syno/bin` (not on PATH). Editing `/etc/exports*` directly is NOT persistent — DSM regenerates it; use the DSM UI for permanent rules. `sudo exportfs -i -o <opts> <ip>:/volume1/docker` adds a runtime-only rule.

### dobro

- **Type**: Mac
- **Tailscale IP**: 100.80.29.92
- **LAN IP**: 192.168.68.52 (en0, wired/primary — this is the source IP toward the NAS) and 192.168.68.61 (en1). DHCP; has drifted before (was `.84`), which silently broke the NFS mount since the NAS export was pinned to the old IP.
- **SSH**: `ssh dobro` (default port 22, user `thopper`)
- **Caddy reverse proxy**: runs on dobro, serves `*.hopperhosted.com` with Cloudflare DNS-01 TLS
- **Caddyfile**: `~/Caddyfile` (tracked in yadm dotfiles)
- **Scrypted**: runs on dobro as a launchd service (`app.scrypted.server`, user agent in `~/Library/LaunchAgents/app.scrypted.server.plist`, keepalive). Bridges cameras to Apple HomeKit via the built-in `homekit` plugin. Data dir `~/.scrypted` (volume + `scrypted.db`). Web UI on `:10443` (HTTPS) / `:11080` (HTTP); HomeKit HAP accessories listen on dynamic high ports.
  - **Restart**: `launchctl kickstart -k gui/$(id -u)/app.scrypted.server` (run as user `thopper`).
  - **Known failure mode**: if dobro's data volume fills to ~100%, Scrypted's HomeKit plugin can't persist accessory state and macOS `mDNSResponder` can't advertise the bridge over Bonjour, so **cameras silently disappear from the Home app** even though Scrypted shows as "running". Fix = free disk space, then kickstart the service. Check `df -h /System/Volumes/Data`.
- **Disk-space early-warning** (installed to prevent the above): launchd agent `me.ehop.disk-warn` (user `thopper`) runs `~/.config/disk-warn/disk-warn.sh` every 6h. Emails `t@ehop.me` via Resend (`from dobro@ehop.me`, key in `~/.config/disk-warn/resend.key`) when free space on `/System/Volumes/Data` drops below 25 GB, at most once/day. **Warning only — never deletes.** Readings logged to `~/.config/disk-warn/check.log`. Reload with `launchctl bootout/bootstrap gui/$(id -u) ~/Library/LaunchAgents/me.ehop.disk-warn.plist`.
- **Jellyfin**: a Jellyfin **media server** runs here as the macOS GUI app (`/Applications/Jellyfin.app`), launched at login by `~/Library/LaunchAgents/com.jellyfin.server.plist` (which just runs `open -a Jellyfin`; `KeepAlive` is false). **To restart: quit the app + `open -a Jellyfin`** — `launchctl kickstart com.jellyfin.server` does NOT restart the running GUI app. Data dir `~/Library/Application Support/jellyfin`. This is a **distinct instance from the synology Docker Jellyfin** at `jellyfin.hopperhosted.com`. Libraries (YouTube, TV) read media from the NFS automount `/Users/Shared/media/docker/media/` (synology `/volume1/docker`, via fstab + autofs `-static`). A library's path lives in BOTH `root/default/<lib>/.mblink` and `root/default/<lib>/options.xml` (`<MediaPathInfo><Path>`); after editing those, the path only takes effect on a **library scan** (trigger via `POST /Library/Refresh` with an API key, or the dashboard), not just a restart. **If media disappears**: check the mount (`mount | grep docker`, `ls /Users/Shared/media/docker/media/`) and that the NAS NFS export still permits dobro's current LAN IP.
- **Shell/transfer gotchas**: dobro's login shell is **fish** (wrap remote commands in `bash -lc '...'`); it has **no SSH agent** (`SSH_AUTH_SOCK` empty) but its local key `~/.ssh/id_ed25519` is authorized on synology. dobro→synology SSH works with `BatchMode=yes`; synology→dobro is **not** reachable (Tailscale + LAN both blocked). For dobro↔synology file moves, a tar-pipe relay through a third host works well: `ssh dobro 'tar -C <src> -cf - .' | ssh synology 'tar -C <dst> -xf -'`.

## Caddy Reverse Proxy (on dobro)

Caddy on dobro provides HTTPS reverse proxy for internal services under `*.hopperhosted.com`. TLS certs are obtained via Cloudflare DNS-01 challenge using `CLOUDFLARE_API_TOKEN` env var.

### Proxied Services

| Subdomain | Backend | Notes |
|-----------|---------|-------|
| hopperhosted.com (apex) | Local MkDocs site (`~/repos/hopperhosted/site`) | Static file server |
| synology.hopperhosted.com | https://100.86.145.18:5001 (Tailscale) | Synology DSM web UI |
| pihole.hopperhosted.com | 192.168.68.63:8765 | Pi-hole admin |
| photos.hopperhosted.com | https://192.168.68.63:5443 | Synology Photos |
| drive.hopperhosted.com | https://192.168.68.63:10003 | Synology Drive |
| files.hopperhosted.com / file.hopperhosted.com | https://192.168.68.63:7001 | Synology File Station |
| download.hopperhosted.com | https://192.168.68.63:8001 | Synology Download Station |
| webdav.hopperhosted.com | https://192.168.68.63:5006 | WebDAV |
| mail.hopperhosted.com | https://192.168.68.63:21681 | Synology MailPlus |
| cam.hopperhosted.com | https://192.168.68.63:9901 | Surveillance Station |
| audible.hopperhosted.com | 192.168.68.63:3000 | Audible app (port currently closed — service may be off) |
| jellyfin.hopperhosted.com | 100.86.145.18:8096 (Tailscale) | Jellyfin in **Docker on synology** — NOT the separate Jellyfin app on dobro |
| elwood.hopperhosted.com | http://100.119.124.86:8765 (Tailscale device) | Elwood |
| scrypted.hopperhosted.com | https://127.0.0.1:10443 (local on dobro) | Scrypted web UI |
| shiloh-companion.hopperhosted.com | 100.108.169.83:8888 | Shiloh Companion (Tailscale device) |

> **Note:** Synology LAN services are at `192.168.68.63` (verified: all the above ports respond on `.63`). The Caddyfile (`~/Caddyfile` on dobro) already uses `.63` correctly — no changes needed there. The `.89` address that appeared in older notes is a different host.

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

- Local DNS server: 192.168.68.63 — this is the **synology NAS** running Pi-hole
- Fallback DNS: 1.1.1.3 (Cloudflare with family filtering)
- Tailscale MagicDNS: 100.100.100.100 (resolves `*.<tailnet>.ts.net`)
