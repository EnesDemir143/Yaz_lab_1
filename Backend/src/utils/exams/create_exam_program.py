from Backend.src.utils.exams.ExanProgramClass import ExamProgram
from typing import List
from queue import PriorityQueue
import itertools
from datetime import timedelta, datetime
import pandas as pd
import random


def create_exam_schedule(
    exam_program: ExamProgram,
    class_dict: dict,
    classrooms: list[dict]) -> dict:
    
    statistics = {}
    
    first_date_str = exam_program.get_first_date_of_exam()
    last_date_str = exam_program.get_last_date_of_exam()
    
    first_date = datetime.fromisoformat(first_date_str)
    last_date = datetime.fromisoformat(last_date_str)

    
    exam_schedule = []
    current_date = first_date
    while current_date <= last_date:
        exam_schedule.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "exams": []
        })
        current_date += timedelta(days=1)
        
    all_classroom_combinations = _find_all_combinations(classrooms)
    print(f"Tüm sınıf kombinasyonları bulundu: {len(all_classroom_combinations)} adet")
    
    classes_by_year = {1: [], 2: [], 3: [], 4: []}

    for class_id, info in class_dict.items():
        year = info.get('year', 0)
        if year in classes_by_year:
            class_data = {
                'id': class_id,
                'name': info.get('class_name', ''),
                'year': year,
                "students": info.get('students', []),
                'student_count': len(info.get('students', []))
            }
            classes_by_year[year].append(class_data)

    all_classes = []
    for year_classes in classes_by_year.values():
        all_classes.extend(year_classes)

    random.shuffle(all_classes)

    final_ordered_list = all_classes
            
    failed_classes = []

    print("Birincil Yerleştirme denemesi başlıyor...")
    for idx, class_data in enumerate(final_ordered_list):
        print(f"Deneme - Öncelik {idx}: {class_data['name']}...")
        is_successful = insert_class_to_program(class_data, idx, exam_program, exam_schedule, all_classroom_combinations)
        
        if not is_successful:
            print(f"  -> BAŞARISIZ! '{class_data['name']}' dersi sonraya ertelendi.")
            failed_classes.append(class_data)
        else:
            print(f"  -> BAŞARILI! '{class_data['name']}' dersi yerleştirildi.")

    print("\n" + "="*50 + "\n")
    count = 0
    if failed_classes:
        print("İkincil Yerleştirme denemesi (ertelenen dersler)")
        for class_data in failed_classes:
            print(f"Tekrar Deneme - Ders: {class_data['name']}...")
            is_successful_again = insert_class_to_program(class_data, count, exam_program, exam_schedule, all_classroom_combinations)
            
            if not is_successful_again:
                print(f"  -> SONUÇ: BAŞARISIZ! '{class_data['name']}' dersi programa yerleştirilemedi.")
            else:
                print(f"  -> SONUÇ: BAŞARILI! '{class_data['name']}' dersi yerleştirildi.")
            count += 1
    else:
        print("Tüm dersler ilk denemede başarıyla yerleştirildi!")
        
    statistics['total_classes'] = len(class_dict)
    statistics['failed_classes'] = len(failed_classes)
    statistics['successful_classes'] = statistics['total_classes'] - statistics['failed_classes']

    exam_schedule = create_seating_plan(exam_schedule)
        
    return {
        "exam_schedule": exam_schedule,
        "failed_classes": failed_classes,
        "statistics": statistics
    }

def _find_all_combinations(classrooms: List[dict]) -> List[List[dict]]:
    n = len(classrooms)
    all_combinations = []
    
    for r in range(1, n + 1):
        comb_list = list(itertools.combinations(classrooms, r))
        print(f"{r} öğeli kombinasyonlar: {len(comb_list)} adet")
        print(comb_list)
        
        all_combinations.extend(comb_list)
        
    return all_combinations
        
