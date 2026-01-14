from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import shutil
import os
import asyncio
from pathlib import Path
from src.ingestion.pipeline import run_ingestion
from src.agent.agent import agent
from src.db.database import init_db

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AEC Tender RAG API")
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

from src.api.controller import controller

class QueryRequest(BaseModel):
    message: str
    tender_id: str = "default_tender"
    interface: str = "API"

class QueryResponse(BaseModel):
    response: str
    query_id: str
    classification: str
    strategy: str
    status: str

@app.on_event("startup")
async def on_startup():
    await init_db()

# ... (ingest remains)

@app.get("/")
async def root():
    return HTMLResponse(open("src/api/static/index.html").read())

@app.post("/ingest")
async def ingest_document(tender_name: str, file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    # Save uploaded file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    background_tasks.add_task(run_ingestion, str(file_path), tender_name)
    
    return {"message": f"Ingestion started for {file.filename} under tender {tender_name}"}

@app.post("/query", response_model=QueryResponse)
async def query_agent(full_query_request: QueryRequest):
    try:
        # Use controller instead of direct agent call
        result = await controller.execute(
            tender_id = full_query_request.tender_id,
            query = full_query_request.message,
            interface = full_query_request.interface
        )
    
        return QueryResponse(
            response = result.answer,
            query_id = result.query_id,
            classification = result.classification,
            strategy = result.strategy,
            status = result.status
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

