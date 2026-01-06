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

class QueryRequest(BaseModel):
    message: str

class QueryResponse(BaseModel):
    response: str

@app.on_event("startup")
async def on_startup():
    await init_db()

# ... (ingest and query endpoints remain)

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
        
    # Trigger ingestion in background
    # Note: run_ingestion is async, so we wrap it or just await it if we want result immediately.
    # For better UX we should use BackgroundTasks but we need to run asyncio.run equivalent inside it or strictly use async function.
    # FastAPI BackgroundTasks supports async functions.
    
    background_tasks.add_task(run_ingestion, str(file_path), tender_name)
    
    return {"message": f"Ingestion started for {file.filename} under tender {tender_name}"}

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        response = await agent.ask(request.message)
        return QueryResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AEC Tender RAG API is running"}
