# Initial Feature Request – AEC Tender RAG System

## 1. Purpose

This document defines the **initial product requirements (PRD)** for an internal, locally hosted **Retrieval-Augmented Generation (RAG) system** designed to support **Estimators and Engineers** working with **AEC tender documents**.

The system must provide **accurate, citation-backed answers** to technical and commercial questions arising from tender documentation, with strict traceability and no unsupported outputs.

---

## 2. Target Users

### Primary Users
- **Estimators**
- **Engineers** (Civil, Structural, MEP)

### User Characteristics
- Technically competent
- Familiar with clause-based contracts
- Require speed, accuracy, and traceability
- Low tolerance for hallucinated or speculative answers

---

## 3. Core Principles

1. **Citation-first**: The system must refuse to answer if no supporting source is found.
2. **Clause integrity**: Answers must respect contractual clause boundaries.
3. **Single-tender scope (MVP)**: Queries are scoped to one selected tender.
4. **Technical tone**: Responses must be written in professional, engineering-style language.
5. **Auditability**: All retrieved content must be logged internally.

---

## 4. High-Level Architecture

### API Layer
- FastAPI
- Server-Sent Events (SSE) for streaming responses

### Agent Layer
- PydanticAI Agent
- Typed tool interfaces
- Deterministic orchestration

### Storage & Retrieval
- PostgreSQL
  - Metadata
  - Clause text
  - Tables (Markdown / JSON)
- pgvector
  - Semantic embeddings
- BM25 (Postgres full-text search)
- Neo4j (Graphiti)
  - Clause relationships and references

### Ingestion
- Docling for document parsing
- Clause-aware chunking
- Sentence overlap within clauses

---

## 5. Document Model

### Tender
- `tender_id`
- `tender_name`
- `source_folder`
- `version`
- `ingested_at`

### Document
- `document_id`
- `tender_id`
- `document_type` (Conditions, Scope, BOQ, Drawings, etc.)
- `discipline`

### Clause
- `clause_id` (e.g. 8.7.1)
- `document_id`
- `parent_clause_id`
- `page_number`
- `content`

### Chunk
- `chunk_id`
- `clause_id`
- `content`
- `embedding`

---

## 6. Feature Set (MVP)

### 6.1 Tender Ingestion

**Description**
- Ingest all documents within a selected tender folder.
- Parse into structured Markdown.
- Preserve clause hierarchy, tables, and page references.

**Acceptance Criteria**
- Each tender is independently indexed.
- Clause numbers and titles are preserved.
- Tables are stored separately but linked to parent clauses.

---

### 6.2 Tender Selection

**Description**
- User selects one active tender for querying.

**Acceptance Criteria**
- All retrieval is scoped to the selected tender.
- No cross-tender retrieval occurs.

---

### 6.3 Clause Lookup (Exact)

**Example Questions**
- "What does Clause 4.3 say?"
- "Show Appendix C"

**Retrieval Strategy**
- BM25 (PostgreSQL full-text search)

**Behavior**
- Retrieve exact clause(s).
- Summarize only if requested.

---

### 6.4 Semantic Question Answering

**Example Questions**
- "What penalties apply for late completion?"
- "Who is responsible for temporary works?"

**Retrieval Strategy**
- Vector search (pgvector)
- Clause-scoped chunk retrieval

**Behavior**
- Aggregate evidence from relevant clauses.
- Answer must include citations.

---

### 6.5 Hybrid Retrieval

**Use Cases**
- Ambiguous wording
- Mixed identifier + semantic queries

**Retrieval Strategy**
- Parallel BM25 + Vector
- Reranking by relevance

---

### 6.6 Table Handling

**Capabilities**
- Retrieve tables verbatim
- Summarize tables on request

**Example Questions**
- "Show the BOQ for electrical works"
- "Summarize the provisional sums"

---

### 6.7 Citation Enforcement

**Rules**
- If no supporting clause is found, the system must refuse to answer.
- All answers must list clause number(s) and page number(s).

**User Output Example**
```
Liquidated damages apply at ZAR 50,000 per calendar day.

Source:
- Clause 8.7.1, Page 132
```

---

### 6.8 Internal Logging (Non-User Visible)

**Logged Data**
- Retrieved chunk IDs
- Clause IDs
- Retrieval method used
- LLM prompt and response

**Purpose**
- Debugging
- Audit trail
- Model evaluation

---

## 7. Graph-Based Capabilities (Early / Partial)

### Included in MVP (Backend Only)
- Clause-to-clause references
- Clause-to-table relationships

### Not Exposed to User Yet
- Dependency exploration UI
- Conflict detection

---

## 8. Non-Functional Requirements

- **Accuracy > latency**
- Deterministic responses
- Local deployment support
- Dockerized services
- No external data leakage

---

## 9. Explicit Out of Scope (MVP)

- Cross-tender comparison
- Automated compliance matrices
- Drawing OCR and interpretation
- Risk scoring or red-flagging
- Multi-agent reviews

---

## 10. Future Roadmap (Post-MVP)

- Compliance checking (mandatory submissions, requirements)
- Cross-tender clause comparison
- Clause conflict detection
- Estimator-focused cost-risk extraction
- Graph-based query UI

---

## 11. Success Criteria

- Users can reliably extract contractual answers with citations
- Zero hallucinated answers
- Improved tender review speed for estimators and engineers

