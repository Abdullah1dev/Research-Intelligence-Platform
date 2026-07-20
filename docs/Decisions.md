# Engineering Decisions

This document records the major architectural and technical decisions made during the design of the **Research Intelligence Platform**. These decisions act as the project's single source of truth and should be reviewed before introducing any significant architectural changes.

---

# Product Decisions

## Project Name

**Research Intelligence Platform**

A production-ready AI platform designed to help users discover, organize, understand, and learn from scientific research.

---

## Development Philosophy

The project is designed as a real-world software product rather than a tutorial project. Every major feature is planned, documented, and reviewed before implementation.

---

# Architecture Decisions

## Feature-Based Architecture

The backend follows a Vertical Slice (Feature-Based) Architecture.

Each feature owns:

- Router
- Business Logic
- Schemas
- Repository
- Tests

This improves scalability, maintainability, and feature isolation.

---

## Single Responsibility Principle

Every service is responsible for exactly one business capability.

Examples:

- Search Service
- Library Service
- AI Service
- Knowledge Engine
- Learning Intelligence

---

## LangGraph Responsibility

LangGraph is responsible only for AI workflows.

Business logic, authentication, and API handling remain inside the backend services.

---

## API-First Development

The backend will be completed before the frontend.

Every frontend feature will consume production-ready REST APIs.

---

# Database Decisions

## Primary Database

PostgreSQL

Reason:

Reliable relational database with excellent support for structured data and future scalability.

---

## Vector Search

pgvector

Reason:

Allows vector search directly inside PostgreSQL, reducing infrastructure complexity during the MVP.

---

## Business Data vs AI Data

Business data and AI-generated data remain separated.

Examples:

Business Data

- Users
- Collections
- Papers
- Conversations

AI Data

- Embeddings
- Chunks
- Summaries
- Keywords
- Concepts

---

## Paper Analysis

AI-generated paper information will be stored separately from paper metadata.

This allows AI analysis to evolve independently from the original source data.

---

# AI Decisions

## Knowledge Engine

A dedicated Knowledge Engine is responsible for

- Document Processing
- Chunking
- Embedding Generation
- Retrieval
- AI Metadata

---

## Background Processing

Long-running operations never block the user.

Tasks such as

- PDF Processing
- Chunk Generation
- Embedding Creation
- Paper Analysis

run asynchronously using background workers.

---

# Technology Decisions

Backend

FastAPI

Frontend

Next.js

Database

PostgreSQL

Vector Search

pgvector

AI Framework

LangGraph

Deployment

Docker

Background Jobs

Dramatiq + Redis

---

# Engineering Principles

The following principles guide every implementation:

- Backend First
- API First
- Docker From Day One
- Feature Isolation
- One Owner Per Data
- One Responsibility Per Service
- Production-Ready Code
- Modular Design
- Scalable Architecture
- Documentation Before Implementation

---

# Development Order

The project will be implemented in the following order:

1. Folder Structure
2. Database
3. Core Backend
4. Search Service
5. Knowledge Engine
6. AI Service
7. Background Workers
8. Frontend
9. Testing
10. Deployment

---

This document should be updated whenever a major architectural decision changes.