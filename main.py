import sqlite3

# Connect to SQLite database (create a new database if it doesn't exist)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Execute SQL commands to create tables
cursor.execute('''
    CREATE TABLE degree (
      degree_name_level VARCHAR(255) PRIMARY KEY,
      name VARCHAR(255),
      level VARCHAR(255),
      name_level VARCHAR(255),
      UNIQUE (name_level)
    )
''')

cursor.execute('''
    CREATE TABLE courses (
      course_number VARCHAR(255) PRIMARY KEY,
      name VARCHAR(255) UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE semester (
      semester_year VARCHAR(255) PRIMARY KEY,
      year INT,
      semester VARCHAR(255)
    )
''')

cursor.execute('''
    CREATE TABLE sections (
      section_number INT PRIMARY KEY,
      number_of_students INT,
      instructor_id INT,
      course_number VARCHAR(255),
      semester_ID VARCHAR(255),
      FOREIGN KEY (instructor_id) REFERENCES instructor (instructor_id),
      FOREIGN KEY (course_number) REFERENCES courses (course_number),
      FOREIGN KEY (semester_ID) REFERENCES semester (semester_year)
    )
''')

cursor.execute('''
    CREATE TABLE sections_courses (
      course_number VARCHAR(255),
      section_number INT,
      number_of_students INT,
      instructor_id INT,
      semester_ID VARCHAR(255),
      course_section VARCHAR(255),
      PRIMARY KEY (course_section),
      FOREIGN KEY (course_number) REFERENCES courses (course_number),
      FOREIGN KEY (instructor_id) REFERENCES instructor (instructor_id),
      FOREIGN KEY (semester_ID) REFERENCES semester (semester_year)
    )
''')

cursor.execute('''
    CREATE TABLE instructor (
      instructor_id INT PRIMARY KEY,
      name VARCHAR(255)
    )
''')

cursor.execute('''
    CREATE TABLE degree_courses (
      degree_courses_ID VARCHAR(255) PRIMARY KEY,
      degree_ID VARCHAR(255),
      course_number VARCHAR(255),
      core_course BOOLEAN,
      FOREIGN KEY (degree_ID) REFERENCES degree (degree_name_level),
      FOREIGN KEY (course_number) REFERENCES courses (course_number)
    )
''')

cursor.execute('''
    CREATE TABLE learning_objectives (
      code INT PRIMARY KEY,
      title VARCHAR(255),
      description TEXT
    )
''')

cursor.execute('''
    CREATE TABLE course_evaluation (
      eval_ID INT PRIMARY KEY,
      section_ID INT,
      objective_code INT,
      eval_criteria VARCHAR(255),
      eval_A_count INT,
      eval_B_count INT,
      eval_C_count INT,
      eval_F_count INT,
      improvements TEXT,
      FOREIGN KEY (section_ID) REFERENCES sections (section_number),
      FOREIGN KEY (objective_code) REFERENCES learning_objectives (code)
    )
''')

cursor.execute('''
    CREATE TABLE course_learning_objective (
      course_learning_objectives_ID VARCHAR(255) PRIMARY KEY,
      course_number VARCHAR(255),
      code INT,
      FOREIGN KEY (course_number) REFERENCES courses (course_number),
      FOREIGN KEY (code) REFERENCES learning_objectives (code)
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Tables created successfully.")
