from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from database import create_table, get_connection
from schemas import StudentCreate, StudentResponse, StudentUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table()
    yield


app = FastAPI(
    title="EWB Student Database CRUD API",
    description="Student Database CRUD Application for the EWB Edu Tech Pvt. Ltd. internship project.",
    version="1.0.0",
    lifespan=lifespan,
)


def _row_to_dict(row) -> dict:
    return dict(row)


@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO students
                (name, date_of_birth, email, phone, course, address, enrollment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student.name,
                student.date_of_birth,
                student.email,
                student.phone,
                student.course,
                student.address,
                student.enrollment_date,
            ),
        )
        student_id = cursor.lastrowid

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    return _row_to_dict(row)


@app.get("/students", response_model=list[StudentResponse])
def list_students(
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    course: Optional[str] = Query(None, description="Filter by course (partial match)"),
):
    query = "SELECT * FROM students WHERE 1=1"
    params: list = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    if course:
        query += " AND course LIKE ?"
        params.append(f"%{course}%")

    query += " ORDER BY student_id"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [_row_to_dict(r) for r in rows]


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found.")

    return _row_to_dict(row)


@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, updates: StudentUpdate):
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    if existing is None:
        raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found.")

    update_data = updates.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=422, detail="No fields provided for update.")

    # check that at least one contact method remains after update
    merged_email = update_data.get("email", existing["email"])
    merged_phone = update_data.get("phone", existing["phone"])
    if not merged_email and not merged_phone:
        raise HTTPException(
            status_code=422,
            detail="At least one contact method (email or phone) is required.",
        )

    set_clause = ", ".join(f"{col} = ?" for col in update_data)
    values = list(update_data.values()) + [student_id]

    with get_connection() as conn:
        conn.execute(
            f"UPDATE students SET {set_clause} WHERE student_id = ?",
            values,
        )

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    return _row_to_dict(row)


@app.delete("/students/{student_id}", status_code=200)
def delete_student(student_id: int):
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

    if existing is None:
        raise HTTPException(status_code=404, detail=f"Student with id {student_id} not found.")

    with get_connection() as conn:
        conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))

    return {"detail": f"Student with id {student_id} deleted successfully."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
