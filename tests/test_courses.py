import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app


def test_get_courses_returns_all_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    courses_file = tmp_path / "courses.json"
    courses_file.write_text(
        json.dumps(
            [
                {
                    "course_name": "자료구조",
                    "year": "2025",
                    "semester": "2",
                    "grade": "A+",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("COURSES_FILE", str(courses_file))

    client = TestClient(app)
    response = client.get("/courses")

    assert response.status_code == 200
    assert response.json() == [
        {
            "course_name": "자료구조",
            "year": "2025",
            "semester": "2",
            "grade": "A+",
        }
    ]


def test_post_courses_appends_record_to_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    courses_file = tmp_path / "courses.json"
    courses_file.write_text("[]\n", encoding="utf-8")
    monkeypatch.setenv("COURSES_FILE", str(courses_file))

    client = TestClient(app)
    new_course = {
        "course_name": "인간로봇상호작용",
        "year": "2026",
        "semester": "2",
        "grade": "A+",
    }

    response = client.post("/courses", json=new_course)

    assert response.status_code == 201
    assert response.json() == new_course
    assert json.loads(courses_file.read_text(encoding="utf-8")) == [new_course]


def test_post_courses_rejects_invalid_body(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    courses_file = tmp_path / "courses.json"
    courses_file.write_text("[]\n", encoding="utf-8")
    monkeypatch.setenv("COURSES_FILE", str(courses_file))

    client = TestClient(app)
    response = client.post(
        "/courses",
        json={
            "course_name": "운영체제",
            "year": "2026",
        },
    )

    assert response.status_code == 422
    assert json.loads(courses_file.read_text(encoding="utf-8")) == []
