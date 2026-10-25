# AutoHaus — Car Dealership Inventory System

A full-stack car dealership inventory management application developed for the **TDD Kata: Car Dealership Inventory System**. AutoHaus combines a FastAPI REST API, a persistent SQLAlchemy database, JWT-based authentication, role-based access control, and a responsive React frontend styled with Tailwind CSS.

The system supports vehicle management, inventory search, purchase operations, stock updates, and administrative controls, with a focus on data integrity, security, and testability.

## Features

- **Vehicle Management:** Create, view, update, and delete vehicle records.
- **Inventory Search:** Filter vehicles by make, model, category, and price range.
- **JWT Authentication:** Authenticate users and protect private API endpoints.
- **Role-Based Access Control:** Restrict vehicle creation, modification, deletion, and restocking to administrators.
- **Inventory Purchases:** Validate purchase quantities and prevent purchases exceeding available stock.
- **Stock Management:** Restock vehicles through authorized administrative operations.
- **Data Persistence:** Store inventory and purchase history in SQLite using SQLAlchemy.
- **Purchase History:** Record the user, vehicle, quantity, price, and timestamp for purchases.
- **Responsive Frontend:** React interface with search, sorting, authentication forms, and inventory controls.
- **Automated Testing:** Pytest-based API tests with coverage reporting.

## Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy 2 |
| Validation | Pydantic |
| Authentication | JWT, password hashing |
| Frontend | React, Vite |
| Styling | Tailwind CSS, HTML5, CSS3 |
| Icons | Lucide |
| Testing | pytest, FastAPI TestClient, HTTPX, pytest-cov |

## Project Structure

```text
car-dealership-inventory/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   └── create_admin.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
├── screenshots/
├── PROMPTS.md
├── README.md
└── TEST_REPORT.md
```

*This is a simplified overview; consult the repository for the complete file structure.*

## Prerequisites

Install the following before running the project:

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- Git

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/sankalpA1004/car-dealership-inventory.git
cd car-dealership-inventory
```

### 2. Set up the backend

Open a terminal and run:

```powershell
cd backend
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python executable directly instead.

Install the dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Configure a strong secret key for local development:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
```

Start the backend:

```powershell
uvicorn app.main:app --reload
```

The API should now be available at:

- **API base URL:** http://localhost:8000
- **Interactive API documentation:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/api/health

The default database is SQLite, stored in `backend/dealership.db`.

### 3. Create an administrator account

Public registration creates regular user accounts. To create or promote an administrator, open another terminal and configure the administrator credentials.

From the `backend` directory, with the virtual environment activated:

```powershell
$env:ADMIN_EMAIL = "admin@example.com"
$env:ADMIN_PASSWORD = "use-a-unique-password-at-least-12-chars"
$env:ADMIN_NAME = "Dealership Admin"

python create_admin.py
```

Use your own credentials. Never commit real passwords, secret keys, or environment files to GitHub.

Sign in through the frontend with the administrator account to access administrative controls.

### 4. Start the frontend

Open a separate terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally:

http://localhost:5173

By default, the frontend connects to the API at `http://localhost:8000`.

To configure a different API address, create `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

The backend supports a configurable `CORS_ORIGINS` environment variable for permitted frontend origins.

## API Reference

Protected vehicle endpoints require a JWT bearer token:

```http
Authorization: Bearer <access_token>
```

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Register a regular user |
| POST | `/api/auth/login` | Public | Authenticate and receive a JWT |
| GET | `/api/vehicles` | Authenticated | List vehicles |
| GET | `/api/vehicles/search` | Authenticated | Search and filter vehicles |
| POST | `/api/vehicles` | Admin | Create a vehicle |
| PUT | `/api/vehicles/{id}` | Admin | Update a vehicle |
| DELETE | `/api/vehicles/{id}` | Admin | Delete a vehicle |
| POST | `/api/vehicles/{id}/purchase` | Authenticated | Purchase vehicles and reduce stock |
| POST | `/api/vehicles/{id}/restock` | Admin | Increase available stock |
| GET | `/api/health` | Public | Check API availability |

### Example: List vehicles

After logging in, use the returned access token:

```bash
curl http://localhost:8000/api/vehicles \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Search parameters

