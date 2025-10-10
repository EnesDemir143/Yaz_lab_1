from collections import defaultdict, Counter
import math
import datetime
import pandas as pd
from typing import List, Dict, Any, Tuple
from .ExanProgramClass import ExamProgram


def create_exam_schedule(exam_program: ExamProgram, 
                        class_dict: Dict[str, Dict],
                        rooms_data: List[Dict],
                        excel_output_path: str = "sinav_programi.xlsx") -> Dict[str, Any]:
    warnings = []
    
    # Tarih aralığından günleri oluştur
    days = _create_available_days(exam_program)
    if not days:
        warnings.append("Uygun gün bulunamadı")
        return {'schedule': [], 'warnings': warnings, 'excel': excel_output_path}
    
    # Günlük slot sayısı (sabah, öğle, akşam)
    slots_per_day = 3
    slot_list = []
    for d in days:
        for s in range(slots_per_day):
            slot_list.append((d, s))
    
    # class_dict'ten courses_data ve students_data oluştur
    courses_data, students_data = _convert_class_dict_to_courses_and_students(class_dict, exam_program)
    
    # Aktif dersleri hazırla (kalan dersler)
    active_courses = _prepare_courses(exam_program, courses_data, students_data)
    
    if not active_courses:
        warnings.append("Programa eklenecek ders bulunamadı")
        return {'schedule': [], 'warnings': warnings, 'excel': excel_output_path}
    
    # Öğrenci-ders eşleşmelerini oluştur
    student_course_map = _build_student_course_map(students_data)
    course_student_map = _build_course_student_map(students_data)
    
    # Oda uygunluğunu kontrol et
    suitable_rooms = _check_room_suitability(active_courses, rooms_data, warnings)
    
    # Sınavları yerleştir
    assignments = _schedule_exams(
        active_courses, course_student_map, suitable_rooms, 
        slot_list, exam_program.bekleme_suresi, warnings
    )
    
    # Özet rapor oluştur
    schedule_summary = _create_schedule_summary(assignments)
    
    # Excel çıktısı
    _write_excel_output(schedule_summary, assignments, warnings, exam_program, excel_output_path)
    
    return {
        'schedule': schedule_summary,
        'assignments': assignments, 
        'warnings': warnings,
        'excel': excel_output_path,
        'exam_program_info': exam_program.to_dict()
    }
    
def _convert_class_dict_to_courses_and_students(class_dict: Dict[str, Dict], 
                                                exam_program: ExamProgram) -> Tuple[List[Dict], List[Dict]]:
    courses_data = []
    students_data = []
    kalan_dersler = exam_program.get_kalan_dersler()
    
    # Her sınıf bir ders olarak kabul ediliyor
    for class_id, class_info in class_dict.items():
        class_name = class_info['class_name']
        
        # Sadece kalan dersleri al
        if class_name in kalan_dersler:
            courses_data.append({
                'id': class_id,
                'name': class_name,
                'class_group': class_name  # Sınıf grubu olarak ders adını kullan
            })
            
            # Öğrencileri ekle
            for student in class_info['students']:
                student_num = student['student_num']
                
                # Öğrenci zaten eklenmişse, sadece ders listesini güncelle
                existing_student = next(
                    (s for s in students_data if s['id'] == student_num), 
                    None
                )
                
                if existing_student:
                    existing_student['courses'].append(class_id)
                else:
                    students_data.append({
                        'id': student_num,
                        'name': f"{student['name']} {student['surname']}",
                        'courses': [class_id]
                    })
    
    return courses_data, students_data


def _create_available_days(exam_program: ExamProgram) -> List[str]:
    """ExamProgram'dan tarih aralığını alarak uygun günleri oluşturur."""
    
    def parse_date(date_str):
        if isinstance(date_str, str):
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                try:
                    return datetime.datetime.strptime(date_str, "%d.%m.%Y").date()
                except:
                    return None
        elif isinstance(date_str, datetime.date):
            return date_str
        return None
    
    start = parse_date(exam_program.tarih_baslangic)
    end = parse_date(exam_program.tarih_bitis)
    
    if not start or not end:
        # Varsayılan tarih aralığı
        return ["2025-01-06", "2025-01-07", "2025-01-08", "2025-01-09", "2025-01-10"]
    
    # Hariç günleri map et
    exclude_weekdays = set()
    for gun in (exam_program.haris_gunler or []):
        gun_lower = gun.lower()
        if "cumartesi" in gun_lower or "saturday" in gun_lower:
            exclude_weekdays.add(5)  # Saturday
        elif "pazar" in gun_lower or "sunday" in gun_lower:
            exclude_weekdays.add(6)  # Sunday
        elif "pazartesi" in gun_lower or "monday" in gun_lower:
            exclude_weekdays.add(0)
        elif "salı" in gun_lower or "tuesday" in gun_lower:
            exclude_weekdays.add(1)
        elif "çarşamba" in gun_lower or "wednesday" in gun_lower:
            exclude_weekdays.add(2)
        elif "perşembe" in gun_lower or "thursday" in gun_lower:
            exclude_weekdays.add(3)
        elif "cuma" in gun_lower or "friday" in gun_lower:
            exclude_weekdays.add(4)
    
    days = []
    current = start
    while current <= end:
        if current.weekday() not in exclude_weekdays:
            days.append(current.isoformat())
        current += datetime.timedelta(days=1)
    
    return days


