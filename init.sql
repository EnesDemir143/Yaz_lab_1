CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id VARCHAR(50) UNIQUE NOT NULL,
    class_name VARCHAR(255) NOT NULL,
    is_optional BOOLEAN NOT NULL DEFAULT FALSE,
    teacher VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_num INT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    grade INT NOT NULL,
    department VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS student_classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_num INT NOT NULL,
    class_id VARCHAR(50) NOT NULL,
    FOREIGN KEY (student_num) REFERENCES students(student_num),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    UNIQUE(student_num, class_id)
);

CREATE TABLE IF NOT EXISTS classrooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_code VARCHAR(50) UNIQUE NOT NULL,
    classroom_name VARCHAR(255) NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    desks_per_row INT NOT NULL,
    desks_per_column INT NOT NULL,
    desk_structure VARCHAR(10) NOT NULL
);
