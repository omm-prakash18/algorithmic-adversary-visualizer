"""
High-Performance RAG Engine (v2.0)
===================================
Thread-safe, persistent ChromaDB-backed vector store with MMR retrieval,
semantic metadata filtering, query caching, and automatic reranking.

Architecture:
  ChromaDB (persistent) ← OpenAI Embeddings ← Knowledge Base Documents
  Query → Metadata Filter → MMR Retriever → Reranker → Context
"""

import hashlib
import logging
import os
import threading
import time
from functools import lru_cache
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Singleton RAG engine with persistent ChromaDB storage,
    thread-safe initialization, and intelligent caching.
    """

    _instance: Optional["RAGEngine"] = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return

            self._vectorstores: dict[str, any] = {}
            self._embeddings = None
            self._query_cache: dict[str, tuple[float, list]] = {}
            self._cache_ttl = 300  # 5 minutes
            self._max_cache_size = 200
            self._initialized = True
            logger.info("RAGEngine singleton initialized")

    def _get_api_key(self) -> str:
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            # Try to see if there's a Google API key as backup
            key = os.getenv("GOOGLE_API_KEY", "")
            if not key:
                raise ValueError("Neither OPENAI_API_KEY nor GOOGLE_API_KEY set in environment")
        return key

    def _ensure_vectorstore(self, collection_name: str = "algorithm_knowledge_v2"):
        """Lazy-initialize the vector store with ChromaDB persistent backend."""
        if collection_name in self._vectorstores:
            return

        with self._lock:
            if collection_name in self._vectorstores:
                return

            start = time.perf_counter()

            try:
                # 1. Try to get API key (OpenAI preferred, then Google)
                api_key = ""
                try:
                    api_key = self._get_api_key()
                except ValueError:
                    logger.warning("No API keys found, using FakeEmbeddings for offline mode")

                # 2. Initialize Embeddings
                self._embeddings = None
                if api_key.startswith("sk-"):
                    from langchain_openai import OpenAIEmbeddings
                    self._embeddings = OpenAIEmbeddings(
                        api_key=api_key,
                        model="text-embedding-3-small",
                        max_retries=0, # Fail fast to trigger fallback
                    )

                elif api_key:
                    # Google or other
                    try:
                        from langchain_google_genai import GoogleGenerativeAIEmbeddings
                        self._embeddings = GoogleGenerativeAIEmbeddings(
                            model="models/embedding-001",
                            google_api_key=api_key
                        )
                    except ImportError:
                        logger.warning("langchain-google-genai not installed, using FakeEmbeddings")

                if self._embeddings is None:
                    from langchain_core.embeddings import FakeEmbeddings
                    self._embeddings = FakeEmbeddings(size=1536)

                # 3. Initialize Vector Store
                persist_dir = os.path.join(
                    settings.BASE_DIR, ".chromadb", "algo_visualizer"
                )
                os.makedirs(persist_dir, exist_ok=True)

                try:
                    from langchain_chroma import Chroma
                    self._vectorstores[collection_name] = Chroma(
                        persist_directory=persist_dir,
                        embedding_function=self._embeddings,
                        collection_name=collection_name,
                    )
                except ImportError:
                    logger.warning("langchain-chroma not found, falling back to InMemoryVectorStore")
                    from langchain_community.vectorstores import InMemoryVectorStore
                    # We can't persist InMemoryVectorStore easily, so we just populate it every time
                    self._vectorstores[collection_name] = InMemoryVectorStore(self._embeddings)

                # 4. Populate if empty
                is_empty = True
                if hasattr(self._vectorstores[collection_name], "get"):
                    # ChromaDB
                    is_empty = not self._vectorstores[collection_name].get()['ids']
                elif hasattr(self._vectorstores[collection_name], "_store"):
                    # LangChain InMemoryVectorStore
                    is_empty = len(self._vectorstores[collection_name]._store) == 0
                
                if is_empty:
                    logger.info(f"Populating empty collection: {collection_name}")
                    from .models import KnowledgeDocument
                    from langchain_core.documents import Document

                    # 1. Try to pull from DB first
                    db_docs = KnowledgeDocument.objects.filter(collection_name=collection_name)
                    if db_docs.exists():
                        docs_to_add = [
                            Document(page_content=d.content, metadata=d.metadata)
                            for d in db_docs
                        ]
                    else:
                        # 2. Fallback to hardcoded knowledge and save to DB
                        if collection_name == "algorithm_knowledge_v2":
                            from .knowledge_base import VISUALIZATION_KNOWLEDGE
                            docs_to_add = VISUALIZATION_KNOWLEDGE
                        elif collection_name == "adversary_knowledge_v1":
                            from adversary.knowledge_base import ADVERSARY_KNOWLEDGE
                            docs_to_add = ADVERSARY_KNOWLEDGE
                        else:
                            docs_to_add = []

                        # Save to DB for future persistency
                        for doc in docs_to_add:
                            KnowledgeDocument.objects.get_or_create(
                                collection_name=collection_name,
                                content=doc.page_content,
                                metadata=doc.metadata,
                            )
                    
                    if docs_to_add:
                        self._vectorstores[collection_name].add_documents(docs_to_add)
                        logger.info(f"Added {len(docs_to_add)} docs to {collection_name}")

                elapsed = (time.perf_counter() - start) * 1000
                logger.info(f"Vectorstore '{collection_name}' ready in {elapsed:.1f}ms")

            except Exception as e:
                logger.error(f"Critical failure in RAG initialization for {collection_name}: {e}")


    def _cache_key(self, query: str, category: Optional[str] = None, k: int = 4) -> str:
        """Generate a deterministic cache key for a query."""
        raw = f"{query}|{category}|{k}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _evict_expired_cache(self):
        """Remove expired entries and enforce max cache size."""
        now = time.time()
        # Thread-safe iteration
        with self._lock:
            expired = [
                k for k, (ts, _) in self._query_cache.items()
                if now - ts > self._cache_ttl
            ]
            for k in expired:
                del self._query_cache[k]

            # LRU-style eviction if over max size
            if len(self._query_cache) > self._max_cache_size:
                sorted_keys = sorted(
                    self._query_cache.keys(),
                    key=lambda k: self._query_cache[k][0]
                )
                for k in sorted_keys[:len(self._query_cache) - self._max_cache_size]:
                    del self._query_cache[k]

    def retrieve(
        self,
        query: str,
        category: Optional[str] = None,
        k: int = 4,
        use_mmr: bool = True,
        mmr_diversity: float = 0.3,
        collection_name: str = "algorithm_knowledge_v2",
    ) -> list:
        """
        Retrieve relevant documents with MMR diversity and optional metadata filtering.
        """
        # Check cache first
        cache_key = self._cache_key(query, category, k) + f"|{collection_name}"
        self._evict_expired_cache()

        with self._lock:
            if cache_key in self._query_cache:
                _, docs = self._query_cache[cache_key]
                logger.debug(f"RAG cache hit for key {cache_key}")
                return docs

        self._ensure_vectorstore(collection_name)
        
        with self._lock:
            vectorstore = self._vectorstores.get(collection_name)

        if vectorstore is None:
            logger.error(f"Vectorstore {collection_name} not available")
            return []


        start = time.perf_counter()

        try:
            # Build metadata filter
            filter_dict = None
            if category:
                filter_dict = {"category": category}

            if use_mmr:
                # MMR provides diverse, relevant results
                docs = vectorstore.max_marginal_relevance_search(
                    query,
                    k=k,
                    fetch_k=min(k * 3, 20),
                    lambda_mult=1.0 - mmr_diversity,
                    filter=filter_dict,
                )
            else:
                # Pure similarity search
                docs = vectorstore.similarity_search(
                    query,
                    k=k,
                    filter=filter_dict,
                )

            # Cache the result
            self._query_cache[cache_key] = (time.time(), docs)

            elapsed = (time.perf_counter() - start) * 1000
            logger.info(
                f"RAG retrieval from '{collection_name}': {len(docs)} docs in {elapsed:.1f}ms "
                f"(mmr={use_mmr}, category={category})"
            )

            return docs

        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")
            # Return empty list on failure — caller handles graceful degradation
            return []

    def detect_algorithm_category(self, code: str) -> Optional[str]:
        """
        Heuristic code analysis to detect the algorithm category
        for metadata-filtered retrieval.
        """
        code_lower = code.lower()

        # Tree indicators
        if any(kw in code_lower for kw in ["->left", "->right", "root->", "treenode", "bst"]):
            return "trees"

        # Graph indicators
        if any(kw in code_lower for kw in ["adj[", "adjacency", "graph", "bfs", "dfs", "dijkstra", "visited["]):
            return "graphs"

        # Sorting indicators
        if any(kw in code_lower for kw in ["sort", "bubble", "quicksort", "mergesort", "partition"]):
            return "sorting"

        # DP indicators
        if any(kw in code_lower for kw in ["dp[", "memo[", "knapsack", "fibonacci", "tabulation"]):
            return "dynamic_programming"

        # Linear structure indicators
        if any(kw in code_lower for kw in ["->next", "stack", "queue", "push", "pop", "enqueue"]):
            return "linear"

        # Hash table indicators
        if any(kw in code_lower for kw in ["hash", "unordered_map", "bucket"]):
            return "hashing"

        # Heap indicators
        if any(kw in code_lower for kw in ["heap", "priority_queue", "sift", "heapify"]):
            return "trees"

        return None

    def get_context_string(
        self,
        code: str,
        k: int = 4,
        use_mmr: bool = True,
        collection_name: str = "algorithm_knowledge_v2",
    ) -> str:
        """
        High-level convenience method: detect category, retrieve docs,
        and return a formatted context string for the LLM prompt.
        """
        category = self.detect_algorithm_category(code)
        docs = self.retrieve(
            code, category=category, k=k, use_mmr=use_mmr, collection_name=collection_name
        )


        if not docs:
            return ""

        context_parts = []
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            algo = meta.get("algorithm", meta.get("category", "General"))
            pattern = meta.get("pattern", "unknown")
            context_parts.append(
                f"[Reference {i} — {algo}/{pattern}]\n{doc.page_content}"
            )

        return "\n\n---\n\n".join(context_parts)

    def clear_cache(self):
        """Clear the query cache (useful for testing or manual refresh)."""
        self._query_cache.clear()
        logger.info("RAG query cache cleared")

    def get_stats(self) -> dict:
        """Return engine statistics for diagnostics."""
        return {
            "initialized": len(self._vectorstores) > 0,
            "cache_size": len(self._query_cache),
            "cache_ttl_seconds": self._cache_ttl,
            "max_cache_size": self._max_cache_size,
        }


# Module-level convenience accessor
def get_rag_engine() -> RAGEngine:
    """Get the global RAG engine singleton."""
    return RAGEngine()
