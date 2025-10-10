# Backend/src/utils/exams/create_exam_program.py
from collections import defaultdict, Counter
import math
import datetime
import os
from typing import List, Dict, Any, Tuple

import pandas as pd

from .ExanProgramClass import ExamProgram
import numpy as np

def _safe_to_str(val):
    """Excel'e yazılabilir güvenli dönüştürme (numpy, liste, tarih, dict vb.)."""
    if isinstance(val, (list, tuple, set, np.ndarray)):
        return ", ".join(map(str, val))
    elif isinstance(val, dict):
        return ", ".join(f"{k}: {v}" for k, v in val.items())
    elif isinstance(val, (datetime.date, datetime.datetime)):
        return val.isoformat()
    elif pd.isna(val):
        return ""
    return str(val)


def create_exam_schedule(
    exam_program: ExamProgram,
    class_dict: Dict[str, Dict],
    rooms_data: List[Dict],
    excel_output_path: str = "sinav_programi.xlsx",
) -> Dict[str, Any]:
    warnings: List[str] = []
    critical_errors: List[str] = []  # ✅ KRİTİK HATALAR

    # 1) Tarih aralığı kontrolü
    days = _create_available_days(exam_program)
    if not days:
        critical_errors.append("❌ KRİTİK: Uygun gün bulunamadı! Lütfen tarih aralığını ve hariç günleri kontrol edin.")
        return {
            "status": "error",
            "schedule": [],
            "warnings": warnings,
            "errors": critical_errors,
            "excel": None
        }

    # 2) Slot oluşturma
    slots_per_day = 3
    slot_list: List[Tuple[str, int]] = []
    for d in days:
        for s in range(slots_per_day):
            slot_list.append((d, s))

    # 3) Veri dönüşümleri
    courses_data, students_data = _convert_class_dict_to_courses_and_students(class_dict, exam_program)

    # 4) Aktif dersler
    active_courses = _prepare_courses(exam_program, courses_data, students_data)
    if not active_courses:
        critical_errors.append("❌ KRİTİK: Programa eklenecek ders bulunamadı. Tüm dersler hariç tutulmuş olabilir.")
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

    # 6) Oda uygunluk kontrolü (geliştirilmiş)
    suitable_rooms, room_errors = _check_room_suitability_v2(active_courses, rooms_data)
    warnings.extend(room_errors)

    # 7) Kapasite kontrolü
    capacity_errors = _validate_capacity_requirements(active_courses, rooms_data)
    if capacity_errors:
        critical_errors.extend(capacity_errors)
        return {
            "status": "error",
            "schedule": [],
            "warnings": warnings,
            "errors": critical_errors,
            "excel": None
        }

    # 8) Yerleştirme
    assignments, placement_warnings = _schedule_exams_v2(
        active_courses=active_courses,
        course_student_map=course_student_map,
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
        critical_errors.append(f"❌ KRİTİK: {len(unplaced)} ders yerleştirilemedi!")
        for course in unplaced:
            critical_errors.append(
                f"   • {course['name']} (Öğrenci: {course['expected_students']}, "
                f"Süre: {course['duration_minutes']} dk)"
            )
        
        # Eğer tüm derslerin yarısından fazlası yerleştirilemediyse programı oluşturma
        if len(unplaced) > len(active_courses) / 2:
            critical_errors.append(
                "❌ KRİTİK: Derslerin yarısından fazlası yerleştirilemedi. "
                "Program oluşturulmadı. Lütfen tarih aralığını genişletin veya "
                "odaları artırın."
            )
            return {
                "status": "error",
                "schedule": [],
                "warnings": warnings,
                "errors": critical_errors,
                "excel": None
            }

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

# ---------------------------------------------------------------------
# DÖNÜŞÜMLER
# ---------------------------------------------------------------------
def _convert_class_dict_to_courses_and_students(
    class_dict: Dict[str, Dict], exam_program: ExamProgram
) -> Tuple[List[Dict], List[Dict]]:
    """class_dict'i courses ve students listelerine dönüştürür."""
    courses_data: List[Dict] = []
    students_data: List[Dict] = []
    kalan_dersler = set(exam_program.get_kalan_dersler())

    for class_id, class_info in class_dict.items():
        class_name = class_info["class_name"]

        # Sadece kalan dersler
        if class_name in kalan_dersler:
            courses_data.append({"id": class_id, "name": class_name})

            # Öğrenciler
            for student in class_info.get("students", []):
                student_num = student.get("student_num")
                if not student_num:
                    continue
                existing = next((s for s in students_data if s["id"] == student_num), None)
                if existing:
                    if class_id not in existing["courses"]:
                        existing["courses"].append(class_id)
                else:
                    students_data.append(
                        {
                            "id": student_num,
                            "name": f"{student.get('name', '')} {student.get('surname', '')}".strip(),
                            "courses": [class_id],
                        }
                    )

    return courses_data, students_data


def _create_available_days(exam_program: ExamProgram) -> List[str]:
    """ExamProgram'dan tarih aralığını alarak uygun günleri oluşturur."""
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

    # Varsayılan tarih aralığı
    if not start or not end:
        start = datetime.date.today()
        end = start + datetime.timedelta(days=10)

    if end < start:
        start, end = end, start

    # Hariç günleri map et
    exclude_weekdays = set()
    weekday_map = {
        "pazartesi": 0,
        "monday": 0,
        "salı": 1,
        "tuesday": 1,
        "çarşamba": 2,
        "wednesday": 2,
        "perşembe": 3,
        "thursday": 3,
        "cuma": 4,
        "friday": 4,
        "cumartesi": 5,
        "saturday": 5,
        "pazar": 6,
        "sunday": 6,
    }
    for gun in (exam_program.haris_gunler or []):
        gun_lower = str(gun).lower().strip()
        for key, val in weekday_map.items():
            if key in gun_lower:
                exclude_weekdays.add(val)
                break

    # Günleri oluştur
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
    """Kalan dersleri hazırlar ve ders sürelerini ekler."""
    kalan_dersler = set(exam_program.get_kalan_dersler())
    active: List[Dict] = []

    # Ders bazında öğrenci sayısı
    course_student_count = defaultdict(int)
    for student in students_data:
        for cid in student.get("courses", []):
            course_student_count[cid] += 1

    for course in courses_data:
        name = course.get("name")
        if name in kalan_dersler:
            c = dict(course)
            # Süreleri al
            c["duration_minutes"] = exam_program.get_ders_suresi(name)
            # Öğrenci sayısı (0 ise en az 1 yap ki kapasite kontrolü devreye girsin)
            c["expected_students"] = max(1, int(course_student_count.get(course["id"], 0)))
            active.append(c)

    return active


# ---------------------------------------------------------------------
# HARİTALAR
# ---------------------------------------------------------------------
def _build_student_course_map(students_data: List[Dict]) -> Dict[str, set]:
    return {s["id"]: set(s.get("courses", [])) for s in students_data}


def _build_course_student_map(students_data: List[Dict]) -> Dict[str, set]:
    mapping = defaultdict(set)
    for s in students_data:
        for cid in s.get("courses", []):
            mapping[cid].add(s["id"])
    return mapping


# ---------------------------------------------------------------------
# ODA & YERLEŞTİRME
# ---------------------------------------------------------------------
def _check_room_suitability_v2(
    courses: List[Dict], rooms: List[Dict]
) -> Tuple[Dict[str, List], List[str]]:
    """Geliştirilmiş oda uygunluk kontrolü - detaylı hata mesajları"""
    suitable_rooms: Dict[str, List] = {}
    errors: List[str] = []
    
    all_caps = [int(r.get("capacity", 0) or 0) for r in rooms]
    max_cap = max(all_caps) if all_caps else 0

    sorted_rooms = sorted(rooms, key=lambda x: int(x.get("capacity", 0) or 0))

    for course in courses:
        need = int(course["expected_students"])
        suitable = [r for r in sorted_rooms if int(r.get("capacity", 0) or 0) >= need]
        
        if not suitable:
            errors.append(
                f"⚠️ UYARI: '{course['name']}' dersi için uygun oda yok!\n"
                f"   → Gerekli kapasite: {need} öğrenci\n"
                f"   → En büyük oda: {max_cap} kişilik\n"
                f"   → Önerilen çözüm: {need} kişilik veya daha büyük oda ekleyin"
            )
            # En büyük odayı seç (program aksamasın)
            suitable = sorted_rooms[-1:] if sorted_rooms else []
        
        suitable_rooms[course["id"]] = suitable

    return suitable_rooms, errors

def _validate_capacity_requirements(
    courses: List[Dict], rooms: List[Dict]
) -> List[str]:
    """Tüm derslerin toplam kapasitesinin odalarla karşılanıp karşılanmadığını kontrol eder"""
    errors: List[str] = []
    
    if not rooms:
        errors.append("❌ KRİTİK: Hiç derslik tanımlanmamış!")
        return errors
    
    total_room_capacity = sum(int(r.get("capacity", 0) or 0) for r in rooms)
    max_course_students = max((int(c["expected_students"]) for c in courses), default=0)
    
    if max_course_students > total_room_capacity:
        errors.append(
            f"❌ KRİTİK: Hiçbir oda kombinasyonu en büyük dersi karşılayamıyor!\n"
            f"   → En kalabalık ders: {max_course_students} öğrenci\n"
            f"   → Toplam oda kapasitesi: {total_room_capacity}\n"
            f"   → Önerilen çözüm: Daha büyük oda ekleyin veya dersi parçalayın"
        )
    
    return errors

def _schedule_exams_v2(
    active_courses: List[Dict],
    course_student_map: Dict[str, set],
    suitable_rooms: Dict[str, List[Dict]],
    slot_list: List[Tuple[str, int]],
    bekleme_suresi: int,
    exam_program: ExamProgram,
) -> Tuple[List[Dict], List[str]]:
    """Geliştirilmiş yerleştirme - detaylı sebep açıklaması"""
    
    assignments: List[Dict] = []
    warnings: List[str] = []
    student_assigned_slots: Dict[str, set] = defaultdict(set)
    class_assignments: Dict[str, List[Tuple[str, int]]] = defaultdict(list)

    # Sıralama
    class_counts = Counter([c.get("name") for c in active_courses])
    active_courses.sort(
        key=lambda c: (-c["expected_students"], -class_counts.get(c.get("name"), 0))
    )

    slot_duration = int(exam_program.varsayilan_sure or 75)
    bekleme_slots = max(1, math.ceil(int(bekleme_suresi or 0) / slot_duration))
    check_conflicts = getattr(exam_program, "exam_conflict", True)

    for course in active_courses:
        cid = course["id"]
        group = course.get("name")
        rooms = suitable_rooms.get(cid, [])
        
        if not rooms:
            warnings.append(f"⚠️ '{course['name']}' için uygun oda bulunamadı.")
            continue

        placed = False
        rejection_reasons = []  # ✅ RED SEBEPLERİ

        day_prefs = _calculate_day_preferences(group, class_assignments, slot_list)

        for _, day in day_prefs:
            day_slots = [i for i, (d, _) in enumerate(slot_list) if d == day]

            for slot_idx in day_slots:
                # Sınıf çakışması
                if _has_class_conflict(group, slot_idx, class_assignments, slot_list):
                    rejection_reasons.append(
                        f"   ✗ {day} Slot {slot_idx}: Aynı sınıfın ({group}) başka sınavı var"
                    )
                    continue

                # Öğrenci çakışması
                if check_conflicts:
                    conflict_students = _get_conflicting_students(
                        cid, slot_idx, course_student_map, student_assigned_slots, bekleme_slots
                    )
                    if conflict_students:
                        rejection_reasons.append(
                            f"   ✗ {day} Slot {slot_idx}: "
                            f"{len(conflict_students)} öğrenci çakışması"
                        )
                        continue

                # Oda müsaitliği
                available_room = _find_available_room(rooms, slot_idx, assignments)
                if not available_room:
                    rejection_reasons.append(
                        f"   ✗ {day} Slot {slot_idx}: Tüm uygun odalar dolu"
                    )
                    continue

                # ✅ YERLEŞTİR
                d, s_in_day = slot_list[slot_idx]
                assignments.append(
                    {
                        "course_id": cid,
                        "course_name": course["name"],
                        "day": d,
                        "slot_index": slot_idx,
                        "slot_in_day": s_in_day,
                        "room_id": available_room["id"],
                        "room_name": available_room["name"],
                        "expected_students": int(course["expected_students"]),
                        "duration_minutes": int(course["duration_minutes"]),
                    }
                )

                if check_conflicts:
                    for sid in course_student_map.get(cid, set()):
                        student_assigned_slots[sid].add(slot_idx)

                class_assignments[group].append((cid, slot_idx))
                placed = True
                break

            if placed:
                break

        if not placed:
            warning_msg = (
                f"❌ '{course['name']}' dersi yerleştirilemedi!\n"
                f"   → Öğrenci sayısı: {course['expected_students']}\n"
                f"   → Süre: {course['duration_minutes']} dk\n"
                f"   → Sınıf: {group}\n"
                f"   → Red sebepleri ({len(rejection_reasons)} deneme):\n"
            )
            warning_msg += "\n".join(rejection_reasons[:5])  # İlk 5 sebep
            if len(rejection_reasons) > 5:
                warning_msg += f"\n   ... ve {len(rejection_reasons) - 5} sebep daha"
            warnings.append(warning_msg)

    return assignments, warnings


def _get_conflicting_students(
    course_id: str,
    slot_idx: int,
    course_student_map: Dict[str, set],
    student_assigned_slots: Dict[str, set],
    bekleme_slots: int
) -> set:
    """Çakışan öğrencileri döndürür (debug için)"""
    conflicting = set()
    students = course_student_map.get(course_id, set())
    
    for sid in students:
        for assigned_slot in student_assigned_slots.get(sid, set()):
            if abs(assigned_slot - slot_idx) <= bekleme_slots:
                conflicting.add(sid)
    
    return conflicting


def _calculate_day_preferences(
    class_name: str, class_assignments: Dict[str, List[Tuple[str, int]]], slot_list: List[Tuple[str, int]]
) -> List[Tuple[int, str]]:
    """Sınıf için gün tercihlerini hesaplar (az kullanılan günler önce)."""
    day_counts = defaultdict(int)
    for _, slot_idx in class_assignments.get(class_name, []):
        day = slot_list[slot_idx][0]
        day_counts[day] += 1

    unique_days = list({d for d, _ in slot_list})
    prefs = [(day_counts[day], day) for day in unique_days]
    prefs.sort(key=lambda x: x[0])
    # [(0, '2025-10-10'), (0, '2025-10-11'), (1, '2025-10-12'), ...]
    return [(i, day) for i, (_, day) in enumerate(prefs)]


def _has_class_conflict(
    class_name: str, slot_idx: int, class_assignments: Dict[str, List[Tuple[str, int]]], slot_list: List[Tuple[str, int]]
) -> bool:
    """Aynı sınıfın aynı gün içinde birden fazla sınava konmasını engeller."""
    day = slot_list[slot_idx][0]
    for _, a_slot_idx in class_assignments.get(class_name, []):
        a_day = slot_list[a_slot_idx][0]
        if a_day == day:
            return True
    return False


def _find_available_room(rooms: List[Dict], slot_idx: int, assignments: List[Dict]) -> Dict:
    """Verilen slot için uygun ve boş bir oda döndürür (küçükten büyüğe)."""
    occupied = {a["room_id"] for a in assignments if a["slot_index"] == slot_idx}
    for room in rooms:
        if room["id"] not in occupied:
            return room
    return None


# ---------------------------------------------------------------------
# ÖZET / EXCEL
# ---------------------------------------------------------------------
def _create_schedule_summary(assignments: List[Dict]) -> List[Dict]:
    """Sınav programı özetini oluşturur (ders bazlı tek satır)."""
    summary: List[Dict] = []
    group_map = defaultdict(list)
    
    for a in assignments:
        group_map[a["course_id"]].append(a)

    for cid, assigns in group_map.items():
        first = assigns[0]
        
        # ✅ TÜM DEĞERLERİ PYTHON NATIVE TİPLERE ÇEVİR
        summary.append(
            {
                "course_id": _safe_to_str(first["course_id"]),
                "course_name": _safe_to_str(first["course_name"]),
                "day": _safe_to_str(first["day"]),
                "slot_in_day": int(first["slot_in_day"]),
                "room_name": _safe_to_str(first["room_name"]),
                "expected_students": int(first["expected_students"]),
                "duration_minutes": int(first["duration_minutes"]),
            }
        )

    summary.sort(key=lambda x: (x["day"], x["slot_in_day"]))
    return summary


def _write_excel_output(
    schedule_summary: List[Dict], assignments: List[Dict], warnings: List[str], exam_program: ExamProgram, output_path: str
) -> str:

    print("\n\n🧩 DEBUG: Excel yazma işlemi başlıyor")
    print(f"📄 schedule_summary uzunluk: {len(schedule_summary)}")
    
    if not schedule_summary:
        print("⚠️ schedule_summary boş olduğu için Excel oluşturma atlanıyor.")
        return os.path.abspath(output_path)

    abs_path = os.path.abspath(output_path)
    print(f"📁 Excel absolute path: {abs_path}")

    try:
        # 1) Ana program sheet'ini doğrudan schedule_summary'den oluştur
        # Bu yaklaşım, manuel liste oluşturmaktan çok daha güvenlidir.
        # --- MANUEL DÖNÜŞÜM BAŞLANGICI ---
        print("\n🔄 DataFrame için manuel dönüşüm yapılıyor...")
        
        # 1. Sütun isimlerini (ve sırasını) belirle. Bu sıra önemli.
        #    schedule_summary'deki sözlüklerin bu anahtarlara sahip olduğunu biliyoruz.
        columns = [
            "course_id", "course_name", "day", "slot_in_day", 
            "room_name", "expected_students", "duration_minutes"
        ]
        
        # 2. Veriyi 'liste içinde liste' formatına çevir.
        data_as_list_of_lists = []
        for row_dict in schedule_summary:
            # Belirlenen sıraya göre değerleri bir listeye ekle
            row_as_list = [row_dict.get(key, None) for key in columns]
            data_as_list_of_lists.append(row_as_list)
            
        print("✅ Manuel dönüşüm tamamlandı.")

        # 3. DataFrame'i bu yeni, basit yapıdan oluştur.
        #    Sütun isimlerini ayrıca belirt.
        df_schedule = pd.DataFrame(data_as_list_of_lists, columns=columns)
        print("Pandas DataFrame manuel olarak başarıyla oluşturuldu.")
        # --- MANUEL DÖNÜŞÜM SONU ---


        # Sütunları Türkçeye yeniden adlandır
        column_rename_map = {
            "course_id": "Ders ID",
            "course_name": "Ders Adı",
            "day": "Tarih",
            "slot_in_day": "Seans",
            "room_name": "Oda",
            "expected_students": "Öğrenci Sayısı",
            "duration_minutes": "Süre (dk)"
        }
        df_schedule = df_schedule.rename(columns=column_rename_map)
        
        # Olası eksik sütunları doldur ve sırayı garantile
        desired_columns = ["Ders ID", "Ders Adı", "Tarih", "Seans", "Oda", "Öğrenci Sayısı", "Süre (dk)"]
        for col in desired_columns:
            if col not in df_schedule.columns:
                df_schedule[col] = None
        df_schedule = df_schedule[desired_columns]

        slot_names = ["Sabah (09:00-10:15)", "Öğle (11:00-12:15)", "Akşam (14:00-15:15)"]
        room_data = []
        for a in assignments:
            try:
                slot_idx = int(a.get("slot_in_day", 0))
                s_name = slot_names[slot_idx] if slot_idx < 3 else f"Slot {slot_idx + 1}"
                room_data.append([
                    _safe_to_str(a.get("room_name", "")),
                    _safe_to_str(a.get("day", "")),
                    s_name,
                    _safe_to_str(a.get("course_name", "")),
                    int(a.get("expected_students", 0)),
                    f"{int(a.get('duration_minutes', 0))} dk",
                ])
            except Exception as e:
                print(f"⚠️ Oda satırı işlenirken hata: {e}")
                continue
        
        df_room = pd.DataFrame(room_data, columns=["Oda", "Gün", "Seans", "Ders", "Öğrenci Sayısı", "Süre"])

        # 3) Program bilgi sheet
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
            ["Çakışma Kontrolü", "Aktif" if getattr(exam_program, "exam_conflict", True) else "Pasif"],
            ["Toplam Ders", str(len(schedule_summary))],
            ["Hariç Dersler", ", ".join(map(str, exam_program.excluded_courses)) if exam_program.excluded_courses else "Yok"],
        ]
        df_info = pd.DataFrame(info_data, columns=["Alan", "Değer"])

        # 4) Uyarılar sheet
        warn_data = [[_safe_to_str(w)] for w in warnings] if warnings else [["✅ Uyarı yok"]]
        df_warn = pd.DataFrame(warn_data, columns=["Uyarılar"])

        # Yaz
        with pd.ExcelWriter(abs_path, engine="openpyxl") as writer:
            df_schedule.to_excel(writer, sheet_name="Sınav Programı", index=False)
            df_room.to_excel(writer, sheet_name="Oda Bazlı Görünüm", index=False)
            df_info.to_excel(writer, sheet_name="Program Bilgileri", index=False)
            df_warn.to_excel(writer, sheet_name="Uyarılar", index=False)

        print(f"✅ Excel dosyası başarıyla oluşturuldu: {abs_path}")
        return abs_path

    except Exception as e:
        msg = f"❌ Excel oluşturulamadı: {str(e)}"
        warnings.append(msg)
        print(msg)
        import traceback
        print(traceback.format_exc())
        return abs_path