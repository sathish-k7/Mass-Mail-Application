import mysql.connector
from mysql.connector import pooling
import bcrypt
import os
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self._connection_pool = None
        self._init_connection_pool()

    def _init_connection_pool(self):
        """Initialize a connection pool"""
        try:
            self._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="user_app_pool",
                pool_size=5,
                host="localhost",
                user="root",
                password="Sath2005@",  # Ensure this is correct
                database="data"
            )
        except mysql.connector.Error as err:
            if err.errno == 1049:  # ER_BAD_DB_ERROR
                self._create_database()
                self._init_connection_pool()
            elif err.errno == 1045:  # Access denied
                logger.error(f"Access denied: Check your MySQL credentials or configuration")
                raise
            elif err.errno == 2059:  # Authentication error
                logger.error("Authentication error, ensure your MySQL version supports 'caching_sha2_password'")
                raise
            else:
                logger.error(f"Error initializing connection pool: {err}")
                raise

    def _create_database(self):
        """Create database if it doesn't exist"""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="your_password"  # Ensure this is correct
            )
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS data")
            connection.commit()
        except mysql.connector.Error as err:
            logger.error(f"Error creating database: {err}")
        finally:
            if connection:
                cursor.close()
                connection.close()

    def _get_connection(self):
        """Get a connection from the pool"""
        try:
            return self._connection_pool.get_connection()
        except mysql.connector.Error as err:
            logger.error(f"Error getting connection: {err}")
            return None

    def init_db(self):
        """Initialize database tables"""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    username VARCHAR(255) UNIQUE,
                                    password VARCHAR(255),
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                  )''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS email_stats (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    status VARCHAR(50),
                                    count INT DEFAULT 0,
                                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                                  )''')
                connection.commit()
                logger.info("Database tables initialized successfully")
            except mysql.connector.Error as err:
                logger.error(f"Error creating tables: {err}")
            finally:
                if cursor:
                    cursor.close()
                connection.close()

    def validate_password(self, password):
        """
        Validate password complexity:
        - At least 8 characters long
        - Contains at least one uppercase, one lowercase, one number
        """
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

    def add_user(self, username, password):
        """Add a new user to the database"""
        if not self.validate_password(password):
            logger.warning("Password does not meet complexity requirements")
            return False

        connection = self._get_connection()
        if connection:
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                               (username, hashed_password))
                connection.commit()
                logger.info(f"User {username} added successfully")
                return True
            except mysql.connector.IntegrityError:
                logger.warning(f"Username {username} already exists")
                return False
            except mysql.connector.Error as err:
                logger.error(f"Error adding user: {err}")
                return False
            finally:
                if connection:
                    cursor.close()
                    connection.close()

    def get_user(self, username):
        """Retrieve user details"""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                return {"username": user[0], "password": user[1]} if user else None
            except mysql.connector.Error as err:
                logger.error(f"Error fetching user details: {err}")
                return None
            finally:
                if connection:
                    cursor.close()
                    connection.close()

    def check_password(self, stored_password, entered_password):
        """Check if entered password matches stored password"""
        try:
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password)
        except Exception as err:
            logger.error(f"Error checking password: {err}")
            return False

    def update_email_stats(self, status):
        """Update email sending statistics"""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO email_stats (status, count) 
                    VALUES (%s, 1) 
                    ON DUPLICATE KEY UPDATE count = count + 1
                """, (status,))
                connection.commit()
                logger.info(f"Updated email stats for status: {status}")
            except mysql.connector.Error as err:
                logger.error(f"Error updating email stats: {err}")
            finally:
                if connection:
                    cursor.close()
                    connection.close()

    def get_email_stats(self):
        """Retrieve email statistics"""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT status, count FROM email_stats")
                stats = cursor.fetchall()
                return {status: count for status, count in stats}
            except mysql.connector.Error as err:
                logger.error(f"Error fetching email stats: {err}")
                return {}
            finally:
                if connection:
                    cursor.close()
                    connection.close()
        return {}

# Instantiate the DatabaseManager
db_manager = DatabaseManager()

# Initialize the database
db_manager.init_db()

# Expose key methods
def add_user(username, password):
    return db_manager.add_user(username, password)

def get_user(username):
    return db_manager.get_user(username)

def check_password(stored_password, entered_password):
    return db_manager.check_password(stored_password, entered_password)

def get_email_stats():
    return db_manager.get_email_stats()