def _prepare_courses(exam_program: ExamProgram, courses_data: List[Dict], students_data: List[Dict]) -> List[Dict]:
    """Kalan dersleri hazırlar ve ders sürelerini ekler."""
    
    kalan_dersler = exam_program.get_kalan_dersler()
    active_courses = []
    
    # Öğrenci sayılarını hesapla
    course_student_count = defaultdict(int)
    for student in students_data:
        for course_id in student.get('courses', []):
            course_student_count[course_id] += 1
    
    for course in courses_data:
        course_name = course.get('name')
        if course_name in kalan_dersler:
            course_copy = dict(course)
            # Ders süresini ExamProgram'dan al
            course_copy['duration_minutes'] = exam_program.get_ders_suresi(course_name)
            # Öğrenci sayısını ekle
            course_copy['expected_students'] = course_student_count.get(course['id'], 0)
            active_courses.append(course_copy)
    
    return active_courses


def _build_student_course_map(students_data: List[Dict]) -> Dict[str, set]:
    """Öğrenci ID -> Ders ID setleri haritası oluşturur."""
    return {s['id']: set(s.get('courses', [])) for s in students_data}


def _build_course_student_map(students_data: List[Dict]) -> Dict[str, set]:
    """Ders ID -> Öğrenci ID setleri haritası oluşturur."""
    course_students = defaultdict(set)
    for student in students_data:
        for course_id in student.get('courses', []):
            course_students[course_id].add(student['id'])
    return course_students


def _check_room_suitability(courses: List[Dict], rooms: List[Dict], warnings: List[str]) -> Dict[str, List]:
    """Her ders için uygun odaları bulur."""
    
    suitable_rooms = {}
    for course in courses:
        suitable = [r for r in rooms if r.get('capacity', 0) >= course['expected_students']]
        if not suitable:
            warnings.append(f"❌ {course['name']} dersi için uygun oda yok (öğrenci: {course['expected_students']})")
        else:
            # Küçük odaları öncelikle kullan (packing optimization)
            suitable.sort(key=lambda x: x.get('capacity', 0))
        suitable_rooms[course['id']] = suitable
    return suitable_rooms


def _schedule_exams(courses: List[Dict], course_student_map: Dict, suitable_rooms: Dict, 
                   slot_list: List[Tuple], bekleme_suresi: int, warnings: List[str]):
    """Sınavları otomatik olarak yerleştirir."""
    
    assignments = []
    student_assigned_slots = defaultdict(set)
    class_assignments = defaultdict(list)  # sınıf -> [(course_id, slot_idx)]
    
    # Dersleri önceliklendir: büyük sınıflar ve çakışması fazla olanlar önce
    class_counts = Counter([c.get('class_group') for c in courses])
    courses.sort(key=lambda c: (-c['expected_students'], -class_counts.get(c.get('class_group'), 0)))
    
    # Bekleme süresini slot sayısına çevir (varsayılan slot süresi 75 dk)
    bekleme_slots = max(1, math.ceil(bekleme_suresi / 75))
    
    for course in courses:
        course_id = course['id']
        rooms = suitable_rooms.get(course_id, [])
        if not rooms:
            continue
            
        placed = False
        class_group = course.get('class_group')
        
        # Aynı sınıfın az derse sahip olduğu günleri öncelikle dene
        day_preferences = _calculate_day_preferences(class_group, class_assignments, slot_list)
        
        for day_idx, day in day_preferences:
            day_slots = [i for i, (d, s) in enumerate(slot_list) if d == day]
            
            for slot_idx in day_slots:
                # Öğrenci çakışması kontrolü
                if _has_student_conflict(course_id, slot_idx, course_student_map, 
                                       student_assigned_slots, bekleme_slots):
                    continue
                
                # Oda müsaitlik kontrolü
                available_room = _find_available_room(rooms, slot_idx, assignments)
                if not available_room:
                    continue
                
                # Sınavı yerleştir
                assignments.append({
                    'course_id': course_id,
                    'course_name': course['name'],
                    'class_group': class_group,
                    'day': slot_list[slot_idx][0],
                    'slot_index': slot_idx,
                    'slot_in_day': slot_list[slot_idx][1],
                    'room_id': available_room['id'],
                    'room_name': available_room['name'],
                    'expected_students': course['expected_students'],
                    'duration_minutes': course['duration_minutes']
                })
                
                # Öğrenci atamalarını güncelle
                for student_id in course_student_map.get(course_id, set()):
                    student_assigned_slots[student_id].add(slot_idx)
                
                # Sınıf atamalarını güncelle
                class_assignments[class_group].append((course_id, slot_idx))
                
                placed = True
                break
            
            if placed:
                break
        
        if not placed:
            warnings.append(f"⚠️ {course['name']} dersi yerleştirilemedi")
    
    return assignments


