import math
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
    
    exam_type = exam_program.get_exam_type()
    print("exam_type: ", exam_type, "exam_type type:", type(exam_type))

    exam_schedule = []
    current_date = first_date
    while current_date <= last_date:
        exam_schedule.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "exam_type": exam_type,
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
                'instructor': info.get('instructor', 'N/A'),
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
    print("Oturma planları oluşturuldu.")
            
    return {
        "exam_schedule": exam_schedule,
        "failed_classes": failed_classes,
        "statistics": statistics
    }

def _find_all_combinations(classrooms: List[dict]) -> List[List[dict]]:
    n = len(classrooms)
    all_combinations = []

    MAX_COMBINATION_SIZE = 5

    for r in range(1, min(n, MAX_COMBINATION_SIZE) + 1):
        comb_list = [list(c) for c in itertools.combinations(classrooms, r)]
        print(f"{r} öğeli kombinasyonlar: {len(comb_list)} adet")
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
    instructor = class_data.get('instructor', 'N/A')

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
                    "instructor": instructor,
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
                    "instructor": instructor,
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
                        "instructor": instructor,
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
        total_capacity = 0

        for room in combination:
            desks_per_row = room['desks_per_row']
            desks_per_column = room['desks_per_column']
            desk_structure = int(room['desk_structure'])

            row_capacity = 0

            if desk_structure == 1:
                row_capacity = desks_per_row

            elif desk_structure == 2 or desk_structure == 4:
                row_capacity = math.ceil(desks_per_row / 2)

            elif desk_structure == 3:
                num_groups = desks_per_row // 3
                leftovers = desks_per_row % 3
                row_capacity = (num_groups * 2) + leftovers
            total_capacity += row_capacity * desks_per_column
            print(f"Sınıf '{room['classroom_name']}' kapasitesi: {row_capacity * desks_per_column}")
        priority = (len(combination), total_capacity - student_count)
        print(f"Kombinasyon: {[r['classroom_name'] for r in combination]}, Toplam Kapasite: {total_capacity}, Öğrenci Sayısı: {student_count}")
    
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
            for cls in exam.get("classes", []):
                instructor = cls.get("instructor", "N/A")

                rows.append({
                    "Tarih": date,
                    "Sınav Saati": float_to_time_str(cls.get("start_time", "-")),
                    "Ders Adı": cls.get("name", "-"),
                    "Öğretim Elemanı": instructor,
                    "Derslik": ", ".join([r.get("classroom_name", "-") for r in cls.get("classrooms", [])])
                })

    if not rows:
        print("Sınav programında yazdırılacak veri bulunmuyor.")
        return

    df = pd.DataFrame(rows)

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    sheet_name = 'Vize Sınav Programı'
    
    df.to_excel(writer, sheet_name=sheet_name, startrow=2, header=False, index=False)

    workbook  = writer.book
    worksheet = writer.sheets[sheet_name]

    title_format = workbook.add_format({
        'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
        'bg_color': '#F8CBAD', 'border': 1
    })
    header_format = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter',
        'bg_color': '#F8CBAD', 'border': 1, 'text_wrap': True
    })
    cell_format = workbook.add_format({'border': 1, 'valign': 'vcenter'})
    center_cell_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})

    num_cols = len(df.columns)
    worksheet.merge_range(0, 0, 0, num_cols - 1, 'BİLGİSAYAR MÜHENDİSLİĞİ BÖLÜMÜ VİZE SINAV PROGRAMI', title_format)
    worksheet.set_row(0, 30)  # Başlık satırının yüksekliği

    header_data = [{"header": col} for col in df.columns]
    worksheet.write_row(1, 0, df.columns, header_format)
    worksheet.set_column('A:A', 15)  # Tarih
    worksheet.set_column('B:B', 15)  # Sınav Saati
    worksheet.set_column('C:C', 45)  # Ders Adı
    worksheet.set_column('D:D', 35)  # Öğretim Elemanı
    worksheet.set_column('E:E', 35)  # Derslik


    date_groups = df.groupby((df['Tarih'] != df['Tarih'].shift()).cumsum())
    start_row = 2  
    for _, group in date_groups:
        if len(group) > 1:
            end_row = start_row + len(group) - 1
            worksheet.merge_range(start_row, 0, end_row, 0, group['Tarih'].iloc[0], center_cell_format)
        
        worksheet.conditional_format(start_row, 0, start_row + len(group) - 1, num_cols - 1,
                                     {'type': 'no_blanks', 'format': cell_format})
        worksheet.conditional_format(start_row, 0, start_row + len(group) - 1, 0,
                                     {'type': 'no_blanks', 'format': center_cell_format})
        worksheet.conditional_format(start_row, 0, start_row + len(group) - 1, 1,
                                     {'type': 'no_blanks', 'format': center_cell_format})

        start_row += len(group)

    writer.close()
    print(f"Sınav programı '{filename}' dosyasına başarıyla kaydedildi.")


