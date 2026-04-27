"""RAG API routes."""
from fastapi import APIRouter, HTTPException

from app.rag.retriever import RAGRetriever
from app.schemas.rag import (
    RAGIngestResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResultItem,
    RAGStatusResponse,
)

router = APIRouter(prefix="/rag", tags=["rag"])

# Global retriever instance (lazy initialized)
_retriever: RAGRetriever | None = None


def get_retriever() -> RAGRetriever:
    """Get or create RAG retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = RAGRetriever()
    return _retriever


@router.get("/status", response_model=RAGStatusResponse, summary="Get RAG status")
def get_rag_status() -> RAGStatusResponse:
    """Get current RAG system status."""
    retriever = get_retriever()
    status = retriever.get_status()
    return RAGStatusResponse(
        enabled=status.enabled,
        indexed=status.indexed,
        total_chunks=status.total_chunks,
        embedding_provider=status.embedding_provider,
        embedding_model=status.embedding_model,
        is_mock_embedding=status.is_mock_embedding,
        warning=status.warning,
        error=status.error,
    )


@router.post("/search", response_model=RAGSearchResponse, summary="Search knowledge base")
def search_knowledge(request: RAGSearchRequest) -> RAGSearchResponse:
    """Search the RAG knowledge base for relevant chunks."""
    retriever = get_retriever()

    if not retriever.is_available():
        return RAGSearchResponse(
            query=request.query,
            results=[],
            total=0,
            embedding_model=None,
        )

    try:
        results = retriever.search(
            query=request.query,
            top_k=request.top_k,
            filter_type=request.filter_type,
        )

        items = [
            RAGSearchResultItem(
                chunk_id=r.chunk.chunk_id,
                source_type=r.chunk.source_type,
                title=r.chunk.title,
                content=r.chunk.content,
                score=r.final_score,
                rule_score=r.rule_score,
                vector_score=r.vector_score,
                vector_score_normalized=r.vector_score_normalized,
                retrieval_source=r.retrieval_source,
                is_mock_embedding=r.is_mock_embedding,
                industry=r.chunk.industry,
                canvas_tags=r.chunk.canvas_tags,
                pain_points=r.chunk.pain_points,
                ai_scenarios=r.chunk.ai_scenarios,
            )
            for r in results
        ]

        return RAGSearchResponse(
            query=request.query,
            results=items,
            total=len(items),
            embedding_model=results[0].embedding_model if results else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/ingest", response_model=RAGIngestResponse, summary="Ingest knowledge base")
def ingest_knowledge() -> RAGIngestResponse:
    """Ingest knowledge files into the vector store."""
    retriever = get_retriever()

    try:
        result = retriever.ingest()
        return RAGIngestResponse(
            status=result.get("status", "unknown"),
            chunks_added=result.get("chunks_added", 0),
            embedding_model=result.get("embedding_model"),
            provider=result.get("provider"),
            message=result.get("message"),
        )
    except Exception as e:
        return RAGIngestResponse(
            status="error",
            message=str(e),
        )