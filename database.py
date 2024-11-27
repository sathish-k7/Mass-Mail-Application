import mysql.connector
from mysql.connector import pooling
import bcrypt
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
        """Initialize a connection pool."""
        try:
            self._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="user_app_pool",
                pool_size=5,
                host="localhost",
                user="root",
                password="Sath2005@",  # Update with your actual password
                database="data"
            )
        except mysql.connector.Error as err:
            if err.errno == 1049:  # ER_BAD_DB_ERROR
                self._create_database()
                self._init_connection_pool()
            else:
                logger.error(f"Error initializing connection pool: {err}")
                raise

    def _create_database(self):
        """Create database if it doesn't exist."""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Sath2005@"  # Update with your actual password
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
        """Get a connection from the pool."""
        try:
            return self._connection_pool.get_connection()
        except mysql.connector.Error as err:
            logger.error(f"Error getting connection: {err}")
            return None

    def init_db(self):
        """Initialize database tables for users and email statistics."""
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
                logger.info("Database tables initialized successfully.")
            except mysql.connector.Error as err:
                logger.error(f"Error creating tables: {err}")
            finally:
                if connection:
                    cursor.close()
                    connection.close()

    def init_contacts_table(self):
        """Create the contacts table if it doesn't exist."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contacts (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL UNIQUE
                    )
                """)
                connection.commit()
            except mysql.connector.Error as err:
                logger.error(f"Error creating contacts table: {err}")
            finally:
                connection.close()

    def init_templates_table(self):
        """Create the templates table if it doesn't exist."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS templates (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        content TEXT NOT NULL
                    )
                """)
                connection.commit()
            except mysql.connector.Error as err:
                logger.error(f"Error creating templates table: {err}")
            finally:
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
        """Add a new user to the database."""
        if not self.validate_password(password):
            logger.warning("Password does not meet complexity requirements.")
            return False

        connection = self._get_connection()
        if connection:
            try:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                               (username, hashed_password))
                connection.commit()
                logger.info(f"User {username} added successfully.")
                return True
            except mysql.connector.IntegrityError:
                logger.warning(f"Username {username} already exists.")
                return False
            except mysql.connector.Error as err:
                logger.error(f"Error adding user: {err}")
                return False
            finally:
                connection.close()

    def get_user(self, username):
        """Retrieve user details."""
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
                connection.close()

    def check_password(self, stored_password, entered_password):
        """Check if entered password matches stored password."""
        try:
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password)
        except Exception as err:
            logger.error(f"Error checking password: {err}")
            return False

    def update_email_stats(self, status):
        """Update email sending statistics."""
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
                connection.close()

    def get_email_stats(self):
        """Retrieve email statistics."""
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
                connection.close()

    def fetch_all_contacts(self):
        """Retrieve all contacts."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT id, name, email FROM contacts")
                return cursor.fetchall()
            finally:
                connection.close()

    def add_contact(self, name, email):
        """Add a new contact."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO contacts (name, email) VALUES (%s, %s)", (name, email))
                connection.commit()
            finally:
                connection.close()

    def delete_contact(self, contact_id):
        """Delete a contact by ID."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
                connection.commit()
            finally:
                connection.close()

    def fetch_all_templates(self):
        """Retrieve all templates."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT id, name, content FROM templates")
                return cursor.fetchall()
            finally:
                connection.close()

    def add_template(self, name, content):
        """Add a new template."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO templates (name, content) VALUES (%s, %s)", (name, content))
                connection.commit()
            finally:
                connection.close()

    def update_template(self, template_id, name, content):
        """Update an existing template."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE templates 
                    SET name = %s, content = %s 
                    WHERE id = %s
                """, (name, content, template_id))
                connection.commit()
            finally:
                connection.close()

    def delete_template(self, template_id):
        """Delete a template by ID."""
        connection = self._get_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM templates WHERE id = %s", (template_id,))
                connection.commit()
            finally:
                connection.close()


# Instantiate the DatabaseManager
db_manager = DatabaseManager()

# Ensure all tables are initialized
db_manager.init_db()
db_manager.init_contacts_table()
db_manager.init_templates_table()

# Expose key methods as standalone functions
def add_user(username, password):
    return db_manager.add_user(username, password)

def get_user(username):
    return db_manager.get_user(username)

def check_password(stored_password, entered_password):
    return db_manager.check_password(stored_password, entered_password)

def get_email_stats():
    return db_manager.get_email_stats()

def add_contact(name, email):
    return db_manager.add_contact(name, email)

def fetch_all_contacts():
    return db_manager.fetch_all_contacts()

def add_template(name, content):
    return db_manager.add_template(name, content)

def fetch_all_templates():
    return db_manager.fetch_all_templates()
