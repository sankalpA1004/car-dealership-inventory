# AutoHaus — Car Dealership Inventory System

A full-stack car dealership inventory application built for the **TDD Kata: Car Dealership Inventory System**. It includes a FastAPI REST API, persistent SQLAlchemy database, JWT authentication, role-based administration, atomic stock deductions, and a responsive React + Tailwind CSS SPA.

> **Project status:** Source code and automated tests are included. Run the verification steps below in your own environment before claiming a test result. The unauthenticated page uses a clearly labeled preview collection; sign in to access the live database inventory. No live deployment or public repository has been created by this archive.

## Features

- Register and log in with email/password; passwords are hashed with bcrypt.
- JWT bearer authentication for inventory endpoints.
- Persistent SQLite database by default; configurable via `DATABASE_URL`.
- Create, list, search, update, delete, purchase and restock vehicle records.
- Admin-only create/update/delete/restock operations; regular users can view and purchase.
- Search by make, model, category, and minimum/maximum price.
- Validated prices and quantities; stock cannot be purchased below zero.
- Atomic conditional stock updates reduce overselling under concurrent purchase requests.
- Purchase history records the user, vehicle, quantity, price and timestamp.
- Responsive React UI with filtering, sorting, login/register modal, inventory management forms and stock-aware purchase controls.
- Pytest API tests and coverage-report configuration.

## Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2, Pydantic, PyJWT, salted PBKDF2 password hashing
- **Database:** SQLite by default (persistent file `backend/dealership.db`); PostgreSQL can be configured using a compatible SQLAlchemy URL and driver
- **Frontend:** React, Vite, HTML5, CSS3, Tailwind CSS, Lucide icons
- **Tests:** pytest, FastAPI TestClient, HTTPX, pytest-cov

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer and npm
- Git

## Run locally

### 1. Backend

Open a terminal:

```bash
cd backend
python -m venv .venv
```

Activate the environment:

- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies and configure a secret:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Set a strong `SECRET_KEY` before running outside a local demo. For PowerShell:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
```

For macOS/Linux:

```bash
export SECRET_KEY="replace-with-a-long-random-secret"
```

Start the API (the SQLite database/table schema is created at startup):

```bash
uvicorn app.main:app --reload
```

- API base URL: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### 2. Create an administrator

Public registration intentionally creates **regular users only**. In a second backend terminal, activate the same virtual environment and set credentials. Do not commit the credentials or `.env` file.

PowerShell:

```powershell
$env:ADMIN_EMAIL = "admin@example.com"
$env:ADMIN_PASSWORD = "use-a-unique-password-at-least-12-chars"
$env:ADMIN_NAME = "Dealership Admin"
python create_admin.py
```

macOS/Linux:

```bash
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="use-a-unique-password-at-least-12-chars"
export ADMIN_NAME="Dealership Admin"
python create_admin.py
```

Log in through the frontend with this account to access admin controls. The script creates or promotes the named account and resets its password to the supplied value.

### 3. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend expects the API at `http://localhost:8000` by default. To use another API origin, create `frontend/.env.local` with:

```env
VITE_API_URL=http://localhost:8000
```

The backend's `CORS_ORIGINS` environment variable accepts a comma-separated list; the default is `http://localhost:5173`.

### 4. Run tests and generate a test report

From the backend directory, with dependencies installed:

```bash
pytest
```

This runs the API tests and produces a terminal coverage summary plus `htmlcov/index.html`. To save a text test report:

```bash
pytest --junitxml=test-report.xml
```

Commit the actual report generated on your machine if required by your evaluator. Do not manually change test counts or claim tests passed without running them.

## API reference

All `/api/vehicles` endpoints require `Authorization: Bearer <access_token>`.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Create a regular user account |
| POST | `/api/auth/login` | Public | Authenticate and receive JWT |
| GET | `/api/vehicles` | Authenticated | List inventory |
| GET | `/api/vehicles/search?make=...&model=...&category=...&min_price=...&max_price=...` | Authenticated | Filter inventory |
| POST | `/api/vehicles` | Admin | Create vehicle |
| PUT | `/api/vehicles/{id}` | Admin | Update vehicle fields |
| DELETE | `/api/vehicles/{id}` | Admin | Delete vehicle |
| POST | `/api/vehicles/{id}/purchase` | Authenticated | Decrease stock; body `{"quantity": 1}` |
| POST | `/api/vehicles/{id}/restock` | Admin | Increase stock; body `{"quantity": 5}` |
| GET | `/api/health` | Public | Health check |

