import sqlite3, os, json
from dish import Dish
class Restaurant:
    def __init__(self, name, address, cuisine, latitude=None, longitude=None, dish_ids=None):
        self.name = name
        self.address = address
        self.cuisine = cuisine
        self.latitude = latitude
        self.longitude = longitude
        
         # Check if dish_ids is a list or a comma-separated string and store into list
        if isinstance(dish_ids, list):
            self.dish_ids = dish_ids
        elif isinstance(dish_ids, str):
            self.dish_ids = [dish_id.strip() for dish_id in dish_ids.split(',') if dish_id.strip()]
        else:
            self.dish_ids = []

    # Method to save the restaurant to the database
    def save_to_db(self, db):
        # If the database file does not exist, it creates a new one with the specified filename. If the file already exists, it connects to it.
        conn = sqlite3.connect(db.name)
        # Pointer to a specific location in the database and provides methods to perform operations such as executing SQL queries and fetching data from the result.
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO restaurants (restaurant_name, address, cuisine, latitude, longitude, dish_ids)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.name, self.address, self.cuisine, self.latitude, self.longitude, ",".join(self.dish_ids)))
        # Save changes permanently to database
        conn.commit()
        # Close the conenction
        conn.close()
        
    def to_json(self, id):
        data = {
            "id": id,
            "restaurant_name": self.name,
            "address": self.address,
            "cuisine": self.cuisine,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "dish_ids": self.dish_ids
        }
        return json.dumps(data)


