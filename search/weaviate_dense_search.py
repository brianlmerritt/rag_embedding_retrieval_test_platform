import weaviate
from typing import Dict, List, Optional, Any
import os
from sentence_transformers import SentenceTransformer

# Weaviate connection settings
WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST", "weaviate")
WEAVIATE_PORT = os.environ.get("WEAVIATE_PORT", "8080")
WEAVIATE_URL = f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}"

# BGE-M3 model for query embedding
MODEL_NAME = "BAAI/bge-m3"
model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    return model

def search_dense_weaviate(query: str, filters: Optional[Dict[str, str]] = None, k: int = 10) -> List[Dict[str, Any]]:
    """
    Search using dense BGE-M3 embeddings stored in Weaviate.
    
    Args:
        query: The search query string
        filters: Optional dictionary of metadata filters (field:value)
        k: Number of results to return
        
    Returns:
        List of search results with document content and metadata
    """
    # Initialize Weaviate client
    client = weaviate.Client(WEAVIATE_URL)
    
    # Generate query embedding
    model = get_model()
    query_vector = model.encode(query).tolist()
    
    # Prepare filter if provided
    where_filter = None
    if filters and len(filters) > 0:
        where_filter = {"operator": "And", "operands": []}
        for field, value in filters.items():
            where_filter["operands"].append({
                "path": [field],
                "operator": "Equal",
                "valueString": value
            })
    
    # Perform the search
    result = client.query.get(
        "VetDocument",
        ["id", "contents", "course_id", "activity_id", "course_name", "activity_name", "strand"]
    ).with_near_vector(
        {"vector": query_vector}
    ).with_where(
        where_filter
    ).with_limit(k).do()
    
    # Process results
    results = []
    if result and "data" in result and "Get" in result["data"] and "VetDocument" in result["data"]["Get"]:
        for doc in result["data"]["Get"]["VetDocument"]:
            results.append({
                "id": doc.get("id", ""),
                "score": doc.get("_additional", {}).get("score", 0.0),
                "contents": doc.get("contents", ""),
                "course_id": doc.get("course_id", ""),
                "activity_id": doc.get("activity_id", ""),
                "course_name": doc.get("course_name", ""),
                "activity_name": doc.get("activity_name", ""),
                "strand": doc.get("strand", "")
            })
    
    return results