# Papers Module Documentation

## 1. Overview

The Papers module is responsible for managing research papers within the Research Intelligence Platform.

It provides authenticated users with the ability to:

* Create research papers
* Retrieve their papers
* Retrieve a specific paper
* Update papers
* Delete papers
* Search papers
* Filter papers
* Sort papers
* Paginate paper results
* View pagination metadata

The module also enforces ownership and database-level uniqueness for DOI values.

---

## 2. Module Structure

The Papers feature follows a feature-based architecture:

```text
app/
└── features/
    └── papers/
        ├── __init__.py
        ├── models.py
        ├── schemas.py
        ├── enums.py
        ├── service.py
        └── router.py
```

### Responsibilities

| File         | Responsibility                                    |
| ------------ | ------------------------------------------------- |
| `models.py`  | SQLAlchemy database model                         |
| `schemas.py` | Pydantic request/response validation              |
| `enums.py`   | Fixed choices such as sorting fields and ordering |
| `service.py` | Business logic and database operations            |
| `router.py`  | FastAPI endpoints and API documentation           |

---

# 3. Paper Database Model

The `Paper` model represents a research paper stored in PostgreSQL.

## Fields

| Field              | Type     | Description                       |
| ------------------ | -------- | --------------------------------- |
| `id`               | Integer  | Primary key                       |
| `title`            | String   | Paper title                       |
| `abstract`         | String   | Paper abstract                    |
| `authors`          | String   | Paper authors                     |
| `publication_year` | Integer  | Year of publication               |
| `journal`          | String   | Journal or publication venue      |
| `doi`              | String   | Digital Object Identifier         |
| `category`         | String   | Research category                 |
| `pdf_url`          | String   | URL pointing to the paper PDF     |
| `owner_id`         | Integer  | ID of the user who owns the paper |
| `created_at`       | DateTime | Creation timestamp                |
| `updated_at`       | DateTime | Last update timestamp             |

## DOI uniqueness

The DOI column has a unique constraint.

This is intentional because a DOI identifies a specific publication.

For example:

```text
10.48550/arXiv.1706.03762
```

is an identifier for a particular paper.

Two different papers should not normally have the same DOI.

The database therefore prevents duplicate DOI values.

---

# 4. Authentication and Authorization

All paper operations require an authenticated user.

The authenticated user is obtained through the application's authentication dependency.

The user's ID is used as the paper's `owner_id`.

For example:

```text
User
  ID = 7
   │
   ├── Paper 1
   ├── Paper 2
   └── Paper 3
```

A user should not be able to modify or delete another user's papers simply by knowing the paper ID.

Ownership checks are therefore performed inside the Papers business logic.

---

# 5. Create Paper

## Endpoint

```http
POST /papers/
```

Creates a new research paper for the authenticated user.

## Request body

```json
{
  "title": "Attention Is All You Need",
  "abstract": "This paper introduces the Transformer architecture.",
  "authors": "Ashish Vaswani et al.",
  "publication_year": 2017,
  "journal": "NeurIPS",
  "doi": "10.48550/arXiv.1706.03762",
  "category": "Artificial Intelligence",
  "pdf_url": "https://example.com/paper.pdf"
}
```

The client does not provide:

```text
id
owner_id
created_at
updated_at
```

These are managed by the application.

## Successful response

```http
201 Created
```

The response contains the created paper and its generated database information.

---

# 6. Get All Papers

## Endpoint

```http
GET /papers/
```

Returns papers belonging to the authenticated user.

The endpoint supports:

* Pagination
* Filtering
* Searching
* Sorting
* Pagination metadata

---

# 7. Pagination

Pagination prevents the API from returning a very large number of records at once.

The endpoint supports:

```text
page
limit
```

Example:

```http
GET /papers/?page=1&limit=10
```

This means:

> Return the first page containing at most 10 papers.

Another request:

```http
GET /papers/?page=2&limit=10
```

returns the second page.

## Pagination calculation

The database offset is calculated as:

```text
offset = (page - 1) × limit
```

For example:

```text
page = 1
limit = 10

offset = (1 - 1) × 10
       = 0
```

For page 2:

```text
offset = (2 - 1) × 10
       = 10
```

For page 3:

```text
offset = (3 - 1) × 10
       = 20
```

---

# 8. Pagination Metadata

The API also returns metadata describing the result set.

