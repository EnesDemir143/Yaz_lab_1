from collections import defaultdict
import math
import datetime
import os
from typing import List, Dict, Any, Tuple, Set
import pandas as pd
from .ExanProgramClass import ExamProgram
import numpy as np
from itertools import combinations

def _safe_to_str(val):
    """Excel'e yazılabilir güvenli dönüştürme"""
    if isinstance(val, (list, tuple, set, np.ndarray)):
        return ", ".join(map(str, val))
    elif isinstance(val, dict):
        return ", ".join(f"{k}: {v}" for k, v in val.items())
    elif isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat()
    elif pd.isna(val):
        return ""
    return str(val)

def _has_student_conflict(
    course_id: str, slot_idx: int, course_student_map: Dict[str, set],
    student_assigned_slots: Dict[str, set]
) -> bool:
    """Öğrenci çakışması kontrolü - aynı slotta çakışma var mı? (HER ZAMAN AKTİF)"""
    students = course_student_map.get(course_id, set())
    for sid in students:
        if slot_idx in student_assigned_slots.get(sid, set()):
            return True
    return False

def _has_same_year_conflict(
    course_year: str, slot_idx: int, day: str,
    day_year_courses: Dict[Tuple[str, str], List[str]]
) -> bool:
    """Aynı sınıfın başka bir dersi bu günde var mı kontrolü (HER ZAMAN AKTİF)"""
    return len(day_year_courses.get((day, course_year), [])) > 0

def _has_cross_year_conflict(
    course_id: str, slot_idx: int, 
    slot_assigned_courses: Dict[int, List[Dict]],
    exam_conflict: bool
) -> bool:
    """Farklı sınıflardan dersler aynı slotta olabilir mi kontrolü"""
    if exam_conflict:
        # exam_conflict=True ise farklı sınıfların dersleri aynı anda olabilir
        return False
    else:
        # exam_conflict=False ise hiçbir ders aynı anda olamaz
        return slot_idx in slot_assigned_courses and len(slot_assigned_courses[slot_idx]) > 0

def _has_waiting_time_conflict(
    course_id: str, slot_idx: int, course_student_map: Dict[str, set],
    student_assigned_slots: Dict[str, set], bekleme_slots: int
) -> bool:
    """Bekleme süresi çakışması kontrolü"""
    students = course_student_map.get(course_id, set())
    for sid in students:
        student_slots = student_assigned_slots.get(sid, set())
        # Bekleme süresi kadar önceki ve sonraki slotları kontrol et
        for offset in range(-bekleme_slots, bekleme_slots + 1):
            if offset == 0:
                continue
            check_slot = slot_idx + offset
            if check_slot in student_slots:
                return True
    return False

def _find_available_room_combo(
    combos: List[List[Dict]], slot_idx: int, slot_room_usage: Dict[int, set]
) -> List[Dict]:
    """Kullanılabilir oda kombinasyonu bul"""
    occupied = slot_room_usage.get(slot_idx, set())
    for combo in combos:
        combo_ids = {r["id"] for r in combo}
        if combo_ids.isdisjoint(occupied):
            return combo
    return None

def _place_course(
    course: Dict, day: str, global_slot_idx: int, slot_in_day: int,
    start_time: str, end_time: str, combo: List[Dict], assignments: List[Dict],
    student_assigned_slots: Dict[str, set], slot_room_usage: Dict[int, set],
    course_student_map: Dict[str, set]
):
    """Dersi programa yerleştir"""
    cid = course["id"]
    
    assignments.append({
        "course_id": cid,
        "course_name": course["name"],
        "course_year": course.get("year", ""),
        "day": day,
        "slot_index": global_slot_idx,
        "slot_in_day": slot_in_day,
        "start_time": start_time,
        "end_time": end_time,
        "room_ids": [r["id"] for r in combo],
        "room_name": ", ".join(r["name"] for r in combo),
        "expected_students": int(course["expected_students"]),
        "duration_minutes": int(course["duration_minutes"]),
    })
    
    # Öğrencilerin slotlarını işaretle
    for sid in course_student_map.get(cid, set()):
        student_assigned_slots[sid].add(global_slot_idx)
    
    # Odaları işaretle
    for r in combo:
        slot_room_usage[global_slot_idx].add(r["id"])

