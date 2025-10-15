# KnowledgeExplorer - RAG System

A full-stack Retrieval-Augmented Generation (RAG) system built with FastAPI and React. Upload documents (PDF/TXT) and ask questions to get AI-powered answers with source citations.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.119.0-green)
![React](https://img.shields.io/badge/React-18.3.1-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6.2-blue)

## ✨ Features

- 📄 **Document Upload**: Support for PDF and TXT files
- 🔍 **Smart Search**: Vector-based semantic search using Pinecone
- 🤖 **AI Answers**: Powered by Groq's Llama 3.3 70B model
- 🌊 **Real-time Streaming**: Token-by-token answer generation
- 📚 **Source Citations**: See exactly where answers come from
- 🎨 **Beautiful UI**: Modern React interface with Tailwind CSS
- ⚡ **Fast Embeddings**: Cloud-based Jina AI with local fallback

## 🏗️ Architecture

### Backend Stack
- **FastAPI** - Modern Python web framework
- **Groq** - LLM inference (Llama 3.3 70B)
- **Pinecone** - Vector database for semantic search
- **Jina AI** - High-quality embeddings
- **LangChain** - Document processing and text splitting

### Frontend Stack
- **React** - UI library
- **Vite** - Build tool
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **Framer Motion** - Animations

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- Node.js 18+
- API Keys:
  - [Groq API Key](https://console.groq.com/keys)
  - [Pinecone API Key](https://app.pinecone.io/)
  - [Jina AI API Key](https://jina.ai/) (optional)

### Installation

**Step 1: Clone the repository**
```bash
git clone https://github.com/yourusername/knowledge-explorer.git
cd knowledge-explorer
```

**Step 2: Install Python dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Install Node dependencies**
```bash
npm install
```

**Step 4: Configure environment variables**

Create a `.env` file in the root directory:
```env
# Groq Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=2048

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=us-east-1
PINECONE_INDEX=knowledge-explorer

# Jina AI Configuration (optional)
JINA_API_KEY=your_jina_api_key_here

# Document Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=64

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

**Step 5: Create Pinecone Index**
- Go to [Pinecone Console](https://app.pinecone.io/)
- Create a new index:
  - Name: `knowledge-explorer`
  - Dimensions: `768`
  - Metric: `cosine`
  - Region: `us-east-1` (AWS)

### Running the Application

**Option 1: Using Batch Files (Windows)**
```bash
# Start backend
start-backend.bat

# In another terminal, start frontend
start-frontend.bat
```

**Option 2: Manual Start**
```bash
# Terminal 1 - Backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage

1. **Upload Documents**
   - Click "Attach Documents"
   - Select PDF or TXT files
   - Wait for green checkmark ✅

2. **Ask Questions**
   - Type your question in the input box
   - Press Enter
   - Watch the AI-generated answer stream in real-time

3. **View Sources**
   - See which document chunks were used
   - Click on sources for more context

## 🛠️ Development

### Project Structure

```
knowledge-explorer/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── backend_config.py       # Configuration loader
│   ├── services/               # Core services
│   │   ├── embeddings.py       # Jina AI + local embeddings
│   │   ├── vectorstore.py      # Pinecone wrapper
│   │   └── llm.py              # Groq LLM wrapper
│   ├── pipeline/               # RAG pipeline
│   │   ├── ingest.py           # Document processing
│   │   └── query.py            # Query pipeline
│   └── routes/                 # API routes
│       ├── upload.py           # File upload endpoint
│       └── query.py            # Query endpoints
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   └── lib/                # Utilities
│   │       └── api.ts          # API client
├── tests/                      # Unit tests
├── uploads/                    # Uploaded documents
├── requirements.txt            # Python dependencies
├── package.json                # Node dependencies
└── .env                        # Environment config (not in git)
```

### Running Tests

```bash
pytest tests/
```

### API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## 🎯 How It Works

### Document Upload Flow
```
1. User uploads PDF/TXT → Backend
2. Text extraction from document
3. Split into 512-character chunks (64 overlap)
4. Create embeddings via Jina AI (768-dim vectors)
5. Store vectors in Pinecone
6. Ready for queries!
```

### Query Flow
```
1. User asks a question
2. Question → Jina AI → embedding vector
3. Search Pinecone for top 5 similar chunks
4. Build context with retrieved chunks
5. Send to Groq LLM (Llama 3.3 70B)
6. Stream answer token-by-token
7. Show sources with citations
```

## 🐛 Troubleshooting

### "Failed to fetch" Error
- Make sure backend is running on port 8000
- Check CORS is configured for your frontend port
- Verify API keys are correct

### "Internal Server Error"
- Check backend logs for detailed error
- Verify all API keys are valid
- Ensure Pinecone index exists with correct dimensions (768)

### Upload Fails
- Check file size (max 10MB)
- Verify file is PDF or TXT format
- Check backend logs for processing errors

### No Answers Generated
- Make sure you've uploaded documents first
- Verify documents were processed (check backend logs)
- Ensure Groq API key is valid

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more details.

## 📚 Documentation

- [Backend README](BACKEND_README.md) - Detailed backend documentation
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues and solutions
- [Quick Reference](QUICK_REFERENCE.md) - Quick start commands

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) - Fast LLM inference
- [Pinecone](https://www.pinecone.io/) - Vector database
- [Jina AI](https://jina.ai/) - Embeddings API
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend library
- [Shadcn UI](https://ui.shadcn.com/) - UI components

## 🔮 Future Enhancements

- [ ] Support for more document formats (DOCX, CSV, etc.)
- [ ] Multi-language support
- [ ] User authentication and document management
- [ ] Chat history and conversation threads
- [ ] Export answers to PDF/markdown
- [ ] Batch document processing
- [ ] Custom embedding models
- [ ] Advanced search filters

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, React, and modern AI technologies**

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS




