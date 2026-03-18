# 🧠 Text-to-SQL Assistant

A full-stack, AI-powered natural language to SQL application. Ask questions in plain English and the assistant generates, executes, and visualizes SQL queries against your database in real time.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite)
![Cerebras](https://img.shields.io/badge/LLM-Cerebras-orange)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Text-to-SQL Assistant** bridges the gap between natural language and databases. Users type questions like _"Show me the top 3 customers by total spending"_ and the system:

1. Retrieves the relevant database schema (via vector search or manual table selection).
2. Sends the schema + question to a large language model (Cerebras).
3. Executes the generated SQL against a live SQLite database.
4. Returns structured results and interactive visualizations.

---

## ✨ Features

### Core
- **Natural Language → SQL** — Converts plain English questions into valid SQLite queries using the Cerebras LLM (`gpt-oss-120b`).
- **Smart Schema Retrieval** — Automatically finds the most relevant tables using ChromaDB vector similarity search, or lets users manually select tables.
- **Live SQL Execution** — Runs generated queries against a real SQLite database and returns structured results.
- **Conversational Context** — Stores and retrieves past question/SQL pairs to improve accuracy over time.

### Frontend
- **Interactive Chat UI** — A modern, dark-themed chat interface built with React.
- **Schema Explorer Sidebar** — Browse all tables and columns in a collapsible sidebar with real-time updates via Server-Sent Events (SSE).
- **Table Selection Pills** — Choose which tables the AI should consider: _Auto_ (vector search), _All Tables_, or specific tables — reducing unnecessary tokens and improving accuracy.
- **Data Visualization** — Automatically renders bar, line, and pie charts using Recharts, with **selectable X and Y axes** so you can explore data from any angle.
- **SQL Viewer** — Syntax-highlighted display of the generated SQL query.
- **Results Table** — Clean, scrollable table view of query results.
- **Persistent Chat History** — Conversations are saved to `localStorage` and persist across browser sessions.

### Backend
- **Intelligent Prompt Engineering** — SQLite-specific rules are injected into the LLM prompt (no `INTERVAL`, use `INSERT OR IGNORE`, etc.) ensuring generated SQL is always compatible.
- **DDL Detection & Auto-Sync** — When `CREATE TABLE`, `ALTER TABLE`, or `DROP TABLE` is executed, the schema is automatically re-synced to ChromaDB and all connected clients are notified via SSE.
- **Detailed Request Logging** — Every request is logged step-by-step: schema retrieval → history lookup → LLM prompt → SQL execution → response time.
- **Server-Sent Events (SSE)** — Real-time push notifications from backend to frontend when the schema changes.
- **Token Optimization** — Only the top 5 rows per table are sent to the LLM for context, minimizing token usage.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)              │
│                                                             │
│  ChatInput ──► ChatPage ──► API Service ──► Backend         │
│  (table selection pills)     (sendQuery)                    │
│                                                             │
│  SchemaExplorer ◄── SSE ◄── Backend /schema/events          │
│  DataChart (selectable axes)                                │
│  ResultTable, SQLViewer, ChatMessage                        │
└─────────────────────────────────────────────────────────────┘
                            │  HTTP + SSE
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI + Uvicorn)                │
│                                                             │
│  /query/          →  Schema Retrieval (ChromaDB / SQLite)   │
│                   →  History Retrieval (ChromaDB)            │
│                   →  LLM SQL Generation (Cerebras)          │
│                   →  SQL Execution (SQLAlchemy + SQLite)     │
│                   →  DDL Sync + SSE Broadcast               │
│                                                             │
│  /schema/         →  Live table & column metadata           │
│  /schema/events   →  SSE stream for schema changes          │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         ┌────────┐   ┌──────────┐   ┌──────────┐
         │ SQLite │   │ ChromaDB │   │ Cerebras │
         │  (DB)  │   │ (Vector  │   │  (LLM)   │
         │        │   │  Store)  │   │          │
         └────────┘   └──────────┘   └──────────┘
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | High-performance async Python web framework |
| **Uvicorn** | ASGI server for running the FastAPI app |
| **SQLAlchemy** | ORM and database toolkit for SQLite |
| **SQLite** | Lightweight relational database |
| **ChromaDB** | Vector database for semantic schema search and chat history |
| **Sentence-Transformers** | Embedding model for vectorizing schema descriptions |
| **Cerebras Cloud SDK** | LLM API for SQL generation (`gpt-oss-120b` model) |
| **python-dotenv** | Environment variable management |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | Component-based UI library |
| **Vite 5** | Fast build tool and dev server |
| **TailwindCSS 3** | Utility-first CSS framework |
| **Recharts** | Composable chart library for data visualization |
| **Axios** | HTTP client for API communication |
| **Lucide React** | Modern icon library |

---

## 📁 Project Structure

