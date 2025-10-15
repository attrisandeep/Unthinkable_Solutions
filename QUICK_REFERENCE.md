# KnowledgeExplorer Quick Reference

## 🚀 Quick Start

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
Copy-Item .env.example .env
# Edit .env and add API keys

# 3. Start server
python main.py
# OR
.\start_backend.ps1
```

## 📍 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint |
| `/health` | GET | Health check with config |
| `/api/health` | GET | Simple health check |
| `/api/upload` | POST | Upload files (PDF/TXT) |
| `/api/upload/status` | GET | Check upload directory |
| `/api/query` | POST | Query knowledge base |
| `/api/stream-query` | GET | Query with streaming (SSE) |

## 🔑 Required API Keys

```env
GROQ_API_KEY=gsk_...           # Get from: https://console.groq.com/keys
PINECONE_API_KEY=pcsk_...      # Get from: https://app.pinecone.io/
JINA_API_KEY=jina_...          # Get from: https://jina.ai/ (optional)
```

## 📤 Upload Example

```powershell
# Upload single file
curl -X POST http://localhost:8000/api/upload `
  -F "files=@document.pdf"

# Upload multiple files
curl -X POST http://localhost:8000/api/upload `
  -F "files=@doc1.pdf" `
  -F "files=@doc2.txt"
```

## 🔍 Query Examples

### Standard Query
```powershell
curl -X POST http://localhost:8000/api/query `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"What is the main topic?\", \"top_k\": 5}'
```

### Streaming Query
```powershell
curl -N http://localhost:8000/api/stream-query?question=What%20is%20the%20main%20topic?
```

## 🧪 Testing

```powershell
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_embeddings.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run integration tests (requires API keys)
pytest tests/test_integration.py -v
```

## 🔧 Configuration

Edit `.env` to customize:

```env
# LLM Settings
GROQ_MODEL=mixtral-8x7b-32768
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=2048

# Document Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=64

# Server Settings
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

## 📁 Project Structure

```
knowledge-spark-38-main/
├── main.py                    # FastAPI app
├── backend_config.py          # Config loader
├── requirements.txt           # Dependencies
├── .env                       # Environment vars
├── services/                  # Core services
│   ├── embeddings.py         # Jina + local
│   ├── vectorstore.py        # Pinecone
│   └── llm.py                # Groq LLM
├── pipeline/                  # Data pipelines
│   ├── ingest.py             # Document ingestion
│   └── query.py              # RAG queries
├── routes/                    # API routes
│   ├── upload.py             # Upload endpoint
│   └── query.py              # Query endpoints
└── tests/                     # Test suite
```

## 🌐 Frontend Integration

### Fetch API (Standard)
```typescript
const response = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'What is...?', top_k: 5 })
});
const data = await response.json();
console.log(data.answer);
```

### EventSource (Streaming)
```typescript
const es = new EventSource('http://localhost:8000/api/stream-query?question=What%20is...?');
es.addEventListener('message', e => console.log(e.data));
es.addEventListener('done', e => { 
  console.log(JSON.parse(e.data)); 
  es.close(); 
});
```

## 🐛 Troubleshooting

### Import Errors
```powershell
pip install -r requirements.txt
```

### Port In Use
Change in `.env`:
```env
PORT=8001
```

### API Key Errors
Check validation:
```powershell
curl http://localhost:8000/health
```

### No Documents Retrieved
1. Verify files uploaded successfully
2. Check Pinecone index exists
3. Verify embeddings dimension matches

## 📚 Documentation

- `BACKEND_README.md` - Full setup guide
- `frontend-integration.md` - Frontend integration
- `requirements.txt` - Dependencies
- `.env.example` - Configuration template

## 🔗 Useful URLs

- Backend: http://localhost:8000
- Health: http://localhost:8000/health
- Frontend: http://localhost:5173 (Vite default)
- Docs: http://localhost:8000/docs (FastAPI auto-docs)

## 💡 Tips

1. **Use local embeddings**: Remove `JINA_API_KEY` from `.env`
2. **Debug streaming**: Use `curl -N` to test SSE
3. **Monitor logs**: Set `LOG_LEVEL=DEBUG` in `.env`
4. **Reset database**: Delete and recreate Pinecone index
5. **Test without keys**: Run unit tests (skip integration tests)

## 📊 Sample Response

### Query Response
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk_id": "0_1",
      "score": 0.95,
      "preview": "..."
    }
  ],
  "metadata": {
    "retrieved_docs": 5,
    "question": "What is the main topic?",
    "top_k": 5
  }
}
```

### SSE Events
```
event: metadata
data: {"sources": [...], "retrieved_docs": 5}

event: message
data: The

event: message
data:  answer

event: done
data: {"answer": "The answer is...", "token_count": 50}
```
