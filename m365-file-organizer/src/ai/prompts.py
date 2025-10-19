from __future__ import annotations

ANALYZE_FILE_PROMPT = '''
Analyze this document and provide:
1. Document type (invoice, contract, report, email, presentation, other)
2. Suggested filename (max 50 chars, descriptive, no special chars except _ and -)
3. Suggested folder path (logical categorization)
4. Extracted entities:
   - dates (ISO format)
   - monetary amounts
   - company/organization names
   - people names
   - any other relevant entities
5. 3-5 relevant tags
6. Brief summary (2-3 sentences)

Document metadata:
- Current name: {current_name}
- File type: {mime_type}
- Size: {size}
- Created: {created_date}

Document content preview (first 5000 chars):
{content}

Return response as JSON:
{
  "doc_type": "string",
  "suggested_name": "string",
  "suggested_path": "string",
  "entities": {
    "dates": [],
    "amounts": [],
    "companies": [],
    "people": [],
    "custom": {}
  },
  "tags": [],
  "summary": "string",
  "confidence": 0.0
}
'''

EXTRACT_EMBEDDING_PROMPT = '''
Generate a semantic summary of this document for vector search.
Focus on: topic, purpose, key entities, and context.
Keep it concise but comprehensive (2-3 paragraphs max).

{content}
'''
