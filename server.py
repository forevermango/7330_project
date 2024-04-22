from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

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
            user='root',
            passwd='<YOUR_PASSWORD>',  # Make sure the password is correct here
            database='project'
        )
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None

