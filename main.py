"""SentimentScope — FastAPI app."""
import io
import csv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sys, os
sys.path.insert(0, os.path.dirname(__file__) + "/..")

from backend.services.llm_analyzer import analyze_text, analyze_batch
from backend.services.results_store import save_result, get_all_results, get_stats, clear_results

app = FastAPI(title="SentimentScope API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class TextRequest(BaseModel):
    text: str


class BatchRequest(BaseModel):
    texts: List[str]


@app.post("/api/analyze/text")
def analyze_single(req: TextRequest):
    result = analyze_text(req.text)
    return save_result(result)


@app.post("/api/analyze/batch")
def analyze_batch_endpoint(req: BatchRequest):
    if len(req.texts) > 50:
        raise HTTPException(status_code=400, detail="Max 50 texts per batch")
    results = analyze_batch(req.texts)
    return [save_result(r) for r in results]


@app.post("/api/analyze/csv")
async def analyze_csv(file: UploadFile = File(...), text_column: str = "text"):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    texts = [row[text_column] for row in reader if row.get(text_column)]
    if not texts:
        raise HTTPException(status_code=400, detail=f"No column '{text_column}' found in CSV")
    results = analyze_batch(texts[:100])  # cap at 100
    return [save_result(r) for r in results]


@app.get("/api/results")
def list_results():
    return {"results": get_all_results()}


@app.get("/api/stats")
def stats():
    return get_stats()


@app.delete("/api/results")
def clear():
    clear_results()
    return {"message": "All results cleared"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "SentimentScope"}
