"""
LightRAG knowledge-graph adapter for the demo knowledge base.

Replaces ChromaDB vector-only retrieval with LightRAG's graph-enhanced
entity/relationship retrieval when LIGHTRAG_ENABLED=true.

Public API matches the existing RAGRetriever interface so callers
(case_matcher, scenario_recommender, report_enrichment) work unchanged.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.rag.schemas import RAGChunk, RAGSearchResult, RAGStatus

logger = logging.getLogger(__name__)

# ── deferred imports: lightrag is optional ──
_LIGHTRAG_AVAILABLE = False
try:
    from lightrag import LightRAG, QueryParam  # type: ignore[import-untyped]
    from lightrag.utils import EmbeddingFunc

    _LIGHTRAG_AVAILABLE = True
except ImportError:
    pass


@dataclass
class LightRAGConfig:
    enabled: bool = False
    working_dir: str = "./backend/data/lightrag"
    llm_model: str = ""
    embedding_model: str = "text-embedding-3-small"
    top_k: int = 5


def _build_llm_func() -> Any:
    """Build an async LLM callable compatible with LightRAG's llm_model_func signature.

    Returns a wrapper around the project's OpenAI client (same credentials as
    the rest of the backend).  Cached at module level to avoid repeated imports.
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    async def _call(prompt: str, system_prompt: str | None = None, history_messages: list[dict] | None = None, **kwargs: Any) -> str:
        messages: list[dict] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.3,
                max_tokens=kwargs.get("max_tokens", 2048),
            ),
        )
        return response.choices[0].message.content or ""

    return _call


def _build_embedding_func() -> Any:
    """Build an EmbeddingFunc compatible with LightRAG.

    LightRAG's EmbeddingFunc expects the wrapped function to return a numpy
    array (ndarray), not a plain Python list.
    """
    import numpy as np
    from app.rag.embeddings import EmbeddingManager

    manager = EmbeddingManager()
    provider = manager.get_provider()  # force init to detect mock/real
    dim = 384 if isinstance(provider, __import__('app.rag.embeddings', fromlist=['MockEmbedding']).MockEmbedding) else 1536

    # Actually just ask the first embedding what dimension it produces
    test_embed = manager.embed(["test"])
    dim = len(test_embed[0])

    async def _embed(texts: list[str]) -> np.ndarray:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, manager.embed, texts)
        return np.array(result, dtype=np.float32)

    return EmbeddingFunc(
        embedding_dim=dim,
        max_token_size=8191,
        func=_embed,
    )


