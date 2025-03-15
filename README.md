# RAG embedding, indexing, and retieval test platform (ARCHIVED!)


##  This is a good attempt, but pyserini issues suggest I should do this another way, and also try again but with vespa.ai


A modular Python-based prototype search platform that supports multiple retrieval methods for technical and specialised learning content.

## Features

- **Multiple Retrieval Methods**:
  - BM25 (classical sparse) using Pyserini
  - uniCOIL (pre-trained learned sparse) using Pyserini
  - Dense embeddings using BGE-M3 stored in Weaviate
  - Multi-vector embeddings using BGE-M3 (token embeddings) stored in Weaviate
- **Metadata Filtering**: Filter by course ID, activity ID, learning strand, etc.
- **API Endpoints**: Test queries and compare results across methods
- **Docker-based**: Easy setup with Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- 8GB+ RAM recommended (for BGE-M3 model)

### Setup

1. Clone this repository:

```bash
git clone https://github.com/brianlmerritt/rag_embedding_retrieval_test_platform.git
cd rag_embedding_retrieval_test_platform
```

2. Prepare test data (or bring your own):
   - Create a `data` directory and add your JSONL dataset
   - Each line should be a JSON object with the following structure:

```json
{
  "id": "doc1",
  "contents": "Full textual content for retrieval.",
  "course_id": "VET101",
  "activity_id": "ACT205",
  "course_name": "Small Animal Medicine",
  "activity_name": "Renal Diseases",
  "activity_type": "Moodle Book",
  "strand": "Internal Medicine"
}
```

3. Start the services:

```bash
docker-compose up -d
```

### Indexing

The indexing process will automatically start when you run `docker-compose up`. It will:

1. Create BM25 index
2. Process and create uniCOIL index
3. Generate BGE-M3 embeddings and store in Weaviate
4. Store multi-vector token embeddings in Weaviate

You can monitor the indexing progress by checking the logs:

```bash
docker-compose logs -f indexer
```

## API Usage

The API will be available at `http://localhost:8000` once all services are running.

### API Endpoints

- **GET /** - Welcome page
- **POST /search/bm25** - BM25 search
- **POST /search/unicoil** - uniCOIL search
- **POST /search/dense** - Dense embedding search
- **POST /search/multivector** - Multi-vector embedding search
- **POST /search/all** - Run query across all methods and compare

### Example Request

```bash
curl -X POST http://localhost:8000/search/all \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How to treat CKD in cats?",
    "filters": {
      "strand": "Internal Medicine"
    },
    "top_k": 5
  }'
```

### Example Response

```json
{
  "bm25_results": [...],
  "unicoil_results": [...],
  "dense_results": [...],
  "multi_vector_results": [...],
  "metadata": {
    "query": "How to treat CKD in cats?",
    "filters": {
      "strand": "Internal Medicine"
    },
    "top_k": 5
  }
}
```

## Testing

To test the system with your own queries:

1. Open your browser to `http://localhost:8000/docs` to use the Swagger UI
2. Try different queries and filters
3. Compare results from different retrieval methods

## System Architecture

- **Weaviate**: Vector database for dense and multi-vector embeddings
- **Pyserini**: For BM25 and uniCOIL indexing and search
- **FastAPI**: API layer for search endpoints
- **BGE-M3**: Large language model for generating embeddings

## Future Enhancements

- Reranking module
- UI for manual evaluation
- Score calibration/combination
- Model fine-tuning pipeline

## Troubleshooting

- If Weaviate fails to start, check if the port 8080 is already in use
- For memory issues, reduce batch sizes in the indexing process
- Check logs with `docker-compose logs service-name`

## License

This project is licensed under the MIT License - see the LICENSE file for details.