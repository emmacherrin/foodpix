import sqlite3, os, json, restaurant
from restaurant import Restaurant
from dish import Dish
class DB:
    def __init__(self, name):
        self.name = name
    
    def create_db(self):
        # Create a connection to the SQLite database
        conn = sqlite3.connect(self.name)
        cursor = conn.cursor()

        # Create the "restaurants" table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY,
                restaurant_name TEXT NOT NULL,
                address TEXT NOT NULL,
                cuisine TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                dish_ids TEXT NOT NULL
            )
        ''')

        # Create the "dishes" table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY,
                restaurant_id INTEGER NOT NULL,
                image_url TEXT,
                dish_name TEXT NOT NULL,
                date TEXT,
                stars INTEGER,
                dietary_restrictions TEXT, 
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
            )
        ''')

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        
    def clear_db(self):
        # If the database file already exists, delete it to start fresh
        if os.path.exists(self.name):
            os.remove(self.name)    

    def get_all_restaurants(self):
        # Use context manager for the database connection
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM restaurants")
            restaurants = cursor.fetchall()

            # Convert the list of tuples to a list of Restaurant objects
            restaurant_objects = []
            for restaurant_data in restaurants:
                # Create a Restaurant object and pass the data from the tuple
                restaurant_obj = Restaurant(*restaurant_data)
                # Append the JSON representation of the restaurant to the list
                restaurant_json = restaurant_obj.to_json(restaurant_data[0])
                restaurant_objects.append(restaurant_json)

            return restaurant_objects
    
    def get_all_dishes(self, order="default"):
        conn = sqlite3.connect(self.name)
        cursor = conn.cursor()

        # Use context manager for the database connection
        with sqlite3.connect(self.name) as conn:
            if order.lower() == "date_asc":
                cursor.execute('''
                    SELECT * FROM dishes ORDER BY date ASC
                ''')
            elif order.lower() == "date_desc":
                cursor.execute('''
                    SELECT * FROM dishes ORDER BY date DESC
                ''')
            elif order.lower() == "stars_desc":
                cursor.execute('''
                    SELECT * FROM dishes ORDER BY stars DESC
                ''')
            elif order.lower() == "stars_asc":
                cursor.execute('''
                    SELECT * FROM dishes ORDER BY stars ASC
                ''')
            elif order.lower() == "default":
                cursor.execute('''
                    SELECT * FROM dishes
                ''')
            else:
                raise ValueError("Invalid order parameter. Use 'asc' for ascending or 'desc' for descending.")

            dishes = cursor.fetchall()
            conn.close()

            # Convert the list of tuples to a list of Dish objects
            dishes_list = []
            for dish in dishes:
                dish_obj = Dish(*dish)
                dishes_list.append(dish_obj.to_json(id=dish[0]))

            return dishes_list

    def get_dish(self, dish_id):
        # Use context manager for the database connection
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
        
            # Get the dish where this unique ID in the parameter exists
            cursor.execute('''
                SELECT * FROM dishes WHERE id = ?
            ''', (dish_id,))

            dish_in_db = cursor.fetchone()
        
            # Raise an exception if the dish with this ID can't be found 
            if not dish_in_db:
                raise LookupError(f"Dish with ID {dish_id} not found.")
        
            # Create a Dish object and pass the data from the tuple
            dish_obj = Dish(*dish_in_db)
        
            # Convert the Dish object to a JSON representation
            dish_json = dish_obj.to_json(id=dish_in_db[0])

            return dish_json

    def get_restaraunt(self, restaurant_id):
        # Use context manager for the database connection
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            
            # Get the restaraunt where at this ID
            cursor.execute('''
                    SELECT * FROM restaurants WHERE id = ?
                ''', (restaurant_id,))

            restaurant_in_db = cursor.fetchone()
        
            # Raise an exception if the dish with this ID can't be found 
            if not restaurant_in_db:
                raise LookupError(f"Restaurant with ID {restaurant_id} not found.")
            
            # Save the dish that has been selected as a json dictionary
            restaurant_obj = Restaurant(*restaurant_in_db)
            restaurant_json = restaurant_obj.to_json(id=restaurant_in_db[0])
            
            return restaurant_json
    
    def get_dishes_from_restaraunt(restaraunt_id, self):
        # Use context manager for database connection
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            
            # Get the restaurant so we can access its Dish IDs
            cursor.execute('''
                    SELECT dish_ids FROM restaraunts WHERE id = ?
                ''', (restaraunt_id,))

            # Gets a tuple whose first element is the dish_ids represented as a comma separated string
            dish_ids_tuple = cursor.fetchone()   
            
            # If there are no IDs raise an error-- each restaurant must have a list of dish_ids.
            if len(dish_ids_tuple) == 0:
                raise LookupError("ERROR: There are no dish IDs provided for this restaurant.")
            
            dish_list = []
            
            # Iterate through each dish and add it to the list of dishes for this particular restaurant
            for dish_id in dish_ids_tuple[0].split(","):
                dish_id = dish_id.strip()
                curr_dish = self.get_dish(dish_id)
                dish_list.append(curr_dish)
            
            conn.close()

            # Convert the list of dishes to a JSON formatted string
            return json.dumps(dish_list)
            
    def update_dish(self, dish_id, **kwargs):
        # Build the SQL query dynamically based on the provided keyword arguments
        sql_query = 'UPDATE dishes SET '
        params = []

        # Iterate through each keyword argument, add it to the query and SQL parameter list
        for field, value in kwargs.items():
            sql_query += f'{field} = ?, '
            params.append(value)

        # Remove the trailing comma and space from the query
        sql_query = sql_query.rstrip(', ')

        # Add the WHERE clause to update the specific dish with the given dish_id
        sql_query += ' WHERE id = ?'
        params.append(dish_id)

        # Update the dishes table in the database
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, tuple(params))
            
    def update_restaurant(self, restaurant_id, **kwargs):
        # Build the SQL query dynamically based on the provided keyword arguments
        sql_query = 'UPDATE restaurants SET '
        params = []

        # Iterate through each keyword argument, add it to the query and SQL parameter list
        for field, value in kwargs.items():
            sql_query += f'{field} = ?, '
            params.append(value)

        # Add the WHERE clause to update the specific restaurant with the given restaurant_id
        sql_query += 'WHERE id = ?'
        params.append(restaurant_id)

        # Update the restaurants table in the database
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, tuple(params))                
        
    def add_restaurant(self, restaurant):
        # Add a new restaurant to the 'restaurants' table
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO restaurants (restaurant_name, address, cuisine, latitude, longitude, dish_ids)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (restaurant.restaurant_name, restaurant.address, restaurant.cuisine, restaurant.latitude, restaurant.longitude, ''))  # Initialize dish_ids as an empty string

            # Get the ID of the newly added restaurant
            restaurant_id = cursor.lastrowid

        return restaurant_id

    def add_dish(self, dish):
        # Add a new dish to the 'dishes' table
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO dishes (restaurant_id, image_url, dish_name, date, stars, dietary_restrictions)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (dish.restaurant_id, dish.image_url, dish.dish_name, dish.date, dish.stars, dish.dietary_restrictions))

            # Get the ID of the newly added dish
            dish_id = cursor.lastrowid

        return dish_id