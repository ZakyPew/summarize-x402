from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import hashlib
import time
import json
from pathlib import Path

# For actual summarization, you can use OpenAI, Kimi, or local models
# Using a simple implementation for now, easily swappable

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = FastAPI(title="SummarizeAI x402", description="Content summarization microservice with x402 payments")

# x402 Configuration
RECEIVER_WALLET = "0xcAa16ffB50cb7f17690286ED4a19224AF7dC199B"  # Your ETH address
PRICE_PER_REQUEST = 33333333333333  # ~$0.10 USD at $3,000 ETH (0.000033 ETH in wei)

# Simple in-memory payment tracking (use Redis/DB in production)
payments_db = {}

class SummarizeRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    max_length: int = 200
    style: str = "concise"  # concise, detailed, bullets

class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    cost: str

# x402 Middleware
@app.middleware("http")
async def x402_middleware(request: Request, call_next):
    # Skip middleware for docs and health endpoints
    if request.url.path in ["/docs", "/openapi.json", "/health", "/"]: 
        return await call_next(request)
    
    # Check for x402 payment header
    payment_header = request.headers.get("X-402-Payment")
    
    if not payment_header:
        # Return 402 Payment Required with details
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment Required",
                "x402": {
                    "receiver": RECEIVER_WALLET,
                    "amount": str(PRICE_PER_REQUEST),
                    "currency": "wei",
                    "network": "base",  # or "ethereum", "optimism"
                    "description": f"Content summarization ({request.url.path})"
                }
            },
            headers={
                "X-402-Receiver": RECEIVER_WALLET,
                "X-402-Amount": str(PRICE_PER_REQUEST)
            }
        )
    
    # In production: verify payment on-chain
    # For now, accept any payment header as "proof of payment"
    # TODO: Add proper on-chain verification
    payment_hash = hashlib.sha256(payment_header.encode()).hexdigest()[:16]
    
    if payment_hash in payments_db:
        return JSONResponse(
            status_code=402,
            content={"error": "Payment already used"}
        )
    
    # Mark payment as used
    payments_db[payment_hash] = {
        "timestamp": time.time(),
        "endpoint": request.url.path
    }
    
    response = await call_next(request)
    return response

async def summarize_content(text: str, max_length: int = 200, style: str = "concise") -> str:
    """Summarize content using AI."""
    
    # Try OpenAI first
    if OPENAI_AVAILABLE and Path(".env").exists():
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            style_prompts = {
                "concise": "Summarize this in 2-3 sentences:",
                "detailed": "Provide a detailed summary with key points:",
                "bullets": "Summarize as bullet points:"
            }
            
            prompt = style_prompts.get(style, style_prompts["concise"])
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"{prompt} Keep it under {max_length} words."},
                    {"role": "user", "content": text[:8000]}  # Limit input
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")
            pass
    
    # Fallback: Simple extractive summarization
    sentences = text.replace("!", ".").replace("?", ".").split(".")
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if style == "bullets":
        return "\n• " + "\n• ".join(sentences[:5])
    
    # Score sentences by word importance (simple frequency)
    word_freq = {}
    for sentence in sentences:
        for word in sentence.lower().split():
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score and pick top sentences
    scored = []
    for sentence in sentences:
        score = sum(word_freq.get(w.lower(), 0) for w in sentence.split())
        scored.append((score, sentence))
    
    scored.sort(reverse=True)
    top_sentences = [s for _, s in scored[:3]]
    
    summary = ". ".join(top_sentences) + "."
    return summary[:max_length * 5]  # Rough char limit

@app.get("/")
async def root():
    return {
        "service": "SummarizeAI x402",
        "description": "Content summarization with automatic x402 payments",
        "endpoints": {
            "POST /summarize": "Summarize URL or text content",
            "GET /health": "Health check",
            "GET /pricing": "Current pricing"
        },
        "payment": {
            "type": "x402",
            "receiver": RECEIVER_WALLET,
            "amount_per_request": "$0.10 USD (0.000033 ETH)",
            "network": "base"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "payments_processed": len(payments_db)}

@app.get("/pricing")
async def pricing():
    return {
        "endpoint": "/summarize",
        "price": "$0.10 USD (0.000033 ETH)",
        "price_wei": PRICE_PER_REQUEST,
        "currency": "ETH",
        "network": "base",
        "receiver": RECEIVER_WALLET
    }

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """Summarize content from URL or provided text."""
    
    content = ""
    
    # Fetch content from URL if provided
    if request.url:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(request.url, follow_redirects=True)
                response.raise_for_status()
                
                # Basic HTML stripping
                html = response.text
                # Simple tag removal (use BeautifulSoup in production)
                import re
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'\s+', ' ', text).strip()
                content = text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    
    # Use provided text
    elif request.text:
        content = request.text
    else:
        raise HTTPException(status_code=400, detail="Provide either 'url' or 'text'")
    
    if len(content) < 100:
        raise HTTPException(status_code=400, detail="Content too short to summarize")
    
    # Generate summary
    summary = await summarize_content(content, request.max_length, request.style)
    
    return SummarizeResponse(
        summary=summary,
        original_length=len(content),
        summary_length=len(summary),
        cost=f"{PRICE_PER_REQUEST} wei (0.1 ETH)"
    )

# Webhook endpoint for async processing
@app.post("/summarize/webhook")
async def summarize_webhook(request: SummarizeRequest, webhook_url: str):
    """Submit summarization job with webhook callback."""
    # TODO: Implement async queue (Celery, RQ, etc.)
    return {"status": "queued", "job_id": hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:12]}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)