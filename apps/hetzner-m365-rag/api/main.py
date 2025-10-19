# api/main.py
# Custom API Layer - Integrating RAG-Anything + Elasticsearch + RAGFlow
# M365 RAG System on Hetzner

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import os
import asyncio
import hashlib

# RAG-Anything imports
try:
    from raganything import RAGAnything  # type: ignore
    RAG_ANYTHING_AVAILABLE = True
except ImportError:
    RAG_ANYTHING_AVAILABLE = False
    logging.warning("RAG-Anything not available, limited functionality")


# ============================================
# RAG ENGINE STUB (for when RAG-Anything unavailable)
# ============================================
class RAGEngineUnavailable:
    """
    Stub class that raises explicit errors when RAG-Anything is not available.
    This prevents confusing AttributeError exceptions and provides clear feedback.
    """

    def __init__(self):
        self._error_message = (
            "RAG-Anything is not available. "
            "Install it with: pip install raganything[all]"
        )

    def __getattr__(self, name: str):
        """Raise clear error for any method/attribute access"""
        raise RuntimeError(
            f"Cannot use RAG-Anything method '{name}': {self._error_message}"
        )

    def __bool__(self):
        """Allow truthiness checks to work correctly"""
        return False

# Elasticsearch imports
from elasticsearch import AsyncElasticsearch  # type: ignore
from elasticsearch.helpers import async_bulk  # type: ignore

# Database and cache
import asyncpg  # type: ignore
import redis.asyncio as redis

# Utilities
import json
import uuid


# ============================================
# LOGGING CONFIGURATION
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# CONFIGURATION
# ============================================
class Settings:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Elasticsearch
    ES_HOST = os.getenv("ES_HOST", "elasticsearch")
    ES_PORT = int(os.getenv("ES_PORT", 9200))
    ES_USER = os.getenv("ES_USER", "elastic")
    ES_PASSWORD = os.getenv("ES_PASSWORD", "changeme")
    ES_USE_SSL = os.getenv("ES_USE_SSL", "true").lower() == "true"
    ES_VERIFY_CERTS = os.getenv("ES_VERIFY_CERTS", "false").lower() == "true"

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

    # MinIO
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Azure AD
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")

    # Security
    JWT_SECRET = os.getenv("JWT_SECRET")

    # RAG Configuration
    EMBEDDING_MODEL = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS = 1536
    LLM_MODEL = "gpt-4o-mini"
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50


settings = Settings()


# ============================================
# GLOBAL CLIENTS
# ============================================
es_client: Optional[AsyncElasticsearch] = None
pg_pool: Optional[asyncpg.Pool] = None  # type: ignore
redis_client: Optional[redis.Redis] = None
# rag_engine is always initialized in lifespan - either RAGAnything or RAGEngineUnavailable stub
rag_engine: Union[Any, "RAGEngineUnavailable"]  # type: ignore


# ============================================
# PYDANTIC MODELS
# ============================================
class SearchQuery(BaseModel):
    query: str = Field(..., description="Natural language search query")
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Metadata filters"
    )
    top_k: int = Field(10, ge=1, le=100, description="Number of results")
    include_images: bool = Field(True, description="Include image results")
    include_tables: bool = Field(True, description="Include table results")
    use_kg: bool = Field(True, description="Use knowledge graph enhancement")
    search_mode: str = Field("hybrid", pattern="^(vector|text|hybrid)$")


class SearchResult(BaseModel):
    doc_id: str
    title: str
    content: str
    score: float
    metadata: Dict[str, Any]
    highlights: Optional[List[str]] = None
    images: Optional[List[Dict[str, Any]]] = None
    tables: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[str]] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    took_ms: int
    kg_entities: Optional[List[str]] = None


class DocumentUpload(BaseModel):
    file_name: str
    source: str = "upload"
    metadata: Optional[Dict[str, Any]] = None


class IngestionJob(BaseModel):
    job_id: str
    status: str
    progress: float
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class M365SyncRequest(BaseModel):
    source_type: str = Field(
        ..., pattern="^(sharepoint|onedrive|teams|outlook)$"
    )
    site_url: Optional[str] = None
    folder_path: Optional[str] = None
    delta_sync: bool = True


