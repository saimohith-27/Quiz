# 🤖 AI Quiz & Assessment Platform

A Flask-based **AI-powered Computer-Based Testing (CBT) platform** that dynamically generates structured quiz questions using **Google Gemini**, validates them with **Pydantic**, evaluates candidate responses, and presents detailed performance analytics.

> 🎓 Built as a full-stack academic project with a focus on AI integration, assessment automation, and a professional CBT experience.

## 🚀 Live Demo

🔗 **Live Demo:** [Add live deployment URL here]( )

---

## ✨ Overview

The AI Quiz & Assessment Platform provides an end-to-end examination workflow:

**Candidate Registration → Roll Number Validation → Exam Configuration → AI Question Generation → Timed Examination → Evaluation → Analytics → Answer Review**

The platform is designed to simulate a modern online examination system while demonstrating practical integration of **Flask, AI APIs, structured data validation, session management, and data visualization**.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application logic |
| **Flask** | Web framework & backend |
| **Google Gemini API** | AI-powered question generation |
| **Pydantic** | Question/schema validation |
| **HTML5 / CSS3** | Frontend |
| **JavaScript** | Interactive CBT functionality |
| **Chart.js** | Result visualization |
| **Gunicorn** | Production WSGI server |
| **Git & GitHub** | Version control & collaboration |

---

## 🎯 Key Features

### 🤖 AI-Powered Question Generation
- Generates quiz questions dynamically using Gemini.
- Supports structured question generation.
- Validates AI-generated responses using Pydantic schemas.
- Reduces dependence on manually created question banks.

### 🎓 Candidate Management
- Candidate name, roll number, and section collection.
- NBKRIST roll-number validation.
- Automatic decoding of:
  - Admission year
  - College
  - Entry type
  - Branch
  - Student identifier

### 📝 CBT Examination Interface
- Timed examination environment.
- Question navigation.
- Previous / Next controls.
- Clear response functionality.
- Question status tracking.
- Support for different question types.

### 🧮 Evaluation & Scoring
- Python-based answer evaluation.
- Supports:
  - Single-choice questions
  - Multiple-choice questions
  - True/False questions
- Partial scoring.
- Negative marking.
- Automatic score calculation.

### 📊 Result Analytics
- Overall score and performance summary.
- Correct, incorrect, partial, and unanswered analysis.
- Visual performance charts.
- Question-wise review.

### 🔍 Answer Review
Candidates can filter questions by:

- All
- Correct
- Incorrect
- Partially Correct
- Unanswered

---

## 🔄 Candidate Flow

```text
Home
  ↓
Candidate Details
  ↓
Roll Number Validation
  ↓
Decoded Candidate Details
  ↓
Exam Configuration
  ↓
AI Question Generation
  ↓
Timed Examination
  ↓
Submit Exam
  ↓
Result Dashboard
  ↓
Question-wise Review
```

---

## 🧠 AI Question Generation

The application uses Gemini to generate structured examination questions rather than directly accepting unrestricted AI output.

The generated questions are validated before being presented to the candidate, helping maintain a consistent question format and reducing malformed AI responses.

---

## 🏫 NBKRIST Roll Number Decoder

The platform includes a dedicated roll-number parsing service for NBKR Institute of Science & Technology.

It validates the roll number format and extracts meaningful information such as:

```text
Admission Year
College Code
Entry Type
Branch
Student Identifier
```

Example:

```text
25KB1A0592
```

can be decoded into the corresponding candidate information according to the application's roll-number rules.

---

## 📈 Result Dashboard

After submission, the candidate receives a detailed performance report containing:

- Total questions
- Attempted questions
- Correct answers
- Incorrect answers
- Partial answers
- Unanswered questions
- Marks obtained
- Performance visualization

The result page uses **Chart.js** to present the assessment data visually.

---

## 🔐 Current Architecture

The current version is intentionally lightweight and **does not use a database**.

Active examination state is maintained through Flask sessions and server-side application state.

Persistent examination history and user accounts are not currently part of this prototype.

### Current Architecture

```text
                    ┌─────────────────┐
                    │    Candidate    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Flask Backend  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Roll Decoder    Gemini API     Exam Engine
              │              │              │
              │              ▼              │
              │       Question Generator   │
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │  Result Engine  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Analytics / UI  │
                    └─────────────────┘
```

---

## 📂 Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/saimohith-27/Quiz
cd quiz_platform
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

#### Linux / macOS

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Add your Gemini API Key from [Google's AI Studio](https://aistudio.google.com) to `.env`.

### 6. Run the application

```bash
python run.py
```

The application will be available at:

```text
http://127.0.0.1:5000
```

---

## 🌐 Production Deployment

The application can be served using Gunicorn:

```bash
gunicorn run:app
```

For platforms such as Render or other cloud hosting providers, configure the appropriate start command and environment variables.

---

## 🔮 Future Improvements

The current prototype can be extended into a production-ready assessment platform.

### Planned Enhancements

- 🔐 User authentication and authorization
- 🗄️ PostgreSQL / Supabase database integration
- 👤 Persistent user profiles
- 📚 Exam history
- 📊 Historical performance tracking
- 🏆 Leaderboards
- 👨‍🏫 Admin dashboard
- 📝 Custom question banks
- 📈 Advanced analytics
- 📧 Result notifications
- 🔑 Role-based access control
- ☁️ Cloud-based persistent storage

### Database-based Architecture

```text
              Candidate
                  │
                  ▼
            Authentication
                  │
                  ▼
             Flask API
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   Gemini API           Database
        │                   │
        ▼                   ▼
 Question Engine      Users / Exams
        │              Results / History
        └─────────┬─────────┘
                  ▼
           Result Analytics
```

---

## 🎯 Project Goals

This project demonstrates practical implementation of:

- AI API integration
- Prompt-based structured generation
- Pydantic data validation
- Flask application architecture
- Session management
- Algorithmic evaluation
- Data visualization
- REST-style backend development
- Production deployment
- Git-based development workflow

---
## 👨‍💻 Built By

**[Sai Mohith](https://github.com/saimohith-27/) × [GitHub Copilot](https://github.com)**

B.Tech — Computer Science & Engineering

> Designed and developed by Sai Mohith with AI-assisted development using GitHub Copilot.

---

## 📄 License

This project is developed for educational and academic purposes.