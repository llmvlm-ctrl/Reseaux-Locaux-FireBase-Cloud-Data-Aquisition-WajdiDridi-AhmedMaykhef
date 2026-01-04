# Bureau d'étude Réseaux Locaux  
## Projet : Tableau de bord IoT Température & Humidité (Cloud Firebase)

**Établissement** : Bureau d'étude Réseaux Locaux  
**Encadrant** : Pr. Khaled Jelassi  
**Réalisé par** :  
- Wajdi Dridi  
- Ahmed Chikh Maykhef  

Ce projet lit des données de température et d’humidité à partir d’un Arduino Uno, les envoie à un Raspberry Pi via le port série, puis les stocke dans une base de données Firestore (Firebase) dans le cloud.  
Les données sont ensuite visualisées dans un tableau de bord web développé avec Dash et Plotly, sans utiliser la mémoire locale du Raspberry Pi pour la persistance.

---

## Aperçu du système

L’objectif est de mettre en place une chaîne IoT complète, depuis le capteur jusqu’au cloud et à la visualisation :

- L’Arduino lit les mesures d'un capteur DHT11 et les envoie au Raspberry Pi via USB (port série).
- Un script Python sur le Raspberry Pi (`serial_to_firebase.py`) lit les trames série, extrait l’humidité et la température, puis les enregistre dans Firestore.
- Un tableau de bord Dash (`dashboard.py`) récupère l’historique des mesures stockées dans Firestore et affiche :
  - des jauges pour la dernière valeur de température et d’humidité,
  - des courbes temporelles des 200 dernières mesures.

Le Raspberry Pi ne stocke donc pas les données en local : toute la persistance se fait dans le cloud, dans Firebase Firestore.

---

## Architecture du système

1. **Arduino → Raspberry Pi (série)**  
   L’Arduino envoie des lignes de texte contenant à la fois `Humidite:` et `Temperature:` avec les valeurs numériques correspondantes, à 9600 bauds.

2. **Raspberry Pi → Firebase (script Python)**  
   Le script `serial_to_firebase.py` :
   - ouvre le port série `/dev/ttyUSB0` (modifiable si besoin),
   - lit en continu les lignes série,
   - vérifie la présence des mots-clés `Humidite:` et `Temperature:`,
   - parse les valeurs numériques,
   - envoie les données vers Firestore dans deux collections :
     - `donne_dh11` : document courant (`temp_hum`) contenant la dernière mesure,
     - `donne_dh11_history` : historique, où chaque mesure est ajoutée comme un nouveau document.

3. **Firebase → Tableau de bord Dash**  
   Le fichier `dashboard.py` :
   - interroge la collection `donne_dh11_history` pour récupérer les 200 derniers documents, triés par timestamp,
   - construit un DataFrame Pandas,
   - affiche deux jauges pour la dernière mesure de température et d’humidité,
   - trace deux courbes temporelles (température et humidité) sur la base des données historiques,
   - met à jour l’affichage automatiquement toutes les 30 secondes ou lorsque l’utilisateur clique sur le bouton “Actualiser”.

Cette architecture permet d’avoir un Raspberry Pi « léger », qui agit comme passerelle entre le monde physique (Arduino/capteur) et le cloud (Firestore), tandis que la visualisation se fait via un simple navigateur web.

---

## Structure du projet

- `serial_to_firebase.py`  
  Script Python exécuté sur le Raspberry Pi.  
  - Ouvre le port série (`/dev/ttyUSB0`, 9600 bauds, timeout 1 s).  
  - Lit les lignes série envoyées par l’Arduino.  
  - Extrait les valeurs d’humidité et de température.  
  - Écrit :
    - la valeur courante dans `donne_dh11` (document `temp_hum`),
    - l’historique dans `donne_dh11_history` (un document par mesure).

- `dashboard.py`  
  Définition du tableau de bord Dash/Plotly.  
  - Composants :
    - Titre : « Dashboard Réseau local - Données Cloud »,
    - Bouton “Actualiser”,
    - Conteneur pour les jauges,
    - Conteneur pour les graphes,
    - Indicateur “Dernière mise à jour”.
  - Callback :
    - récupère les 200 dernières mesures dans `donne_dh11_history`,
    - convertit les timestamps en `datetime`,
    - convertit `temperature` et `humidite` en valeurs numériques,
    - supprime les lignes invalides,
    - crée :
      - 1 jauge pour `temperature`,
      - 1 jauge pour `humidite`,
      - 1 graphe temporel pour chaque variable.

- `firebase_config.py`  
  - Initialise le SDK Firebase Admin à partir d’une clé de service (`firebase-key.json`).  
  - Expose un client Firestore (`db`) utilisé par `serial_to_firebase.py` et `dashboard.py`.

- `firebase-key.json`  
  - Fichier de clé de service Firebase (compte de service).  
  - Ce fichier doit être remplacé par ta propre clé téléchargée depuis la console Firebase.  
  - **Ne jamais committer une clé réelle dans un dépôt public.**

- `requirements.txt`  
  Liste des dépendances Python :
  - `dash`
  - `firebase-admin`
  - `paho-mqtt`
  - `python-dotenv`
  - `plotly`
  - `pandas`

- `run.sh`  
  Script bash pour lancer facilement le tableau de bord :
  - crée un environnement virtuel Python `env` (si inexistant),
  - active l’environnement,
  - installe les dépendances (`pip install -r requirements.txt`),
  - lance `python3 app.py`,
  - désactive l’environnement virtuel à l’arrêt.

> Remarque : le script `run.sh` suppose l’existence d’un fichier `app.py` qui crée l’application Dash et importe le layout et les callbacks définis dans `dashboard.py`.

---

## Prérequis

### Matériel

- Arduino Uno (ou compatible) avec un capteur de température/humidité (par exemple DHT11/DHT22).
- Raspberry Pi avec :
  - une connexion Internet,
  - un port USB libre pour connecter l’Arduino.

### Logiciel

- Python 3.x installé sur le Raspberry Pi.
- Un projet Firebase configuré avec Firestore Database (mode natif).
- Un fichier de clé de service Firebase (`firebase-key.json`), généré depuis la console Firebase.
- Les paquets Python listés dans `requirements.txt`.

---

## Installation et configuration

1. **Cloner le dépôt (sur le Raspberry Pi)**

   ```bash
   git clone <url-de-ton-depot>.git
   cd <dossier-du-projet>