Example:

```json
{
  "items": [],
  "page": 1,
  "limit": 10,
  "total": 37,
  "total_pages": 4
}
```

### Metadata

| Field         | Meaning                              |
| ------------- | ------------------------------------ |
| `items`       | Papers returned for the current page |
| `page`        | Current page                         |
| `limit`       | Maximum number of papers per page    |
| `total`       | Total number of matching papers      |
| `total_pages` | Total number of available pages      |

This allows a frontend application to build pagination controls such as:

```text
Previous | 1 | 2 | 3 | 4 | Next
```

---

# 9. Filtering

Filtering narrows the dataset based on specific paper properties.

## Category filtering

```http
GET /papers/?category=Artificial%20Intelligence
```

Returns papers belonging to the specified category.

## Publication year filtering

```http
GET /papers/?publication_year=2024
```

Returns papers published in 2024.

Filters can also be combined:

```http
GET /papers/?category=Artificial%20Intelligence&publication_year=2024
```

This means:

> Return AI papers published in 2024.

---

# 10. Searching

The Papers endpoint supports keyword searching.

The search functionality checks relevant text fields such as:

* title
* authors

Example:

```http
GET /papers/?search=transformer
```

The search uses case-insensitive matching.

For example, a search for:

```text
transformer
```

can match:

```text
Transformer Architecture
Transformers in Computer Vision
Efficient Transformer Models
```

---

# 11. Filtering vs Pagination

These two concepts serve different purposes.

### Filtering

Filtering answers:

> "Which papers do I want?"

Example:

```http
GET /papers/?category=AI
```

### Pagination

Pagination answers:

> "How many of those papers should I receive at once?"

Example:

```http
GET /papers/?category=AI&page=1&limit=10
```

The request first identifies the matching papers and then returns a specific page of those results.

---

# 12. Sorting

The Papers endpoint supports sorting.

Supported sorting fields include:

```text
title
publication_year
created_at
```

Supported ordering:

```text
asc
desc
```

## Sort by publication year

Newest first:

```http
GET /papers/?sort_by=publication_year&order=desc
```

Oldest first:

```http
GET /papers/?sort_by=publication_year&order=asc
```

## Sort by title

Alphabetical:

```http
GET /papers/?sort_by=title&order=asc
```

Reverse alphabetical:

```http
GET /papers/?sort_by=title&order=desc
```

## Sort by creation date

```http
GET /papers/?sort_by=created_at&order=desc
```

This is useful when the user wants the most recently added papers first.

---

# 13. Sorting Enums

Sorting values are represented using Python enums.

```python
class PaperSortField(str, Enum):
    TITLE = "title"
    PUBLICATION_YEAR = "publication_year"
    CREATED_AT = "created_at"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"
```

Enums are used because sorting fields and ordering directions are fixed choices.

They also allow FastAPI to automatically validate the incoming query parameters and expose the allowed values through Swagger/OpenAPI.

---

# 14. API Metadata

Query parameters are documented using FastAPI's `Query()` metadata.

For example:

```python
sort_by: PaperSortField = Query(
    PaperSortField.CREATED_AT,
    description="Field used to sort papers."
)
```

and:

```python
order: SortOrder = Query(
    SortOrder.DESC,
    description="Sorting direction."
)
```

This makes the API self-documenting in Swagger UI.

Instead of requiring a developer to guess the accepted values, Swagger exposes the available choices.

---

# 15. Sorting Implementation

The service layer maps allowed sorting fields to SQLAlchemy columns.

Conceptually:

```python
valid_sort_fields = {
    PaperSortField.TITLE: Paper.title,
    PaperSortField.PUBLICATION_YEAR: Paper.publication_year,
    PaperSortField.CREATED_AT: Paper.created_at,
}
```

The requested enum value is then mapped to the appropriate database column.

For ascending sorting:

```python
sort_column.asc()
```

For descending sorting:

```python
sort_column.desc()
```

---

# 16. Query Processing Order

The list endpoint follows an important logical order:

```text
Request
   ↓
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
Response + metadata
```

Sorting must happen before pagination.

For example, if the user requests:

```text
sort_by=publication_year
order=desc
limit=10
```

the system should first sort the complete matching dataset and then select the first 10 records.

Otherwise, the returned page could contain incorrect results.

---

# 17. Get Paper by ID

