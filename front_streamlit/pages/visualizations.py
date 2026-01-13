"""Detailed visualizations page with advanced charts and analytics."""

import streamlit as st
import pandas as pd

from visualization_data.charts import ProductCharts


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