The search endpoint supports the following filters:

- `make`
- `model`
- `category`
- `min_price`
- `max_price`

Example:

```text
GET /api/vehicles/search?make=Toyota&min_price=5000&max_price=30000
```

### Inventory validation

- Prices must be nonnegative.
- Stock quantities must be nonnegative.
- Purchase quantities must be at least one.
- Purchases exceeding available stock are rejected.
- Unauthenticated requests to protected endpoints return HTTP `401`.
- Authenticated users without the required administrative privileges receive HTTP `403`.
- Insufficient stock returns HTTP `409`.

## Testing

The backend tests are located in `backend/tests/test_api.py`.

From the backend directory, with dependencies installed, run:

```powershell
pytest
```

To generate a JUnit XML test report:

```powershell
pytest --junitxml=test-report.xml
```

The project includes pytest coverage configuration. The test run can also produce an HTML coverage report at `htmlcov/index.html`, depending on the configured test command.

To build the frontend, open a terminal in `frontend`:

```powershell
npm run build
```

Test coverage and pass/fail results should be recorded from actual executions. Do not treat a successful frontend launch as proof that every backend feature or security requirement has passed testing.

## Test-Driven Development

The project follows the Red-Green-Refactor approach:

1. **Red:** Write a test for the expected behavior and confirm that it fails for the intended reason.
2. **Green:** Implement the smallest change needed to make the test pass.
3. **Refactor:** Improve the code while preserving the passing behavior.
4. **Verify:** Rerun the relevant tests and commit meaningful changes.

Important test scenarios include authentication, duplicate registration, protected endpoints, role restrictions, vehicle creation and search, invalid prices, purchases, insufficient stock, restocking, updating, and deletion.

## Security Considerations

- Passwords are stored as hashes rather than plaintext.
- JWTs protect authenticated API operations.
- Administrative permissions are enforced on the backend.
- Input validation helps prevent invalid vehicle and stock data.
- Conditional stock updates help reduce overselling during concurrent purchases.
- Secrets and administrator credentials must be configured outside source control.
- Production deployments should use HTTPS and appropriately restricted CORS settings.

For production use, additional measures may include authentication rate limiting, token revocation or refresh-token management, database migrations, and a production-grade database configuration.

## Screenshots

Add screenshots captured from the running application to the `screenshots/` directory.

Recommended screenshots:

1. Main inventory dashboard.
2. Search and filter results.
3. Login or registration interface.
4. Administrator inventory controls.
5. FastAPI interactive documentation.
6. Actual automated test output.

Once the images exist in the repository, embed them here using relative paths. Do not use mock images as evidence of a real application run.

## AI Usage

ChatGPT assisted with selected development activities, including architecture planning, initial code scaffolding, API and database design, authentication components, frontend structure, test ideas, debugging guidance, and documentation.

AI-generated suggestions require review and validation. The project author is responsible for understanding the implementation, testing application behavior, reviewing security controls, and ensuring that documented results accurately reflect the current code.

The root `PROMPTS.md` file contains a curated collection of development prompts related to the project. It should not be interpreted as a verbatim historical transcript unless an actual conversation export or transcript is included.

## Known Limitations and Future Improvements

Potential areas for further development include:

- Add database migrations using Alembic.
- Add rate limiting for authentication endpoints.
- Improve automated test coverage for edge cases and concurrent operations.
- Capture screenshots and document verified test results.
- Configure PostgreSQL and production deployment settings if required.

These items should be treated as future work unless already implemented and verified.

## License

Developed for educational purposes as part of the Car Dealership Inventory System TDD Kata. Add an explicit open-source license if you intend to distribute the project under specific reuse terms.
