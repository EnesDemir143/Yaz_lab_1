CREATE DATABASE IF NOT EXISTS yazlab1
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_turkish_ci;

USE yazlab1;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id VARCHAR(50) UNIQUE NOT NULL,
    class_name VARCHAR(255) NOT NULL,
    year INT NOT NULL,
    is_optional BOOLEAN NOT NULL DEFAULT FALSE,
    teacher VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_num INT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    grade INT NOT NULL,
    department VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

CREATE TABLE IF NOT EXISTS student_classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_num INT NOT NULL,
    class_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (student_num) REFERENCES students(student_num)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE(student_num, class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

CREATE TABLE IF NOT EXISTS classrooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id VARCHAR(50) UNIQUE NOT NULL,
    classroom_name VARCHAR(255) NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    desks_per_row INT NOT NULL,
    desks_per_column INT NOT NULL,
    desk_structure VARCHAR(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
CREATE TABLE IF NOT EXISTS exam_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    exam_type VARCHAR(100) NOT NULL,
    UNIQUE (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

CREATE TABLE IF NOT EXISTS exam_block (
    id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    class_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    exam_start_time TIME NOT NULL,
    exam_end_time TIME NOT NULL,
    duration FLOAT NOT NULL,
    instructor VARCHAR(100) NOT NULL,
    student_count INT NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES exam_schedules(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (schedule_id, class_id, exam_start_time, exam_end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

CREATE TABLE IF NOT EXISTS exam_classrooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    classroom_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exam_block(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (exam_id, classroom_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

CREATE TABLE IF NOT EXISTS exam_students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    student_num INT NOT NULL,
    classroom_id VARCHAR(50),
    FOREIGN KEY (exam_id) REFERENCES exam_block(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (student_num) REFERENCES students(student_num)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    UNIQUE (exam_id, student_num, classroom_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;

CREATE TABLE IF NOT EXISTS exam_seating_plan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    classroom_id VARCHAR(50) NOT NULL,
    student_num INT NOT NULL,
    `row_number` INT NOT NULL,
    column_number INT NOT NULL,
    FOREIGN KEY (exam_id) REFERENCES exam_block(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (student_num) REFERENCES students(student_num)
        ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE (exam_id, classroom_id, `row_number`, column_number),
    UNIQUE (exam_id, student_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;
