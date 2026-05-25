# A2A + MCP Prototype: Resume Analyzer + Job Matcher Agents

Build two cooperating A2A agents within the rag-multiagent project: a Resume Analyzer that extracts skills from Lorie's resume, and a Job Matcher that finds matching remote jobs via vector search. Agents communicate via Google's A2A protocol while remaining compatible with the existing MCP-based Windsurf Cascade orchestrator.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User (you)                                 │
│                 "Find jobs matching my skills"                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         Orchestrator Agent (MCP + A2A Client)               │
│              Windsurf Cascade or custom agent               │
│         - Receives user query                                 │
│         - Speaks A2A to delegate to specialist agents         │
└───────────────────────┬─────────────────────────────────────┘
                        │ A2A Protocol (HTTP/JSON-RPC/SSE)
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌───────────────────┐       ┌───────────────────┐
│ Resume Analyzer   │       │   Job Matcher     │
│   Agent (A2A)     │◄─────►│   Agent (A2A)     │
│                   │  A2A  │                   │
│ - A2A Server      │       │ - A2A Server      │
│ - MCP Client to   │       │ - MCP Client to   │
│   retrieve resume │       │   ES for jobs     │
│ - Extracts skills │       │ - Matches skills  │
│ - Returns skills  │       │   to job listings │
│   via A2A         │       │ - Returns matches │
│                   │       │   via A2A         │
└───────────────────┘       └───────────────────┘
        │                               │
        └───────────────┬───────────────┘
                        │
                Reuses existing
                MCP elasticsearch-
                specialist for data