## Endpoint

```http
GET /papers/{paper_id}
```

Returns a specific paper.

Example:

```http
GET /papers/7
```

The service verifies that the requested paper belongs to the authenticated user before returning it.

---

# 18. Update Paper

## Endpoint

```http
PATCH /papers/{paper_id}
```

Updates an existing paper.

Only allowed fields are updated.

The service:

1. Finds the paper.
2. Verifies ownership.
3. Applies the requested changes.
4. Updates `updated_at`.
5. Commits the transaction.
6. Returns the updated paper.

If a new DOI conflicts with another paper, the database's unique constraint prevents the update.

---

# 19. Delete Paper

## Endpoint

```http
DELETE /papers/{paper_id}
```

Deletes a paper belonging to the authenticated user.

The service:

1. Finds the paper.
2. Verifies ownership.
3. Deletes the paper.
4. Commits the transaction.

If the paper does not exist or does not belong to the authenticated user, an appropriate HTTP error is returned.

---

# 20. Error Handling

The module handles common errors such as:

### Paper not found

```http
404 Not Found
```

### Unauthorized access

A user cannot operate on another user's paper.

### Duplicate DOI

The database raises a unique constraint violation if a duplicate DOI is inserted.

The service handles this condition and returns an appropriate API error rather than exposing the raw database exception.

### Invalid sorting field

FastAPI validation prevents unsupported sorting fields.

### Invalid sorting order

Only:

```text
asc
desc
```

are accepted.

### Invalid pagination

Pagination parameters are constrained so that invalid page numbers or unreasonable limits are rejected.

---

# 21. Example Combined Request

The endpoint can combine multiple capabilities.

Example:

```http
GET /papers/?search=transformer&category=Artificial%20Intelligence&publication_year=2024&sort_by=publication_year&order=desc&page=1&limit=10
```

This means:

> Search for transformer-related papers, restrict them to Artificial Intelligence papers published in 2024, sort them by publication year from newest to oldest, and return the first 10 results.

This demonstrates how the Papers endpoint acts as a complete paper-discovery API rather than just a basic CRUD endpoint.

---

# 22. Database Migrations

The Papers table is managed through Alembic migrations.

The migration history includes the creation of the Papers table.

Example migration revision:

```text
d929fe1d24f8
```

The migration chain ensures that the database schema and SQLAlchemy models remain synchronized.

Migrations should be used whenever the database structure changes.

---

# 23. Testing

The Papers module has been tested through the FastAPI Swagger UI.

The following operations have been verified:

```text
✓ Create paper
✓ Get all papers
✓ Get paper by ID
✓ Update paper
✓ Delete paper
✓ Authentication
✓ Ownership protection
✓ DOI uniqueness
✓ Duplicate DOI handling
✓ Search
✓ Filtering
✓ Pagination
✓ Pagination metadata
✓ Sorting
```

The module is currently functioning correctly.

---

# 24. Design Principles

The Papers module follows several important backend design principles:

### Separation of concerns

```text
Router
   ↓
Service
   ↓
Database
```

The router handles HTTP concerns while the service contains business logic.

### Validation at the API boundary

Pydantic schemas and FastAPI validation prevent invalid data from entering the application.

### Database integrity

Important constraints such as DOI uniqueness are enforced at the database level.

### Authorization

Ownership is checked before users can access or modify papers.

### Self-documenting API

FastAPI metadata and enums make query parameters understandable through Swagger/OpenAPI.

### Pagination

Large datasets are not returned in a single response.

### Flexible paper discovery

Search, filters, sorting, and pagination allow users to efficiently find relevant research papers.

---

# 25. Current Status

The Papers module is considered complete for the current backend stage.

```text
Papers Module
      │
      ├── Database model             ✓
      ├── Schemas                   ✓
      ├── Authentication            ✓
      ├── Authorization             ✓
      ├── Create                    ✓
      ├── Read                      ✓
      ├── Update                    ✓
      ├── Delete                    ✓
      ├── Search                    ✓
      ├── Filtering                 ✓
      ├── Pagination                ✓
      ├── Pagination metadata       ✓
      ├── Sorting                   ✓
      ├── Validation                ✓
      ├── Error handling            ✓
      └── Testing                   ✓
```

The module is now ready to serve as the foundation for the next components of the Research Intelligence Platform.
