Prompt: Prototype Test Platform for Veterinary Learning Content Search
Goal:
Create a modular Python-based prototype search platform that:

Supports multiple retrieval methods:
BM25 (classical sparse) using Pyserini.
uniCOIL (pre-trained learned sparse) using Pyserini.
Dense embeddings using BGE-M3 stored in Weaviate.
Multi-vector embeddings using BGE-M3 (token embeddings) stored in Weaviate (multi-vector support v1.29).
Enables flexible metadata indexing and filtering (e.g., course ID, activity ID, learning strand).
Provides API endpoints (Flask/FastAPI) for query testing and results comparison.
Stores results with metadata for downstream ranking work (scoring/reranking to be added later).
✅ Key Components to Deliver:
1. Data Preparation Pipeline
Input: Veterinary Moodle learning content.
Process:
Parse/export content into JSON Lines format (.jsonl), with each line:
json
Copy
Edit
{
  "id": "doc1",
  "contents": "Full textual content for retrieval.",
  "course_id": "VET101",
  "activity_id": "ACT205",
  "course_name": "Small Animal Medicine",
  "activity_name": "Renal Diseases",
  "strand": "Internal Medicine"
}
Output:
Data ready for Pyserini indexing and Weaviate ingestion.
2. Sparse Indexing and Retrieval with Pyserini
BM25 Indexing:

Create BM25 index using Pyserini from .jsonl dataset.
uniCOIL Indexing (pre-trained):

Process .jsonl through pre-trained uniCOIL (e.g., castorini/unicoil-noexp-msmarco) to create term-weighted impact format.
Index uniCOIL-formatted output using Pyserini --impact mode.
Search Functions:

Function to run BM25 search with metadata filter:
python
Copy
Edit
def search_bm25(query: str, filters: dict, k: int = 10): pass
Function to run uniCOIL search with metadata filter:
python
Copy
Edit
def search_unicoil(query: str, filters: dict, k: int = 10): pass
3. Dense and Multi-vector Embedding with BGE-M3 + Weaviate
Dense Embeddings:

Generate BGE-M3 dense embeddings (Hugging Face transformers).
Store dense embeddings in Weaviate under dense_vector.
Multi-vector Embeddings:

Extract token-level embeddings from BGE-M3 (list of vectors).
Store in Weaviate using multi-vector mode under multi_vector.
Metadata Support:

Full metadata stored with each entry: course_id, activity_id, course_name, activity_name, strand.
Ingestion Function:

python
Copy
Edit
def ingest_into_weaviate(doc: dict, dense_vector: list, multi_vector: list): pass
Dense Search Function:
python
Copy
Edit
def search_dense_weaviate(query: str, filters: dict, k: int = 10): pass
Multi-vector Search Function:
python
Copy
Edit
def search_multivector_weaviate(query: str, filters: dict, k: int = 10): pass
4. API Interface for Query Testing (FastAPI / Flask)
Endpoints:

/search/bm25: BM25 search with optional metadata filter.
/search/unicoil: uniCOIL search with optional metadata filter.
/search/dense: Dense BGE-M3 search.
/search/multivector: Multi-vector BGE-M3 search.
/search/all: Run query across all modes and return results for comparison.
Sample API Request:

json
Copy
Edit
{
  "query": "How to treat CKD in cats?",
  "filters": {
    "course_id": "VET101",
    "strand": "Internal Medicine"
  },
  "top_k": 10
}
Sample Response:
json
Copy
Edit
{
  "bm25_results": [...],
  "unicoil_results": [...],
  "dense_results": [...],
  "multi_vector_results": [...]
}
5. Result Storage for Evaluation (Optional)
Store search results in local database or JSON file for later analysis, e.g.:
json
Copy
Edit
{
  "query": "How to treat CKD in cats?",
  "bm25": [...],
  "unicoil": [...],
  "dense": [...],
  "multi_vector": [...]
}
✅ 6. Deliverable Structure
bash
Copy
Edit
vet-retrieval-platform/
│
├── data/
│   └── vet_moodle_dataset.jsonl  # Prepared content with metadata
│
├── indexing/
│   ├── pyserini_bm25_index.py    # BM25 indexing
│   ├── pyserini_unicoil_index.py # uniCOIL indexing pipeline
│   └── weaviate_ingest.py        # Dense & multi-vector ingestion
│
├── search/
│   ├── bm25_search.py
│   ├── unicoil_search.py
│   ├── weaviate_dense_search.py
│   └── weaviate_multivector_search.py
│
├── api/
│   └── main.py                   # FastAPI/Flask entrypoint with endpoints
│
└── README.md                     # Full setup and usage guide
✅ 7. Constraints and Assumptions
Focus on indexing and search, not ranking (for now).
Flexible design for adding reranking or combined scoring later.
Assume Python 3.9+, transformers, weaviate-client, pyserini, FastAPI/Flask.
✅ 8. Optional (Future Enhancements)
Feature	Possible Add-On
Reranking module	Plug-in reranker (e.g., T5/MonoT5/MonoBERT fine-tuned)
UI for manual evaluation	Simple web interface to review query results
Score calibration/combination	Model to combine sparse/dense/multi-vector scores later
Model fine-tuning pipeline	Fine-tune BGE-M3 and uniCOIL on vet-specific queries/doc pairs
✅ 9. Expected Outcomes
Working prototype retrieval system covering sparse, dense, and multi-vector embeddings.
Metadata-aware search (course, activity, strand, etc.).
Modular architecture for testing and future extensions.
Foundation for future evaluation and ranking improvements.