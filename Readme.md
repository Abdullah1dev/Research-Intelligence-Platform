# Research Intelligence Platform — Backend

Backend for the **Research Intelligence Platform**, an AI-powered research application for managing research papers, processing academic PDFs, performing semantic search, and asking grounded questions using RAG and agentic workflows.

The backend is built with **FastAPI, PostgreSQL, pgvector, LangChain, LangGraph, and OpenRouter**.

---

## Features

* JWT-based authentication
* User registration and login
* Current-user authentication endpoint
* Role-based access
* Paper CRUD operations
* Paper ownership and authorization
* Paper search
* Category filtering
* Publication-year filtering
* Sorting
* Pagination and pagination metadata
* PDF upload and storage
* PDF text extraction
* Automatic document chunking
* 384-dimensional embeddings
* PostgreSQL + pgvector storage
* Semantic vector search
* Grounded RAG question answering
* Paper summarization
* Paper analysis
* Semantic Scholar paper recommendations
* Conversational research assistant
* LangGraph agent workflow
* Conversation persistence and checkpointing
* Context-window management
* Source-aware RAG responses
* Document replacement and deletion
* PDF download
* Database migrations with Alembic

---

# Architecture

The backend follows a layered, feature-based architecture.

```text
                         React Frontend
                               │
                               │ HTTP / JSON
                               ▼
                         ┌─────────────┐
                         │   FastAPI   │
                         └──────┬──────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                 Routers                 Auth
                    │                       │
                    ▼                       ▼
                Services                User/Auth
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
        RAG      Agents    Papers/Documents
          │         │
          ▼         ▼
    Vector Search  LangGraph
          │         │
          └────┬────┘
               ▼
        PostgreSQL + pgvector
               │
               ▼
        Research Documents
```

The backend separates HTTP handling from business logic and infrastructure services.

---

# Technology Stack

| Technology           | Purpose                              |
| -------------------- | ------------------------------------ |
| Python               | Backend programming language         |
| FastAPI              | REST API framework                   |
| SQLAlchemy           | ORM and database interaction         |
| PostgreSQL           | Primary relational database          |
| pgvector             | Vector storage and similarity search |
| Pydantic             | Request and response validation      |
| JWT                  | Authentication                       |
| LangChain            | LLM and RAG integrations             |
| LangGraph            | Agentic workflow orchestration       |
| OpenRouter           | LLM API access                       |
| Alembic              | Database migrations                  |
| Semantic Scholar API | Research paper recommendations       |

---

# Project Structure

The backend follows a feature-based and layered structure.

```text
app/
│
├── features/
│   ├── auth/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── ...
│   │
│   ├── papers/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── enums.py
│   │   └── ...
│   │
│   ├── conversations/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── models.py
│   │   └── ...
│   │
│   └── users/
│       └── models.py
│
├── infrastructure/
│   ├── database/
│   ├── storage/
│   ├── document_processing/
│   ├── embeddings/
│   ├── vector_search/
│   ├── rag/
│   ├── llm/
│   └── agent/
│
├── config/
├── shared/
│
└── main.py
```

### Feature Layer

The feature layer contains application functionality such as:

* Authentication
* Papers
* Conversations
* Users

### Infrastructure Layer

The infrastructure layer contains reusable technical components such as:

* Database configuration
* Local file storage
* PDF extraction
* Chunking
* Embeddings
* Vector search
* RAG
* LLM services
* LangGraph agents

---

# Authentication

The API uses JWT bearer authentication.

Authentication flow:

```text
Register
   ↓
User created
   ↓
Login
   ↓
JWT access token
   ↓
Authorization: Bearer <token>
   ↓
Authenticated API request
```

## Authentication endpoints

### Register

```http
POST /auth/register
```

Creates a new user.

Request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

---

### Login

```http
POST /auth/login
```

Authenticates the user and returns an access token.

Example response:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

---

### Current User

```http
GET /auth/me
```

Returns the authenticated user's information.

Example:

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "is_active": true,
  "role": "researcher",
  "created_at": "...",
  "updated_at": "..."
}
```

---

# Paper Management

The Papers module provides complete CRUD functionality.

```text
Create
Read
Update
Delete
Search
Filter
Sort
Paginate
```

All paper operations enforce ownership.

A user can only access and modify papers belonging to that user.

---

# Paper Search, Filtering and Pagination

The paper listing endpoint supports multiple query capabilities.

Example:

```http
GET /papers/?search=transformer
```

Category:

```http
GET /papers/?category=Artificial%20Intelligence
```

Publication year:

```http
GET /papers/?publication_year=2024
```

Sorting:

```http
GET /papers/?sort_by=publication_year&order=desc
```

Pagination:

```http
GET /papers/?page=1&limit=10
```

These capabilities can also be combined:

```http
GET /papers/?search=transformer&category=Artificial%20Intelligence&page=1&limit=10&sort_by=publication_year&order=desc
```

The query processing order is:

```text
Authentication
      ↓
