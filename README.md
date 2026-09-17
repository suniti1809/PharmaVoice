# 💊 PharmaVoice — AI Customer Complaint Management System

> **AI-powered customer complaint intake, risk assessment, duplicate detection, and CAPA support for pharmaceutical quality management.**

PharmaVoice is an AI-assisted **Customer Complaint Management System (QMS)** designed for pharmaceutical organizations. It converts unstructured customer complaints from emails, documents, or pasted text into structured complaint records and supports quality teams with **field extraction, completeness checking, risk assessment, duplicate detection, root-cause suggestions, CAPA recommendations, and grounded Q&A**.

The system combines a modern React frontend with a FastAPI backend, LangGraph-based AI workflows, and database support for complaint management.

---

## 🚀 Live Demo

### 🌐 Live Application

**Frontend:**
`https://pharmavoice-sp14.onrender.com`

### ⚙️ Backend API

**Backend:**
`https://pharmavoice-api.onrender.com`

### 📚 API Documentation

`https://pharmavoice-api.onrender.com/docs`

---

## ✨ Key Features

### 📩 Complaint Intake

PharmaVoice supports multiple complaint input formats:

* Paste complaint text directly
* Upload PDF documents
* Upload DOCX documents
* Upload EML email files
* Upload TXT files
* Process structured complaint information

The system converts unstructured complaint content into a structured complaint record.

---

### 🤖 AI-Powered Field Extraction

The AI workflow extracts important complaint information such as:

* Complaint description
* Product information
* Batch number
* Customer information
* Event date
* Location
* Product issue
* Reported symptoms
* Supporting information

Each extracted field can include a **confidence level** to help the reviewer understand the reliability of the extraction.

---

### 📝 Complaint Completeness Check

Before saving a complaint, PharmaVoice checks whether important information is missing.

The system can:

* Identify incomplete fields
* Highlight missing information
* Generate follow-up questions
* Help the reviewer collect additional details

This helps reduce incomplete complaint records.

---

### ⚠️ Risk Assessment

PharmaVoice evaluates complaints using a structured risk assessment workflow.

It provides:

* Severity
* Priority
* Risk score
* Possible root causes
* Recommended actions
* CAPA suggestions

The risk score is represented on a **0–100 scale**.

---

### 🔍 Duplicate Complaint Detection

The system checks whether a new complaint may already exist in the complaint register.

Duplicate detection can compare information such as:

* Product
* Batch
* Complaint description
* Customer information
* Complaint characteristics

Potential duplicates are flagged for human review.

---

### 🧠 AI Root-Cause & CAPA Suggestions

Based on the complaint information, PharmaVoice can provide:

* Possible root causes
* Investigation directions
* Corrective actions
* Preventive actions
* CAPA recommendations

These recommendations are intended as **decision support** and require human review before being used operationally.

---

### 💬 Grounded Complaint Q&A

Users can ask questions about complaint information.

Example:

> **Which batch is affected?**

The system provides answers based on the available complaint information instead of relying only on general AI knowledge.

---

### 📋 Complaint Register

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

### 👤 Human Review

PharmaVoice keeps a **human-in-the-loop workflow**.

AI-generated information can be reviewed and corrected before a complaint is finally saved.

This allows quality personnel to verify:

* Extracted fields
* Risk assessment
* Duplicate flags
* Root causes
* CAPA suggestions

---

## 🧠 AI Workflow

The core workflow follows a structured pipeline:

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

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      User / QMS      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ React + Vite Frontend│
                    │      Render          │
                    └──────────┬───────────┘
                               │ REST API
                               ▼
                    ┌──────────────────────┐
                    │ FastAPI Backend      │
                    │      Render          │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
       ┌────────────────┐ ┌───────────┐ ┌──────────────┐
       │ LangGraph      │ │ SQLAlchemy│ │ Complaint    │
       │ AI Workflow    │ │ Database  │ │ Services     │
       └───────┬────────┘ └─────┬─────┘ └──────────────┘
               │                │
               ▼                ▼
        ┌──────────────┐  ┌──────────────┐
        │ Groq LLM     │  │ SQLite /     │
        │ Optional     │  │ PostgreSQL   │
        └──────────────┘  └──────────────┘
