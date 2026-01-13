"""Overview page with basic statistics and product filtering."""

import streamlit as st
import pandas as pd

from visualization_data.filters import ProductFilters
from visualization_data.charts import ProductCharts


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