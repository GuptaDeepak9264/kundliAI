# Kundli AI

Kundli AI is a full-stack application that turns user-provided birth details into a structured, Markdown-based reflection report using Google Gemini. It includes JWT authentication, user profiles, report history, and an admin dashboard.

> **Important:** Astrology content is presented for entertainment and self-reflection. It is not medical, legal, financial, or professional advice.

## Features

- Signup, login, logout, JWT-protected pages, profile editing, password changes, and account deletion.
- Gemini-powered Kundli reports with structured Markdown and a responsive dark glassmorphism interface.
- Persistent report history with search, review, and deletion.
- MySQL persistence through SQLAlchemy; SQLite is used automatically only when `DATABASE_URL` is unset for local experimentation.
- Configurable admin bootstrap, user management, reports endpoint, and basic analytics.

## Project structure

```
Kundli-AI/
├── backend/
│   ├── main.py             # FastAPI routes and application setup
│   ├── auth.py             # JWT and password helpers
│   ├── database.py         # SQLAlchemy configuration
│   ├── models.py           # Users and Reports tables
│   ├── schemas.py          # API validation models
│   └── services/           # Gemini client and prompt construction
└── frontend/
    └── src/                # React pages, components, API client, styling
```

## Backend setup

1. Create a MySQL database:

   ```sql
   CREATE DATABASE kundli_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Copy `backend/.env.example` to `backend/.env`, then set `DATABASE_URL`, `SECRET_KEY`, and `GEMINI_API_KEY`.
3. Create and activate a virtual environment, then install dependencies:

   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Start the API:

   ```bash
   uvicorn main:app --reload --port 8000
   ```

Tables are created automatically at startup. When both `ADMIN_EMAIL` and `ADMIN_PASSWORD` are set in `.env`, the initial administrator is created safely on startup.

## Gemini API key

Create a Gemini API key in Google AI Studio, add it as `GEMINI_API_KEY` in `backend/.env`, and select a supported model in `GEMINI_MODEL` if needed. The default is `gemini-1.5-flash`.

## Frontend setup

1. Copy `frontend/.env.example` to `frontend/.env` and update `REACT_APP_API_URL` if the API runs elsewhere.
2. Install and run:

   ```bash
   cd frontend
   npm install
   npm start
   ```

The app opens at `http://localhost:3000`.

## API surface

- `POST /signup`, `POST /login`
- `POST /generate-kundli`, `GET /history`, `GET /report/{id}`, `DELETE /report/{id}`
- `GET /profile`, `PUT /profile`, `DELETE /account`
- `GET /admin/users`, `GET /admin/reports`, `GET /admin/analytics`, `DELETE /admin/users/{id}`

## Screenshots

_Placeholder: add deployed application screenshots here._

## Future improvements

- Add a birth-location geocoding provider and ephemeris calculation service for exact planetary data.
- Add rate limiting, database migrations with Alembic, email verification, and automated test coverage.
- Upgrade the Gemini SDK/model selection as Google evolves its API.
