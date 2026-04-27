"""Embedding implementation with OpenAI-compatible and fallback modes."""
import os
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI-compatible embedding provider."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "text-embedding-3-small",
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self._model = model
        self._client: Any = None

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def provider_name(self) -> str:
        return "openai"

    def _get_client(self):
        """Lazy init OpenAI client."""
        if self._client is None:
            from openai import OpenAI
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using OpenAI API."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        client = self._get_client()
        response = client.embeddings.create(
            input=texts,
            model=self._model,
        )
        return [item.embedding for item in response.data]


class MockEmbedding(EmbeddingProvider):
    """Mock embedding provider for demo mode."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    @property
    def model_name(self) -> str:
        return "mock-embedding"

    @property
    def provider_name(self) -> str:
        return "mock"

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate deterministic mock embeddings based on text hash."""
        import hashlib

        embeddings = []
        for text in texts:
            # Use hash of text to generate deterministic embedding
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            # Generate dimension values from hash
            embedding = []
            for i in range(self.dimension):
                # Use modulo to get values from hash
                val = int(text_hash[i % len(text_hash):i % len(text_hash) + 2], 16)
                # Normalize to [-0.5, 0.5]
                embedding.append((val - 128) / 256)
            embeddings.append(embedding)
        return embeddings


class EmbeddingManager:
    """Manage embedding providers with fallback."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.provider = provider or os.getenv("EMBEDDING_PROVIDER", "openai")
        self.model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self._embedding_provider: EmbeddingProvider | None = None

    def get_provider(self) -> EmbeddingProvider:
        """Get embedding provider with fallback."""
        if self._embedding_provider is not None:
            return self._embedding_provider

        if self.provider == "mock":
            self._embedding_provider = MockEmbedding()
            return self._embedding_provider

        if self.provider == "openai" and self.api_key:
            try:
                self._embedding_provider = OpenAIEmbedding(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    model=self.model,
                )
                return self._embedding_provider
            except Exception:
                pass

        # Fallback to mock if OpenAI not available
        print("Warning: OpenAI embedding not available, using mock embedding")
        self._embedding_provider = MockEmbedding()
        return self._embedding_provider

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts."""
        return self.get_provider().embed(texts)

    @property
    def model_name(self) -> str:
        return self.get_provider().model_name

    @property
    def provider_name(self) -> str:
        return self.get_provider().provider_name

    @property
    def is_mock(self) -> bool:
        return isinstance(self._embedding_provider, MockEmbedding)