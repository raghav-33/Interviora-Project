# 1. Start with a lightweight version of Python
FROM python:3.10-slim

# 2. Create a standard user. 
# Hugging Face Spaces requires this for security (User ID 1000)
RUN useradd -m -u 1000 user
USER user

# 3. Set up the home folder path for our new user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# 4. Create a folder inside the container where our app will live
WORKDIR $HOME/app

# 5. Copy your requirements file first
# We do this first because Docker caches steps. If you change your code 
# but not your requirements, Docker won't have to reinstall everything.
COPY --chown=user:user requirements.txt ./

# 6. Install all the Python packages (FastAPI, LangGraph, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy your entire backend folder into the container
# This automatically includes your main.py, vector DB file, 
COPY --chown=user:user . .

# 8. Open port 7860. Hugging Face Spaces always looks for this exact port.
EXPOSE 7860

# 9. Start the FastAPI server
# This command tells Uvicorn to look inside the 'backend' folder, find 'main.py', 
# and run the 'app' variable.
CMD ["uvicorn", "ai-interview-backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
