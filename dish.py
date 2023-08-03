import sqlite3, os, json
class Dish:
    def __init__(self, restaurant_id=None, dish_name=None, image_url=None, date=None, stars=None, dietary_restrictions=None):
        self.restaurant_id = restaurant_id
        self.dish_name = dish_name
        self.image_url = image_url
        self.date = date
        self.stars = stars
        
        # Check if dietary_restrictions is a list or a comma-separated string, and store in a list
        if isinstance(dietary_restrictions, list):
            self.dietary_restrictions = dietary_restrictions
        elif isinstance(dietary_restrictions, str):
            self.dietary_restrictions = [restriction.strip() for restriction in dietary_restrictions.split(',') if restriction.strip()]
        else:
            self.dietary_restrictions = []

    # Method to save the dish to the database
    def save_to_db(self, db):
        # If the database file does not exist, it creates a new one with the specified filename. If the file already exists, it connects to it.
        conn = sqlite3.connect(db.name)
         # Pointer to a specific location in the database and provides methods to perform operations such as executing SQL queries and fetching data from the result.
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO dishes (dish_id, restaurant_id, image_url, dish_name, date, stars, dietary_restrictions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.restaurant_id, self.image_url, self.dish_name, self.date, self.stars, ",".join(self.dietary_restrictions)))
        # Save changes permanently to database
        conn.commit()
        # Close the connection
        conn.close()

    def to_json(self, id):
        data = {
            "id": id,
            "restaurant_id": self.restaurant_id,
            "image_url": self.image_url,
            "dish_name": self.dish_name,
            "date": self.date,
            "stars": self.stars,
            "dietary_restrictions": self.dietary_restrictions
        }
        return json.dumps(data)

