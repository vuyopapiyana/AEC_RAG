from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Tender(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    client: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))
    
    documents: List["Document"] = Relationship(back_populates="tender")

class Document(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    filename: str
    tender_id: UUID = Field(foreign_key="tender.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))
    
    tender: Tender = Relationship(back_populates="documents")
    clauses: List["Clause"] = Relationship(back_populates="document")

class Clause(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    document_id: UUID = Field(foreign_key="document.id")
    clause_number: str
    title: Optional[str] = None
    content: str
    page_number: Optional[int] = None
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))
    
    document: Document = Relationship(back_populates="clauses")
    chunks: List["Chunk"] = Relationship(back_populates="clause")

class Chunk(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    clause_id: UUID = Field(foreign_key="clause.id")
    content: str
    chunk_index: int
    embedding: List[float] = Field(sa_type=Vector(1536))
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))
    
    clause: Clause = Relationship(back_populates="chunks")

class Table(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    clause_id: UUID = Field(foreign_key="clause.id")
    caption: Optional[str] = None
    markdown_content: str
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))

# Parsing/Chat State Models

class Session(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))
    
    messages: List["Message"] = Relationship(back_populates="session")

class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="session.id")
    role: str # 'user', 'assistant', 'system'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))
    
    session: Session = Relationship(back_populates="messages")
