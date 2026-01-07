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

# ... imports ...

class QueryRequest(BaseModel):
    message: str
    tender_id: str = "default_tender" # For now default, but really required
    interface: str = "API"

class QueryResponse(BaseModel):
    response: str
    query_id: str
    classification: str
    strategy: str
    status: str

# ... startup and ingest ...

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        # Use controller instead of direct agent call
        result = await controller.execute(
            tender_id=request.tender_id,
            query=request.message,
            interface=request.interface
        )
        
        if result.status == "REFUSED":
            # Just return the refusal as a valid response but with refusal info
             return QueryResponse(
                response=result.answer,
                query_id=result.query_id,
                classification=result.classification,
                strategy=result.strategy,
                status=result.status
            )
        
        return QueryResponse(
            response=result.answer,
            query_id=result.query_id,
            classification=result.classification,
            strategy=result.strategy,
            status=result.status
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AEC Tender RAG API is running"}
