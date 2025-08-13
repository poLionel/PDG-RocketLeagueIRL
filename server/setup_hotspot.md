# Point d’accès Wi‑Fi Raspberry Pi (hostapd + dnsmasq) — Guide « copier‑coller »

Configure un Pi en point d’accès 2,4 GHz WPA2 sur `wlan0`, avec Internet via `eth0` (Ethernet).

> Modèle testé pour Raspberry Pi OS (Bullseye/Bookworm) avec systemd.

---

## Prérequis (à faire une fois)

Quelques paquets et réglages système nécessaires avant d’activer le hotspot.

```bash
# Met à jour l’index des paquets et installe hostapd/dnsmasq, outils Wi‑Fi et firmwares
sudo apt-get update
sudo apt-get install -y hostapd dnsmasq wireless-tools iw iptables-persistent   firmware-brcm80211 firmware-misc-nonfree

# Démasque hostapd (si masqué par défaut) et arrête hostapd/dnsmasq le temps de la config
sudo systemctl unmask hostapd
sudo systemctl stop hostapd dnsmasq 2>/dev/null || true

# Définit le domaine réglementaire Wi‑Fi (remplacez CH par votre pays: FR/BE/CH/CA…)
sudo iw reg set CH

# Évite des résolutions d’hôte lentes en ajoutant l’IP du Pi à /etc/hosts
echo "$(hostname -I | awk '{print $1}') $(hostname)" | sudo tee -a /etc/hosts >/dev/null
```

---

## Hotspot sur `wlan0`, Internet via `eth0`

### Donner une IP statique à `wlan0` (et désactiver le mode client)

Astuce: la commande sed supprime tout bloc existant pour `wlan0` dans `/etc/dhcpcd.conf`. Sauvegardez si nécessaire.

```bash
# Nettoie d’anciennes sections wlan0 dans dhcpcd.conf
sudo sed -i '/^interface wlan0/,$d' /etc/dhcpcd.conf

# Ajoute une IPv4 statique et coupe wpa_supplicant côté client sur wlan0
sudo tee -a /etc/dhcpcd.conf >/dev/null <<'EOF'
# Point d’accès: IP statique du Raspberry Pi sur le réseau Wi‑Fi privé
interface wlan0
  static ip_address=10.42.0.1/24
  # Empêche wpa_supplicant de gérer wlan0 (le Pi ne se connecte pas en client)
  nohook wpa_supplicant
EOF

# Applique la nouvelle configuration IP
sudo systemctl restart dhcpcd
```

### Configuration `hostapd` : Choisissez entre WPA2-PSK (sécurisé) ou réseau ouvert

Vous pouvez configurer le point d’accès en mode sécurisé (WPA2-PSK) ou ouvert (sans chiffrement).  
**Le mode ouvert est déconseillé en production car il n’y a aucune sécurité.**

#### Option 1 : WPA2-PSK (recommandé)

Modifiez `ssid`, `wpa_passphrase`, `country_code` et `channel` selon vos besoins.

```bash
sudo mkdir -p /etc/hostapd

# Fichier de configuration du point d’accès sécurisé
sudo tee /etc/hostapd/hostapd.conf >/dev/null <<'EOF'
# AP 2.4 GHz sur wlan0
interface=wlan0
driver=nl80211

# Identité du réseau (SSID) et pays (réglementation radio)
ssid=RL-Hotspot            # Nom du Wi‑Fi
country_code=CH            # Adaptez à votre pays (p.ex. FR, BE, CA, CH)

# Bande 2,4 GHz (802.11g/n) et canal
hw_mode=g
channel=1                  # Choisissez un canal libre (1/6/11 en général)

# Qualité de service et 802.11n
wmm_enabled=1
ieee80211n=1
ht_capab=[SHORT-GI-20]

# Sécurité WPA2‑PSK (AES)
auth_algs=1
wpa=2
wpa_passphrase=rocketleague  # Changez ce mot de passe
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF

# Pointeur du service hostapd vers ce fichier de configuration
echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | sudo tee /etc/default/hostapd
```

#### Option 2 : Réseau ouvert (non sécurisé)

Modifiez `ssid`, `country_code` et `channel` selon vos besoins.

```bash
sudo mkdir -p /etc/hostapd

# Fichier de configuration du point d’accès ouvert (aucune sécurité !)
sudo tee /etc/hostapd/hostapd.conf >/dev/null <<'EOF'
# AP 2.4 GHz sur wlan0
interface=wlan0
driver=nl80211

# Identité du réseau (SSID) et pays (réglementation radio)
ssid=RL-Hotspot            # Nom du Wi‑Fi
country_code=CH            # Adaptez à votre pays (p.ex. FR, BE, CA, CH)

# Bande 2,4 GHz (802.11g/n) et canal
hw_mode=g
channel=1                  # Choisissez un canal libre (1/6/11 en général)

# Qualité de service et 802.11n
wmm_enabled=1
ieee80211n=1
ht_capab=[SHORT-GI-20]

# Réseau ouvert (sans chiffrement). Attention: non sécurisé.
auth_algs=1
EOF

# Pointeur du service hostapd vers ce fichier de configuration
echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | sudo tee /etc/default/hostapd
```

### Configuration `dnsmasq` (DHCP/DNS pour les clients)

Distribue des adresses IP aux clients du Wi‑Fi et relaie le DNS.

```bash
sudo mkdir -p /etc/dnsmasq.d

# Pool DHCP sur le sous-réseau 10.42.0.0/24, DNS publics Cloudflare/Google
sudo tee /etc/dnsmasq.d/hotspot.conf >/dev/null <<'EOF'
# Interface du point d’accès
interface=wlan0
bind-interfaces

# Hygiène DNS
domain-needed
bogus-priv

# Plage DHCP (baux de 12 h) et serveurs DNS
dhcp-range=10.42.0.50,10.42.0.150,255.255.255.0,12h
dhcp-option=6,1.1.1.1,8.8.8.8
EOF
```

### Activer le routage IPv4 + NAT vers l’interface Ethernet

Active le forwarding IP et fait du masquerading (NAT) vers `eth0` pour donner Internet aux clients.

```bash
# Active le routage IPv4 de manière persistante
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-ipforward.conf
sudo sysctl -p /etc/sysctl.d/99-ipforward.conf

# Ajoute (si absent) la règle NAT de sortie vers eth0 puis sauvegarde
sudo iptables -t nat -C POSTROUTING -o eth0 -j MASQUERADE 2>/dev/null || sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo netfilter-persistent save
```

### Démarrer les services

Désactive `wpa_supplicant` sur `wlan0` (mode client) et lance `hostapd` + `dnsmasq`.

```bash
# S’assure que wpa_supplicant ne gère pas wlan0
sudo systemctl stop wpa_supplicant@wlan0.service 2>/dev/null || true
sudo systemctl stop wpa_supplicant.service 2>/dev/null || true

# Active et démarre les services du point d’accès et du DHCP/DNS
sudo systemctl enable --now hostapd
sudo systemctl enable --now dnsmasq
```