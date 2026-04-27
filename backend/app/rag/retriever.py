"""RAG retriever with hybrid matching support."""
import os
from datetime import datetime

from app.rag.chunker import DocumentChunker
from app.rag.document_loader import DocumentLoader
from app.rag.embeddings import EmbeddingManager
from app.rag.schemas import HybridMatchResult, RAGChunk, RAGSearchResult, RAGStatus
from app.rag.vector_store import VectorStore


class RAGRetriever:
    """RAG retriever with hybrid matching (rule + vector)."""

    def __init__(
        self,
        rag_enabled: bool | None = None,
        persist_dir: str | None = None,
        top_k: int | None = None,
    ):
        self.rag_enabled = (
            rag_enabled if rag_enabled is not None
            else os.getenv("RAG_ENABLED", "false").lower() == "true"
        )
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR")
        self.top_k = top_k or int(os.getenv("RAG_TOP_K", "5"))

        self._embedding_manager: EmbeddingManager | None = None
        self._vector_store: VectorStore | None = None
        self._loader: DocumentLoader | None = None
        self._chunker: DocumentChunker | None = None

    @property
    def embedding_manager(self) -> EmbeddingManager:
        if self._embedding_manager is None:
            self._embedding_manager = EmbeddingManager()
        return self._embedding_manager

    @property
    def vector_store(self) -> VectorStore:
        if self._vector_store is None:
            self._vector_store = VectorStore(persist_dir=self.persist_dir)
        return self._vector_store

    @property
    def loader(self) -> DocumentLoader:
        if self._loader is None:
            self._loader = DocumentLoader()
        return self._loader

    @property
    def chunker(self) -> DocumentChunker:
        if self._chunker is None:
            self._chunker = DocumentChunker()
        return self._chunker

    def ingest(self) -> dict:
        """Ingest all knowledge into vector store."""
        if not self.rag_enabled:
            return {"status": "disabled", "message": "RAG is not enabled"}

        # Load all sources
        sources = self.loader.load_all_sources()

        # Chunk documents
        chunks = self.chunker.chunk_all(
            cases=sources.get("cases", []),
            scenarios=sources.get("scenarios", []),
            canvas_guide=sources.get("canvas_guide"),
            report_templates=sources.get("report_templates"),
            risk_playbook=sources.get("risk_playbook"),
        )

        if not chunks:
            return {"status": "error", "message": "No chunks to ingest"}

        # Generate embeddings
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_manager.embed(texts)

        # Clear existing and add new
        self.vector_store.clear()
        added = self.vector_store.add_chunks(chunks, embeddings)

        return {
            "status": "success",
            "chunks_added": added,
            "embedding_model": self.embedding_manager.model_name,
            "provider": self.embedding_manager.provider_name,
        }

    def search(
        self,
        query: str,
        top_k: int | None = None,
        filter_type: str | None = None,
    ) -> list[RAGSearchResult]:
        """Search for relevant chunks."""
        if not self.rag_enabled:
            return []

        top_k = top_k or self.top_k

        # Generate query embedding
        query_embedding = self.embedding_manager.embed([query])[0]

        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_type=filter_type,
        )

        return [
            RAGSearchResult(
                chunk=chunk,
                score=score,
                embedding_model=self.embedding_manager.model_name,
            )
            for chunk, score in results
        ]

    def hybrid_match(
        self,
        query: str,
        candidates: list[RAGChunk],
        rule_scores: list[float],
        rule_weight: float = 0.70,
        vector_weight: float = 0.30,
    ) -> list[HybridMatchResult]:
        """Combine rule-based and vector search results.
        
        Scores:
        - rule_score: 0-100 scale
        - vector_score: 0-1 scale (ChromaDB distance)
        - vector_score_normalized: 0-100 scale (vector_score * 100)
        - final_score: 0-100 scale (rule * 0.70 + vector_normalized * 0.30)
        """
        is_mock = self.embedding_manager.is_mock
        
        if not self.rag_enabled:
            # Fallback to rule-only
            return [
                HybridMatchResult(
                    chunk=chunk,
                    rule_score=rule_score,
                    vector_score=0.0,
                    vector_score_normalized=0.0,
                    final_score=rule_score,
                    retrieval_source="rule",
                    is_mock_embedding=False,
                )
                for chunk, rule_score in zip(candidates, rule_scores)
            ]

        # Get vector search results
        vector_results = self.search(query, top_k=len(candidates) * 2)
        vector_scores = {r.chunk.chunk_id: r.score for r in vector_results}

        results = []
        for chunk, rule_score in zip(candidates, rule_scores):
            vector_score = vector_scores.get(chunk.chunk_id, 0.0)
            # Normalize vector score to 0-100 scale
            vector_score_normalized = vector_score * 100
            # Calculate final score with normalized vector score
            final_score = rule_score * rule_weight + vector_score_normalized * vector_weight

            # Determine retrieval source
            if vector_score > 0:
                retrieval_source = "hybrid_mock" if is_mock else "hybrid"
            else:
                retrieval_source = "rule"

            results.append(HybridMatchResult(
                chunk=chunk,
                rule_score=rule_score,
                vector_score=vector_score,
                vector_score_normalized=vector_score_normalized,
                final_score=final_score,
                retrieval_source=retrieval_source,
                is_mock_embedding=is_mock,
            ))

        # Sort by final score
        results.sort(key=lambda x: x.final_score, reverse=True)
        return results

    def get_status(self) -> RAGStatus:
        """Get RAG system status."""
        if not self.rag_enabled:
            return RAGStatus(
                enabled=False,
                indexed=False,
                total_chunks=0,
                embedding_provider=None,
                embedding_model=None,
                is_mock_embedding=False,
                warning=None,
                error="RAG is disabled by configuration",
            )

        try:
            status = self.vector_store.get_status(
                embedding_provider=self.embedding_manager.provider_name,
                embedding_model=self.embedding_manager.model_name,
            )
            # Add mock embedding status
            is_mock = self.embedding_manager.is_mock
            status.is_mock_embedding = is_mock
            if is_mock:
                status.warning = (
                    "RAG is running with mock embeddings. "
                    "Retrieval results are for demo only."
                )
            return status
        except Exception as e:
            return RAGStatus(
                enabled=True,
                indexed=False,
                total_chunks=0,
                embedding_provider=None,
                embedding_model=None,
                is_mock_embedding=False,
                warning=None,
                error=str(e),
            )

    def is_available(self) -> bool:
        """Check if RAG is available for use."""
        if not self.rag_enabled:
            return False
        status = self.get_status()
        return status.indexed and status.total_chunks > 0