import mysql.connector
from fastapi import HTTPException
from config import config  # Assuming config.py is in the same directory

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user=config.get('DB_USER'),
            password=config.get('DB_PASSWORD'),
            database=config.get('DATABASE')
        )
        return connection
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

def add_entity(entity, table, columns):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            column_names = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            values = tuple(getattr(entity, col) for col in columns)
            query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            return {"status": f"{table[:-1]} added"}  # Simplifies message creation
    finally:
        if conn:
            conn.close()

