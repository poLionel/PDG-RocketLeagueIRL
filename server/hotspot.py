import subprocess
import time

def start_hotspot(ssid="RL-Hotspot", password="rocketleague"):
    config = f"""
interface=wlan0
driver=nl80211
ssid={ssid}
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={password}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
    """
    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write(config)

    print("→ Démarrage du hotspot WiFi...")
    subprocess.run(["sudo", "systemctl", "restart", "hostapd"])
    subprocess.run(["sudo", "systemctl", "restart", "dnsmasq"])
    time.sleep(5)
    print("✅ Hotspot prêt.")
