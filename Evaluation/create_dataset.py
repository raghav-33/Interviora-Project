import os
from dotenv import load_dotenv
from langsmith import Client
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()
client = Client()

# 1.Dataset Schema
class MockInterview(BaseModel):
    role: str = Field(description="The job title, e.g., Data Scientist or AI Engineer.")
    experience_level: str = Field(description="Intern, Junior, Mid-Level, or Senior.")
    questions: list[str] = Field(description="Exactly 7 technical interview questions.")
    user_answers: list[str] = Field(description="Exactly 7 candidate answers matching the questions.")
    expected_verdict: str = Field(description="Pass, Needs Improvement, or Fail.")
    expected_feedback: str = Field(description="A brief summary of why the candidate deserves this verdict.")

# LLM for Synthetic Data Generation
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7)

generator_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert HR data generator. Create realistic technical interview transcripts for an AI evaluation dataset."),
    ("user", """
    Generate a mock interview for the role of: {role}. 
    The candidate's behavior persona is: {persona}. 
    
    You MUST output the specific role and a logical experience level (e.g., Intern or Senior).
    You MUST generate exactly 7 technical questions appropriate for the role.
    You MUST generate exactly 7 answers exactly matching the candidate's persona.
    """)
])

generator_chain = generator_prompt | llm.with_structured_output(MockInterview)

roles = [
    "Data Scientist (Machine Learning, Big Data)",
    "AI Engineer (LangChain, LLMs)",
    "Fullstack Developer (React, FastAPI)",
    "Software Engineer (Python Backend)",
    "Data Analyst (SQL, Visualization)"
]

personas = [
    "The Expert: Answers perfectly with deep technical knowledge.",
    "The Beginner: Gives very short, basic textbook definitions.",
    "The Rambler: Talks a lot, goes off-topic.",
    "The Recoverer: Fails the first 3 questions, perfectly answers the last 4.",
    "The Overconfident: Confidently gives completely wrong answers.",
    "The Average: Gets half right, struggles with advanced concepts."
]

# Dataset Geneartion and Upload Functin
def generate_and_upload():
    dataset_name = "Interviora V2 Fixed Schema"
    
    print(f" ******************   Creating LangSmith dataset: {dataset_name}")
    dataset = client.create_dataset(
        dataset_name=dataset_name, 
        description="30 Auto-generated multi-turn interviews with role and experience_level."
    )

    examples_to_upload = []
    count = 1

    print(f"***************** Starting Synthetic Data Generation...\n")

    for role in roles:
        for persona in personas:
            print(f" Generating #{count}: Role [{role.split(' ')[0]}] | Persona [{persona.split(':')[0]}]")
            
            try:
                mock_data = generator_chain.invoke({"role": role, "persona": persona})
                
                langsmith_example = {
                    "inputs": {
                        "role": mock_data.role,
                        "experience_level": mock_data.experience_level,
                        "questions": mock_data.questions,
                        "user_answers": mock_data.user_answers
                    },
                    "outputs": {
                        "expected_verdict": mock_data.expected_verdict,
                        "expected_feedback": mock_data.expected_feedback
                    }
                }
                examples_to_upload.append(langsmith_example)
                count += 1
                
            except Exception as e:
                print(f"⚠️ Error generating data for #{count}: {e}")

    print("\n  Uploading all 30 examples to LangSmith...")
    client.create_examples(dataset_id=dataset.id, examples=examples_to_upload)
    print(" Successfully uploaded V2 dataset!")

if __name__ == "__main__":
    generate_and_upload()