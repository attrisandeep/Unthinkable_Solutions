# Frontend Integration Guide

This guide shows how to integrate the KnowledgeExplorer backend with your React/TypeScript frontend.

## 🎯 Overview

The backend provides two main query endpoints:
1. **POST /api/query** - Standard request/response
2. **GET /api/stream-query** - Server-Sent Events (SSE) streaming

## 📦 TypeScript Types

First, define the types for API responses:

```typescript
// types/api.ts

export interface SourceItem {
  filename: string;
  chunk_id: string;
  score: number;
  preview: string;
}

export interface QueryResponse {
  answer: string;
  sources: SourceItem[];
  metadata: {
    retrieved_docs: number;
    question: string;
    top_k: number;
  };
}

export interface UploadResponse {
  status: string;
  message: string;
  files: Array<{
    filename: string;
    status: string;
    message?: string;
    chunks: number;
    upserted?: number;
  }>;
}

export interface StreamMetadata {
  sources: SourceItem[];
  retrieved_docs: number;
  question: string;
}

export interface StreamDoneData {
  answer: string;
  token_count: number;
}
```

## 📤 File Upload

### Basic Upload Example

```typescript
// utils/api.ts

const API_BASE_URL = 'http://localhost:8000';

export async function uploadFiles(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  
  files.forEach(file => {
    formData.append('files', file);
  });
  
  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }
  
  return await response.json();
}
```

### React Component Example

```typescript
// components/FileUpload.tsx

import { useState } from 'react';
import { uploadFiles } from '../utils/api';

export function FileUpload() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<string>('');

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    
    if (files.length === 0) return;
    
    setUploading(true);
    setResult('');
    
    try {
      const response = await uploadFiles(files);
      setResult(`✅ ${response.message}`);
      console.log('Upload details:', response.files);
    } catch (error) {
      setResult(`❌ Upload failed: ${error.message}`);
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
      {uploading && <p>Uploading and processing...</p>}
      {result && <p>{result}</p>}
    </div>
  );
}
```

## 🔍 Standard Query (POST /api/query)

### Basic Query Example

```typescript
// utils/api.ts

export async function queryKnowledge(
  question: string,
  topK: number = 5
): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      top_k: topK,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Query failed: ${response.statusText}`);
  }
  
  return await response.json();
}
```

### React Component Example

```typescript
// components/QueryInput.tsx

import { useState } from 'react';
import { queryKnowledge, QueryResponse } from '../utils/api';

