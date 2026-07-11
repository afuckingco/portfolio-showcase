# Network Reconnaissance Report

**Date**: July 4, 2026  
**Network**: 192.168.1.0/24  
**Scanning Tool**: nmap 7.99

## Network Topology

```
┌─────────────────────────────────────────────┐
│   Gateway/Router (192.168.1.1)              │
│   - lighttpd HTTP/HTTPS                     │
│   - Unbound DNS                             │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┼────────────────┬──────────────┐
        │            │                │              │
    192.168.1.34  192.168.1.48   192.168.1.73  192.168.1.123
    (iPhone)    (Linux dev)    (Redmi Pad)   (Samsung A52)
    iOS 15       Device          Android        Android
                                  SE             Tablet
```

## Active Hosts

| IP | Hostname | OS/Device | Status |
|----|----------|-----------|--------|
| 192.168.1.1 | bayu.local | Router (lighttpd) | Up |
| 192.168.1.34 | - | iPhone iOS 15 | Up |
| 192.168.1.48 | - | Linux device | Up |
| 192.168.1.73 | - | Redmi Pad SE Android | Up |
| 192.168.1.123 | - | Samsung A52 Android | Up |
| 192.168.1.233 | - | iPhone iOS 15 | Up |

## Scan Commands Used

### 1. Ping Scan (Host Discovery)
```bash
nmap -sn 192.168.1.0/24
```
**Result**: 6 active hosts discovered

### 2. Service Version Detection
```bash
nmap -sV 192.168.1.1
```

### 3. Aggressive Scan with OS Detection
```bash
nmap -A 192.168.1.0/24
```

### 4. XML Export
```bash
nmap -sV 192.168.1.0/24 -oX network_scan.xml
```

## Gateway (192.168.1.1) - Detailed Analysis

### Open Ports & Services

| Port | Service | Software | Notes |
|------|---------|----------|-------|
| 53 | DNS | Unbound | Recursive DNS resolver |
| 80 | HTTP | lighttpd | Web server (redirects to /cgi-bin/luci/) |
| 443 | HTTPS | lighttpd | Self-signed SSL cert (valid until 2122) |

### SSL Certificate Details

```
Issuer: CN = OpenWrt, O = OpenWrt, C = CN
Subject: CN = OpenWrt
Validity: 2026-07-04 to 2122-10-20
Self-signed: Yes
```

### HTTP Response

Gateway redirects to OpenWrt LuCI admin panel:
```html
<!-- Redirect to /cgi-bin/luci/?stamp=TIME -->
<!-- Browser compatibility check for IE9+ -->
```

**Endpoint**: `http://192.168.1.1/cgi-bin/luci/`

### DNS Enumeration

```bash
dig @192.168.1.1 bayu.local
```

**Result**: NXDOMAIN (domain doesn't exist in DNS)

The gateway hostname is `bayu.local` (Bayu Coffee Shop WiFi) but not resolvable via gateway's DNS.

## Connected Devices Analysis

### Android Devices (2 detected)
- **Redmi Pad SE**: 192.168.1.73 - Tablet
- **Samsung A52**: 192.168.1.123 - Smartphone

### iOS Devices (2 detected)
- **iPhone 1**: 192.168.1.34 - iOS 15
- **iPhone 2**: 192.168.1.233 - iOS 15

### Linux Device
- **192.168.1.48** - Likely lab machine or development device

## Potential Attack Vectors

### Gateway Layer
1. **Web Interface Access** - lighttpd on ports 80/443
   - Accessible at: `http://192.168.1.1/cgi-bin/luci/`
   - Requires authentication (OpenWrt admin credentials)

2. **DNS Spoofing** - Unbound DNS on port 53
   - Possible MITM attack via DNS redirection
   - Requires local network position

3. **SSL/TLS** - Self-signed certificate
   - Vulnerable to MITM attacks
   - No certificate pinning detected

### Connected Devices
- All devices on same subnet (192.168.1.0/24)
- Potential for ARP spoofing / local MITM
- No additional security measures detected from scan results

## Reconnaissance Limitations (WSL)

Due to running nmap in WSL without direct WiFi adapter access:
- ✅ Gateway scanning possible (via wired/bridged network)
- ✅ Active host discovery via ping
- ❌ Cannot perform WiFi deauth attacks
- ❌ Cannot crack WPA2 (requires monitor mode)
- ❌ Cannot sniff raw wireless frames

**Workaround for WiFi hacking**: Use Kali Linux native install or VM with wireless adapter passthrough.

## Lab Network Characteristics

| Aspect | Value |
|--------|-------|
| SSID | Bayu Coffe |
| Security | WPA2-Personal |
| IP Range | 192.168.1.0/24 |
| Gateway | 192.168.1.1 |
| Active Hosts | 6 |
| DNS Server | 192.168.1.1 (Unbound) |

## Scan Output File

Full nmap XML output saved to: `network_scan.xml`

To parse XML:
```bash
nmap -oX scan.xml 192.168.1.0/24
cat scan.xml
```

## Next Steps

1. ✅ Gateway reconnaissance complete
2. ⏳ Web interface enumeration (LuCI admin panel)
3. ⏳ DNS zone transfer attempt (if misconfigured)
4. ⏳ Device-specific scanning (iOS/Android fingerprinting)
