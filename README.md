# SummarizeAI x402

Content summarization microservice with automatic x402 (HTTP 402) payments.

## What is this?

An AI-powered API that summarizes articles, documents, and text. Agents (or humans) pay per-request via x402 payment headers - no accounts, no subscriptions, just pay-as-you-go.

## Pricing

- **0.1 ETH per request** (~$0.25-0.50 depending on market)
- Payments on Base L2 (low gas fees)
- Revenue goes directly to your wallet

## API Endpoints

### GET / - Service info
### GET /health - Health check  
### GET /pricing - Current pricing
### POST /summarize - Summarize content

## Usage Example

```bash
# 1. Get pricing info
curl https://your-service.railway.app/pricing

# 2. Send request with payment
curl -X POST https://your-service.railway.app/summarize \
  -H "Content-Type: application/json" \
  -H "X-402-Payment: YOUR_PAYMENT_PROOF_HERE" \
  -d '{
    "url": "https://example.com/article",
    "max_length": 200,
    "style": "concise"
  }'
```

## Request Body

```json
{
  "url": "https://example.com/article",     // Optional: URL to summarize
  "text": "Raw text content...",             // Optional: Direct text
  "max_length": 200,                         // Max words in summary
  "style": "concise"                         // concise | detailed | bullets
}
```

## Response

```json
{
  "summary": "The article discusses...",
  "original_length": 5234,
  "summary_length": 142,
  "cost": "100000000000000000 wei (0.1 ETH)"
}
```

## Payment Required Response (402)

If no payment header provided:

```json
{
  "error": "Payment Required",
  "x402": {
    "receiver": "0xcAa16ffB50cb7f17690286ED4a19224AF7dC199B",
    "amount": "100000000000000000",
    "currency": "wei",
    "network": "base",
    "description": "Content summarization (/summarize)"
  }
}
```

## Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set OpenAI API key (optional, for better summaries)
echo "OPENAI_API_KEY=your_key" > .env

# 3. Run locally
uvicorn main:app --reload

# 4. Test
curl http://localhost:8000/
```

## Deployment

### Railway (Recommended)

1. Push to GitHub
2. Connect repo to Railway
3. Deploy automatically

### Docker

```bash
docker build -t summarize-x402 .
docker run -p 8000:8000 summarize-x402
```

## Revenue

All payments go to: `0xcAa16ffB50cb7f17690286ED4a19224AF7dC199B`

Monitor earnings on [BaseScan](https://basescan.org/address/0xcAa16ffB50cb7f17690286ED4a19224AF7dC199B)

## TODO / Enhancements

- [ ] On-chain payment verification
- [ ] Redis for payment tracking (prevent replay)
- [ ] Rate limiting
- [ ] Usage analytics
- [ ] More summarization models (Claude, local LLMs)
- [ ] Batch processing endpoint
- [ ] Webhook callbacks for async jobs

## License

MIT - Build your own x402 services!
