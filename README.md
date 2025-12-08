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
│   ├── main.py              # Application entry point
│   ├── api/                 # API Routes & Dependencies
│   │   ├── routes/
│   │   │   ├── auth.py      # Login, Register, Profile, Resume
│   │   │   ├── jobs.py      # Feed, Saved, Applied
│   │   │   ├── swipe.py     # Swipe actions
│   │   │   ├── chat.py      # Messaging
│   │   │   └── scrape.py    # Job Scraping
│   │   └── deps.py          # Dependencies (get_current_user)
│   ├── core/                # Core Configuration
│   │   ├── config.py        # Settings (DB Path, Secrets)
│   │   └── security.py      # Auth Logic (JWT, Hashing)
│   └── schemas/             # Pydantic Data Models
│       ├── user.py          # User schemas
│       ├── job.py           # Job schemas
│       └── chat.py          # Chat schemas
├── database/
│   ├── db_manager.py        # Low-level DB utilities
│   └── schema.sql           # Database schema definitions
├── frontend/                # Premium Web Interface
│   ├── css/
│   │   ├── variables.css    # Design tokens (colors, fonts)
│   │   ├── base.css         # Reset and global styles
│   │   ├── components.css   # Cards, Buttons, Inputs
│   │   ├── animations.css   # Keyframes for swipes/fades
│   │   ├── explanation.css  # AI Badge & Insight styles
│   │   └── dashboard.css    # Analytics dashboard styles
│   ├── js/
│   │   ├── app.js           # Main app controller
│   │   ├── api.js           # Backend communication & Auth handling
│   │   ├── auth.js          # Login/Register logic
│   │   ├── cards.js         # Dynamic card rendering
│   │   ├── swipe.js         # Touch/Mouse gesture handler
│   │   ├── profile.js       # Resume upload & profile handling
│   │   └── dashboard.js     # Stats & Visualization
│   ├── index.html           # Main Swipe Interface
│   ├── profile.html         # User Profile & Resume Upload
│   ├── dashboard.html       # Career Analytics
│   ├── login.html           # Authentication Page
│   └── applied.html         # Application History
├── matching/
│   ├── explanations.py      # Gemini Prompt Engineering for Insights
│   ├── scorer.py            # Heuristic match scoring
│   └── embeddings.py        # Vector embedding utilities
├── parsers/
│   └── resume_parser.py     # LLM-based Resume Extractor
├── scrapers/
│   └── timesjobs_scraper.py # Real-time job board scraper
├── utils/
│   └── file_handler.py      # PDF/DOCX Text Extraction
├── .env                     # Environment variables (API Keys)
├── requirements.txt         # Python dependencies
└── README.md                # Project Documentation
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
