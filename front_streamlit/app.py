"""Product Intelligence Platform - Streamlit Application"""

import streamlit as st

# Import page functions from the pages module
from front_streamlit.pages import (
    display_overview_page,
    load_products_from_file,
    validate_csv_structure,
    display_detailed_visualizations_page,
    display_enrichment_page,
    display_database_page,
    display_api_explorer_page
)

# Import database utilities
try:
    from database_utils import check_database_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


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
    
    # Add database section if available
    nav_options = ["Vue d'ensemble", "Visualisations détaillées", "Enrichissement IA", "🔍 API Explorer"]
    if DATABASE_AVAILABLE:
        nav_options.append("🗄️ Base de données")
    
    page = st.sidebar.selectbox(
        "Choisir une section",
        nav_options
    )
    
    if page == "Vue d'ensemble":
        display_overview_page(df)
    elif page == "Visualisations détaillées":
        display_detailed_visualizations_page(df)
    elif page == "Enrichissement IA":
        display_enrichment_page(df)
    elif page == "🔍 API Explorer":
        display_api_explorer_page()
    elif page == "🗄️ Base de données":
        display_database_page(df)


if __name__ == "__main__":
    main()