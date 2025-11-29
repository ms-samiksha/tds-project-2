# TDS Quiz Auto-Solver

This project is built for the Tools in Data Science (TDS) course.
It implements an **autonomous quiz-solving system** that receives quiz tasks via an API endpoint, loads quiz pages, extracts instructions, solves tasks, and submits answers — all automatically.

The system is built using:
- **FastAPI** → to receive requests
- **LangGraph + LangChain** → to build an LLM-driven agent
- **Google Gemini 2.5 Flash** → for reasoning and tool orchestration
- **Playwright** → for JavaScript-rendered web pages
- **Custom Tools** → scraping, downloading files, executing Python code, submitting answers

---

## 🚀 Overview

When the server receives a POST request for a quiz, it:

1. Validates the secret key
2. Starts the autonomous agent as a background task
3. The agent:
- Loads the quiz page
- Reads instructions
- Downloads/loads required data files
- Performs data processing or analysis
- Generates the answer
- Submits it to the submission endpoint
- Continues solving until no new quiz URL is provided

The entire system works within the 3-minute limit given by the evaluation server.

---

## 🧠 Architecture (Short & Simple)


### Components:
- **main.py** → FastAPI server
- **agent.py** → LangGraph state machine + LLM logic
- **tools/** → helper modules
- **.env** → secrets (not included in repo)

---

## 📁 Project Structure

project/
├── main.py
├── agent.py
├── tools/
│ ├── get_rendered_html.py
│ ├── download_file.py
│ ├── post_request.py
│ ├── add_dependencies.py
│ └── run_code.py
├── Dockerfile
├── pyproject.toml / requirements.txt
├── README.md
└── .gitignore


---

## ⚙️ Setup Instructions

### 1. Clone the repo
git clone git clone https://github.com/ms-samiksha/tds-quiz-generator.git
cd tds-quiz-generator

EMAIL=your-email
SECRET=your-secret
GOOGLE_API_KEY=your-gemini-api-key


### 2. Install dependencies


uv sync
uv run playwright install chromium


### 3. Run the server


uv run main.py


Server runs at:


http://0.0.0.0:7860


---

## 🧪 Testing the Endpoint

POST request:


http://localhost:7860/solve


⭐ Features

Autonomous multi-step quiz solving

JavaScript page rendering with Playwright

File downloading & processing

Dynamic Python code execution for data tasks

Automatic submission to given endpoints

Loops until no next quiz URL

Background execution to avoid timeouts