# Dockerfile pour PostgreSQL avec initialisation The Bradery
FROM postgres:15-alpine

# Variables d'environnement PostgreSQL
ENV POSTGRES_DB=thebradery_db
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Installer des utilitaires supplémentaires
RUN apk add --no-cache \
    curl \
    vim \
    postgresql-contrib

# Copier les scripts d'initialisation
COPY database/init/ /docker-entrypoint-initdb.d/

# Copier les données d'exemple (optionnel)
COPY Data/ /tmp/data/

# Exposer le port PostgreSQL
EXPOSE 5432

# Créer des volumes pour la persistance
VOLUME ["/var/lib/postgresql/data"]

# Commande de démarrage par défaut (héritée de postgres:15-alpine)
CMD ["postgres"]