# ============================================
# LIFESPAN MANAGEMENT
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global es_client, pg_pool, redis_client, rag_engine

    logger.info("🚀 Starting M365 RAG API...")

    # Initialize Elasticsearch with SSL support
    es_scheme = "https" if settings.ES_USE_SSL else "http"
    es_client = AsyncElasticsearch(
        hosts=[f"{es_scheme}://{settings.ES_HOST}:{settings.ES_PORT}"],
        basic_auth=(settings.ES_USER, settings.ES_PASSWORD),
        verify_certs=settings.ES_VERIFY_CERTS,
        ssl_show_warn=False  # Suppress SSL warnings for self-signed certs
    )
    await ensure_indices()
    logger.info(f"✅ Elasticsearch connected ({es_scheme.upper()})")

    # Initialize PostgreSQL
    if not settings.DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Please set it in your .env file or environment."
        )
    pg_pool = await asyncpg.create_pool(settings.DATABASE_URL)  # type: ignore
    logger.info("✅ PostgreSQL connected")

    # Initialize Redis
    redis_client = redis.from_url(settings.REDIS_URL)
    if redis_client:
        await redis_client.ping()
    logger.info("✅ Redis connected")

    # Initialize RAG-Anything (real or stub)
    if RAG_ANYTHING_AVAILABLE:
        rag_engine = RAGAnything(
            llm_model=settings.LLM_MODEL,
            embedding_model=settings.EMBEDDING_MODEL,
            vector_store="custom",  # We'll use our ES integration
            kg_enabled=True,
            multimodal=True,
            parsers=["mineru", "docling"]
        )
        logger.info("✅ RAG-Anything initialized")
    else:
        # Use stub that raises explicit errors if accessed
        rag_engine = RAGEngineUnavailable()
        logger.warning(
            "⚠️  RAG-Anything not available - using stub. "
            "Document processing will be limited."
        )

    yield

    # Cleanup
    logger.info("🔌 Shutting down...")
    if es_client:
        await es_client.close()
    if pg_pool:
        await pg_pool.close()
    if redis_client:
        await redis_client.close()
    logger.info("👋 Shutdown complete")


# ============================================
# FASTAPI APPLICATION
# ============================================
app = FastAPI(
    title="M365 RAG API",
    description="Multimodal RAG System for Microsoft 365 Documents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# ELASTICSEARCH INDEX MANAGEMENT
# ============================================
async def ensure_indices():
    """Create Elasticsearch indices if they don't exist"""

    # Documents index
    documents_mapping = {
        "mappings": {
            "properties": {
                "doc_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "standard"},
                "content": {"type": "text", "analyzer": "standard"},
                "content_vector": {
                    "type": "dense_vector",
                    "dims": settings.EMBEDDING_DIMENSIONS,
                    "index": True,
                    "similarity": "cosine"
                },
                "metadata": {
                    "properties": {
                        "source": {"type": "keyword"},
                        "author": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "modified_at": {"type": "date"},
                        "file_type": {"type": "keyword"},
                        "file_size": {"type": "long"},
                        "m365_id": {"type": "keyword"},
                        "path": {"type": "keyword"}
                    }
                },
                "entities": {"type": "keyword"},
                "has_images": {"type": "boolean"},
                "has_tables": {"type": "boolean"},
                "indexed_at": {"type": "date"}
            }
        },
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "standard": {
                        "type": "standard"
                    }
                }
            }
        }
    }

    if es_client and not await es_client.indices.exists(index="documents"):
        await es_client.indices.create(
            index="documents", body=documents_mapping
        )
        logger.info("Created 'documents' index")

    # Images index
    images_mapping = {
        "mappings": {
            "properties": {
                "image_id": {"type": "keyword"},
                "doc_id": {"type": "keyword"},
                "image_vector": {
                    "type": "dense_vector",
                    "dims": 512,  # CLIP embeddings
                    "index": True,
                    "similarity": "cosine"
                },
                "ocr_text": {"type": "text"},
                "caption": {"type": "text"},
                "image_url": {"type": "keyword"},
                "page_number": {"type": "integer"}
            }
        }
    }

    if es_client and not await es_client.indices.exists(index="images"):
        await es_client.indices.create(index="images", body=images_mapping)
        logger.info("Created 'images' index")

    # Knowledge graph index
    kg_mapping = {
        "mappings": {
            "properties": {
                "entity_id": {"type": "keyword"},
                "entity_text": {"type": "text"},
                "entity_type": {"type": "keyword"},
                "doc_ids": {"type": "keyword"},
                "relationships": {
                    "type": "nested",
                    "properties": {
                        "target_entity": {"type": "keyword"},
                        "relation_type": {"type": "keyword"},
                        "weight": {"type": "float"}
                    }
                }
            }
        }
    }

    if es_client and not await es_client.indices.exists(
        index="knowledge_graph"
    ):
        await es_client.indices.create(
            index="knowledge_graph", body=kg_mapping
        )
        logger.info("Created 'knowledge_graph' index")


