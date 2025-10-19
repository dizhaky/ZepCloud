"""
Load Testing for M365 RAG System
Run with: locust -f locustfile.py --host http://localhost:8000
"""

from locust import HttpUser, task, between  # type: ignore
import random

# Sample queries for realistic testing
SAMPLE_QUERIES = [
    "quarterly financial report",
    "employee handbook policies",
    "project timeline",
    "meeting notes from last week",
    "technical documentation",
    "marketing strategy",
    "sales presentation",
    "budget planning",
    "team collaboration",
    "product roadmap",
    "customer feedback",
    "training materials",
    "performance metrics",
    "security guidelines",
    "onboarding process"
]


class RAGSystemUser(HttpUser):
    """Simulated user for M365 RAG system"""

    # Wait between 1-3 seconds between tasks
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a simulated user starts"""
        # Check system health on start
        self.client.get("/health")

    @task(10)
    def search_documents(self):
        """
        Primary task: Search for documents
        Weight: 10 (most common operation)
        """
        query = random.choice(SAMPLE_QUERIES)

        payload = {
            "query": query,
            "top_k": random.choice([5, 10, 20]),
            "search_mode": random.choice(["hybrid", "vector", "text"]),
            "include_images": random.choice([True, False]),
            "use_kg": random.choice([True, False])
        }

        with self.client.post(
            "/search",
            json=payload,
            catch_response=True,
            name="/search"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("total", 0) > 0:
                    response.success()
                else:
                    response.failure("No results returned")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def health_check(self):
        """
        Health check endpoint
        Weight: 2 (occasional health checks)
        """
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    status = data.get('status')
                    response.failure(f"System unhealthy: {status}")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def search_with_filters(self):
        """
        Advanced search with filters
        Weight: 1 (less common)
        """
        query = random.choice(SAMPLE_QUERIES)

        payload = {
            "query": query,
            "top_k": 10,
            "search_mode": "hybrid",
            "filters": {
                "source": random.choice(["sharepoint", "onedrive", "teams"])
            }
        }

        with self.client.post(
            "/search",
            json=payload,
            catch_response=True,
            name="/search (filtered)"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class PowerUser(HttpUser):
    """Simulated power user with heavier load"""

    wait_time = between(0.5, 1.5)

    @task(20)
    def rapid_search(self):
        """Rapid consecutive searches"""
        for _ in range(3):
            query = random.choice(SAMPLE_QUERIES)
            self.client.post(
                "/search",
                json={"query": query, "top_k": 10},
                name="/search (rapid)"
            )

    @task(5)
    def check_system_status(self):
        """Frequent system checks"""
        self.client.get("/health", name="/health (power user)")


class DataScienceUser(HttpUser):
    """Simulated data science user with analytical queries"""

    wait_time = between(2, 5)

    @task
    def complex_analytical_query(self):
        """Complex queries with knowledge graph"""
        queries = [
            "analyze sales trends over last quarter",
            "compare project performance metrics",
            "identify key stakeholders in project X",
            "summarize customer feedback patterns"
        ]

        payload = {
            "query": random.choice(queries),
            "top_k": 20,
            "search_mode": "hybrid",
            "use_kg": True,
            "include_images": True,
            "include_tables": True
        }

        self.client.post(
            "/search",
            json=payload,
            name="/search (analytical)"
        )
