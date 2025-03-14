from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os

# Import search methods
from search.bm25_search import search_bm25
from search.unicoil_search import search_unicoil
from search.weaviate_dense_search import search_dense_weaviate
from search.weaviate_multivector_search import search_multivector_weaviate

app = FastAPI(
    title="Veterinary Learning Content Search API",
    description="API for searching veterinary learning content using multiple retrieval methods",
    version="0.1.0"
)

class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, str]] = None
    top_k: int = 10

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Welcome to the Veterinary Learning Content Search API"}

@app.post("/search/bm25", response_model=SearchResponse)
async def bm25_search(request: SearchRequest):
    try:
        results = search_bm25(request.query, request.filters, request.top_k)
        return {
            "results": results,
            "metadata": {
                "search_method": "BM25",
                "query": request.query,
                "filters": request.filters,
                "top_k": request.top_k
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/unicoil", response_model=SearchResponse)
async def unicoil_search(request: SearchRequest):
    try:
        results = search_unicoil(request.query, request.filters, request.top_k)
        return {
            "results": results,
            "metadata": {
                "search_method": "uniCOIL",
                "query": request.query,
                "filters": request.filters,
                "top_k": request.top_k
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/dense", response_model=SearchResponse)
async def dense_search(request: SearchRequest):
    try:
        results = search_dense_weaviate(request.query, request.filters, request.top_k)
        return {
            "results": results,
            "metadata": {
                "search_method": "Dense BGE-M3",
                "query": request.query,
                "filters": request.filters,
                "top_k": request.top_k
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/multivector", response_model=SearchResponse)
async def multivector_search(request: SearchRequest):
    try:
        results = search_multivector_weaviate(request.query, request.filters, request.top_k)
        return {
            "results": results,
            "metadata": {
                "search_method": "Multi-vector BGE-M3",
                "query": request.query,
                "filters": request.filters,
                "top_k": request.top_k
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/all")
async def search_all(request: SearchRequest):
    try:
        # Get results from all search methods
        bm25_results = search_bm25(request.query, request.filters, request.top_k)
        unicoil_results = search_unicoil(request.query, request.filters, request.top_k)
        dense_results = search_dense_weaviate(request.query, request.filters, request.top_k)
        multivector_results = search_multivector_weaviate(request.query, request.filters, request.top_k)
        
        # Store results for later analysis
        search_record = {
            "query": request.query,
            "filters": request.filters,
            "top_k": request.top_k,
            "bm25_results": bm25_results,
            "unicoil_results": unicoil_results,
            "dense_results": dense_results,
            "multi_vector_results": multivector_results
        }
        
        # Return combined results
        return {
            "bm25_results": bm25_results,
            "unicoil_results": unicoil_results,
            "dense_results": dense_results,
            "multi_vector_results": multivector_results,
            "metadata": {
                "query": request.query,
                "filters": request.filters,
                "top_k": request.top_k
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)