"""Product Intelligence Platform - Streamlit Application"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from visualization_data.filters import ProductFilters
from visualization_data.charts import ProductCharts
from ai_enrichment import ProductEnricher


@st.cache_data
def load_products_from_file(uploaded_file):
    """Load products from uploaded CSV file."""
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {str(e)}")
        return None


def validate_csv_structure(df):
    """Validate that the CSV has the required columns."""
    required_columns = [
        'product_id', 'product_type', 'product_tags', 'images_array', 
        'vendor', 'inventory_quantity', 'gross_amount_exc_tax_product', 'description'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Colonnes manquantes dans le fichier: {', '.join(missing_columns)}")
        st.info(f"Colonnes requises: {', '.join(required_columns)}")
        return False
    
    return True


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Product Intelligence Platform", 
        layout="wide"
    )
    
    st.title("🛍️ Product Intelligence Platform")
    st.write("Analyse et enrichissement de catalogues produits avec l'IA")
    
    # File upload section
    st.header("📁 Chargement des données")
    
    # Upload option
    uploaded_file = st.file_uploader(
        "Choisir un fichier CSV de produits",
        type=['csv'],
        help="Le fichier doit contenir les colonnes: product_id, product_type, product_tags, images_array, vendor, inventory_quantity, gross_amount_exc_tax_product, description"
    )
    
    # Load data
    df = None
    
    if uploaded_file is not None:
        # Load uploaded file
        df = load_products_from_file(uploaded_file)
        if df is not None and validate_csv_structure(df):
            st.success(f"✅ Fichier chargé avec succès: {len(df)} produits")
        else:
            df = None
    else:
        df = None
    
    if df is None:
        st.info("👆 Veuillez charger un fichier CSV pour commencer l'analyse")
        st.stop()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choisir une section",
        ["Vue d'ensemble", "Visualisations détaillées", "Enrichissement IA"]
    )
    
    if page == "Vue d'ensemble":
        display_overview_page(df)
    elif page == "Visualisations détaillées":
        display_detailed_visualizations_page(df)
    elif page == "Enrichissement IA":
        display_enrichment_page(df)


def display_overview_page(df: pd.DataFrame):
    """Display overview page with basic statistics."""
    charts = ProductCharts()
    filters = ProductFilters()
    
    # Display basic metrics
    charts.display_overview_metrics(df)
    
    # Display description quality analysis
    charts.display_description_quality_analysis(df)
    
    # Display missing descriptions by top vendors
    charts.display_missing_descriptions_by_vendor(df)
    
    # Get filters
    filter_values = filters.get_filter_inputs(df)
    
    # Apply filters
    filtered_df = filters.apply_filters(df, filter_values)
    
    st.write(f"**{len(filtered_df)} produits** correspondent aux critères")
    
    # Display filtered products table
    if len(filtered_df) > 0:
        st.header("📋 Produits filtrés")
        
        display_df = filtered_df[
            ['product_id', 'vendor', 'product_type', 'description']
        ].copy()
        display_df['description'] = (
            display_df['description'].fillna('').str[:100] + '...'
        )
        
        st.dataframe(display_df, use_container_width=True)


def display_detailed_visualizations_page(df: pd.DataFrame):
    """Display detailed visualizations page with advanced scatter plot first."""
    charts = ProductCharts()
    
    st.header("📊 Visualisations détaillées")
    
    # Advanced scatter plot first
    st.subheader("🎯 Visualisation avancée")
    st.write(
        "Cette visualisation montre la relation entre prix, stock et marques "
        "pour les 50 meilleurs types de produits selon le critère sélectionné."
    )
    charts.display_advanced_scatter_plot(df)
    
    # Separator
    st.divider()
    
    # Other detailed charts
    st.subheader("📈 Analyses complémentaires")
    
    # Vendor distribution
    charts.display_vendor_distribution(df)
    
    # Product type distribution
    charts.display_product_type_distribution(df)
    
    # Inventory analysis
    charts.display_inventory_analysis(df)
    
    # Price analysis
    charts.display_price_analysis(df)


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
    with col2:
        if enricher.is_ollama_available():
            st.success("🟢 Ollama connecté")
        else:
            st.error("🔴 Ollama non disponible")
            st.info("Lancez Ollama avec: `ollama serve`")
    
    # Model selection
    if enricher.is_ollama_available():
        available_models = enricher.get_available_models()
        if available_models:
            selected_model = st.selectbox(
                "Modèle IA:",
                available_models,
                index=0 if "llama3.1" in str(available_models) else 0,
                help="Modèle utilisé pour générer les descriptions"
            )
            enricher.model = selected_model
        else:
            st.warning("Aucun modèle disponible. Téléchargez un modèle avec: `ollama pull llama3.1:8b`")
    
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


if __name__ == "__main__":
    main()