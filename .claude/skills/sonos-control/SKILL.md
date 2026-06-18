---
name: sonos-control
description: Control Sonos speakers on Tim's home network. Use when the user wants to (1) play, pause, or stop music on Sonos speakers, (2) change volume on speakers, (3) skip tracks, (4) check what's playing, (5) see speaker status, (6) group or ungroup speakers, (7) any Sonos or music/audio playback task involving home speakers. Triggers on "sonos", "speakers", "play music", "what's playing", "volume", "turn up", "turn down", "pause music", "stop music".
model: haiku
effort: low
---

# Sonos Speaker Control

Control Tim's 12 Sonos speakers via the `sonos-ctl` CLI tool at `~/.local/bin/sonos-ctl`.

Read [references/speaker-inventory.md](references/speaker-inventory.md) for the full speaker list, IPs, and network details.

## Quick Reference

```bash
sonos-ctl status                # Show all speakers with volume, state, now playing
sonos-ctl play <speaker>        # Play/resume
sonos-ctl pause <speaker>       # Pause
sonos-ctl stop <speaker>        # Stop
sonos-ctl vol <speaker>         # Get current volume
sonos-ctl vol <speaker> <0-100> # Set volume
sonos-ctl next <speaker>        # Next track
sonos-ctl prev <speaker>        # Previous track
```

Speaker names use **case-insensitive partial matching**: `office`, `patio`, `kitchen`, `gravity`, `porch`, `mezzanine`, etc.

## Network Architecture

The Sonos speakers are on the IoT VLAN (`10.20.1.x`), separate from Tim's Mac (`10.20.4.x`). The `sonos-ctl` script uses `curl --interface en0` to bypass the corporate VPN (which would otherwise route traffic through the tunnel instead of the local gateway).

**If `sonos-ctl` stops working**, the likely causes are:
1. **VPN routing changed** - verify `curl --interface en0 -m 3 http://10.20.1.43:1400/xml/device_description.xml` still works
2. **Speaker IPs changed** - re-discover with `dns-sd -B _sonos._tcp local.` then resolve IPs with `dns-sd -L "<instance>" _sonos._tcp local.`
3. **New speakers added** - same discovery process, then update the SPEAKERS map in `~/.local/bin/sonos-ctl`

## Common Patterns

### Check what's playing everywhere
```bash
sonos-ctl status
```

### Play/pause a specific room
```bash
sonos-ctl play office
sonos-ctl pause office
```

### Adjust volume
```bash
sonos-ctl vol office        # check current
sonos-ctl vol office 20     # set to 20
```

### Bulk operations
Loop over speakers with bash:
```bash
for spk in office kitchen patio; do sonos-ctl pause "$spk"; done
for spk in office kitchen patio; do sonos-ctl vol "$spk" 15; done
```

## Direct UPnP API (Advanced)

The `sonos-ctl` script wraps UPnP SOAP calls. For operations not covered by the script, you can make raw SOAP calls. Always use `curl --interface en0` to bypass the VPN.

### Get device info
```bash
curl -s --interface en0 -m 3 "http://<IP>:1400/xml/device_description.xml"
```

### SOAP call pattern
```bash
curl -s --interface en0 -m 3 "http://<IP>:1400/<endpoint>" \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H 'SOAPAction: "urn:schemas-upnp-org:service:<Service>:1#<Action>"' \
  -d '<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:<Action> xmlns:u="urn:schemas-upnp-org:service:<Service>:1">
      <body params here>
    </u:<Action>>
  </s:Body>
</s:Envelope>'
```

### Key UPnP endpoints

| Endpoint | Service | Common Actions |
|----------|---------|----------------|
| `/MediaRenderer/AVTransport/Control` | AVTransport | Play, Pause, Stop, Next, Previous, GetTransportInfo, GetPositionInfo, SetAVTransportURI |
| `/MediaRenderer/RenderingControl/Control` | RenderingControl | GetVolume, SetVolume, GetMute, SetMute |
| `/ZoneGroupTopology/Control` | ZoneGroupTopology | GetZoneGroupState (discover all speakers and groups) |
| `/MediaServer/ContentDirectory/Control` | ContentDirectory | Browse (queue, favorites) |

### Grouping speakers (not yet in sonos-ctl)

To group a speaker with a coordinator, set the speaker's AVTransport URI to the coordinator's URI:
```bash
# Get coordinator's URI: x-rincon:<COORDINATOR_UUID>
# Then on the speaker to join:
curl -s --interface en0 -m 3 "http://<JOINER_IP>:1400/MediaRenderer/AVTransport/Control" \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H 'SOAPAction: "urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"' \
  -d '...SetAVTransportURI...<CurrentURI>x-rincon:RINCON_COORDINATOR_UUID</CurrentURI>...'
```

To ungroup, call `BecomeCoordinatorOfStandaloneGroup` on the speaker.