A vehicle has a database-generated unique ID, make, model, category, price, quantity, description and optional image URL. Prices must be nonnegative; quantities must be nonnegative. Purchase quantity must be at least one. Insufficient stock returns HTTP `409`; unauthenticated requests return `401`; authenticated non-admin attempts at admin-only actions return `403`.

### Example requests

Register:

```bash
curl -X POST http://localhost:8000/api/auth/register \\
  -H 'Content-Type: application/json' \\
  -d '{"email":"customer@example.com","full_name":"Sample Customer","password":"secure-password-123"}'
```

After logging in, use the returned `access_token` as a bearer token:

```bash
curl http://localhost:8000/api/vehicles \\
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

## TDD approach

The tests in `backend/tests/test_api.py` cover registration, duplicate accounts, invalid login, protected routes, role restrictions, vehicle creation and search, invalid prices, purchasing, insufficient stock, restocking, updating, deleting and invalid price ranges. The intended Red–Green–Refactor workflow is:

1. Add a test for one behavior and run it to observe a meaningful failure (Red).
2. Implement the minimum behavior needed to pass (Green).
3. Refactor without changing behavior; rerun the tests (Refactor).
4. Commit each meaningful stage with a descriptive message.

**Important:** this archive does not fabricate an earlier commit history. If demonstrating TDD is part of the evaluation, make incremental commits while developing and keep the real test output for each stage.

## Security and production notes

- Change `SECRET_KEY` to a strong random value before deployment; never deploy with the development fallback.
- Configure `CORS_ORIGINS` narrowly for the deployed frontend.
- The admin bootstrap script is a local operator tool; do not expose it as an API route.
- Use HTTPS in production, rate-limit authentication endpoints, and consider refresh-token/revocation strategy for a production system.
- SQLite is suitable for local evaluation. For multi-instance production deployments, use PostgreSQL and add database migration management (e.g. Alembic).
- Purchase quantity updates are conditional SQL updates. Consider explicit transaction isolation and a production database when scaling.
- Demo preview data is frontend-only and is not persisted; it is replaced with database inventory after login and successful API retrieval.

## Screenshots

Add real screenshots from your running application to `screenshots/` and embed them here before submission. Suggested captures:

1. `screenshots/homepage.png` — hero and collection grid.
2. `screenshots/search-filters.png` — search and filters applied.
3. `screenshots/login.png` — login/register modal.
4. `screenshots/admin-inventory.png` — admin view with add/edit/delete controls.
5. `screenshots/api-docs.png` — FastAPI `/docs` page.
6. `screenshots/test-report.png` — actual pytest terminal or HTML coverage report.

No screenshots are included yet because the application has not been launched in a browser in this environment. Do not use mock screenshots as evidence of a real run.

## My AI Usage

AI assistance was used in this project-building conversation to help plan the architecture and generate an initial implementation scaffold, including backend API structure, SQLAlchemy models, Pydantic schemas, security helpers, frontend components and styling, test cases, and documentation. The generated code should be reviewed and tested by the project author before submission.

The project author should update this section before submitting with the actual tools used, the exact tasks for which each tool was used, what they manually changed, the bugs they found, and what they learned. Do not claim that AI-generated code was independently written or verified if it was not. Be prepared to explain JWT authentication, password hashing, role checks, database transactions, the test suite and the UI implementation.

## PROMPTS.md and AI transparency

See the root `PROMPTS.md`. It records the assignment prompt and the instruction to build the project, but it is **not a complete export of the entire chat transcript**. Attach the raw, unedited chat export or a real public chat link there before final submission, as required by the assignment. Do not invent a public URL.

## License

For educational/kata use. Add a license if you intend to distribute the project publicly.
