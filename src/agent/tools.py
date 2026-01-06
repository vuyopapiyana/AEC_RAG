from typing import List, Optional
from pydantic import BaseModel, Field
from src.retrieval.search import SearchEngine
from src.db.models import Chunk, Clause

search_engine = SearchEngine()

class ClauseLookupArgs(BaseModel):
    clause_number: str = Field(..., description="The clause number to look up, e.g., '5.1' or 'GEN-1'")

class SearchArgs(BaseModel):
    query: str = Field(..., description="The semantic query to search for technical specifications or requirements")

async def lookup_clause_tool(args: ClauseLookupArgs) -> str:
    """Tool to look up a specific clause by its number."""
    clauses = await search_engine.search_clause(args.clause_number)
    if not clauses:
        return "No clause found with that number."
    
    # Return formatted text
    results = []
    for c in clauses:
        results.append(f"Clause {c.clause_number}: {c.content}")
    return "\n---\n".join(results)

async def search_tool(args: SearchArgs) -> str:
    """Tool to search for information in the tender documents."""
    chunks = await search_engine.search_vector(args.query)
    if not chunks:
        return "No relevant information found."
    
    results = []
    for chunk in chunks:
        results.append(f"Content: {chunk.content}")
    return "\n---\n".join(results)
