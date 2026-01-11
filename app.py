"""Product Intelligence Platform - Streamlit Application"""

import streamlit as st
import pandas as pd
from pathlib import Path


@st.cache_data
def load_products():
    """Load products from CSV file."""
    csv_path = Path("Data/products.csv")
    if not csv_path.exists():
        st.error("products.csv not found in Data/ directory")
        return None
    
    return pd.read_csv(csv_path)


def get_basic_stats(df):
    """Get basic statistics about the product catalog."""
    return {
        "total_products": len(df),
        "unique_vendors": df['vendor'].nunique(),
        "unique_product_types": df['product_type'].nunique(),
        "missing_descriptions": df['description'].isna().sum()
    }


def apply_filters(df, vendor, product_type, quality_filter):
    """Apply filters to the product dataframe."""
    filtered_df = df.copy()
    
    if vendor != "Tous":
        filtered_df = filtered_df[filtered_df['vendor'] == vendor]
    
    if product_type != "Tous":
        filtered_df = filtered_df[filtered_df['product_type'] == product_type]
    
    if quality_filter == "Descriptions vides":
        filtered_df = filtered_df[
            filtered_df['description'].isna() | 
            (filtered_df['description'].str.strip() == '')
        ]
    elif quality_filter == "Descriptions courtes (<50 chars)":
        filtered_df = filtered_df[filtered_df['description'].str.len() < 50]
    elif quality_filter == "Descriptions longues (>50 chars)":
        filtered_df = filtered_df[filtered_df['description'].str.len() >= 50]
    
    return filtered_df


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Product Intelligence Platform", 
        layout="wide"
    )
    
    st.title("🛍️ Product Intelligence Platform")
    st.write("Enrichissez vos descriptions de produits avec l'IA")
    
    # Load data
    df = load_products()
    if df is None:
        return
    
    # Display statistics
    st.header("📊 Statistiques du catalogue")
    stats = get_basic_stats(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total produits", stats["total_products"])
    with col2:
        st.metric("Marques uniques", stats["unique_vendors"])
    with col3:
        st.metric("Types de produits", stats["unique_product_types"])
    with col4:
        st.metric("Descriptions manquantes", stats["missing_descriptions"])
    
    # Filter section
    st.header("🔍 Filtrage des produits")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vendors = ["Tous"] + sorted(df['vendor'].dropna().unique())
        selected_vendor = st.selectbox("Marque", vendors)
    
    with col2:
        product_types = ["Tous"] + sorted(df['product_type'].dropna().unique())
        selected_type = st.selectbox("Type de produit", product_types)
    
    with col3:
        quality_options = [
            "Tous",
            "Descriptions vides", 
            "Descriptions courtes (<50 chars)",
            "Descriptions longues (>50 chars)"
        ]
        quality_filter = st.selectbox("Qualité de description", quality_options)
    
    # Apply filters
    filtered_df = apply_filters(df, selected_vendor, selected_type, quality_filter)
    
    st.write(f"**{len(filtered_df)} produits** correspondent aux critères")
    
    # Display filtered products
    if len(filtered_df) > 0:
        st.header("📋 Produits filtrés")
        
        display_df = filtered_df[
            ['product_id', 'vendor', 'product_type', 'description']
        ].copy()
        display_df['description'] = (
            display_df['description'].fillna('').str[:100] + '...'
        )
        
        st.dataframe(display_df, use_container_width=True)
        
        # Enrichment section
        st.header("🤖 Enrichissement IA")
        st.info("Section d'enrichissement IA - À implémenter")
        
        selected_products = st.multiselect(
            "Sélectionner des produits à enrichir",
            options=filtered_df['product_id'].tolist(),
            format_func=lambda x: f"ID: {x}"
        )
        
        if selected_products:
            if st.button("Enrichir les descriptions sélectionnées"):
                st.warning("Fonctionnalité d'enrichissement IA en cours de développement")


if __name__ == "__main__":
    main()