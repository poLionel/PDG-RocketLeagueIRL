# Design

Ce document décrit les choix techniques et la justification des composants sélectionnés pour la conception des voitures.  
Le composant central est l’**ESP32-S3 avec caméra intégrée**, qui assure à la fois la gestion des capteurs, la communication et le contrôle moteur.

---

## 1. Composant central : ESP32-S3 + Caméra intégrée
- **Rôle :**  
  - Microcontrôleur principal du véhicule  
  - Gestion des entrées/sorties (moteurs, capteurs)  
  - Traitement de la vidéo embarquée pour détection et streaming
  - Communication avec le serveur (Wi-Fi et Bluetooth)
- **Justification :**  
  - Intègre Wi-Fi et Bluetooth (pas besoin de module externe)  
  - Supporte traitement d'image embarqué (via capteur OV2640)  
  - Gestion de charge batterie Li-Po 3,7 V
- **Référence choisie :** Seeed Studio XIAO ESP32-S3 Sense  
  - Compact, facile à intégrer dans un châssis  
  - Caméra intégrée 
  - Prix compétitif

---

## 2. Moteurs DC
- **Rôle :**  
  - Fournir la propulsion et le contrôle directionnel
- **Justification :**  
  - Simplicité de commande via driver H-bridge  
  - Tension compatible avec la batterie Li-Po 3,7 V  
  - Disponibilité en lots à faible coût
- **Référence :** JYD061217 – JIE YI ELECTRONICS  
  - Couple suffisant pour la taille et le poids prévus du véhicule

---

## 3. Driver moteur DC double canal (Adafruit DRV8833)
- **Rôle :**  
  - Piloter deux moteurs DC en contrôle bidirectionnel  
- **Justification :**  
  - Double pont en H, support jusqu’à 1,2 A par moteur  
  - Compatible avec les tensions des moteurs et l’ESP32  
  - Facilement disponible (Adafruit, Digitec)
- **Avantage :**  
  - Commande simple via GPIO de l’ESP32  
  - Compact et efficace

---

## 4. Accéléromètre 3 axes (MPU-6050)
- **Rôle :**  
  - Mesurer l’orientation, l’inclinaison et les chocs  
  - Améliorer le contrôle dynamique du véhicule
- **Justification :**  
  - Très utilisé dans les projets robotiques  
  - Communication I2C facile à intégrer avec l’ESP32  
  - Faible consommation
- **Référence :** Purecrea MPU-6050

---

## 5. Batterie Li-Po
- **Rôle :**  
  Alimenter l’ensemble du système embarqué : microcontrôleur, moteurs et capteurs.

- **Caractéristiques de la batterie sélectionnée :**  
  - Type : Li-Po  
  - Tension : 3.7 V  
  - Capacité : 1000 mAh  

### Consommation maximale estimée :
| Composant                                      | Courant estimé |
|-----------------------------------------------|----------------|
| ESP32-S3 + caméra OV2640                       | ~330 mA        |
| 4 moteurs DC (50 mA chacun)                    | ~200 mA        |
| Driver moteur DRV8833 (pertes internes)        | ~20 mA         |
| Accéléromètre 3 axes (MPU-6050 avec DMP)       | ~6 mA          |
| **Total**                                      | **≈ 556 mA**   |

### Calcul autonomie batterie :
Formule :  
**Capacité (mAh) = Courant (mA) × Durée (h)**

- Pour 30 minutes (0.5 h) :  
  `556 mA × 0.5 h = 278 mAh`
- Pour 1 heure :  
  `556 mA × 1 h = 556 mAh`

#### 🔒 Marge de sécurité 30 % incluse :
- 30 min → `278 mAh × 1.3 = 361.4 mAh`
- 1 h → `556 mAh × 1.3 = 722.8 mAh`

### Conclusion :
Avec une batterie de **1000 mAh**, le système peut fonctionner :
- Environ **1h30** en utilisation soutenue
- Avec **30 % de marge**, il couvre confortablement **jusqu'à 1h en pleine charge continue**

---

## 📌 Conclusion
L’architecture repose sur un ESP32-S3 centralisé, relié directement aux moteurs via driver, et aux capteurs via bus I2C.  
Ce choix maximise la compacité, la performance et la facilité de développement tout en restant économique.

