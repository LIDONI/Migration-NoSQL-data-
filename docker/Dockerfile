# Image python
FROM python:3.10-slim

# Le dossier de travail dans le conteneur
WORKDIR /app

# Copier des dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier tout le code source dans le conteneur
COPY . .

# La commande de démarage de l'application 
CMD ["pytest", "tests/"]
