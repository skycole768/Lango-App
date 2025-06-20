# Lango
Hey! This is Lango, a language flashcard app I built to help me (and hopefully you too) learn new words across different languages. It’s got a React frontend and a Python backend running on AWS Lambda with DynamoDB as the database.

# What's in this Project?
  User signup/login with JWT
  
  Create, edit, delete languages, sets, and flashcards
  
  React frontend with a nice UI
  
  Python Lambdas handling backend logic
  
  DynamoDB for storing data
  
  Terraform scripts to set up AWS infra
  
  GitHub Actions running tests automatically

# How to get this running locally
  Backend
  Go to backend/ folder
  
  Make sure you have Python 3.12 installed
  
  Create and activate a virtual environment:
  
  bash
  Copy code
  
    python -m venv venv
    source venv/bin/activate   # on macOS/Linux  
    venv\Scripts\activate      # on Windows
    Install dependencies:
  
  bash
  Copy code
  
    pip install -r requirements.txt
    
  Run tests:
  
  bash
  Copy code
  
    pytest tests --maxfail=1 --disable-warnings -q
    Frontend
    Go to frontend/ folder
  
  Run:
  
  bash
  Copy code
  
    npm install
    npm run dev
  
  Open http://localhost:5173 in your browser

# Deployment
  AWS resources managed via Terraform in the terraform/ folder
  
  Backend Lambdas live in backend/lambdas/
  
  Frontend can be hosted anywhere you like (S3, Vercel, etc)
  
  Tests run on every push via GitHub Actions (see .github/workflows/python-tests.yml)
