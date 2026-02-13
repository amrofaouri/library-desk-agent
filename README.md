# 📚 Library Desk Agent

AI-powered Library Desk Agent with chat interface using LangChain + Ollama.

## Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/download) installed
- Git

## Setup

1. Clone the repo
```
git clone https://github.com/amrofaouri/library-desk-agent.git
cd library-desk-agent
```

2. Create virtual environment
```
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Configure environment
```
copy .env.example .env
```

5. Pull the Ollama model
```
ollama pull llama3.1
```

6. Seed the database
```
python seed_db.py
```

7. Start Ollama (in a separate terminal)
```
ollama serve
```

8. Run the app
```
python -m server.main
```

9. Open **http://localhost:8000** in your browser

## Features
- 🔍 Find books by title or author
- 🛒 Create orders for customers
- 📦 Restock books
- 💰 Update book prices
- 📋 Check order status
- 📊 View inventory summary

## Tech Stack
- **Backend:** FastAPI, LangChain, LangGraph
- **LLM:** Ollama (llama3.1)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript