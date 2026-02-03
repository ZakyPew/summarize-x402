#!/bin/bash

# Test script for SummarizeAI x402 service

BASE_URL="${1:-http://localhost:8000}"

echo "🧪 Testing SummarizeAI x402 at $BASE_URL"
echo ""

# Test 1: Health check
echo "1️⃣ Testing health endpoint..."
curl -s "$BASE_URL/health" | jq .
echo ""

# Test 2: Pricing info
echo "2️⃣ Testing pricing endpoint..."
curl -s "$BASE_URL/pricing" | jq .
echo ""

# Test 3: Payment required (no payment header)
echo "3️⃣ Testing 402 response (no payment)..."
curl -s -w "\nHTTP Status: %{http_code}\n" "$BASE_URL/summarize" -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test article about artificial intelligence and machine learning. It covers deep learning, neural networks, and modern AI applications in industry."}'
echo ""

# Test 4: Successful summarization (with mock payment)
echo "4️⃣ Testing summarization with payment..."
curl -s "$BASE_URL/summarize" -X POST \
  -H "Content-Type: application/json" \
  -H "X-402-Payment: mock_payment_$(date +%s)" \
  -d '{
    "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals. The term artificial intelligence had previously been used to describe machines that mimic and display human cognitive skills that are associated with the human mind, such as learning and problem-solving. This has led to the development of various AI technologies including machine learning, deep learning, neural networks, computer vision, natural language processing, and robotics. These technologies have been applied across numerous industries including healthcare, finance, transportation, and entertainment, transforming how businesses operate and how people interact with technology.",
    "max_length": 100,
    "style": "concise"
  }' | jq .
echo ""

# Test 5: URL summarization
echo "5️⃣ Testing URL summarization..."
curl -s "$BASE_URL/summarize" -X POST \
  -H "Content-Type: application/json" \
  -H "X-402-Payment: mock_payment_url_$(date +%s)" \
  -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence", "max_length": 150}' | jq .summary
echo ""

echo "✅ Tests complete!"