def insert_class_to_program(
    class_data: dict,
    priority: int,
    exam_program: ExamProgram,
    exam_schedule: List[dict],
    all_classroom_combs: List[dict]
) -> bool:
    class_id = class_data['id']
    class_name = class_data['name']
    year = class_data['year']
    student_count = class_data['student_count']
    students = class_data.get('students', [])

    has_exam_conflict = exam_program.get_exam_conflict()
    start_time = exam_program.get_start_time()
    end_time = exam_program.get_end_time()

    exam_time = exam_program.get_ders_suresi(class_name) / 60
    waiting_after_exam = exam_program.get_bekleme_suresi() / 60

    print(f"🧩 '{class_name}' için sınav süresi: {exam_time} saat, bekleme: {waiting_after_exam} saat")

    for day in exam_schedule:
        exams = day["exams"]

        if not exams:
            new_exam_block = {
                "end_time": start_time + exam_time,
                "classes": [{
                    "id": class_id,
                    "name": class_name,
                    "year": year,
                    "student_count": student_count,
                    "students": students,
                    "duration": exam_time,
                    "classrooms": [],
                    "start_time": start_time,
                    "end_time": start_time + exam_time
                }]
            }

            classroom = find_suitable_classroom(all_classroom_combs, student_count)
            if classroom is None:
                print(f"❌ {class_name}: uygun sınıf bulunamadı (boş güne ekleme).")
                continue

            new_exam_block["classes"][0]["classrooms"] = classroom
            exams.append(new_exam_block)
            print(f"✅ '{class_name}' yeni güne yerleştirildi ({day['date']})")
            return True

        for exam in exams:
            if exam["end_time"] + exam_time <= end_time:
                classroom = find_suitable_classroom(all_classroom_combs, student_count)
                if classroom is None:
                    continue

                exam["classes"].append({
                    "id": class_id,
                    "name": class_name,
                    "year": year,
                    "student_count": student_count,
                    "students": students,
                    "duration": exam_time,
                    "classrooms": classroom,
                    "start_time": exam["end_time"],
                    "end_time": exam["end_time"] + exam_time
                })

                exam["end_time"] += exam_time + waiting_after_exam
                print(f"✅ '{class_name}' sırayla yerleştirildi ({day['date']})")
                return True

    if has_exam_conflict:
        print(f"⚙️ Çakışma modu aktif — '{class_name}' için tüm günlerde paralel arama başlıyor.")
        for day in exam_schedule:
            for exam in day["exams"]:
                has_conflict_with_any = False
                for existing_class in exam["classes"]:
                    if _students_conflict(existing_class, class_data):
                        print(f"   ❌ '{class_name}' ile '{existing_class['name']}' arasında öğrenci çakışması var.")
                        has_conflict_with_any = True
                        continue

                if not has_conflict_with_any:
                    not_suitable_classrooms = [
                        r['classroom_name']
                        for c in exam["classes"]
                        for r in c.get('classrooms', [])
                    ]

                    classroom = find_suitable_classroom(
                        all_classroom_combs,
                        student_count,
                        not_suitable_classrooms=not_suitable_classrooms
                    )
                    if classroom is None:
                        print(f"❌ {class_name}: uygun sınıf bulunamadı (paralel ekleme).")
                        continue

                    exam["classes"].append({
                        "id": class_id,
                        "name": class_name,
                        "year": year,
                        "student_count": student_count,
                        "students": students,
                        "duration": exam_time,
                        "classrooms": classroom,
                        "start_time": exam["classes"][0]["start_time"],
                        "end_time": exam["classes"][0]["start_time"] + exam_time
                    })
                    print(f"⚡ '{class_name}' paralel olarak '{exam['classes'][0]['name']}' ile aynı saatte ({day['date']}) yerleştirildi.")
                    return True

    print(f"⚠️ '{class_name}' için hiçbir gün/slotta uygun yer bulunamadı.")
    return False
                        
   
def find_suitable_classroom(all_classroom_combs, student_count: int, not_suitable_classrooms: List = []) -> List[dict] | None:
    suitable_combinations = PriorityQueue()
    counter = 0
    
    
    for combination in all_classroom_combs:
        comb_room_names = [r['classroom_name'] for r in combination]
        total_capacity = sum(room['capacity'] for room in combination)
        priority =(len(combination), total_capacity - student_count)
        if total_capacity >= student_count and not any(n in not_suitable_classrooms for n in comb_room_names):
            suitable_combinations.put((priority, counter, combination))
            counter += 1
            
    
    if suitable_combinations.empty():
        print(f"Öğrenci sayısı {student_count} için uygun sınıf kombinasyonu bulunamadı.")
        return None    
    else:
        best_combination = suitable_combinations.get()[2]
        print(f"Öğrenci sayısı {student_count} için uygun sınıf kombinasyonu bulundu: {[room['classroom_name'] for room in best_combination]}")
        return best_combination
    
def _students_conflict(class1: dict, class2: dict) -> bool:
    students1 = {s.get('student_num') for s in class1.get('students', []) if s.get('student_num')}
    students2 = {s.get('student_num') for s in class2.get('students', []) if s.get('student_num')}

    return not students1.isdisjoint(students2)

def download_exam_schedule(exam_schedule: List[dict], filename: str):
    rows = []

    for day in exam_schedule:
        date = day.get("date", "-")
        exams = day.get("exams", [])
        for exam in exams:
            classes = exam.get("classes", [])
            for cls in classes:
                start_time = cls.get("start_time", "-")
                end_time = cls.get("end_time", "-")
                class_name = cls.get("name", "-")
                year = cls.get("year", "-")
                student_count = cls.get("student_count", 0)
                classrooms = [r.get("classroom_name", "-") for r in cls.get("classrooms", [])]

                rows.append({
                    "Tarih": date,
                    "Başlangıç Saati": float_to_time_str(start_time),
                    "Bitiş Saati": float_to_time_str(end_time),
                    "Ders Adı": class_name,
                    "Sınıf Yılı": year,
                    "Öğrenci Sayısı": student_count,
                    "Sınıflar": ", ".join(classrooms)
                })

    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False)
    print(f"Sınav programı '{filename}' dosyasına kaydedildi.")


def float_to_time_str(hour_float: float) -> str:
    hour = int(hour_float)
    minute = int(round((hour_float - hour) * 60))
    return f"{hour:02d}:{minute:02d}"


def create_seating_plan(exam_schedule: List[dict]) -> dict:

    for day in exam_schedule:
        date = day.get("date", "-")
        exams = day.get("exams", [])

        for exam in exams:
            classes = exam.get("classes", [])
            for cls in classes:
                classrooms = [r.get("classroom_name", "-") for r in cls.get("classrooms", [])]
                print(f'{cls.get("name", "-")} has a {len(cls.get("students", "-"))}, in rooms: {", ".join(classrooms)}')

                def seperate_students(students, classrooms):
                    for room in classrooms:
                        yield students[0:room['capacity']]
                        students = students[room['capacity']:]

                students = cls.get("students", []).copy()
                random.shuffle(students)
                cls['seating_plan'] = {}

                for room, students in zip(classrooms, seperate_students(students, classrooms)):
                    cls['seating_plan'][room['classroom_name']] = students
                    print(f'{room["classroom_name"]} has {len(students)} students')

    return exam_schedule