"""RAG schemas for AI readiness assessment."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RAGChunk(BaseModel):
    """A single chunk of knowledge for RAG."""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    doc_id: str = Field(..., description="Source document identifier")
    source_file: str = Field(..., description="Source file name")
    source_type: str = Field(..., description="Type: case, scenario, canvas, template, risk")
    title: str = Field(..., description="Chunk title")
    content: str = Field(..., description="Chunk content text")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Common metadata fields
    industry: str | None = Field(None, description="Related industry")
    canvas_tags: list[str] = Field(default_factory=list, description="Related canvas blocks")
    pain_points: list[str] = Field(default_factory=list, description="Related pain points")
    ai_scenarios: list[str] = Field(default_factory=list, description="Related AI scenarios")


class RAGSearchResult(BaseModel):
    """Result from RAG search."""
    chunk: RAGChunk
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    embedding_model: str | None = Field(None, description="Embedding model used")


class RAGStatus(BaseModel):
    """RAG system status."""
    enabled: bool = Field(..., description="Whether RAG is enabled")
    indexed: bool = Field(default=False, description="Whether knowledge is indexed")
    total_chunks: int = Field(default=0, description="Total chunks in index")
    embedding_provider: str | None = Field(None, description="Embedding provider")
    embedding_model: str | None = Field(None, description="Embedding model")
    is_mock_embedding: bool = Field(default=False, description="Whether using mock embeddings")
    warning: str | None = Field(None, description="Warning message (e.g., mock mode)")
    last_indexed_at: datetime | None = Field(None, description="Last index timestamp")
    error: str | None = Field(None, description="Error message if any")


class HybridMatchResult(BaseModel):
    """Result from hybrid matching (rule + RAG)."""
    chunk: RAGChunk
    rule_score: float = Field(default=0.0, description="Rule-based score (0-100)")
    vector_score: float = Field(default=0.0, description="Vector similarity score (0-1)")
    vector_score_normalized: float = Field(default=0.0, description="Vector score normalized to 0-100 scale")
    final_score: float = Field(..., description="Combined final score (0-100)")
    retrieval_source: str = Field(default="hybrid", description="Source: rule, vector, hybrid, hybrid_mock")
    is_mock_embedding: bool = Field(default=False, description="Whether mock embeddings were used")