Ownership restriction
      ↓
Search
      ↓
Filtering
      ↓
Sorting
      ↓
Pagination
      ↓
Response
```

Sorting is applied before pagination so that the requested page represents the correctly ordered dataset.

---

# PDF Document Management

Each paper can have an associated research PDF.

The backend supports:

* Upload
* Retrieve metadata
* Replace
* Delete
* Download

A paper has at most one associated `PaperDocument`.

---

## Upload PDF

```http
POST /papers/{paper_id}/document
```

The uploaded PDF is:

```text
Uploaded
   ↓
Stored
   ↓
PDF text extracted
   ↓
Text chunked
   ↓
Embeddings generated
   ↓
Chunks stored in PostgreSQL
```

---

## Retrieve Document Metadata

```http
GET /papers/{paper_id}/document
```

Returns document metadata such as:

```json
{
  "id": 1,
  "paper_id": 5,
  "file_name": "research-paper.pdf",
  "file_size": 245678,
  "mime_type": "application/pdf",
  "storage_key": "papers/5/....pdf",
  "processing_status": "completed"
}
```

---

## Replace PDF

```http
PUT /papers/{paper_id}/document
```

The replacement process creates a new document representation and regenerates:

* Extracted text
* Chunks
* Embeddings

Old chunks are removed before the new chunks are committed.

---

## Delete PDF

```http
DELETE /papers/{paper_id}/document
```

Deleting a document also removes its associated chunks.

---

## Download PDF

```http
GET /papers/{paper_id}/document/download
```

The endpoint returns the actual stored PDF file.

Authorization and paper ownership are checked before the file is returned.

---

# Document Processing Pipeline

The document-processing pipeline is:

```text
PDF
 │
 ▼
LocalStorage
 │
 ▼
PDFExtractor
 │
 ▼
Extracted Text
 │
 ▼
DocumentChunker
 │
 ▼
Text Chunks
 │
 ▼
EmbeddingService
 │
 ▼
384-dimensional Embeddings
 │
 ▼
DocumentChunk
 │
 ▼
PostgreSQL + pgvector
```

Each chunk stores:

```text
chunk_id
document_id
chunk_index
content
embedding
created_at
```

Embeddings currently use a 384-dimensional vector representation.

---

# Vector Search

The vector-search layer converts the user's question into an embedding and searches the paper's document chunks using pgvector similarity search.

The current RAG retrieval configuration uses:

```text
top_k = 4
similarity_threshold = 0.5
```

Conceptually:

```text
User Question
      ↓
Question Embedding
      ↓
pgvector Similarity Search
      ↓
Top Relevant Chunks
      ↓
Similarity Threshold
      ↓
Retrieved Sources
```

Only chunks that satisfy the retrieval requirements are passed into the RAG generation step.

---

# Retrieval Result

The RAG layer uses structured retrieval results.

```python
@dataclass
class RetrievalSource:
    chunk_id: int
    chunk_index: int
    content: str
    similarity_score: float
```

The complete retrieval result contains:

```python
@dataclass
class RetrievalResult:
    context: str
    sources: list[RetrievalSource]
```

This allows the API to return both:

* Generated answer
* Supporting document sources

---

# Grounded RAG

The platform provides document-grounded question answering.

Endpoint:

```http
POST /papers/{paper_id}/ask
```

The RAG pipeline is:

```text
User Question
      ↓
Vector Search
      ↓
Relevant Chunks
      ↓
Context Builder
      ↓
Grounded Prompt
      ↓
LLM
      ↓
Answer + Sources
```

The LLM is instructed to answer using only the retrieved document context.

It must not invent information or use outside knowledge to fill missing information.

If no relevant information is retrieved, the API returns:

```text
I could not find relevant information in this document.
```

with an empty source list.

Example:

```json
{
  "answer": "I could not find relevant information in this document.",
  "sources": []
}
```

This behavior prevents unrelated questions from being answered using unsupported information.

---

# RAG Service

The `RAGService` separates retrieval from generation.

```text
RAGService
   │
   ├── retrieve()
   │     ├── Vector Search
   │     ├── Context Building
   │     └── Source Preparation
   │
   └── ask()
         ├── retrieve()
         ├── Grounded Prompt
         └── LLM Generation
