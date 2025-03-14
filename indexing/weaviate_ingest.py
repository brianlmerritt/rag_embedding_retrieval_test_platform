import os
import weaviate
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Weaviate connection settings
WEAVIATE_HOST = os.environ.get("WEAVIATE_HOST", "weaviate")
WEAVIATE_PORT = os.environ.get("WEAVIATE_PORT", "8080")
WEAVIATE_URL = f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}"

# BGE-M3 model for embeddings
MODEL_NAME = "BAAI/bge-m3"
model = None
tokenizer = None

def get_model():
    global model, tokenizer
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    return model, tokenizer

def initialize_weaviate_schema():
    """Initialize Weaviate schema for both dense and multi-vector embeddings"""
    client = weaviate.Client(WEAVIATE_URL)
    
    # Check if classes already exist
    schema = client.schema.get()
    existing_classes = [c['class'] for c in schema['classes']] if schema.get('classes') else []
    
    # Create VetDocument class for dense embeddings if it doesn't exist
    if "VetDocument" not in existing_classes:
        vet_doc_class = {
            "class": "VetDocument",
            "description": "Veterinary learning content document with dense embedding",
            "vectorizer": "none",  # We'll provide our own vectors
            "properties": [
                {
                    "name": "contents",
                    "dataType": ["text"],
                    "description": "The textual content of the document"
                },
                {
                    "name": "course_id",
                    "dataType": ["string"],
                    "description": "Course identifier"
                },
                {
                    "name": "activity_id",
                    "dataType": ["string"],
                    "description": "Activity identifier"
                },
                {
                    "name": "course_name",
                    "dataType": ["string"],
                    "description": "Course name"
                },
                {
                    "name": "activity_name",
                    "dataType": ["string"],
                    "description": "Activity name"
                },
                {
                    "name": "strand",
                    "dataType": ["string"],
                    "description": "Learning strand"
                }
            ]
        }
        client.schema.create_class(vet_doc_class)
        logger.info("Created VetDocument class in Weaviate")
    
    # Create VetDocumentMultiVector class for multi-vector embeddings if it doesn't exist
    if "VetDocumentMultiVector" not in existing_classes:
        vet_multivec_class = {
            "class": "VetDocumentMultiVector",
            "description": "Veterinary learning content document with multi-vector embedding",
            "vectorizer": "none",  # We'll provide our own vectors
            "vectorIndexConfig": {
                "skip": False,
                "vectorCacheMaxObjects": 500000,
                "ef": 256,
                "efConstruction": 512,
                "maxConnections": 128,
                "multiVectorStorage": True  # Enable multi-vector storage
            },
            "properties": [
                {
                    "name": "contents",
                    "dataType": ["text"],
                    "description": "The textual content of the document"
                },
                {
                    "name": "course_id",
                    "dataType": ["string"],
                    "description": "Course identifier"
                },
                {
                    "name": "activity_id",
                    "dataType": ["string"],
                    "description": "Activity identifier"
                },
                {
                    "name": "course_name",
                    "dataType": ["string"],
                    "description": "Course name"
                },
                {
                    "name": "activity_name",
                    "dataType": ["string"],
                    "description": "Activity name"
                },
                {
                    "name": "strand",
                    "dataType": ["string"],
                    "description": "Learning strand"
                }
            ]
        }
        client.schema.create_class(vet_multivec_class)
        logger.info("Created VetDocumentMultiVector class in Weaviate")

def get_token_embeddings(text: str, model, tokenizer):
    """Generate token-level embeddings for multi-vector storage"""
    # Tokenize the text
    encoded_input = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors='pt'
    )
    
    # Get token embeddings
    with torch.no_grad():
        outputs = model(**encoded_input)
        token_embeddings = outputs.last_hidden_state
        
    # Average pool the token embeddings in chunks of 5 tokens
    # This reduces the number of vectors per document
    chunk_size = 5
    pooled_embeddings = []
    for i in range(0, token_embeddings.size(1), chunk_size):
        if i + chunk_size <= token_embeddings.size(1):
            chunk = token_embeddings[0, i:i+chunk_size, :]
            pooled = torch.mean(chunk, dim=0)
            pooled_embeddings.append(pooled.tolist())
    
    return pooled_embeddings

def ingest_into_weaviate(doc: Dict[str, Any]):
    """
    Ingest a document into Weaviate with both dense and multi-vector embeddings.
    
    Args:
        doc: Document dictionary with content and metadata
    """
    client = weaviate.Client(WEAVIATE_URL)
    model, tokenizer = get_model()
    
    # Get document text
    text = doc.get("contents", "")
    if not text:
        logger.warning(f"Skipping document {doc.get('id', 'unknown')} with empty content")
        return
    
    # Get dense document embedding
    dense_vector = model.encode(text).tolist()
    
    # Get token-level embeddings for multi-vector
    multi_vectors = get_token_embeddings(text, model.model, tokenizer)
    
    # Add document with dense embedding
    doc_id = doc.get("id", "")
    try:
        client.data_object.create(
            data_object={
                "contents": text,
                "course_id": doc.get("course_id", ""),
                "activity_id": doc.get("activity_id", ""),
                "course_name": doc.get("course_name", ""),
                "activity_name": doc.get("activity_name", ""),
                "strand": doc.get("strand", "")
            },
            class_name="VetDocument",
            uuid=doc_id,
            vector=dense_vector
        )
        logger.debug(f"Added document {doc_id} to VetDocument class")
    except Exception as e:
        logger.error(f"Error adding document {doc_id} to VetDocument class: {str(e)}")
    
    # Add document with multi-vector embedding
    try:
        client.data_object.create(
            data_object={
                "contents": text,
                "course_id": doc.get("course_id", ""),
                "activity_id": doc.get("activity_id", ""),
                "course_name": doc.get("course_name", ""),
                "activity_name": doc.get("activity_name", ""),
                "strand": doc.get("strand", "")
            },
            class_name="VetDocumentMultiVector",
            uuid=doc_id,
            vectors=multi_vectors
        )
        logger.debug(f"Added document {doc_id} to VetDocumentMultiVector class")
    except Exception as e:
        logger.error(f"Error adding document {doc_id} to VetDocumentMultiVector class: {str(e)}")