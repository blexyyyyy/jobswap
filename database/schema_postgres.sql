-- PostgreSQL Schema for JobSwipe
-- This is the production database schema for deployment on Render

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    skills TEXT,
    experience_years INTEGER,
    preferred_location VARCHAR(255),
    preferred_seniority VARCHAR(100),
    resume_text TEXT,
    resume_file_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    summary TEXT,
    skills TEXT,
    experience TEXT,
    education TEXT,
    raw_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    url VARCHAR(1000),
    skills TEXT,
    salary_range VARCHAR(255),
    job_type VARCHAR(100),
    seniority_level VARCHAR(100),
    posted_date DATE,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(title, company)
);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    score REAL NOT NULL,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- User swipe actions
CREATE TABLE IF NOT EXISTS user_swipes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE(user_id, job_id)
);

-- Chat messages
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Interactions for ML training
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    semantic_sim REAL,
    skill_overlap REAL,
    exp_gap REAL,
    location_match REAL,
    label INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_user_swipes_user_id ON user_swipes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_swipes_job_id ON user_swipes(job_id);
CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_job_id ON interactions(job_id);
