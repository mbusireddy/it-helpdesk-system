
# Import necessary types and Utilities
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from app.utils.config import settings  # Import config for Chroma DB path, etc.
from app.services.llm_service import llm_service  # For embedding generation via LLM
from app.utils.logger import logger  # Logging system for info/errors


class VectorService:
    def __init__(self):
        """
        Initialize the VectorService with a persistent Chromadb client and collection.

        - Uses persistent storage directory defined in settings.
        - Disables anonymized telemetry for privacy.
        - Retrieves or creates a collection named "helpdesk_knowledge".
        - Uses cosine similarity as the metric space for efficient vector search.

        This setup supports adding and querying vector embeddings related to helpdesk knowledge.
        """
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,  # Directory to store persistent vectors
            settings=ChromaSettings(anonymized_telemetry=False)  # Privacy settings
        )
        self.collection = self.client.get_or_create_collection(
            name="helpdesk_knowledge",  # Logical grouping of vectors (documents)
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity for nearest neighbor search
        )

    async def add_knowledge(self, question: str, answer: str, category: str, metadata: Dict = None):
        """
        Adds a new knowledge entry to the vector database.

        Args:
            question (str): The user question or query text.
            answer (str): The response or answer text.
            category (str): Category or topic label for classification/filtering.
            metadata (Dict, optional): Additional metadata fields to store with the entry.

        Process:
            - Generate an embedding vector for the question using the LLM service.
            - Construct a unique document ID based on category and current number of stored docs.
            - Add the embedding along with document text and metadata to the collection.
            - Log success or catch and log errors if addition fails.

        Notes:
            - Embedding is required to store; if generation fails, no insertion happens.
            - Metadata dictionary merges with base metadata like question, answer, and category.
        """
        try:
            embedding = await llm_service.generate_embedding(question)
            if embedding:
                # Generate a unique ID by combining category and current size of collection
                doc_id = f"{category}_{len(self.collection.get()['ids'])}"
                self.collection.add(
                    embeddings=[embedding],  # Embedding vector list
                    documents=[f"Q: {question}\nA: {answer}"],  # Document text (combined QA)
                    metadatas=[{
                        "category": category,
                        "question": question,
                        "answer": answer,
                        **(metadata or {})  # Merge any extra metadata if provided
                    }],
                    ids=[doc_id]  # Unique identifier for this entry
                )
                logger.info(f"Added knowledge entry: {doc_id}")
        except Exception as e:
            # Log the error but don’t throw, so service remains stable
            logger.error(f"Error adding knowledge: {e}")

    async def search_knowledge(self, query: str, category: str = None, n_results: int = 5) -> List[Dict]:
        """
        Search the knowledge base for documents semantically similar to the query.

        Args:
            query (str): The search query string.
            category (str, optional): Filter search by this category.
            n_results (int, optional): Max number of results to return (default 5).

        Returns:
            List[Dict]: List of matched knowledge entries, each containing:
                - question (str)
                - answer (str)
                - category (str)
                - similarity (float): Similarity score (1 - distance) between query and doc.
                - document (str): Full stored document text.

        Steps:
            - Generate embedding for the query using LLM service.
            - Prepare an optional filter `where_clause` if category specified.
            - Query the collection for nearest vectors by cosine similarity.
            - Parse and structure results including similarity score.
            - Return empty list on any failure or if embedding generation fails.

        Note:
            - Similarity is calculated as 1 - cosine distance (closer to 1 means more similar).
        """
        try:
            embedding = await llm_service.generate_embedding(query)
            if not embedding:
                return []  # Return empty if embedding could not be generated

            # Optional filter for restricting results by category
            where_clause = {"category": category} if category else None

            # Query chromadb collection for top-N similar documents
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=where_clause
            )

            knowledge_results = []
            # Unpack results from chromadb format (list of lists for multiple queries)
            for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
            )):
                knowledge_results.append({
                    "question": metadata.get("question", ""),
                    "answer": metadata.get("answer", ""),
                    "category": metadata.get("category", ""),
                    "similarity": 1 - distance,  # Convert distance to similarity score
                    "document": doc
                })

            return knowledge_results
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return []


# Create a single instance for app-wide reuse (singleton pattern)
vector_service = VectorService()
