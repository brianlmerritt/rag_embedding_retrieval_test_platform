#!/bin/bash

# Create directory structure
mkdir -p data indexes

# Check if sample data already exists
if [ ! -f "data/vet_moodle_dataset.jsonl" ]; then
    echo "Generating sample data..."
    python data_generator.py
fi

# Build and start the containers
echo "Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Monitor indexing progress
echo "Monitoring indexing progress (press Ctrl+C to stop)..."
docker-compose logs -f indexer