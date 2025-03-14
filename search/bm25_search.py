from pyserini.search import LuceneSearcher
from typing import Dict, List, Optional, Any
import os
import json

# Path to the BM25 index
INDEX_PATH = os.environ.get("BM25_INDEX_PATH", "/app/indexes/bm25")

def search_bm25(query: str, filters: Optional[Dict[str, str]] = None, k: int = 10) -> List[Dict[str, Any]]:
    """
    Search using BM25 with optional metadata filtering.
    
    Args:
        query: The search query string
        filters: Optional dictionary of metadata filters (field:value)
        k: Number of results to return
        
    Returns:
        List of search results with document content and metadata
    """
    # Initialize the searcher
    searcher = LuceneSearcher(INDEX_PATH)
    
    # Construct filter query if filters are provided
    filter_query = None
    if filters and len(filters) > 0:
        filter_clauses = []
        for field, value in filters.items():
            filter_clauses.append(f"{field}:{value}")
        filter_query = " AND ".join(filter_clauses)
    
    # Perform the search
    if filter_query:
        hits = searcher.search(query, k=k, query_generator=None, filter_query=filter_query)
    else:
        hits = searcher.search(query, k=k)
    
    # Process results
    results = []
    for hit in hits:
        doc = json.loads(searcher.doc(hit.docid).raw())
        results.append({
            "id": doc.get("id", hit.docid),
            "score": hit.score,
            "contents": doc.get("contents", ""),
            "course_id": doc.get("course_id", ""),
            "activity_id": doc.get("activity_id", ""),
            "course_name": doc.get("course_name", ""),
            "activity_name": doc.get("activity_name", ""),
            "strand": doc.get("strand", "")
        })
    
    return results