def _schedule_exams_optimized(
    active_courses: List[Dict],
    course_student_map: Dict[str, set],
    student_course_map: Dict[str, set],
    suitable_rooms: Dict[str, List[List[Dict]]],
    slot_list: List[Tuple[str, int, str, str]],
    bekleme_suresi: int,
    exam_program: ExamProgram,
) -> Tuple[List[Dict], List[str]]:
    """Optimize edilmiş sınav yerleştirme algoritması"""
    assignments: List[Dict] = []
    warnings: List[str] = []
    
    student_assigned_slots: Dict[str, set] = defaultdict(set)
    slot_room_usage: Dict[int, set] = defaultdict(set)
    day_year_courses: Dict[Tuple[str, str], List[str]] = defaultdict(list)  # (gün, yıl) -> ders listesi
    slot_assigned_courses: Dict[int, List[Dict]] = defaultdict(list)  # slot -> dersler
    
    # exam_conflict durumunu kontrol et
    check_cross_year = getattr(exam_program, "exam_conflict", False)
    
    # Bekleme süresi slot sayısına çevir
    slot_duration = int(exam_program.varsayilan_sure or 75)
    bekleme_slots = max(1, math.ceil(int(bekleme_suresi or 0) / slot_duration))
    
    print(f"\n🎯 OPTİMİZE YERLEŞTIRME BAŞLIYOR")
    print(f"   • Toplam Ders: {len(active_courses)}")
    print(f"   • Toplam Slot: {len(slot_list)}")
    print(f"   • Bekleme Süresi: {bekleme_suresi} dk ({bekleme_slots} slot)")
    print(f"   • Sınıflar Arası Aynı Anda: {'✅ İzin Verilir' if check_cross_year else '❌ İzin Verilmez'}")
    print(f"   • Öğrenci Çakışma Kontrolü: ✅ Her Zaman Aktif")
    print(f"   • Aynı Sınıf Farklı Gün: ✅ Her Zaman Aktif")
    
    # Dersleri yıl ve öğrenci sayısına göre grupla
    courses_by_year = defaultdict(list)
    for course in active_courses:
        year = course.get("year", "Bilinmeyen")
        courses_by_year[year].append(course)
    
    # Her yılın derslerini öğrenci sayısına göre sırala (büyükten küçüğe)
    for year in courses_by_year:
        courses_by_year[year].sort(key=lambda c: -int(c.get("expected_students", 0)))
    
    # Günleri eşit dağıtmak için
    days_list = sorted(set(day for day, _, _, _ in slot_list))
    total_days = len(days_list)
    
    print(f"\n📅 Yıl Bazlı Ders Dağılımı:")
    for year, courses in courses_by_year.items():
        print(f"   • {year}: {len(courses)} ders")
    
    # Her yılın derslerini günlere dağıt
    # ÖNCELİKLE: Her yıl için günleri belirle (bir yıl = bir gün)
    year_to_days: Dict[str, List[str]] = {}
    days_list = sorted(set(day for day, _, _, _ in slot_list))
    
    for idx, (year, courses) in enumerate(courses_by_year.items()):
        # Her yıla farklı günler ata (döngüsel olarak)
        year_days = []
        course_count = len(courses)
        
        # Kaç gün gerekli?
        days_needed = course_count  # Her ders bir gün
        
        # Günleri döngüsel olarak ata
        for i in range(days_needed):
            day_idx = (idx + i) % len(days_list)
            year_days.append(days_list[day_idx])
        
        year_to_days[year] = year_days
    
    print(f"\n📅 Sınıf-Gün Atamaları:")
    for year, days in year_to_days.items():
        print(f"   • {year}: {len(days)} gün ({', '.join(days[:3])}...)" if len(days) > 3 else f"   • {year}: {len(days)} gün")
    
    # Şimdi her yılın derslerini atanan günlere yerleştir
    for year, courses in courses_by_year.items():
        print(f"\n🎓 {year} dersleri yerleştiriliyor ({len(courses)} ders)...")
        assigned_days = year_to_days.get(year, [])
        day_idx = 0
        
        for course_idx, course in enumerate(courses):
            cid = course["id"]
            course_year = course.get("year", "Bilinmeyen")
            combos = suitable_rooms.get(cid, [])
            
            if not combos:
                warnings.append(f"⚠️ '{course['name']}' için uygun oda kombinasyonu yok")
                continue
            
            placed = False
            attempts = 0
            max_attempts = len(slot_list) * 2
            
            # Bu dersi sırayla günlere dene
            for attempt_offset in range(len(assigned_days)):
                if placed:
                    break
                
                target_day_idx = (day_idx + attempt_offset) % len(assigned_days)
                target_day = assigned_days[target_day_idx]
                
                # KURAL 1: Aynı sınıfın dersi bu günde var mı? (HER ZAMAN KONTROL)
                if _has_same_year_conflict(course_year, 0, target_day, day_year_courses):
                    continue
                    
                # Bu gündeki slotları dene
                day_slots = [
                    (idx, day, slot_in_day, start, end) 
                    for idx, (day, slot_in_day, start, end) in enumerate(slot_list)
                    if day == target_day
                ]
                
                for global_slot_idx, day, slot_in_day, start_time, end_time in day_slots:
                    attempts += 1
                    if attempts > max_attempts:
                        break
                    
                    # KURAL 2: Öğrenci çakışması kontrolü (HER ZAMAN AKTİF)
                    if _has_student_conflict(
                        cid, global_slot_idx, course_student_map, student_assigned_slots
                    ):
                        continue
                    
                    # KURAL 3: Bekleme süresi kontrolü (HER ZAMAN AKTİF)
                    if _has_waiting_time_conflict(
                        cid, global_slot_idx, course_student_map, 
                        student_assigned_slots, bekleme_slots
                    ):
                        continue
                    
                    # KURAL 4: Farklı sınıflar aynı anda olabilir mi? (exam_conflict'e göre)
                    if _has_cross_year_conflict(
                        cid, global_slot_idx, slot_assigned_courses, check_cross_year
                    ):
                        continue
                    
                    # KURAL 5: Oda uygunluğu kontrolü
                    combo = _find_available_room_combo(combos, global_slot_idx, slot_room_usage)
                    if not combo:
                        continue
                    
                    # Dersi yerleştir
                    _place_course(
                        course, day, global_slot_idx, slot_in_day, start_time, end_time,
                        combo, assignments, student_assigned_slots, slot_room_usage,
                        course_student_map
                    )
                    
                    day_year_courses[(day, course_year)].append(cid)
                    slot_assigned_courses[global_slot_idx].append(course)
                    placed = True
                    
                    # Slot doluluk oranını hesapla
                    slot_courses = slot_assigned_courses[global_slot_idx]
                    slot_years = set(c.get('year', 'N/A') for c in slot_courses)
                    
                    print(f"   ✓ {course['name']} ({course_year}) → {day} {start_time}-{end_time} ({combo[0]['name']}) "
                          f"[Slot: {len(slot_courses)} ders, {len(slot_years)} sınıf]")
                    break
            
            if placed:
                day_idx += 1  # Sonraki ders için sonraki güne geç
            
            if not placed:
                warnings.append(
                    f"❌ '{course['name']}' yerleştirilemedi "
                    f"(Öğrenci: {course['expected_students']}, Sınıf: {course_year})"
                )
    
    # İstatistikler
    placed_count = len(assignments)
    success_rate = (placed_count / len(active_courses) * 100) if active_courses else 0
    
    print(f"\n📊 YERLEŞTIRME SONUÇLARI:")
    print(f"   • Yerleştirilen: {placed_count}/{len(active_courses)} (%{success_rate:.1f})")
    print(f"   • Yerleştirilemeyen: {len(active_courses) - placed_count}")
    
    # Gün bazlı yıl dağılım istatistiği
    print(f"\n📈 Gün Bazlı Sınıf Dağılımı:")
    days_list = sorted(set(day for day, _, _, _ in slot_list))
    for day in days_list:
        day_stats = []
        for year in courses_by_year.keys():
            courses_in_day = day_year_courses.get((day, year), [])
            if courses_in_day:
                day_stats.append(f"{year}: {len(courses_in_day)} ders")
        if day_stats:
            print(f"   • {day}: {', '.join(day_stats)}")
    
    return assignments, warnings

