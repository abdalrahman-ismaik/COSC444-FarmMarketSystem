USE school_db;

INSERT INTO students (student_name, major, year_level) VALUES
('Alice', 'Computer Science', 2),
('Bob', 'Information Systems', 3),
('Carol', 'Computer Science', 1),
('David', 'Mathematics', 4),
('Eva', 'Data Science', 2);

INSERT INTO teachers (teacher_name, department) VALUES
('Dr. Smith', 'Computer Science'),
('Prof. Lee', 'Mathematics'),
('Dr. Brown', 'Data Science');

INSERT INTO courses (course_name, teacher_id, credits) VALUES
('Database Systems', 1, 3),
('Data Structures', 1, 3),
('Linear Algebra', 2, 4),
('Machine Learning', 3, 3);

INSERT INTO enrollments (student_id, course_id, semester, grade) VALUES
(1, 1, '2026Spring', 'A'),
(1, 2, '2026Spring', 'B+'),
(2, 1, '2026Spring', 'A-'),
(3, 2, '2026Spring', 'B'),
(4, 3, '2026Spring', 'A'),
(5, 4, '2026Spring', 'A'),
(2, 4, '2026Spring', 'B+');