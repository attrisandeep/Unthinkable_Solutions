# 🔧 Troubleshooting Guide

## Issue: Generic/Repetitive Responses

### Problem
The system returns the same generic response regardless of what you upload or ask:
> "Based on the analysis of 0 document(s), here's what I found: The documents contain comprehensive information about the topic you've inquired about..."

### Root Causes & Solutions

#### ✅ FIXED: Frontend Not Calling Backend API

**Problem**: The frontend was using a hardcoded mock response instead of calling the backend.

**Solution**: Updated `src/pages/Index.tsx` and `src/components/FileUpload.tsx` to use the real API from `src/lib/api.ts`.

**Files Changed**:
- ✅ `src/pages/Index.tsx` - Now calls `apiQuery()` from `@/lib/api`
- ✅ `src/components/FileUpload.tsx` - Now calls `apiUploadFiles()` from `@/lib/api`

---

#### ⚠️ ACTION REQUIRED: Configure API Keys

**Problem**: The `.env` file contains placeholder values for API keys.

**Current State**:
```env
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
JINA_API_KEY=your_jina_api_key_here
```

**Solution**: Get real API keys and update the `.env` file:

### Step 1: Get Your API Keys

#### 1. Groq API Key (Required - for LLM)
1. Go to: https://console.groq.com/keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `gsk_...`)

#### 2. Pinecone API Key (Required - for vector storage)
1. Go to: https://app.pinecone.io/
2. Sign up or log in
3. Create a new index named `knowledge-explorer`
   - Dimensions: **768** (for Jina embeddings)
   - Metric: **cosine**
   - Region: **us-east-1** (or your preferred region)
4. Get your API key from the dashboard
5. Note your environment (e.g., `us-east-1-aws`)

#### 3. Jina AI API Key (Optional - for better embeddings)
1. Go to: https://jina.ai/
2. Sign up or log in
3. Get your API key
4. **Note**: If you skip this, the system will use local sentence-transformers (slower but free)

### Step 2: Update `.env` File

Edit `c:\Users\User\Unthinkable 2.0\knowledge-spark-38-main\.env`:

```env
# Groq API Configuration
GROQ_API_KEY=gsk_YOUR_ACTUAL_GROQ_KEY_HERE
GROQ_MODEL=mixtral-8x7b-32768
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=2048

# Pinecone Configuration
PINECONE_API_KEY=YOUR_ACTUAL_PINECONE_KEY_HERE
PINECONE_ENV=us-east-1-aws  # or your region
PINECONE_INDEX=knowledge-explorer

# Jina AI Configuration (optional)
JINA_API_KEY=YOUR_ACTUAL_JINA_KEY_HERE
# Or leave as placeholder to use local embeddings
```

### Step 3: Restart the Backend

After updating `.env`, restart the backend:

```powershell
# Stop the current backend (Ctrl+C in the terminal)
# Then restart:
cd "c:\Users\User\Unthinkable 2.0\knowledge-spark-38-main"
python main.py
```

You should see:
```
✅ API Keys validated: {'groq': True, 'pinecone': True, 'jina': True}
```

### Step 4: Test the System

1. **Open Frontend**: http://localhost:8080
2. **Upload a document**: Click "Attach Documents" and upload a PDF or TXT file
3. **Wait for processing**: You'll see "Uploaded" status when complete
4. **Ask a question**: Type a question about your document
5. **Get real answer**: The system should now analyze your document and provide a real answer!

---

## Verification Checklist

Use this checklist to verify everything is working:

### Backend Status
```powershell
# Health check
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "api_keys": {
    "groq": true,
    "pinecone": true,
    "jina": true  // or false if using local embeddings
  }
}
```

### Frontend Status
- [ ] Frontend running on http://localhost:8080
- [ ] Can access the page without errors
- [ ] File upload button appears
- [ ] Query input box is visible

### API Integration
- [ ] File upload shows "Uploading..." status
- [ ] File upload shows "Uploaded" when complete
- [ ] Backend logs show: `📄 Processing file: your_file.pdf`
- [ ] Backend logs show: `✅ Successfully upserted X vectors`

### Query Functionality
- [ ] Typing a question doesn't show generic response
- [ ] Answer changes based on document content
- [ ] Different questions give different answers
- [ ] Sources are shown below the answer

---

## Common Issues

### Issue: "Failed to upload files to backend"

**Cause**: Backend not running or wrong URL

**Fix**:
```powershell
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
cd "c:\Users\User\Unthinkable 2.0\knowledge-spark-38-main"
python main.py
```

### Issue: "401 Unauthorized" or "Invalid API Key"

**Cause**: API keys not configured correctly

**Fix**:
1. Double-check your API keys in `.env`
2. Make sure there are no extra spaces
3. Restart the backend after changing `.env`

### Issue: Still getting generic responses after fixing

**Cause**: Browser cache or old state

**Fix**:
1. Hard refresh the browser (Ctrl+Shift+R)
2. Clear browser cache
3. Restart both frontend and backend

### Issue: "Pinecone index not found"

**Cause**: Pinecone index doesn't exist

**Fix**:
1. Go to https://app.pinecone.io/
2. Create a new index:
   - Name: `knowledge-explorer`
   - Dimensions: **768**
   - Metric: **cosine**
3. Update `PINECONE_INDEX` in `.env` if you used a different name

### Issue: Slow embedding generation

**Cause**: Using local sentence-transformers without Jina API key

**Fix**:
- Get a Jina AI API key for faster cloud embeddings
- Or wait longer (local embeddings can take 10-30 seconds for large documents)

---

## Debug Mode

To see what's happening in detail:

### Enable Backend Debug Logs

Edit `.env`:
```env
LOG_LEVEL=DEBUG
```

Restart backend to see detailed logs:
- Embedding generation
- Vector storage operations
- LLM API calls
- Retrieved document chunks

### Check Browser Console

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for API calls and errors
4. Check Network tab for failed requests

### Test Backend Directly

Test without frontend:

```powershell
# Upload a file
curl -X POST http://localhost:8000/api/upload -F "files=@test.txt"

# Query
curl -X POST http://localhost:8000/api/query `
  -H "Content-Type: application/json" `
  -d '{"question":"What is in the document?","top_k":5}'
```

---

## Quick Fix Summary

**If you're still seeing generic responses:**

1. ✅ Frontend code updated (already done)
2. ⚠️ **Update API keys in `.env` file** (YOU NEED TO DO THIS)
3. ⚠️ **Restart backend** (after updating .env)
4. ⚠️ **Create Pinecone index** (if not exists)
5. Hard refresh browser (Ctrl+Shift+R)
6. Upload a new document
7. Ask a question

**The main issue is**: The frontend was using mock data, which is now fixed. But you still need to configure real API keys for the backend to work properly!

---

## Still Having Issues?

Check these files for errors:

1. **Backend Terminal**: Look for error messages
2. **Frontend Terminal**: Look for build/runtime errors
3. **Browser Console**: Look for API call failures
4. **Backend Logs**: See `LOG_LEVEL=DEBUG` in `.env`

Common log messages to look for:

✅ Good:
- `✅ API Keys validated`
- `📄 Processing file: your_file.pdf`
- `✅ Successfully upserted X vectors`
- `🔍 Retrieved X documents`

❌ Bad:
- `❌ Invalid API key`
- `Error: Pinecone index not found`
- `Failed to embed text`
- `Connection refused`
