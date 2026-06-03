import json
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(title="Course Records API")


class Course(BaseModel):
    course_name: str = Field(min_length=1)
    year: str = Field(min_length=1)
    semester: str = Field(min_length=1)
    grade: str = Field(min_length=1)


def get_courses_file() -> Path:
    configured_path = os.getenv("COURSES_FILE")
    if configured_path:
        return Path(configured_path)
    return Path(__file__).with_name("courses.json")


def read_courses() -> list[dict[str, Any]]:
    courses_file = get_courses_file()

    if not courses_file.exists():
        courses_file.write_text("[]\n", encoding="utf-8")

    try:
        data = json.loads(courses_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail="courses.json 파일을 읽을 수 없습니다.",
        ) from exc

    if not isinstance(data, list):
        raise HTTPException(
            status_code=500,
            detail="courses.json 파일은 JSON list 형태여야 합니다.",
        )

    return data


def write_courses(courses: list[dict[str, Any]]) -> None:
    courses_file = get_courses_file()
    courses_file.write_text(
        json.dumps(courses, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


@app.get("/courses", response_model=list[Course])
def get_courses() -> list[dict[str, Any]]:
    return read_courses()


@app.post("/courses", response_model=Course, status_code=201)
def create_course(course: Course) -> Course:
    courses = read_courses()
    courses.append(course.model_dump())
    write_courses(courses)
    return course
