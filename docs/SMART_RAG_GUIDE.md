# 🎯 Smart RAG System - Usage Guide

## ✅ What's New - Option A Implementation

Your RAG system now has **Smart Detection** with clean, professional answers!

---

## 🚀 Key Features

### 1. **Clean Answers** (No More Technical Junk!)
**Before:**
```
According to Document: SANDEEP_resume.pdf (Relevance Score: 0.717), the candidate has experience with Python...
```

**After:**
```
The candidate has extensive experience with Python, Java, and Spring Boot. He has worked on an online course management system and social media data mining projects.

Source: SANDEEP_resume.pdf
```

✅ No relevance scores in answers
✅ Clean, natural language
✅ Professional tone
✅ Source mentioned cleanly at the end

---

### 2. **Smart Detection** (Automatic Mode Selection)

The system automatically detects if your question needs documents or general knowledge:

#### **Document-Related Questions** → Uses Uploaded Documents
- "Summarize my resume"
- "What does the document say about..."
- "Describe this report"
- "What is mentioned in the file?"
- "According to the document..."
- "Explain this"

#### **General Questions** → Uses AI Knowledge
- "What is Python?"
- "Explain machine learning"
- "How does React work?"
- "What are the benefits of AI?"

---

## 📖 How to Use

### **Scenario 1: Working with Documents**

```bash
# 1. Clear old documents (fresh start)
Invoke-WebRequest -Uri "http://localhost:8000/api/documents/clear-all" -Method DELETE

# 2. Upload your document at http://localhost:8080

# 3. Ask document-specific questions:
```

**Questions that use YOUR document:**
- ✅ "Summarize this resume"
- ✅ "What projects are mentioned?"
- ✅ "Describe the candidate's experience"
- ✅ "What skills does this person have?"
- ✅ "Tell me about this document"

---

### **Scenario 2: General Questions (No Documents Needed)**

Just ask! The system knows when NOT to use documents:

**Questions that use general AI knowledge:**
- ✅ "What is artificial intelligence?"
- ✅ "Explain what Python is used for"
- ✅ "How does machine learning work?"
- ✅ "What are the benefits of cloud computing?"

No need to upload documents for these!

---

### **Scenario 3: Mixed Usage**

The system is smart enough to handle both:

```
1. Upload your resume
2. Ask: "Summarize my resume" → Uses your document
3. Ask: "What is Python?" → Uses general knowledge
4. Ask: "Based on the resume, is this person qualified for Python roles?" → Uses your document
```

---

## 🎓 Understanding Smart Detection

### Keywords that Trigger Document Mode:

The system looks for these words to know you want document-specific answers:

- **Direct references:** "document", "file", "pdf", "this", "resume", "report"
- **Actions:** "summarize", "describe", "explain this", "tell me about this"
- **Context clues:** "according to", "in the", "from the", "based on", "mentioned"
- **Content:** "what does it say", "what is in", "information about", "details about"

### Examples:

| Question | Mode | Why? |
|----------|------|------|
| "Summarize my resume" | 📄 Document | Contains "summarize" + "resume" |
| "What is Python?" | 🤖 General | No document keywords |
| "What does the report say?" | 📄 Document | Contains "report" + "say" |
| "Explain machine learning" | 🤖 General | General technical topic |
| "Describe this document" | 📄 Document | Contains "describe" + "document" |

---

## 💡 Pro Tips

### 1. **Get Better Document Answers**

Be specific:
- ❌ "Tell me" (vague)
- ✅ "Summarize the key skills in this resume"
- ✅ "What projects are described in the document?"
- ✅ "Explain the candidate's experience with Python"

### 2. **Force General Knowledge**

Remove document-specific words:
- ❌ "What is Python mentioned in this document?" (uses document)
- ✅ "What is Python?" (uses general knowledge)

### 3. **Keep Documents Clean**

Always clear before uploading new topics:
```powershell
# Check what's stored
Invoke-WebRequest -Uri "http://localhost:8000/api/documents/stats"

# Clear everything
Invoke-WebRequest -Uri "http://localhost:8000/api/documents/clear-all" -Method DELETE

# Or remove specific file
Invoke-WebRequest -Uri "http://localhost:8000/api/documents/filename/old_file.pdf" -Method DELETE
```

### 4. **Verify Source Usage**

Check the metadata in the response:
```json
{
  "answer": "The candidate has...",
  "sources": [...],
  "metadata": {
    "mode": "rag",           // or "general" or "general_fallback"
    "retrieved_docs": 5,
    "question": "..."
  }
}
```

