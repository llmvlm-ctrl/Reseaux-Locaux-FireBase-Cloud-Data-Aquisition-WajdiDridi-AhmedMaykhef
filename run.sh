#!/bin/bash

# Nom de l'environnement virtuel
ENV_DIR="env"

# Créer un environnement virtuel s'il n'existe pas
if [ ! -d "$ENV_DIR" ]; then
  echo "🧪 Création de l'environnement virtuel..."
  python3 -m venv $ENV_DIR
fi

# Activer l'environnement
source $ENV_DIR/bin/activate

#!/bin/bash

echo "🔧 Installation des dépendances..."
pip install -r requirements.txt

echo "🚀 Lancement du dashboard cloud..."
python3 app.py

echo "🛑 Arrêt du dashboard — désactivation de l'environnement..."
deactivate
