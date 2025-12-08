PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;  -- Better concurrency
PRAGMA synchronous = NORMAL;


-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT,
    phone TEXT,
    skills TEXT,              -- user's skills for matching
    experience_years INTEGER,
    preferred_location TEXT,
    preferred_seniority TEXT,
    resume_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    summary TEXT,
    skills TEXT,          -- comma-separated or JSON string
    experience TEXT,      -- JSON string
    education TEXT,       -- JSON string
    raw_text TEXT,        -- original resume text
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    score REAL NOT NULL,
    explanation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- User swipe actions
CREATE TABLE IF NOT EXISTS user_swipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    action TEXT NOT NULL,  -- 'apply', 'skip', 'save'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE(user_id, job_id)
);

-- Chat messages between users and employers
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    sender_type TEXT NOT NULL,  -- 'user' or 'employer'
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Tracks how users interact with jobs (for ML training)
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    job_id       INTEGER NOT NULL,
    semantic_sim REAL,
    skill_overlap REAL,
    exp_gap      REAL,
    location_match REAL,
    label        INTEGER NOT NULL,  -- 1 = like/save/apply, 0 = skip
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Auto-cleanup Trigger: Remove duplicates if they sneak in
CREATE TRIGGER IF NOT EXISTS trg_cleanup_jobs
AFTER INSERT ON jobs
BEGIN
    DELETE FROM jobs 
    WHERE id NOT IN (
        SELECT MIN(id) 
        FROM jobs 
        GROUP BY title, company
    );
END;

