# Quick Guide: Using the Improved RAG System

## 🎯 What Changed?

Your system now gives **precise, accurate answers** instead of vague ones!

## 🚀 How to Use for Best Results

### Option 1: Fresh Start (Recommended)
```bash
# 1. Clear old documents
curl -X DELETE http://localhost:8000/api/documents/clear-all

# 2. Upload your NEW document
# Use the UI or drag & drop at http://localhost:8080

# 3. Ask questions!
```

### Option 2: Remove Specific Old Document
```bash
# If you know the filename causing issues:
curl -X DELETE http://localhost:8000/api/documents/filename/old_report.pdf
```

## 📊 Check What's in Your System
```bash
curl http://localhost:8000/api/documents/stats
```

## ✅ Testing It

1. **Clear all documents** (fresh start)
2. **Upload ONE document**
3. **Ask a question about that document**
4. **Verify**: Answer should ONLY reference that document

## 🎯 Key Improvements

| Before | After |
|--------|-------|
| Small chunks (512 chars) | Larger chunks (1000 chars) |
| No quality filtering | Only high-relevance results (>0.7) |
| Mixed old/new documents | Can clear specific documents |
| Used external knowledge | STRICT context-only answers |
| Vague answers | Precise with source citations |

## 🔧 New Endpoints

- `GET /api/documents/stats` - See what's stored
- `DELETE /api/documents/filename/{name}` - Remove specific file
- `DELETE /api/documents/clear-all` - Fresh start

## 💡 Pro Tip

**For each new topic/project**:
1. Clear all documents
2. Upload only relevant files
3. Get focused, accurate answers

---

**The system is now running with these improvements!** 🎉
**Try it at: http://localhost:8080**
