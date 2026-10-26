import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

# add project root to path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# override the database before importing the app
_temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEMP_DB_PATH = _temp_db.name
_temp_db.close()

import database  # noqa: E402
database.DATABASE_NAME = TEMP_DB_PATH

from main import app  # noqa: E402

client = TestClient(app)

# test data
VALID_STUDENT = {
    "name": "Rahul Sharma",
    "date_of_birth": "2000-05-15",
    "email": "rahul.sharma@example.com",
    "phone": "9876543210",
    "course": "Computer Science",
    "address": "123 Main Street, Mumbai",
    "enrollment_date": "2024-08-01",
}

VALID_STUDENT_2 = {
    "name": "Priya Patel",
    "date_of_birth": "1999-11-20",
    "email": "priya.patel@example.com",
    "phone": "9123456789",
    "course": "Data Science",
    "address": "456 Park Avenue, Delhi",
    "enrollment_date": "2024-09-01",
}


@pytest.fixture(autouse=True)
def _setup_db():
    """Reset the table before each test."""
    with database.get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS students")
    database.create_table()
    yield


class TestCreateStudent:
    def test_create_student_success(self):
        response = client.post("/students", json=VALID_STUDENT)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Rahul Sharma"
        assert data["student_id"] is not None

    def test_create_student_email_only(self):
        payload = {**VALID_STUDENT, "phone": None}
        response = client.post("/students", json=payload)
        assert response.status_code == 201

    def test_create_student_phone_only(self):
        payload = {**VALID_STUDENT, "email": None}
        response = client.post("/students", json=payload)
        assert response.status_code == 201

    def test_create_student_no_contact_method(self):
        payload = {**VALID_STUDENT, "email": None, "phone": None}
        response = client.post("/students", json=payload)
        assert response.status_code == 422

    def test_create_student_future_dob(self):
        payload = {**VALID_STUDENT, "date_of_birth": "2099-01-01"}
        response = client.post("/students", json=payload)
        assert response.status_code == 422

    def test_create_student_invalid_dob_format(self):
        payload = {**VALID_STUDENT, "date_of_birth": "15-05-2000"}
        response = client.post("/students", json=payload)
        assert response.status_code == 422

    def test_create_student_invalid_email(self):
        payload = {**VALID_STUDENT, "email": "not-an-email"}
        response = client.post("/students", json=payload)
        assert response.status_code == 422

    def test_create_student_missing_name(self):
        payload = {**VALID_STUDENT}
        del payload["name"]
        response = client.post("/students", json=payload)
        assert response.status_code == 422

    def test_create_student_empty_name(self):
        payload = {**VALID_STUDENT, "name": "   "}
        response = client.post("/students", json=payload)
        assert response.status_code == 422


class TestListStudents:
    def test_list_empty(self):
        response = client.get("/students")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_students(self):
        client.post("/students", json=VALID_STUDENT)
        client.post("/students", json=VALID_STUDENT_2)
        response = client.get("/students")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filter_by_name(self):
        client.post("/students", json=VALID_STUDENT)
        client.post("/students", json=VALID_STUDENT_2)
        response = client.get("/students", params={"name": "Rahul"})
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["name"] == "Rahul Sharma"

    def test_filter_by_course(self):
        client.post("/students", json=VALID_STUDENT)
        client.post("/students", json=VALID_STUDENT_2)
        response = client.get("/students", params={"course": "Data"})
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["course"] == "Data Science"


class TestGetStudent:
    def test_get_student_success(self):
        post_resp = client.post("/students", json=VALID_STUDENT)
        sid = post_resp.json()["student_id"]
        response = client.get(f"/students/{sid}")
        assert response.status_code == 200
        assert response.json()["name"] == "Rahul Sharma"

    def test_get_student_not_found(self):
        response = client.get("/students/9999")
        assert response.status_code == 404


class TestUpdateStudent:
    def test_update_partial(self):
        post_resp = client.post("/students", json=VALID_STUDENT)
        sid = post_resp.json()["student_id"]

        response = client.put(
            f"/students/{sid}", json={"name": "Rahul Kumar"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Rahul Kumar"
        # other fields should stay the same
        assert data["course"] == "Computer Science"
        assert data["email"] == "rahul.sharma@example.com"

    def test_update_not_found(self):
        response = client.put(
            "/students/9999", json={"name": "Nobody"}
        )
        assert response.status_code == 404

    def test_update_no_fields(self):
        post_resp = client.post("/students", json=VALID_STUDENT)
        sid = post_resp.json()["student_id"]
        response = client.put(f"/students/{sid}", json={})
        assert response.status_code == 422

    def test_update_removes_all_contacts(self):
        """Should reject if update would remove both email and phone."""
        payload = {**VALID_STUDENT, "phone": None}
        post_resp = client.post("/students", json=payload)
        sid = post_resp.json()["student_id"]

        response = client.put(
            f"/students/{sid}", json={"email": None}
        )
        assert response.status_code == 422

    def test_update_future_dob(self):
        post_resp = client.post("/students", json=VALID_STUDENT)
        sid = post_resp.json()["student_id"]
        response = client.put(
            f"/students/{sid}", json={"date_of_birth": "2099-01-01"}
        )
        assert response.status_code == 422


class TestDeleteStudent:
    def test_delete_student_success(self):
        post_resp = client.post("/students", json=VALID_STUDENT)
        sid = post_resp.json()["student_id"]

        response = client.delete(f"/students/{sid}")
        assert response.status_code == 200

        # confirm it's actually gone
        get_resp = client.get(f"/students/{sid}")
        assert get_resp.status_code == 404

    def test_delete_student_not_found(self):
        response = client.delete("/students/9999")
        assert response.status_code == 404


@pytest.fixture(scope="session", autouse=True)
def _cleanup_temp_db():
    yield
    try:
        os.unlink(TEMP_DB_PATH)
    except OSError:
        pass
