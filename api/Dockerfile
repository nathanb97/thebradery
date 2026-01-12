# Dockerfile pour l'API FastAPI
FROM python:3.11-slim-bookworm

# Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y \
    libpq-dev \
    gcc \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -m -u 1000 apiuser

# Copier les fichiers de configuration
COPY requirements.txt /app/requirements.txt
WORKDIR /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . /app/

# Variables d'environnement
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://user:password@postgres:5432/thebradery_db

# Changer vers l'utilisateur non-root
USER apiuser

# Exposer le port de l'API
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Lancer l'API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]