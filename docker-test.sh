#!/bin/bash

# Quick local test with Docker

echo "🐳 Building and testing with Docker..."

# Build
docker build -t summarize-x402 .

# Run in background
docker run -d --name summarize-test -p 8000:8000 summarize-x402

# Wait for startup
sleep 3

# Test
echo ""
echo "🧪 Testing endpoints..."
curl -s http://localhost:8000/health | jq .
curl -s http://localhost:8000/pricing | jq .

echo ""
echo "✅ Service running at http://localhost:8000"
echo "📚 Docs at http://localhost:8000/docs"
echo ""
echo "Stop with: docker stop summarize-test && docker rm summarize-test"
