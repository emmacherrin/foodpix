import mysql.connector

# Higher-privileged credentials for initial setup (sample root and root password for MySQL-- can be replaced with admin username and password)
setup_user = "root"
setup_password = "root_pwd"

# Connect to MySQL as root
setup_conn = mysql.connector.connect(host="127.0.0.1", user=setup_user, password=setup_password)
setup_cursor = setup_conn.cursor()

# Create a new user for the application without granting privileges
app_user = "test_user"
app_password = "test_password"

# Drop the user if it already exists -- doesn't work without these two lines
setup_cursor.execute(f"DROP USER IF EXISTS '{app_user}'@'127.0.0.1'")
setup_cursor.execute(f"DROP USER IF EXISTS '{app_user}'@'localhost'")

# Create the new user
setup_cursor.execute(f"CREATE USER '{app_user}'@'127.0.0.1' IDENTIFIED BY '{app_password}'")

# Commit the user creation
setup_conn.commit()

# Create the database for the application
app_database = "foodpix_db"
setup_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app_database}")

# Switch to the application database
setup_cursor.execute(f"USE {app_database}")

# Grant privileges on specific database to the user
database_name = "foodpix_db"  # Update the database name here
setup_cursor.execute(f"GRANT ALL PRIVILEGES ON {database_name}.* TO '{app_user}'@'127.0.0.1'")

# Grant privileges to the new user
setup_cursor.execute(f"GRANT ALL PRIVILEGES ON {app_database}.* TO '{app_user}'@'127.0.0.1'")
setup_cursor.execute("FLUSH PRIVILEGES")

# Create the necessary tables
setup_cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id CHAR(36) PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL
    )
''')

setup_cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id CHAR(36) PRIMARY KEY,
        restaurant_name VARCHAR(255) NOT NULL,
        address VARCHAR(255) NOT NULL,
        cuisine VARCHAR(255) NOT NULL,
        latitude FLOAT,
        longitude FLOAT,
        user_id CHAR(36),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

setup_cursor.execute('''
    CREATE TABLE IF NOT EXISTS dishes (
        id CHAR(36) PRIMARY KEY,
        restaurant_id CHAR(36) NOT NULL,
        dish_name VARCHAR(255) NOT NULL,
        image_url VARCHAR(255),
        date DATE,
        stars INT,
        dietary_restrictions TEXT,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
    )
''')

# Commit the changes and close the connection
setup_conn.commit()
setup_conn.close()

print("Initial setup completed successfully.")
