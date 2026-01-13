"""Product Intelligence Platform - Streamlit Application"""

import streamlit as st
import pandas as pd
from pathlib import Path
import os


from visualization_data.filters import ProductFilters
from visualization_data.charts import ProductCharts
from front_streamlit.ai_enrichment import ProductEnricher
from config import API_BASE_URL

# Import database utilities
try:
    from database_utils import load_csv_to_database, get_database_stats, check_database_connection
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


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


def display_api_explorer_page():
    """Display API Explorer interface."""
    st.header("🔍 API Explorer")
    st.write(f"Interrogez l'API FastAPI sur {API_BASE_URL} pour tester les endpoints.")
    
    import requests
    
    api_base_url = API_BASE_URL
    
    # Test connection first
    st.subheader("🔌 Test de connexion API")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏥 Test Health"):
            try:
                response = requests.get(f"{api_base_url}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    st.success(f"✅ API connectée! Status: {health_data.get('status', 'OK')}")
                    st.info(f"Database: {health_data.get('database', 'Unknown')}")
                else:
                    st.error(f"❌ API Error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Impossible de se connecter à l'API")
                st.info("💡 Lancez l'API avec: `docker-compose up api`")
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
    
    with col2:
        if st.button("📊 Get Stats"):
            try:
                response = requests.get(f"{api_base_url}/api/v1/stats", timeout=10)
                response.raise_for_status()
                stats = response.json()
                
                # Display stats
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    st.metric("Total Products", stats.get('total_products', 0))
                with col_stat2:
                    st.metric("Total Vendors", stats.get('total_vendors', 0))
                with col_stat3:
                    st.metric("Avg Price", f"€{stats.get('avg_price', 0):.2f}")
                    
            except Exception as e:
                st.error(f"❌ Erreur stats: {str(e)}")
    
    # Main API testing tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Product Search", "🤖 Enriched Products", "📚 API Examples"])
    
    with tab1:
        st.subheader("🔍 Search Products")
        
        # Search form
        with st.form("api_search_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                search_query = st.text_input("Search Query", placeholder="dress, luxury")
                min_price = st.number_input("Min Price €", min_value=0.0, step=10.0, value=None)
                search_vendors = st.text_input("Vendors", placeholder="CHANEL,DIOR")
            
            with col2:
                search_limit = st.slider("Limit", 5, 100, 20)
                max_price = st.number_input("Max Price €", min_value=0.0, step=10.0, value=None)
                has_desc = st.selectbox("Has Description", [None, True, False])
            
            search_submitted = st.form_submit_button("🔍 Search via API")
        
        if search_submitted:
            try:
                # Build API parameters
                params = {"limit": search_limit, "offset": 0}
                if search_query:
                    params["query"] = search_query
                if min_price:
                    params["price_min"] = min_price
                if max_price:
                    params["price_max"] = max_price
                if search_vendors:
                    params["vendors"] = search_vendors.split(",")
                if has_desc is not None:
                    params["has_description"] = has_desc
                
                with st.spinner("Searching via API..."):
                    response = requests.get(f"{api_base_url}/api/v1/products/search", 
                                          params=params, timeout=15)
                    response.raise_for_status()
                    result = response.json()
                
                products = result.get("products", [])
                page_info = result.get("page_info", {})
                
                st.success(f"✅ Found {page_info.get('total_count', 0)} products via API")
                
                # Display products
                if products:
                    for product in products:
                        with st.container():
                            col_prod1, col_prod2 = st.columns([1, 3])
                            
                            with col_prod1:
                                # Try to display image
                                images = product.get("images_array")
                                if images:
                                    try:
                                        import json
                                        if isinstance(images, str):
                                            images_list = json.loads(images)
                                            if images_list and len(images_list) > 0:
                                                st.image(images_list[0], width=120)
                                    except:
                                        st.caption("📷 Image")
                                else:
                                    st.caption("📷 No image")
                            
                            with col_prod2:
                                st.write(f"**#{product.get('product_id')} - {product.get('vendor', 'N/A')}**")
                                st.write(f"Type: {product.get('product_type', 'N/A')}")
                                price = product.get('gross_amount_exc_tax_product')
                                if price:
                                    st.write(f"Price: €{price:.2f}")
                                
                                desc = product.get('description')
                                if desc:
                                    is_ai = product.get('is_generated_description', False)
                                    desc_type = "🤖 AI" if is_ai else "📝 Original"
                                    st.write(f"**Description ({desc_type}):** {desc[:150]}...")
                                else:
                                    st.write("**Description:** None")
                        
                        st.divider()
                else:
                    st.info("No products found")
                    
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")
    
    with tab2:
        st.subheader("🤖 Enriched Products with Photos")
        st.write("⭐ Test de la nouvelle route `/api/v1/products/enriched`")
        
        # Enriched products form
        with st.form("enriched_search_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                enriched_has_photos = st.selectbox("Filter by Photos", [None, True, False], 
                                                 format_func=lambda x: "All" if x is None else ("With Photos" if x else "Without Photos"))
                enriched_limit = st.slider("Results Limit", 5, 50, 10)
            
            with col2:
                enriched_vendors = st.text_input("Vendors Filter", placeholder="CHANEL,DIOR")
                min_quality = st.slider("Min Quality Score", 0.0, 1.0, 0.0, step=0.1)
            
            enriched_submitted = st.form_submit_button("🤖 Get Enriched Products")
        
        if enriched_submitted:
            try:
                # Build enriched API parameters
                enriched_params = {
                    "limit": enriched_limit,
                    "offset": 0,
                    "sort_by": "product_id", 
                    "sort_order": "desc"
                }
                if enriched_has_photos is not None:
                    enriched_params["has_photos"] = str(enriched_has_photos).lower()
                if enriched_vendors:
                    enriched_params["vendors"] = enriched_vendors.split(",")
                if min_quality > 0:
                    enriched_params["min_quality_score"] = min_quality
                
                with st.spinner("Loading enriched products..."):
                    response = requests.get(f"{api_base_url}/api/v1/products/bonus",
                                          params=enriched_params, timeout=15)
                    response.raise_for_status()
                    result = response.json()
                
                products = result.get("products", [])
                page_info = result.get("page_info", {})
                enrichment_stats = result.get("enrichment_stats", {})
                
                # Display enrichment stats
                st.subheader("📊 Enrichment Statistics")
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                with col_stat1:
                    st.metric("Total Enriched", enrichment_stats.get('total_enriched', 0))
                with col_stat2:
                    enrichment_pct = enrichment_stats.get('enrichment_percentage', 0)
                    st.metric("Enrichment %", f"{enrichment_pct:.1f}%")
                with col_stat3:
                    st.metric("With Photos", enrichment_stats.get('with_photos', 0))
                with col_stat4:
                    st.metric("Without Photos", enrichment_stats.get('without_photos', 0))
                
                st.success(f"✅ Found {page_info.get('total_count', 0)} enriched products")
                
                # Display enriched products
                if products:
                    for product in products:
                        with st.container():
                            st.subheader(f"🤖 Product #{product.get('product_id')} - {product.get('vendor', 'N/A')}")
                            
                            # Metrics row
                            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                            with col_m1:
                                price = product.get('gross_amount_exc_tax_product')
                                st.metric("Price", f"€{price:.2f}" if price else "N/A")
                            with col_m2:
                                st.metric("Has Photos", "✅" if product.get('has_photos') else "❌")
                            with col_m3:
                                quality = product.get('quality_score')
                                st.metric("Quality", f"{quality:.2f}" if quality else "N/A")
                            with col_m4:
                                model = product.get('enrichment_model', 'N/A')
                                st.metric("AI Model", model)
                            
                            # Photos and descriptions
                            col_photos, col_desc = st.columns([1, 2])
                            
                            with col_photos:
                                st.write("**📷 Photos:**")
                                images = product.get("images_parsed", [])
                                if images:
                                    for i, img_url in enumerate(images[:2]):
                                        try:
                                            st.image(img_url, width=120, caption=f"Image {i+1}")
                                        except:
                                            st.caption(f"⚠️ Image {i+1} unavailable")
                                    if len(images) > 2:
                                        st.caption(f"+ {len(images)-2} more")
                                else:
                                    st.info("No images")
                            
                            with col_desc:
                                st.write("**📝 Description:**")
                                original_desc = product.get('original_description')
                                enriched_desc = product.get('enriched_description') or product.get('description')
                                
                                if original_desc and enriched_desc:
                                    st.write("*Original:*")
                                    st.info(original_desc[:100] + "...")
                                    st.write("*AI-Enhanced:*")
                                    st.success(enriched_desc[:100] + "...")
                                elif enriched_desc:
                                    st.write("*AI-Generated:*")
                                    st.success(enriched_desc)
                                else:
                                    st.warning("No description available")
                        
                        st.divider()
                else:
                    st.info("No enriched products found")
                    st.info("💡 Run AI enrichment first in the 'Enrichissement IA' tab")
                    
            except Exception as e:
                st.error(f"❌ Enriched products failed: {str(e)}")
    
    with tab3:
        st.subheader("📚 API Examples & Testing")
        
        if st.button("📖 Load API Examples"):
            try:
                response = requests.get(f"{api_base_url}/api/v1/examples/search", timeout=10)
                response.raise_for_status()
                examples = response.json()
                
                st.write("**Available API Endpoints:**")
                for example in examples.get("examples", []):
                    with st.expander(f"🔗 {example['description']}"):
                        full_url = f"{api_base_url}{example['url']}"
                        st.code(full_url)
                        
                        if st.button(f"Test this endpoint", key=f"test_{example['url']}"):
                            try:
                                test_response = requests.get(full_url, timeout=10)
                                test_response.raise_for_status()
                                st.success("✅ Success!")
                                with st.expander("Response"):
                                    st.json(test_response.json())
                            except Exception as e:
                                st.error(f"❌ Failed: {str(e)}")
            except Exception as e:
                st.error(f"❌ Failed to load examples: {str(e)}")
        
        # Custom URL testing
        st.subheader("🧪 Custom URL Test")
        test_url = st.text_input("Test custom API endpoint:", 
                                 placeholder=f"{api_base_url}/api/v1/products/search?query=dress")
        
        if st.button("🚀 Test URL") and test_url:
            try:
                response = requests.get(test_url, timeout=10)
                response.raise_for_status()
                st.success(f"✅ Success: {response.status_code}")
                
                with st.expander("Response Data"):
                    st.json(response.json())
            except Exception as e:
                st.error(f"❌ Failed: {str(e)}")


if __name__ == "__main__":
    main()