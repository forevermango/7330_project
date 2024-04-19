
import mysql.connector
from mysql.connector import Error

try:
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host='localhost',          # Host, usually localhost for local server
        user='root',               # Adjust this to your MySQL username
        passwd='<YOUR_PASSWORD>',        # Your MySQL password
        database='project'         # Your database name
    )

    if conn.is_connected():
        cursor = conn.cursor()

        # Execute SQL commands to create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS degree (
              degree_name_level VARCHAR(255) PRIMARY KEY,
              name VARCHAR(255),
              level VARCHAR(255),
              name_level VARCHAR(255),
              UNIQUE (name_level)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
              course_number VARCHAR(255) PRIMARY KEY,
              name VARCHAR(255) UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semester (
              semester_year VARCHAR(255) PRIMARY KEY,
              year INT,
              semester VARCHAR(255)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instructor (
              instructor_id INT PRIMARY KEY,
              name VARCHAR(255)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
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
            CREATE TABLE IF NOT EXISTS sections_courses (
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
            CREATE TABLE IF NOT EXISTS degree_courses (
              degree_courses_ID VARCHAR(255) PRIMARY KEY,
              degree_ID VARCHAR(255),
              course_number VARCHAR(255),
              core_course BOOLEAN,
              FOREIGN KEY (degree_ID) REFERENCES degree (degree_name_level),
              FOREIGN KEY (course_number) REFERENCES courses (course_number)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_objectives (
              code INT PRIMARY KEY,
              title VARCHAR(255),
              description TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_evaluation (
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
            CREATE TABLE IF NOT EXISTS course_learning_objective (
              course_learning_objectives_ID VARCHAR(255) PRIMARY KEY,
              course_number VARCHAR(255),
              code INT,
              FOREIGN KEY (course_number) REFERENCES courses (course_number),
              FOREIGN KEY (code) REFERENCES learning_objectives (code)
            )
        ''')

        # Commit changes
        conn.commit()
        print("Tables created successfully.")

except Error as e:
    print(f"Error: {e}")

finally:
    # Ensure the connection is closed
    if conn and conn.is_connected():
        cursor.close()
        conn.close()
        print("MySQL connection is closed")

