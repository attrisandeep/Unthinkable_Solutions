# KnowledgeExplorer - Intelligent RAG System

A production-ready Retrieval-Augmented Generation (RAG) system with smart document detection, built with FastAPI and React.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-green)
![React](https://img.shields.io/badge/React-18.3.1-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6.2-blue)

## 🌟 Features

- 📄 **Smart Document Processing** - Automatic PDF/TXT upload with intelligent chunking
- 🧠 **Intelligent Mode Detection** - Automatically switches between document-based and general AI responses
- 🔍 **Semantic Search** - Powered by Pinecone vector database with relevance filtering
- 🤖 **Advanced AI** - Groq's Llama 3.3 70B model with streaming support
- 🎯 **Clean Answers** - Natural language responses without technical metadata
- ⚡ **Real-time Streaming** - Token-by-token answer generation via Server-Sent Events
- 📚 **Source Citations** - Automatic source attribution in professional format
- 🔧 **Document Management** - Full API for managing knowledge base

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + TypeScript + Vite + Tailwind + Shadcn UI          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├── HTTP/SSE
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │   Pipeline   │  │   Services   │     │
│  │  - Upload    │→ │  - Ingest    │→ │  - Embeddings│     │
│  │  - Query     │  │  - Query     │  │  - LLM       │     │
│  │  - Documents │  │              │  │  - Vectorstore│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├── API Calls
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Groq     │  │  Pinecone  │  │  Jina AI   │           │
│  │ (LLM API)  │  │  (Vectors) │  │ (Embeddings)│           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- Node.js 18+
- API Keys (see [Setup](#setup))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/attrisandeep/Unthinkable_Solutions.git
   cd Unthinkable_Solutions
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Pinecone Index**
   - Go to [Pinecone Console](https://app.pinecone.io/)
   - Create index: `knowledge-explorer`
   - Dimensions: `768`
   - Metric: `cosine`
   - Region: `us-east-1` (AWS)

### Running the Application

**Development Mode:**

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Usage

### Smart Mode Detection

The system automatically detects whether to use documents or general knowledge:

**Document Questions** (uses uploaded files):
```
✓ "Summarize my resume"
✓ "What does the document say about..."
✓ "Describe this report"
✓ "What skills are mentioned?"
```

**General Questions** (uses AI knowledge):
```
✓ "What is Python?"
✓ "Explain machine learning"
✓ "How does React work?"
```

### Document Management

```bash
# Get statistics
GET /api/documents/stats

# Clear all documents
DELETE /api/documents/clear-all

# Delete specific document
DELETE /api/documents/filename/report.pdf
```

### API Examples

**Standard Query:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize the document", "top_k": 5}'
```

**Streaming Query:**
```bash
curl "http://localhost:8000/api/stream-query?question=Explain%20this&top_k=5"
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Groq Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=2048

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV=us-east-1
PINECONE_INDEX=knowledge-explorer

# Jina AI (Optional - local fallback available)
JINA_API_KEY=your_jina_api_key

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MIN_RELEVANCE_SCORE=0.7

# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Get API Keys

- **Groq**: https://console.groq.com/keys
- **Pinecone**: https://app.pinecone.io/
- **Jina AI**: https://jina.ai/ (optional)

## 📁 Project Structure

```
Unthinkable_Solutions/
├── backend/                    # Python FastAPI backend
│   ├── routes/                 # API route handlers
│   │   ├── upload.py          # File upload endpoint
│   │   ├── query.py           # Query endpoints
│   │   └── documents.py       # Document management
│   ├── services/              # Core services
│   │   ├── embeddings.py      # Jina AI + local embeddings
│   │   ├── llm.py             # Groq LLM wrapper
│   │   └── vectorstore.py     # Pinecone integration
│   ├── pipeline/              # RAG pipeline
│   │   ├── ingest.py          # Document ingestion
│   │   └── query.py           # Query processing
│   ├── tests/                 # Unit tests
│   ├── main.py                # FastAPI app entry point
│   ├── backend_config.py      # Configuration loader
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── lib/               # Utilities & API client
│   │   └── hooks/             # Custom React hooks
│   ├── public/                # Static assets
│   └── package.json           # Node dependencies
│
├── docs/                       # Documentation
│   ├── SMART_RAG_GUIDE.md     # Usage guide
│   ├── RAG_IMPROVEMENTS.md    # Technical details
│   └── API.md                 # API documentation
│
├── scripts/                    # Utility scripts
│   ├── start-backend.bat      # Windows backend launcher
│   └── start-frontend.bat     # Windows frontend launcher
│
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## 🎯 Key Features Explained

### 1. Smart Detection

Automatically identifies question types:
- Document-specific keywords trigger RAG pipeline
- General questions use AI knowledge
- Seamless fallback when documents unavailable

### 2. Clean Answers

**Before:**
```
According to Document: resume.pdf (Relevance Score: 0.717), the candidate has...
```

**After:**
```
The candidate has extensive experience in Python and Java, with projects 
in web development and data mining.

Source: resume.pdf
```

### 3. Relevance Filtering

- Only uses matches with >0.7 similarity score
- Prevents low-quality context from polluting answers
- Automatic fallback to general knowledge

### 4. Optimized Chunking

- 1000-character chunks (vs 512) for better context
- 200-character overlap for continuity
- Preserves semantic meaning across splits

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Check code quality
flake8 .
black --check .
```

## 📊 Performance

- **Query Speed**: ~2-3 seconds avg
- **Upload Processing**: ~1 second per page
- **Streaming Latency**: <100ms first token
- **Vector Search**: <200ms for top-5 retrieval

## 🐛 Troubleshooting

### Common Issues

**1. "Failed to connect to backend"**
- Verify backend is running on port 8000
- Check CORS configuration
- Ensure API keys are valid

**2. "No relevant documents found"**
- Clear old documents: `DELETE /api/documents/clear-all`
- Re-upload your files
- Check Pinecone index configuration

**3. "Mixed document information"**
- Use document management API to clear old files
- Upload only relevant documents together

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more.

## 📚 Documentation

- [SMART_RAG_GUIDE.md](docs/SMART_RAG_GUIDE.md) - Complete usage guide
- [RAG_IMPROVEMENTS.md](docs/RAG_IMPROVEMENTS.md) - Technical improvements
- [API.md](docs/API.md) - Full API reference

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Ultra-fast LLM inference
- [Pinecone](https://www.pinecone.io/) - Vector database
- [Jina AI](https://jina.ai/) - Embedding API
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Shadcn UI](https://ui.shadcn.com/) - Beautiful UI components

## 📧 Contact

**Sandeep** - [@attrisandeep](https://github.com/attrisandeep)

**Project Link**: https://github.com/attrisandeep/Unthinkable_Solutions

---

