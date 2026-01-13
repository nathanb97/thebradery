"""AI enrichment page for generating product descriptions."""

import streamlit as st
import pandas as pd
import os

from visualization_data.filters import ProductFilters
from front_streamlit.ai_enrichment import ProductEnricher

# Import database utilities
try:
    from database_utils import load_csv_to_database, check_database_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


def display_enrichment_page(df: pd.DataFrame):
    """Display AI enrichment interface."""
    filters = ProductFilters()
    enricher = ProductEnricher()
    
    st.header("🤖 Enrichissement IA des descriptions")
    st.write("Utilisez l'IA pour générer automatiquement des descriptions manquantes")
    
    # Ollama status check
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Configuration IA")
        st.info(f"Modèle utilisé: {enricher.model}")
    with col2:
        if enricher.is_ollama_available():
            st.success("🟢 Ollama connecté")
        else:
            st.error("🔴 Ollama non disponible")
            st.info("Lancez Ollama avec: `ollama serve`")
    
    # Description quality stats
    st.subheader("📊 État des descriptions")
    quality_stats = filters.get_description_quality_stats(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total produits", quality_stats["total"])
    with col2:
        st.metric("Descriptions vides", f"{quality_stats['empty']} ({quality_stats['empty_pct']}%)")
    with col3:
        st.metric("Descriptions courtes", f"{quality_stats['short']} ({quality_stats['short_pct']}%)")
    with col4:
        st.metric("Descriptions longues", f"{quality_stats['long']} ({quality_stats['long_pct']}%)")
    
    # Products needing enrichment
    st.subheader("🎯 Enrichissement automatique")
    products_to_enrich = enricher.identify_missing_descriptions(df)
    
    if products_to_enrich.empty:
        st.success("🎉 Toutes les descriptions sont complètes!")
        st.balloons()
    else:
        st.warning(f"⚠️ {len(products_to_enrich)} produits ont besoin d'enrichissement")
        
        # Show sample of products to enrich
        with st.expander("👀 Aperçu des produits à enrichir"):
            sample_products = products_to_enrich[['product_id', 'vendor', 'product_type', 'description']].head(10)
            st.dataframe(sample_products, use_container_width=True)
        
        # Enrichment action
        if enricher.is_ollama_available():
            if st.button(
                f"🚀 Enrichir toutes les descriptions manquantes ({len(products_to_enrich)} produits)",
                type="primary",
                help="Génère automatiquement des descriptions pour tous les produits sans description"
            ):
                # Store original df in session state if not exists
                if 'original_df' not in st.session_state:
                    st.session_state.original_df = df.copy()
                
                # Perform enrichment
                enriched_df = enricher.enrich_missing_descriptions(df)
                
                # Update session state
                st.session_state.enriched_df = enriched_df
                
                # Show statistics
                stats = enricher.get_enrichment_stats(df, enriched_df)
                
                st.success("✅ Enrichissement terminé!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Produits enrichis", stats["enriched_count"])
                with col2:
                    st.metric("Taux de succès", f"{stats['enrichment_rate']}%")
                with col3:
                    st.metric("Encore manquants", stats["still_missing"])
                
                # Download enriched data
                if stats["enriched_count"] > 0:
                    csv_data = enriched_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Télécharger le fichier enrichi (CSV)",
                        data=csv_data,
                        file_name="products_enriched.csv",
                        mime="text/csv"
                    )
        else:
            st.error("Ollama doit être disponible pour lancer l'enrichissement")
            st.info("Instructions:\n1. Installez Ollama: https://ollama.ai\n2. Lancez: `ollama serve`\n3. Téléchargez un modèle: `ollama pull llama3.1:8b`")
    
    # Show current session state
    if 'enriched_df' in st.session_state:
        st.divider()
        st.subheader("📈 Données enrichies en session")
        enriched_stats = filters.get_description_quality_stats(st.session_state.enriched_df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Descriptions vides: {enriched_stats['empty']} ({enriched_stats['empty_pct']}%)")
        with col2:
            if st.button("🔄 Utiliser les données enrichies pour les visualisations"):
                st.info("Fonctionnalité à implémenter: synchronisation avec les autres pages")
    
    # Export to PostgreSQL section
    if DATABASE_AVAILABLE:
        st.divider()
        st.subheader("🗄️ Export vers PostgreSQL")
        
        # Determine which dataset to export
        export_df = st.session_state.get('enriched_df', df) if 'enriched_df' in st.session_state else df
        is_enriched = 'enriched_df' in st.session_state
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if is_enriched:
                st.info(f"💡 Export des données enrichies ({len(export_df)} produits) vers PostgreSQL")
            else:
                st.info(f"💡 Export des données CSV originales ({len(export_df)} produits) vers PostgreSQL")
            
            if check_database_connection():
                st.success("🟢 Connexion PostgreSQL active")
            else:
                st.error("🔴 Connexion PostgreSQL échouée")
        
        with col2:
            if st.button(
                "🚀 Exporter vers DB",
                type="secondary",
                help="Charge les données dans PostgreSQL pour l'API de recherche"
            ):
                if check_database_connection():
                    # Save current dataframe to temporary CSV
                    temp_csv_path = "temp_export.csv"
                    export_df.to_csv(temp_csv_path, index=False)
                    
                    # Load to database
                    with st.spinner("Export en cours..."):
                        success, message = load_csv_to_database(temp_csv_path)
                    
                    # Clean up temp file
                    try:
                        os.remove(temp_csv_path)
                    except:
                        pass
                    
                    # Show result
                    if success:
                        st.success(message)
                        st.info("✅ L'API de recherche peut maintenant être utilisée")
                    else:
                        st.error(message)
                else:
                    st.error("❌ Impossible de se connecter à PostgreSQL")