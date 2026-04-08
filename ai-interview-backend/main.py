from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import whisper

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List


from interview_workflow import workflow

# ---------------- APP SETUP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- WHISPER MODEL ----------------
whisper_model = whisper.load_model("base")

# ---------------- IN-MEMORY SESSION STORE ----------------
INTERVIEW_SESSIONS = {}

# ---------------- REQUEST MODELS ----------------
class JDRequest(BaseModel):
    job_description: str

class NextQuestionRequest(BaseModel):
    session_id: str
    index: int
class InterviewFeedback(BaseModel):
    score: int = Field(description="Score from 0 to 100")
    strengths: List[str]
    improvements: List[str]
    verdict: str

feedback_llm = ChatGroq(
    model="llama-3.3-70b-versatile"
).with_structured_output(InterviewFeedback)


# ---------------- ROUTES ----------------
@app.get("/")
def home():
    return {"status": "Backend running"}

# ---------- START INTERVIEW ----------
@app.post("/start-interview")
def start_interview(data: JDRequest):
    result = workflow.invoke({
        "job_description": data.job_description
    })

    session_id = str(len(INTERVIEW_SESSIONS) + 1)
    INTERVIEW_SESSIONS[session_id] = result

    return {
        "session_id": session_id,
        "questions": result["questions"]
    }

# ---------- NEXT QUESTION ----------
@app.post("/next-question")
def next_question(data: NextQuestionRequest):
    session = INTERVIEW_SESSIONS.get(data.session_id)

    if not session:
        return {"error": "Invalid session"}

    questions = session["questions"]

    if data.index >= len(questions):
        return {"done": True}

    return {
        "question": questions[data.index],
        "index": data.index
    }

# ---------- SUBMIT ANSWER (VOICE) ----------
"""@app.post("/submit-answer")
async def submit_answer(
    audio: UploadFile = File(...),
    session_id: str = Form(...)
):
    os.makedirs("answer_audio", exist_ok=True)

    audio_path = f"answer_audio/{audio.filename}"

    # Save audio file
    with open(audio_path, "wb") as f:
        f.write(await audio.read())

    # Transcribe using Whisper
    result = whisper_model.transcribe(audio_path)
    transcription = result["text"]

    return {
        "transcription": transcription
    }
"""
from fastapi import Body

@app.post("/submit-answer")
async def submit_answer(
    session_id: str = Body(...),
    answer: str = Body(...)
):
    session = INTERVIEW_SESSIONS.get(session_id)

    if not session:
        return {"error": "Invalid session"}

    session.setdefault("user_answers", [])
    session["user_answers"].append(answer.strip())

    return {
        "message": "Answer saved",
        "answer_count": len(session["user_answers"])
    }


    # 🔥 STORE ANSWER
    session.setdefault("user_answers", [])
    session["user_answers"].append(transcription)

    return {
        "transcription": transcription,
        "answer_count": len(session["user_answers"])
    }

@app.post("/generate-feedback")
def generate_feedback(session_id: str = Form(...)):
    session = INTERVIEW_SESSIONS.get(session_id)

    if not session:
        return {"error": "Invalid session"}

    answers = session.get("user_answers", [])
    if not answers:
        return {"error": "No answers found"}

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a Senior Hiring Manager. "
         "Evaluate the interview answers strictly and fairly."),
        ("human",
         """
         Role: {role}
         Experience Level: {experience_level}
         Questions: {questions}
         Answers: {answers}

         Provide feedback strictly in the defined schema.
         """
        )
    ])

    chain = prompt | feedback_llm

    result = chain.invoke({
        "role": session["role"],
        "experience_level": session["experience_level"],
        "questions": session["questions"],
        "answers": answers
    })

    session["feedback"] = result.model_dump()

    return {
        "feedback": session["feedback"]
    }



