# VidEdit 🎬

Application de montage vidéo locale avec interface graphique PyQt5.

## Fonctionnalités ✨

- **✂️ Découpage vidéo** : Découpez des portions spécifiques de vos vidéos en définissant les temps de début et de fin
- **🔄 Redimensionnement** : Modifiez la taille de vos vidéos avec des facteurs scale X et Y personnalisables
- **🎵 Ajout d'audio** : Ajoutez ou remplacez la piste audio de vos vidéos
- **🔗 Fusion de vidéos** : Combinez plusieurs vidéos en une seule

## Prérequis 📋

- Python 3.7 ou supérieur
- FFmpeg installé sur votre système

### Installation de FFmpeg

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Téléchargez depuis [ffmpeg.org](https://ffmpeg.org/download.html) et ajoutez au PATH.

## Installation 🚀

### Méthode 1 : Utiliser les scripts de lancement (Recommandé)

**Linux/macOS:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
Double-cliquez sur `run.bat` ou exécutez dans le terminal:
```cmd
run.bat
```

Ces scripts créeront automatiquement l'environnement virtuel et installeront les dépendances.

### Méthode 2 : Installation manuelle

1. Clonez ou téléchargez ce dépôt
2. Créez un environnement virtuel:
```bash
python3 -m venv venv
```

3. Activez l'environnement virtuel:

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```cmd
venv\Scripts\activate
```

4. Installez les dépendances:
```bash
pip install -r requirements.txt
```

5. Lancez l'application:
```bash
python3 main.py
```

## Utilisation 📖

### 1. Charger une vidéo
Cliquez sur le bouton "📁 Charger une vidéo" et sélectionnez votre fichier vidéo.

### 2. Découpage vidéo
- Allez dans l'onglet "✂️ Découper"
- Définissez le temps de début et de fin en secondes
- Cliquez sur "✂️ Découper la vidéo"
- Choisissez où enregistrer la vidéo découpée

### 3. Redimensionnement
- Allez dans l'onglet "🔄 Redimensionner"
- Ajustez les valeurs Scale X et Scale Y (100 = taille originale)
- Utilisez les presets (50%, 200%) pour des valeurs communes
- Cliquez sur "🔄 Redimensionner la vidéo"

### 4. Ajout d'audio
- Allez dans l'onglet "🎵 Ajouter Audio"
- Cliquez sur "📁 Choisir un fichier audio"
- Cochez "Remplacer l'audio existant" si vous voulez remplacer au lieu de mixer
- Cliquez sur "🎵 Ajouter l'audio"

### 5. Fusion de vidéos
- Allez dans l'onglet "🔗 Fusionner"
- Ajoutez plusieurs vidéos à la liste (dans l'ordre souhaité)
- Cliquez sur "🔗 Fusionner les vidéos"
- Choisissez où enregistrer la vidéo fusionnée

## Structure du projet 📁

```
VidEdit/
├── main.py              # Point d'entrée de l'application
├── video_editor.py      # Interface graphique PyQt5
├── video_processor.py   # Logique de traitement vidéo
├── requirements.txt     # Dépendances Python
├── run.sh              # Script de lancement Linux/macOS
├── run.bat             # Script de lancement Windows
└── README.md           # Ce fichier
```

## Formats supportés 🎞️

**Vidéo:**
- MP4
- AVI
- MOV
- MKV

**Audio:**
- MP3
- WAV
- AAC
- M4A

## Dépendances 📦

- PyQt5: Interface graphique
- MoviePy: Traitement vidéo
- NumPy: Calculs numériques
- Pillow: Traitement d'images

## Dépannage 🔧

### Erreur: "No module named 'PyQt5'"
Assurez-vous d'avoir activé l'environnement virtuel et installé les dépendances.

### Erreur: "ffmpeg not found"
FFmpeg doit être installé sur votre système et accessible dans le PATH.

### Vidéo trop lente à traiter
Le traitement vidéo peut prendre du temps selon:
- La taille et la durée de la vidéo
- La puissance de votre ordinateur
- Le type d'opération effectuée

## Contribution 🤝

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou à proposer une pull request.

## Licence 📄

Ce projet est open source et disponible sous licence MIT.