```

The retrieval method always returns a `RetrievalResult`, including when no relevant chunks are found.

This keeps the retrieval contract consistent and prevents type-related failures during no-result retrieval.

---

# Paper Summarization

The backend provides paper summarization functionality.

The summary generation uses the paper/document information available through the backend's RAG and LLM infrastructure.

The goal is to produce a concise representation of the research paper while keeping the generated result grounded in the available paper content.

---

# Paper Analysis

The backend also provides research-paper analysis functionality.

Analysis can be used to extract structured insights from the available research content.

The analysis layer uses the same research-oriented backend architecture rather than creating a separate AI stack.

---

# Semantic Scholar Integration

The platform integrates with the Semantic Scholar API for research-paper recommendations.

Architecture:

```text
Paper Recommendation API
          ↓
Recommendation Service
          ↓
SemanticScholarService
          ↓
Semantic Scholar API
```

Endpoint:

```http
GET /papers/{paper_id}/recommendations
```

The system can resolve a paper through its title when a Semantic Scholar ID is not already available.

The integration also includes:

* Paper ID resolution
* Paper lookup
* Recommendation retrieval
* API rate limiting
* Retry handling
* `Retry-After` support for HTTP 429 responses

The integration is designed to avoid unnecessary requests while respecting the external API's rate limits.

---

# Agentic Research Assistant

The platform also contains a conversational research agent powered by LangGraph.

Endpoint:

```http
POST /conversations/{conversation_id}/messages
```

The agent can use research tools to retrieve information from the paper library.

Current research tools include:

```text
search_paper
search_papers
```

The architecture is:

```text
User Message
     ↓
Research Agent
     ↓
LLM
     ↓
Tool Decision
     ↓
Research Tool
     ↓
Paper / Vector Data
     ↓
Tool Result
     ↓
LLM
     ↓
Final Answer
```

---

# LangGraph Architecture

The research agent is implemented using LangGraph.

Simplified graph:

```text
                 START
                   │
                   ▼
          research_assistant
                   │
            ┌──────┴──────┐
            │             │
       No tool call    Tool call
            │             │
            ▼             ▼
        Final Answer     tools
                          │
                          ▼
                research_assistant
```

The agent uses a tool-enabled LLM and a `ToolNode` for executing research tools.

---

# Conversation State

The research agent maintains state containing:

```python
class ResearchAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    conversation_id: int
    user_id: int
    paper_id: int
```

This allows the agent to maintain the context necessary for a research conversation.

---

# Conversation Memory

LangGraph checkpointing is used to persist conversation state.

The application initializes the research agent during FastAPI startup.

```text
FastAPI Startup
      ↓
Create Checkpointer
      ↓
Build Research Agent
      ↓
Store Agent in app.state
      ↓
API Requests
```

This prevents the agent graph from being rebuilt for every request.

Conversation state can therefore persist across messages and sessions according to the configured checkpointing system.

---

# Context Window Management

The agent includes explicit context management to avoid sending unlimited conversation history to the LLM.

The current model context budget is approximately:

```text
MAX_CONTEXT_TOKENS = 4000
```

The context builder prioritizes recent conversation information while keeping the model input within the configured limit.

This allows longer research conversations without continuously increasing the model context.

---

# LLM

The current research agent uses an OpenRouter-hosted model:

```text
openai/gpt-oss-20b
```

Configuration:

```text
Provider: OpenRouter
Temperature: 0.2
```

The LLM is initialized through the backend infrastructure rather than directly inside individual API endpoints.

---

# Database

The backend uses PostgreSQL as its primary database.

Major entities include:

```text
Users
Papers
PaperDocuments
DocumentChunks
Conversations
```

Vector embeddings are stored using PostgreSQL's `pgvector` extension.

Simplified relationship:

```text
User
 │
 ├── Papers
 │      │
 │      └── PaperDocument
 │              │
 │              └── DocumentChunks
 │                      │
 │                      └── Embeddings
 │
 └── Conversations
```

---

# Database Migrations

Database schema changes are managed with Alembic.

Migrations keep the SQLAlchemy models and PostgreSQL database schema synchronized.

Run migrations with:

```bash
alembic upgrade head
```

---

# Environment Variables

Create a `.env` file in the backend project.

Typical configuration includes:

```env
APP_NAME=Research Intelligence Platform
APP_VERSION=1.0.0

