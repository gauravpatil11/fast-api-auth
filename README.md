# FastAPI Auth Service

This project is a FastAPI-based authentication and user-management service with:

- user registration and login
- JWT bearer-token authentication
- forgot-password and OTP-based password reset
- profile management
- admin-only user listing
- strategy CRUD for authenticated users

## Tech Stack

- FastAPI
- SQLAlchemy
- MySQL via `PyMySQL`
- Pydantic
- JWT via `python-jose`
- Password hashing via `pwdlib`
- Uvicorn

## Project Structure

```text
fast-api-auth/
|-- src/
|   |-- app.py
|   |-- config.py
|   |-- socket_manager.py
|   |-- constant/
|   |   `-- app_constants.py
|   |-- controllers/
|   |   |-- auth_controller.py
|   |   |-- exceptions.py
|   |   |-- strategy_controller.py
|   |   `-- user_controller.py
|   |-- models/
|   |   |-- database.py
|   |   |-- db_models.py
|   |   |-- schemas.py
|   |   |-- strategy_crud.py
|   |   `-- user_crud.py
|   |-- routes/
|   |   |-- auth_routes.py
|   |   |-- strategy_routes.py
|   |   `-- user_routes.py
|   `-- utils/
|       |-- dependencies.py
|       |-- exception_handlers.py
|       |-- logging.py
|       |-- middleware.py
|       |-- request_context.py
|       |-- responses.py
|       `-- security.py
|-- .env
|-- requirements.txt
|-- server-out.log
|-- server-error.log
`-- README.md
```

## Internal Layering

The project is organized in a clean request flow:

1. `routes/`
   Defines API endpoints, request methods, and response models.

2. `controllers/`
   Contains business logic such as registration, login, password reset, profile updates, and strategy operations.

3. `models/db_models.py`
   Defines the SQLAlchemy database tables.

4. `models/schemas.py`
   Defines request and response schemas, validation rules, and shared API response models.

5. `models/*_crud.py`
   Handles low-level database operations such as fetching, creating, updating, and deleting rows.

6. `utils/`
   Contains shared infrastructure like authentication helpers, dependencies, middleware, logging, standardized responses, and exception handling.

7. `app.py`
   Wires everything together by creating the FastAPI app, registering middleware and exception handlers, and including all routers.

## How the Request Flow Works

For most API calls, the flow is:

`Client -> route -> controller -> CRUD/data access -> database`

For protected routes, authentication is checked in dependencies before the controller runs.

## Setup

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create or update the `.env` file in the project root.

Example:

```env
APP_NAME=FastAPI Auth Service
APP_ENV=development
APP_DEBUG=true
APP_HOST=127.0.0.1
APP_PORT=8000
APP_LOG_LEVEL=INFO
AUTO_CREATE_TABLES=true

DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fastapi_auth
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

RESET_TOKEN_EXPIRE_MINUTES=5
RESET_OTP_LENGTH=6

FRONTEND_URL=http://localhost:3000
PASSWORD_RESET_URL_BASE=http://localhost:3000
PASSWORD_RESET_PATH=/reset-password

MAIL_HOST=
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM_EMAIL=
MAIL_USE_TLS=true
```

### 4. Create the database

Make sure MySQL is running, then create the database:

```sql
CREATE DATABASE fastapi_auth;
```

If `AUTO_CREATE_TABLES=true`, the application will automatically create the tables on startup.

## Running the App

Start the app with:

```powershell
uvicorn src.app:app --reload
```

This means:

- `src.app` points to `src/app.py`
- `app` is the FastAPI application object
- `--reload` restarts the server automatically when files change

Once the app is running in development mode, docs are typically available at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Authentication Flow

- `POST /auth/register` accepts JSON with `username`, `email`, and `password`.
- `POST /auth/login` accepts JSON with `email` and `password`.
- `POST /auth/forgot-password` accepts JSON with `email`, then sends a password reset OTP.
- `POST /auth/reset-password` accepts JSON with `email`, `otp`, and `new_password`.
- `GET /user/profile` returns the authenticated user profile.
- `PUT /user/profile` updates the authenticated user's `username`.
- `POST /user/change-password` accepts JSON with `current_password` and `new_password`.
- `GET /user/userlist` is accessible only to admin users.
- Strategy endpoints under `/strategies` are accessible only to authenticated users.

Protected routes expect:

```http
Authorization: Bearer <access_token>
```

## Main Endpoints

### 1. Register

`POST /auth/register`

Request body:

```json
{
  "username": "gaurav",
  "email": "gaurav@example.com",
  "password": "StrongPass123"
}
```

Example success response:

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "username": "gaurav",
      "email": "gaurav@example.com",
      "id": 1,
      "is_active": true,
      "is_admin": false
    },
    "token": {
      "access_token": "jwt_token_here",
      "token_type": "bearer"
    }
  },
  "error": null,
  "meta": {
    "request_id": "request-id-value"
  }
}
```

### 2. Login

`POST /auth/login`

Request body:

```json
{
  "email": "gaurav@example.com",
  "password": "StrongPass123"
}
```

Example success response:

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "jwt_token_here",
    "token_type": "bearer"
  },
  "error": null,
  "meta": {
    "request_id": "request-id-value"
  }
}
```

### 3. Forgot Password

`POST /auth/forgot-password`

Request body:

```json
{
  "email": "gaurav@example.com"
}
```

Example success response:

```json
{
  "success": true,
  "message": "If the account exists, password reset instructions will be sent",
  "data": {
    "detail": "If the account exists, password reset instructions will be sent",
    "otp_preview": "123456"
  },
  "error": null,
  "meta": {
    "request_id": "request-id-value"
  }
}
```

Note: `otp_preview` is meant for non-production behavior. In production it may be omitted.

### 4. Reset Password

`POST /auth/reset-password`

Request body:

```json
{
  "email": "gaurav@example.com",
  "otp": "123456",
  "new_password": "NewStrongPass123"
}
```

### 5. Get Profile

`GET /user/profile`

Requires bearer token.

### 6. Update Profile

`PUT /user/profile`

Request body:

```json
{
  "username": "gaurav_new"
}
```

Requires bearer token.

### 7. Change Password

`POST /user/change-password`

Request body:

```json
{
  "current_password": "StrongPass123",
  "new_password": "AnotherStrongPass123"
}
```

Requires bearer token.

### 8. List Users

`GET /user/userlist`

Requires bearer token and admin access.

### 9. Create Strategy

`POST /strategies`

Request body:

```json
{
  "strategy_name": "Bull Call Spread",
  "legs": [
    {
      "side": "BUY",
      "expiry": "2026-04-30",
      "strike": 22000,
      "type": "CE",
      "lots": 1
    },
    {
      "side": "SELL",
      "expiry": "2026-04-30",
      "strike": 22500,
      "type": "CE",
      "lots": 1
    }
  ],
  "multiplier": 1
}
```

Requires bearer token.

### 10. Strategy CRUD Routes

- `POST /strategies`
- `GET /strategies`
- `GET /strategies/{strategy_id}`
- `PUT /strategies/{strategy_id}`
- `DELETE /strategies/{strategy_id}`

## Standard API Response Shape

Successful responses follow this structure:

```json
{
  "success": true,
  "message": "Human readable success message",
  "data": {},
  "error": null,
  "meta": {
    "request_id": "request-id-value"
  }
}
```

Error responses follow this structure:

```json
{
  "success": false,
  "message": "Human readable error message",
  "data": null,
  "error": {
    "code": "validation_error",
    "details": []
  },
  "meta": {
    "request_id": "request-id-value"
  }
}
```

## Database Notes

The project uses SQLAlchemy with MySQL.

Main tables:

- `users`
- `strategies`

The `users` table stores:

- username
- email
- hashed password
- active/admin flags
- password reset OTP hash and expiry fields

The `strategies` table stores:

- the owning user ID
- strategy name
- JSON list of legs
- multiplier
- timestamps

## Logging

Logs are written to:

- `server-out.log`
- `server-error.log`

The application also adds request-level metadata such as request ID and processing time.

## Testing

There are currently no dedicated test files or test suite configured in this repository.

That means:

- no `tests/` folder is present
- no `pytest` setup is currently included
- verification is mainly manual through API calls or Swagger docs

If you extend the project, adding automated tests for auth, user, and strategy flows would be a strong next step.

## Suggested Study Order

To understand the project flow, study files in this order:

1. `README.md`
2. `requirements.txt`
3. `src/app.py`
4. `src/config.py`
5. `src/constant/app_constants.py`
6. `src/models/database.py`
7. `src/models/db_models.py`
8. `src/models/schemas.py`
9. `src/utils/request_context.py`
10. `src/utils/logging.py`
11. `src/utils/middleware.py`
12. `src/utils/responses.py`
13. `src/controllers/exceptions.py`
14. `src/utils/exception_handlers.py`
15. `src/utils/security.py`
16. `src/utils/dependencies.py`
17. `src/models/user_crud.py`
18. `src/controllers/auth_controller.py`
19. `src/routes/auth_routes.py`
20. `src/controllers/user_controller.py`
21. `src/routes/user_routes.py`
22. `src/models/strategy_crud.py`
23. `src/controllers/strategy_controller.py`
24. `src/routes/strategy_routes.py`
25. `src/socket_manager.py`

Read these last or just skim:

- `src/__init__.py`
- `src/routes/__init__.py`
- `src/controllers/__init__.py`
- `src/models/__init__.py`
- `src/utils/__init__.py`
- `src/constant/__init__.py`

Optional after code reading:

- `server-out.log`
- `server-error.log`

## Notes

- In development, docs are enabled unless `APP_ENV=production`.
- The app validates important settings at startup.
- If email settings are not configured, OTP behavior may fall back to logging instead of sending real email.
