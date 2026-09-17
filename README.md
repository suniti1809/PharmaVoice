# 💊 PharmaVoice — AI Customer Complaint Management System

> **AI-powered customer complaint intake, risk assessment, duplicate detection, and CAPA support for pharmaceutical quality management.**

PharmaVoice is an AI-assisted **Customer Complaint Management System (QMS)** designed for pharmaceutical organizations.

It converts unstructured customer complaints received through emails, documents, or pasted text into structured complaint records and supports quality teams with:

- AI-powered field extraction
- Complaint completeness checking
- Risk assessment
- Duplicate complaint detection
- Root-cause suggestions
- CAPA recommendations
- Grounded complaint Q&A
- Human-in-the-loop review
- Complaint record management

The system combines a modern **React + Vite frontend**, **FastAPI backend**, **LangGraph AI workflow**, **Groq LLM integration**, and **PostgreSQL database**.

---

# 🚀 Live Demo

## 🌐 Live Application

**Frontend:**  
https://pharmavoice-sp14.onrender.com

## ⚙️ Backend API

**Backend:**  
https://pharmavoice-api.onrender.com



## 📚 API Documentation

**Swagger / OpenAPI:**  
https://pharmavoice-api.onrender.com/docs

### ❤️ API Health Check
https://pharmavoice-api.onrender.com/api/health

---

# ✨ Key Features

## 📩 Complaint Intake

PharmaVoice supports multiple complaint input formats:

- Paste complaint text directly
- Upload PDF documents
- Upload DOCX documents
- Upload EML email files
- Upload TXT files
- Process structured complaint information

The system converts unstructured complaint content into a structured complaint record.

---

## 🤖 AI-Powered Field Extraction

The AI workflow extracts important complaint information such as:

- Complaint description
- Product information
- Batch number
- Customer information
- Event date
- Location
- Product issue
- Reported symptoms
- Supporting information

Extracted information can include confidence levels to help reviewers understand the reliability of the extraction.

---

## 📝 Complaint Completeness Check

Before saving a complaint, PharmaVoice checks whether important information is missing.

The system can:

- Identify incomplete fields
- Highlight missing information
- Generate follow-up questions
- Help reviewers collect additional details

This helps reduce incomplete complaint records.

---

## ⚠️ Risk Assessment

PharmaVoice evaluates complaints using a structured risk assessment workflow.

It provides:

- Severity
- Priority
- Risk score
- Possible root causes
- Recommended actions
- CAPA suggestions

The risk score is represented on a **0–100 scale**.

---

## 🔍 Duplicate Complaint Detection

The system checks whether a new complaint may already exist in the complaint register.

Duplicate detection can compare information such as:

- Product
- Batch
- Complaint description
- Customer information
- Complaint characteristics

Potential duplicates are flagged for human review.

---

## 🧠 AI Root-Cause & CAPA Suggestions

Based on complaint information, PharmaVoice can provide:

- Possible root causes
- Investigation directions
- Corrective actions
- Preventive actions
- CAPA recommendations

These recommendations are intended as **decision support** and require human review before operational use.

---

## 💬 Grounded Complaint Q&A

Users can ask questions about complaint information.

Example:

> **Which batch is affected?**

The system provides answers based on the available complaint information.

---

## 📋 Complaint Register

Saved complaints receive complaint IDs following the format:

```text
CC-YYYY-NNNN
```

Example:

```text
CC-2026-0001
```

The complaint register helps users review and manage submitted complaints.

---

## 👤 Human Review

PharmaVoice follows a **human-in-the-loop workflow**.

AI-generated information can be reviewed and corrected before a complaint is finally saved.

Quality personnel can verify:

- Extracted fields
- Risk assessment
- Duplicate flags
- Root causes
- CAPA suggestions

---

# 🧠 AI Workflow