def create_exam_schedule(
    exam_program: ExamProgram,
    class_dict: Dict[str, Dict],
    rooms_data: List[Dict],
    excel_output_path: str = "sinav_programi.xlsx",
) -> Dict[str, Any]:
    warnings: List[str] = []
    critical_errors: List[str] = []

    # 1) Tarih aralığı kontrolü
    days = _create_available_days(exam_program)
    if not days:
        critical_errors.append("❌ KRİTİK: Uygun gün bulunamadı!")
        return {
            "status": "error",
            "schedule": [],
            "warnings": warnings,
            "errors": critical_errors,
            "excel": None
        }

    # 2) Slot oluşturma
    start_hour = 10
    end_hour = 20
    slot_duration_hours = exam_program.bekleme_suresi // 60 + (exam_program.varsayilan_sure or 75) // 60
    slot_list: List[Tuple[str, int, str, str]] = []

    for d in days:
        current_hour = start_hour
        slot_idx_in_day = 0
        while current_hour + slot_duration_hours <= end_hour:
            start_time = f"{current_hour:02d}:00"
            end_time = f"{current_hour + slot_duration_hours:02d}:00"
            slot_list.append((d, slot_idx_in_day, start_time, end_time))
            current_hour += slot_duration_hours
            slot_idx_in_day += 1

    # 3) Veri dönüşümleri
    courses_data, students_data = _convert_class_dict_to_courses_and_students(class_dict, exam_program)

    # 4) Aktif dersler
    active_courses = _prepare_courses(exam_program, courses_data, students_data)
    if not active_courses:
        critical_errors.append("❌ KRİTİK: Programa eklenecek ders bulunamadı.")
        return {
            "status": "error",
            "schedule": [],
            "warnings": warnings,
            "errors": critical_errors,
            "excel": None
        }

    # 5) Öğrenci-ders haritaları
    student_course_map = _build_student_course_map(students_data)
    course_student_map = _build_course_student_map(students_data)

    # 6) Oda uygunluk kontrolü (DÜZELTİLDİ)
    suitable_rooms, room_errors = _check_room_suitability_v3(active_courses, rooms_data)
    warnings.extend(room_errors)

    # 7) Kapasite kontrolü (DÜZELTİLDİ - artık tüm odaların toplamını kontrol ediyor)
    capacity_errors = _validate_capacity_requirements(active_courses, rooms_data)
    if capacity_errors:
        # Kapasite hatası varsa warning olarak ekle, ama devam et
        warnings.extend(capacity_errors)

    # 8) OPTİMİZE YERLEŞTİRME
    assignments, placement_warnings = _schedule_exams_optimized(
        active_courses=active_courses,
        course_student_map=course_student_map,
        student_course_map=student_course_map,
        suitable_rooms=suitable_rooms,
        slot_list=slot_list,
        bekleme_suresi=exam_program.bekleme_suresi,
        exam_program=exam_program,
    )
    warnings.extend(placement_warnings)

    # 9) Yerleştirilemeyenler kontrolü
    placed_course_ids = {a["course_id"] for a in assignments}
    unplaced = [c for c in active_courses if c["id"] not in placed_course_ids]
    
    if unplaced:
        warnings.append(f"⚠️ {len(unplaced)} ders yerleştirilemedi!")
        for course in unplaced[:5]:
            warnings.append(
                f"   • {course['name']} (Öğrenci: {course['expected_students']}, "
                f"Yıl: {course.get('year', 'N/A')}, "
                f"Süre: {course['duration_minutes']} dk)"
            )

    # 10) Özet
    schedule_summary = _create_schedule_summary(assignments)

    # 11) Excel yazma
    excel_output_path = _write_excel_output(
        schedule_summary, assignments, warnings, exam_program, excel_output_path
    )

    return {
        "status": "success" if not critical_errors else "warning",
        "schedule": schedule_summary,
        "assignments": assignments,
        "warnings": warnings,
        "errors": critical_errors,
        "excel": excel_output_path,
        "exam_program_info": exam_program.to_dict(),
        "statistics": {
            "total_courses": len(active_courses),
            "placed_courses": len(placed_course_ids),
            "unplaced_courses": len(unplaced),
            "total_days": len(days),
            "total_slots": len(slot_list),
        }
    }

