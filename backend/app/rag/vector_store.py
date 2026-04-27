"""Vector store using ChromaDB."""
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from app.rag.schemas import RAGChunk, RAGStatus


class VectorStore:
    """ChromaDB-based vector store."""

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str = "ai_readiness_knowledge",
    ):
        self.persist_dir = persist_dir or os.getenv(
            "CHROMA_PERSIST_DIR",
            str(Path(__file__).parent.parent.parent.parent / "data" / "chroma"),
        )
        self.collection_name = collection_name
        self._client: Any = None
        self._collection: Any = None

    def _get_client(self):
        """Lazy init ChromaDB client."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            # Ensure directory exists
            Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False),
            )
        return self._client

    def get_collection(self):
        """Get or create collection."""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add_chunks(
        self,
        chunks: list[RAGChunk],
        embeddings: list[list[float]],
    ) -> int:
        """Add chunks with embeddings to the collection."""
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have same length")

        collection = self.get_collection()

        ids = [chunk.chunk_id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "doc_id": chunk.doc_id,
                "source_file": chunk.source_file,
                "source_type": chunk.source_type,
                "title": chunk.title,
                "industry": chunk.industry or "",
                "canvas_tags": ",".join(chunk.canvas_tags),
                "pain_points": ",".join(chunk.pain_points),
                "ai_scenarios": ",".join(chunk.ai_scenarios),
            }
            for chunk in chunks
        ]

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_type: str | None = None,
    ) -> list[tuple[RAGChunk, float]]:
        """Search for similar chunks."""
        collection = self.get_collection()

        where_filter = None
        if filter_type:
            where_filter = {"source_type": filter_type}

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        chunks_with_scores = []
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                document = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if results["distances"] else 1.0

                # Convert cosine distance to similarity score (1 - distance)
                score = max(0.0, min(1.0, 1.0 - distance))

                chunk = RAGChunk(
                    chunk_id=chunk_id,
                    doc_id=metadata.get("doc_id", ""),
                    source_file=metadata.get("source_file", ""),
                    source_type=metadata.get("source_type", ""),
                    title=metadata.get("title", ""),
                    content=document,
                    metadata=metadata,
                    industry=metadata.get("industry") or None,
                    canvas_tags=[t for t in metadata.get("canvas_tags", "").split(",") if t],
                    pain_points=[p for p in metadata.get("pain_points", "").split(",") if p],
                    ai_scenarios=[s for s in metadata.get("ai_scenarios", "").split(",") if s],
                )
                chunks_with_scores.append((chunk, score))

        return chunks_with_scores

    def count(self) -> int:
        """Get total number of chunks."""
        collection = self.get_collection()
        return collection.count()

    def clear(self) -> None:
        """Clear all chunks from collection."""
        client = self._get_client()
        try:
            client.delete_collection(self.collection_name)
            self._collection = None
        except Exception:
            pass

    def get_status(self, embedding_provider: str, embedding_model: str) -> RAGStatus:
        """Get vector store status."""
        total = self.count()
        return RAGStatus(
            enabled=True,
            indexed=total > 0,
            total_chunks=total,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            last_indexed_at=datetime.now() if total > 0 else None,
        )