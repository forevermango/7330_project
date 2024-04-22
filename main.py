
import mysql.connector
from mysql.connector import Error
import os

def load_config(file_path):
    """Load configuration from a text file into environment variables."""
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Strip whitespace and ignore lines that are empty or start with a comment
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        print("Configuration file not found.")
    except Exception as e:
        print(f"An error occurred while reading the configuration file: {e}")

# Usage
load_config('config.txt')

# Now you can access the variables as environment variables
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db = os.getenv('DATABASE')

try:
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host='localhost',          # Host, usually localhost for local server
        user=db_user,               # Adjust this to your MySQL username
        passwd=db_password,        # Your MySQL password
        database=db         # Your database name
    )

    if conn.is_connected():
        cursor = conn.cursor()

        # Execute SQL commands to create tables
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS degrees (
                name VARCHAR(255),
                level VARCHAR(255),
                name_level VARCHAR(255) AS (CONCAT(name, ' ', level)) STORED PRIMARY KEY,
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
            CREATE TABLE IF NOT EXISTS semesters (
                semester_year VARCHAR(255) AS (CONCAT(year, ' ', semester)) STORED PRIMARY KEY,
                year INT,
                semester VARCHAR(255)
            )
        ''')

        # Insert semesters for Fall and Spring 2024
        cursor.execute('''
            INSERT INTO semesters (year, semester) VALUES (2024, 'Fall'), (2024, 'Spring')
            ON DUPLICATE KEY UPDATE year=VALUES(year), semester=VALUES(semester)
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS instructors (
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
              semester_year VARCHAR(255),
              FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id),
              FOREIGN KEY (course_number) REFERENCES courses (course_number),
              FOREIGN KEY (semester_year) REFERENCES semesters (semester_year)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections_courses (
              course_number VARCHAR(255),
              section_number INT,
              number_of_students INT,
              instructor_id INT,
              semester_year VARCHAR(255),
              course_section VARCHAR(255),
              PRIMARY KEY (course_section),
              FOREIGN KEY (course_number) REFERENCES courses (course_number),
              FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id),
              FOREIGN KEY (semester_year) REFERENCES semesters (semester_year)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS degree_courses (
              degree_courses_ID VARCHAR(255) PRIMARY KEY,
              degree_ID VARCHAR(255),
              course_number VARCHAR(255),
              core_course BOOLEAN,
              FOREIGN KEY (degree_ID) REFERENCES degrees (name_level),
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
            CREATE TABLE IF NOT EXISTS course_evaluations (
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
          CREATE TABLE IF NOT EXISTS course_learning_objectives(
            course_number VARCHAR(255),
            objective_code INT,
            PRIMARY KEY (course_number, objective_code),
            FOREIGN KEY (course_number) REFERENCES courses (course_number),
            FOREIGN KEY (objective_code) REFERENCES learning_objectives (code)
            );
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