def _convert_class_dict_to_courses_and_students(
    class_dict: Dict[str, Dict], exam_program: ExamProgram
) -> Tuple[List[Dict], List[Dict]]:
    courses_data: List[Dict] = []
    students_data: List[Dict] = []
    kalan_dersler = set(exam_program.get_kalan_dersler())

    for class_id, class_info in class_dict.items():
        class_name = class_info["class_name"]

        if class_name in kalan_dersler:
            courses_data.append({
                "id": class_id, 
                "name": class_name, 
                "year": class_info.get('year', 'Bilinmeyen'),
            })

            for student in class_info.get("students", []):
                student_num = student.get("student_num")
                if not student_num:
                    continue
                existing = next((s for s in students_data if s["id"] == student_num), None)
                if existing:
                    if class_id not in existing["courses"]:
                        existing["courses"].append(class_id)
                else:
                    students_data.append({
                        "id": student_num,
                        "name": f"{student.get('name', '')} {student.get('surname', '')}".strip(),
                        "courses": [class_id],
                    })

    return courses_data, students_data

def _create_available_days(exam_program: ExamProgram) -> List[str]:
    def parse_date(date_str):
        if isinstance(date_str, str):
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"):
                try:
                    return datetime.datetime.strptime(date_str, fmt).date()
                except Exception:
                    continue
        elif isinstance(date_str, datetime.date):
            return date_str
        return None

    start = parse_date(exam_program.tarih_baslangic)
    end = parse_date(exam_program.tarih_bitis)

    if not start or not end:
        start = datetime.date.today()
        end = start + datetime.timedelta(days=10)

    if end < start:
        start, end = end, start

    exclude_weekdays = set()
    weekday_map = {
        "pazartesi": 0, "monday": 0,
        "salı": 1, "tuesday": 1,
        "çarşamba": 2, "wednesday": 2,
        "perşembe": 3, "thursday": 3,
        "cuma": 4, "friday": 4,
        "cumartesi": 5, "saturday": 5,
        "pazar": 6, "sunday": 6,
    }
    for gun in (exam_program.haris_gunler or []):
        gun_lower = str(gun).lower().strip()
        for key, val in weekday_map.items():
            if key in gun_lower:
                exclude_weekdays.add(val)
                break

    days: List[str] = []
    cur = start
    while cur <= end:
        if cur.weekday() not in exclude_weekdays:
            days.append(cur.isoformat())
        cur += datetime.timedelta(days=1)

    return days

