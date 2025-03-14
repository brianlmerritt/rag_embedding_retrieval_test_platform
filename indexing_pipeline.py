import os
import json
import logging
from tqdm import tqdm
from typing import Dict, List, Any

# Import indexing functions
from indexing.pyserini_bm25_index import create_bm25_index
from indexing.pyserini_unicoil_index import create_unicoil_index
from indexing.weaviate_ingest import initialize_weaviate_schema, ingest_into_weaviate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Get environment variables
    data_path = os.environ.get("DATA_PATH", "/app/data/vet_moodle_dataset.jsonl")
    
    # Check if data file exists
    if not os.path.exists(data_path):
        logger.error(f"Data file not found: {data_path}")
        return
    
    # Load data
    logger.info(f"Loading data from {data_path}")
    documents = []
    with open(data_path, 'r') as f:
        for line in f:
            documents.append(json.loads(line))
    
    logger.info(f"Loaded {len(documents)} documents")
    
    # Create BM25 index
    logger.info("Creating BM25 index")
    create_bm25_index(documents)
    
    # Create uniCOIL index
    logger.info("Creating uniCOIL index")
    create_unicoil_index(documents)
    
    # Initialize Weaviate schema
    logger.info("Initializing Weaviate schema")
    initialize_weaviate_schema()
    
    # Ingest documents into Weaviate
    logger.info("Ingesting documents into Weaviate")
    for doc in tqdm(documents, desc="Ingesting documents"):
        ingest_into_weaviate(doc)
    
    logger.info("Indexing complete!")

if __name__ == "__main__":
    main()