export function QueryInput() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) return;
    
    setLoading(true);
    
    try {
      const response = await queryKnowledge(question);
      setResult(response);
    } catch (error) {
      console.error('Query failed:', error);
      alert(`Query failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? 'Searching...' : 'Ask'}
        </button>
      </form>
      
      {result && (
        <div>
          <h3>Answer:</h3>
          <p>{result.answer}</p>
          
          <h4>Sources:</h4>
          <ul>
            {result.sources.map((source, idx) => (
              <li key={idx}>
                <strong>{source.filename}</strong> 
                (Score: {source.score.toFixed(3)})
                <p>{source.preview}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## 🌊 Streaming Query (GET /api/stream-query)

### EventSource Streaming Example

```typescript
// utils/streaming.ts

export interface StreamCallbacks {
  onMetadata?: (metadata: StreamMetadata) => void;
  onToken?: (token: string) => void;
  onDone?: (data: StreamDoneData) => void;
  onError?: (error: string) => void;
}

export function streamQuery(
  question: string,
  topK: number = 5,
  callbacks: StreamCallbacks
): () => void {
  const url = new URL(`${API_BASE_URL}/api/stream-query`);
  url.searchParams.set('question', question);
  url.searchParams.set('top_k', topK.toString());
  
  const eventSource = new EventSource(url.toString());
  
  eventSource.addEventListener('metadata', (event) => {
    const metadata = JSON.parse(event.data);
    callbacks.onMetadata?.(metadata);
  });
  
  eventSource.addEventListener('message', (event) => {
    callbacks.onToken?.(event.data);
  });
  
  eventSource.addEventListener('done', (event) => {
    const data = JSON.parse(event.data);
    callbacks.onDone?.(data);
    eventSource.close();
  });
  
  eventSource.addEventListener('error', (event) => {
    const errorData = JSON.parse((event as any).data || '{}');
    callbacks.onError?.(errorData.error || 'Stream error');
    eventSource.close();
  });
  
  eventSource.onerror = () => {
    callbacks.onError?.('Connection error');
    eventSource.close();
  };
  
  // Return cleanup function
  return () => {
    eventSource.close();
  };
}
```

### React Component with Streaming

```typescript
// components/StreamingQuery.tsx

import { useState, useRef } from 'react';
import { streamQuery, StreamMetadata, SourceItem } from '../utils/streaming';

export function StreamingQuery() {
  const [question, setQuestion] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<SourceItem[]>([]);
  const cleanupRef = useRef<(() => void) | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) return;
    
    // Reset state
    setStreaming(true);
    setAnswer('');
    setSources([]);
    
    // Start streaming
    cleanupRef.current = streamQuery(question, 5, {
      onMetadata: (metadata) => {
        console.log('Received sources:', metadata.sources);
        setSources(metadata.sources);
      },
      onToken: (token) => {
        setAnswer(prev => prev + token);
      },
      onDone: (data) => {
        console.log('Stream complete:', data);
        setStreaming(false);
      },
      onError: (error) => {
        console.error('Stream error:', error);
        setStreaming(false);
        alert(`Error: ${error}`);
      },
    });
  };

  const handleStop = () => {
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }
    setStreaming(false);
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
        {!streaming ? (
          <button type="submit" disabled={!question.trim()}>
            Ask
          </button>
        ) : (
          <button type="button" onClick={handleStop}>
            Stop
          </button>
        )}
      </form>
      
      {(answer || streaming) && (
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
                (Relevance: {(source.score * 100).toFixed(1)}%)
                <p className="text-sm text-gray-600">{source.preview}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## 🎨 Advanced: Chat-like Interface

```typescript
// components/ChatInterface.tsx

import { useState, useRef, useEffect } from 'react';
import { streamQuery, SourceItem } from '../utils/streaming';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceItem[];
  streaming?: boolean;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const cleanupRef = useRef<(() => void) | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || streaming) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };
    
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      streaming: true,
    };
    
    setMessages(prev => [...prev, userMessage, assistantMessage]);
    setInput('');
    setStreaming(true);
    
    cleanupRef.current = streamQuery(input, 5, {
      onMetadata: (metadata) => {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, sources: metadata.sources }
              : msg
          )
        );
      },
      onToken: (token) => {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, content: msg.content + token }
              : msg
          )
        );
      },
      onDone: () => {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, streaming: false }
              : msg
          )
        );
        setStreaming(false);
      },
      onError: (error) => {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, content: `Error: ${error}`, streaming: false }
              : msg
          )
        );
        setStreaming(false);
      },
    });
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="content">
              {msg.content}
              {msg.streaming && '▊'}
            </div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <small>Sources: {msg.sources.map(s => s.filename).join(', ')}</small>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={streaming}
        />
        <button type="submit" disabled={streaming || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
```

## 🛠️ Error Handling

```typescript
// utils/errorHandling.ts

export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.error || errorMessage;
    } catch {
      // If response is not JSON, use status text
    }
    
    throw new APIError(errorMessage, response.status);
  }
  
  return await response.json();
}

// Usage
export async function queryKnowledge(
  question: string,
  topK: number = 5
): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK }),
  });
  
  return handleResponse<QueryResponse>(response);
}
```

## 🔒 CORS Notes

The backend is configured to accept requests from:
- `http://localhost:3000` (Create React App default)
- `http://localhost:5173` (Vite default)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

If you need additional origins, update the CORS configuration in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://your-custom-origin:port"  # Add your origin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Testing API Calls

### Using Fetch API in Browser Console

```javascript
// Test upload
const formData = new FormData();
formData.append('files', document.querySelector('input[type=file]').files[0]);
await fetch('http://localhost:8000/api/upload', { method: 'POST', body: formData })
  .then(r => r.json())
  .then(console.log);

// Test query
await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: 'test', top_k: 5 })
}).then(r => r.json()).then(console.log);

// Test streaming
const es = new EventSource('http://localhost:8000/api/stream-query?question=test');
es.addEventListener('message', e => console.log('Token:', e.data));
es.addEventListener('done', e => { console.log('Done:', e.data); es.close(); });
```

## 📚 Additional Resources

- [EventSource MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Fetch API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [React Hooks Reference](https://react.dev/reference/react)
