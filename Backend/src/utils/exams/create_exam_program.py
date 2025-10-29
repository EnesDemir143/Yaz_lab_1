import math
from Backend.src.utils.exams.ExanProgramClass import ExamProgram
from typing import List
from queue import Empty, PriorityQueue
import itertools
from datetime import timedelta, datetime
import pandas as pd
import random
from collections import defaultdict, deque

def create_exam_schedule(exam_program, class_dict: dict, classrooms: list[dict], max_per_day: int = 2) -> dict:
    statistics = {}

    first_date = datetime.fromisoformat(exam_program.get_first_date_of_exam())
    last_date = datetime.fromisoformat(exam_program.get_last_date_of_exam())
    exam_type = exam_program.get_exam_type()

    used_classrooms_per_day = {}    

    # Günleri oluştur
    exam_schedule = []
    current_date = first_date
    while current_date <= last_date:
        date_str = current_date.strftime("%Y-%m-%d")
        exam_schedule.append({
            "date": date_str,
            "exam_type": exam_type,
            "exams": []
        })        
        used_classrooms_per_day[date_str] = {classroom['classroom_name']: 0 for classroom in classrooms}
        current_date += timedelta(days=1)

    
    total_days = len(exam_schedule)

    # Sınıfları yıllara göre grupla
    classes_by_year = {1: [], 2: [], 3: [], 4: []}
    for class_id, info in class_dict.items():
        year = info.get('year', 0)
        if year in classes_by_year:
            classes_by_year[year].append({
                'id': class_id,
                'name': info.get('class_name', ''),
                'year': year,
                'instructor': info.get('instructor', 'N/A'),
                "students": info.get('students', []),
                'student_count': len(info.get('students', []))
            })

    # Karıştır ve deque'e çevir
    for y in classes_by_year:
        random.shuffle(classes_by_year[y])
        classes_by_year[y] = deque(classes_by_year[y])

    all_classroom_combinations = _find_all_combinations(classrooms)
    print(f"Tüm sınıf kombinasyonları bulundu: {len(all_classroom_combinations)} adet")

    failed_classes = []
    success_count = 0

    # Günlük yıl sınav sayacı
    daily_year_counts = [defaultdict(int) for _ in range(total_days)]

    print("Dinamik Yerleştirme başlıyor...")
    round_counter = 0
    start_day = 0  # round-robin başlangıç günü

    while any(classes_by_year[y] for y in classes_by_year):
        year_order = [1, 2, 3, 4]
        random.shuffle(year_order)

        for y in year_order:
            if not classes_by_year[y]:
                continue

            found_day = None
            found_date = None
            flexible_mode = False
            
            # round-robin gün araması (normal mod)
            for offset in range(total_days):
                test_day = (start_day + offset) % total_days
                test_date = exam_schedule[test_day]['date'] 
                if daily_year_counts[test_day][y] < max_per_day:
                    found_day = test_day
                    found_date = test_date
                    break

            # 🔹 Eğer normal modda yer bulunamadıysa, esnek mod devreye girer
            if found_day is None:
                print(f"⚠️   normal yerleştirme yapılamadı. Esnek mod aktif.")
                flexible_mode = True
                
                # En az yoğun günü bul (max_per_day'i aşsa bile)
                min_count = min(daily_year_counts[d][y] for d in range(total_days))
                for offset in range(total_days):
                    test_day = (start_day + offset) % total_days
                    test_date = exam_schedule[test_day]['date']
                    if daily_year_counts[test_day][y] == min_count:
                        found_day = test_day
                        found_date = test_date
                        print(f"   🔹 Esnek modda Gün {found_day+1} seçildi (mevcut: {min_count} sınav)")
                        break

            if found_day is None:
                # Bu duruma düşmemeli ama yine de kontrol
                failed_classes.extend(classes_by_year[y])
                classes_by_year[y].clear()
                continue

            class_data = classes_by_year[y].popleft()
            current_day = exam_schedule[found_day]

            if flexible_mode:
                print(f"Gün {found_day + 1} | {class_data['name']} ({y}. sınıf) yerleştiriliyor... [ESNEK MOD]")
            else:
                print(f"Gün {found_day + 1} | {class_data['name']} ({y}. sınıf) yerleştiriliyor...")
            
            # 🔹 Günün used_classrooms dict'ini gönder
            is_successful = insert_class_to_program(
                class_data,
                round_counter,
                exam_program,
                current_day,  # 🔹 Sadece o günü gönder
                all_classroom_combinations,
                used_classrooms=used_classrooms_per_day[found_date]  # 🔹 O günün kullanım bilgisi
            )

            if is_successful:
                success_count += 1
                daily_year_counts[found_day][y] += 1
                mode_text = "ESNEK MOD" if flexible_mode else "NORMAL"
                limit_text = f"(limit: {max_per_day})" if daily_year_counts[found_day][y] > max_per_day else ""
                print(f"  -> BAŞARILI [{mode_text}] ({y}. sınıf - Gün {found_day+1} toplam {daily_year_counts[found_day][y]}) {limit_text}")
            else:
                failed_classes.append(class_data)
                print(f"  -> BAŞARISIZ: {class_data['name']}")

            # Bir sonraki sınıfın yerleştirme araması bir sonraki günden başlasın
            start_day = (found_day + 1) % total_days
            round_counter += 1

    # --- Oturma planı oluştur ---
    exam_schedule = create_seating_plan(exam_schedule)

    # --- İstatistikler ---
    statistics['total_classes'] = len(class_dict)
    statistics['failed_classes'] = len(failed_classes)
    statistics['successful_classes'] = success_count

    print("\nYerleştirme tamamlandı.")
    print(f"Başarılı: {success_count} | Başarısız: {len(failed_classes)}")

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
        all_combinations.extend(comb_list)

    return all_combinations
        