```

---

## 🛠️ Technology Stack

| Layer            | Technology           |
| ---------------- | -------------------- |
| Frontend         | React 18             |
| Build Tool       | Vite                 |
| State Management | Redux Toolkit        |
| UI               | Inter Font + Dark UI |
| Backend          | FastAPI              |
| ORM              | SQLAlchemy           |
| AI Workflow      | LangGraph            |
| LLM              | Groq                 |
| Database         | SQLite / PostgreSQL  |
| API              | REST                 |
| Deployment       | Render               |
| Language         | Python + JavaScript  |

---

## 📁 Project Structure

```text
PharmaVoice/
│
├── api/
│   ├── app/
│   │   ├── agents/
│   │   ├── routers/
│   │   ├── services/
│   │   └── ...
│   │
│   ├── sample_data/
│   ├── scripts/
│   ├── tests/
│   ├── index.py
│   |── requirements.txt
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── store/
│   ├── assets/
│   └── ...
│
├── index.html
├── package.json
├── vite.config.js
├── render.yaml
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Local Installation

## 1. Clone the Repository

```bash
git clone https://github.com/suniti1809/pharmavoice.git
cd pharmavoice
```

---

## 2. Install Frontend Dependencies

From the project root:

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

## 3. Setup Backend

Open another terminal:

```bash
cd api
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements-dev.txt
```

---

## 4. Start FastAPI Backend

From the `api` directory:

```bash
uvicorn index:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/api/health
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

### GROQ_API_KEY

Optional API key for Groq-powered AI processing.

If the API key is not provided, the application can use its **rule-based fallback mode**.

### DATABASE_URL

Optional database connection string.

If it is not provided, the application can use SQLite according to the project configuration.

### AUTO_SEED

Controls whether sample complaint data is automatically seeded.

Example:

```env
AUTO_SEED=true
```

---

# 🤖 AI Processing Modes

PharmaVoice supports two processing modes.

### With Groq API Key

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

### Without Groq API Key

```text
Complaint
   ↓
Rule-Based Processing
   ↓
Structured Result
   ↓
Human Review
```

This allows the application to remain usable even when an external LLM API key is not configured.

---

# ☁️ Render Deployment

PharmaVoice is designed to be deployed on **Render** using separate frontend and backend services.

## Deployment Architecture

```text
                    GitHub Repository
                           │
                           ▼
                    ┌──────────────┐
                    │    Render    │
                    └──────┬───────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
   ┌──────────────────┐       ┌──────────────────┐
   │ Frontend         │       │ Backend          │
   │ Render Static    │──────▶│ Render Web       │
   │ Site             │ REST  │ Service          │
   └──────────────────┘ API   └────────┬─────────┘
                                       │
                                       ▼
                              Database / AI
```

---

## Option 1 — Deploy Using `render.yaml`

The repository contains:

```text
render.yaml
```

Push the project to GitHub:

```bash
git add .
git commit -m "Prepare PharmaVoice for Render"
git push origin main
```

Then:

1. Open Render.
2. Connect your GitHub account.
3. Select the `suniti1809/pharmavoice` repository.
4. Choose **Blueprint**.
5. Render reads `render.yaml`.
6. Create the required services.
7. Add environment variables.
8. Deploy.

---

## Backend Render Configuration

The FastAPI backend should use:

```text
Root Directory:
api
```

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn index:app --host 0.0.0.0 --port $PORT
```

---

## Frontend Render Configuration

The React/Vite frontend should use:

```text
Root Directory:
.
```

Build command:

```bash
npm install && npm run build
```

Publish directory:

```text
dist
```

---

## Frontend API Configuration

After deploying the backend, copy its Render URL.

Example:

```text
https://pharmavoice-backend.onrender.com
```

Set the frontend environment variable:

```env
VITE_API_URL=https://pharmavoice-backend.onrender.com
```

Then redeploy the frontend.

---

# 🗄️ Database

PharmaVoice supports:

### SQLite

Useful for:

* Local development
* Testing
* Demonstrations

### PostgreSQL