DATABASE_URL=postgresql://username:password@localhost:5432/research_db

JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

OPENROUTER_API_KEY=your-openrouter-api-key

SEMANTIC_SCHOLAR_API_KEY=your-semantic-scholar-api-key
```

The Semantic Scholar API key is optional depending on the configured integration.

**Never commit `.env` files or API keys to GitHub.**

---

# Installation

## 1. Clone the repository

```bash
git clone <your-backend-repository-url>
cd <backend-repository>
```

## 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# Install Dependencies

Install the project's dependencies:

```bash
pip install -r requirements.txt
```

---

# Configure PostgreSQL

Create a PostgreSQL database for the application.

Example:

```text
research_db
```

Then configure the database connection in `.env`.

The backend uses SQLAlchemy for database access.

---

# Run Database Migrations

After configuring PostgreSQL:

```bash
alembic upgrade head
```

---

# Run the Backend

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

---

# API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Swagger can be used to test:

* Authentication
* Paper CRUD
* Search
* Filtering
* Pagination
* Document operations
* RAG
* Summarization
* Analysis
* Recommendations
* Conversations
* Research agent

---

# API Module Overview

| Module          | Main Responsibility                    |
| --------------- | -------------------------------------- |
| Auth            | Registration, login and authentication |
| Papers          | Paper CRUD and discovery               |
| Documents       | PDF management and processing          |
| RAG             | Document-grounded question answering   |
| Vector Search   | Semantic chunk retrieval               |
| Agent           | Conversational research workflow       |
| Conversations   | Persistent research conversations      |
| Recommendations | Semantic Scholar integration           |
| Users           | User data and relationships            |

---

# Error Handling

The backend handles common API errors including:

```text
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error
```

Examples include:

* Invalid authentication credentials
* Unauthorized paper access
* Paper not found
* Document not found
* Duplicate DOI
* Invalid request data
* Invalid query parameters
* Document-processing failures
* External API failures

---

# Security and Authorization

The backend applies authentication and ownership checks to protected resources.

For paper operations:

```text
Authenticated User
       ↓
Current User
       ↓
Paper owner_id == current_user.id
       ↓
Allow operation
```

This prevents users from accessing or modifying another user's research papers simply by knowing a paper ID.

Passwords are stored as password hashes rather than plaintext passwords.

JWT bearer tokens are used for authenticated API requests.

---

# Research Workflow

A typical research workflow looks like:

```text
User
 │
 ▼
Create Research Paper
 │
 ▼
Upload PDF
 │
 ▼
Extract Text
 │
 ▼
Chunk Document
 │
 ▼
Generate Embeddings
 │
 ▼
Store in PostgreSQL + pgvector
 │
 ▼
Ask Research Question
 │
 ▼
Semantic Vector Search
 │
 ▼
Retrieve Relevant Evidence
 │
 ▼
Grounded RAG Response
 │
 ▼
Sources
```

For conversational research:

```text
User
 │
 ▼
Conversation
 │
 ▼
LangGraph Research Agent
 │
 ▼
Tool Selection
 │
 ▼
Paper / Research Retrieval
 │
 ▼
LLM
 │
 ▼
Grounded Response
```

---

# Design Principles

## Separation of Concerns

The backend separates:

```text
Router
   ↓
Service
   ↓
Infrastructure
   ↓
Database / External APIs
```

Routers handle HTTP/API concerns while services contain business logic.

---

## Grounded AI

Research questions should be answered using available research evidence.

The RAG layer explicitly avoids unsupported information when relevant document evidence cannot be retrieved.

---

## Reusable Infrastructure

Technical capabilities such as:

* Embeddings
* Vector search
* LLM calls
* PDF extraction
* Storage
* RAG

are implemented as reusable infrastructure services.

---

## Database Integrity

Important constraints are enforced at the database level.

Examples include:

* Unique user emails
* Unique paper DOIs
* Unique document storage keys
* Vector dimensions
* Foreign-key relationships

---

## Ownership

Research papers and their associated documents are protected by user ownership.

---

## Scalable AI Architecture

The backend separates direct RAG from the agentic research workflow.

```text
Direct RAG
   ↓
Fast document question answering

Agentic RAG
   ↓
