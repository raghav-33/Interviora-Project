from fastapi import FastAPI, Form, Body, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uuid
from fastapi.responses import StreamingResponse
import json

from interview_workflow import workflow, feedback_node

# ---------------- APP SETUP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- REQUEST MODELS ----------------
class JDRequest(BaseModel):
    job_description: str

class NextQuestionRequest(BaseModel):
    session_id: str
    index: int

class FeedbackRequest(BaseModel):
    session_id: str
    
# ---------------- ROUTES ----------------
# Home Route
@app.get("/")
def home():
    return {"status": "Backend running."}

#**************************** Start Interview Route ****************************************************
@app.post("/start-interview")
def start_interview(data: JDRequest):
    print("\n STARTING NEW INTERVIEW...")
    thread_id = uuid.uuid4().hex
    config = {"configurable": {"thread_id": thread_id}}
    
    workflow.invoke({"job_description": data.job_description}, config=config)
    state = workflow.get_state(config).values

    print(f" Generated {len(state.get('questions', []))} questions for session: {thread_id}")
    return {
        "session_id": thread_id,
        "questions": state["questions"] 
    }

#***************************************** Next Question Route ********************************************
@app.post("/next-question")
def next_question(data: NextQuestionRequest):
    config = {"configurable": {"thread_id": data.session_id}}
    state = workflow.get_state(config).values
    
    # State is Empty : raise Exception
    if not state:
        raise HTTPException(status_code=404, detail="Invalid session")

    questions = state["questions"]
    
    # All Question Generated
    if data.index >= len(questions):
        return {"done": True}

    return {
        "question": questions[data.index],
        "index": data.index
    }


#************************************** Submit Answer Route ***********************************************
@app.post("/submit-answer")
async def submit_answer(
    session_id: str = Body(...),
    answer: str = Body(...)
):
    print(f"\n SAVING ANSWER FOR SESSION: {session_id}")
    config = {"configurable": {"thread_id": session_id}}
    state = workflow.get_state(config).values
    
    # Error Raise : if State Empty
    if not state:
        print("ERROR: Session not found in memory!")
        raise HTTPException(status_code=404, detail="Invalid session")

    workflow.update_state(config, {"user_answers": [answer.strip()]})
    updated_state = workflow.get_state(config).values

    print(f"\n Answer saved! Total answers in memory: {len(updated_state.get('user_answers', []))}")
    return {
        "message": "Answer saved to graph state",
        "answer_count": len(updated_state["user_answers"])
    }

#************************************ Generate Feedback Route ************************************************
#************************************ Generate Feedback Route ************************************************
@app.post("/generate-feedback")
async def generate_feedback(data: FeedbackRequest):
    print(f"\n WAKING UP FEEDBACK NODE FOR SESSION: {data.session_id}")
    config = {"configurable": {"thread_id": data.session_id}}
    state = workflow.get_state(config).values

    if not state:
        print(" ERROR: State is empty. The server likely restarted and wiped the RAM.")
        raise HTTPException(status_code=404, detail="Invalid session")

    answers = state.get("user_answers", [])
    print(f" Found {len(answers)} user answers in memory.")

    if not answers:
        print(" ERROR: No answers found in state.")
        raise HTTPException(status_code=400, detail="No answers found in state")

    print(" AI is generating feedback... (This takes a few seconds)")
    
    try:
        # Run the feedback node directly
        new_state_data = feedback_node(state)
        print(" Feedback generated successfully!")
    except Exception as e:
        print(f" SEVERE ERROR inside feedback_node: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    # Fallback safety check to ensure feedback is structured dictionary
    feedback_content = new_state_data.get("feedback")
    if isinstance(feedback_content, str):
        try:
            feedback_content = json.loads(feedback_content)
        except:
            pass

    workflow.update_state(config, {"feedback": feedback_content})
    print("Feedback securely saved to LangGraph memory.")
    
    return {
        "feedback": feedback_content
    }
