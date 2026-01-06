from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from pgvector.sqlalchemy import Vector

class Tender(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    client: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    documents: List["Document"] = Relationship(back_populates="tender")

class Document(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str
    tender_id: UUID = Field(foreign_key="tender.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    tender: Tender = Relationship(back_populates="documents")
    clauses: List["Clause"] = Relationship(back_populates="document")

class Clause(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="document.id")
    clause_number: str
    title: Optional[str] = None
    content: str
    page_number: Optional[int] = None
    
    document: Document = Relationship(back_populates="clauses")
    chunks: List["Chunk"] = Relationship(back_populates="clause")

class Chunk(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    clause_id: UUID = Field(foreign_key="clause.id")
    content: str
    chunk_index: int
    embedding: List[float] = Field(sa_type=Vector(1536))
    
    clause: Clause = Relationship(back_populates="chunks")

class Table(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    clause_id: UUID = Field(foreign_key="clause.id")
    caption: Optional[str] = None
    markdown_content: str
