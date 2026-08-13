# Authentication & Authorization Approach

## Overview

The Research Intelligence Platform uses JWT-based authentication and Role-Based Access Control (RBAC) to secure the API and control what different users are allowed to access.

## Authentication

Authentication is responsible for verifying the identity of a user.

Our authentication flow is:

1. User registers with name, email, and password.
2. The password is hashed using Argon2 before being stored in PostgreSQL.
3. During login, the user provides their email and password.
4. The stored password hash is verified against the provided password.
5. If the credentials are valid, the backend generates a JWT access token.
6. The token contains the user's identity and an expiration time.
7. Protected endpoints use `HTTPBearer` to extract the token from the request.
8. The JWT is decoded and verified using the application's secret key.
9. The current user is retrieved from the database.

Passwords are never stored in plain text.

## Authorization

Authorization determines what an authenticated user is allowed to do.

We implemented Role-Based Access Control (RBAC). Each user has a role stored in the database.

Current roles:

- `ADMIN` — full administrative access
- `RESEARCHER` — access to research-related functionality
- `REVIEWER` — access to review-related functionality

The `require_roles()` dependency checks the authenticated user's role before allowing access to protected endpoints.

If the user is authenticated but does not have the required role, the API returns:

```text
403 Forbidden