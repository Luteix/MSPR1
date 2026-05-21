FROM debian:12-slim

WORKDIR /app

# Installation d'un environement python et de la librairie pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

#Installation des dépendances pour MySQL
RUN apt-get update && apt-get install -y \ 
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances python
COPY requirements.txt .

#Installation de la liste des dépendances utiles pour le porjet
RUN pip3 install --no-cache-dir -r requirements.txt

# Copie du reste du code
COPY . .

# Exposition du port Flask
EXPOSE 5000

CMD ["python3", "app.py"]
