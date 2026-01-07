# AEC Tender RAG System

A **citation-first Retrieval-Augmented Generation (RAG) system** designed to support **estimators and engineers** working with complex AEC tender documentation.

The system enables accurate, traceable answers to contractual and technical questions, with strict enforcement of clause-level evidence.

---

## Problem Statement

AEC tender documents are:
- Large, fragmented, and clause-heavy
- Time-consuming to manually interrogate
- High-risk if misinterpreted or hallucinated by generic AI tools

Existing AI solutions prioritise fluency over correctness and provide answers without traceability—making them unsuitable for tender review.

---

## Solution Overview

This project implements a **deterministic, audit-ready RAG architecture** with the following guarantees:

- **Citation-first answers**: every answer is backed by explicit clause references
- **Clause integrity**: no cross-clause reasoning unless explicitly aggregated. This may change in later versions to enable comparison accross different documents and clauses
- **Single-tender scope (MVP)**: eliminates cross-document leakage
- **Refusal by default**: if no supporting evidence is found, the system refuses to answer and flags it for human review
- **Full internal audit trail**: every retrieval and response is logged

The system will be designed for **local deployment**, with no external data leakage however for the MVP phase, it will use chatgpt to generate the embeddings and retrieve the relevant clauses with local databases

---

## Target Users

- Estimators
- Civil, Structural, and MEP Engineers
- Architects
- Construction Managers

Users are assumed to be:
- Technically competent
- Intolerant of speculative or untraceable answers

---

## High-Level Architecture
[CLI / API / Tests]
↓
Query Controller
↓
Agent (PydanticAI)
↓
Retrieval Tools
├── BM25 (Exact Clause Lookup)
├── Vector Search (Semantic)
└── Hybrid Retrieval

## Status

🚧 **In active development (MVP)**  
Current focus:
- Schema and storage setup
- Deterministic ingestion
- Retrieval tool contracts

---

## Non-Goals (MVP)

- Cross-tender comparison
- Automated compliance matrices
- Drawing OCR or interpretation
- Risk scoring or red-flagging
- Multi-agent reviews