**Modes:**
- `rag` = Used documents
- `general` = Used AI knowledge (no documents)
- `general_fallback` = Tried documents but none relevant, used AI knowledge

---

## 🔧 Advanced: Force Document Mode

If you want to ALWAYS use documents (even for general questions):

### API:
```json
POST /api/query
{
  "question": "What is Python?",
  "force_documents": true
}
```

This will search your uploaded documents for "Python" information instead of using general knowledge.

---

## 📊 API Reference

### 1. Standard Query
```http
POST /api/query
Content-Type: application/json

{
  "question": "Summarize my resume",
  "top_k": 5,
  "force_documents": false
}
```

**Response:**
```json
{
  "answer": "Clean answer here...\n\nSource: SANDEEP_resume.pdf",
  "sources": [
    {
      "filename": "SANDEEP_resume.pdf",
      "chunk_id": "0_1",
      "score": 0.85,
      "preview": "First 200 chars..."
    }
  ],
  "metadata": {
    "mode": "rag",
    "retrieved_docs": 5,
    "question": "Summarize my resume"
  }
}
```

### 2. Streaming Query
```http
GET /api/stream-query?question=Summarize%20my%20resume&top_k=5&force_documents=false
```

Returns SSE (Server-Sent Events) stream.

### 3. Document Management
```http
# Get stats
GET /api/documents/stats

# Clear all
DELETE /api/documents/clear-all

# Delete specific file
DELETE /api/documents/filename/my_file.pdf
```

---

## 🎯 Quick Start Workflow

### **For Document Q&A:**
```powershell
# 1. Clear old stuff
Invoke-WebRequest -Uri "http://localhost:8000/api/documents/clear-all" -Method DELETE

# 2. Upload your file at http://localhost:8080

# 3. Ask questions like:
#    - "Summarize this document"
#    - "What are the key points?"
#    - "Describe the content"
```

### **For General Questions:**
Just ask! No setup needed:
```
- "What is AI?"
- "Explain Python"
- "How does React work?"
```

---

## 🐛 Troubleshooting

### Issue: "Still seeing old document information"
**Solution:** Clear documents
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/documents/clear-all" -Method DELETE
```

### Issue: "Using documents when I want general knowledge"
**Solution:** Rephrase without document keywords
- ❌ "What does this document say about Python?"
- ✅ "What is Python?"

### Issue: "Using general knowledge when I want my documents"
**Solution:** Add document keywords
- ❌ "Tell me about Python skills"
- ✅ "What Python skills are mentioned in this resume?"

### Issue: "Answer not detailed enough"
**Solution:** Be more specific
- ❌ "Summarize"
- ✅ "Provide a detailed summary of the candidate's technical skills, projects, and experience"

---

## 🎉 Example Interactions

### **Example 1: Resume Analysis**
```
Q: "Summarize my resume"
A: "The candidate is a skilled software developer with expertise in Python, Java, 
and Spring Boot. He has completed several projects including an online course 
management system and social media data mining application. He holds certifications 
in Data Analytics and placed among the top 200 teams in Flipkart GRiD 6.0.

Source: SANDEEP_resume.pdf"
```

### **Example 2: General Knowledge**
```
Q: "What is Python?"
A: "Python is a high-level, interpreted programming language known for its simplicity 
and readability. It's widely used for web development, data analysis, artificial 
intelligence, scientific computing, and automation. Python emphasizes code readability 
and allows programmers to express concepts in fewer lines of code."
```

### **Example 3: Mixed Context**
```
Q: "Based on the resume, is this person qualified for Python development roles?"
A: "Yes, based on the resume, this candidate is well-qualified for Python development 
roles. They have demonstrated Python expertise through multiple projects and possess 
additional skills in frameworks and libraries commonly used in Python development.

Source: SANDEEP_resume.pdf"
```

---

## ✅ Summary

| Feature | Status |
|---------|--------|
| Clean answers (no scores) | ✅ Implemented |
| Smart document detection | ✅ Implemented |
| General knowledge fallback | ✅ Implemented |
| Source citations | ✅ Clean format |
| Document management | ✅ Full API |
| Relevance filtering (>0.7) | ✅ Active |
| Larger chunks (1000 chars) | ✅ Active |

**Your system is now production-ready!** 🚀

---

**Questions? Check the logs or API docs at http://localhost:8000/docs**
