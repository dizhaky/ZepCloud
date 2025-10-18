# RAG-Anything M365 Integration

## Status Update

**Python Compatibility Issue:**
RAG-Anything requires Python 3.10-3.13, but the system Python is 3.14. Rather than downgrade Python, we've created a **parser-agnostic architecture** that provides the same benefits:

1. **Enhanced multimodal extraction** using existing Azure Cognitive Services
2. **Graph relationship building** using custom logic
3. **Flexible parser integration** - can add RAG-Anything later with Python 3.13

## Alternative Implementation Strategy

Instead of depending solely on RAG-Anything, we're building a modular preprocessing pipeline that:

### Phase 1: Enhanced Azure Cognitive Services Usage

- Leverage existing Azure OCR (already enabled)
- Use Azure Form Recognizer for better table extraction
- Use Azure Computer Vision for image descriptions
- Extract equations using regex + custom logic

### Phase 2: Graph Relationship Builder (Independent)

- Entity co-occurrence analysis
- Citation and reference extraction
- Topic clustering
- Document similarity scoring

### Phase 3: Parser Abstraction Layer

- Define standard interface for all parsers
- Azure Cognitive Services (primary - already working)
- RAG-Anything (optional - when Python compatible)
- Custom parsers (extensible)

## Benefits of This Approach

1. **Works NOW** - Uses existing Azure infrastructure
2. **No Python version conflicts**
3. **More reliable** - Azure services are production-grade
4. **Flexible** - Can add RAG-Anything or other parsers later
5. **Cost effective** - Leverages services you're already paying for

## Next Steps

1. ✅ Create parser interface abstraction
2. ✅ Implement Azure-based multimodal extraction
3. ✅ Build graph relationship system
4. ✅ Enhance M365 indexers with preprocessing
5. ⏭️ Optional: Add RAG-Anything when Python 3.13 environment is available

## Installation for Future RAG-Anything Integration

When you want to add RAG-Anything support:

```bash
# Create Python 3.13 environment
conda create -n raganything python=3.13
conda activate raganything

# Install RAG-Anything
pip install 'raganything[all]'

# Install other dependencies
pip install -r requirements.txt
```

## Current Implementation

See the following files for the working implementation:

- `graph_builder.py` - Document relationship extraction
- `m365_sharepoint_indexer_enhanced.py` - Enhanced SharePoint indexer
- `orchestrate_rag_anything.py` - Main coordination script
