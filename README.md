# RAG Multiagent System

A production-pattern **Retrieval-Augmented Generation (RAG)** system built on the **Model Context Protocol (MCP)**, using a multiagent architecture with an orchestrator and a specialist subagent.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────┐
│   Windsurf Cascade       │  ← Orchestrator (LLM reasoning layer)
│   (Lead Agent)           │    Decides when to retrieve, synthesizes final response
└────────────┬────────────┘
             │  MCP tool call: retrieve_documents(query)
             ▼
┌─────────────────────────┐
│  Elasticsearch Specialist│  ← Subagent (MCP Server)
│  Subagent                │    agents/elasticsearch_agent.py
│  (elasticsearch-specialist) │    Handles all retrieval logic
└────────────┬────────────┘
             │  knn vector search
             ▼
┌─────────────────────────┐
│    Elasticsearch Index   │  ← Knowledge Base
│    (rag_documents)       │    Dense vector embeddings via Gemini
└─────────────────────────┘
```

### Flow

1. User submits a natural language query to Windsurf Cascade
2. Cascade (orchestrator) invokes the `retrieve_documents` MCP tool with the query
3. The Elasticsearch specialist subagent generates a query embedding via **Gemini Embeddings API** (`gemini-embedding-001`)
4. The subagent runs a **kNN vector search** against the `rag_documents` index
5. Top-ranked document chunks (score ≥ 0.6, top-7) are returned to Cascade
6. Cascade synthesizes a grounded response using the retrieved context

---

## MCP Design

### Orchestrator
- **Windsurf Cascade** acts as the lead agent
- Handles user interaction, reasoning, and final response generation
- Delegates retrieval to the specialist via a single MCP tool call

### Specialist Subagent — `elasticsearch-specialist`
- Runs as a local MCP server via `stdio` transport
- Exposes one tool: `retrieve_documents(query: str) -> str`
- Handles embedding generation + vector search internally
- Returns ranked JSON chunks ready for LLM consumption

### MCP Config (`~/.codeium/windsurf/mcp_config.json`)
```json
{
  "mcpServers": {
    "elasticsearch-specialist": {
      "command": "python",
      "args": ["agents/elasticsearch_agent.py"]
    }
  }
}
```

---

## Stack

| Component | Technology |
|---|---|
| Orchestrator | Windsurf Cascade |
| MCP Framework | `mcp[cli]` 1.27.1 |
| Specialist Subagent | Python + FastMCP |
| Vector Search | Elasticsearch 8.x (`knn` query) |
| Embeddings | Gemini Embeddings API (`gemini-embedding-001`) |
| Transport | `stdio` (local dev) |

---

## Setup

### 1. Start Elasticsearch
```bash
docker run -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.13.0
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Add your GEMINI_API_KEY
```

### 4. Ingest documents
```bash
python ingest.py
```
Reads `.md` and `.txt` files, chunks them, generates embeddings, and indexes into Elasticsearch.

### 5. Add MCP server to Windsurf config
Add the `elasticsearch-specialist` entry to `~/.codeium/windsurf/mcp_config.json`, then fully restart Windsurf.

### 6. Query
Ask Windsurf Cascade any question — it will automatically invoke `retrieve_documents` and ground its response in your indexed documents.

---

## Key Implementation Details

- **Chunking**: 400-word chunks with 80-word overlap (`ingest.py`)
- **Embeddings**: Per-chunk at ingest time, stored as `dense_vector` in ES
- **Retrieval**: `knn` query with `num_candidates: 50`, filtered to `score ≥ 0.6`
- **Top-K**: 7 chunks returned per query
- **Transport**: `stdio` for local dev — switch to `sse` for networked/production deployment
