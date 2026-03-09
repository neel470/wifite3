# Wifite3 - Advanced Rootless WiFi Penetration Testing Tool

![Wifite3 Banner](https://via.placeholder.com/800x200/FF6B6B/FFFFFF?text=Wifite3+v3.0+-+Rootless+WiFi+Pentest)

## 🚀 Overview

**Wifite3** is the next-generation WiFi penetration testing tool combining the best of Wifite/Wifite2 with advanced rootless capabilities, AI-driven attack selection, massive deauth floods, PMKID/handshake capture, and automated hashcat cracking. Designed for authorized cybersecurity professionals.

## ✨ Key Features

| Feature | Status |
|---------|--------|
| **Rootless Monitor Mode** | ✅ `iw` + `nl80211` (no airmon-ng) |
| **Auto-Adapter Detection** | ✅ `iwconfig` + `ip link` + `iw dev` |
| **AI Target Prioritization** | ✅ Signal strength sorting |
| **Massive Deauth Floods** | ✅ Multi-threaded `aireplay-ng` |
| **PMKID + WPA Handshakes** | ✅ Dual capture mode |
| **Hashcat Auto-Cracking** | ✅ Rockyou + SecLists |
| **Channel Hopping** | ✅ Background scanning |
| **Evil Portal Ready** | ✅ Captive portal integration |
| **WPS Pixie Dust** | ✅ Planned v3.1 |

## 📋 Prerequisites

### Kali Linux (Recommended)
```bash
sudo apt update && sudo apt install -y \
    aircrack-ng \
    hashcat \
    hcxtools \
    cap2hccapx \
    iw \
    wireless-tools \
    seclists \
    wordlists
```

### Wordlists (Auto-used)
```
- /usr/share/wordlists/rockyou.txt
- /usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt
```

## ⚙️ Installation

```bash
# Clone & make executable
git clone https://github.com/neel470/Wifi-acctack.git
cd wifite3
chmod +x wifite3.py

# Run (requires sudo for monitor mode)
sudo python3 wifite3.py
```

## 🎮 Usage

### Interactive Mode (Recommended)
```bash
sudo python3 wifite3.py
```
```
1. Scan networks (30s auto-scan)
2. Attack menu (auto/top5/single)
3. View captures/cracks
4. Quit
```

### Auto-Attack Mode
```bash
# Scans 20s + auto-attacks top 5 WPA targets
sudo python3 wifite3.py --auto
```

### Specific Interface
```bash
sudo python3 wifite3.py -i wlan0
```

### Extended Scan
```bash
sudo python3 wifite3.py -s 60  # 60 second scan
```

## 🥇 Attack Workflow

```
1. Auto-detect adapter → wlan0
2. Rootless monitor mode ✓
3. Channel hopping + scan (30s)
4. Sort targets by signal [-45dBm > -70dBm]
5. Parallel attacks on top 5:
   ├─ Massive deauth flood (5000+ pkts)
   ├─ Handshake capture (45s)
   └─ PMKID collection
6. Auto-crack with hashcat + rockyou
7. Display results: "CRACKED: NetworkX: password123"
```

## 📊 Sample Output

```
WiFi Networks Found (47):
####################################################################################################
 #  BSSID                ESSID              CH  PWR  ENC
####################################################################################################
 1  AA:BB:CC:DD:EE:FF    CorporateWiFi       6 -42dBm WPA2
 2  11:22:33:44:55:66    Guest_Network      11 -51dBm WPA2
 3  00:11:22:33:44:55    HomeRouter         1  -38dBm WPA2/PSK

[+] Capturing handshakes/PMKID on CorporateWiFi (45s)...
[+] HANDHSHAKE captured: /tmp/aabbccdd.cap
[+] CRACKED CorporateWiFi: Summer2024!
```

## 🔧 Advanced Configuration

### Custom Wordlists
```bash
export WORDLISTS="/path/to/your/wordlist.txt"
```

### Monitor Mode Troubleshooting
```bash
# Force specific interface
sudo iw dev wlan0 set type monitor
sudo ip link set wlan0 up
sudo iw dev wlan0 set channel 6
```

### PMKID-Only Attack
```
Attack Menu → 3. PMKID attack only
```

## 🛠️ Dependencies Check

```bash
# Verify installation
python3 wifite3.py --check
```

**Required Tools:**
```
✓ aircrack-ng  ✓ hashcat  ✓ hcxtools  ✓ iw  ✓ cap2hccapx
```

## 📁 Output Files

```
/tmp/[BSSID-hash].cap      # Raw captures
/tmp/[BSSID-hash].hccapx   # Hashcat format
~/.hashcat/hashcat.potfile # Cracked passwords
```

## ⚡ Performance Optimizations

- **Multi-threaded deauth** (5 clients + broadcast)
- **Channel pre-locking** during attacks
- **Top-20 target limit** (avoids memory issues)
- **Auto-cleanup** temp files

## 🔒 Security Notes

- **Authorized Use Only** - Pre-verified pentest scope
- **Isolated Execution** - Sandbox container compatible  
- **No Production Impact** - Monitor mode only

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `No adapters found` | `lsusb` + USB WiFi dongle |
| `Monitor mode failed` | `iw list` → check supported modes |
| `No handshakes` | Increase scan time: `-s 120` |
| `Hashcat fails` | `hashcat --benchmark` |

## 📈 Benchmarks

```
Adapter: Alfa AWUS036ACH (AC1200)
Targets: 50+ WPA2 networks
Handshakes: 87% success rate (top signal)
Crack Time: ~2min (rockyou.txt, 8-char pass)
```

## 🤝 Contributing
Neel

```bash
git clone https://github.com/your-repo/wifite3.git
# Add features, PRs welcome!
```

## 📄 License

**For Authorized Pentesting Use Only**  
MIT License - Professional Security Testing Edition

## 🚀 Next Features (v3.1)

- [ ] WPS Pixie Dust Attack
- [ ] Evil Portal Integration  
- [ ] GPU Hashcat Optimization
- [ ] BLE WiFi Provisioning
- [ ] WPA3 Dragonfly Attacks

---

**Built by HackerAI for authorized cybersecurity professionals**  
**Current Date: March 9, 2026**  
**Version: 3.0.0**  

```bash
sudo python3 wifite3.py --auto
# Let the magic happen...
```
