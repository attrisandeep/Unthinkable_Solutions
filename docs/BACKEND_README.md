# KnowledgeExplorer Backend

A complete FastAPI-based RAG (Retrieval-Augmented Generation) backend for document Q&A with streaming support.

## 🚀 Features

- **Document Ingestion**: Upload and process PDF and TXT files
- **Vector Storage**: Store embeddings in Pinecone for semantic search
- **RAG Pipeline**: Retrieve relevant context and generate answers using Groq LLM
- **Streaming Support**: Server-Sent Events (SSE) for real-time token streaming
- **Smart Embeddings**: Jina AI Hub cloud embeddings with local fallback
- **CORS Enabled**: Ready for React/Vite frontend integration

## 📋 Prerequisites

- Python 3.9 or higher
- API Keys:
  - [Groq API Key](https://console.groq.com/keys)
  - [Pinecone API Key](https://app.pinecone.io/)
  - [Jina AI API Key](https://jina.ai/) (optional, fallback to local model)

## 🛠️ Installation

1. **Install Python dependencies**:

```powershell
pip install -r requirements.txt
```

2. **Create environment configuration**:

```powershell
Copy-Item .env.example .env
```

3. **Edit `.env` and add your API keys**:

```env
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=us-west1-gcp
JINA_API_KEY=your_jina_api_key_here
```

## 🏃 Running the Server

### Development Mode (with auto-reload)

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at `http://localhost:8000`

## 🔍 API Endpoints

### Health Check

```powershell
# Basic health check
curl http://localhost:8000/health

# API health check
curl http://localhost:8000/api/health
```

### Upload Documents

```powershell
# Upload single file
curl -X POST http://localhost:8000/api/upload `
  -F "files=@document.pdf"

# Upload multiple files
curl -X POST http://localhost:8000/api/upload `
  -F "files=@document1.pdf" `
  -F "files=@document2.txt"
```

### Query (Standard)

```powershell
# JSON query
curl -X POST http://localhost:8000/api/query `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"What is the main topic?\", \"top_k\": 5}'
```

### Query (Streaming)

```powershell
# Streaming query with SSE
curl -N http://localhost:8000/api/stream-query?question=What%20is%20the%20main%20topic?
```

## 🧪 Running Tests

### Run all tests

```powershell
pytest tests/ -v
```

### Run specific test file

```powershell
pytest tests/test_embeddings.py -v
```

### Run with coverage

```powershell
pytest tests/ --cov=. --cov-report=html
```

### Run integration tests (requires API keys)

Integration tests are automatically skipped if API keys are not configured. To run them, ensure all API keys are set in `.env`:

```powershell
pytest tests/test_integration.py -v
```

## 📁 Project Structure

```
knowledge-spark-38-main/
├── main.py                    # FastAPI application entry point
├── backend_config.py          # Central configuration loader
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── services/
│   ├── embeddings.py         # Jina + local embeddings
│   ├── vectorstore.py        # Pinecone wrapper
│   └── llm.py               # Groq LLM with streaming
├── pipeline/
│   ├── ingest.py            # Document ingestion pipeline
│   └── query.py             # RAG query pipeline
├── routes/
│   ├── upload.py            # File upload endpoints
│   └── query.py             # Query endpoints
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── test_embeddings.py   # Embeddings tests
│   ├── test_vectorstore.py  # Vector store tests
│   └── test_integration.py  # Integration tests
└── uploads/                  # Uploaded files directory
```

## ⚙️ Configuration

All settings are in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM | Required |
| `GROQ_MODEL` | Groq model name | mixtral-8x7b-32768 |
| `GROQ_TEMPERATURE` | LLM temperature | 0.7 |
| `GROQ_MAX_TOKENS` | Max tokens to generate | 2048 |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_ENV` | Pinecone environment | us-west1-gcp |
| `PINECONE_INDEX` | Pinecone index name | knowledge-explorer |
| `JINA_API_KEY` | Jina AI API key | Optional |
| `CHUNK_SIZE` | Document chunk size | 512 |
| `CHUNK_OVERLAP` | Chunk overlap size | 64 |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `LOG_LEVEL` | Logging level | INFO |

## 🔧 Debugging Tips

### Embeddings

To use only local embeddings (skip Jina):
- Remove `JINA_API_KEY` from `.env`
- Or set `use_jina=False` in `services/embeddings.py`

### Streaming

To debug SSE streaming:
1. Check browser console for EventSource errors
2. Verify CORS headers are correct
3. Monitor server logs for token generation
4. Test with curl `-N` flag for no buffering

### Vector Store

To verify Pinecone connection:
```powershell
curl http://localhost:8000/health
```

Check the `api_keys` section in the response.

## 🌐 Local Development Workflow

1. **Start Backend Server**:
```powershell
python main.py
```

2. **Start Frontend** (in another terminal):
```powershell
cd knowledge-spark-38-main
npm run dev
```

3. **Test Upload**:
   - Open frontend at `http://localhost:5173`
   - Upload a PDF or TXT file
   - Check server logs for ingestion progress

4. **Test Query**:
   - Enter a question in the frontend
   - Watch for streaming tokens
   - Check sources in response

## 📊 Sample Logs

```
INFO - 🚀 Starting KnowledgeExplorer backend...
INFO - 📋 Configuration: CHUNK_SIZE=512, CHUNK_OVERLAP=64
INFO - 🔑 API Keys validation: {'groq': True, 'pinecone': True, 'jina': True}
INFO - ✅ API routes registered successfully
INFO - 🌐 Starting server on 0.0.0.0:8000
INFO - 📤 Received 1 file(s) for upload
INFO - 💾 Saved file: document.pdf (123456 bytes)
INFO - 🚀 Starting ingestion pipeline for: document.pdf
INFO - 📄 Loading document: document.pdf
INFO - ✅ Loaded 5 page(s) from document.pdf
INFO - ✂️  Splitting 5 document(s) into chunks...
INFO - ✅ Created 42 chunks
INFO - 🔢 Generating embeddings for 42 chunks...
INFO - 💾 Upserting 42 vectors to Pinecone...
INFO - ✅ Ingestion complete for document.pdf
INFO - 🔍 Processing streaming query: What is the main topic?
INFO - 🔢 Embedding question: What is the main topic?
INFO - 🔍 Querying Pinecone for top 5 results...
INFO - ✅ Retrieved 5 documents
INFO - 🤖 Streaming answer with LLM...
```

## 🤝 Integration with Frontend

See [frontend-integration.md](frontend-integration.md) for detailed examples of:
- Using `fetch()` for standard queries
- Using `EventSource` for streaming queries
- Handling SSE events
- Error handling
- TypeScript types

## 🐛 Troubleshooting

### Import Errors

If you get import errors, ensure you're in the correct directory and all dependencies are installed:

```powershell
pip install -r requirements.txt
```

### Port Already in Use

If port 8000 is in use, change it in `.env`:

```env
PORT=8001
```

### API Key Errors

Verify your API keys are correct:
```powershell
curl http://localhost:8000/health
```

Check the `api_keys` validation in the response.

### Pinecone Index Not Found

The index will be created automatically on first use. Ensure:
- `PINECONE_API_KEY` is valid
- `PINECONE_ENV` matches your Pinecone project
- You have quota available in your Pinecone account

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Jina AI Documentation](https://docs.jina.ai/)
- [LangChain Documentation](https://python.langchain.com/)
