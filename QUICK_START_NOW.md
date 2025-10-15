# 🚀 Quick Start - Get KnowledgeExplorer Working NOW!

## The Problem Is FIXED! ✅

Your frontend was using fake/mock data. I've updated it to use the real backend API.

**But** you still need to configure API keys for it to work!

## 2-Minute Setup

### Option 1: Interactive Setup (Recommended)

```powershell
cd "c:\Users\User\Unthinkable 2.0\knowledge-spark-38-main"
.\setup-wizard.ps1
```

Follow the prompts to configure your API keys.

### Option 2: Manual Setup (Fast)

1. **Edit `.env` file** with your API keys:

```env
GROQ_API_KEY=gsk_YOUR_KEY_HERE
PINECONE_API_KEY=YOUR_KEY_HERE
PINECONE_ENV=us-east-1-aws
PINECONE_INDEX=knowledge-explorer
JINA_API_KEY=YOUR_KEY_HERE  # Optional
```

2. **Create Pinecone Index**:
   - Go to https://app.pinecone.io/
   - Create index: `knowledge-explorer`
   - Dimensions: **768** ← Important!
   - Metric: cosine

3. **Restart Backend**:

```powershell
# Stop current backend (Ctrl+C)
python main.py
```

4. **Refresh Frontend**: Press Ctrl+Shift+R in browser

5. **Test It**:
   - Upload a PDF/TXT file
   - Wait for green checkmark
   - Ask a question
   - Get REAL answer! 🎉

## Where to Get API Keys

| Service | URL | Required? | Why? |
|---------|-----|-----------|------|
| **Groq** | https://console.groq.com/keys | ✅ YES | LLM for answers |
| **Pinecone** | https://app.pinecone.io/ | ✅ YES | Store document vectors |
| **Jina AI** | https://jina.ai/ | ⚠️ Optional | Better embeddings (or use local) |

## Verification

After setup, check if it's working:

```powershell
# Backend health check
curl http://localhost:8000/health
```

Should show:
```json
{
  "status": "healthy",
  "api_keys": {
    "groq": true,
    "pinecone": true,
    "jina": true
  }
}
```

If any show `false`, that API key is not configured correctly!

## Test Flow

1. **Upload**: Click "Attach Documents" → Upload a file → See green checkmark ✅
2. **Query**: Type "What is this document about?" → Get specific answer
3. **Verify**: Answer should be different for different documents

## Still Getting Generic Responses?

Check these:

1. ❌ API keys configured? → Edit `.env`
2. ❌ Backend restarted? → `python main.py`
3. ❌ Pinecone index created? → https://app.pinecone.io/
4. ❌ Dimensions = 768? → Recreate index if wrong
5. ❌ Browser cache? → Hard refresh (Ctrl+Shift+R)

## Complete Documentation

- **ISSUE_RESOLVED.md** - What was fixed
- **TROUBLESHOOTING.md** - Detailed debugging
- **FULL_STACK_RUNNING.md** - Complete guide
- **BACKEND_README.md** - Backend documentation

## TL;DR

```powershell
# 1. Configure API keys
.\setup-wizard.ps1

# 2. Create Pinecone index (dimensions=768)

# 3. Restart backend
python main.py

# 4. Upload document and ask questions!
```

**The frontend code is already fixed. You just need API keys!** 🔑
