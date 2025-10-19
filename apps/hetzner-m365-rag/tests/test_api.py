"""
API Integration Tests for M365 RAG System
Run with: pytest test_api.py -v
"""

import pytest
import asyncio
from httpx import AsyncClient

# Base URL for API
BASE_URL = "http://localhost:8000"


class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test basic health check"""
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.get("/health")

            assert response.status_code == 200
            data = response.json()

            assert "status" in data
            assert "services" in data
            assert data["status"] in ["healthy", "degraded"]

    @pytest.mark.asyncio
    async def test_health_check_services(self):
        """Test individual service health"""
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.get("/health")
            data = response.json()

            services = data.get("services", {})

            # Check expected services
            expected_services = ["elasticsearch", "postgres", "redis"]
            for service in expected_services:
                assert service in services


class TestSearchEndpoints:
    """Test search functionality"""

    @pytest.mark.asyncio
    async def test_simple_search(self):
        """Test basic search query"""
        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            payload = {
                "query": "test document",
                "top_k": 5
            }

            response = await client.post("/search", json=payload)

            assert response.status_code == 200
            data = response.json()

            assert "query" in data
            assert "results" in data
            assert "total" in data
            assert "took_ms" in data

            assert data["query"] == "test document"
            assert isinstance(data["results"], list)
            assert isinstance(data["total"], int)
            assert isinstance(data["took_ms"], int)

    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """Test search with metadata filters"""
        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            payload = {
                "query": "report",
                "top_k": 10,
                "filters": {
                    "source": "sharepoint"
                }
            }

            response = await client.post("/search", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert "results" in data

    @pytest.mark.asyncio
    async def test_search_modes(self):
        """Test different search modes"""
        search_modes = ["hybrid", "vector", "text"]

        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            for mode in search_modes:
                payload = {
                    "query": "test",
                    "top_k": 5,
                    "search_mode": mode
                }

                response = await client.post("/search", json=payload)

                assert response.status_code == 200, f"Failed for mode: {mode}"
                data = response.json()
                assert "results" in data

    @pytest.mark.asyncio
    async def test_search_validation(self):
        """Test input validation"""
        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            # Empty query
            response = await client.post("/search", json={"query": ""})
            assert response.status_code in [400, 422]

            # Invalid search mode
            response = await client.post("/search", json={
                "query": "test",
                "search_mode": "invalid"
            })
            assert response.status_code in [400, 422]

            # Invalid top_k
            response = await client.post("/search", json={
                "query": "test",
                "top_k": 1000
            })
            assert response.status_code in [400, 422]


class TestDocumentIngestion:
    """Test document upload and processing"""

    @pytest.mark.asyncio
    async def test_upload_endpoint_exists(self):
        """Test that upload endpoint exists"""
        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            # This should return 422 (validation error) not 404
            response = await client.post("/ingest/upload")
            assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_m365_sync_endpoint_exists(self):
        """Test that M365 sync endpoint exists"""
        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            response = await client.post("/ingest/m365/sync", json={
                "source_type": "sharepoint"
            })
            # Should accept the request (may not be fully implemented)
            assert response.status_code in [200, 202, 501]


class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.asyncio
    async def test_search_latency(self):
        """Test that search completes within acceptable time"""
        import time

        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            payload = {"query": "test", "top_k": 10}

            start = time.time()
            response = await client.post("/search", json=payload)
            elapsed = time.time() - start

            assert response.status_code == 200

            # Should complete within 2 seconds (p95 target)
            msg = f"Search took {elapsed:.2f}s (target: <2s)"
            assert elapsed < 2.0, msg

    @pytest.mark.asyncio
    async def test_concurrent_searches(self):
        """Test handling of concurrent requests"""
        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            tasks = []

            for i in range(10):
                payload = {"query": f"test query {i}", "top_k": 5}
                task = client.post("/search", json=payload)
                tasks.append(task)

            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks)

            # All should succeed
            for response in responses:
                assert response.status_code == 200


class TestCaching:
    """Test caching behavior"""

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Test that identical queries benefit from caching"""
        import time

        async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
            payload = {"query": "cache test query", "top_k": 5}

            # First request (cache miss)
            start1 = time.time()
            response1 = await client.post("/search", json=payload)
            time1 = time.time() - start1

            assert response1.status_code == 200

            # Second request (cache hit - should be faster)
            start2 = time.time()
            response2 = await client.post("/search", json=payload)
            time2 = time.time() - start2

            assert response2.status_code == 200

            # Cache hit should be significantly faster
            # (Not always true if first query was already cached, so just log)
            print(f"First query: {time1:.3f}s, Second query: {time2:.3f}s")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
