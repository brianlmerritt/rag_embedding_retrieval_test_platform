import os
import json
import tempfile
import shutil
from typing import List, Dict, Any
from pyserini.index import IndexReader
from pyserini.index.lucene import LuceneIndexer
import logging

logger = logging.getLogger(__name__)

def create_bm25_index(documents: List[Dict[str, Any]]) -> None:
    """
    Create a BM25 index using Pyserini from the provided documents.
    
    Args:
        documents: List of document dictionaries
    """
    # Create output directory if it doesn't exist
    output_dir = os.environ.get("BM25_INDEX_PATH", "/app/indexes/bm25")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create temporary directory for indexing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write documents to temporary JSON files
        logger.info(f"Writing {len(documents)} documents to temporary files")
        for i, doc in enumerate(documents):
            with open(os.path.join(temp_dir, f"doc{i}.json"), 'w') as f:
                json.dump(doc, f)
        
        # Create indexer
        indexer = LuceneIndexer(output_dir)
        
        # Set indexing options
        indexer.set_analyze_tokenically(True)
        indexer.set_keepStopwords(True)
        indexer.set_storePositions(True)
        indexer.set_storeDocvectors(True)
        indexer.set_storeContents(True)
        indexer.set_storeRaw(True)
        
        # Additional fields to index
        indexer.set_fields(["contents", "course_id", "activity_id", "course_name", "activity_name", "strand"])
        
        # Index the documents
        logger.info("Indexing documents for BM25")
        indexer.index(temp_dir)
        
        logger.info(f"BM25 index created at {output_dir}")