-----

# 📈 DHANDHO - AI-Powered Financial Analysis Platform

Welcome to **DHANDHO**, your personal stock market intelligence platform. This application leverages a sophisticated agent-based system to fetch, parse, and analyze corporate financial results, providing you with AI-powered insights and a conversational chat interface to ask questions about company performance.

This project is a full-stack application featuring a **React.js** frontend and a **Python (FastAPI)** backend.

## ✨ Features

  * **📊 Results Calendar**: View a list of companies with upcoming quarterly result announcements.
  * **🤖 One-Click AI Analysis**: Select any company from the calendar to trigger a full analysis pipeline. The system downloads the latest results, extracts key financial metrics, and generates an AI-powered summary.
  * **📈 Latest Analysis Dashboard**: See a clean, card-based view of the most recently analyzed companies, complete with key metrics, highlights, and potential red flags.
  * **💬 Conversational AI Chat**: Ask questions about company performance in plain English. The chatbot maintains conversation history and uses its knowledge base to provide accurate, context-aware answers.
  * **🧠 Agentic Workflow**: The backend is built on a powerful multi-agent architecture where each agent has a specific responsibility (Scraping, Fetching, Parsing, Analyzing).
  * **🛡️ Demo Data Fallback**: For robustness (and hackathon-readiness\!), the system gracefully falls back to realistic demo data if live data cannot be fetched, ensuring the application is always functional.

## 🛠️ Tech Stack

  * **Frontend**: React.js, Tailwind CSS
  * **Backend**: Python, FastAPI
  * **AI/LLM**: Groq API with LLaMA 3
  * **Core Python Libraries**: `uvicorn`, `pydantic`, `python-dotenv`, `beautifulsoup4`

## 🚀 Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

  * Node.js and npm (for the frontend)
  * Python 3.8+ and pip (for the backend)
  * A Groq API Key (for the AI analysis features)

### 1\. Setup the Backend

First, navigate to the `backend` directory and set up the Python environment.

```bash
# 1. Go into the backend folder
cd backend

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# 3. Install the required Python packages
pip install -r requirements.txt 
# Or if you use uv/rye: pip install -r pyproject.toml

# 4. Create the environment file
# Create a file named .env in the backend folder and add your Groq API key
touch .env
```

Your **`.env`** file should look like this:

```
GROQ_API_KEY="your_groq_api_key_here"
```

### 2\. Setup the Frontend

Now, open a **new terminal** and navigate to the **root directory** of the project to set up the React application.

```bash
# 1. Go to the project's root folder (where package.json is)
# (If you are in the backend folder, you can use `cd ..`)

# 2. Install the required npm packages
npm install
```

### 3\. Run the Application

You need to have both the backend server and the frontend development server running simultaneously.

  * **In your backend terminal:**

    ```bash
    # Make sure you are in the /backend directory
    uvicorn main:app --reload
    ```

    The backend server will start, usually on `http://127.0.0.1:8000`.

  * **In your frontend (root) terminal:**

    ```bash
    # Make sure you are in the project's root directory
    npm start
    ```

    The React application will open in your browser, usually at `http://localhost:3000`.

You can now use the application\!

## 🤖 How the Agentic Workflow Works

The core of DHANDHO is its backend architecture, which uses a team of specialized AI agents that work together in a pipeline.

1.  **`ScraperAgent`**: This agent is responsible for fetching the list of companies with upcoming financial results. It attempts to get live data and falls back to a pre-defined list for reliability.
2.  **`PDFFetcherAgent`**: When a user requests an analysis, this agent's job is to find and download the official quarterly results PDF from the internet for that company. If it fails, it signals the next agent to use demo data.
3.  **`ParserAgent`**: This agent takes the downloaded PDF (or the demo signal) and extracts the key financial metrics, such as Revenue, Profit After Tax, EPS, etc., into a structured format.
4.  **`AnalyzerAgent`**: The final agent in the pipeline. It takes the structured financial data and uses a powerful LLM (via Groq) to generate qualitative insights, highlights, and potential red flags in a human-readable, "street-smart" tone.

This entire process is managed by the **`AgentOrchestrator`**, which ensures each agent performs its task in the correct order.

## 📁 Project Structure

```
/
├── backend/
│   ├── agents/             # Contains all the specialized AI agents
│   ├── data/               # Stores cached data, generated analyses, and PDFs
│   ├── main.py             # The main FastAPI application file
│   └── ...
├── src/
│   ├── components/         # React components (Dashboard, LandingPage)
│   ├── services/           # API service for frontend-backend communication
│   ├── App.js              # Main React app component
│   └── ...
├── public/                 # Static assets for the React app
└── package.json            # Frontend dependencies and scripts
```
