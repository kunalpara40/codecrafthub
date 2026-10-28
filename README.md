# CodeCraftHub Learning Management System

CodeCraftHub is a beginner-friendly REST API built with Python and Flask. It helps developers track courses they want to learn. Course data is stored in a local `courses.json` file, so no database or authentication is required.

## Features

- Create, list, retrieve, update, and delete courses (CRUD).
- Automatically generated numeric IDs and creation timestamps.
- Validates required fields, date format, and course status.
- Stores data in a JSON file.
- Includes a bonus course statistics endpoint.
- Includes automated tests using Python's `unittest` framework.

## Requirements

- Python 3.9 or newer recommended.
- pip.
- `curl` (included on many systems; PowerShell users may use `curl.exe`).

## Project structure

```text
codecrafthub/
├── app.py
├── courses.json
├── requirements.txt
├── README.md
└── tests/
    └── test_app.py
```

- `app.py`: Flask application and API endpoints.
- `courses.json`: persistent course data; initialized automatically if missing.
- `requirements.txt`: Python dependencies.
- `tests/test_app.py`: automated API tests.

## Installation

1. Open a terminal in the project directory.
2. Create and activate a virtual environment (recommended):

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Run the application

```bash
python app.py
```

The API runs at `http://localhost:5000`. Keep this terminal open while testing. Open a second terminal for `curl` commands.

## API endpoints

Valid statuses are exactly `Not Started`, `In Progress`, and `Completed`. Dates must be real dates in `YYYY-MM-DD` format.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Welcome message |
| POST | `/api/courses` | Create a course |
| GET | `/api/courses` | List all courses |
| GET | `/api/courses/<id>` | Get one course |
| PUT | `/api/courses/<id>` | Update one or more fields |
| DELETE | `/api/courses/<id>` | Delete a course |
| GET | `/api/courses/stats` | Bonus: totals grouped by status |

### Create a course

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Python Basics","description":"Learn Python fundamentals","target_date":"2027-12-31","status":"Not Started"}'
```

A successful create returns HTTP `201 Created`, including the new course's ID and `created_at` timestamp.

### List all courses

```bash
curl http://localhost:5000/api/courses
```

### Get a specific course

```bash
curl http://localhost:5000/api/courses/1
```

### Update a course

PUT accepts one or more fields to update:

```bash
curl -X PUT http://localhost:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"In Progress"}'
```

### Delete a course

```bash
curl -X DELETE http://localhost:5000/api/courses/1
```

### Course statistics (bonus)

```bash
curl http://localhost:5000/api/courses/stats
```

### Error examples

Missing field:

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Incomplete"}'
```

Invalid status:

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","description":"Test course","target_date":"2027-12-31","status":"Started"}'
```

Course not found:

```bash
curl -i http://localhost:5000/api/courses/999
```

Errors return a JSON object with `success: false` and an explanation. Typical status codes are `400` for invalid input, `404` for a missing course or route, and `500` if the JSON file cannot be read or written.

## Automated tests

With dependencies installed, run:

```bash
python -m unittest discover -s tests -v
```

The tests cover CRUD operations, validation errors, missing courses, statistics, and JSON persistence.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'flask'`**: Activate your virtual environment and run `python -m pip install -r requirements.txt`.
- **Port 5000 already in use**: Stop the other server process or change the port in the final `app.run(...)` line.
- **Invalid JSON in `courses.json`**: Back up the file, then repair it so it contains a JSON list (for example, `[]`).
- **PowerShell command differences**: Use `curl.exe` in PowerShell if `curl` is mapped to another command.

## Data format

Each course is saved with this shape:

```json
{
  "id": 1,
  "name": "Python Basics",
  "description": "Learn Python fundamentals",
  "target_date": "2027-12-31",
  "status": "Not Started",
  "created_at": "2026-10-28 12:00:00"
}
```

The timestamp above is an example; the application generates the actual value when a course is created.
