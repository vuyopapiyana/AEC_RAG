import re
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from src.agent.agent import agent
from src.db.models import Clause

# --- Enums & Models ---

class QueryClassification(str, Enum):
    EXACT = "EXACT"
    SEMANTIC = "SEMANTIC"
    HYBRID = "HYBRID"

class RetrievalStrategy(str, Enum):
    BM25 = "BM25"       # Keyword/Exact match
    VECTOR = "VECTOR"   # Semantic embedding search
    HYBRID = "HYBRID"   # Combined

class QueryContext(BaseModel):
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tender_id: str
    raw_query: str
    interface_source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    classification: Optional[QueryClassification] = None
    strategy: Optional[RetrievalStrategy] = None
    log_status: str = "OPEN"
    refusal_reason: Optional[str] = None
    agent_response: Optional[str] = None

class ControllerResponse(BaseModel):
    query_id: str
    answer: str
    classification: str
    strategy: str
    status: str

# --- Controller Implementation ---

class QueryController:
    """
    Deterministic governance layer.
    Enforces policies, invariants, and audit logging.
    """

    def _validate_preconditions(self, tender_id: str, query: str) -> bool:
        """
        Hard gates:
        - tender_id must be provided
        - query must be non-empty
        """
        if not tender_id:
            return False
        if not query or not query.strip():
            return False
        # In a real app, check if tender exists in DB here
        return True

    def _classify_query(self, query: str) -> QueryClassification:
        """
        Deterministic classification based on regex patterns.
        """
        # EXACT strategy patterns:
        # e.g., "Clause 5.1", "Section 3.2.1", "Appendix A"
        exact_pattern = r"(?i)\b(clause|section|appendix)\s+\d+(\.\d+)*"
        
        if re.search(exact_pattern, query):
            # If it looks like a specific clause reference, treat as EXACT (or HYBRID if complex)
            # For strict determinism, let's say purely numeric references are EXACT.
            # "Clause 5.1" -> EXACT
            # "What does Clause 5.1 say about X" -> HYBRID? 
            # For MVP simplicity: Presence of clause ref -> EXACT (prioritize lookup)
            return QueryClassification.EXACT
        
        # Default to SEMANTIC
        return QueryClassification.SEMANTIC

    def _select_strategy(self, classification: QueryClassification) -> RetrievalStrategy:
        """
        Map classification to retrieval strategy.
        """
        if classification == QueryClassification.EXACT:
            return RetrievalStrategy.BM25 # Use keyword/clause lookup
        elif classification == QueryClassification.SEMANTIC:
            return RetrievalStrategy.VECTOR
        else:
            return RetrievalStrategy.HYBRID

    def _create_log_record(self, ctx: QueryContext):
        """
        Mock logging function. In production, write to DB/CloudWatch.
        """
        print(f"[AUDIT LOG] ID={ctx.query_id} TENDER={ctx.tender_id} TYPE={ctx.classification} STRAT={ctx.strategy} QUERY='{ctx.raw_query}'")

    def _validate_response(self, response: str, ctx: QueryContext):
        """
        Post-agent validation.
        Check for citations if answer is factual.
        """
        # MVP: Simple check - if response is not a refusal, it should ideally have some indication of source.
        # But asking the agent to handle citations is better.
        # We can enforce "Clause X" appears in text if strategy was EXACT.
        pass

    async def execute(self, tender_id: str, query: str, interface: str = "API") -> ControllerResponse:
        # 1. Validate
        if not self._validate_preconditions(tender_id, query):
            return ControllerResponse(
                query_id="N/A",
                answer="Invalid Request: Missing tender_id or empty query.",
                classification="REJECTED",
                strategy="NONE",
                status="REFUSED"
            )

        # 2. Context & Classification
        ctx = QueryContext(
            tender_id=tender_id,
            raw_query=query,
            interface_source=interface
        )
        ctx.classification = self._classify_query(query)
        ctx.strategy = self._select_strategy(ctx.classification)
        
        # 3. Log Start
        self._create_log_record(ctx)

        # 4. Invoke Agent
        # Agent implementation needs to handle explicit strategy strategies
        try:
            answer = await agent.ask_with_strategy(
                query=query, 
                tender_id=tender_id, 
                strategy=ctx.strategy.value
            )
            ctx.agent_response = answer
            ctx.log_status = "ANSWERED"
        except Exception as e:
            ctx.refusal_reason = str(e)
            ctx.log_status = "ERROR"
            ctx.agent_response = "I encountered an error processing your request."
            print(f"[ERROR] {e}")

        # 5. Finalize
        # self._validate_response(ctx.agent_response, ctx) # (Optional strict check)
        
        return ControllerResponse(
            query_id=ctx.query_id,
            answer=ctx.agent_response,
            classification=ctx.classification.value,
            strategy=ctx.strategy.value,
            status=ctx.log_status
        )

# Global instance
controller = QueryController()
