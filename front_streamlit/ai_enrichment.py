"""AI-powered product description enrichment module."""

import requests
import json
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any
import time
import config


class ProductEnricher:
    """Handles AI-powered product description enrichment using Ollama."""
    
    def __init__(self, base_url: str = None):
        """Initialize the enricher with Ollama configuration.
        
        Args:
            base_url: Ollama server URL (defaults to config)
        """
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL
        
    def is_ollama_available(self) -> bool:
        """Check if Ollama server is running and accessible.
        
        Returns:
            bool: True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models from Ollama.
        
        Returns:
            list: Available model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                return [model["name"] for model in models_data.get("models", [])]
        except requests.RequestException:
            pass
        return []
    
    def _create_enrichment_prompt(self, product_data: Dict[str, Any]) -> str:
        """Create a contextual prompt for product description enrichment.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            str: Formatted prompt for AI model
        """
        vendor = product_data.get('vendor', 'marque inconnue')
        product_type = product_data.get('product_type', 'produit')
        price = product_data.get('gross_amount_exc_tax_product', 0)
        tags = product_data.get('product_tags', '')
        
        prompt = f"""
        Tu es un expert en rédaction e-commerce pour des produits de mode premium.

        Contexte produit:
        - Marque: {vendor}
        - Type: {product_type}
        - Prix: {price}€ HT
        - Tags: {tags}

        Tâche: Rédige une description produit attractive et professionnelle en français pour ce {product_type} de la marque {vendor}.

        Contraintes:
        - 50-150 mots maximum
        - Ton persuasif et élégant
        - Intègre la marque :{vendor}
        - Pour le product_type : {product_type} ainsi que les tags :{tags}, traduis les en francais pour pouvoir les exploiter
        - Utilse le product_type : {product_type} ainsi que les tags :{tags} que si tu y trouves un sens
        - Intègre naturellement les mots-clés: {vendor}, {product_type} ainsi que les {tags}
        - Mets en valeur le positionnement premium si le prix le justifie
        - Tu reponds toujours en français

        Format de réponse: Description uniquement, sans préambule ni explication.

        Description:
        """
                
        return prompt
    
    def _create_improvement_prompt(self, description: str) -> str:
        """Create a prompt for improving an existing product description.
        
        Args:
            description: The current product description to improve
            
        Returns:
            str: Formatted prompt for AI model
        """
        prompt = f"""
        Tu es un expert en rédaction e-commerce pour des produits de mode premium.

        Tâche: Améliore cette description produit en éliminant les incohérences et en la rendant plus professionnelle.

        Description actuelle:
        {description}

        Consignes d'amélioration:
        - Supprime tous les numéros de référence ou codes qui n'apportent aucune valeur au client comme des X0P
        - Corrige les erreurs grammaticales et orthographiques
        - Améliore la fluidité et la lisibilité
        - Conserve le ton persuasif et élégant
        - Garde la même longueur approximative (50-150 mots)
        - Tu reponds toujours en français


        Format de réponse: Description améliorée uniquement, sans préambule ni explication.

        Description améliorée:
        """
        
        return prompt
    
    def _call_ollama_api(self, prompt: str) -> Optional[str]:
        """Make a call to Ollama API with the given prompt.
        
        Args:
            prompt: The prompt to send to the AI model
            
        Returns:
            Optional[str]: AI response or None if failed
        """
        if not self.is_ollama_available():
            st.error("Ollama n'est pas disponible. Vérifiez que le serveur est lancé.")
            return None
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "").strip()
                
                # Basic validation
                if len(ai_response) < 20:
                    return None
                
                return ai_response
            
        except requests.RequestException as e:
            st.error(f"Erreur lors de l'appel API: {str(e)}")
            return None
        
        return None
    
    def enrich_single_description(self, product_data: Dict[str, Any]) -> Optional[str]:
        """Enrich a single product description using AI.
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Optional[str]: Enriched description or None if failed
        """
        prompt = self._create_enrichment_prompt(product_data)
        enriched_description = self._call_ollama_api(prompt)
        
        return enriched_description
    
    def improve_description(self, description: str) -> Optional[str]:
        """Improve an existing product description by removing inconsistencies and enhancing quality.
        
        Args:
            description: The existing description to improve
            
        Returns:
            Optional[str]: Improved description or None if failed
        """
        if not description or len(description.strip()) < 10:
            return None
            
        prompt = self._create_improvement_prompt(description)
        improved_description = self._call_ollama_api(prompt)
        
        return improved_description
    
    def identify_missing_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify products with missing or empty descriptions.
        
        Args:
            df: Product dataframe
            
        Returns:
            pd.DataFrame: Filtered dataframe with products needing enrichment
        """
        missing_mask = (
            df['description'].isna() | 
            (df['description'].str.strip() == '') |
            (df['description'].str.len() < 10)  # Very short descriptions
        )
        
        return df[missing_mask].copy()
    
    def enrich_missing_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich all products with missing descriptions.
        
        Args:
            df: Product dataframe
            
        Returns:
            pd.DataFrame: Dataframe with enriched descriptions
        """
        # Create a copy to avoid modifying original
        enriched_df = df.copy()
        
        # Ajouter la colonne is_generated_description si elle n'existe pas
        if 'is_generated_description' not in enriched_df.columns:
            enriched_df['is_generated_description'] = False
        
        # Identify products needing enrichment
        products_to_enrich = self.identify_missing_descriptions(df)
        
        if products_to_enrich.empty:
            st.info("Aucun produit ne nécessite d'enrichissement")
            return enriched_df
        
        st.info(f"🤖 Enrichissement de {len(products_to_enrich)} descriptions en cours...")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        success_count = 0
        error_count = 0
        
        for idx, (row_idx, product) in enumerate(products_to_enrich.iterrows()):
            if idx == 3:
                break
            # Update progress
            progress = (idx + 1) / len(products_to_enrich)
            progress_bar.progress(progress)
            status_text.text(f"Traitement {idx + 1}/{len(products_to_enrich)}: {product['vendor']} - {product['product_type']}")
            
            # Enrich description
            product_data = product.to_dict()
            enriched_desc = self.enrich_single_description(product_data)
            
            # Improve the description to remove inconsistencies
            if enriched_desc:
                enriched_desc = self.improve_description(enriched_desc)
            
            if enriched_desc:
                enriched_df.at[row_idx, 'description'] = enriched_desc
                enriched_df.at[row_idx, 'is_generated_description'] = True
                success_count += 1
                
                # Show real-time result
                with results_container:
                    with st.expander(f"✅ {product['vendor']} - {product['product_type']}", expanded=False):
                        st.write(f"**Nouvelle description:**")
                        st.write(enriched_desc)
            else:
                error_count += 1
                st.warning(f"❌ Échec pour {product['vendor']} - {product['product_type']}")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        # Final status
        progress_bar.progress(1.0)
        status_text.text("✅ Enrichissement terminé!")
        
        st.success(f"Enrichissement terminé: {success_count} succès, {error_count} échecs")
        
        return enriched_df
    
    def get_enrichment_stats(self, original_df: pd.DataFrame, enriched_df: pd.DataFrame) -> Dict[str, int]:
        """Calculate enrichment statistics.
        
        Args:
            original_df: Original dataframe
            enriched_df: Enriched dataframe
            
        Returns:
            Dict[str, int]: Statistics about the enrichment process
        """
        original_missing = self.identify_missing_descriptions(original_df)
        final_missing = self.identify_missing_descriptions(enriched_df)
        
        return {
            "total_products": len(original_df),
            "originally_missing": len(original_missing),
            "still_missing": len(final_missing),
            "enriched_count": len(original_missing) - len(final_missing),
            "enrichment_rate": round(((len(original_missing) - len(final_missing)) / len(original_missing)) * 100, 1) if len(original_missing) > 0 else 0
        }
    

if __name__ == "__main__":
    # Test de la fonction enrich_single_description
    product_data = {
        'product_id': 7228338536544,
        'product_type': 'Long Sleeved Top',
        'product_tags': 'FRAME, Long Sleeved Top, YOOX1024',
        'images_array': '[https://cdn.shopify.com/s/files/1/0002/7600/4882/files/49755158TH_2.jpg?v=1729250973]',
        'vendor': 'FRAME',
        'inventory_quantity': 20000,
        'gross_amount_exc_tax_product': 0.0,
        'description': float('nan')
    }
    
    # Initialiser l'enrichisseur
    enricher = ProductEnricher()
    
    # Tester la fonction
    result = enricher.enrich_single_description(product_data)
    
    if result:
        pass  # Test successful
    else:
        pass  # Test failed