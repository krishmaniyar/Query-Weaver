# Text-to-SQL Assistant

An intelligent natural language interface for database querying that converts plain English questions into executable SQL queries using Large Language Models (LLMs) and vector-based schema retrieval.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture Overview](#architecture-overview)
- [System Design Diagrams](#system-design-diagrams)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Performance Measurement & Execution Timing](#performance-measurement--execution-timing)
- [Project Structure](#project-structure)
- [Configuration & Hyperparameters](#configuration--hyperparameters)
- [Metrics & Evaluation](#metrics--evaluation)
- [Dependencies](#dependencies)
- [Contributing Guidelines](#contributing-guidelines)
- [License](#license)

---

## Project Overview

### Description

The **Text-to-SQL Assistant** is a full-stack application that enables users to interact with relational databases using natural language. Users can ask questions like "Show me the top 5 customers by revenue" or "What were the total sales last quarter?" and receive accurate SQL queries along with visualized results.

### Objectives

- **Democratize Database Access**: Enable non-technical stakeholders to query databases without SQL knowledge
- **Enhance Developer Productivity**: Provide developers with a rapid prototyping tool for database exploration
- **Ensure Query Safety**: Implement security measures to prevent destructive operations without user confirmation
- **Maintain Context**: Leverage conversational history for multi-turn query refinement

### Key Features

| Feature | Description |
|---------|-------------|
| **Natural Language to SQL** | Converts English questions into MySQL-compatible SQL queries |
| **Schema-Aware Retrieval** | Uses vector embeddings (ChromaDB) to intelligently retrieve relevant table schemas |
| **Conversational Memory** | Stores and retrieves chat history for contextual follow-up questions |
| **Data Visualization** | Renders query results as interactive tables and charts |
| **Schema Explorer** | Interactive sidebar for browsing database tables and columns |
| **Safety Controls** | Requires confirmation for data-modifying operations (INSERT, UPDATE, DELETE, DDL) |
| **Multi-Strategy Schema Selection** | Supports Auto (AI-selected), All Tables, or Specific Table selection |
| **Real-time Logging** | Comprehensive request/response logging with execution timing |

---

## Architecture Overview

### High-Level System Design

The system follows a **three-tier architecture** with clear separation of concerns:

1. **Presentation Layer**: React-based SPA with Tailwind CSS for responsive UI
2. **Application Layer**: FastAPI backend handling HTTP requests, LLM orchestration, and database operations
3. **Data Layer**: MySQL database for application data, ChromaDB for vector storage of schemas and chat history

### Package Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          Frontend (React)                            │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │   │
│  │  │  ChatPage   │ │SchemaExplorer│ │ DataChart   │ │ ResultTable │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP / REST / SSE
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            APPLICATION LAYER                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Backend (FastAPI)                          │   │
│  │                                                                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │ query_routes │  │ schema_routes│  │   Middleware   │            │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │   │
│  │                                                                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │ LLM Service  │  │ SQL Executor │  │ Schema Loader│            │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │   │
│  │                                                                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │ Vector Store │  │   Logger     │  │ SSE Broadcaster           │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ SQLAlchemy / Vector Operations
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               DATA LAYER                                     │
│  ┌─────────────────────┐    ┌─────────────────────┐                       │
│  │      MySQL DB       │    │     ChromaDB          │                       │
│  │  (Application Data) │    │ (Vector Embeddings)   │                       │
│  └─────────────────────┘    └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ API Calls
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐                       │
│  │   Groq LLM API      │    │  Sentence-Transformers │                     │
│  │  (llama-3.3-70b)    │    │   (all-MiniLM-L6-v2)  │                     │
│  └─────────────────────┘    └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Package Explanations:**

| Package | Responsibility |
|---------|---------------|
| `Frontend` | React SPA components for chat interface, schema browsing, and data visualization |
| `Routes` | FastAPI route handlers for HTTP endpoints and request validation |
| `LLM Service` | Orchestrates communication with Groq API for SQL generation |
| `SQL Executor` | Safely executes SQL queries with result sanitization and multi-statement support |
| `Schema Loader` | Introspects database schema and loads table metadata |
| `Vector Store` | Manages ChromaDB collections for semantic schema and history search |
| `SSE Broadcaster` | Server-Sent Events for real-time schema change notifications |
| `Logger` | Structured logging with execution timing and request tracing |

---

## System Design Diagrams

### Activity Diagram: Query Processing Flow

```mermaid
flowchart TD
    A[User Submits Question] --> B{Schema Selection Mode?}
    B -->|Auto| C[Vector Search Top-3 Tables]
    B -->|All Tables| D[Load Full Schema]
    B -->|Specific| E[Load Selected Tables]
    C --> F[Retrieve Chat History]
    D --> F
    E --> F
    F --> G[Inject Sample Data]
    G --> H[Construct LLM Prompt]
    H --> I[Generate SQL via Groq]
    I --> J{Is Modifying Query?}
    J -->|Yes| K[Request User Confirmation]
    K --> L{User Confirms?}
    L -->|No| M[Abort & Return SQL]
    L -->|Yes| N[Execute SQL]
    J -->|No| N
    N --> O{DDL Executed?}
    O -->|Yes| P[Sync Schema to ChromaDB]
    O -->|No| Q[Skip Sync]
    P --> R[Store Chat Message]
    Q --> R
    R --> S[Return Results to User]
```

**Explanation**: This diagram illustrates the complete query lifecycle from user input to result display. The system dynamically selects schema retrieval strategy, incorporates conversational history, generates SQL via LLM, and handles safety confirmations for data-modifying operations.

### Use Case Diagram

```mermaid
flowchart LR
    subgraph UserActions[" " ]
        U((User))
    end
    
    subgraph TextToSQLSystem["Text-to-SQL System"]
        UC1[Ask Natural Language Question]
        UC2[Browse Database Schema]
        UC3[Select Tables for Query Context]
        UC4[View Generated SQL]
        UC5[Execute Query with Confirmation]
        UC6[Visualize Results]
        UC7[View Query History]
        UC8[Confirm Destructive Operations]
    end
    
    subgraph SystemActions["System Actions"]
        UC9[Auto-Retrieve Relevant Tables]
        UC10[Generate SQL via LLM]
        UC11[Execute SQL Safely]
        UC12[Sync Schema Changes]
    end
    
    U --> UC1
    U --> UC2
    U --> UC3
    U --> UC4
    U --> UC5
    U --> UC6
    U --> UC7
    U --> UC8
    
    UC1 -.-> UC9
    UC1 -.-> UC10
    UC5 -.-> UC11
    UC5 -.-> UC12
```

**Explanation**: The use case diagram shows interactions between the user and the system. The system automatically handles SQL generation and schema synchronization while requiring user confirmation for safety-critical operations.

### Sequence Diagram: Query Execution Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as FastAPI
    participant VS as VectorStore
    participant LLM as LLM Service
    participant DB as MySQL
    participant CH as ChromaDB

    U->>F: Enter natural language query
    F->>API: POST /query {question, selected_tables}
    
    alt Auto Mode
        API->>VS: search_schema(question, k=3)
        VS->>CH: Semantic similarity search
        CH-->>VS: Relevant table schemas
    else Specific Tables
        API->>VS: load_database_schema(filtered)
    else All Tables
        API->>VS: load_database_schema()
    end
    
    VS-->>API: Schema context
    API->>CH: retrieve_relevant_history(question)
    CH-->>API: Historical Q&A pairs
    
    API->>DB: get_table_data(limit=5)
    DB-->>API: Sample rows
    
    API->>LLM: generate_sql(question, schema, history)
    LLM->>API: Constructed prompt with MySQL rules
    LLM->>External: Groq API (llama-3.3-70b)
    External-->>LLM: Generated SQL
    LLM-->>API: SQL query string
    
    alt Modifying Query
        API-->>F: Return {sql, requires_confirmation: true}
        F->>U: Display SQL for review
        U->>F: Confirm execution
        F->>API: POST /execute {sql}
    end
    
    API->>DB: execute_sql(query)
    DB-->>API: Query results
    
    alt DDL Executed
        API->>VS: sync_tables_to_schema()
        VS->>CH: Upsert new schema embeddings
    end
    
    API->>CH: store_chat_message(question, sql)
    API-->>F: Return {sql, results}
    F->>U: Display SQL, table, and chart
```

**Explanation**: This sequence diagram details the end-to-end flow including schema retrieval strategies, LLM prompt construction with MySQL-specific rules, safety confirmation for modifying queries, and bidirectional synchronization between the relational database and vector store.

### Class Diagram

```mermaid
classDiagram
    class FastAPIApp {
        +app: FastAPI
        +setup_middleware()
        +setup_exception_handlers()
        +lifespan()
    }
    
    class QueryRoutes {
        +router: APIRouter
        +process_query(request: QueryRequest): QueryResponse
        +execute_confirmed_query(request: ExecuteRequest): QueryResponse
    }
    
    class LLMService {
        -client: Groq
        -model_name: str
        -db_type: str
        +generate_sql(question, schema, history): str
        -construct_prompt(): str
    }
    
    class SQLExecutor {
        +execute_sql(query): Dict
        +is_modifying_query(query): bool
        -detect_query_type(query): str
        -sanitize_value(value)
        -split_statements(query): List
    }
    
    class VectorStore {
        -client: ChromaDB
        -schema_collection: Collection
        -chat_collection: Collection
        +store_schema_embeddings(metadata)
        +search_schema(query, k): List
        +store_chat_message(question, sql)
        +retrieve_relevant_history(query, k): List
        +sync_tables_to_schema(tables): int
    }
    
    class SchemaLoader {
        +load_database_schema(): List
        +get_table_data(table, limit): List
    }
    
    class ChatPage {
        -messages: State
        -isLoading: State
        +handleSendMessage(text, tables)
        +handleConfirmQuery(index, question, sql)
        +scrollToBottom()
    }
    
    class ChatInput {
        -input: State
        -selectedTables: State
        +handleSubmit()
    }
    
    class DataChart {
        +data: Array
        +renderChart()
    }
    
    class RequestModels {
        +QueryRequest
        +QueryResponse
        +ExecuteRequest
    }
    
    FastAPIApp --> QueryRoutes
    QueryRoutes --> LLMService
    QueryRoutes --> SQLExecutor
    QueryRoutes --> VectorStore
    QueryRoutes --> SchemaLoader
    LLMService ..> "Uses" GroqAPI : External
    SQLExecutor ..> "Uses" MySQL : External
    VectorStore ..> "Uses" ChromaDB : External
    SchemaLoader ..> "Uses" SQLAlchemy : External
    ChatPage --> ChatInput
    ChatPage --> DataChart
    ChatPage ..> "Uses" APIClient : HTTP
```

**Explanation**: The class diagram shows the main components and their relationships. The backend follows a service-oriented design with clear interfaces between routing, LLM orchestration, SQL execution, and vector storage layers. The frontend uses React functional components with state management for the chat interface.

---

## Installation & Setup

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.9+ | Backend runtime |
| Node.js | 18+ | Frontend build tools |
| MySQL | 8.0+ | Primary database |
| Conda | Latest | Environment management |

### Step-by-Step Installation

#### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd "NLP Project"
```

#### 2. Set Up Conda Environment

```bash
# Create environment (recommended: computer_vision)
conda create -n text2sql python=3.11
conda activate text2sql

# Or use existing computer_vision environment
conda activate computer_vision
```

#### 3. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL: MySQL connection string
# - GROQ_API_KEY: Your Groq API key
# - DB_TYPE: mysql (default)

# Initialize database schema sync
python sync_chroma.py
```

#### 4. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Build for production (optional)
npm run build
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/text2sql
DB_TYPE=mysql

# LLM API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Server Configuration
PORT=8000
```

---

## Usage

### Running the Project

#### Start the Backend Server

```bash
conda activate computer_vision  # or your preferred environment
cd backend
python -m app.main
```

The backend will start on `http://localhost:8000` with:
- API documentation at `http://localhost:8000/docs`
- Health check at `http://localhost:8000/health`

#### Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

#### Production Deployment

```bash
cd frontend
npm run build
# Serve dist/ folder via static file server or CDN
```

### Example Workflows

#### Basic Query Flow

1. **Navigate to the application** (`http://localhost:5173`)
2. **Ask a question**: "Show me all employees in the engineering department"
3. **Select schema mode**: Choose "Auto" for AI-selected tables or pick specific tables
4. **Review results**: View generated SQL, result table, and data visualization

#### Schema Exploration Workflow

1. **Open Schema Explorer**: Click the menu button to view all database tables
2. **Browse table structure**: Expand tables to see column names and types
3. **Select context tables**: Choose specific tables to constrain the LLM context
4. **Ask targeted questions**: Queries will only use selected table schemas

#### Data Modification Workflow

1. **Submit modifying query**: "Add a new employee John Doe to the HR department"
2. **Review confirmation prompt**: System detects INSERT/UPDATE/DELETE/DDL
3. **Verify generated SQL**: Review the SQL before execution
4. **Confirm or cancel**: Click "Run Query" to execute or dismiss to abort
5. **Automatic schema sync**: New tables/columns are automatically indexed

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |
| `/query` | POST | Submit natural language query |
| `/execute` | POST | Execute confirmed modifying query |
| `/schema` | GET | Retrieve database schema |
| `/schema/events` | GET | SSE stream for schema changes |

**Example API Request:**

```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the top 5 products by sales?",
    "selected_tables": ["Auto"]
  }'
```

---

## Performance Measurement & Execution Timing

The system includes comprehensive timing instrumentation at multiple stages of query processing.

### Extracting Execution Time from Logs

Execution times are automatically logged to `backend/logs/app.log`:

```log
2024-01-15 10:30:45 - INFO - SQL execution time: 0.0234s | type: SELECT
2024-01-15 10:30:46 - INFO - Total processing time: 2.3456s
```

**Log File Location:**
- File: `backend/logs/app.log`
- Rotation: Automatic with size-based rotation
- Format: Timestamp, log level, message with timing

### Displaying Execution Time to Users

To add user-facing execution timing, modify the response models and UI:

#### Backend Modification

**File:** `backend/app/models/request_models.py`

```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryResponse(BaseModel):
    sql: str
    results: List[Dict[str, Any]]
    requires_confirmation: bool = False
    execution_time_ms: Optional[float] = None  # Add this field
    sql_generation_time_ms: Optional[float] = None  # Add this field
```

**File:** `backend/app/routes/query_routes.py`

```python
@router.post("/", response_model=QueryResponse)
def process_query(request: QueryRequest):
    import time
    total_start = time.time()
    
    # Schema retrieval timing
    schema_start = time.time()
    schema_context = search_schema(request.question, k=3)
    schema_time = (time.time() - schema_start) * 1000
    
    # LLM generation timing
    llm_start = time.time()
    generated_sql = llm_service.generate_sql(request.question, schema_context)
    llm_time = (time.time() - llm_start) * 1000
    
    # SQL execution timing
    sql_start = time.time()
    exec_result = execute_sql(generated_sql)
    sql_time = (time.time() - sql_start) * 1000
    
    total_time = (time.time() - total_start) * 1000
    
    return {
        "sql": generated_sql,
        "results": exec_result["rows"],
        "execution_time_ms": total_time,
        "sql_generation_time_ms": llm_time,
        "schema_retrieval_time_ms": schema_time,
        "sql_execution_time_ms": sql_time
    }
```

#### Frontend Modification

**File:** `frontend/src/components/QueryMetrics.jsx` (create new file)

```jsx
import React from 'react';
import { Clock, Database, Brain, Search } from 'lucide-react';

export default function QueryMetrics({ metrics }) {
  if (!metrics) return null;
  
  const formatTime = (ms) => ms ? `${ms.toFixed(1)}ms` : '-';
  
  return (
    <div className="flex gap-4 text-xs text-gray-400 mt-2">
      <div className="flex items-center gap-1">
        <Clock className="w-3 h-3" />
        <span>Total: {formatTime(metrics.execution_time_ms)}</span>
      </div>
      <div className="flex items-center gap-1">
        <Brain className="w-3 h-3" />
        <span>LLM: {formatTime(metrics.sql_generation_time_ms)}</span>
      </div>
      <div className="flex items-center gap-1">
        <Search className="w-3 h-3" />
        <span>Schema: {formatTime(metrics.schema_retrieval_time_ms)}</span>
      </div>
      <div className="flex items-center gap-1">
        <Database className="w-3 h-3" />
        <span>SQL: {formatTime(metrics.sql_execution_time_ms)}</span>
      </div>
    </div>
  );
}
```

**Integration in ChatPage.jsx:**

```jsx
import QueryMetrics from '../components/QueryMetrics';

// In the message rendering section:
{!msg.isPending && !msg.isError && !msg.needsConfirmation && (
  <>
    <ChatMessage message={{ role: 'assistant', content: 'Here is the SQL query and result:' }} />
    <div className="ml-12 max-w-full mt-4 flex flex-col gap-6">
      <SQLViewer sql={msg.sql} />
      <QueryMetrics metrics={msg.metrics} />
      <ResultTable result={msg.result} />
      <DataChart data={msg.result} />
    </div>
  </>
)}
```

### Performance Optimization Tips

1. **Vector Search Tuning**: Adjust `k` parameter in `search_schema()` for precision vs. recall trade-off
2. **LLM Caching**: Implement response caching for repeated similar queries
3. **Connection Pooling**: SQLAlchemy engine already uses connection pooling
4. **Schema Sync Strategy**: Run `sync_chroma.py` only after DDL operations, not on every request

---

## Actual Measured Execution Times

The following timing data was collected from actual query executions on the running system:

### Sample Query Execution Times (from logs)

| Query Type | SQL Execution Time | Total Processing Time | HTTP Response Time |
|------------|-------------------|----------------------|-------------------|
| SELECT * FROM student | 0.0032s | 0.3081s | 0.3091s |
| ALTER TABLE (DROP COLUMN) | 0.0176s | 0.7851s | 0.7894s |
| ALTER TABLE (ADD COLUMN) | 0.0182s | 1.3127s | 1.3144s |
| ALTER TABLE (MODIFY) | 0.0119s | 0.4701s | 0.4714s |
| DROP TABLE | 0.0270s | 0.6622s | 0.6664s |
| CREATE TABLE | 0.0198s | 1.3210s | 1.3225s |

### Timing Statistics Summary

| Metric | Min | Max | Average |
|--------|-----|-----|---------|
| SQL Execution Time | 0.0020s | 0.0270s | ~0.0127s |
| Total Processing Time | 0.3081s | 1.3210s | ~0.7013s |
| HTTP Response Time | 0.3091s | 1.3225s | ~0.7034s |

### Key Observations

- **Simple SELECT queries** execute in ~2-3ms at the database level
- **DDL operations** (ALTER, DROP, CREATE) take 12-27ms for SQL execution
- **Total end-to-end latency** ranges from 0.3s to 1.3s depending on:
  - LLM generation time (majority of the latency)
  - Schema retrieval from vector store
  - Database query complexity
- **Schema sync overhead** adds ~40-100ms when DDL operations are executed

### Log Entry Examples

```log
# SELECT Query Timing
2026-03-28 16:41:30,249 - SQL execution time: 0.0020s | type: SELECT
2026-03-28 16:41:30,274 - Total processing time: 0.5008s
2026-03-28 16:41:30,275 - SUCCESS (200) - Time: 0.5024s

# DDL Operation Timing
2026-03-28 16:41:55,486 - SQL execution time: 0.0198s | type: ALTER
2026-03-28 16:41:55,520 - Schema sync complete. 1 table(s) upserted
2026-03-28 16:41:55,546 - Total processing time: 1.3210s
2026-03-28 16:41:55,548 - SUCCESS (200) - Time: 1.3225s
```

---

## Full Pipeline Timing Breakdown

The following table shows the detailed timing breakdown for each component in the query processing pipeline, measured from actual query executions:

### Component Timing Analysis

| Pipeline Stage | Description | Typical Time | Percentage |
|----------------|-------------|--------------|------------|
| **Schema Retrieval** | Vector search for relevant tables | 0.0440s | ~3.9% |
| **Table Data Fetch** | Query sample data from tables | 0.0045s | ~0.4% |
| **History Retrieval** | Retrieve chat context from ChromaDB | 0.0020s | ~0.2% |
| **LLM Generation** | Groq API call (llama-3.3-70b) | 1.0183s | ~89.2% |
| **SQL Execution** | Execute generated SQL on MySQL | 0.0023s | ~0.2% |
| **Schema Sync** | Update vector store (if DDL) | 0.0000s | ~0% |
| **Chat Store** | Store Q&A in history | 0.0700s | ~6.1% |
| **Overhead** | Serialization, logging, etc. | ~0.001s | ~0.2% |
| **TOTAL** | End-to-end processing | **1.1411s** | **100%** |

### Key Observations

1. **LLM Generation Dominates**: The Groq API call accounts for ~89% of total processing time (~1.02s). This is expected for LLM-based systems.

2. **Vector Operations are Fast**: Schema retrieval (0.044s) and history retrieval (0.002s) using ChromaDB are very efficient.

3. **Database Operations are Minimal**: SQL execution on MySQL is extremely fast (~2-3ms) for typical queries.

4. **Chat Storage Overhead**: Storing conversation history takes ~70ms due to ChromaDB embeddings generation.

### LLM Generation Time Details

The LLM generation time varies based on:

| Factor | Impact on Time |
|--------|----------------|
| Query complexity | Complex queries with JOINs take longer |
| Schema size | More tables/columns = longer context |
| Network latency | Groq API response time varies |
| Temperature setting | Lower temp = faster deterministic responses |

**Typical LLM Generation Times Observed:**
- Simple SELECT: 0.8-1.2s
- Complex JOIN queries: 1.0-1.5s
- DDL statements: 0.9-1.3s

### Full Pipeline Log Example

```log
2026-04-06 12:18:18,114 - Strategy: Auto (Vector Search)
2026-04-06 12:18:18,158 - Schema retrieval time: 0.0440s
2026-04-06 12:18:18,162 - Table data fetch time: 0.0045s
2026-04-06 12:18:18,166 - History retrieval time: 0.0020s
2026-04-06 12:18:19,185 - *** LLM GENERATION TIME: 1.0183s ***
2026-04-06 12:18:19,260 - SQL execution time: 0.0023s
2026-04-06 12:18:19,260 - Chat message store time: 0.0700s
2026-04-06 12:18:19,260 - PIPELINE TIMING BREAKDOWN:
2026-04-06 12:18:19,260 -   Schema Retrieval:    0.0440s
2026-04-06 12:18:19,260 -   Table Data Fetch:    0.0045s
2026-04-06 12:18:19,260 -   History Retrieval:   0.0020s
2026-04-06 12:18:19,260 -   LLM Generation:      1.0183s
2026-04-06 12:18:19,262 -   SQL Execution:       0.0023s
2026-04-06 12:18:19,262 -   Schema Sync:         0.0000s
2026-04-06 12:18:19,262 -   Chat Store:          0.0700s
2026-04-06 12:18:19,262 - Total processing time: 1.1411s
```

### Optimization Recommendations

Based on the pipeline timing analysis:

1. **Enable LLM Response Caching**: Cache common queries to avoid repeated LLM calls (potential 89% time savings for cached queries)

2. **Optimize Schema Retrieval**: The current 44ms can be reduced by:
   - Pre-caching schema embeddings
   - Using smaller embedding models for schema search

3. **Async Chat Storage**: Store chat history asynchronously to avoid blocking the response

4. **Connection Pooling**: Already implemented - SQL execution time is minimal at ~2ms

---

## Project Structure

```
NLP Project/
├── README.md                          # This documentation file
├── backend/                           # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuration management
│   │   ├── logger.py                  # Structured logging setup
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── sse_broadcaster.py         # Server-Sent Events for schema changes
│   │   ├── db/                        # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py            # SQLAlchemy engine and session
│   │   │   └── schema_loader.py       # Schema introspection utilities
│   │   ├── models/                    # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   └── request_models.py      # QueryRequest, QueryResponse
│   │   ├── routes/                    # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── query_routes.py        # /query and /execute endpoints
│   │   │   └── schema_routes.py       # /schema endpoints and SSE
│   │   ├── services/                  # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py         # LLM orchestration (Groq)
│   │   │   └── sql_executor.py        # Safe SQL execution engine
│   │   └── vectorstore/               # Vector database integration
│   │       ├── __init__.py
│   │       └── vectordb.py            # ChromaDB schema and history management
│   ├── chroma_data/                   # Persistent ChromaDB storage
│   ├── logs/                          # Application logs
│   ├── .env                           # Environment variables (not in git)
│   ├── check_db.py                    # Database connectivity test
│   ├── clear_db.py                    # Database reset utility
│   ├── requirements.txt               # Python dependencies
│   ├── setup_dummy_db.py              # Sample data generator
│   └── sync_chroma.py                 # Schema synchronization script
├── frontend/                          # React SPA frontend
│   ├── src/
│   │   ├── App.jsx                    # Root component
│   │   ├── main.jsx                   # Entry point
│   │   ├── components/                # React components
│   │   │   ├── ChatInput.jsx          # User input with schema selector
│   │   │   ├── ChatMessage.jsx        # Message bubble component
│   │   │   ├── DataChart.jsx          # Recharts visualization wrapper
│   │   │   ├── Loader.jsx             # Loading indicator
│   │   │   ├── ResultTable.jsx        # Data table renderer
│   │   │   ├── SchemaExplorer.jsx     # Database schema sidebar
│   │   │   └── SQLViewer.jsx          # Syntax-highlighted SQL display
│   │   ├── pages/
│   │   │   └── ChatPage.jsx           # Main chat interface page
│   │   ├── services/
│   │   │   └── api.js                 # HTTP client for backend API
│   │   └── styles/
│   │       └── (Tailwind CSS classes)
│   ├── dist/                          # Production build output
│   ├── index.html                     # HTML template
│   ├── package.json                   # Node.js dependencies
│   ├── vite.config.js                 # Vite build configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   └── postcss.config.js              # PostCSS configuration
└── Backup/                            # Project backup files
```

### Key Files Reference

| File Path | Purpose |
|-----------|---------|
| `backend/app/main.py` | FastAPI application setup, middleware, logging |
| `backend/app/routes/query_routes.py` | Core query processing endpoint |
| `backend/app/services/llm_service.py` | LLM integration with Groq |
| `backend/app/vectorstore/vectordb.py` | ChromaDB vector operations |
| `frontend/src/pages/ChatPage.jsx` | Main UI component |
| `frontend/src/components/DataChart.jsx` | Data visualization |

---

## Configuration & Hyperparameters

### Backend Configuration (`backend/app/config.py`)

| Parameter | Description | Default Value | Type | Range/Options |
|-----------|-------------|---------------|------|---------------|
| `PROJECT_NAME` | API title for documentation | "Text-to-SQL API" | String | Any valid string |
| `PORT` | HTTP server port | 8000 | Integer | 1024-65535 |
| `DATABASE_URL` | SQLAlchemy connection string | `mysql+pymysql://root:password@localhost:3306/text2sql` | String | Valid SQLAlchemy URL |
| `DB_TYPE` | Database dialect for LLM prompts | "mysql" | String | "mysql", "postgresql", "sqlite" |
| `GROQ_API_KEY` | API key for LLM access | "" (from env) | String | Valid Groq API key |

### Vector Store Parameters (`backend/app/vectorstore/vectordb.py`)

| Parameter | Description | Default Value | Type | Range/Options |
|-----------|-------------|---------------|------|---------------|
| `CHROMA_DB_PATH` | Persistent storage directory | `"chroma_data"` | String | Valid filesystem path |
| `EMBEDDING_MODEL` | Sentence transformer model | `"all-MiniLM-L6-v2"` | String | Any HuggingFace sentence-transformer |
| `SCHEMA_SEARCH_K` | Number of tables to retrieve | 3 | Integer | 1-10 |
| `HISTORY_SEARCH_K` | Number of history items to retrieve | 3 | Integer | 1-10 |
| `TABLE_SAMPLE_LIMIT` | Rows to include in LLM context | 5 | Integer | 0-20 |

### LLM Parameters (`backend/app/services/llm_service.py`)

| Parameter | Description | Default Value | Type | Range/Options |
|-----------|-------------|---------------|------|---------------|
| `MODEL_NAME` | LLM model identifier | `"llama-3.3-70b-versatile"` | String | Available Groq models |
| `TEMPERATURE` | Sampling randomness | 0.2 | Float | 0.0-1.0 |
| `MAX_TOKENS` | Maximum response length | 4096 | Integer | 256-8192 |
| `DB_RULES` | Database-specific SQL constraints | MySQL rules | Dict | DB-specific prompts |

### Frontend Configuration (`frontend/vite.config.js`)

| Parameter | Description | Default Value | Type | Range/Options |
|-----------|-------------|---------------|------|---------------|
| `server.port` | Dev server port | 5173 | Integer | 1024-65535 |
| `server.proxy` | API proxy target | `http://localhost:8000` | String | Valid URL |
| `build.outDir` | Production output | "dist" | String | Valid path |

---

## Metrics & Evaluation

### Evaluation Metrics

| Metric | Description | Formula | Use Case |
|--------|-------------|---------|----------|
| **SQL Generation Accuracy** | Percentage of syntactically valid SQL queries | `valid_queries / total_queries × 100` | Model performance monitoring |
| **Schema Retrieval Precision** | Relevance of retrieved tables to query intent | `relevant_tables / retrieved_tables` | Vector search tuning |
| **Schema Retrieval Recall** | Coverage of necessary tables for query | `retrieved_necessary / total_necessary` | System completeness |
| **End-to-End Latency** | Total time from request to response | `T_response - T_request` | User experience optimization |
| **LLM Latency** | Time for LLM to generate SQL | `T_llm_response - T_llm_request` | API performance tracking |
| **SQL Execution Time** | Database query execution duration | `T_exec_complete - T_exec_start` | Database optimization |
| **User Confirmation Rate** | Frequency of safety prompts | `confirmations_required / total_modifying` | Safety system calibration |
| **Query Success Rate** | Successful query executions | `successful_executions / total_attempts` | System reliability |

### Performance Benchmarks

| Operation | Expected Latency | Acceptable Range |
|-----------|-----------------|------------------|
| Schema Vector Search | 50-150ms | < 500ms |
| LLM SQL Generation | 500-2000ms | < 5000ms |
| SQL Execution | 10-500ms | < 2000ms |
| Total End-to-End | 1000-3000ms | < 8000ms |

---

## Dependencies

### Backend Dependencies (`backend/requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | Latest | Web framework for API endpoints |
| `uvicorn` | Latest | ASGI server for FastAPI |
| `sqlalchemy` | Latest | ORM and database abstraction |
| `pymysql` | Latest | MySQL database driver |
| `chromadb` | Latest | Vector database for embeddings |
| `sentence-transformers` | Latest | Text embedding generation |
| `python-dotenv` | Latest | Environment variable management |
| `groq` | Latest | Groq LLM API client |
| `cryptography` | Latest | Secure credential handling |

### Frontend Dependencies (`frontend/package.json`)

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | ^18.2.0 | UI framework |
| `react-dom` | ^18.2.0 | React DOM renderer |
| `axios` | ^1.6.0 | HTTP client for API calls |
| `lucide-react` | ^0.300.0 | Icon library |
| `recharts` | ^3.8.0 | Data visualization charts |
| `vite` | ^5.0.0 | Build tool and dev server |
| `tailwindcss` | ^3.3.5 | Utility-first CSS framework |
| `@vitejs/plugin-react` | ^4.2.0 | Vite React plugin |

### External Services

| Service | Purpose | Required |
|---------|---------|----------|
| Groq API | LLM inference for SQL generation | Yes |
| MySQL | Primary relational database | Yes |
| ChromaDB | Vector storage (local or remote) | Yes (local included) |

---

## Contributing Guidelines

### Getting Started

1. **Fork the repository** and clone your fork
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Set up development environment** following Installation & Setup
4. **Make changes** with clear, focused commits
5. **Test thoroughly** before submitting

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript/React**: Use consistent formatting with ESLint/Prettier
- **Commits**: Use conventional commit format (`feat:`, `fix:`, `docs:`, `refactor:`)

### Submitting Changes

1. **Update documentation** for any API or configuration changes
2. **Add tests** for new functionality
3. **Ensure all tests pass** before submitting PR
4. **Fill out the PR template** with description and motivation
5. **Request review** from maintainers

### Areas for Contribution

| Area | Description | Skill Level |
|------|-------------|-------------|
| LLM Prompt Engineering | Improve SQL generation accuracy | Intermediate |
| Vector Search Optimization | Enhance schema retrieval | Advanced |
| UI/UX Improvements | Frontend feature additions | Beginner-Intermediate |
| Database Support | Add PostgreSQL/SQLite adapters | Intermediate |
| Testing | Unit and integration tests | Beginner-Intermediate |
| Documentation | README, code comments, guides | Beginner |

### Reporting Issues

When reporting bugs, include:
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, Node version)
- **Relevant logs** from `backend/logs/app.log`

---

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2026 KBM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

- **Groq** for providing fast LLM inference
- **ChromaDB** for open-source vector storage
- **Sentence-Transformers** for efficient text embeddings
- **FastAPI** for modern Python web framework
- **React & Tailwind CSS** for frontend tooling

---

*For questions or support, please open an issue in the project repository.*
