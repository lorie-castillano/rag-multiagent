# RAG Multiagent System — Todo

**Architecture**: Windsurf Cascade (orchestrator) + Elasticsearch MCP Server (specialist subagent)

---

## Step 1 — Set Up Elasticsearch Instance *(can run in parallel with Step 2)*
- [x] Run local Elasticsearch via Docker (`docker run -p 9200:9200 elasticsearch:8.x`)
- [x] Verify connectivity: `curl http://localhost:9200`
- **Estimated time**: ~30 minutes
- **Depends on**: —

## Step 2 — Configure MCP for ES Subagent in mcp_config.json *(can run in parallel with Step 1)*
- [x] Add MCP server entry to `/Users/loriecastillano/.codeium/windsurf/mcp_config.json`
- [x] Configure transport (`stdio` for local dev)
- [x] Define capabilities: `retrieve_documents`
- **Estimated time**: ~15 minutes
- **Depends on**: —

## Step 3 — Implement Elasticsearch Specialist Subagent
- [x] Create `agents/elasticsearch_agent.py` in project directory
- [x] Implement `retrieve_documents(query)` tool using `elasticsearch-py`
- [x] Return ranked document chunks in MCP-compatible response format
- [x] Add `requirements.txt` with `mcp`, `elasticsearch`, etc.
- **Estimated time**: ~1 hour 30 minutes
- **Depends on**: Step 2

## Step 4 — Ingest Sample Data into Elasticsearch
- [x] Prepare sample documents (Markdown, text) as knowledge base
- [x] Write and run Python ingestion script to create index and load documents
- [x] Verify documents are indexed and searchable
- **Estimated time**: ~45 minutes
- **Depends on**: Step 1

## Step 5 — Build Cascade Orchestrator RAG Workflow
- [x] Create main Cascade RAG workflow script
- [x] Pattern: `user query → Cascade → ES subagent → retrieved chunks → LLM → response`
- [x] Handle context window limits (chunk size, top-k results)
- [x] Create `.windsurf/workflows/rag_query.md` workflow file
- **Estimated time**: ~2 hours
- **Depends on**: Steps 2, 3

## Step 6 — Start MCP Server + Cascade App
- [x] Start MCP server process (loads `mcp_config.json`, registers ES subagent)
- [x] Start Windsurf Cascade and confirm subagent is recognized
- [x] Test a basic tool call from Cascade to the subagent
- **Estimated time**: ~15 minutes
- **Depends on**: Steps 3, 5

## Step 7 — Test End-to-End RAG System
- [x] Send test queries through the full workflow
- [x] Verify ES retrieval via MCP invocation logs
- [x] Validate LLM responses are grounded in retrieved context
- [x] Tune chunk size, top-k, and index mappings as needed
- **Estimated time**: ~1 hour
- **Depends on**: Steps 4, 6

---

## Notes
- Total estimated time: **~6 hours 15 minutes**
- Steps 1 & 2 are independent and can be done simultaneously
- LLM integration handled by Cascade (no separate LLM service needed)
- Keep ES index mappings aligned with document structure for best retrieval quality
- Use `stdio` MCP transport for local dev, `sse` for production/networked setup
