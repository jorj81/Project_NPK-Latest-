import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
import bcrypt


def connect_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if connection.is_connected():
            return connection
        return None
    except Error as e:
        print(f"MySQL connection error: {e}")
        return None



def create_user(username, password, contact_number, barangay_id, user_role_id):
    connection = None
    cursor = None

    try:
        # Validate inputs
        if (
            not username
            or not password
            or not contact_number
            or not barangay_id
            or not user_role_id
        ):
            return False, "Username, password, contact number, barangay, and user role are required"

        # Hash password
        password_bytes = password.encode("utf-8")
        hashed_password = bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt()
        )
        hashed_password_str = hashed_password.decode("utf-8")

        # Connect to database
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            INSERT INTO users
            (
                username,
                password_hash,
                contact_number,
                barangay_id,
                user_role_id
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            username,
            hashed_password_str,
            contact_number,
            barangay_id,
            user_role_id
        )

        cursor.execute(query, values)
        connection.commit()

        return True, "User created successfully"

    except Error as e:
        return False, f"MySQL error: {e}"

    except Exception as e:
        return False, f"Error creating user: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def dashboard_users_data():
    connection = None
    cursor = None

    try:
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                u.id,
                u.username,
                u.contact_number,
                u.barangay_id,
                u.user_role_id,
                u.last_seen AS last_activity,

                ur.role_name,

                b.barangay_name,

                cm.city_name,
                cm.type AS city_type,

                p.province_name,

                r.region_name,

                c.name AS country_name

            FROM users u

            LEFT JOIN user_roles ur
                ON u.user_role_id = ur.id

            LEFT JOIN barangays b
                ON u.barangay_id = b.id

            LEFT JOIN cities_municipalities cm
                ON b.city_id = cm.id

            LEFT JOIN provinces p
                ON cm.province_id = p.id

            LEFT JOIN regions r
                ON p.region_id = r.id

            LEFT JOIN countries c
                ON r.country_id = c.id

            ORDER BY u.id DESC
        """

        cursor.execute(query)

        users = cursor.fetchall()

        return True, users

    except Error as e:
        return False, f"MySQL Error: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def delete_user(user_id):
    connection = None
    cursor = None

    try:
        if not user_id:
            return False, "User ID is required"

        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        # Check if user exists
        check_query = """
            SELECT id
            FROM users
            WHERE id = %s
        """

        cursor.execute(check_query, (user_id,))
        user = cursor.fetchone()

        if user is None:
            return False, "User not found"

        # Delete user
        delete_query = """
            DELETE FROM users
            WHERE id = %s
        """

        cursor.execute(delete_query, (user_id,))
        connection.commit()

        return True, "User deleted successfully"

    except Error as e:
        if connection is not None:
            connection.rollback()

        return False, f"MySQL Error: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def get_user_count():

    connection = None
    cursor = None

    try:
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT COUNT(*) AS total_users
            FROM users
        """

        cursor.execute(query)

        result = cursor.fetchone()

        return True, result["total_users"]

    except Error as e:
        return False, f"MySQL Error: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def add_comment(user_id, username, comment):
    connection = None
    cursor = None

    try:
        # Validate inputs
        if not user_id:
            return False, "User ID is required"

        if not username:
            return False, "Username is required"

        if not comment or not comment.strip():
            return False, "Comment cannot be empty"

        # Connect to database
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            INSERT INTO comments
            (
                user_id,
                username,
                comment
            )
            VALUES (%s, %s, %s)
        """

        values = (
            user_id,
            username,
            comment.strip()
        )

        cursor.execute(query, values)
        connection.commit()

        return True, "Comment added successfully"

    except Error as e:
        return False, f"MySQL error: {e}"

    except Exception as e:
        return False, f"Error adding comment: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def edit_comment(comment_id, user_id, comment):
    connection = None
    cursor = None

    try:
        # Validate inputs
        if not comment_id:
            return False, "Comment ID is required"

        if not user_id:
            return False, "User ID is required"

        if not comment or not comment.strip():
            return False, "Comment cannot be empty"

        # Connect to database
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            UPDATE comments
            SET comment = %s
            WHERE id = %s
            AND user_id = %s
        """

        values = (
            comment.strip(),
            comment_id,
            user_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return False, "Comment not found or you are not allowed to edit it"

        return True, "Comment updated successfully"

    except Error as e:
        return False, f"MySQL error: {e}"

    except Exception as e:
        return False, f"Error editing comment: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def delete_comment(comment_id, user_id):
    connection = None
    cursor = None

    try:
        # Validate inputs
        if not comment_id:
            return False, "Comment ID is required"

        if not user_id:
            return False, "User ID is required"

        # Connect to database
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            DELETE FROM comments
            WHERE id = %s
            AND user_id = %s
        """

        values = (
            comment_id,
            user_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            return False, "Comment not found or you are not allowed to delete it"

        return True, "Comment deleted successfully"

    except Error as e:
        return False, f"MySQL error: {e}"

    except Exception as e:
        return False, f"Error deleting comment: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def get_all_comments():

    connection = None
    cursor = None

    try:

        connection = connect_database()

        if connection is None:
            return []

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id,
                user_id,
                username,
                comment,
                created_at,
                updated_at
            FROM comments
            ORDER BY created_at DESC
        """

        cursor.execute(query)

        comments = cursor.fetchall()

        return comments

    except Error as e:

        print(f"Error retrieving comments: {e}")

        return []

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()



def update_user_last_seen(user_id):
    connection = None
    cursor = None

    try:
        # Validate user ID
        if not user_id:
            return False, "User ID is required"

        # Connect to database
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            UPDATE users
            SET last_seen = NOW()
            WHERE id = %s
        """

        cursor.execute(query, (user_id,))
        connection.commit()

        # Check if the user exists
        if cursor.rowcount == 0:
            return False, "User not found"

        return True, "User activity updated successfully"

    except Error as e:
        return False, f"MySQL error: {e}"

    except Exception as e:
        return False, f"Error updating user activity: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

def clear_user_last_seen(user_id):
    connection = None
    cursor = None

    try:
        # Validate user ID
        if not user_id:
            return False, "User ID is required"

        # Connect to database
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            UPDATE users
            SET last_seen = NULL
            WHERE id = %s
        """

        cursor.execute(query, (user_id,))
        connection.commit()

        # Check if the user exists
        if cursor.rowcount == 0:
            return False, "User not found"

        return True, "User activity cleared successfully"

    except Error as e:
        return False, f"MySQL error: {e}"

    except Exception as e:
        return False, f"Error clearing user activity: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_current_sensor_data():
    connection = None
    cursor = None

    try:
        connection = connect_database()

        if connection is None:
            return False, "Database connection failed"

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id,
                timestamp,
                soil_moisture,
                nitrogen,
                phosphorus,
                potassium
            FROM sensor_logs
            ORDER BY timestamp DESC
            LIMIT 1
        """

        cursor.execute(query)

        record = cursor.fetchone()

        if record is None:
            return False, "No sensor data available."

        return True, record

    except Error as e:
        return False, f"MySQL Error: {e}"

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def get_active_user_count():

    connection = None
    cursor = None

    try:

        connection = connect_database()

        if connection is None:

            return False, "Database connection failed"

        cursor = connection.cursor()

        query = """
            SELECT COUNT(*)
            FROM users
            WHERE last_seen >= DATE_SUB(
                NOW(),
                INTERVAL 5 MINUTE
            )
        """

        cursor.execute(query)

        result = cursor.fetchone()

        active_users = result[0] if result else 0

        return True, active_users

    except Exception as e:

        return False, str(e)

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


def get_active_users():

    connection = None
    cursor = None

    try:

        connection = connect_database()

        if connection is None:

            return False, "Database connection failed"

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id,
                username,
                contact_number,
                last_seen
            FROM users
            WHERE last_seen >= DATE_SUB(
                NOW(),
                INTERVAL 5 MINUTE
            )
            ORDER BY last_seen DESC
        """

        cursor.execute(query)

        active_users = cursor.fetchall()

        return True, active_users

    except Exception as e:

        return False, str(e)

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

def get_user_comments(user_id):

    connection = None
    cursor = None

    try:


        if not user_id:

            return False, "User ID is required"


        # ====================================================
        # CONNECT TO DATABASE
        # ====================================================

        connection = connect_database()

        if connection is None:

            return False, "Database connection failed"


        cursor = connection.cursor(dictionary=True)


        # ====================================================
        # GET USER COMMENTS
        # ====================================================

        query = """
            SELECT
                id,
                user_id,
                username,
                comment,
                created_at
            FROM comments
            WHERE user_id = %s
            ORDER BY created_at DESC
        """


        cursor.execute(
            query,
            (user_id,)
        )


        comments = cursor.fetchall()


        return True, comments


    except Error as e:

        return False, f"MySQL error: {e}"


    except Exception as e:

        return False, f"Error getting comments: {e}"


    finally:

        if cursor is not None:

            cursor.close()


        if connection is not None and connection.is_connected():

            connection.close()