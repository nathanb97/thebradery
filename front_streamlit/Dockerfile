# Dockerfile pour Streamlit Frontend
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
RUN useradd -m -u 1000 streamlituser

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
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

# Changer vers l'utilisateur non-root
USER streamlituser

# Exposer le port Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Créer le répertoire .streamlit pour la config
RUN mkdir -p /home/streamlituser/.streamlit

# Configuration Streamlit
RUN echo '[server]\n\
headless = true\n\
port = 8501\n\
address = "0.0.0.0"\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
' > /home/streamlituser/.streamlit/config.toml

# Lancer Streamlit
CMD ["streamlit", "run", "front_streamlit/app.py", "--server.address", "0.0.0.0"]