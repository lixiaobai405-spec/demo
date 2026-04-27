"""RAG API schemas."""
from pydantic import BaseModel, Field


class RAGStatusResponse(BaseModel):
    """RAG status response."""
    enabled: bool = Field(..., description="Whether RAG is enabled")
    indexed: bool = Field(..., description="Whether knowledge is indexed")
    total_chunks: int = Field(..., description="Total chunks in index")
    embedding_provider: str | None = Field(None, description="Embedding provider")
    embedding_model: str | None = Field(None, description="Embedding model")
    is_mock_embedding: bool = Field(default=False, description="Whether using mock embeddings")
    warning: str | None = Field(None, description="Warning message if in mock mode")
    error: str | None = Field(None, description="Error message if any")


class RAGSearchRequest(BaseModel):
    """RAG search request."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    filter_type: str | None = Field(
        default=None,
        description="Filter by source type: case, scenario, canvas, template, risk",
    )


class RAGSearchResultItem(BaseModel):
    """Single search result item."""
    chunk_id: str = Field(..., description="Chunk identifier")
    source_type: str = Field(..., description="Source type")
    title: str = Field(..., description="Chunk title")
    content: str = Field(..., description="Chunk content")
    score: float = Field(..., ge=0.0, le=100.0, description="Relevance score (0-100)")
    rule_score: float = Field(default=0.0, description="Rule-based score (0-100)")
    vector_score: float = Field(default=0.0, description="Vector similarity score (0-1)")
    vector_score_normalized: float = Field(default=0.0, description="Vector score normalized (0-100)")
    retrieval_source: str = Field(default="hybrid", description="Source: rule, vector, hybrid, hybrid_mock")
    is_mock_embedding: bool = Field(default=False, description="Whether mock embeddings were used")
    industry: str | None = Field(None, description="Related industry")
    canvas_tags: list[str] = Field(default_factory=list, description="Related canvas blocks")
    pain_points: list[str] = Field(default_factory=list, description="Related pain points")
    ai_scenarios: list[str] = Field(default_factory=list, description="Related AI scenarios")


class RAGSearchResponse(BaseModel):
    """RAG search response."""
    query: str = Field(..., description="Original query")
    results: list[RAGSearchResultItem] = Field(default_factory=list, description="Search results")
    total: int = Field(..., description="Total results found")
    embedding_model: str | None = Field(None, description="Embedding model used")


class RAGIngestResponse(BaseModel):
    """RAG ingest response."""
    status: str = Field(..., description="Ingestion status")
    chunks_added: int = Field(default=0, description="Number of chunks added")
    embedding_model: str | None = Field(None, description="Embedding model used")
    provider: str | None = Field(None, description="Embedding provider")
    message: str | None = Field(None, description="Additional message")