# Elasticsearch + RAG-Anything + OlmoCR Setup Guide

## Overview

This guide will help you set up the complete Elasticsearch-based RAG system with RAG-Anything and OlmoCR integration,
  replacing Azure AI Search with significant cost savings.

## Cost Savings

- **Previous (Azure AI Search):** $599-$1,213/month
- **New (Elasticsearch):** $0-120/month
- **Annual Savings:** $6,348-$15,156

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ installed
- Microsoft 365 tenant with admin access
- 1Password CLI (for secure credential management)

## Quick Start

### 1. Start Elasticsearch Infrastructure

```bash

# Start Elasticsearch, Kibana, and Tika

docker-compose up -d

# Wait for services to be ready (60 seconds)

sleep 60

# Verify Elasticsearch is running

curl -u elastic:YourStrongPassword123! http://localhost:9200

```

### 2. Install Dependencies

```bash

# Install Python dependencies

pip install -r requirements-elasticsearch.txt

# Install OlmoCR (optional, for advanced PDF processing)

git clone https://github.com/allenai/olmocr.git
cd olmocr
pip install -e .
pip install "sglang[all]==0.4.2"
cd ..

```

### 3. Configure Environment

```bash

# Copy and edit environment file

cp env.elasticsearch .env

# Edit with your Azure credentials

nano .env

```

Required environment variables:

```bash

# Azure AD Configuration (from 1Password)

AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here

# Elasticsearch Configuration

ELASTIC_HOST=http://localhost:9200
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=YourStrongPassword123!
ELASTIC_INDEX=m365-documents

```

### 4. Create Elasticsearch Index

```bash

# Create index with RAG-Anything enhanced mappings

python elasticsearch_setup.py

```

### 5. Test the System

```bash

# Run comprehensive integration test

python test_elasticsearch_integration.py

```

### 6. Start API Server

```bash

# Start the REST API server

python api_server.py

```

The API will be available at `http://localhost:5000`

### 7. Sync M365 Data

```bash

# Start syncing your M365 data

python m365_sync_elasticsearch.py

```

### 8. Configure TypingMind

Update your TypingMind configuration to use the new Elasticsearch API:

```json

{
  "name": "M365 Elasticsearch with RAG-Anything",
  "endpoints": {
    "base_url": "http://localhost:5000",
    "search": "/search",
    "health": "/health"
  }
}

```

## Features

### RAG-Anything Enhancements

- **Multimodal Content Detection:** Tables, equations, images, charts
- **Entity Extraction:** People, organizations, locations, emails
- **Relationship Building:** Document connections and co-occurrence
- **Topic Clustering:** Automatic topic identification
- **Complexity Analysis:** Document complexity scoring
- **Sentiment Analysis:** Content sentiment detection

### OlmoCR Integration

- **Advanced PDF Processing:** Structure-preserving text extraction
- **Image OCR:** High-quality image text extraction
- **Table Extraction:** Structured table data
- **Equation Recognition:** LaTeX equation extraction

### Elasticsearch Features

- **Full-Text Search:** Fuzzy matching and relevance scoring
- **Advanced Filtering:** By source, date, file type, entities
- **Aggregations:** Statistics and analytics
- **Relationship Queries:** Document relationship search
- **Multimodal Search:** Search across tables, images, charts

## API Endpoints

### Core Search

- `POST /search` - Simple full-text search
- `POST /search/advanced` - Advanced search with filters
- `POST /search/multimodal` - Multimodal content search
- `POST /search/entity` - Entity-based search

### Enhanced Features

- `GET /search/relationships/<doc_id>` - Document relationships
- `GET /enhanced` - RAG-Anything enhanced documents
- `GET /recent` - Recent documents
- `GET /stats` - Index statistics

### System

- `GET /health` - Health check
- `GET /context` - User context
- `POST /store` - Store information

## Example API Usage

### Simple Search

```bash

curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "quarterly report", "size": 5}'

```

### Advanced Search

```bash

curl -X POST http://localhost:5000/search/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "query": "budget planning",
    "filters": {
      "source_type": "sharepoint",
      "date_from": "2024-01-01"
    },
    "size": 10
  }'

```

