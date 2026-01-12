"""Database utilities for Streamlit - CSV loading and data management."""

import pandas as pd
import streamlit as st
import json
import ast
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, create_tables
from database.models import Product


def to_list(value):
    """Convert various formats to a proper Python list for JSON field."""
    if pd.isna(value):
        return None
    # Si c'est déjà une liste (parfois Pandas peut garder des objets)
    if isinstance(value, list):
        return value

    s = str(value).strip()

    # Cas 1: JSON valide (prioritaire) - ex: '["url1", "url2"]'
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Cas 2: format python-like - ex: "['url1','url2']"
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass

    # Cas 3: format sans guillemets - ex: [url1,url2,...]
    if s.startswith('[') and s.endswith(']'):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [u.strip() for u in inner.split(',') if u.strip()]

    # Cas 4: une seule URL
    return [s]


def load_csv_to_database(csv_path: str) -> tuple[bool, str]:
    """Load CSV data into PostgreSQL database.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Create tables if they don't exist
        create_tables()
        
        # Create database session using get_db()
        db_generator = get_db()
        db = next(db_generator)
        
        try:
            # Clear existing products (optional - comment out to append)
            db.query(Product).delete()
            
            # Convert DataFrame to Product records avec système de batches
            BATCH_SIZE = 20  # Limite pour éviter "too many parameters"
            products = []
            products_added = 0
            total_products = len(df)
            
            for idx, (_, row) in enumerate(df.iterrows()):
                product = Product(
                    product_id=int(row['product_id']) if pd.notna(row['product_id']) else None,
                    product_type=str(row['product_type']) if pd.notna(row['product_type']) else None,
                    product_tags=str(row['product_tags']) if pd.notna(row['product_tags']) else None,
                    images_array=to_list(row['images_array']),
                    vendor=str(row['vendor']) if pd.notna(row['vendor']) else None,
                    inventory_quantity=int(row['inventory_quantity']) if pd.notna(row['inventory_quantity']) else None,
                    gross_amount_exc_tax_product=float(row['gross_amount_exc_tax_product']) if pd.notna(row['gross_amount_exc_tax_product']) else None,
                    description=str(row['description']).strip() if pd.notna(row['description']) else None,
                    is_generated_description=bool(row.get('is_generated_description', False)) if 'is_generated_description' in row else False
                )
                products.append(product)
                products_added += 1
                
                # Commit par batch pour éviter "too many parameters"
                if len(products) >= BATCH_SIZE:
                    db.bulk_save_objects(products)
                    db.commit()
                    products.clear()
                    print(f"✅ Batch {idx//BATCH_SIZE + 1}: {products_added}/{total_products} produits traités")
            
            # Commit le dernier batch s'il reste des produits
            if products:
                db.bulk_save_objects(products)
                db.commit()
                print(f"✅ Final batch: {products_added}/{total_products} produits traités")
            
            return True, f"✅ Successfully loaded {products_added} products into database"
            
        except Exception as e:
            db.rollback()
            return False, f"❌ Database error: {str(e)}"
        finally:
            db.close()
            
    except Exception as e:
        return False, f"❌ CSV loading error: {str(e)}"


def get_database_stats() -> dict:
    """Get database statistics.
    
    Returns:
        dict: Database statistics
    """
    try:
        db_generator = get_db()
        db = next(db_generator)
        try:
            total_products = db.query(Product).count()
            vendors_count = db.query(Product.vendor).distinct().count()
            types_count = db.query(Product.product_type).distinct().count()
            with_description = db.query(Product).filter(
                Product.description.isnot(None),
                Product.description != ''
            ).count()
            generated_descriptions = db.query(Product).filter(
                Product.is_generated_description == True
            ).count()
            
            return {
                "total_products": total_products,
                "vendors_count": vendors_count,
                "types_count": types_count,
                "with_description": with_description,
                "without_description": total_products - with_description,
                "generated_descriptions": generated_descriptions
            }
        finally:
            db.close()
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return {
            "total_products": 0,
            "vendors_count": 0,
            "types_count": 0,
            "with_description": 0,
            "without_description": 0,
            "generated_descriptions": 0
        }


def check_database_connection() -> bool:
    """Check if database connection is working.
    
    Returns:
        bool: True if connection is successful
    """
    try:
        db_generator = get_db()
        db = next(db_generator)
        try:
            # Simple query to test connection
            db.execute(text("SELECT 1"))
            return True
        finally:
            db.close()
    except Exception:
        return False