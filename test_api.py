"""Test script for the FastAPI endpoints."""

import requests
import json
import time
from typing import Optional


class APITester:
    """Test class for API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def test_connection(self) -> bool:
        """Test if API server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test root endpoint."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def test_stats_endpoint(self) -> Optional[dict]:
        """Test stats endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException:
            return None
    
    def test_search_endpoint(self, query: str = None) -> Optional[dict]:
        """Test search endpoint."""
        try:
            params = {}
            if query:
                params['query'] = query
            
            response = requests.get(
                f"{self.base_url}/api/v1/products/search",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException:
            return None
    
    def test_vendors_endpoint(self) -> Optional[dict]:
        """Test vendors endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/vendors", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException:
            return None
    
    def test_product_types_endpoint(self) -> Optional[dict]:
        """Test product types endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/product-types", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException:
            return None
    
    def run_all_tests(self) -> dict:
        """Run all tests and return results."""
        print("🧪 Testing FastAPI endpoints...")
        print("=" * 50)
        
        results = {}
        
        # Test connection
        print("1. Testing API connection...")
        results['connection'] = self.test_connection()
        if results['connection']:
            print("   ✅ API server is running")
        else:
            print("   ❌ API server not accessible")
            print("   💡 Run: uvicorn api.main:app --reload --port 8000")
            return results
        
        # Test root endpoint
        print("2. Testing root endpoint...")
        results['root'] = self.test_root_endpoint()
        if results['root']:
            print("   ✅ Root endpoint working")
        else:
            print("   ❌ Root endpoint failed")
        
        # Test stats
        print("3. Testing stats endpoint...")
        stats = self.test_stats_endpoint()
        results['stats'] = stats is not None
        if stats:
            print(f"   ✅ Stats: {stats['total_products']} products, {stats['total_vendors']} vendors")
        else:
            print("   ❌ Stats endpoint failed (database might not be populated)")
        
        # Test search
        print("4. Testing search endpoint...")
        search_results = self.test_search_endpoint()
        results['search'] = search_results is not None
        if search_results:
            total = search_results['page_info']['total_count']
            returned = len(search_results['products'])
            print(f"   ✅ Search: {returned} products returned out of {total} total")
        else:
            print("   ❌ Search endpoint failed")
        
        # Test search with query
        print("5. Testing search with query...")
        search_query = self.test_search_endpoint("dress")
        results['search_query'] = search_query is not None
        if search_query:
            total = search_query['page_info']['total_count']
            returned = len(search_query['products'])
            print(f"   ✅ Search 'dress': {returned} products returned out of {total} matches")
        else:
            print("   ❌ Search with query failed")
        
        # Test vendors
        print("6. Testing vendors endpoint...")
        vendors = self.test_vendors_endpoint()
        results['vendors'] = vendors is not None
        if vendors:
            print(f"   ✅ Vendors: {len(vendors)} vendors found")
        else:
            print("   ❌ Vendors endpoint failed")
        
        # Test product types
        print("7. Testing product types endpoint...")
        types = self.test_product_types_endpoint()
        results['product_types'] = types is not None
        if types:
            print(f"   ✅ Product types: {len(types)} types found")
        else:
            print("   ❌ Product types endpoint failed")
        
        print("=" * 50)
        
        # Summary
        passed = sum(1 for v in results.values() if v)
        total_tests = len(results)
        print(f"📊 Test Results: {passed}/{total_tests} tests passed")
        
        if passed == total_tests:
            print("🎉 All tests passed! API is ready to use.")
        elif results['connection']:
            print("⚠️  Some tests failed. Check database connection and data loading.")
        else:
            print("❌ API server not running. Start with: uvicorn api.main:app --reload --port 8000")
        
        return results


def main():
    """Main test function."""
    tester = APITester()
    results = tester.run_all_tests()
    
    # Instructions
    print("\n📝 Next steps:")
    if not results['connection']:
        print("1. Start the API server:")
        print("   cd /path/to/project")
        print("   uvicorn api.main:app --reload --port 8000")
    elif not results.get('stats', False):
        print("1. Load data into PostgreSQL:")
        print("   - Use Streamlit app: 'Base de données' section")
        print("   - Click 'Charger en base' to load CSV data")
    else:
        print("1. API is ready! Access documentation at:")
        print("   http://localhost:8000/docs")
        print("2. Try example searches:")
        print("   http://localhost:8000/api/v1/products/search?query=dress")
        print("   http://localhost:8000/api/v1/vendors")


if __name__ == "__main__":
    main()