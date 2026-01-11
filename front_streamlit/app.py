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


@st.cache_data
def load_products():
    """Load products from CSV file."""
    csv_path = Path("Data/products.csv")
    if not csv_path.exists():
        st.error("products.csv not found in Data/ directory")
        return None
    
    return pd.read_csv(csv_path)


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Product Intelligence Platform", 
        layout="wide"
    )
    
    st.title("🛍️ Product Intelligence Platform")
    st.write("Analyse et enrichissement de catalogues produits avec l'IA")
    
    # Load data
    df = load_products()
    if df is None:
        return
    
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
    
    st.header("🤖 Enrichissement IA des descriptions")
    st.info("Section d'enrichissement IA - À implémenter")
    
    # Description quality stats
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
    
    # Get filters for enrichment
    st.subheader("Sélection des produits à enrichir")
    filter_values = filters.get_filter_inputs(df)
    filtered_df = filters.apply_filters(df, filter_values)
    
    st.write(f"**{len(filtered_df)} produits** sélectionnés pour enrichissement")
    
    if len(filtered_df) > 0:
        # Product selection for enrichment
        selected_products = st.multiselect(
            "Sélectionner des produits spécifiques (optionnel):",
            options=filtered_df['product_id'].tolist(),
            format_func=lambda x: f"ID: {x} - {filtered_df[filtered_df['product_id']==x]['vendor'].iloc[0]}"
        )
        
        products_to_enrich = (
            filtered_df[filtered_df['product_id'].isin(selected_products)] 
            if selected_products 
            else filtered_df
        )
        
        if st.button("Enrichir les descriptions sélectionnées", type="primary"):
            st.warning(
                f"Fonctionnalité d'enrichissement IA en cours de développement\n"
                f"Produits à traiter: {len(products_to_enrich)}"
            )


if __name__ == "__main__":
    main()