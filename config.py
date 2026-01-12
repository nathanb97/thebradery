"""Configuration management for The Bradery project."""

from __future__ import annotations
import os
from enum import Enum


class EnvironmentVariables(Enum):
    # Database configuration
    DATABASE_URL = "DATABASE_URL"
    
    # PostgreSQL components
    PG_USER: str | None = "PG_USER"
    PG_PASSWORD: str | None = "PG_PASSWORD"
    PG_HOST: str | None = "PG_HOST"
    PG_PORT: str | None = "PG_PORT"
    PG_DATABASE: str | None = "PG_DATABASE"
    
    # Environment
    IS_LOCAL = "IS_LOCAL"
    
    # API configuration
    CORS_ORIGINS = "CORS_ORIGINS"
    API_HOST = "API_HOST"
    API_PORT = "API_PORT"
    
    # Ollama/AI configuration
    OLLAMA_BASE_URL = "OLLAMA_BASE_URL"
    OLLAMA_MODEL = "OLLAMA_MODEL"
    
    # Session/Security
    SESSIONMIDDLESECRET: str | None = "SESSIONMIDDLESECRET"

    def get(self: EnvironmentVariables, default: str | None = None) -> str:
        return os.environ.get(self.name, default)


# Initialisation des variables globales à None
DATABASE_URL = None
PG_USER = None
PG_PASSWORD = None
PG_HOST = None
PG_PORT = None
PG_DATABASE = None
IS_LOCAL = None
CORS_ORIGINS = None
API_HOST = None
API_PORT = None
OLLAMA_BASE_URL = None
OLLAMA_MODEL = None
SESSIONMIDDLESECRET = None

# Valeurs par défaut pour The Bradery
default_values = {
    "DATABASE_URL": "postgresql://user:password@localhost:5432/thebradery_db",
    "PG_USER": "user",
    "PG_PASSWORD": "password", 
    "PG_HOST": "localhost",
    "PG_PORT": "5432",
    "PG_DATABASE": "thebradery_db",
    "IS_LOCAL": "true",
    "CORS_ORIGINS": "http://localhost:8000,http://localhost:8501",  # API + Streamlit
    "API_HOST": "0.0.0.0",
    "API_PORT": "8000",
    "OLLAMA_BASE_URL": "http://localhost:11434",
    "OLLAMA_MODEL": "mistral:7b-instruct-v0.3-q4_1",
    "SESSIONMIDDLESECRET": "thebradery_secret_key_change_in_production"
}

# Initialisation des variables en utilisant le dictionnaire
for var, default_value in default_values.items():
    if hasattr(EnvironmentVariables, var):
        env_var = getattr(EnvironmentVariables, var)
        if isinstance(env_var, EnvironmentVariables):
            globals()[var] = env_var.get(default_value)
        else:
            globals()[var] = os.environ.get(var, default_value)
    else:
        globals()[var] = default_value


def build_database_url() -> str:
    """Build database URL from individual components if DATABASE_URL not set."""
    # Priorité 1: Utiliser DATABASE_URL si elle existe et n'est pas la valeur par défaut
    if DATABASE_URL and DATABASE_URL != default_values["DATABASE_URL"]:
        return DATABASE_URL
    
    # Priorité 2: Construire depuis les composants
    import urllib.parse
    escaped_password = urllib.parse.quote_plus(PG_PASSWORD)
    return f"postgresql://{PG_USER}:{escaped_password}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"


def get_cors_origins_list() -> list[str]:
    """Get CORS origins as a list."""
    return CORS_ORIGINS.split(',') if CORS_ORIGINS else []


def is_local_environment() -> bool:
    """Check if running in local environment."""
    return IS_LOCAL.lower() in ('true', '1', 'yes', 'local')


# Export computed values
COMPUTED_DATABASE_URL = build_database_url()
CORS_ORIGINS_LIST = get_cors_origins_list()
IS_LOCAL_ENV = is_local_environment()

# Print configuration for debugging (only in local)
if IS_LOCAL_ENV:
    print(f"🔧 Configuration loaded:")
    print(f"   DATABASE_URL: {COMPUTED_DATABASE_URL}")
    print(f"   OLLAMA_BASE_URL: {OLLAMA_BASE_URL}")
    print(f"   OLLAMA_MODEL: {OLLAMA_MODEL}")
    print(f"   CORS_ORIGINS: {CORS_ORIGINS_LIST}")
    print(f"   IS_LOCAL: {IS_LOCAL_ENV}")

