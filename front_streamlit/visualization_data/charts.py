"""Data visualization charts using Plotly for the Streamlit application."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ast
import json


class ProductCharts:
    """Handles all product data visualization."""
    
    @staticmethod
    def display_overview_metrics(df: pd.DataFrame):
        """Display basic catalog overview metrics.
        
        Args:
            df: Product dataframe
        """
        st.header("📊 Vue d'ensemble du catalogue")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total produits", f"{len(df):,}")
        
        with col2:
            st.metric("Marques uniques", df['vendor'].nunique())
        
        with col3:
            st.metric("Types de produits", df['product_type'].nunique())
        
        with col4:
            missing_desc = df['description'].isna().sum()
            st.metric("Descriptions manquantes", missing_desc)
    
    @staticmethod
    def display_vendor_distribution(df: pd.DataFrame):
        """Display vendor distribution chart.
        
        Args:
            df: Product dataframe
        """
        st.subheader("📈 Répartition par marque")
        
        vendor_counts = df['vendor'].value_counts().head(15)
        
        fig = px.bar(
            x=vendor_counts.values,
            y=vendor_counts.index,
            orientation='h',
            title="Top 15 des marques par nombre de produits",
            labels={'x': 'Nombre de produits', 'y': 'Marque'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def display_product_type_distribution(df: pd.DataFrame):
        """Display product type distribution chart.
        
        Args:
            df: Product dataframe
        """
        st.subheader("🏷️ Répartition par type de produit")
        
        type_counts = df['product_type'].value_counts().head(10)
        
        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Top 10 des types de produits"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def display_description_quality_analysis(df: pd.DataFrame):
        """Display description quality analysis charts.
        
        Args:
            df: Product dataframe
        """
        st.subheader("📝 Analyse de la qualité des descriptions")
        
        # Calculate description lengths
        df_analysis = df.copy()
        df_analysis['desc_length'] = df_analysis['description'].fillna('').str.len()
        df_analysis['desc_category'] = pd.cut(
            df_analysis['desc_length'],
            bins=[0, 1, 50, 200, float('inf')],
            labels=['Vide', 'Courte (1-50)', 'Moyenne (51-200)', 'Longue (>200)'],
            include_lowest=True
        )
        
        # Quality distribution pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            quality_counts = df_analysis['desc_category'].value_counts()
            fig_pie = px.pie(
                values=quality_counts.values,
                names=quality_counts.index,
                title="Distribution de la qualité des descriptions"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Description length histogram
            fig_hist = px.histogram(
                df_analysis[df_analysis['desc_length'] > 0],
                x='desc_length',
                nbins=50,
                title="Distribution des longueurs de description",
                labels={'desc_length': 'Longueur (caractères)', 'count': 'Nombre de produits'}
            )
            fig_hist.update_layout(showlegend=False)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    @staticmethod
    def display_inventory_analysis(df: pd.DataFrame):
        """Display inventory analysis if data is available.
        
        Args:
            df: Product dataframe
        """
        if 'inventory_quantity' not in df.columns:
            return
            
        st.subheader("📦 Analyse des stocks")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Inventory distribution
            inventory_stats = df['inventory_quantity'].describe()
            fig_box = px.box(
                df, 
                y='inventory_quantity',
                title="Distribution des quantités en stock"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        with col2:
            # Top vendors by inventory
            vendor_inventory = df.groupby('vendor')['inventory_quantity'].sum().sort_values(ascending=False).head(10)
            fig_bar = px.bar(
                x=vendor_inventory.values,
                y=vendor_inventory.index,
                orientation='h',
                title="Top 10 marques par stock total",
                labels={'x': 'Stock total', 'y': 'Marque'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    @staticmethod
    def display_price_analysis(df: pd.DataFrame):
        """Display price analysis if data is available.
        
        Args:
            df: Product dataframe
        """
        if 'gross_amount_exc_tax_product' not in df.columns:
            return
            
        st.subheader("💰 Analyse des prix")
        
        # Remove zero and negative prices for analysis
        price_df = df[df['gross_amount_exc_tax_product'] > 0].copy()
        
        if len(price_df) == 0:
            st.warning("Aucune donnée de prix valide trouvée")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price distribution
            fig_hist = px.histogram(
                price_df,
                x='gross_amount_exc_tax_product',
                nbins=50,
                title="Distribution des prix",
                labels={'gross_amount_exc_tax_product': 'Prix (€)', 'count': 'Nombre de produits'}
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Average price by vendor (top 15)
            vendor_prices = price_df.groupby('vendor')['gross_amount_exc_tax_product'].agg(['mean', 'count'])
            vendor_prices = vendor_prices[vendor_prices['count'] >= 5].sort_values('mean', ascending=False).head(15)
            
            fig_bar = px.bar(
                x=vendor_prices['mean'],
                y=vendor_prices.index,
                orientation='h',
                title="Prix moyen par marque (≥5 produits)",
                labels={'x': 'Prix moyen (€)', 'y': 'Marque'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    @staticmethod
    def display_missing_descriptions_by_vendor(df: pd.DataFrame):
        """Display missing descriptions analysis by top vendors.
        
        Args:
            df: Product dataframe
        """
        st.subheader("🔍 Descriptions manquantes par marque (Top 10)")
        
        # Calculate missing descriptions by vendor
        df_analysis = df.copy()
        df_analysis['has_missing_desc'] = (
            df_analysis['description'].isna() | 
            (df_analysis['description'].str.strip() == '')
        )
        
        # Calculate stats for ALL vendors
        vendor_stats = []
        for vendor in df_analysis['vendor'].dropna().unique():
            vendor_data = df_analysis[df_analysis['vendor'] == vendor]
            total_products = len(vendor_data)
            missing_desc = vendor_data['has_missing_desc'].sum()
            missing_pct = (missing_desc / total_products * 100) if total_products > 0 else 0
            
            vendor_stats.append({
                'vendor': vendor,
                'total_products': total_products,
                'missing_descriptions': missing_desc,
                'missing_percentage': missing_pct
            })
        
        vendor_stats_df = pd.DataFrame(vendor_stats)
        vendor_stats_df = vendor_stats_df.sort_values('missing_descriptions', ascending=False)
        
        # Keep only top 10 vendors with most missing descriptions
        top_10_missing = vendor_stats_df.head(10)
        
        # Create horizontal bar chart
        fig = px.bar(
            top_10_missing,
            x='missing_descriptions',
            y='vendor',
            orientation='h',
            title="Top 10 des marques avec le plus de descriptions manquantes",
            labels={'missing_descriptions': 'Descriptions manquantes', 'vendor': 'Marque'},
            text='missing_descriptions'
        )
        
        # Add percentage as hover info and display on bars
        fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Descriptions manquantes: %{x}<br>"
                "Pourcentage: %{customdata:.1f}%"
                "<extra></extra>"
            ),
            customdata=top_10_missing['missing_percentage'],
            texttemplate='%{text} (%{customdata:.1f}%)',
            textposition="outside"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def display_advanced_scatter_plot(df: pd.DataFrame):
        """Display advanced scatter plot with product_type grouping and product interaction.
        
        Args:
            df: Product dataframe
        """
        st.subheader("🎯 Visualisation avancée - Prix par type de produit")
        
        # Configuration options
        col1, col2 = st.columns(2)
        with col1:
            ranking_method = st.radio(
                "Critère de classement des types:",
                ["Nombre de lignes (count)", "Stock total (sum)"],
                help="Méthode pour sélectionner les 50 meilleurs types de produits"
            )
        
        with col2:
            sorting_method = st.radio(
                "Tri des produits par type:",
                ["Prix décroissant", "Prix croissant", "Aléatoire"],
                help="Comment trier les produits au sein de chaque type"
            )
        
        # Prepare data
        df_viz = ProductCharts._prepare_scatter_data(df, ranking_method, sorting_method)
        
        if df_viz.empty:
            st.warning("Aucune donnée disponible pour la visualisation")
            return
        
        # Filters
        st.write("**Filtres pour la visualisation:**")
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate counts for each product type
            type_counts = df_viz['product_type'].value_counts()
            available_types = ["Tous"]
            for ptype in sorted(df_viz['product_type'].dropna().unique()):
                count = type_counts.get(ptype, 0)
                available_types.append(f"{ptype} ({count} lignes)")
            
            selected_type_display = st.selectbox("Type de produit:", available_types, key="scatter_type")
            
            # Extract actual type name (remove count info)
            if selected_type_display == "Tous":
                selected_type = "Tous"
            else:
                selected_type = selected_type_display.split(" (")[0]
        
        with col2:
            available_vendors = ["Tous"] + sorted(df_viz['vendor'].dropna().unique())
            selected_vendor = st.selectbox("Marque:", available_vendors, key="scatter_vendor")
        
        # Apply filters
        filtered_viz = df_viz.copy()
        if selected_type != "Tous":
            filtered_viz = filtered_viz[filtered_viz['product_type'] == selected_type]
        if selected_vendor != "Tous":
            filtered_viz = filtered_viz[filtered_viz['vendor'] == selected_vendor]
        
        # Create scatter plot
        fig = ProductCharts._create_scatter_plot(filtered_viz)
        
        # Display plot and product selection
        col_plot, col_info = st.columns([7, 3])
        
        with col_plot:
            selected_points = st.plotly_chart(fig, use_container_width=True, key="scatter_plot")
        
        with col_info:
            st.write("**Fiche produit**")
            
            # Product selection
            if not filtered_viz.empty:
                selected_product_id = st.selectbox(
                    "Sélectionner un produit:",
                    options=filtered_viz['product_id'].tolist(),
                    format_func=lambda x: f"ID: {x}",
                    key="product_selector"
                )
                
                ProductCharts._display_product_card(filtered_viz, selected_product_id)
            else:
                st.info("Aucun produit à afficher")
    
    @staticmethod
    def _prepare_scatter_data(df: pd.DataFrame, ranking_method: str, sorting_method: str) -> pd.DataFrame:
        """Prepare data for scatter plot visualization."""
        # Filter valid data
        valid_df = df[
            (df['gross_amount_exc_tax_product'] > 0) & 
            (df['inventory_quantity'] > 0) &
            df['vendor'].notna() &
            df['product_type'].notna()
        ].copy()
        
        if valid_df.empty:
            return pd.DataFrame()
        
        # Select top 50 product types
        if "Stock total" in ranking_method:
            type_ranking = valid_df.groupby('product_type')['inventory_quantity'].sum()
        else:  # Nombre de lignes (count)
            type_ranking = valid_df.groupby('product_type').size()
        
        top_types = type_ranking.sort_values(ascending=False).head(50).index
        filtered_df = valid_df[valid_df['product_type'].isin(top_types)].copy()
        
        # Sort product types by ranking
        type_order = type_ranking[top_types].sort_values(ascending=False).index
        
        # Prepare scatter data with x_index
        scatter_data = []
        current_x = 0
        gap_between_types = 3
        
        for type_rank, product_type in enumerate(type_order):
            type_products = filtered_df[filtered_df['product_type'] == product_type].copy()
            
            # Sort products within product type
            if sorting_method == "Prix décroissant":
                type_products = type_products.sort_values('gross_amount_exc_tax_product', ascending=False)
            elif sorting_method == "Prix croissant":
                type_products = type_products.sort_values('gross_amount_exc_tax_product', ascending=True)
            else:  # Random
                type_products = type_products.sample(frac=1).reset_index(drop=True)
            
            # Assign x_index
            for i, (_, product) in enumerate(type_products.iterrows()):
                product_data = product.to_dict()
                product_data['x_index'] = current_x + i
                product_data['type_rank'] = type_rank + 1
                product_data['x_label_group'] = product_type
                
                # Fixed point size for all products
                product_data['point_size'] = 8
                
                # Extract first image URL
                images_str = str(product.get('images_array', '[]'))
                try:
                    images_list = ast.literal_eval(images_str) if images_str != 'nan' else []
                    first_image = images_list[0] if images_list else None
                except:
                    first_image = None
                product_data['first_image_url'] = first_image
                
                scatter_data.append(product_data)
            
            current_x += len(type_products) + gap_between_types
        
        return pd.DataFrame(scatter_data)
    
    @staticmethod
    def _create_scatter_plot(df_viz: pd.DataFrame) -> go.Figure:
        """Create the scatter plot figure."""
        if df_viz.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # Create scatter plot by vendor (for color coding)
        for vendor in df_viz['vendor'].unique():
            vendor_data = df_viz[df_viz['vendor'] == vendor]
            
            fig.add_trace(go.Scatter(
                x=vendor_data['x_index'],
                y=vendor_data['gross_amount_exc_tax_product'],
                mode='markers',
                name=vendor,
                marker=dict(
                    size=vendor_data['point_size'],
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Type: %{customdata[1]}<br>"
                    "Prix: %{y:.2f}€<br>"
                    "Stock: %{customdata[2]}<br>"
                    "ID: %{customdata[3]}"
                    "<extra></extra>"
                ),
                customdata=vendor_data[['vendor', 'product_type', 'inventory_quantity', 'product_id']].values
            ))
        
        # Add vertical lines to separate product types
        type_boundaries = df_viz.groupby('product_type')['x_index'].agg(['min', 'max'])
        for _, row in type_boundaries.iterrows():
            fig.add_vline(x=row['max'] + 1.5, line_dash="dash", line_color="gray", opacity=0.3)
        
        fig.update_layout(
            title="Prix des produits par type (Top 50)",
            xaxis_title="Index produit (groupé par type)",
            yaxis_title="Prix HT (€)",
            height=600,
            hovermode='closest',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        return fig
    
    @staticmethod
    def _display_product_card(df_viz: pd.DataFrame, product_id: int):
        """Display product information card."""
        product = df_viz[df_viz['product_id'] == product_id]
        
        if product.empty:
            st.info("Produit non trouvé")
            return
        
        product_data = product.iloc[0]
        
        # Display image if available
        if product_data.get('first_image_url'):
            try:
                st.image(product_data['first_image_url'], width=200)
            except:
                st.write("🖼️ Image non disponible")
        else:
            st.write("🖼️ Aucune image")
        
        # Product information
        st.write(f"**Marque:** {product_data['vendor']}")
        st.write(f"**Type:** {product_data['product_type']}")
        st.write(f"**Prix HT:** {product_data['gross_amount_exc_tax_product']:.2f}€")
        st.write(f"**Stock:** {product_data['inventory_quantity']}")
        st.write(f"**ID:** {product_data['product_id']}")
        
        # Description
        description = str(product_data.get('description', ''))
        if description and description != 'nan':
            if len(description) > 300:
                description = description[:300] + "..."
            st.write(f"**Description:**")
            st.write(description)
        else:
            st.write("**Description:** Non disponible")
        
        # Tags
        tags = str(product_data.get('product_tags', ''))
        if tags and tags != 'nan':
            st.write(f"**Tags:** {tags}")