def _prepare_courses(
    exam_program: ExamProgram, courses_data: List[Dict], students_data: List[Dict]
) -> List[Dict]:
    kalan_dersler = set(exam_program.get_kalan_dersler())
    active: List[Dict] = []

    course_student_count = defaultdict(int)
    for student in students_data:
        for cid in student.get("courses", []):
            course_student_count[cid] += 1

    for course in courses_data:
        name = course.get("name")
        if name in kalan_dersler:
            c = dict(course)
            c["duration_minutes"] = exam_program.get_ders_suresi(name)
            c["expected_students"] = max(1, int(course_student_count.get(course["id"], 0)))
            active.append(c)

    return active

def _build_student_course_map(students_data: List[Dict]) -> Dict[str, set]:
    return {s["id"]: set(s.get("courses", [])) for s in students_data}

def _build_course_student_map(students_data: List[Dict]) -> Dict[str, set]:
    mapping = defaultdict(set)
    for s in students_data:
        for cid in s.get("courses", []):
            mapping[cid].add(s["id"])
    return mapping

def _check_room_suitability_v3(
    courses: List[Dict], rooms: List[Dict]
) -> Tuple[Dict[str, List[List[Dict]]], List[str]]:
    """Her ders için uygun oda kombinasyonlarını bul"""
    suitable_rooms: Dict[str, List[List[Dict]]] = {}
    errors: List[str] = []
    
    if not rooms:
        errors.append("❌ KRİTİK: Hiç derslik tanımlanmamış!")
        return {}, errors

    # Odaları kapasiteye göre sırala
    sorted_rooms = sorted(rooms, key=lambda x: int(x.get("capacity", 0) or 0))
    
    # Toplam kapasite hesapla
    total_capacity = sum(int(r.get("capacity", 0) or 0) for r in rooms)
    max_single_room = max((int(r.get("capacity", 0) or 0) for r in rooms), default=0)

    print(f"\n🏫 ODA BİLGİLERİ:")
    print(f"   • Toplam Oda: {len(rooms)}")
    print(f"   • Toplam Kapasite: {total_capacity}")
    print(f"   • En Büyük Oda: {max_single_room}")

    for course in courses:
        need = int(course["expected_students"])
        combos = _find_room_combinations(sorted_rooms, need, max_combo=3)

        if not combos:
            errors.append(
                f"⚠️ UYARI: '{course['name']}' için yeterli oda yok "
                f"(İhtiyaç: {need}, Maks Tek Oda: {max_single_room})"
            )
            # En büyük odayı ata (yetersiz olsa bile)
            if sorted_rooms:
                combos = [sorted_rooms[-1:]]

        suitable_rooms[course["id"]] = combos

    return suitable_rooms, errors

