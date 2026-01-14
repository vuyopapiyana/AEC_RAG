import pytest
from uuid import uuid4
from src.db.models import Tender, Document, Clause, Chunk, Table, Session, Message

def test_tender_model_creation():
    tender = Tender(name="Test Tender", description="A test tender", metadata_={"key": "value"})
    assert tender.name == "Test Tender"
    assert tender.metadata_["key"] == "value"
    assert tender.id is not None

def test_document_model_creation():
    tender_id = uuid4()
    doc = Document(filename="test.md", tender_id=tender_id)
    assert doc.filename == "test.md"
    assert doc.tender_id == tender_id
    assert doc.id is not None

def test_clause_model_creation():
    doc_id = uuid4()
    clause = Clause(
        document_id=doc_id,
        clause_number="1.0",
        content="This is a clause.",
        title="Test Clause"
    )
    assert clause.clause_number == "1.0"
    assert clause.content == "This is a clause."
    assert clause.document_id == doc_id

def test_chunk_model_creation():
    clause_id = uuid4()
    embedding = [0.1] * 1536 
    
    chunk = Chunk(
        clause_id=clause_id,
        content="Chunk content",
        chunk_index=0,
        embedding=embedding
    )
    assert chunk.clause_id == clause_id
    assert chunk.content == "Chunk content"
    assert chunk.chunk_index == 0
    assert len(chunk.embedding) == 1536

def test_session_message_creation():
    session = Session(user_id="user123")
    assert session.user_id == "user123"
    assert session.id is not None
    
    msg = Message(
        session_id=session.id,
        role="user",
        content="Hello world"
    )
    assert msg.session_id == session.id
    assert msg.role == "user"
    assert msg.content == "Hello world"
