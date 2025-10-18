"""
Test script for Elasticsearch + RAG-Anything + OlmoCR integration
"""
import requests
import json
import time
from datetime import datetime
from config_elasticsearch import Config

def test_elasticsearch_connection():
    """Test Elasticsearch connection"""
    print("🔍 Testing Elasticsearch connection...")
    try:
        response = requests.get(
            f"{Config.ELASTIC_HOST}/_cluster/health",
            auth=(Config.ELASTIC_USERNAME, Config.ELASTIC_PASSWORD),
            timeout=10
        )
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Elasticsearch connected - Status: {health['status']}")
            return True
        else:
            print(f"❌ Elasticsearch connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Elasticsearch connection error: {e}")
        return False

def test_tika_connection():
    """Test Apache Tika connection"""
    print("🔍 Testing Apache Tika connection...")
    try:
        response = requests.get(f"{Config.TIKA_HOST}/tika", timeout=10)
        if response.status_code == 200:
            print("✅ Apache Tika connected")
            return True
        else:
            print(f"❌ Apache Tika connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Apache Tika connection error: {e}")
        return False

def test_api_server():
    """Test API server endpoints"""
    print("🔍 Testing API server...")
    base_url = "http://localhost:5000"

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API server healthy - Documents: {health.get('total_documents', 0)}")
            return True
        else:
            print(f"❌ API server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API server connection error: {e}")
        return False

def test_search_functionality():
    """Test search functionality"""
    print("🔍 Testing search functionality...")
    base_url = "http://localhost:5000"

    try:
        # Test simple search
        search_data = {
            "query": "test document",
            "size": 5
        }

        response = requests.post(
            f"{base_url}/search",
            json=search_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search working - Found {result.get('total', 0)} results")
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Search test error: {e}")
        return False

def test_enhanced_features():
    """Test RAG-Anything enhanced features"""
    print("🔍 Testing enhanced features...")
    base_url = "http://localhost:5000"

    try:
        # Test enhanced documents endpoint
        response = requests.get(f"{base_url}/enhanced", timeout=10)

        if response.status_code == 200:
            result = response.json()
            enhanced_count = result.get('total', 0)
            print(f"✅ Enhanced features working - {enhanced_count} enhanced documents")
            return True
        else:
            print(f"❌ Enhanced features test failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Enhanced features test error: {e}")
        return False

def test_multimodal_search():
    """Test multimodal search functionality"""
    print("🔍 Testing multimodal search...")
    base_url = "http://localhost:5000"

    try:
        search_data = {
            "query": "table data",
            "content_types": ["tables", "charts"],
            "size": 5
        }

        response = requests.post(
            f"{base_url}/search/multimodal",
            json=search_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Multimodal search working - Found {result.get('total', 0)} results")
            return True
        else:
            print(f"❌ Multimodal search failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Multimodal search test error: {e}")
        return False

def test_entity_search():
    """Test entity-based search"""
    print("🔍 Testing entity search...")
    base_url = "http://localhost:5000"

    try:
        search_data = {
            "entity_value": "test",
            "size": 5
        }

        response = requests.post(
            f"{base_url}/search/entity",
            json=search_data,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Entity search working - Found {result.get('total', 0)} results")
            return True
        else:
            print(f"❌ Entity search failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Entity search test error: {e}")
        return False

def test_stats_endpoint():
    """Test statistics endpoint"""
    print("🔍 Testing statistics endpoint...")
    base_url = "http://localhost:5000"

    try:
        response = requests.get(f"{base_url}/stats", timeout=10)

        if response.status_code == 200:
            result = response.json()
            stats = result.get('stats', {})
            print(f"✅ Statistics working - Total docs: {stats.get('total_documents', 0)}")
            print(f"   Enhanced docs: {stats.get('enhanced_documents', 0)}")
            print(f"   Enhancement rate: {stats.get('enhancement_rate', '0%')}")
            return True
        else:
            print(f"❌ Statistics test failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Statistics test error: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive integration test"""
    print("="*60)
    print("🧪 Elasticsearch + RAG-Anything + OlmoCR Integration Test")
    print("="*60)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    tests = [
        ("Elasticsearch Connection", test_elasticsearch_connection),
        ("Apache Tika Connection", test_tika_connection),
        ("API Server Health", test_api_server),
        ("Search Functionality", test_search_functionality),
        ("Enhanced Features", test_enhanced_features),
        ("Multimodal Search", test_multimodal_search),
        ("Entity Search", test_entity_search),
        ("Statistics Endpoint", test_stats_endpoint)
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            results[test_name] = False

        time.sleep(1)  # Brief pause between tests

    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed! Integration is working correctly.")
        print("\nNext steps:")
        print("1. Start the API server: python api_server.py")
        print("2. Configure TypingMind with the new Elasticsearch API")
        print("3. Test with real M365 data: python m365_sync_elasticsearch.py")
    else:
        print(f"\n⚠️ {total-passed} tests failed. Please check the issues above.")
        print("\nTroubleshooting:")
        print("1. Ensure Elasticsearch is running: docker-compose up -d")
        print("2. Check API server is running: python api_server.py")
        print("3. Verify configuration in env.elasticsearch")

    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
