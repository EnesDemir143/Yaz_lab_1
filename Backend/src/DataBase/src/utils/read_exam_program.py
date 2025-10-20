from Backend.src.DataBase.src.Database_connection import get_database
from pymysql.cursors import DictCursor

def read_exam_schedule_by_department(department_name: str | None = None):
    try:
        with get_database() as db:
            with db.cursor(DictCursor) as cursor:
                cursor.execute("SELECT id, date, exam_type FROM exam_schedules")
                schedules = cursor.fetchall()
                
                if not schedules:
                    return {"status": "empty", "message": "Hiç schedule bulunamadı."}

                all_departments = {}

                for sched in schedules:
                    sid = sched["id"]
                    day_date = sched["date"]
                    exam_type = sched.get("exam_type", "N/A")

                    # 2️⃣ exam_block (ders bilgileri)
                    cursor.execute("""
                        SELECT * FROM exam_block 
                        WHERE schedule_id = %s
                    """, (sid,))
                    blocks = cursor.fetchall()

                    for block in blocks:
                        exam_id = block["id"]

                        # 3️⃣ Bu dersin bağlı olduğu departmanı bul
                        # (Bunu exam_classrooms -> classrooms tablosundan çekelim)
                        cursor.execute("""
                            SELECT c.department_name 
                            FROM exam_classrooms ec
                            JOIN classrooms c ON ec.classroom_id = c.classroom_id
                            WHERE ec.exam_id = %s
                            LIMIT 1
                        """, (exam_id,))
                        dep_row = cursor.fetchone()
                        dep_name = dep_row["department_name"] if dep_row else "Bilinmiyor"

                        # Filtre varsa ve eşleşmiyorsa atla
                        if department_name and dep_name != department_name:
                            continue

                        # 4️⃣ Sınıfa ait diğer ilişkiler
                        cursor.execute("""
                            SELECT classroom_id FROM exam_classrooms WHERE exam_id = %s
                        """, (exam_id,))
                        classrooms = [{"classroom_id": r["classroom_id"]} for r in cursor.fetchall()]

                        cursor.execute("""
                            SELECT student_num FROM exam_students WHERE exam_id = %s
                        """, (exam_id,))
                        students = [{"student_num": r["student_num"]} for r in cursor.fetchall()]

                        cursor.execute("""
                            SELECT classroom_id, student_num, `row_number`, `column_number`
                            FROM exam_seating_plan WHERE exam_id = %s
                        """, (exam_id,))
                        seating_plan_rows = cursor.fetchall()
                        seating_plan = {}
                        for r in seating_plan_rows:
                            cname = r["classroom_id"]
                            key = f"{r['row_number']},{r['column_number']}"
                            if cname not in seating_plan:
                                seating_plan[cname] = {}
                            seating_plan[cname][key] = {"student_num": r["student_num"]}

                        # 5️⃣ class objesi
                        cls_obj = {
                            "id": block["class_id"],
                            "name": block["name"],
                            "year": block["year"],
                            "start_time": str(block["exam_start_time"]),
                            "end_time": str(block["exam_end_time"]),
                            "duration": block.get("duration", 0),
                            "instructor": block.get("instructor", "N/A"),
                            "student_count": block.get("student_count", 0),
                            "classrooms": classrooms,
                            "students": students,
                            "seating_plan": seating_plan
                        }

                        # 6️⃣ Departman altında grupla
                        dep_data = all_departments.setdefault(dep_name, {})
                        day_data = dep_data.setdefault(day_date, {
                            "exam_type": exam_type,
                            "exams": []
                        })
                        day_data["exams"].append({"classes": [cls_obj]})

        if department_name:
            if department_name not in all_departments:
                return {"status": "empty", "message": f"{department_name} için kayıt bulunamadı."}
            return {"status": "success", "department": department_name, "exam_schedule": all_departments[department_name]}

        return {"status": "success", "departments": all_departments, "message": "Tüm departmanlar için exam schedule başarıyla okundu."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "exam_schedule": {}, "message": str(e)}
