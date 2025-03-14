import os
import json
import tempfile
import shutil
from typing import List, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModel
import logging

logger = logging.getLogger(__name__)

def create_unicoil_index(documents: List[Dict[str, Any]]) -> None:
    """
    Create a uniCOIL index using Pyserini.
    
    Args:
        documents: List of document dictionaries
    """
    # Create output directory if it doesn't exist
    output_dir = os.environ.get("UNICOIL_INDEX_PATH", "/app/indexes/unicoil")
    os.makedirs(output_dir, exist_ok=True)
    
    # Load pretrained uniCOIL model and tokenizer
    model_name = "castorini/unicoil-noexp-msmarco"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    # Create temporary directory for indexing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Process documents with uniCOIL
        logger.info(f"Processing {len(documents)} documents with uniCOIL")
        for i, doc in enumerate(documents):
            # Get the document content
            content = doc.get("contents", "")
            
            # Tokenize the content
            inputs = tokenizer(content, return_tensors="pt", max_length=512, truncation=True)
            
            # Get the weights from the model
            with torch.no_grad():
                outputs = model(**inputs)
                term_weights = outputs.term_weights.squeeze().cpu().numpy()
            
            # Create term-impact pairs
            term_impact_pairs = []
            for token_id, weight in zip(inputs.input_ids.squeeze().tolist(), term_weights):
                if weight > 0:
                    term = tokenizer.decode([token_id]).strip()
                    if term:
                        term_impact_pairs.append((term, weight))
            
            # Prepare document for indexing
            indexed_doc = {
                "id": doc.get("id", f"doc{i}"),
                "contents": content,
                "vector": term_impact_pairs,
                "course_id": doc.get("course_id", ""),
                "activity_id": doc.get("activity_id", ""),
                "course_name": doc.get("course_name", ""),
                "activity_name": doc.get("activity_name", ""),
                "strand": doc.get("strand", "")
            }
            
            # Write document to temporary file
            with open(os.path.join(temp_dir, f"doc{i}.json"), 'w') as f:
                json.dump(indexed_doc, f)
        
        # Use Pyserini's impact indexer
        from pyserini.index.lucene import IndexArgs, LuceneIndexer
        
        index_args = IndexArgs()
        index_args.index_path = output_dir
        index_args.input = temp_dir
        index_args.impact = True
        index_args.fields = ["contents", "course_id", "activity_id", "course_name", "activity_name", "strand"]
        index_args.storePositions = True
        index_args.storeDocvectors = True
        index_args.storeContents = True
        index_args.storeRaw = True
        
        # Create the index
        logger.info("Creating uniCOIL index")
        LuceneIndexer(index_args)
        
        logger.info(f"uniCOIL index created at {output_dir}")