# 🚀 Interviora — AI-Powered Mock Interview Platform

> **Transform any Job Description into a personalized AI mock interview with voice interaction, structured feedback, and production-grade evaluation.**

Interviora is a full-stack AI interview platform that analyzes a job description, generates role-specific interview questions, conducts a voice-based mock interview, and provides structured interview feedback powered by Large Language Models (LLMs).

Unlike traditional interview preparation tools that only generate questions, Interviora simulates an interview workflow and evaluates candidate responses using a structured AI pipeline.

---

## 🔗 Live Demo

| Resource | Link |
|---|---|
| 🌐 Live App | [https://interviora-project-1.onrender.com](https://interviora-project-1.onrender.com) |
| 📦 Backend API Docs | [https://interviora-project.onrender.com](https://interviora-project.onrender.com) |
---


## ✨ Features

- 📄 Intelligent Job Description Analysis
- 🤖 AI-generated role-specific interview questions
- 🎙️ Voice-based interview experience
- 💬 Real-time speech transcription
- 🔄 Automatic interview flow
- 🧠 AI-generated structured interview feedback
- 📊 Numerical interview score
- ✅ Strengths & improvement suggestions
- 🎯 Final hiring verdict
- ⚡ Multi-agent workflow using LangGraph
- 📈 Production evaluation using LangSmith + LLM-as-a-Judge

---

##  Demo Workflow

```text
Paste Job Description
          │
          ▼
JD Analyzer Agent
          │
          ▼
Extract Role + Skills + Experience
          │
          ▼
Interview Question Generator
          │
          ▼
React Frontend
          │
          ▼
Voice-Based Interview
          │
          ▼
Candidate Answers
          │
          ▼
Feedback Generation Agent
          │
          ▼
Interview Score + Feedback + Verdict
```

---

## 🏗️ System Architecture

```text
                    React Frontend
                           │
                           ▼
                     FastAPI Backend
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
   LangGraph Workflow                 Session Manager
          │
          ▼
 ┌─────────────────────────────┐
 │ JD Analyzer Agent           │
 └─────────────────────────────┘
                 │
                 ▼
 ┌─────────────────────────────┐
 │ Interview Question Agent    │
 └─────────────────────────────┘
                 │
                 ▼
          Voice Interview
                 │
                 ▼
         Candidate Responses
                 │
                 ▼
 ┌─────────────────────────────┐
 │ Feedback Evaluation Agent   │
 └─────────────────────────────┘
                 │
                 ▼
 Structured Interview Feedback
```

---

## 🧠 AI Workflow

### 1. JD Analyzer Agent

The uploaded Job Description is analyzed using an LLM to extract:

- Job Role
- Experience Level
- Required Skills
- Responsibilities

Instead of parsing raw text manually, the output is generated as a validated Pydantic object.

### 2. Interview Question Generator

Using the extracted information, the AI generates interview questions tailored to:

- Role
- Skills
- Experience Level

This produces significantly more relevant questions than generic interview generators.

### 3. Voice Interview

The candidate answers questions using voice.

The frontend uses the browser's Web Speech API for speech recognition and sends the transcribed responses to the backend.

### 4. Feedback Generation

After the interview completes, another LLM evaluates all candidate answers and generates:

- Overall Interview Score
- Key Strengths
- Areas for Improvement
- Final Hiring Verdict

The frontend displays this as a structured feedback card.

---

## ⭐ Why Structured Outputs?

One of the key design decisions in Interviora is the use of **Pydantic Structured Outputs** instead of parsing free-form LLM responses.

**Traditional Approach**

```text
LLM → Random text → Regex → JSON parsing → Possible failures
```

**Interviora Approach**

```text
LLM → Pydantic Schema → Validated Objects → Reliable Backend Logic
```

Benefits:

- Reliable JSON generation
- Type-safe outputs
- Automatic validation
- Eliminates parsing errors
- Easier frontend integration
- Better production reliability

This approach is used for:

- JD Analysis
- Interview Question Generation
- Interview Feedback

---

## ⚙️ Tech Stack

**AI**
- LangChain
- LangGraph
- Groq API
- Llama 3.3 70B Versatile
- Llama 3.1 8B Instant (Evaluation Judge)
- Pydantic Structured Outputs

**Backend**
- Python
- FastAPI
- Uvicorn
- dotenv

**Frontend**
- React.js
- Web Speech API

**Evaluation**
- LangSmith
- LLM-as-a-Judge
- Custom Deterministic Evaluators

---

## 📊 AI Evaluation

A major focus of Interviora is evaluating the quality of AI-generated interview feedback. Instead of manually checking responses, the project includes a complete evaluation pipeline built using LangSmith.

**Evaluation Dataset**

A synthetic benchmark dataset was generated containing:

- Multiple technical roles
- Multiple candidate personas
- Interview questions
- Candidate answers
- Expected hiring verdicts
- Expected feedback

This provides consistent and repeatable evaluation.

**LLM-as-a-Judge**

A separate LLM evaluates the generated interview feedback against the expected ground truth. The judge considers:

- Candidate answers
- Expected verdict
- Expected feedback
- Actual AI-generated feedback

It then assigns a semantic quality score along with reasoning, allowing evaluation beyond simple string matching.

**Deterministic Evaluators**

In addition to the LLM Judge, Interviora includes rule-based evaluators for:

- **Professional Tone** — Ensures generated feedback remains professional and avoids inappropriate language.
- **Verdict Accuracy** — Checks whether the predicted hiring verdict matches the expected verdict.

---

## 📈 Evaluation Results

| Metric | Score |
|---|---:|
| AI Coach Quality Score | **0.96** |
| Professional Tone Score | **1.00** |
| Verdict Accuracy | **0.97** |

These results indicate that the generated interview feedback is highly relevant, professionally written, and consistent with expected hiring decisions.

---

## ⚡ Performance

The application was traced and benchmarked using LangSmith.

| Metric | Value |
|---|---:|
| P50 Latency | **3.23 seconds** |
| P99 Latency | **7.60 seconds** |

These latency measurements represent end-to-end AI workflow execution under evaluation.

---

## 📂 Project Structure

```
Interviora
│
├── ai_interview_backend
│   ├── main.py
│   ├── interview_workflow.py
│
├── ai_interview_frontend
│   ├── App.jsx
│   ├── JDInput.jsx
│   ├── Interview.jsx
│   ├── main.jsx
│
├── Evaluation
│   ├── create_dataset.py
│   ├── run_evaluations.py
│
├── .env
└── README.md
```

---

## 🚀 Running the Project

**Backend**

```bash
cd ai_interview_backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**

```bash
cd ai_interview_frontend
npm install
npm run dev
```

---

## 🚀 Future Improvements

- User authentication
- Interview history dashboard
- Resume-based personalized interviews
- Advanced analytics dashboard
- Interview recording and playback
- Multi-language interview support

---

## 👨‍💻 Author

**Raghav Devgan**

B.Tech Artificial Intelligence & Data Science

Passionate about building production-ready AI applications using LLMs, Agentic AI, LangGraph, and modern full-stack technologies.

---

⭐ If you found this project interesting, consider giving the repository a star!