Multi-step research workflow
```

This allows the platform to support both simple document queries and more complex research interactions.

---

# Current Backend Status

The backend is currently complete for the implemented Research Intelligence Platform scope.

```text
Backend
│
├── FastAPI                         ✓
├── PostgreSQL                      ✓
├── SQLAlchemy                      ✓
├── Authentication                  ✓
├── Authorization                  ✓
├── Paper CRUD                      ✓
├── Search                          ✓
├── Filtering                       ✓
├── Sorting                         ✓
├── Pagination                      ✓
├── PDF Upload                      ✓
├── PDF Processing                 ✓
├── PDF Replacement                ✓
├── PDF Deletion                   ✓
├── PDF Download                   ✓
├── Text Chunking                  ✓
├── Embeddings                     ✓
├── pgvector                        ✓
├── Vector Search                   ✓
├── Direct RAG                      ✓
├── Grounded Answers                ✓
├── Source Retrieval                ✓
├── Paper Summarization             ✓
├── Paper Analysis                  ✓
├── Semantic Scholar                ✓
├── Research Agent                  ✓
├── LangGraph                       ✓
├── Conversation Memory             ✓
├── Context Management              ✓
├── Database Migrations              ✓
└── API Documentation               ✓
```

---

# Future Frontend Integration

The backend exposes REST APIs consumed by the separate React frontend.

```text
Research Intelligence Platform
│
├── Backend
│   ├── FastAPI
│   ├── PostgreSQL
│   ├── pgvector
│   ├── RAG
│   └── LangGraph Agent
│
└── Frontend
    ├── React
    ├── TypeScript
    └── Vite
```

The frontend communicates with the backend through authenticated HTTP requests.

---

# Project Status

The backend provides the core infrastructure for the Research Intelligence Platform, including paper management, document processing, semantic retrieval, grounded RAG, conversational research, and external research-paper recommendations.

The backend is ready to serve as the API layer for the platform's frontend and future deployment.

---

## License

This project is currently a personal/portfolio project.

Add your preferred license here before making the repository public if you intend to distribute the source under a specific license.


##Deployment

🐳 Docker Deployment

The project is distributed using pre-built Docker images, so you do not need to build the frontend or backend images yourself.

The Docker Compose configuration automatically pulls the required images from Docker Hub.

Prerequisites

Install:

Docker Desktop
Git

Make sure Docker Desktop is running before starting the application.

1. Clone the Repository

Clone the backend/main repository:

git clone <YOUR-BACKEND-REPOSITORY-URL>
cd "Research Intelligence Platform"
2. Configure Environment Variables

Create your local environment file from the example:

cp .env.example .env

On Windows PowerShell, you can use:

Copy-Item .env.example .env

Open .env and configure the required values.

Example structure:

APP_NAME=Research Intelligence Platform
APP_VERSION=1.0.0
DEBUG=True

DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=research_platform
DATABASE_USER=postgres
DATABASE_PASSWORD=your_database_password

OPENROUTER_API_KEY=your_openrouter_api_key
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key
Important

Never commit your real .env file to GitHub.

Your API keys and database credentials should remain private.

The repository should contain:

.env.example

but not:

.env
3. Start the Application

Run:

docker compose up -d

Docker Compose will start:

PostgreSQL
FastAPI backend
React frontend

The backend and frontend images are pulled automatically from Docker Hub.

4. Check Running Containers

Run:

docker ps

You should see containers similar to:

research-postgres
research-backend
research-intelligence-frontend

The PostgreSQL container should become healthy before the backend starts using the database.

5. Open the Application

Once the containers are running, open:

http://localhost:3000

The FastAPI backend is available at:

http://localhost:8000

FastAPI Swagger documentation:

http://localhost:8000/docs
🔄 Managing the Application
Stop the Application
docker compose stop

This stops the containers without removing them.

Start Again
docker compose start
View Container Status
docker ps
View Backend Logs
docker logs -f research-backend
View Frontend Logs
docker logs -f research-intelligence-frontend
View PostgreSQL Logs
docker logs -f research-postgres
Stop and Remove Containers
docker compose down
⚠️ Database Warning

Do not use:

docker compose down -v

unless you intentionally want to remove the Docker volume containing the PostgreSQL database.

The PostgreSQL data is stored in a persistent Docker volume so that restarting the containers does not automatically remove the database.

📁 Project Structure
Research Intelligence Platform/
│
├── app/
│   ├── config/
│   ├── features/
│   │   ├── auth/
│   │   ├── papers/
│   │   └── conversations/
│   │
│   ├── infrastructure/
│   │   ├── agent/
│   │   └── ...
│   │
│   └── main.py
│
├── storage/
│
├── Docs/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
