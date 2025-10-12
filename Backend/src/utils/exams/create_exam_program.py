from Backend.src.utils.exams.ExanProgramClass import ExamProgram
from typing import List
from queue import PriorityQueue
import itertools

def create_exam_schedule(
    exam_program: ExamProgram,
    class_dict: dict,
    classrooms: list[dict]) -> dict:
    
    first_date = exam_program.get_first_date_of_exam()
    last_date = exam_program.get_last_date_of_exam()
    
    exam_schedule = []
    for date in range(first_date, last_date + 1):
        exam_schedule.append({ "date": date, "exams": [] })
        
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

    for year in classes_by_year:
        classes_by_year[year].sort(key=lambda x: x['student_count'], reverse=True)

    final_ordered_list = []

    years = sorted(classes_by_year.keys())
    processing_order = years + years[-2:0:-1]

    year_iterator = itertools.cycle(processing_order)

    while any(classes_by_year.values()):
        year_to_process = next(year_iterator)
        if classes_by_year[year_to_process]:
            class_to_add = classes_by_year[year_to_process].pop(0)
            final_ordered_list.append(class_to_add)

    
    classes_queue = PriorityQueue()
    priority_counter = 0

    for class_data in final_ordered_list:
        classes_queue.put((priority_counter, class_data))
        priority_counter += 1
            
    failed_classes = []

    print("Birincil Yerleştirme denemesi başlıyor...")
    while not classes_queue.empty():
        priority, class_data = classes_queue.get()
        print(f"Deneme - Öncelik {priority}: {class_data['name']}...")
        is_successful = insert_class_to_program(class_data, priority, exam_program, exam_schedule, all_classroom_combinations)
        
        if not is_successful:
            print(f"  -> BAŞARISIZ! '{class_data['name']}' dersi sonraya ertelendi.")
            failed_classes.append(class_data)
        else:
            print(f"  -> BAŞARILI! '{class_data['name']}' dersi yerleştirildi.")

    print("\n" + "="*50 + "\n")
    if failed_classes:
        print("İkincil Yerleştirme denemesi (ertelenen dersler)")
        for class_data in failed_classes:
            print(f"Tekrar Deneme - Ders: {class_data['name']}...")
            is_successful_again = insert_class_to_program(class_data, None, exam_program, exam_schedule, all_classroom_combinations)
            
            if not is_successful_again:
                print(f"  -> SONUÇ: BAŞARISIZ! '{class_data['name']}' dersi programa yerleştirilemedi.")
            else:
                print(f"  -> SONUÇ: BAŞARILI! '{class_data['name']}' dersi yerleştirildi.")
    else:
        print("Tüm dersler ilk denemede başarıyla yerleştirildi!")

def _find_all_combinations(classrooms: List[dict]) -> List[List[dict]]:
    n = len(classrooms)
    all_combinations = []
    
    for r in range(1, n + 1):
        comb_list = itertools.combinations(classrooms, r) 

        print(f"{r} öğeli kombinasyonlar: {len(comb_list)} adet")
        print(list(comb_list))
        
        all_combinations.extend(comb_list)
        
    return all_combinations
        
        
