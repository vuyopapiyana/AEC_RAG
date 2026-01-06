# TENDER_RAG_PLAN.md

## 1. Objective

This document defines a **comprehensive implementation plan** for the AEC Tender RAG System described in `initial.md`. The goal is to translate the product requirements into **actionable engineering tasks**, **recommended design patterns**, and **supporting resources** suitable for guiding an AI coding assistant and human developers.

The plan prioritises:
- Determinism and auditability
- Contractual clause integrity
- Citation-enforced outputs
- Local, production-grade deployment

---

## 2. Requirements Analysis

### 2.1 Functional Requirements

| Area | Requirement | Implication |
|----|----|----|
| Retrieval | BM25, vector, and hybrid retrieval | Multi-index strategy with orchestration |
| Scope | Single-tender querying (MVP) | Strict tenant-style scoping in queries |
| Accuracy | Citation-first, refusal on no evidence | Guardrails at agent level |
| Structure | Clause- and table-aware parsing | Custom ingestion + schema design |
| Logging | Full internal traceability | Persistent retrieval + prompt logs |
| UX | Technical, engineering-style answers | Prompt constraints and output schema |

### 2.2 Non-Functional Requirements

| Category | Requirement | Design Response |
|----|----|----|
| Determinism | Repeatable outputs | Fixed retrieval sizes, temperature=0 |
| Security | Local-only, no leakage | No external APIs beyond LLM runtime |
| Performance | Accuracy > latency | Multi-step retrieval acceptable |
| Maintainability | Modular services | Clear service boundaries |

---

## 3. Recommended Architecture Patterns

### 3.1 Overall Pattern

**Layered RAG Architecture with Deterministic Agent Orchestration**

```
[API]
  └── Query Controller (FastAPI)
        └── Agent Orchestrator (PydanticAI)
              ├── Clause Lookup Tool (BM25)
              ├── Semantic Retrieval Tool (pgvector)
              ├── Hybrid Reranker
              └── Citation Validator
                    └── Answer Composer
```

Key design choice: **The LLM never retrieves data directly**. All retrieval is tool-driven and logged.

---

## 4. Detailed Implementation Plan

### Phase 0 – Foundations

#### Tasks
- Define repository structure (api / ingestion / retrieval / agent / storage / logging)
- Set up Docker Compose (Postgres + pgvector + Neo4j + API)
- Configure environment management (.env, secrets)

#### Resources
- Docker Compose best practices
- 12-factor app principles

---

### Phase 1 – Data Model & Storage

#### Tasks
1. Implement PostgreSQL schema
   - tender
   - document
   - clause
   - chunk
   - table
2. Enable pgvector extension
3. Define SQLAlchemy models + migrations
4. Design Neo4j schema
   - (:Clause)-[:REFERENCES]->(:Clause)
   - (:Clause)-[:HAS_TABLE]->(:Table)

#### Design Notes
- Clause IDs must be globally unique *within a tender*
- Never embed across tender boundaries

---

### Phase 2 – Ingestion Pipeline

#### Tasks
1. Folder-based tender ingestion
2. Parse documents using Docling
3. Convert to structured Markdown
4. Clause hierarchy extraction
5. Table extraction and linkage
6. Clause-aware chunking
   - Sentence overlap
   - No cross-clause chunks
7. Generate embeddings per chunk
8. Persist all artefacts

#### Best Practices
- Deterministic chunk sizes
- Stable clause numbering
- Store raw parsed output for reprocessing

---

### Phase 3 – Retrieval Layer

#### Tasks

**BM25 Retrieval**
- PostgreSQL full-text search on:
  - clause_id
  - clause title
  - clause content

**Vector Retrieval**
- pgvector similarity search
- Filter by tender_id
- Limit results per clause

**Hybrid Retrieval**
- Parallel execution
- Weighted score merge
- Optional reranking step

#### Output Contract
Each retrieval tool must return:
- clause_id
- page_number
- chunk_id(s)
- relevance score

---

### Phase 4 – Agent & Tooling

#### Tasks
1. Implement PydanticAI agent
2. Define strict tool schemas
3. Query classification
   - Exact clause lookup
   - Semantic question
   - Hybrid
4. Tool invocation logic
5. Evidence aggregation
6. Citation validation gate
7. Refusal logic if evidence < threshold

#### Design Pattern
**Evidence-First Answering**
- LLM sees only retrieved content
- No open-ended generation

---

### Phase 5 – Answer Composition

#### Tasks
- Structured prompt template
- Enforced output format
- Engineering tone
- Citation block generation

#### Output Rules
- Every factual claim must map to a clause
- No inferred obligations
- No legal interpretation beyond text

---

### Phase 6 – Internal Logging & Audit

#### Tasks
- Persist retrieval traces
- Store prompts and responses
- Capture refusal reasons
- Add correlation IDs per query

#### Usage
- Debugging
- Accuracy audits
- Model evaluation

---

### Phase 7 – API Layer

#### Tasks
- FastAPI endpoints
  - /ingest
  - /select-tender
  - /query
- SSE streaming responses
- Error handling and refusals

---

## 5. AI Coding Assistant Task Decomposition

The AI coding assistant should be guided to:

1. Generate schemas and migrations
2. Implement ingestion modules incrementally
3. Build retrieval tools with strict I/O contracts
4. Write deterministic unit tests
5. Enforce citation validation logic
6. Avoid end-to-end generation shortcuts

Each task should be:
- Small
- Testable
- Deterministic

---

## 6. Testing Strategy

### Required Tests
- Clause lookup accuracy
- Tender isolation
- Citation completeness
- Refusal on no evidence
- Deterministic repeatability

### Test Data
- Synthetic tender
- Known clause questions

---

## 7. Risks & Mitigations

| Risk | Mitigation |
|----|----|
| Hallucination | Citation gate + refusal |
| Clause leakage | Tender-scoped filters |
| Poor parsing | Store raw + reprocess |
| Over-retrieval | Clause-level aggregation |

---

## 8. Deliverables

- Fully ingested tender index
- Queryable RAG API
- Logged, auditable answers
- Deterministic behaviour

---

## 9. Alignment With Success Criteria

This plan directly supports:
- Zero hallucinated answers
- Faster tender review
- High estimator and engineer trust

---

**End of Document**

