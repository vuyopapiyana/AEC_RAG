from pathlib import Path
from uuid import uuid4
import asyncio
import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from src.db.models import Tender, Document, Clause, Chunk
from src.ingestion.parser import DocumentParser
from src.ingestion.chunker import ClauseChunker, DocumentChunk
from src.ingestion.embed import get_embedding
from src.db.graph_db import graph_db

class IngestionPipeline:
    def __init__(self):
        self.parser = DocumentParser()
        self.chunker = ClauseChunker()

    async def ingest_file(self, file_path: Path, tender_id: uuid4):
        session_gen = get_session()
        session: AsyncSession = await anext(session_gen)
        
        try:
            # 1. Parse Document (Get raw content)
            parsed_data = self.parser.parse(file_path)
            content = parsed_data["content"]
            metadata = parsed_data["metadata"]
            
            # 2. Create Document Record
            doc = Document(
                filename=metadata["filename"],
                tender_id=tender_id
            )
            session.add(doc)
            await session.commit()
            await session.refresh(doc)
            
            # 3. Chunk Content (Using new Chunker)
            # Add doc_id to metadata for convenient tracking if needed
            doc_metadata = metadata.copy()
            doc_metadata["document_id"] = str(doc.id)
            
            chunks: List[DocumentChunk] = self.chunker.chunk_document(content, doc_metadata)
            
            print(f"Generated {len(chunks)} chunks for {file_path.name}")

            for chunk_obj in chunks:
                # Create Clause (One chunk = One clause for this MVP)
                clause_number = chunk_obj.metadata.get("clause_number", f"GEN-{chunk_obj.index}")
                
                clause = Clause(
                    document_id=doc.id,
                    clause_number=clause_number,
                    content=chunk_obj.content,
                    title=f"Clause {clause_number}" 
                )
                session.add(clause)
                await session.commit()
                await session.refresh(clause)
                
                # Create Chunk & Embed
                embedding = await get_embedding(chunk_obj.content)
                
                db_chunk = Chunk(
                    clause_id=clause.id,
                    content=chunk_obj.content,
                    chunk_index=chunk_obj.index,
                    embedding=embedding
                    # metadata=json.dumps(chunk_obj.metadata) # If we add metadata column to Chunk table later
                )
                session.add(db_chunk)
                
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