def _find_room_combinations(rooms: List[Dict], need: int, max_combo: int = 3) -> List[List[Dict]]:
    """Gerekli kapasiteyi karşılayan oda kombinasyonlarını bul"""
    valid = []
    
    # 1, 2, 3 odalı kombinasyonları dene
    for r in range(1, min(max_combo + 1, len(rooms) + 1)):
        for combo in combinations(rooms, r):
            total = sum(int(c.get("capacity", 0) or 0) for c in combo)
            if total >= need:
                valid.append(list(combo))
    
    # En küçük toplam kapasiteli kombinasyonu önce kullan
    valid.sort(key=lambda c: sum(int(x.get("capacity", 0) or 0) for x in c))
    return valid

def _validate_capacity_requirements(courses: List[Dict], rooms: List[Dict]) -> List[str]:
    """Kapasite gereksinimlerini kontrol et"""
    errors: List[str] = []
    
    if not rooms:
        errors.append("❌ KRİTİK: Hiç derslik tanımlanmamış!")
        return errors
    
    # Tüm odaların TOPLAM kapasitesini hesapla
    total_room_capacity = sum(int(r.get("capacity", 0) or 0) for r in rooms)
    max_course_students = max((int(c["expected_students"]) for c in courses), default=0)
    
    # En büyük dersin kapasitesi, tüm odaların toplamından fazla mı?
    if max_course_students > total_room_capacity:
        errors.append(
            f"⚠️ UYARI: En büyük ders ({max_course_students} öğr.) > "
            f"Toplam tüm odalar ({total_room_capacity}). "
            f"Bu ders için birden fazla oda kullanılacak."
        )
    
    return errors

def _create_schedule_summary(assignments: List[Dict]) -> List[Dict]:
    summary: List[Dict] = []
    group_map = defaultdict(list)
    
    for a in assignments:
        group_map[a["course_id"]].append(a)

    for cid, assigns in group_map.items():
        first = assigns[0]
        summary.append({
            "course_id": _safe_to_str(first["course_id"]),
            "course_name": _safe_to_str(first["course_name"]),
            "course_year": _safe_to_str(first.get("course_year", "")),
            "day": _safe_to_str(first["day"]),
            "slot_in_day": int(first["slot_in_day"]),
            "start_time": _safe_to_str(first.get("start_time", "")),
            "room_name": _safe_to_str(first.get("room_name", "")),
            "expected_students": int(first["expected_students"]),
            "duration_minutes": int(first["duration_minutes"]),
        })

    summary.sort(key=lambda x: (x["day"], x["slot_in_day"]))
    return summary

