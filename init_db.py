import mysql.connector
from mysql.connector import Error
import re
import os
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD

def initialize_database():
    print("Checking and initializing database structure...")
    try:
        # Connect without specifying the database
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )

        if not connection.is_connected():
            print("Failed to connect to MySQL server.")
            return

        cursor = connection.cursor()

        # Check if the database dump file exists
        db_file_path = os.path.join(os.path.dirname(__file__), 'database')
        if not os.path.exists(db_file_path):
            print(f"Database dump file not found at {db_file_path}. Skipping initialization.")
            return

        with open(db_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        # Execute statements including INSERT INTO to populate data
        print("Executing schema migrations and inserting pre-configured data...")
        statements = sql_content.split(';')
        
        # Disable foreign key checks to avoid DROP TABLE constraint failures
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        for statement in statements:
            statement = statement.strip()
            if statement:  # Ignore empty statements
                cursor.execute(statement)
                
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        connection.commit()
        print("Database schema successfully verified/initialized!")

    except Error as e:
        print(f"Error while connecting or initializing database: {e}")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    initialize_database()
