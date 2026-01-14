"""
Chunker module for splitting tender documents into clauses.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    """Represents a document chunk (clause)."""
    content: str
    index: int
    metadata: Dict[str, Any]
    token_count: Optional[int] = None

class ClauseChunker:
    """
    Chunks content based on clause patterns.
    For the MVP, we assume a simple Double Newline pattern or explicit separation logic provided by the parser.
    """
    def __init__(self):
        pass

    def chunk_document(self, content: str, base_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """
        Splits content into chunks based on clause heuristics.
        """
        # MVP Logic: Split by double newlines as a proxy for clauses
        # In a real scenario, this would use the parser's structural understanding
        
        raw_chunks = content.split("\n\n")
        chunks = []
        chunk_index = 0
        
        for raw in raw_chunks:
            cleaned_text = raw.strip()
            if not cleaned_text:
                continue
            
            # Basic validation: Skip very short noise
            if len(cleaned_text) < 5:
                continue

            # Heuristic: Try to find a clause number at the start?
            # For now, we generate a generic ID if none exists.
            
            chunk_metadata = base_metadata.copy()
            chunk_metadata["chunk_method"] = "clause_heuristic"
            
            # Simple clause numbering for now
            chunk_metadata["clause_number"] = f"GEN-{chunk_index+1}"
            
            chunks.append(DocumentChunk(
                content=cleaned_text,
                index=chunk_index,
                metadata=chunk_metadata,
                token_count=len(cleaned_text) // 4 # Rough approx
            ))
            chunk_index += 1
            
        return chunks
