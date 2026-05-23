---
description: RAG query — retrieve relevant documents from Elasticsearch and generate a grounded answer
---

## RAG Query Workflow

Given a user question, follow these steps in order:

### Step 1 — Retrieve
Call the `retrieve_documents` tool from the `elasticsearch-specialist` MCP server with the user's query as input.

### Step 2 — Evaluate Results
- If results are empty or no relevant chunks are found, respond: "I couldn't find relevant information in the knowledge base for your question."
- If results are found, proceed to Step 3.

### Step 3 — Generate Grounded Answer
Use the retrieved document chunks as context. Construct your answer by:
1. Grounding your response **only** in the retrieved content — do not rely on training data alone
2. Citing the source document (`source` field) for each key claim
3. Keeping the answer concise and directly addressing the user's question

### Step 4 — Format Response
Structure your response as:

**Answer:** [your grounded answer here]

**Sources used:**
- `[source filename]` — chunk [chunk_id], relevance score: [score]

---

## How to Invoke

Type `/rag_query` followed by your question. Example:

> `/rag_query What Python frameworks does Lorie have experience with?`

> `/rag_query What remote jobs were found matching a Senior Python Developer profile?`