```

**Key Insight**: MCP and A2A are complementary:
- **MCP** = agent-to-tool (how agents access data/tools like Elasticsearch)
- **A2A** = agent-to-agent (how agents delegate work to each other)

---

## Step-by-Step Implementation Plan

### Step 1 — Learn A2A Protocol Fundamentals *(~2 hours)*
- [ ] Read A2A spec at https://github.com/google/A2A
- [ ] Understand core A2A concepts:
  - **Agent Card**: JSON metadata describing agent capabilities (skills, endpoint URL)
  - **Task**: The unit of work passed between agents
  - **Message**: Communication within a task (request/response/updates)
  - **Part**: Content pieces (text, file, data) within a message
- [ ] Study A2A vs MCP relationship:
  - MCP = standard for tools/resources (what we already have)
  - A2A = standard for agent delegation (what we're adding)
- [ ] Review A2A sample code from Google's repo

**Deliverable**: Document explaining A2A concepts using this project's Resume Analyzer + Job Matcher as concrete examples.

---

### Step 2 — Design Agent Interfaces *(~1 hour)*
Define what each agent does and their A2A Agent Cards.

**Resume Analyzer Agent**:
- **Skill**: `resume-analysis`
- **Input**: User ID or resume identifier
- **Output**: JSON list of extracted skills {skills: ["Python", "Django", ...]}
- **Uses internally**: MCP to call `retrieve_documents(query="Lorie's resume skills")`

**Job Matcher Agent**:
- **Skill**: `job-matching`
- **Input**: JSON list of skills
- **Output**: JSON list of matching jobs with relevance scores
- **Uses internally**: MCP to call `retrieve_documents(query="remote jobs Python Django")`

**Deliverable**: `agents/a2a/agent-cards/` directory with `resume-analyzer.json` and `job-matcher.json`.

---

### Step 3 — Set Up A2A Dependencies *(~1 hour)*
- [ ] Install Google's A2A Python SDK or use HTTP/JSON-RPC directly
- [ ] Add to `requirements.txt`:
  - `a2a` (if SDK available) OR `httpx`, `sse-starlette` for manual implementation
  - Keep existing `mcp`, `google-genai`, `elasticsearch`
- [ ] Create `agents/a2a/` directory structure:
  ```
  agents/a2a/
  ├── __init__.py
  ├── agent_cards/          # JSON agent descriptors
  ├── resume_analyzer/      # Resume Analyzer agent code
  │   ├── __init__.py
  │   ├── agent.py          # A2A server implementation
  │   └── main.py           # Entry point
  ├── job_matcher/          # Job Matcher agent code
  │   ├── __init__.py
  │   ├── agent.py
  │   └── main.py
  └── shared/               # Common A2A utilities
      ├── __init__.py
      ├── models.py         # Pydantic models for A2A types
      └── client.py         # A2A client for calling other agents
  ```

---

### Step 4 — Implement Resume Analyzer Agent *(~3 hours)*
Build the first A2A agent.

- [ ] Create `agents/a2a/resume_analyzer/agent.py`:
  - Implement A2A server (HTTP endpoint listening for A2A requests)
  - Handle `tasks/send` endpoint (A2A standard)
  - Parse incoming Task, extract intent
  - If intent is "analyze-resume":
    - Use internal MCP client to call `retrieve_documents(query="What skills does Lorie have?")`
    - Process returned chunks (extract skills from text)
    - Format skills as structured JSON
  - Return Task with result via A2A response

- [ ] Create `agents/a2a/resume_analyzer/main.py`:
  - Start A2A server on a port (e.g., 8001)
  - Expose Agent Card at `/.well-known/agent.json` (A2A standard)

- [ ] Test manually:
  ```bash
  curl -X POST http://localhost:8001/tasks/send \
    -H "Content-Type: application/json" \
    -d '{"skill": "resume-analysis", "input": {"user": "lorie"}}'
  ```

---

### Step 5 — Implement Job Matcher Agent *(~3 hours)*
Build the second A2A agent.

- [ ] Create `agents/a2a/job_matcher/agent.py`:
  - Implement A2A server on different port (e.g., 8002)
  - Handle `tasks/send` endpoint
  - If intent is "find-jobs":
    - Receive skills list from input
    - Use internal MCP client to call `retrieve_documents(query="remote jobs with [skills]")`
    - Rank and format job matches
  - Return Task with results

- [ ] Test manually with sample skills input.

---

### Step 6 — Implement A2A Client for Agent-to-Agent Communication *(~2 hours)*
This is the "glue" that lets agents call each other.

- [ ] Create `agents/a2a/shared/client.py`:
  - Implement A2A client that can:
    - Fetch Agent Card from `/.well-known/agent.json`
    - Send Task to another agent via HTTP POST
    - Handle SSE (Server-Sent Events) for streaming updates
    - Wait for and parse Task result

- [ ] Update Resume Analyzer to optionally call Job Matcher:
  - After extracting skills, if configured, use A2A client to call Job Matcher
  - Pass skills as input, receive job matches as output
  - Return combined result: {skills: [...], matching_jobs: [...]}

---

### Step 7 — Create A2A Orchestrator / Test Script *(~2 hours)*
Build a simple orchestrator that demonstrates both agents working together.

- [ ] Create `agents/a2a/orchestrator.py`:
  - This can be a CLI script or a simple HTTP server
  - Receives user query: "Find me jobs matching my skills"
  - Uses A2A client to call Resume Analyzer → gets skills
  - Uses A2A client to call Job Matcher with those skills → gets jobs
  - Formats and prints final answer to user

- [ ] Alternatively, extend Windsurf Cascade:
  - Create new workflow `.windsurf/workflows/a2a_job_match.md`
  - Cascade acts as A2A client, calls agents sequentially

---

### Step 8 — Integrate with Existing MCP Infrastructure *(~2 hours)*
Ensure A2A agents can use the existing Elasticsearch specialist.

- [ ] Each A2A agent needs its own MCP client configuration:
  - Resume Analyzer's `mcp_config.json` points to ES specialist
  - Job Matcher's `mcp_config.json` also points to ES specialist
  - Both agents reuse the same Elasticsearch index with your resume + job docs

- [ ] Verify data flow:
  1. User: "Find jobs for my skills"
  2. Resume Analyzer (A2A server) → calls ES specialist (MCP) → retrieves resume chunks
  3. Resume Analyzer extracts skills → returns via A2A
  4. Job Matcher (A2A server) receives skills → calls ES specialist (MCP) → retrieves job chunks
  5. Job Matcher returns matching jobs → via A2A
  6. Orchestrator presents combined result

---

### Step 9 — Test End-to-End A2A Flow *(~2 hours)*
- [ ] Start both A2A agents on different ports:
  ```bash
  python agents/a2a/resume_analyzer/main.py  # port 8001
  python agents/a2a/job_matcher/main.py        # port 8002
  ```
- [ ] Run orchestrator test:
  ```bash
  python agents/a2a/orchestrator.py "Find me remote jobs matching my Python skills"
  ```
- [ ] Verify:
  - Resume Analyzer correctly extracts skills from resume
  - Job Matcher finds relevant jobs based on those skills
  - A2A communication works (HTTP requests, JSON-RPC format)
  - Final answer combines both agents' outputs

---

### Step 10 — Document A2A + MCP Integration Learnings *(~1 hour)*
- [ ] Write `agents/a2a/README.md` explaining:
  - How MCP and A2A work together
  - Which agent does what
  - How to add more A2A agents
  - Architecture diagram
- [ ] Update main project `README.md` with A2A section
- [ ] Commit all code

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| A2A Transport | HTTP + JSON-RPC | Standard, simple, matches existing Python ecosystem |
| Agent Discovery | Static Agent Cards | For prototype, hardcode URLs; production would use registry |
| MCP Integration | Each A2A agent has internal MCP client | Clean separation: A2A = public API, MCP = private tools |
| Data Reuse | Use existing ES index with resume + jobs | No need to re-ingest; proves multi-protocol compatibility |
| Error Handling | Return Task with error status | A2A standard way to signal failures |

---

## Success Criteria

- [ ] Two A2A agents running on separate ports
- [ ] Agents can discover each other via Agent Cards
- [ ] Resume Analyzer extracts skills from resume via MCP → ES
- [ ] Job Matcher finds jobs via MCP → ES
- [ ] A2A client can call Resume Analyzer, get skills, call Job Matcher, get jobs
- [ ] End-to-end test returns combined result
- [ ] Documentation explains A2A + MCP relationship

---

## Time Estimate

**Total: ~18 hours** (can be done over multiple sessions)

| Step | Time |
|------|------|
| 1: Learn A2A | 2h |
| 2: Design | 1h |
| 3: Setup | 1h |
| 4: Resume Analyzer | 3h |
| 5: Job Matcher | 3h |
| 6: A2A Client | 2h |
| 7: Orchestrator | 2h |
| 8: MCP Integration | 2h |
| 9: Testing | 2h |
| 10: Documentation | 1h |

---

## What You Will Learn

1. **A2A Protocol**: HTTP endpoints, JSON-RPC, Agent Cards, Tasks, Messages
2. **MCP + A2A Together**: How two complementary protocols serve different purposes
3. **Multi-Agent Architecture**: Agent delegation, coordination, skill-based routing
4. **Agent Discovery**: How agents find and communicate with each other
5. **Error Handling**: How agents report failures and partial results

---

*Plan created: May 25, 2026*
*Suffix: b7e2a0*
