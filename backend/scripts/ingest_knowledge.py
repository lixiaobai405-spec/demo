"""RAG ingestion script for knowledge base."""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.rag.retriever import RAGRetriever


def main():
    """Ingest knowledge into vector store."""
    print("=" * 60)
    print("RAG Knowledge Ingestion")
    print("=" * 60)

    # Create retriever with RAG enabled
    retriever = RAGRetriever(rag_enabled=True)

    # Check if already indexed
    status = retriever.get_status()
    print(f"\nCurrent status:")
    print(f"  - Indexed: {status.indexed}")
    print(f"  - Total chunks: {status.total_chunks}")
    if status.error:
        print(f"  - Error: {status.error}")

    # Perform ingestion
    print("\nStarting ingestion...")
    try:
        result = retriever.ingest()
        print(f"\nIngestion result:")
        print(f"  - Status: {result.get('status')}")
        print(f"  - Chunks added: {result.get('chunks_added', 0)}")
        print(f"  - Embedding model: {result.get('embedding_model')}")
        print(f"  - Provider: {result.get('provider')}")

        if result.get('status') == 'error':
            print(f"  - Message: {result.get('message')}")
            return 1

    except Exception as e:
        print(f"\nError during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Verify ingestion
    print("\nVerifying ingestion...")
    status = retriever.get_status()
    print(f"  - Indexed: {status.indexed}")
    print(f"  - Total chunks: {status.total_chunks}")
    print(f"  - Embedding provider: {status.embedding_provider}")
    print(f"  - Embedding model: {status.embedding_model}")

    print("\n" + "=" * 60)
    print("Ingestion completed successfully!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())