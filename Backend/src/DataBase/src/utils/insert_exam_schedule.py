from Backend.src.DataBase.src.Database_connection import get_database
from joblib import Parallel, delayed
from datetime import datetime
import json

def _insert_single_class(schedule_id, day_date, cls):
    try:
        with get_database() as db:
            with db.cursor() as cursor:
                sql_block = """
                    INSERT INTO exam_block 
                    (schedule_id, class_id, name, year, exam_start_time, exam_end_time, duration, instructor, student_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                sql_room = "INSERT INTO exam_classrooms (exam_id, classroom_id) VALUES (%s, %s)"
                sql_student = "INSERT INTO exam_students (exam_id, student_num) VALUES (%s, %s)"
                sql_seating = """
                    INSERT INTO exam_seating_plan 
                    (exam_id, classroom_id, student_num, `row_number`, `column_number`)
                    VALUES (%s, %s, %s, %s, %s)
                """


                def to_time(val):
                    if isinstance(val, str):
                        return val  
                    try:
                        h = int(val)
                        m = int(round((val - h) * 60))
                        return f"{h:02d}:{m:02d}:00"
                    except Exception:
                        return "00:00:00"

                start_t = to_time(cls.get("start_time", 0))
                end_t = to_time(cls.get("end_time", 0))

                cursor.execute(sql_block, (
                    schedule_id,
                    cls.get("id"),
                    cls.get("name"),
                    cls.get("year"),
                    start_t,
                    end_t,
                    cls.get("duration", 0),
                    cls.get("instructor", "N/A"),
                    cls.get("student_count", 0)
                ))
                exam_id = cursor.lastrowid

                for room in cls.get("classrooms", []):
                    classroom_id = room.get("classroom_id") or room.get("id")
                    if classroom_id:
                        cursor.execute(sql_room, (exam_id, classroom_id))

                for student in cls.get("students", []):
                    s_num = student.get("student_num")
                    if s_num:
                        cursor.execute(sql_student, (exam_id, s_num))

                for classroom_name, grid in cls.get("seating_plan", {}).items():
                    for key, student_obj in grid.items():
                        try:
                            if isinstance(key, str) and "," in key:
                                r, c = map(int, key.split(","))
                            elif isinstance(key, tuple):
                                r, c = key
                            else:
                                continue
                            if isinstance(student_obj, dict) and student_obj.get("student_num"):
                                cursor.execute(sql_seating, (
                                    exam_id,
                                    classroom_name,
                                    student_obj["student_num"],
                                    r,
                                    c
                                ))
                        except Exception as se:
                            print(f"[WARN] seating insert skipped: {se}")

        return {"status": "ok", "class": cls.get('name'), "date": day_date}

    except Exception as e:
        return {"status": "error", "error": str(e), "class": cls.get("name")}


def insert_exam_schedule(exam_schedule, n_jobs: int = 4):
    try:
        
        all_results = []

        for day in exam_schedule:
            day_date = day.get("date")
            exam_type = day.get("exam_type", "N/A")
            exams = day.get("exams", [])

            with get_database() as db:
                with db.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO exam_schedules (date, exam_type) VALUES (%s, %s)",
                        (day_date, exam_type)
                    )
                    db.commit()
                    cursor.execute("SELECT id FROM exam_schedules WHERE date = %s", (day_date,))
                    schedule_id_row = cursor.fetchone()
                    if not schedule_id_row:
                        raise ValueError(f"schedule_id alınamadı ({day_date})")
                    schedule_id = schedule_id_row[0]

            all_classes = []
            for exam in exams:
                for cls in exam.get("classes", []):
                    all_classes.append(cls)

            if not all_classes:
                print(f"⚠️ {day_date} tarihinde eklenebilecek ders yok.")
                continue

            results = Parallel(n_jobs=n_jobs)(
                delayed(_insert_single_class)(schedule_id, day_date, cls)
                for cls in all_classes
            )
            all_results.extend(results)

        errors = [r for r in all_results if r["status"] == "error"]
        if errors:
            print(f"❌ {len(errors)} hata oluştu:")
            for e in errors[:5]:
                print(" -", e)
            return {"status": "error", "message": errors}

        print(f"✅ {len(all_results)} sınıf başarıyla eklendi.")
        return {"status": "success", "message": f"{len(all_results)} class inserted."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
