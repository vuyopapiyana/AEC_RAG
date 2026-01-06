from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, text
from src.db.database import get_session
from src.db.models import Chunk, Clause
from src.ingestion.embed import get_embedding

class SearchEngine:
    async def search_vector(self, query: str, limit: int = 5) -> List[Chunk]:
        embedding = await get_embedding(query)
        session_gen = get_session()
        session = await anext(session_gen)
        
        try:
            # Using pgvector's l2_distance or cosine_distance
            # NOTE: pgvector uses <-> for L2 distance, <=> for cosine distance
            stmt = select(Chunk).order_by(Chunk.embedding.cosine_distance(embedding)).limit(limit)
            result = await session.execute(stmt)
            chunks = result.scalars().all()
            return chunks
        finally:
            await session.close()
            
    async def search_clause(self, clause_number: str, tender_id: Optional[UUID] = None) -> List[Clause]:
        session_gen = get_session()
        session = await anext(session_gen)
        
        try:
            stmt = select(Clause).where(Clause.clause_number == clause_number)
            # Todo: join with Document -> Tender to filter by tender_id if provided
            result = await session.execute(stmt)
            clauses = result.scalars().all()
            return clauses
        finally:
            await session.close()

    async def hybrid_search(self, query: str) -> List[Chunk]:
        # For MVP, we'll just run vector search. 
        # Full hybrid requires full-text search setup on Postgres side which takes more DDL.
        return await self.search_vector(query)
