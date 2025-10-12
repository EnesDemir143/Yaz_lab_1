from Backend.src.utils.exams.ExanProgramClass import ExamProgram

def create_exam_schedule(
    exam_program: ExamProgram,
    class_dict: dict,
    classrooms: list[dict]) -> dict:
    