### Multimodal Search

```bash

curl -X POST http://localhost:5000/search/multimodal \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sales data",
    "content_types": ["tables", "charts"],
    "size": 5
  }'

```

### Entity Search

```bash

curl -X POST http://localhost:5000/search/entity \
  -H "Content-Type: application/json" \
  -d '{
    "entity_value": "Dan Izhaky",
    "entity_type": "person",
    "size": 5
  }'

```

## Monitoring

### Kibana Dashboard

Access Kibana at `http://localhost:5601` to:

- View document distribution
- Create visualizations
- Monitor indexing progress
- Debug issues

### Health Monitoring

```bash

# Check system health

curl http://localhost:5000/health

# Get detailed statistics

curl http://localhost:5000/stats

```

### Logs

```bash

# View sync logs

tail -f m365_sync.log

# View Elasticsearch logs

docker-compose logs elasticsearch

```

## Troubleshooting

### Elasticsearch Issues

```bash

# Check Elasticsearch status

curl -u elastic:password http://localhost:9200/_cluster/health

# Check index status

curl -u elastic:password http://localhost:9200/m365-documents/_stats

```

### API Server Issues

```bash

# Check if API server is running

curl http://localhost:5000/health

# Check API server logs

python api_server.py

```

### M365 Authentication Issues

```bash

# Test M365 authentication

python -c "from utils.graph_client import GraphClientWrapper; GraphClientWrapper()"

```

### OlmoCR Issues

```bash

# Test OlmoCR installation

python -c "import olmocr; print('OlmoCR installed successfully')"

```

## Performance Optimization

### Elasticsearch Tuning

```yaml

# In docker-compose.yml, adjust memory

environment:

  - "ES_JAVA_OPTS=-Xms8g -Xmx8g" # Increase for larger datasets

```

### Batch Processing

```bash

# Adjust batch size in env.elasticsearch

BATCH_SIZE=200  # Increase for faster processing

```

### Date Filtering

```bash

# Enable date filtering to reduce storage

DATE_FILTER_ENABLED=true
DATE_FILTER_FROM=2023-01-01

```

## Migration from Azure

### 1. Keep Azure Running

Don't stop your existing Azure setup until migration is complete.

### 2. Test Elasticsearch Setup

Run the comprehensive test to ensure everything works.

### 3. Sync Data Gradually

Start with a small subset of data to test the pipeline.

### 4. Update TypingMind Configuration

Point TypingMind to the new Elasticsearch API.

### 5. Monitor Performance

Compare search results and performance with Azure.

### 6. Switch Over

Once satisfied, update TypingMind to use Elasticsearch exclusively.

## Maintenance

### Daily Operations

```bash

# Check system health (2)

curl http://localhost:5000/health

# Monitor sync status

tail -f m365_sync.log

```

### Weekly Sync

```bash

# Full M365 sync

python m365_sync_elasticsearch.py

```

### Backup

```bash

# Backup Elasticsearch data

docker exec m365-elasticsearch elasticsearch-snapshot --repo backup --snapshot daily

```

## Support

### Documentation

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [RAG-Anything GitHub](https://github.com/HKUDS/RAG-Anything)
- [OlmoCR GitHub](https://github.com/allenai/olmocr)
- [TypingMind Integration](https://docs.typingmind.com/)

### Common Issues

1. **Elasticsearch won't start:** Check memory allocation in docker-compose.yml
2. **Authentication fails:** Verify Azure credentials in .env
3. **API server errors:** Check Elasticsearch connectivity
4. **Slow indexing:** Adjust batch size and memory settings

## Success Metrics

- [ ] Elasticsearch cluster running with <100ms query response
- [ ] All M365 sources indexing successfully (>95% success rate)
- [ ] OlmoCR processing PDFs with structure preservation
- [ ] RAG-Anything building relationship graphs
- [ ] TypingMind searching Elasticsearch successfully
- [ ] Cost reduced by >80%
- [ ] Query quality maintained or improved

---

**🎉 Congratulations! You now have a cost-effective, feature-rich RAG system with advanced multimodal processing
  capabilities.**