def _write_excel_output(
    schedule_summary: List[Dict],
    assignments: List[Dict],
    warnings: List[str],
    exam_program: ExamProgram,
    output_path: str
) -> str:
    if not schedule_summary:
        print("⚠️ schedule_summary boş, Excel oluşturma atlanıyor.")
        return os.path.abspath(output_path)

    abs_path = os.path.abspath(output_path)
    print(f"\n✍️ Excel yazılıyor: {abs_path}")

    try:
        columns = [
            "course_id", "course_name", "course_year", "day", "slot_in_day",
            "start_time", "room_name", "expected_students", "duration_minutes"
        ]
        
        data_as_list = []
        for row_dict in schedule_summary:
            row_as_list = [row_dict.get(key, None) for key in columns]
            data_as_list.append(row_as_list)

        df_schedule = pd.DataFrame(data_as_list, columns=columns)
        
        column_rename = {
            "course_id": "Ders ID",
            "course_name": "Ders Adı",
            "course_year": "Sınıf",
            "day": "Tarih",
            "slot_in_day": "Seans",
            "start_time": "Başlangıç Saati",
            "room_name": "Oda",
            "expected_students": "Öğrenci Sayısı",
            "duration_minutes": "Süre (dk)"
        }
        df_schedule = df_schedule.rename(columns=column_rename)
        
        desired_columns = ["Ders ID", "Ders Adı", "Sınıf", "Tarih", "Seans", "Başlangıç Saati", "Oda", "Öğrenci Sayısı", "Süre (dk)"]
        for col in desired_columns:
            if col not in df_schedule.columns:
                df_schedule[col] = None
        df_schedule = df_schedule[desired_columns]

        # Oda bazlı görünüm
        slot_names = ["10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00", "18:00-20:00"]
        room_data = []
        for a in assignments:
            try:
                slot_idx = int(a.get("slot_in_day", 0))
                s_name = slot_names[slot_idx] if slot_idx < len(slot_names) else f"Slot {slot_idx + 1}"
                room_data.append([
                    _safe_to_str(a.get("room_name", "")),
                    _safe_to_str(a.get("day", "")),
                    s_name,
                    _safe_to_str(a.get("course_name", "")),
                    _safe_to_str(a.get("course_year", "")),
                    int(a.get("expected_students", 0)),
                    f"{int(a.get('duration_minutes', 0))} dk",
                ])
            except Exception:
                continue
        
        df_room = pd.DataFrame(room_data, columns=["Oda", "Gün", "Seans", "Ders", "Sınıf", "Öğrenci", "Süre"])

        # Program bilgileri
        istisna_text = "Yok"
        if getattr(exam_program, "istisna_dersler", None):
            istisna_list = [f"{d}: {s} dk" for d, s in exam_program.istisna_dersler.items()]
            istisna_text = ", ".join(istisna_list)

        info_data = [
            ["Sınav Türü", _safe_to_str(exam_program.sinav_turu or "Belirtilmemiş")],
            ["Başlangıç Tarihi", _safe_to_str(exam_program.tarih_baslangic)],
            ["Bitiş Tarihi", _safe_to_str(exam_program.tarih_bitis)],
            ["Hariç Günler", ", ".join(map(str, exam_program.haris_gunler)) if exam_program.haris_gunler else "Yok"],
            ["Varsayılan Süre", f"{int(exam_program.varsayilan_sure)} dk"],
            ["İstisna Dersler", istisna_text],
            ["Bekleme Süresi", f"{int(exam_program.bekleme_suresi)} dk"],
            ["Farklı Sınıflar Aynı Anda", "İzin Verilir" if getattr(exam_program, "exam_conflict", False) else "İzin Verilmez"],
            ["Toplam Ders", str(len(schedule_summary))],
            ["Hariç Dersler", ", ".join(map(str, exam_program.excluded_courses)) if exam_program.excluded_courses else "Yok"],
        ]
        df_info = pd.DataFrame(info_data, columns=["Alan", "Değer"])

        day_stats = defaultdict(lambda: {"courses": 0, "students": 0, "rooms": set()})
        for a in assignments:
            day = a.get("day", "")
            day_stats[day]["courses"] += 1
            day_stats[day]["students"] += int(a.get("expected_students", 0))
            for room_id in a.get("room_ids", []):
                day_stats[day]["rooms"].add(room_id)
        
        stat_data = []
        for day in sorted(day_stats.keys()):
            stat = day_stats[day]
            stat_data.append([
                _safe_to_str(day),
                stat["courses"],
                stat["students"],
                len(stat["rooms"])
            ])
        
        df_stats = pd.DataFrame(stat_data, columns=["Tarih", "Sınav Sayısı", "Toplam Öğrenci", "Kullanılan Oda"])

        warn_data = [[_safe_to_str(w)] for w in warnings] if warnings else [["✅ Uyarı yok"]]
        df_warn = pd.DataFrame(warn_data, columns=["Uyarılar"])

        with pd.ExcelWriter(abs_path, engine="openpyxl") as writer:
            df_schedule.to_excel(writer, sheet_name="Sınav Programı", index=False)
            df_room.to_excel(writer, sheet_name="Oda Bazlı Görünüm", index=False)
            df_stats.to_excel(writer, sheet_name="Gün İstatistikleri", index=False)
            df_info.to_excel(writer, sheet_name="Program Bilgileri", index=False)
            df_warn.to_excel(writer, sheet_name="Uyarılar", index=False)

        print(f"✅ Excel dosyası başarıyla oluşturuldu!")
        return abs_path

    except Exception as e:
        msg = f"❌ Excel oluşturulamadı: {str(e)}"
        warnings.append(msg)
        print(msg)
        import traceback
        print(traceback.format_exc())
        return abs_path