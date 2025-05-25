import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from app.utils.config import settings
from app.services.llm_service import llm_service
from app.utils.logger import logger


class VectorService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="helpdesk_knowledge",
            metadata={"hnsw:space": "cosine"}
        )

    async def add_knowledge(self, question: str, answer: str, category: str, metadata: Dict = None):
        try:
            embedding = await llm_service.generate_embedding(question)
            if embedding:
                doc_id = f"{category}_{len(self.collection.get()['ids'])}"
                self.collection.add(
                    embeddings=[embedding],
                    documents=[f"Q: {question}\nA: {answer}"],
                    metadatas=[{
                        "category": category,
                        "question": question,
                        "answer": answer,
                        **(metadata or {})
                    }],
                    ids=[doc_id]
                )
                logger.info(f"Added knowledge entry: {doc_id}")
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")

    async def search_knowledge(self, query: str, category: str = None, n_results: int = 5) -> List[Dict]:
        try:
            embedding = await llm_service.generate_embedding(query)
            if not embedding:
                return []

            where_clause = {"category": category} if category else None

            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=where_clause
            )

            knowledge_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
            )):
                knowledge_results.append({
                    "question": metadata.get("question", ""),
                    "answer": metadata.get("answer", ""),
                    "category": metadata.get("category", ""),
                    "similarity": 1 - distance,
                    "document": doc
                })

            return knowledge_results
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return []


vector_service = VectorService()
