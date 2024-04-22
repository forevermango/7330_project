from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os

app = FastAPI()

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



class Degree(BaseModel):
    name: str
    level: str
    name_level: str

@app.post("/add-degree/")
async def add_degree(degree: Degree):
    conn = get_db_connection()
    if conn is None:
        return {"error": "Failed to connect to the database"}
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO degree (name, level, name_level) VALUES (%s, %s, %s)"
        cursor.execute(query, (degree.name, degree.level, degree.name_level))
        conn.commit()
        return {"status": "degree added"}
    except mysql.connector.Error as error:
        conn.rollback()  # Rollback if any exception occurred
        return {"error": str(error)}
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Database connection setup
def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user=db_user,
            passwd=db_password,  # Make sure the password is correct here
            database=db
        )
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None

