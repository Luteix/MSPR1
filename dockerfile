FROM debian:12-slim

WORKDIR /app

# 1. Installation de Python, pip et de l'outil ping (iputils-ping)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    iputils-ping \
 && rm -rf /var/lib/apt/lists/*

# 2. Copie et installation des dépendances Python
COPY requirements.txt .

# Utilisation de --break-system-packages pour autoriser pip à installer les paquets
# directement dans cet environnement Debian isolé.
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# 3. Copie du reste du code
COPY . .

# 4. Configuration réseau et lancement
EXPOSE 5000

CMD ["python3", "app.py"]