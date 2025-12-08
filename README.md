# 💼 JobSwipe - AI-Powered Career Matcher

**JobSwipe** is a premium, AI-driven career platform that modernizes the job search experience. Built with a "Tinder-like" swipe interface, it uses advanced Machine Learning and the Gemini LLM to provide hyper-personalized job matches, real-time explanation insights, and automated resume parsing.

---

## 🚀 Key Features

### 🧠 AI & Logic
*   **Gemini AI Explanations**: Every job card answers "Why this matches you" with a personalized analysis of your skills vs. the job description.
    *   🔥 **Excellent Match**: Highlights strong skill overlaps.
    *   ⚠️ **Challenging Match**: Identifies missing critical skills.
    *   💡 **Potential Match**: Suggests transferable skills.
*   **Smart Resume Parsing**: Upload a PDF or DOCX resume, and our LLM-powered parser automatically extracts technical skills, experience, and contact info to build your profile instantly.
*   **Vector Matching (Ready)**: Architecture designed for semantic similarity matching (ChromaDB integrated core).

### 🎨 Premium Frontend
*   **Swipe Interface**: Fluid, gesture-based card stack (Left=Skip, Right=Apply, Up=Save).
*   **Glassmorphism UI**: High-end dark mode aesthetics with blurred backdrops, glowing borders, and smooth 60fps animations.
*   **Interactive Dashboard**: Visual analytics of your application history, profile usage, and skill gap analysis.
*   **Real-time Explanations**: Dynamic UI that changes color and content based on AI match verdict.

### ⚙️ Robust Backend
*   **FastAPI**: High-performance async API handling job feeds, swipes, and auth.
*   **JWT Authentication**: Secure, stateful session management with strict loop-prevention logic.
*   **SQLite Database**: Lightweight, relational storage for users, jobs, swipes, and chat history.

---

## 🛠️ Tech Stack

*   **Backend**: Python 3.10+, FastAPI, SQLite, Pydantic, SQLAlchemy/Raw SQL
*   **Frontend**: Vanilla JS (ES6+), CSS3 (Variables, Flexbox/Grid), HTML5
*   **AI/ML**: Google Gemini (Pro), ChromaDB (Vector Store), PyPDF/Docx2txt
*   **DevOps**: Uvicorn, Dotenv

---

## 📂 Project Structure

```text
jobswipe/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API Routes & Dependencies
│   │   ├── routes/
│   │   │   ├── auth.py      # Login, Register, Profile, Resume
│   │   │   ├── jobs.py      # Feed, Saved, Applied
│   │   │   ├── swipe.py     # Swipe actions
│   │   │   ├── chat.py      # Messaging
│   │   │   ├── scrape.py    # Job Scraping trigger
│   │   │   └── apply.py     # Auto-Apply queue
│   │   └── deps.py          # Dependencies (get_current_user)
│   ├── core/                # Core Configuration
│   │   ├── config.py        # Settings (DB Path, Secrets, SMTP)
│   │   └── security.py      # Auth Logic (JWT, Hashing)
│   ├── services/            # Business Logic Layer
│   │   ├── auth_service.py  # User authentication
│   │   ├── job_service.py   # Job feed & scraping
│   │   ├── swipe_service.py # Swipe handling
│   │   ├── user_service.py  # Profile & resume processing
│   │   └── apply_service.py # Auto-apply email service
│   └── schemas/             # Pydantic Data Models
│       ├── user.py, job.py, chat.py, apply.py
├── database/
│   ├── connection.py        # Unified DB connection manager
│   ├── db_manager.py        # Low-level DB utilities
│   └── schema.sql           # Database schema definitions
├── frontend/                # Vite-Powered Web Interface
│   ├── vite.config.js       # Vite configuration with API proxy
│   ├── package.json         # Node dependencies
│   ├── src/
│   │   ├── css/             # Modular stylesheets
│   │   │   ├── variables.css, base.css, components.css
│   │   │   ├── animations.css, explanation.css, dashboard.css
│   │   └── js/              # ES Modules
│   │       ├── app.js, api.js, auth.js, cards.js
│   │       ├── swipe.js, profile.js, dashboard.js
│   │       ├── particles.js, applied.js
│   ├── index.html, login.html, profile.html
│   ├── applied.html, dashboard.html, chat.html
├── matching/
│   ├── explanations.py      # Gemini Prompt Engineering for Insights
│   ├── scorer.py            # Heuristic match scoring
│   └── embeddings.py        # Vector embedding utilities
├── parsers/
│   └── resume_parser.py     # LLM-based Resume Extractor
├── scrapers/
│   └── unified_scraper.py   # Multi-source job aggregator
│   │   └── Sources: Remotive, RemoteOK, Arbeitnow, WeWorkRemotely, Jobicy
├── ingestion/               # Data Pipeline
│   ├── cleaners/            # Job normalization
│   └── pipeline/            # Ingestion workflows
├── tests/                   # Verification Scripts
│   ├── verify_scraping.py, verify_auto_apply.py, check_db.py
├── utils/
│   ├── file_handler.py      # PDF/DOCX Text Extraction
│   └── email_client.py      # SMTP Email Sender
├── scripts/                 # Database migration scripts
├── core/
│   └── llm_client.py        # Gemini API wrapper
├── requirements.txt         # Python dependencies
└── README.md                # Project Documentation

# Not tracked (local only):
# .env                       # API keys & secrets
# .venv/                     # Python virtual environment
# *.db                       # SQLite databases
# node_modules/              # Node dependencies
# chroma_db/                 # Vector store data
```

---

## ⚡ Setup & Installation

1.  **Clone the repository**
2.  **Create virtual environment**:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up Environment**:
    Create a `.env` file in the root:
    ```env
    GEMINI_API_KEY=your_api_key_here
    JWT_SECRET=your_secret_key
    ```
5.  **Run the Server**:
    ```bash
    python -m uvicorn app.main:app --reload
    ```
6.  **Access the App**:
    Open `http://localhost:8000/frontend/login.html` (or serve frontend via a web server).

---

## 🧪 Usage Guide

1.  **Sign Up**: Create an account on the glossy login page.
2.  **Build Profile**: Go to the **Profile** tab. Drag & drop your PDF resume. Watch the AI auto-fill your skills and experience.
3.  **Swipe**: Go to the **Job Feed**.
    *   Read the **"✨ Gemini AI Analysis"** card to see why a job fits.
    *   **Right** = Apply (Confetti!)
    *   **Left** = Skip
    *   **Up** = Save
4.  **Analyze**: Check the **Dashboard** to see your application stats and profile strength.

---

## 🤝 Contribution
This project showcases the integration of Generative AI into practical workflows. Feel free to extend the `scrapers/` or improve `matching/explanations.py` prompt logic.
