@echo off
REM Script de lancement pour VidEdit (Windows)

echo 🎬 Démarrage de VidEdit...

REM Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Installer les dépendances
echo 📥 Installation des dépendances...
pip install -q -r requirements.txt

REM Lancer l'application
echo 🚀 Lancement de l'application...
python main.py

pause
