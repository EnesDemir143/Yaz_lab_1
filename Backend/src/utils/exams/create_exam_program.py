from Backend.src.utils.exams.ExanProgramClass import ExamProgram
from typing import List
from queue import PriorityQueue

def create_exam_schedule(
    exam_program: ExamProgram,
    class_dict: dict,
    classrooms: list[dict]) -> dict:
    
    classes_by_year = {1: [], 2: [], 3: [], 4: []}

    for class_id, info in class_dict.items():
        year = info.get('year', 0)
        if year in classes_by_year:
            class_data = {
                'id': class_id,
                'name': info.get('class_name', ''),
                'year': year,
                'student_count': len(info.get('students', []))
            }
            classes_by_year[year].append(class_data)

    for year in classes_by_year:
        classes_by_year[year].sort(key=lambda x: x['student_count'], reverse=True)

    for year, classes in classes_by_year.items():
        print(f"Yıl {year}:")
        for c in classes:
            print(f"  - {c['name']} ({c['student_count']} öğrenci)")
    print("\n" + "="*50 + "\n")
    
    final_ordered_list = []
    while any(classes_by_year.values()):
        for year in sorted(classes_by_year.keys()):
            if classes_by_year[year]:
                class_to_add = classes_by_year[year].pop(0)
                final_ordered_list.append(class_to_add)

    classes_queue = PriorityQueue()
    priority_counter = 0

    for class_data in final_ordered_list:
        classes_queue.put((priority_counter, class_data))
        priority_counter += 1

    while not classes_queue.empty():
        priority, data = classes_queue.get()
        print(
            f"Sıra: {priority}, "
            f"Yıl: {data['year']}, "
            f"Ders: {data['name']}, "
            f"Öğrenci: {data['student_count']}"
        )