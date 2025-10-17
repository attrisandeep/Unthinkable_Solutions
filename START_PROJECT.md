# 🚀 Quick Start Guide

## Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- Git

## Setup Instructions

### 1️⃣ Clone Repository
```bash
git clone https://github.com/attrisandeep/Unthinkable_Solutions.git
cd Unthinkable_Solutions
```

### 2️⃣ Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
# Copy .env.example to .env and add your API keys:
cp .env.example .env
# Edit .env file with your actual API keys
```

### 3️⃣ Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install
```

### 4️⃣ Configure API Keys
Edit `backend/.env` file with your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
JINA_API_KEY=your_jina_api_key_here
```

**Get API Keys:**
- Groq: https://console.groq.com/
- Pinecone: https://www.pinecone.io/
- Jina AI: https://jina.ai/

### 5️⃣ Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6️⃣ Access Application
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📝 Usage
1. Upload PDF or TXT documents
2. Ask questions about your documents
3. Get AI-powered answers with source citations
4. Can also ask general questions without documents

## ⚙️ Configuration
Edit `backend/backend_config.py` to customize:
- Chunk size and overlap
- Relevance score threshold
- Model selection
- Vector database settings
