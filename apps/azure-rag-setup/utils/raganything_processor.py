"""
RAG-Anything processor for multimodal content detection and relationship extraction
"""
import json
import logging
from typing import Dict, List, Any, Optional
from config_elasticsearch import Config

logger = logging.getLogger(__name__)

class RAGAnythingProcessor:
    """Process documents with RAG-Anything for multimodal content and relationships"""

    def __init__(self):
        self.enabled = Config.RAG_ANYTHING_ENABLED
        self.graph_enabled = Config.RAG_ANYTHING_GRAPH_ENABLED
        self.processed_docs = 0
        self.entities_extracted = 0
        self.relationships_created = 0

    def process_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process document with RAG-Anything for multimodal content and relationships

        Args:
            document: Document dictionary with content and metadata

        Returns:
            Enhanced document with RAG-Anything features
        """
        if not self.enabled:
            return document

        try:
            # Extract entities from content
            entities = self._extract_entities(document.get("content", ""))

            # Extract key phrases and topics
            key_phrases = self._extract_key_phrases(document.get("content", ""))
            topics = self._extract_topics(document.get("content", ""))

            # Analyze document complexity
            complexity_score = self._analyze_complexity(document.get("content", ""))

            # Detect language and sentiment
            language = self._detect_language(document.get("content", ""))
            sentiment = self._analyze_sentiment(document.get("content", ""))

            # Build relationships if graph is enabled
            relationships = []
            if self.graph_enabled:
                relationships = self._extract_relationships(document, entities)

            # Enhance document with RAG-Anything features
            enhanced_document = document.copy()
            enhanced_document.update({
                "entities": entities,
                "key_phrases": key_phrases,
                "topics": topics,
                "complexity_score": complexity_score,
                "language": language,
                "sentiment": sentiment,
                "relationships": relationships,
                "raganything_processed": True
            })

            # Update statistics
            self.processed_docs += 1
            self.entities_extracted += len(entities)
            self.relationships_created += len(relationships)

            return enhanced_document

        except Exception as e:
            logger.error(f"RAG-Anything processing failed: {e}")
            return document

    def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities from document content"""
        # Simulate entity extraction
        # In real implementation, this would use NER models or APIs

        entities = []

        # Simple keyword-based entity extraction
        keywords = ["project", "budget", "meeting", "report", "analysis", "strategy"]

        for i, keyword in enumerate(keywords):
            if keyword.lower() in content.lower():
                entities.append({
                    "type": "keyword",
                    "value": keyword,
                    "confidence": 0.8,
                    "position": content.lower().find(keyword.lower()),
                    "context": self._get_context(content, keyword)
                })

        return entities

    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content"""
        # Simulate key phrase extraction
        # In real implementation, this would use NLP libraries like spaCy or transformers

        phrases = []
        words = content.split()

        # Simple bigram extraction
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            if len(phrase) > 10 and phrase not in phrases:
                phrases.append(phrase)

        return phrases[:10]  # Return top 10 phrases

    def _extract_topics(self, content: str) -> List[str]:
        """Extract topics from content"""
        # Simulate topic extraction
        # In real implementation, this would use topic modeling or classification

        topics = []

        # Simple topic detection based on keywords
        topic_keywords = {
            "business": ["strategy", "revenue", "profit", "market"],
            "technology": ["software", "system", "digital", "platform"],
            "finance": ["budget", "cost", "investment", "financial"],
            "project": ["plan", "timeline", "milestone", "deliverable"]
        }

        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                topics.append(topic)

        return topics

    def _analyze_complexity(self, content: str) -> float:
        """Analyze document complexity score"""
        # Simple complexity analysis based on content length and vocabulary

        words = content.split()
        sentences = content.split('.')

        # Basic complexity metrics
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
        unique_words = len(set(word.lower() for word in words))
        vocabulary_richness = unique_words / len(words) if words else 0

        # Combine metrics into complexity score (0-1)
        complexity = min(1.0, (avg_words_per_sentence / 20) + (vocabulary_richness * 2))

        return round(complexity, 3)

    def _detect_language(self, content: str) -> str:
        """Detect document language"""
        # Simple language detection
        # In real implementation, this would use langdetect or similar

        # Basic English detection
        english_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
        content_lower = content.lower()

        english_count = sum(1 for word in english_words if word in content_lower)

        if english_count > 5:
            return "en"
        else:
            return "unknown"

    def _analyze_sentiment(self, content: str) -> str:
        """Analyze document sentiment"""
        # Simple sentiment analysis
        # In real implementation, this would use VADER, TextBlob, or transformers

        positive_words = ["good", "great", "excellent", "positive", "success", "improve"]
        negative_words = ["bad", "poor", "negative", "problem", "issue", "fail"]

        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_relationships(self, document: Dict[str, Any], entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []

        # Simple relationship extraction
        # In real implementation, this would use more sophisticated NLP

        entity_values = [entity["value"] for entity in entities]

        for i, entity1 in enumerate(entity_values):
            for j, entity2 in enumerate(entity_values[i+1:], i+1):
                # Check if entities appear together in content
                if self._entities_co_occur(document.get("content", ""), entity1, entity2):
                    relationships.append({
                        "source_entity": entity1,
                        "target_entity": entity2,
                        "relationship_type": "co_occurrence",
                        "confidence": 0.7,
                        "context": f"Entities {entity1} and {entity2} appear together"
                    })

        return relationships

    def _entities_co_occur(self, content: str, entity1: str, entity2: str) -> bool:
        """Check if two entities co-occur in content"""
        content_lower = content.lower()
        return entity1.lower() in content_lower and entity2.lower() in content_lower

    def _get_context(self, content: str, keyword: str, window: int = 50) -> str:
        """Get context around a keyword"""
        content_lower = content.lower()
        keyword_lower = keyword.lower()

        pos = content_lower.find(keyword_lower)
        if pos == -1:
            return ""

        start = max(0, pos - window)
        end = min(len(content), pos + len(keyword) + window)

        return content[start:end].strip()

    def find_document_relationships(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find relationships between documents"""
        relationships = []

        for i, doc1 in enumerate(documents):
            for j, doc2 in enumerate(documents[i+1:], i+1):
                # Calculate similarity based on shared entities and topics
                similarity = self._calculate_document_similarity(doc1, doc2)

                if similarity > 0.3:  # Threshold for relationship
                    relationships.append({
                        "source_doc_id": doc1.get("id"),
                        "target_doc_id": doc2.get("id"),
                        "relationship_type": "similarity",
                        "strength": similarity,
                        "shared_entities": self._get_shared_entities(doc1, doc2),
                        "shared_topics": self._get_shared_topics(doc1, doc2)
                    })

        return relationships

    def _calculate_document_similarity(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> float:
        """Calculate similarity between two documents"""
        # Simple similarity calculation
        # In real implementation, this would use more sophisticated methods

        entities1 = set(entity["value"] for entity in doc1.get("entities", []))
        entities2 = set(entity["value"] for entity in doc2.get("entities", []))

        topics1 = set(doc1.get("topics", []))
        topics2 = set(doc2.get("topics", []))

        # Jaccard similarity for entities
        entity_similarity = len(entities1 & entities2) / len(entities1 | entities2) if entities1 | entities2 else 0

        # Jaccard similarity for topics
        topic_similarity = len(topics1 & topics2) / len(topics1 | topics2) if topics1 | topics2 else 0

        # Combined similarity
        return (entity_similarity + topic_similarity) / 2

    def _get_shared_entities(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> List[str]:
        """Get shared entities between documents"""
        entities1 = set(entity["value"] for entity in doc1.get("entities", []))
        entities2 = set(entity["value"] for entity in doc2.get("entities", []))
        return list(entities1 & entities2)

    def _get_shared_topics(self, doc1: Dict[str, Any], doc2: Dict[str, Any]) -> List[str]:
        """Get shared topics between documents"""
        topics1 = set(doc1.get("topics", []))
        topics2 = set(doc2.get("topics", []))
        return list(topics1 & topics2)

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get RAG-Anything processing statistics"""
        return {
            "enabled": self.enabled,
            "graph_enabled": self.graph_enabled,
            "processed_docs": self.processed_docs,
            "entities_extracted": self.entities_extracted,
            "relationships_created": self.relationships_created,
            "avg_entities_per_doc": self.entities_extracted / self.processed_docs if self.processed_docs > 0 else 0,
            "avg_relationships_per_doc": self.relationships_created / self.processed_docs if self.processed_docs > 0 else 0
        }
