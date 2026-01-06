from pathlib import Path
from uuid import uuid4
import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.db.models import Tender, Document, Clause, Chunk
from src.ingestion.parser import DocumentParser
from src.ingestion.embed import get_embedding
from src.db.graph_db import graph_db

class IngestionPipeline:
    def __init__(self):
        self.parser = DocumentParser()

    async def ingest_file(self, file_path: Path, tender_id: uuid4):
        session_gen = get_session()
        session: AsyncSession = await anext(session_gen)
        
        try:
            # 1. Parse Document
            parsed_data = self.parser.parse(file_path)
            
            # 2. Create Document Record
            doc = Document(
                filename=parsed_data["metadata"]["filename"],
                tender_id=tender_id
            )
            session.add(doc)
            await session.commit()
            await session.refresh(doc)
            
            # 3. Extract and Process Clauses
            clauses_data = self.parser.chunk_clauses(parsed_data["content"])
            
            for c_data in clauses_data:
                # Create Clause
                clause = Clause(
                    document_id=doc.id,
                    clause_number=c_data["clause_number"],
                    content=c_data["content"],
                    title=c_data.get("title") # Parser might not extract this yet
                )
                session.add(clause)
                await session.commit()
                await session.refresh(clause)
                
                # Create Chunk & Embed
                # For this simple pipeline, 1 clause = 1 chunk for now, 
                # but we can sub-chunk if needed.
                embedding = await get_embedding(c_data["content"])
                
                chunk = Chunk(
                    clause_id=clause.id,
                    content=c_data["content"],
                    chunk_index=c_data["chunk_index"],
                    embedding=embedding
                )
                session.add(chunk)
                
                # 4. Neo4j Ingestion (Basic)
                self.ingest_graph(clause)
            
            await session.commit()
            print(f"Ingested {file_path.name} successfully.")
            
        except Exception as e:
            await session.rollback()
            print(f"Error ingesting {file_path}: {e}")
            raise e
        finally:
            await session.close()

    def ingest_graph(self, clause: Clause):
        # Basic graph node creation
        with graph_db.get_session() as session:
            session.run(
                """
                MERGE (c:Clause {id: $id})
                SET c.number = $number, c.content = $content
                """,
                id=str(clause.id),
                number=clause.clause_number,
                content=clause.content
            )

async def run_ingestion(file_path: str, tender_name: str):
    session_gen = get_session()
    session = await anext(session_gen)
    
    # Get or Create Tender
    from sqlalchemy import select
    res = await session.execute(select(Tender).where(Tender.name == tender_name))
    tender = res.scalar_one_or_none()
    
    if not tender:
        tender = Tender(name=tender_name)
        session.add(tender)
        await session.commit()
        await session.refresh(tender)
    
    await session.close()
    
    pipeline = IngestionPipeline()
    await pipeline.ingest_file(Path(file_path), tender.id)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python src/ingestion/pipeline.py <file_path> <tender_name>")
    else:
        asyncio.run(run_ingestion(sys.argv[1], sys.argv[2]))