Recommended for persistent hosted deployment.

The database can be configured using:

```env
DATABASE_URL=your_database_connection_string
```

> Render's ephemeral environments should not be treated as permanent storage for SQLite data. For persistent production-style deployment, use PostgreSQL.

---

# 🧪 Testing

Backend tests can be run from the `api` directory:

```bash
pytest
```

For a quick backend verification:

```text
GET /api/health
```

Swagger/OpenAPI documentation:

```text
/docs
```

---

# 🧾 Sample Complaint Workflow

A typical workflow can be demonstrated using:

### 1. Seeded complaints

Use the sample complaint records available in the project.

### 2. Critical particulate complaint

Upload the sample PDF containing a particulate-related complaint.

### 3. Duplicate complaint

Upload the related EML complaint and verify duplicate detection.

### 4. Incomplete complaint

Use the sample TXT/email complaint and check the generated follow-up questions.

### 5. Complaint Q&A

Example:

```text
Which batch is affected?
```

### 6. Human review

Review the extracted fields, risk information, duplicate indication, and CAPA suggestions.

### 7. Save

Save the verified complaint to the complaint register.

---

# 🔎 Example Complaint ID

Saved complaints follow:

```text
CC-YYYY-NNNN
```

Example:

```text
CC-2026-0001
CC-2026-0002
CC-2026-0003
```

---

# 🔒 Security Notes

* API keys should be stored using environment variables.
* Do not commit `.env` files.
* Do not expose `GROQ_API_KEY` in frontend code.
* Use HTTPS URLs for deployed services.
* Keep AI-generated recommendations under human review.
* Use appropriate authentication and access controls before production use.

---

# 📌 Important Production Note

PharmaVoice is an AI-assisted QMS application and should be treated as a **decision-support system**.

AI-generated:

* Extracted information
* Risk assessments
* Root causes
* CAPA suggestions
* Duplicate indications

should be reviewed by authorized personnel before being used in an actual pharmaceutical quality process.

---

# 🎯 Project Highlights

* AI-assisted pharmaceutical complaint management
* Multi-format complaint intake
* Automated field extraction
* Confidence-aware extraction
* Complaint completeness checking
* Follow-up question generation
* Risk scoring
* Severity and priority assessment
* Duplicate complaint detection
* Root-cause suggestions
* CAPA recommendations
* Grounded complaint Q&A
* Human-in-the-loop review
* Complaint register
* LangGraph workflow
* Groq LLM integration
* Rule-based fallback
* React + FastAPI architecture
* Render deployment support

---

# 📚 API Endpoints

Important endpoints include:

| Endpoint       | Purpose                         |
| -------------- | ------------------------------- |
| `/api/health`  | Backend health check            |
| `/docs`        | Swagger API documentation       |
| Complaint APIs | Complaint intake and management |
| Risk APIs      | Risk assessment                 |
| Duplicate APIs | Duplicate detection             |
| Q&A APIs       | Complaint-related questions     |

The exact available routes can be explored through the Swagger documentation:

```text
YOUR_RENDER_BACKEND_URL/docs
```

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

### Frontend

```bash
npm install
npm run dev
```

### Backend

```bash
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn index:app --reload --port 8000
```

---

# 🌐 Links

### Live Application

`YOUR_RENDER_FRONTEND_URL`

### Backend

`YOUR_RENDER_BACKEND_URL`

### API Documentation

`YOUR_RENDER_BACKEND_URL/docs`

### GitHub Repository

[PharmaVoice Repository](https://github.com/suniti1809/pharmavoice?utm_source=chatgpt.com)

---

# 👩‍💻 Developer

**Suniti**

GitHub Profile:
[@suniti1809](https://github.com/suniti1809)

Project Repository:
[PharmaVoice on GitHub](https://github.com/suniti1809/pharmavoice)

---

# 📄 License

This project is intended for educational, demonstration, and project-development purposes.

---

<div align="center">

### 💊 PharmaVoice

**AI-assisted Customer Complaint Management for Pharmaceutical Quality Systems**

Built with React • FastAPI • LangGraph • Groq • SQLAlchemy • Render

</div>
