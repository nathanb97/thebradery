"""Product filtering functionality for the Streamlit application."""

import streamlit as st
import pandas as pd


class ProductFilters:
    """Handles all product filtering logic."""
    
    @staticmethod
    def get_filter_inputs(df: pd.DataFrame) -> dict:
        """Get filter inputs from user interface.
        
        Args:
            df: Product dataframe
            
        Returns:
            dict: Selected filter values
        """
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
        
        return {
            "vendor": selected_vendor,
            "product_type": selected_type,
            "quality_filter": quality_filter
        }
    
    @staticmethod
    def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        """Apply filters to the product dataframe.
        
        Args:
            df: Original product dataframe
            filters: Filter criteria from user input
            
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        filtered_df = df.copy()
        
        # Vendor filter
        if filters["vendor"] != "Tous":
            filtered_df = filtered_df[filtered_df['vendor'] == filters["vendor"]]
        
        # Product type filter
        if filters["product_type"] != "Tous":
            filtered_df = filtered_df[
                filtered_df['product_type'] == filters["product_type"]
            ]
        
        # Description quality filter
        quality_filter = filters["quality_filter"]
        if quality_filter == "Descriptions vides":
            filtered_df = filtered_df[
                filtered_df['description'].isna() | 
                (filtered_df['description'].str.strip() == '')
            ]
        elif quality_filter == "Descriptions courtes (<50 chars)":
            filtered_df = filtered_df[
                filtered_df['description'].str.len() < 50
            ]
        elif quality_filter == "Descriptions longues (>50 chars)":
            filtered_df = filtered_df[
                filtered_df['description'].str.len() >= 50
            ]
        
        return filtered_df
    
    @staticmethod
    def get_description_quality_stats(df: pd.DataFrame) -> dict:
        """Get statistics about description quality.
        
        Args:
            df: Product dataframe
            
        Returns:
            dict: Description quality statistics
        """
        total = len(df)
        empty_desc = df['description'].isna().sum()
        short_desc = (df['description'].str.len() < 50).sum()
        long_desc = (df['description'].str.len() >= 50).sum()
        
        return {
            "total": total,
            "empty": empty_desc,
            "short": short_desc,
            "long": long_desc,
            "empty_pct": round(empty_desc / total * 100, 1) if total > 0 else 0,
            "short_pct": round(short_desc / total * 100, 1) if total > 0 else 0,
            "long_pct": round(long_desc / total * 100, 1) if total > 0 else 0
        }