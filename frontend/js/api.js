/**
 * API Module - Handles all backend communication
 */

const API = {
    baseUrl: 'http://localhost:8000/api',

    /**
     * Get auth token from localStorage
     */
    getToken() {
        return localStorage.getItem('token');
    },

    /**
     * Get auth headers
     */
    getHeaders() {
        const token = this.getToken();
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Fetch job feed for the current user
     */
    async getJobFeed() {
        try {
            const response = await fetch(`${this.baseUrl}/jobs/feed`, {
                headers: this.getHeaders()
            });

            if (response.status === 401) {
                // Clear all data and force Login
                localStorage.clear();
                window.location.href = 'login.html';
                return { jobs: [] };
            }

            if (!response.ok) throw new Error('Failed to fetch jobs');
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            // Return mock data as fallback
            return this.getMockJobs();
        }
    },

    /**
     * Record a swipe action
     */
    async recordSwipe(jobId, action) {
        try {
            const response = await fetch(`${this.baseUrl}/swipe`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify({ job_id: jobId, action })
            });

            if (response.status === 401) {
                window.location.href = 'login.html';
                return false;
            }

            return response.ok;
        } catch (error) {
            console.error('API Error:', error);
            return true; // Fail silently in dev mode
        }
    },

    /**
     * Mock jobs data for development/demo
     */
    getMockJobs() {
        return {
            jobs: [
                {
                    id: 1,
                    title: "Senior Python Developer",
                    company: "Tech Solutions Inc.",
                    location: "Bangalore, India",
                    seniority: "Senior",
                    skills: ["Python", "Django", "REST APIs", "PostgreSQL", "Docker"],
                    description: "Join our dynamic team building scalable backend systems. You'll work on exciting projects involving AI/ML integration, microservices architecture, and cloud-native applications. Remote-friendly with competitive compensation.",
                    match_score: 92,
                    logo_emoji: "🚀"
                },
                {
                    id: 2,
                    title: "Full Stack Engineer",
                    company: "Innovation Labs",
                    location: "Mumbai, India",
                    seniority: "Mid-Senior",
                    skills: ["Python", "React", "Node.js", "AWS", "TypeScript"],
                    description: "Build next-generation fintech products used by millions. Work with cutting-edge technologies in a fast-paced startup environment. Equity options available.",
                    match_score: 87,
                    logo_emoji: "💡"
                },
                {
                    id: 3,
                    title: "Backend Engineer",
                    company: "DataFlow Systems",
                    location: "Hyderabad, India",
                    seniority: "Mid",
                    skills: ["Python", "FastAPI", "Kafka", "Kubernetes", "Redis"],
                    description: "Design and implement high-performance data pipelines processing millions of events per second. Great learning opportunity with mentorship from industry experts.",
                    match_score: 85,
                    logo_emoji: "📊"
                },
                {
                    id: 4,
                    title: "ML Engineer",
                    company: "AI Innovations",
                    location: "Pune, India",
                    seniority: "Senior",
                    skills: ["Python", "TensorFlow", "PyTorch", "NLP", "MLOps"],
                    description: "Lead machine learning initiatives for our product suite. Build and deploy production ML models that impact millions of users. Research opportunities available.",
                    match_score: 78,
                    logo_emoji: "🤖"
                },
                {
                    id: 5,
                    title: "DevOps Engineer",
                    company: "Cloud Solutions",
                    location: "Chennai, India",
                    seniority: "Mid",
                    skills: ["Python", "Terraform", "Docker", "AWS", "CI/CD"],
                    description: "Automate infrastructure and streamline deployments. Work with modern cloud architectures and help teams ship faster. Flexible work arrangements.",
                    match_score: 75,
                    logo_emoji: "☁️"
                },
                {
                    id: 6,
                    title: "Python Developer",
                    company: "StartUp Ventures",
                    location: "Delhi, India",
                    seniority: "Junior-Mid",
                    skills: ["Python", "Django", "JavaScript", "MySQL", "Git"],
                    description: "Perfect for developers looking to grow. Mentorship program, learning budget, and opportunity to work on diverse projects. Great company culture.",
                    match_score: 82,
                    logo_emoji: "🌱"
                },
                {
                    id: 7,
                    title: "Platform Engineer",
                    company: "Enterprise Tech",
                    location: "Bangalore, India",
                    seniority: "Senior",
                    skills: ["Python", "Go", "Kubernetes", "gRPC", "Prometheus"],
                    description: "Build the foundation that powers our entire engineering organization. Work on developer experience, CI/CD, and internal tooling. High impact role.",
                    match_score: 88,
                    logo_emoji: "🏗️"
                },
                {
                    id: 8,
                    title: "Software Engineer",
                    company: "Fintech Innovations",
                    location: "Mumbai, India",
                    seniority: "Mid",
                    skills: ["Python", "AsyncIO", "PostgreSQL", "Redis", "GraphQL"],
                    description: "Build secure, scalable financial systems. Work in a regulated environment with high standards. Competitive salary with excellent benefits.",
                    match_score: 80,
                    logo_emoji: "💰"
                }
            ]
        };
    }
};
