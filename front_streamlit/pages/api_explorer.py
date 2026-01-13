"""API Explorer page for testing FastAPI endpoints."""

import streamlit as st
import requests
import json

from config import API_BASE_URL


def display_api_explorer_page():
    """Display API Explorer interface."""
    st.header("🔍 API Explorer")
    st.write(f"Interrogez l'API FastAPI sur {API_BASE_URL} pour tester les endpoints.")
    
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
        _display_product_search_tab(api_base_url)
    
    with tab2:
        _display_enriched_products_tab(api_base_url)
    
    with tab3:
        _display_api_examples_tab(api_base_url)


def _display_product_search_tab(api_base_url: str):
    """Display the product search tab."""
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
                    _display_product_card(product)
            else:
                st.info("No products found")
                
        except Exception as e:
            st.error(f"❌ Search failed: {str(e)}")


def _display_enriched_products_tab(api_base_url: str):
    """Display the enriched products tab."""
    st.subheader("🤖 Enriched Products with Photos")
    st.write("⭐ Test de la nouvelle route `/api/v1/products/bonus`")
    
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
            _display_enrichment_stats(enrichment_stats)
            
            st.success(f"✅ Found {page_info.get('total_count', 0)} enriched products")
            
            # Display enriched products
            if products:
                for product in products:
                    _display_enriched_product_card(product)
            else:
                st.info("No enriched products found")
                st.info("💡 Run AI enrichment first in the 'Enrichissement IA' tab")
                
        except Exception as e:
            st.error(f"❌ Enriched products failed: {str(e)}")


def _display_api_examples_tab(api_base_url: str):
    """Display the API examples tab."""
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


def _display_product_card(product: dict):
    """Display a product card for search results."""
    with st.container():
        col_prod1, col_prod2 = st.columns([1, 3])
        
        with col_prod1:
            # Try to display image
            images = product.get("images_array")
            if images:
                try:
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


def _display_enriched_product_card(product: dict):
    """Display an enriched product card with photos and descriptions."""
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


def _display_enrichment_stats(enrichment_stats: dict):
    """Display enrichment statistics."""
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