"""Automated tests for the CodeCraftHub API."""

import json
import os
import tempfile
import unittest

import app as app_module


class CodeCraftHubAPITests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_data_file = app_module.DATA_FILE
        app_module.DATA_FILE = os.path.join(self.temp_dir.name, "courses.json")
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def tearDown(self):
        app_module.DATA_FILE = self.original_data_file
        self.temp_dir.cleanup()

    def payload(self, **overrides):
        data = {
            "name": "Python Basics",
            "description": "Learn Python fundamentals",
            "target_date": "2027-12-31",
            "status": "Not Started",
        }
        data.update(overrides)
        return data

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_create_and_list_course(self):
        response = self.client.post("/api/courses", json=self.payload())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["course"]["id"], 1)

        response = self.client.get("/api/courses")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["count"], 1)

    def test_get_one_course(self):
        self.client.post("/api/courses", json=self.payload())
        response = self.client.get("/api/courses/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["course"]["name"], "Python Basics")

    def test_update_course(self):
        self.client.post("/api/courses", json=self.payload())
        response = self.client.put("/api/courses/1", json={"status": "In Progress"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["course"]["status"], "In Progress")

    def test_delete_course(self):
        self.client.post("/api/courses", json=self.payload())
        response = self.client.delete("/api/courses/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/courses/1").status_code, 404)

    def test_missing_field(self):
        response = self.client.post("/api/courses", json={"name": "Incomplete"})
        self.assertEqual(response.status_code, 400)

    def test_invalid_status(self):
        response = self.client.post("/api/courses", json=self.payload(status="Started"))
        self.assertEqual(response.status_code, 400)

    def test_invalid_date(self):
        response = self.client.post("/api/courses", json=self.payload(target_date="31-12-2027"))
        self.assertEqual(response.status_code, 400)

    def test_course_not_found(self):
        self.assertEqual(self.client.get("/api/courses/999").status_code, 404)
        self.assertEqual(self.client.put("/api/courses/999", json={"status": "Completed"}).status_code, 404)
        self.assertEqual(self.client.delete("/api/courses/999").status_code, 404)

    def test_stats(self):
        self.client.post("/api/courses", json=self.payload())
        self.client.post("/api/courses", json=self.payload(name="Flask", status="In Progress"))
        response = self.client.get("/api/courses/stats")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["total_courses"], 2)
        self.assertEqual(response.json["by_status"]["In Progress"], 1)

    def test_json_file_persists_data(self):
        self.client.post("/api/courses", json=self.payload())
        with open(app_module.DATA_FILE, "r", encoding="utf-8") as file:
            courses = json.load(file)
        self.assertEqual(len(courses), 1)


if __name__ == "__main__":
    unittest.main()