```text
Customer Complaint
        │
        ▼
┌─────────────────────┐
│ Complaint Intake    │
│ PDF / DOCX / EML    │
│ TXT / Pasted Text   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Text Extraction     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ AI Field Extraction │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Completeness Check  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Risk Assessment     │
└──────────┬──────────┘
           │
           ├───────────────┐
           ▼               ▼
┌─────────────────┐  ┌──────────────────┐
│ Duplicate Check │  │ Root Cause / CAPA│
└────────┬────────┘  └────────┬─────────┘
         │                    │
         └──────────┬─────────┘
                    ▼
          ┌──────────────────┐
          │ Human Review     │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Complaint Record │
          └──────────────────┘
```

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      User / QMS      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ React + Vite         │
                    │ Frontend / Render    │
                    └──────────┬───────────┘
                               │
                            REST API
                               │
                               ▼
                    ┌──────────────────────┐
                    │ FastAPI Backend      │
                    │ Render               │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
       ┌────────────────┐ ┌───────────┐ ┌──────────────┐
       │ LangGraph      │ │ SQLAlchemy│ │ Complaint    │
       │ AI Workflow    │ │ ORM       │ │ Services     │
       └───────┬────────┘ └─────┬─────┘ └──────────────┘
               │                │
               ▼                ▼
        ┌──────────────┐  ┌──────────────┐
        │ Groq LLM     │  │ PostgreSQL   │
        │ Optional     │  │ / SQLite     │
        └──────────────┘  └──────────────┘
```

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 |
| Build Tool | Vite |
| State Management | Redux Toolkit |
| UI | Inter Font + Dark UI |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| AI Workflow | LangGraph |
| LLM | Groq |
| Database | PostgreSQL / SQLite |
| API | REST |
| Deployment | Render |
| Languages | Python + JavaScript |

---

# 📁 Project Structure

```text
PharmaVoice/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── routers/
│   │   ├── services/
│   │   └── ...
│   │
│   ├── index.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   └── assets/
│   │
│   ├── index.html
│   ├── package.json
│   └── package-lock.json
│
├── render.yaml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

# ⚙️ Local Installation

## 1. Clone the Repository

```bash
git clone https://github.com/suniti1809/PharmaVoice.git
cd PharmaVoice
```

---

# 2. Backend Setup

Open a terminal and navigate to the backend:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

### Windows

Activate the environment:

```bash
.venv\Scripts\activate
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI backend:

```bash
uvicorn index:app --reload --port 8000
```

Backend will run at:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/api/health
```

---

# 3. Frontend Setup

Open another terminal from the project root:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

Frontend will normally run at:

```text
http://localhost:5173
```

---

# 🔐 Environment Variables

Create a `.env` file according to `.env.example`.

Example:

```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=
AUTO_SEED=true
```

## GROQ_API_KEY

The Groq API key enables Groq-powered AI processing.

If the API key is unavailable, PharmaVoice can use its **rule-based fallback mode**.

## DATABASE_URL

Database connection string.

For local development, the application can use SQLite according to the project configuration.

For deployed environments, PostgreSQL is used for persistent database storage.

## AUTO_SEED

Controls whether sample complaint data is automatically seeded.

Example:

```env
AUTO_SEED=true
```

> Never commit `.env` files or API keys to GitHub.

---

# 🤖 AI Processing Modes

PharmaVoice supports two processing modes.

## With Groq API Key

```text
Complaint
   ↓
LangGraph Workflow
   ↓
Groq LLM
   ↓
Extraction / Risk / CAPA
   ↓
Human Review
```

## Without Groq API Key

```text
Complaint
   ↓
Rule-Based Processing
   ↓
Structured Result
   ↓
Human Review
```

The rule-based fallback allows the application to remain usable when an external LLM API key is not configured.

---

# ☁️ Render Deployment

PharmaVoice is deployed on **Render** using separate frontend, backend, and PostgreSQL services.

## Deployment Architecture

```text
                    GitHub Repository
                           │
                           ▼
                    ┌──────────────┐
                    │    Render    │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
   ┌────────────────┐ ┌──────────────┐ ┌──────────────┐
   │ React Frontend │ │ FastAPI      │ │ PostgreSQL   │
   │ Static Site    │ │ Backend      │ │ Database     │
   └────────────────┘ └──────────────┘ └──────────────┘
             │                │
             └──── REST API ──┘
```

Deployment configuration is defined in:

```text
render.yaml
```

---

# Backend Render Configuration

