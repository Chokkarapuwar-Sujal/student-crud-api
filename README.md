# EWB Student Database CRUD API

A Student Database CRUD Application built for the EWB Edu Tech Pvt. Ltd. internship project. This API lets you create, read, update, and delete student records.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Programming language |
| FastAPI | Web framework for building the REST API |
| Uvicorn | ASGI server to run the application |
| SQLite | Lightweight relational database (included with Python) |
| Pydantic | Request/response validation |
| pytest | Testing framework |
| httpx | HTTP client used by FastAPI's TestClient |

## Prerequisites

- Python 3.10 or later (`python --version` to check)
- pip (comes with Python)

## Installation (Windows)

```powershell
cd student-crud-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

You should see `(.venv)` at the beginning of your terminal prompt after activation.

## Running the Application

```bash
python main.py
```

Or:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at http://127.0.0.1:8000

Interactive docs: http://127.0.0.1:8000/docs (Swagger UI)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /students | Create a new student |
| GET | /students | List all students (optional name/course filter) |
| GET | /students/{student_id} | Get a single student |
| PUT | /students/{student_id} | Update student details (partial) |
| DELETE | /students/{student_id} | Delete a student |

## Student Record Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| student_id | Integer | Auto | Auto-generated primary key |
| name | String | Yes | Max 100 characters |
| date_of_birth | String | Yes | YYYY-MM-DD format, must be in the past |
| email | String | No* | Valid email format |
| phone | String | No* | Max 20 characters |
| course | String | Yes | Max 100 characters |
| address | String | No | Max 300 characters |
| enrollment_date | String | Yes | YYYY-MM-DD format |

*At least one of email or phone is required.

## Example Requests

### Create a Student

```bash
curl -X POST http://127.0.0.1:8000/students -H "Content-Type: application/json" -d "{\"name\": \"Rahul Sharma\", \"date_of_birth\": \"2000-05-15\", \"email\": \"rahul@example.com\", \"phone\": \"9876543210\", \"course\": \"Computer Science\", \"address\": \"Mumbai\", \"enrollment_date\": \"2024-08-01\"}"
```

Response (201):
```json
{
  "student_id": 1,
  "name": "Rahul Sharma",
  "date_of_birth": "2000-05-15",
  "email": "rahul@example.com",
  "phone": "9876543210",
  "course": "Computer Science",
  "address": "Mumbai",
  "enrollment_date": "2024-08-01"
}
```

### List Students

```bash
curl http://127.0.0.1:8000/students
```

### Filter by Name

```bash
curl "http://127.0.0.1:8000/students?name=Rahul"
```

### Update a Student (Partial)

```bash
curl -X PUT http://127.0.0.1:8000/students/1 -H "Content-Type: application/json" -d "{\"course\": \"Data Science\"}"
```

Only the fields you include are updated; everything else stays the same.

### Delete a Student

```bash
curl -X DELETE http://127.0.0.1:8000/students/1
```

## Running Tests

```bash
pytest tests/ -v
```

## Database

- SQLite (built into Python, no external server needed)
- File: `students.db` is created automatically when the app starts
- All queries use parameterized placeholders (?) to prevent SQL injection
- The database file is excluded from version control via .gitignore

## Project Structure

```
student-crud-api/
├── .gitignore
├── .venv/               # virtual environment (not committed)
├── database.py          # SQLite connection and table setup
├── main.py              # FastAPI app and all endpoints
├── schemas.py           # Pydantic validation models
├── requirements.txt     # Python dependencies
├── README.md
├── students.db          # SQLite database (auto-created)
└── tests/
    ├── __init__.py
    └── test_api.py      # Automated tests
```

## License

This project was created for the EWB Edu Tech Pvt. Ltd. internship assignment.
