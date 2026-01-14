"""
Tools for the Tender RAG agent.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from pydantic_ai import RunContext

# We need to import AgentDependencies, but it is defined in agent.py usually to avoid circular imports if agent imports tools.
# However, PydanticAI tools usually take a generic context. 
# We'll define the input models here.
# ideally AgentDependencies should stay in agent.py or a separate types.py.
# For now, we will use TYPE_CHECKING to avoid runtime circular import if we were to import AgentDependencies,
# but actually we can just rely on the context being passed at runtime and type it as Any or define a Protocol if needed.
# Better pattern: Define AgentDependencies in a separate file or keep it in agent.py and import it inside the function if needed,
# OR just don't type hint the specific Dependencies class here to keep it loose, OR (best) move AgentDependencies to a shared module.
# Let's try to keep it simple: We will NOT import AgentDependencies here to avoid circular dep with agent.py (which imports this).
# We will just assume ctx.deps has the attributes we need.

class ClauseLookupInput(BaseModel):
    """Input for looking up a specific clause."""
    clause_number: str = Field(..., description="The specific clause number to look up (e.g., '5.1', '10.2.3').")

class TenderSearchInput(BaseModel):
    """Input for semantic search of tender documents."""
    query: str = Field(..., description="The semantic search query.")

async def lookup_clause_tool(ctx: RunContext, input_data: ClauseLookupInput) -> str:
    """
    Look up a specific contractual clause by its number.
    """
    # Access dependencies dynamically to avoid circular imports
    search_engine = ctx.deps.search_engine
    
    clauses = await search_engine.search_clause(input_data.clause_number)
    
    if not clauses:
        return f"No clause found with number '{input_data.clause_number}'."
    
    results = []
    for c in clauses:
        results.append(f"Clause {c.clause_number}: {c.content}")
    return "\n---\n".join(results)

async def search_tender_tool(ctx: RunContext, input_data: TenderSearchInput) -> str:
    """
    Semantically search the tender documents.
    """
    dependencies = ctx.deps
    strategy = dependencies.strategy.upper()
    search_engine = dependencies.search_engine
    
    if strategy == "HYBRID":
        chunks = await search_engine.hybrid_search(input_data.query)
    elif strategy == "BM25":
         # Fallback to hybrid or vector since pure BM25 isn't fully implemented yet
        chunks = await search_engine.hybrid_search(input_data.query)
    else: 
        # Default to VECTOR
        chunks = await search_engine.search_vector(input_data.query)

    if not chunks:
        return "No relevant information found in the tender documents."
    
    results = []
    for chunk in chunks:
        results.append(f"Content: {chunk.content}")
    return "\n---\n".join(results)
