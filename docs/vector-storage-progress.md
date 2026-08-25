# Vector Storage Progress

## Current Document Processing Pipeline

The Research Intelligence Platform currently follows this document-processing pipeline:

```text
PDF Upload
    ↓
Local Storage
    ↓
PDF Extraction
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
Vector Storage
```

## Completed

* PDF upload and local storage
* PDF text extraction
* Document chunking
* Background document processing
* Document processing status tracking
* Embedding generation and testing

## Next Step

The next stage is integrating **pgvector with PostgreSQL** so document embeddings can be stored alongside the existing research-paper data.

The planned retrieval pipeline is:

```text
User Query
    ↓
Query Embedding
    ↓
PostgreSQL + pgvector
    ↓
Similarity Search
    ↓
Relevant Document Chunks
    ↓
RAG Pipeline
```

## Status

The project is currently preparing the PostgreSQL vector-storage layer. pgvector installation and database integration are the next implementation steps.
