# 🚀 Interviora — AI-Powered Interview Platform

**Interviora** is a full-stack AI application that transforms a Job Description into a complete mock interview experience using voice interaction and structured AI feedback. It simulates real interviews by generating questions, capturing spoken answers, and evaluating performance using LLMs.

---

## 🎯 Features

- **Job Description Analyzer**: Extracts role, skills, and responsibilities automatically.
- **AI Interview Question Generator**: Generates role-specific interview questions.
- **Voice-Based Interview**: Answer questions using real-time speech recognition.
- **Auto Question Flow**: Seamless progression between questions.
- **AI Feedback System**: Provides a Score (0–100), Strengths, Areas for improvement, and a Final verdict.
- **Multi-Agent Workflow**: Powered by **LangGraph** for structured AI pipelines.
- **Full Stack Integration**: React frontend + FastAPI backend.

---

## 🏗️ Architecture Overview

The system follows a modern AI agent architecture:
1. **Frontend (React)**: Handles the UI and Web Speech API for voice input.
2. **Backend (FastAPI)**: Manages the API endpoints and session state.
3. **AI Orchestration (LangGraph)**: Directs the flow between different AI agents (Analyzer, Generator, Evaluator).
4. **LLM Layer (Groq/Llama)**: Powers the intelligence for generating and grading content.

---

## 🧠 Tech Stack

- **AI Layer**: LangChain, LangGraph, Groq (Llama models), Pydantic
- **Backend**: FastAPI, Python, Dotenv
- **Frontend**: React.js, Web Speech API

---

## 📂 Project Structure

```text
AI_CAREER_COACH/
│
├── ai_interview_backend/
│   ├── main.py
│   ├── interview_workflow.py
│
├── ai_interview_frontend/
│   ├── App.jsx
│   ├── JDInput.jsx
│   ├── Interview.jsx
│   ├── main.jsx
│   ├── App.css
│   ├── index.css
│
├── .env
└── testing1.py

## ⚙️ Setup Instructions

### 1. Clone Repository
```bash
git clone [https://github.com/your-username/interviora.git](https://github.com/your-username/interviora.git)
cd interviora
```

### 2. Backend Setup
```bash
cd ai_interview_backend
pip install -r requirements.txt
```
**Create a `.env` file:**
```env
GROQ_API_KEY=your_api_key
```
**Run server:**
```bash
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
cd ai_interview_frontend
npm install
npm run dev
```

---

## 🧪 API Endpoints

- `POST /start-interview`: Initializes the session and generates questions.
- `POST /submit-answer`: Processes the user's spoken answer.
- `POST /next-question`: Fetches the next question in the queue.
- `POST /generate-feedback`: Triggers the final evaluation agent.

---

## ⚠️ Challenges Faced

- Handling structured LLM outputs reliably with Pydantic.
- Managing state across multi-agent workflows in LangGraph.
- Debugging speech recognition timing and browser compatibility.
- Ensuring smooth real-time communication between React and FastAPI.

---

## 🚀 Future Improvements

- 📊 **Analytics Dashboard**: Visual performance tracking over time.
- 🗂️ **History**: Save and review past interview sessions.
- 🔐 **Auth**: User authentication and secure profiles.
- ☁️ **Deployment**: Hosting on Vercel and AWS/Render.

---

## 📜 License
This project is open-source and available under the **MIT License**.

## 💡 Author
**Raghav Devgan**  
*Building AI-powered systems* 🚀
```
