# Sonos Speaker Inventory

## Network

- **Speaker VLAN**: `10.20.1.x` (IoT VLAN)
- **Mac VLAN**: `10.20.4.x/23` (gateway `10.20.5.1`)
- **mDNS**: Reflected across VLANs (speakers discoverable via `dns-sd -B _sonos._tcp local.`)
- **TCP routing**: Must use `curl --interface en0` to bypass VPN and route through local gateway
- **Sonos HTTP API port**: 1400

## Speakers (12 total)

| Name | IP | UUID | Notes |
|------|-----|------|-------|
| Basement Hall | 10.20.1.52 | RINCON_38420B537E9801400 | |
| Basement Kitchen | 10.20.1.55 | RINCON_38420B538C6E01400 | Often group coordinator |
| CM Desk Area | 10.20.1.45 | RINCON_38420B537D9601400 | |
| East Mezzanine | 10.20.1.56 | RINCON_38420B5380B001400 | |
| Front Porch | 10.20.1.58 | RINCON_38420B537EDC01400 | |
| Gravity Room (Basement) | 10.20.1.54 | RINCON_38420B537A3801400 | |
| NHB C Dining | 10.20.1.57 | RINCON_38420B537F4601400 | |
| NHB L Bar | 10.20.1.49 | RINCON_38420B538E8001400 | Has sub (RINCON_542A1B26719601400) |
| NHB Patio | 10.20.1.246 | RINCON_38420B2857AF01400 | HDMI CEC available |
| NHB R Bar | 10.20.1.88 | RINCON_F0F6C18BBDAC01400 | |
| Office | 10.20.1.43 | RINCON_38420B53790A01400 | Sonos One SL (model S38) |
| West Mezzanine | 10.20.1.59 | RINCON_38420B537F2601400 | |

## Zone Groups (as of last discovery)

Groups indicate which speakers play in sync. The coordinator controls the queue.

- **Gravity Room**: standalone
- **East Mezzanine**: standalone
- **Basement Hall**: standalone
- **West Mezzanine**: standalone
- **Main group** (coordinator: Basement Kitchen): Office, NHB C Dining, NHB L Bar, NHB R Bar, CM Desk Area, Basement Kitchen, Front Porch, NHB Patio

## Hardware Details

- All speakers run software version `93.1-74010` (Gen 2, SWGen=2)
- All have AirPlay enabled
- All connect via WiFi (WirelessMode=1, EthLink=0)
- WiFi channels: mix of 5GHz (5200, 5805) and 2.4GHz (2412 for NHB Patio)
- NHB L Bar has a paired subwoofer (RINCON_542A1B26719601400)

## Discovery Commands

```bash
# Find all Sonos speakers via mDNS
dns-sd -B _sonos._tcp local.

# Resolve a specific speaker's IP
dns-sd -L "<instance_name>" _sonos._tcp local.
# Example: dns-sd -L "RINCON_38420B53790A01400@Office" _sonos._tcp local.

# Get zone group topology (all speakers + grouping) from any speaker
curl -s --interface en0 -m 5 "http://10.20.1.43:1400/ZoneGroupTopology/Control" \
  -H "Content-Type: text/xml; charset=utf-8" \
  -H 'SOAPAction: "urn:schemas-upnp-org:service:ZoneGroupTopology:1#GetZoneGroupState"' \
  -d '<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:GetZoneGroupState xmlns:u="urn:schemas-upnp-org:service:ZoneGroupTopology:1"/></s:Body></s:Envelope>'
```