def float_to_time_str(hour_float: float) -> str:
    hour = int(hour_float)
    minute = int(round((hour_float - hour) * 60))
    return f"{hour:02d}:{minute:02d}"

def print_plan(plan, room):
    if not plan: return
    max_col = max(key[1] for key in plan.keys())
    max_row = room['desks_per_column']
    
    print(f"\n--- OTURMA PLANI (Yapı: {room['desk_structure']}'li - DÜZELTİLMİŞ) ---")
    for r in range(max_row):
        row_str = ""
        for c in range(max_col + 1):
            cell = plan.get((r, c))
            if cell is None: row_str += "[  BOŞ  ] "
            elif cell == 'AISLE': row_str += " |KORİDOR| "
            else: row_str += f"[{str(cell):^7}] "
        print(row_str)

def create_seating_plan(exam_schedule: List[dict]) -> dict:
    for day in exam_schedule:
        exams = day.get("exams", [])
        for exam in exams:
            classes = exam.get("classes", [])
            for cls in classes:
                classrooms_full_data = cls.get("classrooms", [])
                classroom_names = [r.get("classroom_name", "-") for r in classrooms_full_data]

                print(f'{cls.get("name", "-")} sınavı için {len(cls.get("students", []))} öğrenci, şu sınıflarda: {", ".join(classroom_names)}')

                students = cls.get("students", []).copy()
                random.shuffle(students)
                cls['seating_plan'] = {}

                student_chunks = seperate_students(students, classrooms_full_data)

                for room_data, student_chunk in zip(classrooms_full_data, student_chunks):
                    student_grid = adjust_seating_plan(room_data, student_chunk)

                    room_name = room_data.get("classroom_name", "Bilinmeyen")
                    print(f'Seating plan for {room_name}:')
                    print_plan(student_grid, room_data)
                    cls['seating_plan'][room_name] = student_grid

                    print(f'{room_name} has {len(student_chunk)} students')

    return exam_schedule


def seperate_students(students, classrooms):
    for room in classrooms:
        desks_per_row = room['desks_per_row']
        desks_per_column = room['desks_per_column']
        desk_structure = int(room['desk_structure'])

        row_capacity = 0

        if desk_structure == 1:
            row_capacity = desks_per_row

        elif desk_structure == 2 or desk_structure == 4:
            row_capacity = math.ceil(desks_per_row / 2)

        elif desk_structure == 3:
            num_groups = desks_per_row // 3
            leftovers = desks_per_row % 3
            row_capacity = (num_groups * 2) + leftovers
        total_capacity = row_capacity * desks_per_column

        yield students[0:total_capacity]
        students = students[total_capacity:]


def adjust_seating_plan(room, students):
    student_grid = {}
    desk_structure = int(room['desk_structure'])
    num_rows = room['desks_per_column']
    num_desk_cols = room['desks_per_row']

    if desk_structure <= 0:
        print("Sıra yapısı (desk_structure) pozitif bir sayı olmalıdır.")
        return {}

    grid_col_index = 0
    desk_cols_placed = 0
    while desk_cols_placed < num_desk_cols:
        if desk_cols_placed > 0 and desk_cols_placed % desk_structure == 0:
            for row in range(num_rows):
                student_grid[(row, grid_col_index)] = 'AISLE'
            grid_col_index += 1

        for row in range(num_rows):
            student_grid[(row, grid_col_index)] = None
        desk_cols_placed += 1
        grid_col_index += 1

    student_iterator = iter(students)
    max_grid_col = grid_col_index
    desk_col_counter = 0

    for c in range(max_grid_col):
        if student_grid.get((0, c)) == 'AISLE':
            continue

        position_in_structure = desk_col_counter % desk_structure
        
        place_students_in_this_col = False

        if desk_structure == 1:
            place_students_in_this_col = True
        elif desk_structure == 2 or desk_structure == 4:
            if position_in_structure == 0:
                place_students_in_this_col = True
        elif desk_structure == 3:
            if position_in_structure != 1:
                place_students_in_this_col = True
        elif desk_structure == 4:
            if position_in_structure == 0 or position_in_structure == 3:
                place_students_in_this_col = True

        if place_students_in_this_col:
            for r in range(num_rows):
                try:
                    student_grid[(r, c)] = next(student_iterator)
                except StopIteration:
                    return student_grid
        
        desk_col_counter += 1

    return student_grid