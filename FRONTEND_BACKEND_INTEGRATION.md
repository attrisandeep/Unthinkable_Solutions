# Frontend-Backend Integration Quick Start

## 🚀 Starting Both Services

### Option 1: Use the Start-All Script (Recommended)

```powershell
.\start-all.ps1
```

This will:
- ✅ Check and create `.env` if needed
- ✅ Install frontend dependencies if needed
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:5173

### Option 2: Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```powershell
python main.py
```

**Terminal 2 - Frontend:**
```powershell
npm run dev
```

## 📡 API Integration

The backend is already configured to accept requests from the frontend with CORS enabled for:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (CRA default)

## 🔌 Frontend API Calls

### Using the Backend Endpoints

The frontend should make API calls to: `http://localhost:8000/api/`

### Example: Upload Files

```typescript
const uploadFiles = async (files: FileList) => {
  const formData = new FormData();
  
  Array.from(files).forEach(file => {
    formData.append('files', file);
  });
  
  const response = await fetch('http://localhost:8000/api/upload', {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
};
```

### Example: Query (Standard)

```typescript
const queryKnowledge = async (question: string) => {
  const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      top_k: 5
    }),
  });
  
  return await response.json();
};
```

### Example: Query (Streaming with SSE)

```typescript
const streamQuery = (question: string, onToken: (token: string) => void) => {
  const eventSource = new EventSource(
    `http://localhost:8000/api/stream-query?question=${encodeURIComponent(question)}`
  );
  
  eventSource.addEventListener('metadata', (e) => {
    const metadata = JSON.parse(e.data);
    console.log('Sources:', metadata.sources);
  });
  
  eventSource.addEventListener('message', (e) => {
    onToken(e.data);
  });
  
  eventSource.addEventListener('done', (e) => {
    const data = JSON.parse(e.data);
    console.log('Complete answer:', data.answer);
    eventSource.close();
  });
  
  eventSource.addEventListener('error', () => {
    eventSource.close();
  });
  
  return () => eventSource.close();
};
```

## 🔧 Environment Variables

### Backend (.env)

Already configured with:
```env
GROQ_API_KEY=...
PINECONE_API_KEY=...
JINA_API_KEY=...
```

### Frontend (Optional)

Create a `.env` or `.env.local` in the frontend if you want to configure the API URL:

```env
VITE_API_URL=http://localhost:8000
```

Then use it in your code:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

## 📝 Updating Existing Frontend Components

If you have existing components like FileUpload, QueryInput, etc., update them to call the backend:

### FileUpload Component

```typescript
import { useState } from 'react';

export function FileUpload() {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setMessage('');

    try {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setMessage(`✅ ${data.message}`);
    } catch (error) {
      setMessage(`❌ Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".pdf,.txt"
        multiple
        onChange={handleUpload}
        disabled={uploading}
      />
      {uploading && <p>Processing...</p>}
      {message && <p>{message}</p>}
    </div>
  );
}
```

### QueryInput Component (with Streaming)

```typescript
import { useState } from 'react';

export function QueryInput() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<any[]>([]);
  const [streaming, setStreaming] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || streaming) return;

    setStreaming(true);
    setAnswer('');
    setSources([]);

    const eventSource = new EventSource(
      `http://localhost:8000/api/stream-query?question=${encodeURIComponent(question)}`
    );

    eventSource.addEventListener('metadata', (e) => {
      const metadata = JSON.parse(e.data);
      setSources(metadata.sources);
    });

    eventSource.addEventListener('message', (e) => {
      setAnswer(prev => prev + e.data);
    });

    eventSource.addEventListener('done', () => {
      eventSource.close();
      setStreaming(false);
    });

    eventSource.addEventListener('error', () => {
      eventSource.close();
      setStreaming(false);
    });
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          disabled={streaming}
        />
        <button type="submit" disabled={streaming || !question.trim()}>
          {streaming ? 'Asking...' : 'Ask'}
        </button>
      </form>

      {answer && (
        <div>
          <h3>Answer:</h3>
          <p>{answer}{streaming && '▊'}</p>
        </div>
      )}

      {sources.length > 0 && (
        <div>
          <h4>Sources:</h4>
          <ul>
            {sources.map((source, idx) => (
              <li key={idx}>
                <strong>{source.filename}</strong>
                <br />
                <small>{source.preview}</small>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## 🧪 Testing the Integration

1. **Start both services:**
   ```powershell
   .\start-all.ps1
   ```

2. **Open browser:**
   - Frontend: http://localhost:5173
   - Backend API Docs: http://localhost:8000/docs

3. **Test workflow:**
   - Upload a PDF or TXT file
   - Ask a question about the content
   - See the streaming response

4. **Check health:**
   ```powershell
   curl http://localhost:8000/health
   ```

## 🐛 Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:
- Backend is configured for `localhost:5173`
- Make sure backend is running on port 8000
- Check browser console for exact error

### Connection Refused

If frontend can't connect to backend:
```powershell
# Check if backend is running
curl http://localhost:8000/health
```

### Port Already in Use

If port 5173 is taken:
```powershell
# Vite will automatically try 5174, 5175, etc.
# Or specify a different port:
npm run dev -- --port 3000
```

## 📚 More Examples

See the full documentation:
- **frontend-integration.md** - Complete TypeScript examples
- **BACKEND_README.md** - API documentation
- **QUICK_REFERENCE.md** - Quick commands

## ✨ You're All Set!

Both services should now be running and connected. You can:
- ✅ Upload documents via the frontend
- ✅ Query with real-time streaming
- ✅ See sources and citations
- ✅ Full RAG pipeline working end-to-end