def insert_class_to_program(
    class_data: dict,
    priority: int,
    exam_program: ExamProgram,
    exam_day: dict,  # 🔹 Tek bir gün objesi alıyor artık
    all_classroom_combs: List[dict],
    used_classrooms: dict = {}
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
    print(f"⏰ Sınav günleri için zaman aralığı: {float_to_time_str(start_time)} - {float_to_time_str(end_time)}")

    exam_time = exam_program.get_ders_suresi(class_name) / 60
    waiting_after_exam = exam_program.get_bekleme_suresi() / 60

    print(f"🧩 '{class_name}' için sınav süresi: {exam_time} saat, bekleme: {waiting_after_exam} saat")

    exams = exam_day["exams"]

    # 🔹 Eğer gün boşsa yeni exam block oluştur
    if not exams:
        new_exam_block = {
            "end_time": start_time + exam_time + waiting_after_exam,
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

        classroom = find_suitable_classroom(all_classroom_combs, student_count, used_classrooms=used_classrooms)
        if classroom is None:
            print(f"❌ {class_name}: uygun sınıf bulunamadı (boş güne ekleme).")
            return False

        new_exam_block["classes"][0]["classrooms"] = classroom
        exams.append(new_exam_block)
        print(f"✅ '{class_name}' yeni güne yerleştirildi ({exam_day['date']})")
        return True

    # 🔹 Sırayla yerleştirmeyi dene
    for exam in exams:
        if exam["end_time"] + exam_time <= end_time:
            classroom = find_suitable_classroom(all_classroom_combs, student_count, used_classrooms=used_classrooms)
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
            print(f"✅ '{class_name}' sırayla yerleştirildi ({exam_day['date']})")
            return True

    # 🔹 Çakışma modunu dene
    if has_exam_conflict:
        print(f"⚙️ Çakışma modu aktif — '{class_name}' için paralel yerleştirme deneniyor.")
        for exam in exams:
            has_conflict_with_any = False
            for existing_class in exam["classes"]:
                if _students_conflict(existing_class, class_data):
                    print(f"   ❌ '{class_name}' ile '{existing_class['name']}' arasında öğrenci çakışması var.")
                    has_conflict_with_any = True
                    break

            if not has_conflict_with_any:
                not_suitable_classrooms = [
                    r['classroom_name']
                    for c in exam["classes"]
                    for r in c.get('classrooms', [])
                ]

                classroom = find_suitable_classroom(
                    all_classroom_combs,
                    student_count,
                    not_suitable_classrooms=not_suitable_classrooms,
                    used_classrooms=used_classrooms
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
                print(f"⚡ '{class_name}' paralel olarak '{exam['classes'][0]['name']}' ile aynı saatte ({exam_day['date']}) yerleştirildi.")
                return True

    print(f"⚠️ '{class_name}' için hiçbir slotta uygun yer bulunamadı.")
    return False

def find_suitable_classroom(
    all_classroom_combs,
    student_count: int,
    not_suitable_classrooms: List = [],
    used_classrooms: dict = {}
) -> List[dict] | None:
    suitable_combinations = PriorityQueue()
    counter = 0

    for combination in all_classroom_combs:
        comb_room_names = [r['classroom_name'] for r in combination]
        total_capacity = sum(r.get('capacity', 0) for r in combination)

        # Uygun değilse atla
        if total_capacity < student_count:
            continue
        if any(n in not_suitable_classrooms for n in comb_room_names):
            continue

        # 🔹 Günlük kullanım sayılarını hesapla
        total_usage = sum(used_classrooms.get(name, 0) for name in comb_room_names)
        
        # 🔹 Hiç kullanılmamış mı kontrol et
        is_unused = all(used_classrooms.get(name, 0) == 0 for name in comb_room_names)
        
        # 🔹 Öncelik: (hiç kullanılmamışsa 0, kullanılmışsa 1), toplam kullanım, kombinasyon boyutu, kapasite farkı
        priority = (
            0 if is_unused else 1,  # 🔹 Önce hiç kullanılmayanlar
            total_usage,             # 🔹 Sonra en az kullanılanlar
            len(combination),        # 🔹 Daha az sınıf içeren kombinasyonlar
            total_capacity - student_count  # 🔹 Kapasite fazlası az olanlar
        )

        suitable_combinations.put((priority, counter, combination))
        counter += 1

    if suitable_combinations.empty():
        print(f"⚠️ Öğrenci sayısı {student_count} için uygun sınıf kombinasyonu bulunamadı.")
        return None

    # 🔹 En uygun kombinasyonu seç
    best_combination = suitable_combinations.get()[2]
    clsroom_names = [r['classroom_name'] for r in best_combination]
    
    # 🔹 Kullanım durumunu kontrol et
    usage_counts = [used_classrooms.get(name, 0) for name in clsroom_names]
    if all(count == 0 for count in usage_counts):
        print(f"✅ {student_count} öğrenci için seçilen kombinasyon: {clsroom_names} (Hiç kullanılmamış sınıflar)")
    else:
        print(f"✅ {student_count} öğrenci için seçilen kombinasyon: {clsroom_names} (Kullanım: {usage_counts})")

    # 🔹 Günlük kullanım sayısını artır
    for r_name in clsroom_names:
        used_classrooms[r_name] = used_classrooms.get(r_name, 0) + 1

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

                    room_name = room_data.get("classroom_id", "Bilinmeyen")
                    print(f'Seating plan for {room_name}:')
                    #print_plan(student_grid, room_data)
                    cls['seating_plan'][room_name] = student_grid

                    print(f'{room_name} has {len(student_chunk)} students')

    return exam_schedule


def seperate_students(students, classrooms):
    for room in classrooms:
        total_capacity = room.get('capacity', 0)

        yield students[0:total_capacity]
        students = students[total_capacity:]

def adjust_seating_plan(room, students):
    student_grid = {}
    desk_structure = int(room['desk_structure'])     # Örn. 3 → Ö S Ö
    num_rows = int(room['desks_per_column'])
    num_blocks = int(room['desks_per_row'])

    if desk_structure <= 0:
        print("Sıra yapısı (desk_structure) pozitif bir sayı olmalıdır.")
        return {}

    # 🔹 Masa pattern'ını oluştur (örnek: 3 → Ö S Ö)
    if desk_structure == 1:
        pattern = ['Ö']
    elif desk_structure == 2:
        pattern = ['Ö', 'S']
    elif desk_structure == 3:
        pattern = ['Ö', 'S', 'Ö']
    else:
        pattern = ['Ö'] + ['S'] * (desk_structure - 2) + ['Ö']

    grid_col_index = 0

    for block in range(num_blocks):
        # Her blokta pattern'i uygula
        for symbol in pattern:
            for r in range(num_rows):
                if symbol == 'Ö':
                    student_grid[(r, grid_col_index)] = {
                        "type": "seat",
                        "student_num": None
                    }
                else:
                    student_grid[(r, grid_col_index)] = {
                        "type": "empty"
                    }
            grid_col_index += 1

        # Bloklar arası koridor
        if block < num_blocks - 1:
            for r in range(num_rows):
                student_grid[(r, grid_col_index)] = {"type": "corridor"}
            grid_col_index += 1

    # 🔹 Öğrencileri sırayla yerleştir
    student_iterator = iter(students)
    for c in range(grid_col_index):
        for r in range(num_rows):
            cell = student_grid.get((r, c))
            if cell["type"] != "seat":
                continue
            try:
                student = next(student_iterator)
                cell["student_num"] = student.get("student_num")
            except StopIteration:
                # Kalan koltukları boş yap
                if cell["type"] == "seat":
                    cell["type"] = "empty"
                    del cell["student_num"]
                return student_grid

    return student_grid
