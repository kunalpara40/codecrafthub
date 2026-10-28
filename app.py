"""CodeCraftHub: a beginner-friendly Flask REST API for tracking courses."""

from datetime import datetime
import json
import os
import tempfile

from flask import Flask, jsonify, request

app = Flask(__name__)

# Store the JSON file beside this app.py file, regardless of the current terminal directory.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "courses.json")
VALID_STATUSES = ["Not Started", "In Progress", "Completed"]
REQUIRED_FIELDS = ["name", "description", "target_date", "status"]


def load_courses():
    """Read courses from JSON. Create an empty file if it does not exist."""
    if not os.path.exists(DATA_FILE):
        save_courses([])
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            courses = json.load(file)
        if not isinstance(courses, list):
            raise ValueError("The JSON root must be a list.")
        return courses
    except (OSError, json.JSONDecodeError, ValueError):
        raise


def save_courses(courses):
    """Write courses to JSON using a temporary file to reduce risk of partial writes."""
    folder = os.path.dirname(DATA_FILE)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=folder, delete=False
        ) as temp_file:
            json.dump(courses, temp_file, indent=2)
            temp_file.write("\n")
            temp_path = temp_file.name
        os.replace(temp_path, DATA_FILE)
    except OSError:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise


def get_next_id(courses):
    """Generate the next ID, starting at 1."""
    return max((course.get("id", 0) for course in courses), default=0) + 1


def valid_date(value):
    """Return True when a date matches YYYY-MM-DD and is a real calendar date."""
    if not isinstance(value, str):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return len(value) == 10
    except ValueError:
        return False


def storage_error():
    """Consistent response when the JSON file cannot be read or written."""
    return jsonify({"success": False, "error": "Unable to read or write courses.json"}), 500


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.route("/")
def home():
    return jsonify({"success": True, "message": "Welcome to CodeCraftHub API"}), 200


@app.route("/api/courses", methods=["GET"])
def get_all_courses():
    try:
        courses = load_courses()
    except (OSError, json.JSONDecodeError, ValueError):
        return storage_error()
    return jsonify({"success": True, "count": len(courses), "courses": courses}), 200


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    try:
        courses = load_courses()
    except (OSError, json.JSONDecodeError, ValueError):
        return storage_error()

    course = next((item for item in courses if item.get("id") == course_id), None)
    if course is None:
        return jsonify({"success": False, "error": "Course not found"}), 404
    return jsonify({"success": True, "course": course}), 200


@app.route("/api/courses", methods=["POST"])
def add_course():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Request body must be a JSON object"}), 400

    for field in REQUIRED_FIELDS:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({"success": False, "error": f"Missing or invalid required field: {field}"}), 400

    if not valid_date(data["target_date"]):
        return jsonify({"success": False, "error": "target_date must be a valid date in YYYY-MM-DD format"}), 400

    if data["status"] not in VALID_STATUSES:
        return jsonify({
            "success": False,
            "error": f"Status must be one of: {', '.join(VALID_STATUSES)}"
        }), 400

    try:
        courses = load_courses()
        course = {
            "id": get_next_id(courses),
            "name": data["name"].strip(),
            "description": data["description"].strip(),
            "target_date": data["target_date"],
            "status": data["status"],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        courses.append(course)
        save_courses(courses)
    except (OSError, json.JSONDecodeError, ValueError):
        return storage_error()

    return jsonify({
        "success": True,
        "message": "Course added successfully",
        "course": course
    }), 201


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Request body must be a JSON object"}), 400

    allowed_fields = ["name", "description", "target_date", "status"]
    unknown_fields = set(data) - set(allowed_fields)
    if unknown_fields:
        return jsonify({
            "success": False,
            "error": f"Unsupported fields: {', '.join(sorted(unknown_fields))}"
        }), 400
    if not data:
        return jsonify({"success": False, "error": "Provide at least one field to update"}), 400

    for field, value in data.items():
        if not isinstance(value, str) or not value.strip():
            return jsonify({"success": False, "error": f"Invalid value for {field}"}), 400
        if field == "target_date" and not valid_date(value):
            return jsonify({"success": False, "error": "target_date must be a valid date in YYYY-MM-DD format"}), 400
        if field == "status" and value not in VALID_STATUSES:
            return jsonify({
                "success": False,
                "error": f"Status must be one of: {', '.join(VALID_STATUSES)}"
            }), 400

    try:
        courses = load_courses()
        course = next((item for item in courses if item.get("id") == course_id), None)
        if course is None:
            return jsonify({"success": False, "error": "Course not found"}), 404

        course.update({field: value.strip() for field, value in data.items()})
        save_courses(courses)
    except (OSError, json.JSONDecodeError, ValueError):
        return storage_error()

    return jsonify({
        "success": True,
        "message": "Course updated successfully",
        "course": course
    }), 200


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    try:
        courses = load_courses()
        course_index = next(
            (index for index, item in enumerate(courses) if item.get("id") == course_id),
            None
        )
        if course_index is None:
            return jsonify({"success": False, "error": "Course not found"}), 404

        deleted_course = courses.pop(course_index)
        save_courses(courses)
    except (OSError, json.JSONDecodeError, ValueError):
        return storage_error()

    return jsonify({
        "success": True,
        "message": "Course deleted successfully",
        "deleted_course": deleted_course
    }), 200


@app.route("/api/courses/stats", methods=["GET"])
def course_stats():
    """Optional bonus endpoint: total courses and counts grouped by status."""
    try:
        courses = load_courses()
    except (OSError, json.JSONDecodeError, ValueError):
        return storage_error()

    counts = {status: 0 for status in VALID_STATUSES}
    for course in courses:
        if course.get("status") in counts:
            counts[course["status"]] += 1

    return jsonify({
        "success": True,
        "total_courses": len(courses),
        "by_status": counts
    }), 200


if __name__ == "__main__":
    print("CodeCraftHub API is starting...")
    print(f"Data will be stored in: {os.path.abspath(DATA_FILE)}")
    print("API will be available at: http://localhost:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
