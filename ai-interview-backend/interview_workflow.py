from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Optional, Annotated
import operator

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# -------------------------------
# Pydantic Schemas (Structured Output)
# -------------------------------

class JDAnalysis(BaseModel):
    role: str = Field(description="Job role or title")
    experience_level: str = Field(description="Junior / Mid / Senior / Lead")
    required_skills: List[str] = Field(description="Core technical or professional skills")
    responsibilities: List[str] = Field(description="Main responsibilities of the role")


class InterviewQuestions(BaseModel):
    questions: List[str] = Field(description="A list of exactly 3 interview questions")





# -------------------------------
# LLM Setup
# -------------------------------

llm = ChatGroq(model="llama-3.3-70b-versatile")

jd_llm = llm.with_structured_output(JDAnalysis)
questions_llm = llm.with_structured_output(InterviewQuestions)


# -------------------------------
# LangGraph State
# -------------------------------

class JDState(TypedDict):
    job_description: str

    role: str
    experience_level: str
    required_skills: List[str]
    responsibilities: List[str]

    questions: List[str]

    user_answers: Annotated[List[str], operator.add]
    


# -------------------------------
# Nodes
# -------------------------------

def jd_analyzer_node(state: JDState) -> JDState:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert technical recruiter. Extract information EXACTLY "
         "according to the schema. Do not add extra fields."),
        ("human",
         "Analyze this job description:\n\n{job_description}")
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
        ("system",
         "You are a senior technical interviewer. Generate exactly 3 interview questions."),
        ("human",
         "Role: {role}\nExperience: {experience_level}\nSkills: {required_skills}")
    ])

    chain = prompt | questions_llm
    result = chain.invoke({
        "role": state["role"],
        "experience_level": state["experience_level"],
        "required_skills": state["required_skills"]
    })

    return {"questions": result.questions}





# -------------------------------
# Graph Definitions
# -------------------------------

graph = StateGraph(JDState)

graph.add_node("jd_analyzer_node", jd_analyzer_node)
graph.add_node("interview_question_node", interview_question_node)

graph.add_edge(START, "jd_analyzer_node")
graph.add_edge("jd_analyzer_node", "interview_question_node")
graph.add_edge("interview_question_node", END)

workflow = graph.compile()


# -------------------------------
# Compile Workflow
# -------------------------------

workflow = graph.compile()
