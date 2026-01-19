#!/bin/bash

# Script de lancement pour VidEdit

echo "🎬 Démarrage de VidEdit..."

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -q -r requirements.txt

# Lancer l'application
echo "🚀 Lancement de l'application..."
python3 main.py