def insert_class_to_program(class_data: dict, priority: int, exam_program: ExamProgram, exam_schedule: List, all_classroom_combs: List[dict]) -> bool:
    class_id = class_data['id']
    class_name = class_data['name']
    year = class_data['year']
    student_count = class_data['student_count']
    students = class_data.get('students', [])
    
    has_exam_conflict = exam_program.get_exam_conflict()
    
    start_time = exam_program.get_start_time()
    end_time = exam_program.get_end_time()
    
    
    exam_time = exam_program.get_ders_suresi(class_name)
    print(f"Sınıf {class_name} için sınav süresi: {exam_time} dakika")

    waiting_after_exam = exam_program.get_bekleme_suresi()
    print(f"Sınav sonrası bekleme süresi: {waiting_after_exam} dakika")
    
    len_of_schedule = len(exam_schedule)
    if len_of_schedule < priority + 1:
        print(f"Sınıf {class_name} için daha fazla farkli tarih yok, ayni tarihleri kullanacagiz.")
        list_index = priority % len_of_schedule
    else:
        list_index = priority
        
    exams = exam_schedule[list_index]["exams"]
    
    if exams.empty():
        print(f"Sınıf {class_name} için yeni sınav bloğu oluşturuluyor...")
        new_exam_block = {
            "start_time": start_time,
            "end_time": start_time + exam_time,
            "classes": [{
                "id": class_id,
                "name": class_name,
                "year": year,
                "student_count": student_count,
                "students": students,
                "duration": exam_time,
                "classrooms": []
            }]
        }
        
        classroom = find_suitable_classroom(all_classroom_combs, student_count)
        if classroom is None:
            print(f"Sınıf {class_name} için uygun sınıf bulunamadı, sınav eklenemedi.")
            return False
        else:
            new_exam_block["classes"][0]["classrooms"] = classroom
            print(f"Sınıf {class_name} için sınıflar atandı: {[room['name'] for room in classroom]}")
        
        exams.append(new_exam_block)
        print(f"Sınıf {class_name} için yeni sınav bloğu oluşturuldu.")
        return True
    else:
        for exam in exams:
            if exam["end_time"] + exam_time <= end_time:
                exam["classes"].append({
                    "id": class_id,
                    "name": class_name,
                    "year": year,
                    "student_count": student_count,
                    "students": students,
                    "duration": exam_time,
                    "classrooms": []
                })
                
                exam["end_time"] += exam_time + waiting_after_exam
                
                classroom = find_suitable_classroom(all_classroom_combs, student_count)
                if classroom is None:
                    print(f"Sınıf {class_name} için uygun sınıf bulunamadı, sınav eklenemedi.")
                    return False
                else:
                    exam["classes"][-1]["classrooms"] = classroom
                    print(f"Sınıf {class_name} için sınıflar atandı: {[room['name'] for room in classroom]}")
                    return True
            else:
                print(f"Sınıf {class_name} için mevcut sınav bloğuna eklenemedi, başka bloklar aranıyor...")
                
        else:
            if has_exam_conflict:
                print("Sinif cakismasi serbest, ona gore tekrar kontrol edilcek...")

                not_suitable_classrooms = []
                
                for exam in exams:
                    for existing_class in exam["classes"]:
                        is_student_conflict = _students_conflict(existing_class, class_data)
                        if is_student_conflict:
                            print(f"Sınıf {class_name} ile {existing_class['name']} arasında öğrenci çakışması var, bu bloğa eklenemez.")
                            continue
                        else:
                            print(f"Sınıf {class_name} ile {existing_class['name']} arasında öğrenci çakışması yok, bu bloğa eklenebilir.")
                            not_suitable_classrooms.append(existing_class.get('classrooms', []))
                            if exam["end_time"] + exam_time <= end_time:
                                exam["classes"].append({
                                    "id": class_id,
                                    "name": class_name,
                                    "year": year,
                                    "student_count": student_count,
                                    "students": students,
                                    "duration": exam_time,
                                    "classrooms": []
                                })
                                
                                exam["end_time"] += exam_time + waiting_after_exam
                                
                                classroom = find_suitable_classroom(all_classroom_combs, student_count, not_suitable_classrooms=not_suitable_classrooms)
                                if classroom is None:
                                    print(f"Sınıf {class_name} için uygun sınıf bulunamadı, sınav eklenemedi.")
                                    return False
                                else:
                                    exam["classes"][-1]["classrooms"] = classroom
                                    print(f"Sınıf {class_name} için sınıflar atandı: {[room['name'] for room in classroom]}")
                                    return True
            else:
                print(f"Sınıf {class_name} için mevcut sınav bloklarına eklenemedi ve çakışma izni yok.")
    return False
                        
   
def find_suitable_classroom(all_classroom_combs, student_count: int, not_suitable_classrooms: List = []) -> List[dict] | None:
    suitable_combinations = PriorityQueue()
    
    for combination in all_classroom_combs:
        total_capacity = sum(room['capacity'] for room in combination)
        priority =(len(combination), total_capacity - student_count)
        if total_capacity >= student_count and combination not in not_suitable_classrooms:
            suitable_combinations.put((priority, combination))
            
    
    if suitable_combinations.empty():
        print(f"Öğrenci sayısı {student_count} için uygun sınıf kombinasyonu bulunamadı.")
        return None    
    else:
        best_combination = suitable_combinations.get()[1]
        print(f"Öğrenci sayısı {student_count} için uygun sınıf kombinasyonu bulundu: {[room['name'] for room in best_combination]}")
        return best_combination
    
def _students_conflict(class1: dict, class2: dict) -> bool:
    students1 = set(class1.get('students', []))
    students2 = set(class2.get('students', []))
    
    return not students1.isdisjoint(students2)