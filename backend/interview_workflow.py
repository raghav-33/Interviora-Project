from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Optional, Annotated
import operator
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langgraph.checkpoint.memory import MemorySaver 

load_dotenv()

# -------------------------------
# 1. Pydantic Schemas (Strict Outputs)
# -------------------------------
class JDAnalysis(BaseModel):
    role: str = Field(description="Job role or title")
    experience_level: str = Field(description="Junior / Mid / Senior / Lead")
    required_skills: List[str] = Field(description="Core technical or professional skills")
    responsibilities: List[str] = Field(description="Main responsibilities of the role")

class InterviewQuestions(BaseModel):
    questions: List[str] = Field(description="A list of exactly 3 interview questions")

class InterviewFeedback(BaseModel):
    score: int = Field(description="Score from 0 to 100")
    strengths: List[str]
    improvements: List[str]
    verdict: str

# -------------------------------
# 2. LLM Setup
# -------------------------------
llm = ChatGroq(model="llama-3.3-70b-versatile")
llm1 = ChatGroq(model="llama-3.1-8b-instant")
jd_llm = llm.with_structured_output(JDAnalysis)
questions_llm = llm.with_structured_output(InterviewQuestions)
#feedback_llm = llm.with_structured_output(InterviewFeedback)
feedback_llm = llm1.with_structured_output(InterviewFeedback)


# -------------------------------
# 3. LangGraph State Memory
# -------------------------------
class JDState(TypedDict):
    job_description: str
    role: str
    experience_level: str
    required_skills: List[str]
    responsibilities: List[str]
    questions: List[str]
    user_answers: Annotated[List[str], operator.add] 
    feedback: Optional[dict] 

# -------------------------------
# 4. Nodes (Strict Bracket Notation Enabled)
# -------------------------------
def jd_analyzer_node(state: JDState) -> JDState:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert technical recruiter. Extract information EXACTLY according to the schema."),
        ("human", "Analyze this job description:\n\n{job_description}")
    ])
    chain = prompt | jd_llm
    
    result = chain.invoke({"job_description": state["job_description"]})
    
    return {
        "role": result.role,
        "experience_level": result.experience_level,
        "required_skills": result.required_skills,
        "responsibilities": result.responsibilities
    }

def interview_question_node(state: JDState) -> JDState:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a senior technical interviewer. Generate exactly 2 interview questions."),
        ("human", "Role: {role}\nExperience: {experience_level}\nSkills: {required_skills}")
    ])
    chain = prompt | questions_llm
    
    result = chain.invoke({
        "role": state["role"],
        "experience_level": state["experience_level"],
        "required_skills": state["required_skills"]
    })
    
    return {"questions": result.questions}
'''
def feedback_node(state: JDState) -> JDState:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Senior Hiring Manager. Evaluate the interview answers strictly and fairly."),
        ("human", "Role: {role}\nExperience: {experience_level}\nQuestions: {questions}\nAnswers: {user_answers}\nProvide feedback strictly in the defined schema.")
    ])
    chain = prompt | feedback_llm
    
    result = chain.invoke({
        "role": state["role"],
        "experience_level": state["experience_level"],
        "questions": state["questions"],
        "user_answers": state["user_answers"]
    })
    
    return {"feedback": result.model_dump()}'''
    
def feedback_node(state: JDState) -> JDState:
    # UPDATED PROMPT: Strict instructions to fix the 17% Accuracy issue
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert, highly critical Senior Technical Interviewer. 
Your job is to evaluate a candidate's interview answers based on their specific Role and Experience Level.

1. Verdict Rules: You must evaluate the candidate and choose EXACTLY ONE of these three exact phrases: "Pass", "Fail", or "Needs Improvement". Do not use any other words.
   - Give a "Pass" ONLY if the technical answers are perfectly accurate and match the experience level.
   - Give a "Needs Improvement" if the answers are okay but lack technical depth.
   - Give a "Fail" if the candidate is completely wrong, gives beginner answers for a senior role, or rambles off-topic.

2. Feedback Rules: Write a highly specific, actionable paragraph. 
   - DO NOT just say "Good job" or "Poor effort." 
   - You MUST point out exactly which technical concepts they got wrong or missed from the questions asked.
   - Tell them exactly what specific topics they need to study to improve."""),
        
        ("human", "Role: {role}\nExperience: {experience_level}\nQuestions: {questions}\nAnswers: {user_answers}\nProvide feedback strictly in the defined schema.")
    ])
    
    chain = prompt | feedback_llm
    
    result = chain.invoke({
        "role": state["role"],
        "experience_level": state["experience_level"],
        "questions": state["questions"],
        "user_answers": state["user_answers"]
    })
    
    return {"feedback": result.model_dump()}

# -------------------------------
# 5. Routing Logic
# -------------------------------
def route_start(state: JDState) -> str:
    """
    Looks at the current memory to decide what to do next.
    Note: We use .get() or 'in' checks here because these keys don't exist yet on step one.
    """
    # If no questions exist yet, we are starting fresh.
    if "questions" not in state or not state["questions"]:
        return "jd_analyzer_node"
    
    # If questions and user answers exist, the interview loop is complete.
    if state.get("questions") and state.get("user_answers"):
        return "feedback_node"
        
    return END

# -------------------------------
# 6. Graph Compilation
# -------------------------------
graph = StateGraph(JDState)

graph.add_node("jd_analyzer_node", jd_analyzer_node)
graph.add_node("interview_question_node", interview_question_node)
graph.add_node("feedback_node", feedback_node)

graph.add_conditional_edges(START, route_start)

graph.add_edge("jd_analyzer_node", "interview_question_node")
graph.add_edge("interview_question_node", END)

graph.add_edge("feedback_node", END)

memory = MemorySaver()
workflow = graph.compile(checkpointer=memory)