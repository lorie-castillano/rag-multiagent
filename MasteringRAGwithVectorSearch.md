# Mastering RAG with Vector Search

**Prerequisite:** Steps 1–8 of the RAG Multiagent system are complete.
**Current state:** Elasticsearch 8.13 + Gemini embeddings (`models/gemini-embedding-001`, 3072 dims) + kNN cosine similarity + MCP specialist subagent + Windsurf Cascade orchestrator.

---

## Step 1 — Establish RAG Evaluation Framework
- [ ] Create 20+ question-context-answer triplets from resume/job docs as ground truth
- [ ] Write evaluation script measuring **Hit Rate** and **MRR** (retrieval quality)
- [ ] Measure **faithfulness** (answer grounded in chunks?) and **answer relevance** (addresses the question?)
- [ ] Optionally integrate `ragas` library for automated scoring
- **Estimated time**: ~4 hours
- **Depends on**: —
- **Why first**: You can't improve what you can't measure. All other steps use this to validate improvements.

## Step 2 — Implement Hybrid Search + Reciprocal Rank Fusion (RRF)
- [ ] Configure Elasticsearch to run BM25 + kNN in a single hybrid query
- [ ] Enable RRF scoring to merge and re-rank combined results
- [ ] Compare hybrid vs pure vector search scores using Step 1 eval
- **Estimated time**: ~3 hours
- **Depends on**: Step 1
- **Why**: BM25 catches exact keyword matches; kNN catches semantic meaning — hybrid wins both.

## Step 3 — Add Metadata Pre-Filtering
- [ ] Update `ingest.py` index mappings to include `doc_type`, `date`, `category` fields
- [ ] Update `agents/elasticsearch_agent.py` to accept optional filter params
- [ ] Apply hard metadata filters before kNN vector search (e.g. "only search resume chunks")
- **Estimated time**: ~2 hours
- **Depends on**: Step 2
- **Why**: Filtering before vector search reduces noise and speeds up retrieval.

## Step 4 — Parent-Child (Hierarchical) Chunking
- [ ] Refactor `ingest.py` to create small child chunks (~150 words) for vector matching
- [ ] Store larger parent chunks (~500 words) linked to each child via `parent_id`
- [ ] Update retrieval to match on child vectors but return parent text to LLM
- **Estimated time**: ~4 hours
- **Depends on**: Step 1
- **Why**: Small chunks = precise retrieval. Large parent context = better LLM answers.

## Step 5 — Integrate a Re-ranking Stage
- [ ] Retrieve top 25 candidates via Elasticsearch hybrid search
- [ ] Integrate a cross-encoder reranker (Cohere Rerank API or HuggingFace `cross-encoder/ms-marco-MiniLM-L-6-v2`)
- [ ] Reranker selects final top 5 → passed to LLM
- [ ] Measure improvement with Step 1 eval framework
- **Estimated time**: ~3 hours
- **Depends on**: Step 2
- **Why**: Cosine similarity ranks by vector closeness; cross-encoders understand full query-document interaction — much more accurate.

## Step 6 — Query Transformation / HyDE
- [ ] Add Gemini pre-processing step to rewrite vague queries into better search queries
- [ ] Implement **HyDE** (Hypothetical Document Embeddings): generate a hypothetical answer → embed it → use that vector for retrieval
- [ ] A/B test: original query vs rewritten query vs HyDE — compare Hit Rate
- **Estimated time**: ~3 hours
- **Depends on**: Step 1
- **Why**: Query quality directly affects retrieval quality. Better queries → better chunks → better answers.

## Step 7 — Benchmark + Hyperparameter Tuning
- [ ] Run Step 1 eval framework against all implemented strategies (Steps 2–6)
- [ ] Tune `TOP_K`, `MIN_SCORE`, chunk sizes, RRF weights
- [ ] Document the winning configuration for your dataset
- [ ] Update `ingest.py` and `agents/elasticsearch_agent.py` with optimal settings
- **Estimated time**: ~4 hours
- **Depends on**: Steps 1–6 (all complete)
- **Why**: Combines all improvements and finds the globally optimal setup.

---

## Dependency Order

```
Step 1 (Eval Framework)
    ├── Step 2 (Hybrid Search + RRF)
    │       ├── Step 3 (Metadata Filtering)
    │       └── Step 5 (Re-ranking)
    ├── Step 4 (Parent-Child Chunking)
    └── Step 6 (Query Transformation / HyDE)
                        └── Step 7 (Benchmark + Tuning) ← depends on all
```

Steps 4 and 6 can run in parallel with Step 2.

---

## Key Concepts to Know Before Starting

| Concept | What it is |
|---|---|
| **Hit Rate** | % of queries where the correct chunk appears in top-K results |
| **MRR** | Mean Reciprocal Rank — how high up the correct chunk ranks on average |
| **Faithfulness** | LLM answer only uses information from retrieved chunks |
| **RRF** | Reciprocal Rank Fusion — formula to merge rankings from BM25 + kNN |
| **Cross-encoder** | Model that scores query+document pairs jointly — more accurate than bi-encoder cosine similarity |
| **HyDE** | Generate a fake ideal answer → embed it → retrieve docs similar to that fake answer |
| **Parent-Child chunking** | Index small chunks for retrieval precision, return large parent for LLM context |

---

## Stack Reference

- **Elasticsearch**: 8.13 (Docker, `localhost:9200`)
- **Embedding model**: `models/gemini-embedding-001` (3072 dims, cosine similarity)
- **MCP subagent**: `agents/elasticsearch_agent.py`
- **Ingestion**: `ingest.py` (400-word chunks, 80-word overlap)
- **Orchestrator**: Windsurf Cascade
- **Workflow**: `.windsurf/workflows/rag_query.md`
- **Venv**: `venv/` — activate with `source venv/bin/activate`

---

*Last updated: May 23, 2026 — Steps 1–8 complete. Ready to start mastery roadmap.*
