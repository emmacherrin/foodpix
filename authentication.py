
from database_errors import UserError
import mysql.connector, uuid
from werkzeug.security import generate_password_hash, check_password_hash


def create_user(self, db, username, password):
    try:
        password_hash = generate_password_hash(password)
        user_id = str(uuid.uuid4())  # Generate a UUID for the user ID
        with mysql.connector.connect(
            host=db.host,
            user=db.user,  # Use the higher-privileged user
            password=db.password,
            database=db.name
        ) as conn:
            cursor = conn.cursor()

            # Insert the new user into the 'users' table
            cursor.execute('''
                INSERT INTO users (id, username, password)
                VALUES (%s, %s, %s)
            ''', (user_id, username, password_hash))

            # Grant necessary privileges to the new user
            cursor.execute(f"GRANT ALL PRIVILEGES ON {db.name}.* TO '{username}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")

        # Update the current database object with the new user's credentials
        db.user = username
        db.password = password

        return user_id
    except Exception as e:
        raise UserError("create", username, password, user_id, str(e))
    
def authenticate_user(self, db, username, password):
    try:
        with mysql.connector.connect(
            host=db.host,
            user=username,
            password=password,
            database=db.name
        ) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, password FROM users WHERE username = %s', (username,))
            user_data = cursor.fetchone()

            if user_data:
                user_id, hashed_password = user_data
                if check_password_hash(hashed_password, password):
                    return user_id

            db.user = username
            db.password = password
            
            return None  # Authentication failed

    except Exception as e:
        raise UserError("authenticate", user_id, username, password, str(e))
    