```text
Root Directory:
backend
```

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn index:app --host 0.0.0.0 --port $PORT
```

Health check:

```text
/api/health
```

---

# Frontend Render Configuration

```text
Root Directory:
frontend
```

Build command:

```bash
npm ci && npm run build
```

Publish directory:

```text
dist
```

---

# Database Configuration

The deployed application uses PostgreSQL through:

```env
DATABASE_URL
```

The database connection is configured through the Render Blueprint.

The application also supports SQLite for local development and testing.

---

# 🗄️ Database

PharmaVoice supports two database options.

## SQLite

Useful for:

- Local development
- Testing
- Demonstrations

## PostgreSQL

Used for the deployed application to provide persistent database storage.

Database configuration is provided through:

```env
DATABASE_URL
```

---

# 🧪 Testing

Backend tests can be run from the `backend` directory:

```bash
pytest
```

Quick backend verification:

```text
GET /api/health
```

Local Swagger documentation:

```text
http://localhost:8000/docs
```

Deployed Swagger documentation:

```text
https://pharmavoice-api.onrender.com/docs
```

---

# 🧾 Sample Complaint Workflow

A typical workflow can be demonstrated using:

### 1. Seeded Complaints

Use the sample complaint records available in the project.

### 2. Complaint Intake

Paste complaint text or upload a supported document.

### 3. AI Extraction

Review the extracted complaint fields and confidence information.

### 4. Completeness Check

Check missing information and generated follow-up questions.

### 5. Risk Assessment

Review severity, priority, risk score, and suggested actions.

### 6. Duplicate Detection

Check whether the complaint matches an existing complaint.

### 7. Root Cause & CAPA

Review suggested root causes and CAPA recommendations.

### 8. Human Review

Verify and correct AI-generated information.

### 9. Save

Save the verified complaint to the complaint register.

---

# 🔎 Example Complaint ID

Saved complaints follow:

```text
CC-YYYY-NNNN
```

Examples:

```text
CC-2026-0001
CC-2026-0002
CC-2026-0003
```

---

# 📚 API Documentation

The deployed API documentation is available through FastAPI Swagger/OpenAPI:

```text
https://pharmavoice-api.onrender.com/docs
```

The documentation allows developers to explore and test the available API routes.

Health check:

```text
https://pharmavoice-api.onrender.com/api/health
```

The API includes functionality related to:

- Complaint intake
- Complaint management
- Risk assessment
- Duplicate detection
- Complaint Q&A
- AI processing

---

# 🔒 Security Notes

- Store API keys using environment variables.
- Do not commit `.env` files.
- Do not expose `GROQ_API_KEY` in frontend code.
- Use HTTPS for deployed services.
- Keep AI-generated recommendations under human review.
- Use appropriate authentication and access controls before production use.

---

# 📌 Production Note

PharmaVoice is an AI-assisted QMS application and should be treated as a **decision-support system**.

AI-generated:

- Extracted information
- Risk assessments
- Root causes
- CAPA suggestions
- Duplicate indications

should be reviewed by authorized personnel before being used in an actual pharmaceutical quality process.

---

# 🎯 Project Highlights

- AI-assisted pharmaceutical complaint management
- Multi-format complaint intake
- PDF, DOCX, EML, and TXT support
- Automated field extraction
- Confidence-aware extraction
- Complaint completeness checking
- Follow-up question generation
- Risk scoring
- Severity and priority assessment
- Duplicate complaint detection
- Root-cause suggestions
- CAPA recommendations
- Grounded complaint Q&A
- Human-in-the-loop review
- Complaint register
- LangGraph workflow
- Groq LLM integration
- Rule-based fallback
- React + FastAPI architecture
- PostgreSQL database
- Render deployment

---

# 🔄 End-to-End Workflow

```text
User
 │
 ▼
Complaint Input
 │
 ├── Paste Text
 ├── PDF
 ├── DOCX
 ├── EML
 └── TXT
 │
 ▼
Text Processing
 │
 ▼
AI Extraction
 │
 ▼
Completeness Check
 │
 ▼
Follow-up Questions
 │
 ▼
Risk Assessment
 │
 ├── Severity
 ├── Priority
 └── Risk Score
 │
 ▼
Duplicate Detection
 │
 ▼
Root Cause Analysis
 │
 ▼
CAPA Suggestions
 │
 ▼
Human Review
 │
 ▼
Complaint Register
 │
 ▼
CC-YYYY-NNNN
```

---

# 💻 Development

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn index:app --reload --port 8000
```

---

# 🌐 Links

## Live Application

https://pharmavoice-sp14.onrender.com

## Backend API

https://pharmavoice-api.onrender.com

## API Documentation

https://pharmavoice-api.onrender.com/docs

## GitHub Repository

https://github.com/suniti1809/PharmaVoice

---

# 👩‍💻 Developer

**Suniti**

GitHub Profile:

https://github.com/suniti1809

Project Repository:

https://github.com/suniti1809/PharmaVoice

---

# 📄 License

This project is intended for educational, demonstration, and project-development purposes.

---

<div align="center">

### 💊 PharmaVoice

**AI-assisted Customer Complaint Management for Pharmaceutical Quality Systems**

Built with React • FastAPI • LangGraph • Groq • SQLAlchemy • PostgreSQL • Render

</div>
