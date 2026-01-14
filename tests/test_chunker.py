import pytest
from src.ingestion.chunker import ClauseChunker, DocumentChunk

def test_chunker_basic_split():
    chunker = ClauseChunker()
    content = """Clause 1
This is the first clause.

Clause 2
This is the second clause.

Clause 3
This is the third clause."""
    
    metadata = {"filename": "test.md"}
    chunks = chunker.chunk_document(content, metadata)
    
    assert len(chunks) == 3
    assert chunks[0].content.startswith("Clause 1")
    assert chunks[1].content.startswith("Clause 2")
    assert chunks[2].content.startswith("Clause 3")
    
    # Verify metadata preservation
    assert chunks[0].metadata["filename"] == "test.md"
    assert chunks[0].metadata["chunk_method"] == "clause_heuristic"

def test_chunker_empty_input():
    chunker = ClauseChunker()
    chunks = chunker.chunk_document("", {})
    assert len(chunks) == 0

def test_chunker_small_noise():
    chunker = ClauseChunker()
    content = "a\n\nvalid clause"
    chunks = chunker.chunk_document(content, {})
    # 'a' (length 1) should be filtered out by < 5 char check
    assert len(chunks) == 1
    assert chunks[0].content == "valid clause"
