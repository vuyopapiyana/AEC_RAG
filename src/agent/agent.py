"""
Tender Agent using PydanticAI Agent and RunContext.
"""
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from src.retrieval.search import SearchEngine
from .prompts import SYSTEM_PROMPT
from .tools import (
    lookup_clause_tool,
    search_tender_tool,
    ClauseLookupInput,
    TenderSearchInput
)

# --- Dependencies (injected via RunContext) ---

@dataclass
class AgentDependencies:
    tender_id: str
    strategy: str
    search_engine: SearchEngine

# --- Agent Definition ---

tender_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=AgentDependencies,
    system_prompt=SYSTEM_PROMPT,
)

# --- Tools Registration ---

@tender_agent.tool
async def lookup_clause(ctx: RunContext[AgentDependencies], clause_number: str) -> str:
    """
    Look up a specific contractual clause by its number.
    Use this when the user asks about a specific clause like 'Clause 5.1' or 'Section 3.2'.
    """
    # Adapter to use the structured tool function
    return await lookup_clause_tool(ctx, ClauseLookupInput(clause_number=clause_number))

@tender_agent.tool
async def search_tender(ctx: RunContext[AgentDependencies], query: str) -> str:
    """
    Semantically search the tender documents for technical specifications, requirements, or general information.
    Use this for open-ended questions about the tender content.
    """
    # Adapter to use the structured tool function
    return await search_tender_tool(ctx, TenderSearchInput(query=query))


# --- Agent Wrapper for Controller Integration ---

class TenderAgentWrapper:
    def __init__(self):
        self.search_engine = SearchEngine()

    async def ask_with_strategy(self, query: str, tender_id: str, strategy: str) -> str:
        dependencies = AgentDependencies(
            tender_id = tender_id,
            strategy = strategy,
            search_engine = self.search_engine
        )
        
        result = await tender_agent.run(query, deps = dependencies)
        return result.data

    async def ask(self, query: str) -> str:
        return await self.ask_with_strategy(query, "default_tender", "HYBRID")

# Global instance for the controller
agent = TenderAgentWrapper()
