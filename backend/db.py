import os
import logging
from contextlib import contextmanager
from werkzeug.security import generate_password_hash
from config import Config

logger = logging.getLogger(__name__)

# Attempt to load mysql.connector; fall back to pymysql if not available
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError, pooling
    USE_PYMYSQL = False
except ImportError:
    try:
        import pymysql
        import pymysql.cursors
        from pymysql import Error as MySQLError
        USE_PYMYSQL = True
    except ImportError:
        raise ImportError(
            "Neither 'mysql-connector-python' nor 'PyMySQL' is installed. "
            "Please run: pip install -r requirements.txt"
        )


def get_db_connection():
    """
    Establishes and returns a connection to MySQL database.
    Raises descriptive exceptions if connection parameters are invalid
    or MySQL server is not reachable.
    """
    try:
        if not USE_PYMYSQL:
            conn = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=False,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
        else:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=False,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        return conn
    except MySQLError as err:
        logger.error(f"MySQL Connection Error: {err}")
        raise ConnectionError(
            f"Failed to connect to MySQL database '{Config.DB_NAME}' at {Config.DB_HOST}:{Config.DB_PORT}. "
            f"Details: {err}. Please verify MySQL service is running and credentials in backend/.env are correct."
        )


@contextmanager
def get_db_cursor(commit=False, dictionary=True):
    """
    Context manager providing a safe database connection and cursor.
    Automatically commits if commit=True and no exception occurs.
    Rolls back transaction on exceptions and guarantees connection closure.
    """
    conn = get_db_connection()
    if not USE_PYMYSQL:
        cursor = conn.cursor(dictionary=dictionary)
    else:
        cursor = conn.cursor()

    try:
        yield conn, cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


def test_connection():
    """
    Verifies database connectivity and returns a status dictionary.
    Used for health checks and startup diagnostics.
    """
    try:
        with get_db_cursor(commit=False) as (conn, cursor):
            cursor.execute("SELECT VERSION() AS db_version, DATABASE() AS current_db;")
            row = cursor.fetchone()
            return {
                "success": True,
                "version": row.get("db_version") if isinstance(row, dict) else row[0],
                "database": row.get("current_db") if isinstance(row, dict) else row[1],
                "connector": "pymysql" if USE_PYMYSQL else "mysql-connector-python"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "connector": "pymysql" if USE_PYMYSQL else "mysql-connector-python"
        }


def ensure_demo_accounts():
    """
    Checks if users exist; if the database has been initialized with schema.sql
    but no admin user exists, safely creates the demo admin and passenger accounts.
    Never drops or recreates existing tables.
    """
    try:
        with get_db_cursor(commit=True) as (conn, cursor):
            # Check if users table exists
            cursor.execute("""
                SELECT COUNT(*) AS cnt 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = 'users';
            """, (Config.DB_NAME,))
            res = cursor.fetchone()
            table_exists = (res.get('cnt') if isinstance(res, dict) else res[0]) > 0
            if not table_exists:
                logger.warning("Tables not found in city_bus_db. Please execute database/schema.sql first.")
                return

            # Check if admin user exists
            cursor.execute("SELECT user_id FROM users WHERE username = 'admin' LIMIT 1;")
            admin_user = cursor.fetchone()
            if not admin_user:
                logger.info("Provisioning default demo admin and passenger accounts...")
                admin_hash = generate_password_hash("Admin@123")
                passenger_hash = generate_password_hash("Passenger@123")

                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role, full_name, phone, is_active)
                    VALUES 
                    ('admin', 'admin@amravaticitybus.in', %s, 'admin', 'Amravati Transport Admin', '9822011223', TRUE),
                    ('rahul_sharma', 'rahul.sharma@example.com', %s, 'passenger', 'Rahul Sharma', '9823145678', TRUE);
                """, (admin_hash, passenger_hash))
                
                # Fetch created passenger user_id
                cursor.execute("SELECT user_id FROM users WHERE username = 'rahul_sharma';")
                p_user = cursor.fetchone()
                p_uid = p_user.get('user_id') if isinstance(p_user, dict) else p_user[0]
                
                cursor.execute("""
                    INSERT IGNORE INTO passengers (user_id, gender, age, address, city, emergency_contact)
                    VALUES (%s, 'male', 24, 'Near Rajapeth Police Station, Amravati', 'Amravati', '9823145600');
                """, (p_uid,))
                logger.info("Demo accounts provisioned successfully.")
    except Exception as e:
        logger.warning(f"Note on demo account verification: {e}")