def _calculate_day_preferences(class_group: str, class_assignments: Dict, 
                               slot_list: List[Tuple]) -> List[Tuple[int, str]]:
    """Sınıf için gün tercihlerini hesaplar (az kullanılan günler önce)."""
    
    day_counts = defaultdict(int)
    for course_id, slot_idx in class_assignments.get(class_group, []):
        day = slot_list[slot_idx][0]
        day_counts[day] += 1
    
    # Günleri az kullanılandan çok kullanılana sırala
    unique_days = list(set(slot_list[i][0] for i in range(len(slot_list))))
    day_preferences = [(day_counts[day], day) for day in unique_days]
    day_preferences.sort(key=lambda x: x[0])  # Az kullanılan günler önce
    
    return [(i, day) for i, (count, day) in enumerate(day_preferences)]


def _has_student_conflict(course_id: str, slot_idx: int, course_student_map: Dict, 
                         student_assigned_slots: Dict, bekleme_slots: int) -> bool:
    """Öğrenci çakışması olup olmadığını kontrol eder."""
    
    students = course_student_map.get(course_id, set())
    
    for student_id in students:
        assigned_slots = student_assigned_slots.get(student_id, set())
        
        for assigned_slot in assigned_slots:
            # Aynı slot veya bekleme süresi ihlali
            if abs(assigned_slot - slot_idx) <= bekleme_slots:
                return True
    
    return False


def _find_available_room(rooms: List[Dict], slot_idx: int, assignments: List[Dict]) -> Dict:
    """Verilen slot için müsait oda bulur."""
    
    occupied_rooms = {a['room_id'] for a in assignments if a['slot_index'] == slot_idx}
    
    for room in rooms:
        if room['id'] not in occupied_rooms:
            return room
    
    return None


def _create_schedule_summary(assignments: List[Dict]) -> List[Dict]:
    """Sınav programı özetini oluşturur."""
    
    summary = []
    course_assignments = defaultdict(list)
    
    for assignment in assignments:
        course_assignments[assignment['course_id']].append(assignment)
    
    for course_id, course_assigns in course_assignments.items():
        first = course_assigns[0]
        summary.append({
            'course_id': course_id,
            'course_name': first['course_name'],
            'class_group': first['class_group'],
            'day': first['day'],
            'slot_in_day': first['slot_in_day'],
            'room_name': first['room_name'],
            'expected_students': first['expected_students'],
            'duration_minutes': first['duration_minutes']
        })
    
    # Günlere ve slotlara göre sırala
    summary.sort(key=lambda x: (x['day'], x['slot_in_day']))
    
    return summary


def _write_excel_output(schedule_summary: List[Dict], assignments: List[Dict], 
                       warnings: List[str], exam_program: ExamProgram, output_path: str):
    """Excel formatında çıktı oluşturur."""
    
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Ana program
            df_schedule = pd.DataFrame(schedule_summary)
            if not df_schedule.empty:
                df_schedule.columns = ['Ders ID', 'Ders Adı', 'Sınıf', 'Tarih', 'Seans', 
                                      'Oda', 'Öğrenci Sayısı', 'Süre (dk)']
            df_schedule.to_excel(writer, sheet_name='Sınav Programı', index=False)
            
            # Oda bazlı görünüm
            room_view = []
            for assignment in assignments:
                slot_names = ['Sabah (09:00-10:15)', 'Öğle (11:00-12:15)', 'Akşam (14:00-15:15)']
                room_view.append({
                    'Oda': assignment['room_name'],
                    'Gün': assignment['day'],
                    'Seans': slot_names[assignment['slot_in_day']] if assignment['slot_in_day'] < 3 else f"Slot {assignment['slot_in_day'] + 1}",
                    'Ders': assignment['course_name'],
                    'Öğrenci Sayısı': assignment['expected_students'],
                    'Süre': f"{assignment['duration_minutes']} dk"
                })
            pd.DataFrame(room_view).to_excel(writer, sheet_name='Oda Bazlı Görünüm', index=False)
            
            # Program bilgileri
            program_info = pd.DataFrame([{
                'Sınav Türü': exam_program.sinav_turu or 'Belirtilmemiş',
                'Başlangıç Tarihi': exam_program.tarih_baslangic,
                'Bitiş Tarihi': exam_program.tarih_bitis,
                'Hariç Günler': ', '.join(exam_program.haris_gunler) if exam_program.haris_gunler else 'Yok',
                'Varsayılan Süre': f"{exam_program.varsayilan_sure} dk",
                'Bekleme Süresi': f"{exam_program.bekleme_suresi} dk",
                'Toplam Ders': len(schedule_summary)
            }])
            program_info.to_excel(writer, sheet_name='Program Bilgileri', index=False)
            
            # Uyarılar
            pd.DataFrame({'Uyarılar': warnings if warnings else ['Uyarı yok']}).to_excel(
                writer, sheet_name='Uyarılar', index=False)
            
    except Exception as e:
        warnings.append(f"Excel oluşturulamadı: {str(e)}")