# ============================================
# HEALTH CHECK
# ============================================
@app.get("/health")
async def health_check():
    """System health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "rag_anything": RAG_ANYTHING_AVAILABLE
    }

    # Check Elasticsearch
    try:
        if es_client:
            await es_client.cluster.health()
        health_status["services"]["elasticsearch"] = "ok"
    except Exception as e:
        health_status["services"]["elasticsearch"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check PostgreSQL
    try:
        if pg_pool:
            async with pg_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
        health_status["services"]["postgres"] = "ok"
    except Exception as e:
        health_status["services"]["postgres"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        if redis_client:
            await redis_client.ping()
        health_status["services"]["redis"] = "ok"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


# ============================================
# SEARCH ENDPOINTS
# ============================================
@app.post("/search", response_model=SearchResponse)
async def search_documents(query: SearchQuery):
    """
    Search documents using hybrid retrieval
    Combines vector search, BM25, and knowledge graph
    """
    start_time = datetime.utcnow()

    try:
        # Check cache (use stable hash for cache key)
        query_hash = hashlib.md5(query.query.encode()).hexdigest()
        cache_key = f"search:{query_hash}:{query.search_mode}"
        if redis_client:
            cached = await redis_client.get(cache_key)
            if cached:
                try:
                    logger.info(f"Cache hit for query: {query.query}")
                    # Decode bytes and reconstruct SearchResponse model
                    cached_dict = json.loads(cached.decode('utf-8'))
                    return SearchResponse(**cached_dict)
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    # Cache data is invalid/corrupt, log and continue with fresh search
                    logger.warning(f"Invalid cache data: {e}, performing fresh search")
                    await redis_client.delete(cache_key)

        # Generate query embedding (placeholder - implement with OpenAI)
        # query_vector = await generate_embedding(query.query)

        # Build Elasticsearch query
        es_query = {
            "query": {
                "multi_match": {
                    "query": query.query,
                    "fields": ["title^2", "content"],
                    "type": "best_fields"
                }
            },
            "size": query.top_k,
            "highlight": {
                "fields": {
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                }
            }
        }

        # Execute search
        if not es_client:
            raise HTTPException(
                status_code=503, detail="Elasticsearch not available"
            )

        response = await es_client.search(
            index="documents",
            body=es_query
        )

        # Process results
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            result = SearchResult(
                doc_id=source["doc_id"],
                title=source["title"],
                content=source["content"][:500],  # Truncate for display
                score=hit["_score"],
                metadata=source["metadata"],
                highlights=hit.get("highlight", {}).get("content", [])
            )
            results.append(result)

        # Build response
        duration = (datetime.utcnow() - start_time).total_seconds()
        took_ms = int(duration * 1000)
        search_response = SearchResponse(
            query=query.query,
            results=results,
            total=response["hits"]["total"]["value"],
            took_ms=took_ms
        )

        # Cache results
        if redis_client:
            await redis_client.setex(
                cache_key,
                300,  # 5 minutes
                json.dumps(search_response.dict())
            )

        return search_response

    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# DOCUMENT INGESTION
# ============================================
@app.post("/ingest/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    metadata: Optional[str] = None
):
    """Upload and process a document"""
    job_id = str(uuid.uuid4())

    try:
        # Save file temporarily
        file_path = f"/tmp/{job_id}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse metadata
        doc_metadata = json.loads(metadata) if metadata else {}
        doc_metadata["file_name"] = file.filename
        doc_metadata["file_size"] = len(content)

        # Schedule background processing
        background_tasks.add_task(
            process_document,
            file_path=file_path,
            doc_id=job_id,
            metadata=doc_metadata
        )

        return {
            "job_id": job_id,
            "status": "processing",
            "message": f"Document {file.filename} is being processed"
        }

    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def process_document(
    file_path: str, doc_id: str, metadata: Dict
):
    """
    Process document with RAG-Anything
    
    Note: rag_engine is always initialized in lifespan():
    - If RAG-Anything is available: real RAGAnything instance
    - If RAG-Anything is unavailable: RAGEngineUnavailable stub that raises clear errors
    
    This function checks RAG_ANYTHING_AVAILABLE before using rag_engine to avoid
    triggering the stub's error messages. If this check is bypassed, the stub will
    raise RuntimeError with installation instructions.
    """
    try:
        logger.info(f"Processing document: {file_path}")

        if not RAG_ANYTHING_AVAILABLE:
            msg = "RAG-Anything not available, skipping processing"
            logger.warning(msg)
            return

        # Parse document with RAG-Anything
        # RAG-Anything API is synchronous, run in thread pool to avoid blocking
        parsed_doc = await asyncio.to_thread(
            rag_engine.parse_document,
            file_path
        )

        # Extract text chunks (also synchronous)
        chunks = await asyncio.to_thread(
            parsed_doc.get_chunks,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        # Index to Elasticsearch (simplified - add embedding generation)
        actions = []
        for i, chunk in enumerate(chunks):
            action = {
                "_index": "documents",
                "_id": f"{doc_id}_{i}",
                "_source": {
                    "doc_id": doc_id,
                    "title": metadata.get("file_name", "Untitled"),
                    "content": chunk.text,
                    "metadata": metadata,
                    "has_images": False,  # Update based on parsed_doc
                    "has_tables": False,  # Update based on parsed_doc
                    "indexed_at": datetime.utcnow().isoformat()
                }
            }
            actions.append(action)

        if es_client:
            await async_bulk(es_client, actions)
        logger.info(f"✅ Document processed: {doc_id}")

    except Exception as e:
        msg = f"Processing error for {doc_id}: {str(e)}"
        logger.error(msg, exc_info=True)
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)


# ============================================
# M365 INTEGRATION
# ============================================
@app.post("/ingest/m365/sync")
async def sync_m365(
    sync_request: M365SyncRequest,
    background_tasks: BackgroundTasks
):
    """Sync documents from Microsoft 365"""
    job_id = str(uuid.uuid4())

    # This will be implemented with the migrated M365 indexers
    return {
        "job_id": job_id,
        "status": "not_implemented",
        "message": "M365 sync will be implemented in Phase 4"
    }


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
