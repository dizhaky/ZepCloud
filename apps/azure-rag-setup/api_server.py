"""
REST API server for TypingMind integration with Elasticsearch and RAG-Anything
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from query_interface import M365SearchInterface
from config_elasticsearch import Config
import logging

logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

search = M365SearchInterface()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        stats = search.get_index_stats()
        return jsonify({
            "status": "healthy",
            "elasticsearch": "connected",
            "total_documents": stats['total_documents'],
            "enhanced_documents": stats['enhanced_documents'],
            "enhancement_rate": f"{stats['enhancement_rate']:.1f}%",
            "total_relationships": stats['total_relationships']
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/search', methods=['POST'])
def search_endpoint():
    """Main search endpoint for TypingMind"""
    try:
        data = request.json
        query = data.get('query', '')
        size = data.get('size', 5)

        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Perform search
        results = search.simple_search(query, size)

        # Format for TypingMind
        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r['title'],
                "content": r['snippet'],
                "url": r['url'],
                "source": r['source_type'],
                "site": r.get('site_name', ''),
                "date": r['modified_date'],
                "score": r['score'],
                "enhanced": r.get('raganything_processed', False),
                "entities": r.get('entities', []),
                "topics": r.get('topics', [])
            })

        return jsonify({
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results)
        })

    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/search/advanced', methods=['POST'])
def advanced_search_endpoint():
    """Advanced search with filters"""
    try:
        data = request.json
        query = data.get('query', '')
        filters = data.get('filters', {})
        size = data.get('size', 5)

        if not query:
            return jsonify({"error": "Query is required"}), 400

        results = search.advanced_search(query, filters, size)

        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r['title'],
                "content": r['snippet'],
                "url": r['url'],
                "source": r['source_type'],
                "site": r.get('site_name', ''),
                "date": r['modified_date'],
                "created_by": r.get('created_by', ''),
                "score": r['score'],
                "enhanced": r.get('raganything_processed', False),
                "entities": r.get('entities', []),
                "topics": r.get('topics', []),
                "complexity_score": r.get('complexity_score', 0)
            })

        return jsonify({
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results)
        })

    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/search/multimodal', methods=['POST'])
def multimodal_search_endpoint():
    """Multimodal search for tables, equations, images, charts"""
    try:
        data = request.json
        query = data.get('query', '')
        content_types = data.get('content_types', ['tables', 'equations', 'images', 'charts'])
        size = data.get('size', 5)

        if not query:
            return jsonify({"error": "Query is required"}), 400

        results = search.multimodal_search(query, content_types, size)

        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r['title'],
                "content": r['snippet'],
                "url": r['url'],
                "source": r['source_type'],
                "score": r['score'],
                "enhanced": r.get('raganything_processed', False)
            })

        return jsonify({
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results),
            "content_types_searched": content_types
        })

    except Exception as e:
        logger.error(f"Multimodal search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/search/entity', methods=['POST'])
def entity_search_endpoint():
    """Search for documents containing specific entities"""
    try:
        data = request.json
        entity_value = data.get('entity_value', '')
        entity_type = data.get('entity_type', None)
        size = data.get('size', 5)

        if not entity_value:
            return jsonify({"error": "Entity value is required"}), 400

        results = search.entity_search(entity_value, entity_type, size)

        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r['title'],
                "content": r['snippet'],
                "url": r['url'],
                "source": r['source_type'],
                "score": r['score'],
                "enhanced": r.get('raganything_processed', False)
            })

        return jsonify({
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results),
            "entity_searched": entity_value,
            "entity_type": entity_type
        })

    except Exception as e:
        logger.error(f"Entity search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/search/relationships/<doc_id>', methods=['GET'])
def relationship_search_endpoint(doc_id):
    """Find documents related to a specific document"""
    try:
        size = request.args.get('size', 10, type=int)

        results = search.relationship_search(doc_id, size=size)

        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r['title'],
                "content": r['snippet'],
                "url": r['url'],
                "source": r['source_type'],
                "score": r['score'],
                "enhanced": r.get('raganything_processed', False)
            })

        return jsonify({
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results),
            "source_doc_id": doc_id
        })

    except Exception as e:
        logger.error(f"Relationship search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def stats_endpoint():
    """Get index statistics"""
    try:
        stats = search.get_index_stats()
        by_source = search.aggregate_by_source()
        by_site = search.aggregate_by_site()
        by_entity_type = search.aggregate_by_entity_type()

        return jsonify({
            "success": True,
            "stats": {
                "total_documents": stats['total_documents'],
                "enhanced_documents": stats['enhanced_documents'],
                "enhancement_rate": f"{stats['enhancement_rate']:.1f}%",
                "total_relationships": stats['total_relationships'],
                "total_size_mb": stats['total_size_mb'],
                "by_source": by_source,
                "top_sites": by_site[:10],
                "entity_types": by_entity_type
            }
        })

    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/recent', methods=['GET'])
def recent_documents_endpoint():
    """Get recent documents"""
    try:
        days = request.args.get('days', 7, type=int)
        size = request.args.get('size', 20, type=int)

        results = search.get_recent_documents(days, size)

        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r['title'],
                "content": r['snippet'],
                "url": r['url'],
                "source": r['source_type'],
                "date": r['modified_date'],
                "created_by": r.get('created_by', ''),
                "enhanced": r.get('raganything_processed', False)
            })

        return jsonify({
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results),
            "days": days
        })

    except Exception as e:
        logger.error(f"Recent documents error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/enhanced', methods=['GET'])
def enhanced_documents_endpoint():
    """Get documents with RAG-Anything enhancements"""
    try:
        size = request.args.get('size', 20, type=int)

        results = search.get_enhanced_documents(size)

        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r['title'],
                "content": r['snippet'],
                "url": r['url'],
                "source": r['source_type'],
                "complexity_score": r.get('complexity_score', 0),
                "entities": r.get('entities', []),
                "topics": r.get('topics', []),
                "enhanced": r.get('raganything_processed', False)
            })

        return jsonify({
            "success": True,
            "results": formatted_results,
            "total": len(formatted_results)
        })

    except Exception as e:
        logger.error(f"Enhanced documents error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/context', methods=['GET'])
def context_endpoint():
    """Get user context (for TypingMind integration)"""
    try:
        # This would integrate with ZepCloud or other context systems
        # For now, return basic context
        return jsonify({
            "success": True,
            "context": {
                "user": "current_user",
                "session": "elasticsearch_session",
                "enhancements_enabled": True,
                "rag_anything_active": True,
                "olmocr_active": True
            }
        })

    except Exception as e:
        logger.error(f"Context error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/store', methods=['POST'])
def store_endpoint():
    """Store new information (for ZepCloud integration)"""
    try:
        data = request.json
        content = data.get('content', '')
        metadata = data.get('metadata', {})

        # This would integrate with ZepCloud or other storage systems
        # For now, just acknowledge receipt
        return jsonify({
            "success": True,
            "message": "Information stored successfully",
            "content_length": len(content),
            "metadata": metadata
        })

    except Exception as e:
        logger.error(f"Store error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("="*60)
    print("M365 Elasticsearch API Server with RAG-Anything")
    print("="*60)
    print(f"Elasticsearch: {Config.ELASTIC_HOST}")
    print(f"Index: {Config.ELASTIC_INDEX}")
    print("="*60)
    print("\nStarting server...")
    print("API will be available at http://localhost:5001")
    print("\nEndpoints:")
    print("  GET  /health              - Health check")
    print("  POST /search              - Simple search")
    print("  POST /search/advanced     - Advanced search with filters")
    print("  POST /search/multimodal   - Multimodal content search")
    print("  POST /search/entity       - Entity-based search")
    print("  GET  /search/relationships/<doc_id> - Document relationships")
    print("  GET  /stats               - Index statistics")
    print("  GET  /recent              - Recent documents")
    print("  GET  /enhanced            - Enhanced documents")
    print("  GET  /context             - User context")
    print("  POST /store                - Store information")
    print("="*60)

    app.run(host='0.0.0.0', port=5001, debug=True)
