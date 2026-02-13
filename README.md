# Brand Guardian – ComplianceQA

An AI-powered video compliance auditing system that analyzes YouTube videos for regulatory violations using Azure services and Large Language Models.

---

## 🚀 Overview

Brand Guardian automates brand and regulatory compliance checks for video content.

The system:

- Downloads YouTube videos
- Extracts transcript and OCR using Azure Video Indexer
- Retrieves regulatory policies from Azure AI Search
- Uses a Large Language Model to analyze compliance
- Returns structured JSON compliance results

This project is designed to demonstrate production-ready AI architecture using Azure and modern LLM tooling.

---

## 🏗 System Architecture

**Pipeline Flow:**

YouTube URL  
→ Azure Video Indexer (Transcript + OCR)  
→ Azure AI Search (Rule Retrieval - RAG)  
→ LLM Compliance Analysis  
→ Structured JSON Report  

---

## 🧠 Tech Stack

**Backend Framework**
- FastAPI
- Uvicorn

**AI & LLM**
- Azure OpenAI (Embeddings)
- Groq LLM (Compliance Analysis)

**Vector Store**
- Azure AI Search (Vector Index)

**Video Intelligence**
- Azure Video Indexer

**Supporting Tools**
- yt-dlp (YouTube download)
- LangChain
- LangGraph

---

## 📁 Project Structure

```
.
├── backend
│   ├── src
│   │   ├── api
│   │   ├── graph
│   │   └── services
│   ├── data
│   └── scripts
├── main.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root.

```
# LLM
GROQ_API_KEY=
GROQ_MODEL_NAME=

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=

# Azure AI Search
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=

# Azure Video Indexer
AZURE_VI_NAME=
AZURE_VI_LOCATION=
AZURE_VI_ACCOUNT_ID=
AZURE_SUBSCRIPTION_ID=
AZURE_RESOURCE_GROUP=

# Monitoring (Optional)
APPLICATIONINSIGHTS_CONNECTION_STRING=
```

---

## ⚙ Installation

1. Clone the repository

```
git clone <your-repo-url>
cd ComplianceQA
```

2. Create and activate virtual environment

```
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

---

## ▶ Running the API Server

```
uvicorn backend.src.api.server:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

---

## 📡 Example API Request

POST request to:

```
/audit
```

### Request Body

```json
{
  "video_url": "https://youtu.be/your-video-id"
}
```

### Example Response

```json
{
  "session_id": "uuid",
  "video_id": "vid_xxx",
  "status": "PASS | FAIL",
  "final_report": "Summary of compliance findings",
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "Violation description"
    }
  ]
}
```

---


## 📌 Notes

- Ensure Azure AI Search index dimensions match embedding model (1536 for text-embedding-3-small).
- Azure Video Indexer processing may take several minutes for large videos.
- Production deployment should secure API keys via a secret manager.

---

## 📄 License

This project is for educational and portfolio purposes.