```
NLP Project/
├── backend/
│   ├── .env                          # Environment variables (API keys, DB URL)
│   ├── requirements.txt              # Python dependencies
│   ├── setup_dummy_db.py             # Script to populate sample data
│   ├── clear_db.py                   # Script to clear all databases
│   ├── check_db.py                   # Script to inspect database contents
│   ├── sync_chroma.py                # Script to manually sync ChromaDB
│   ├── app.db                        # SQLite database file
│   ├── chroma_data/                  # ChromaDB persistent storage
│   ├── logs/                         # Application log files
│   │   └── app.log
│   └── app/
│       ├── main.py                   # FastAPI app, lifespan, middleware
│       ├── config.py                 # Configuration (env vars, constants)
│       ├── logger.py                 # Logging setup (file + console)
│       ├── sse_broadcaster.py        # SSE event management
│       ├── db/
│       │   ├── database.py           # SQLAlchemy engine setup
│       │   └── schema_loader.py      # Load schema metadata & table data
│       ├── models/
│       │   └── request_models.py     # Pydantic request/response models
│       ├── routes/
│       │   ├── query_routes.py       # POST /query/ — main NL-to-SQL pipeline
│       │   └── schema_routes.py      # GET /schema/, GET /schema/events (SSE)
│       ├── services/
│       │   ├── llm_service.py        # Cerebras LLM integration & prompt engineering
│       │   └── sql_executor.py       # Safe SQL execution with DDL detection
│       └── vectorstore/
│           └── vectordb.py           # ChromaDB operations (schema search, history)
│
└── frontend/
    ├── index.html                    # Entry HTML
    ├── package.json                  # Node.js dependencies
    ├── vite.config.js                # Vite configuration
    ├── tailwind.config.js            # TailwindCSS configuration
    ├── postcss.config.js             # PostCSS configuration
    └── src/
        ├── main.jsx                  # React entry point
        ├── App.jsx                   # Root component with routing
        ├── components/
        │   ├── ChatInput.jsx         # Message input + table selection pills
        │   ├── ChatMessage.jsx       # Individual chat message bubble
        │   ├── DataChart.jsx         # Interactive charts with axis selectors
        │   ├── Loader.jsx            # Loading spinner component
        │   ├── ResultTable.jsx       # Tabular results display
        │   ├── SchemaExplorer.jsx    # Sidebar with live schema + SSE
        │   └── SQLViewer.jsx         # SQL syntax display
        ├── pages/
        │   └── ChatPage.jsx          # Main chat page layout
        ├── services/
        │   └── api.js                # Axios API client
        └── styles/
            └── globals.css           # Global styles + Tailwind imports
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** with conda (recommended: Anaconda/Miniconda)
- **Node.js 18+** with npm
- A **Cerebras API key** ([get one here](https://cloud.cerebras.ai/))

### Backend Setup

1. **Create and activate a conda environment:**
   ```bash
   conda create -n text2sql python=3.10 -y
   conda activate text2sql
   ```

2. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   
   Create a `.env` file in the `backend/` directory:
   ```env
   PORT=8000
   DB_URL=sqlite:///./app.db
   CEREBRAS_API_KEY=your_cerebras_api_key_here
   ```

4. **(Optional) Populate sample data:**
   ```bash
   python setup_dummy_db.py
   ```

5. **Start the backend server:**
   ```bash
   conda run -n text2sql --no-capture-output uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   You should see:
   ```
   =======================================================
     🚀  Text-to-SQL backend starting up...
   =======================================================
     ⏳  Syncing ChromaDB schema from SQLite...
     ✅  Schema sync complete — 4 table(s) ready.
     🌐  API live at http://localhost:8000
     📖  Docs at    http://localhost:8000/docs
   =======================================================
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser** at `http://localhost:5173`

---

## ⚙️ Configuration

| Variable | Description | Default |
|---|---|---|
| `PORT` | Backend server port | `8000` |
| `DB_URL` | SQLAlchemy database connection string | `sqlite:///./app.db` |
| `CEREBRAS_API_KEY` | API key for Cerebras LLM | _(required)_ |

The frontend connects to the backend at `http://localhost:8000` by default. To change this, set the `VITE_API_URL` environment variable before starting the frontend.

---

## 📖 Usage

1. **Ask a question** in the chat input, e.g.:
   - _"Show all customers from Delhi"_
   - _"Create a table called products with id, name, and price"_
   - _"Insert sample data into customers"_

2. **Select table context** using the pills above the chat input:
   - **Auto** — Let the AI find the most relevant tables automatically (vector search).
   - **All Tables** — Include every table's schema in the prompt.
   - **Specific tables** — Click individual table names to include only those.

3. **View results** — The assistant shows the generated SQL, a data table, and an interactive chart.

4. **Customize the chart** — Use the X-Axis and Y-Axis dropdowns to change what's plotted. Switch between bar, line, and pie charts.

5. **Browse the schema** — Open the sidebar to explore all tables and columns. It updates in real time when you create or modify tables.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/query/` | Submit a natural language question. Returns generated SQL + results. |
| `GET` | `/schema/` | Retrieve live database schema (tables + columns). |
| `GET` | `/schema/events` | SSE stream — pushes `schema_changed` events to clients. |
| `GET` | `/docs` | Auto-generated Swagger/OpenAPI documentation. |

### Example Request

```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show all customers from Delhi",
    "selected_tables": ["customers"]
  }'
```

### Example Response

```json
{
  "sql": "SELECT * FROM customers WHERE city = 'Delhi';",
  "results": [
    { "customer_id": 1, "name": "Alice", "email": "alice@email.com", "city": "Delhi", "signup_date": "2023-01-10" },
    { "customer_id": 3, "name": "Charlie", "email": "charlie@email.com", "city": "Delhi", "signup_date": "2023-03-01" }
  ]
}
```

---

## 📝 Utility Scripts

| Script | Description |
|---|---|
| `setup_dummy_db.py` | Creates sample `customers` and `orders` tables with test data |
| `clear_db.py` | Drops all SQLite tables and clears ChromaDB collections |
| `check_db.py` | Prints current database tables and row counts |
| `sync_chroma.py` | Manually re-syncs SQLite schema into ChromaDB |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