class LightRAGAdapter:
    """Thin wrapper around LightRAG that speaks the project's RAG interface.

    Maintains a persistent background event loop so that LightRAG's internal
    worker pools and locks survive across multiple sync calls.
    """

    def __init__(
        self,
        *,
        working_dir: str | None = None,
        top_k: int | None = None,
    ) -> None:
        if not _LIGHTRAG_AVAILABLE:
            raise ImportError(
                "lightrag-hku is not installed. "
                "Run: pip install lightrag-hku  "
                "or: pip install -e /path/to/LightRAG"
            )

        import threading
        wd = working_dir or settings.lightrag_working_dir
        Path(wd).mkdir(parents=True, exist_ok=True)

        # ── Persistent event loop for LightRAG lifetime ──
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

        llm_func = _build_llm_func()
        emb_func = _build_embedding_func()

        self._rag = LightRAG(
            working_dir=wd,
            llm_model_func=llm_func,
            embedding_func=emb_func,
            top_k=top_k or settings.lightrag_top_k,
        )

        # Initialize storages in the persistent loop
        asyncio.run_coroutine_threadsafe(
            self._rag.initialize_storages(), self._loop
        ).result(timeout=30)

        self._top_k = top_k or settings.lightrag_top_k
        self._working_dir = wd

    def _run_async(self, coro, timeout: int = 60):
        """Run a coroutine in the persistent LightRAG event loop and return its result."""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    # ── public API (sync, matches RAGRetriever) ──

    def search(
        self,
        query: str,
        top_k: int | None = None,
        filter_type: str | None = None,
    ) -> list[RAGSearchResult]:
        """Graph-enhanced search.  filter_type is ignored (LightRAG uses modes)."""
        k = top_k or self._top_k
        try:
            return self._run_async(self._asearch(query, k), timeout=30)
        except Exception as exc:
            logger.warning("LightRAG search failed: %s", exc)
            return []

    async def _asearch(self, query: str, top_k: int) -> list[RAGSearchResult]:
        param = QueryParam(mode="mix", top_k=top_k, only_need_context=True)
        result = await self._rag.aquery_data(query, param)  # type: ignore[arg-type]

        if result.get("status") != "success":
            return []

        data = result.get("data", {})
        results: list[RAGSearchResult] = []

        # Map entities → RAGSearchResult
        for ent in data.get("entities", []):
            results.append(
                RAGSearchResult(
                    chunk=RAGChunk(
                        chunk_id=f"lr-ent-{ent.get('entity_name', '')}",
                        doc_id="lightrag",
                        source_file="knowledge_graph",
                        source_type="entity",
                        title=ent.get("entity_name", ""),
                        content=ent.get("description", ""),
                        metadata={"type": "entity", "source": "lightrag"},
                    ),
                    score=float(ent.get("score", 0.0)),
                    embedding_model="lightrag",
                )
            )

        # Map relations → lower score
        for rel in data.get("relationships", []):
            results.append(
                RAGSearchResult(
                    chunk=RAGChunk(
                        chunk_id=f"lr-rel-{rel.get('source', '')}-{rel.get('target', '')}",
                        doc_id="lightrag",
                        source_file="knowledge_graph",
                        source_type="relation",
                        title=f"{rel.get('source', '')} → {rel.get('target', '')}",
                        content=rel.get("description", ""),
                        metadata={"type": "relation", "source": "lightrag"},
                    ),
                    score=float(rel.get("score", 0.0)) * 0.8,  # relations weighted lower
                    embedding_model="lightrag",
                )
            )

        # Map chunks
        for ch in data.get("chunks", []):
            results.append(
                RAGSearchResult(
                    chunk=RAGChunk(
                        chunk_id=ch.get("chunk_id", ""),
                        doc_id=ch.get("doc_id", ""),
                        source_file=ch.get("file_path", ""),
                        source_type="chunk",
                        title=ch.get("file_path", ""),
                        content=ch.get("content", ""),
                        metadata={"type": "chunk", "source": "lightrag"},
                    ),
                    score=float(ch.get("score", 0.0)),
                    embedding_model="lightrag",
                )
            )

        # De-duplicate by chunk_id and sort by score
        seen: set[str] = set()
        unique: list[RAGSearchResult] = []
        for r in sorted(results, key=lambda x: x.score, reverse=True):
            if r.chunk.chunk_id not in seen:
                seen.add(r.chunk.chunk_id)
                unique.append(r)

        return unique[:top_k]

    def ingest(self) -> dict:
        """Ingest all knowledge-base sources into LightRAG (blocking wrapper)."""
        if not _LIGHTRAG_AVAILABLE:
            return {"status": "error", "message": "lightrag-hku is not installed"}

        try:
            return self._run_async(self._aingest_all(), timeout=300)
        except Exception as exc:
            logger.exception("LightRAG ingest failed: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def _aingest_all(self) -> dict:
        from app.rag.document_loader import DocumentLoader

        loader = DocumentLoader()
        sources = loader.load_all_sources()

        texts: list[str] = []
        # Industry cases
        for case in sources.get("cases", []):
            parts = [case.get("title", ""), case.get("summary", "")]
            if case.get("reference_points"):
                parts.append("参考做法：" + "；".join(case["reference_points"]))
            texts.append("\n".join(parts))

        # AI scenarios
        for sc in sources.get("scenarios", []):
            parts = [sc.get("name", ""), sc.get("description", "")]
            if sc.get("value_points"):
                parts.append("价值点：" + "；".join(sc["value_points"]))
            texts.append("\n".join(parts))

        # Markdown guides
        for key in ("canvas_guide", "report_templates", "risk_playbook"):
            md = sources.get(key)
            if md and isinstance(md, str):
                texts.append(md)

        # User-uploaded files (from data directory)
        upload_dir = Path(self._working_dir).parent / "uploads"
        if upload_dir.exists():
            for f in upload_dir.iterdir():
                if f.suffix in (".txt", ".md"):
                    try:
                        texts.append(f.read_text(encoding="utf-8"))
                    except Exception:
                        pass

        if not texts:
            return {"status": "skipped", "message": "No documents to index"}

        # Insert in batches
        await self._rag.ainsert(texts)
        return {
            "status": "success",
            "chunks_added": len(texts),
            "embedding_provider": "lightrag",
        }

    def ingest_document(self, text: str, source_file: str, metadata: dict | None = None) -> dict:
        """Ingest a single document (e.g. user-uploaded file)."""
        try:
            result = self._run_async(self._rag.ainsert(text, file_paths=[source_file]), timeout=120)
            return {"status": "success", "track_id": result}
        except Exception as exc:
            logger.warning("LightRAG document ingest failed: %s", exc)
            return {"status": "error", "message": str(exc)}

    def get_status(self) -> RAGStatus:
        """Return LightRAG index status."""
        if not _LIGHTRAG_AVAILABLE:
            return RAGStatus(
                enabled=False,
                indexed=False,
                total_chunks=0,
                embedding_provider=None,
                embedding_model=None,
                is_mock_embedding=False,
                error="lightrag-hku is not installed",
            )

        try:
            # LightRAG doesn't expose a direct count; we check if the working dir has data
            kg_file = Path(self._working_dir) / "kv_store_full_docs.json"
            total = 0
            if kg_file.exists():
                import json
                try:
                    data = json.loads(kg_file.read_text(encoding="utf-8"))
                    total = len(data) if isinstance(data, dict) else 0
                except Exception:
                    pass

            from app.rag.embeddings import EmbeddingManager
            mgr = EmbeddingManager()
            return RAGStatus(
                enabled=True,
                indexed=total > 0,
                total_chunks=total,
                embedding_provider="lightrag",
                embedding_model=mgr.model_name,
                is_mock_embedding=mgr.is_mock,
            )
        except Exception as exc:
            return RAGStatus(
                enabled=True,
                indexed=False,
                total_chunks=0,
                embedding_provider="lightrag",
                embedding_model=None,
                is_mock_embedding=False,
                error=str(exc),
            )

    def is_available(self) -> bool:
        status = self.get_status()
        return status.enabled and status.indexed
