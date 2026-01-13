"""Database management page for PostgreSQL operations."""

import streamlit as st
import pandas as pd
import os

# Import database utilities
try:
    from database_utils import load_csv_to_database, get_database_stats, check_database_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


def display_database_page(df: pd.DataFrame):
    """Display database management interface."""
    st.header("🗄️ Gestion de la base de données")
    st.write("Chargez vos données CSV enrichies dans PostgreSQL pour alimenter l'API de recherche")
    
    if not DATABASE_AVAILABLE:
        st.error("⚠️ Module de base de données non disponible")
        st.info("Assurez-vous que les dépendances SQLAlchemy et psycopg2-binary sont installées")
        return
    
    # Database connection status
    st.subheader("🔌 Statut de connexion")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if check_database_connection():
            st.success("🟢 Connexion PostgreSQL active")
        else:
            st.error("🔴 Connexion PostgreSQL échouée")
            st.info("Vérifiez la configuration de DATABASE_URL dans les variables d'environnement")
    
    with col2:
        if st.button("🔄 Tester connexion"):
            if check_database_connection():
                st.success("✅ Test réussi")
            else:
                st.error("❌ Test échoué")
    
    # Database statistics
    if check_database_connection():
        st.subheader("📊 Statistiques de la base")
        db_stats = get_database_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Produits totaux", db_stats["total_products"])
        with col2:
            st.metric("Marques", db_stats["vendors_count"])
        with col3:
            st.metric("Types", db_stats["types_count"])
        with col4:
            st.metric("Avec description", db_stats["with_description"])
    
    # CSV to Database loading
    st.subheader("📤 Chargement des données")
    
    st.info("💡 Cette action va charger les données CSV actuelles (enrichies) dans PostgreSQL")
    
    if df is not None and len(df) > 0:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**Données à charger:** {len(df)} produits")
            
            # Show sample
            with st.expander("👀 Aperçu des données"):
                st.dataframe(df.head())
        
        with col2:
            if st.button(
                "🚀 Charger en base",
                type="primary",
                help="Charge les données CSV dans PostgreSQL (écrase les données existantes)"
            ):
                if check_database_connection():
                    # Save current dataframe to temporary CSV
                    temp_csv_path = "temp_products.csv"
                    df.to_csv(temp_csv_path, index=False)
                    
                    # Load to database
                    with st.spinner("Chargement en cours..."):
                        success, message = load_csv_to_database(temp_csv_path)
                    
                    # Clean up temp file
                    try:
                        os.remove(temp_csv_path)
                    except:
                        pass
                    
                    # Show result
                    if success:
                        st.success(message)
                        st.rerun()  # Refresh to update stats
                    else:
                        st.error(message)
                else:
                    st.error("❌ Pas de connexion à la base de données")
    else:
        st.warning("⚠️ Aucune donnée CSV chargée pour le transfert")
    
    # API Information
    st.subheader("🔌 API de recherche")
    st.info(
        "Une fois les données chargées en base, l'API FastAPI peut être utilisée "
        "pour effectuer des recherches avancées sur le catalogue produits."
    )
    
    # Instructions
    with st.expander("📝 Instructions API"):
        st.markdown("""
        **Pour démarrer l'API:**
        ```bash
        # Depuis le répertoire du projet
        cd api
        uvicorn main:app --reload --port 8000
        ```
        
        **Endpoints disponibles:**
        - `GET /api/v1/products/search` - Recherche de produits
        - `GET /api/v1/products/{id}` - Produit par ID
        - `GET /api/v1/vendors` - Liste des marques
        - `GET /api/v1/product-types` - Liste des types
        
        **Documentation interactive:** http://localhost:8000/docs
        """)