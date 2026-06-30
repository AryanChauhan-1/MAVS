# HireLens
# See Beyond the Resume

### Powered by MAVS (Multi-Agent Validation Suite)

HireLens is an AI-powered hiring intelligence platform that validates technical claims made in resumes instead of relying solely on keyword matching. Built on the MAVS (Multi-Agent Validation System) engine, the system analyzes resumes, understands job descriptions, and generates targeted technical interview questions to help recruiters make evidence-based hiring decisions.

---

## 🚀 Problem Statement

Traditional Applicant Tracking Systems (ATS) primarily perform keyword matching between resumes and job descriptions. This approach often results in:

- Resume keyword stuffing
- AI-generated resume inflation
- False positive candidate selection
- Inefficient technical interviews
- Increased recruiter workload

HireLens addresses these challenges by validating **what candidates claim they have built**, rather than simply checking whether keywords exist.

---

## 💡 Solution

HireLens uses the MAVS engine to perform intelligent resume validation through a structured AI workflow.

```
Resume PDF
      │
      ▼
PDF Text Extraction
      │
      ▼
Resume Analysis
      │
      ▼
Job Description Analysis
      │
      ▼
Technical Validation
      │
      ▼
Match Score
Risk Assessment
Interview Questions
Recruiter Recommendation
```

---

# 🧠 MAVS Architecture

MAVS (Multi-Agent Validation System) follows a three-agent architecture.

### Agent 1 — Resume Intelligence Agent

- Extracts candidate information
- Identifies technical skills
- Understands project experience
- Detects engineering claims

### Agent 2 — Job Description Intelligence Agent

- Extracts role requirements
- Identifies required technologies
- Understands hiring expectations

### Agent 3 — Validation Agent

- Compares resume with JD
- Calculates candidate match score
- Estimates hiring risk
- Generates project-specific technical interview questions
- Produces recruiter recommendations

---

# ✨ Features

- AI-powered Resume Analysis
- Job Description Understanding
- Technical Claim Validation
- Match Score Generation
- Risk Assessment
- Recruiter Recommendation
- AI-generated Technical Interview Questions
- PDF Resume Upload
- Interactive Dashboard

---

# 🛠 Tech Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Gemini 2.5 Flash API
- PyPDF

## Frontend

- Streamlit
- HTML
- CSS

## AI

- Google Gemini 2.5 Flash

## Version Control

- Git
- GitHub

---

# 📁 Project Structure

```
HireLens
│
├── Backend
│   ├── app
│   │   ├── api
│   │   ├── services
│   │   └── core
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── requirements.txt
│
├── Frontend
│   ├── app.py
│   └── requirements.txt
│
├── screenshots
├── README.md
└── .gitignore
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/<AryanChauhan-1>/HireLens.git
```

---

## Backend

```bash
cd Backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

---

## Frontend

Open a second terminal.

```bash
cd Frontend

streamlit run app.py
```

---

# 🔐 Environment Variables

Create a `.env` file inside the Backend directory.

```
GEMINI_API_KEY=YOUR_API_KEY
PORT=8000
```

---

# 📊 Workflow

1. Upload Resume (PDF)
2. Extract Resume Text
3. Enter Job Description
4. AI analyzes Resume
5. AI analyzes Job Description
6. Technical claims are validated
7. Match Score is generated
8. Risk Assessment is calculated
9. Technical Interview Questions are generated
10. Recruiter receives structured validation report

---

# 📌 Future Roadmap

- CrewAI / LangGraph Agent Orchestration
- GitHub Project Verification
- Voice Interview Validation
- Coding Assessment Agent
- PostgreSQL Support
- Recruiter Analytics Dashboard
- Enterprise ATS Integration

---

# 👥 Team

**Aryan Chauhan**  
Project Lead • Backend Architecture • FastAPI • AI Integration

**Aadrika**  
Frontend UI/UX • Documentation

**Mitali Prajapati**  
Frontend Development • Dashboard • User Experience

**Yash Verma**  
Database Design • SQLAlchemy • Schema Management

**Ram**  
Backend Support • PDF Processing • Testing

---

# 📄 License

This project is developed for educational and research purposes.

---

## Built with ❤️ using FastAPI, Streamlit and Google's Gemini AI
