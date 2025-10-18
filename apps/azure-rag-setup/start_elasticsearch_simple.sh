#!/bin/bash
# Simple Elasticsearch startup script

echo "🚀 Starting Elasticsearch for RAG-Anything + OlmoCR System"
echo "============================================================"

# Kill any existing Elasticsearch processes
pkill -f elasticsearch 2>/dev/null || true

# Navigate to Elasticsearch directory
cd elasticsearch-8.11.0

# Clean up previous data
rm -rf data/* logs/* 2>/dev/null || true

# Start Elasticsearch with proper configuration
echo "Starting Elasticsearch with single-node configuration..."
./bin/elasticsearch -E discovery.type=single-node -E xpack.security.enabled=false -E network.host=0.0.0.0 -E http.port=9200 &

# Wait for Elasticsearch to start
echo "Waiting for Elasticsearch to start..."
sleep 20

# Test connection
echo "Testing Elasticsearch connection..."
if curl -s http://localhost:9200 > /dev/null; then
    echo "✅ Elasticsearch is running!"
    echo "Cluster info:"
    curl -s http://localhost:9200 | jq . 2>/dev/null || curl -s http://localhost:9200
else
    echo "❌ Elasticsearch failed to start"
    echo "Check logs: tail -f elasticsearch-8.11.0/logs/elasticsearch.log"
fi

echo "============================================================"
echo "Elasticsearch startup complete!"
