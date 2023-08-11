import sqlite3, os, json, models.restaurant as restaurant, utility
from models.restaurant import Restaurant
from models.dish import Dish
class DB:
    def __init__(self, name):
        self.name = name
        self.create_db()
        
    def create_db(self):
        # Create a connection to the SQLite database
        conn = sqlite3.connect(self.name)
        cursor = conn.cursor()

        # Create the "restaurants" table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id TEXT PRIMARY KEY,
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
                id TEXT PRIMARY KEY,
                restaurant_id INTEGER NOT NULL,
                dish_name TEXT NOT NULL,
                image_url TEXT,
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

            # Convert the list of tuples to a list of JSON representations
            restaurant_objects = []
            for restaurant_data in restaurants:
                restaurant_id = restaurant_data[0]  # Assuming ID is the first column
                # Use the get_restaurant function to retrieve the restaurant object
                restaurant_object = self.get_restaurant(restaurant_id)
                restaurant_objects.append(restaurant_object)

            return restaurant_objects
    
    def get_all_dishes(self, order="default"):
        # Use context manager for the database connection
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
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
            
            # Convert the list of tuples to a list of Dish objects
            dishes_list = []
            for dish in dishes:
                dish_obj = Dish(*dish)
                dishes_list.append(dish_obj)

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

            if dish_in_db is None:
                raise ValueError(f"Dish with ID {dish_id} not found in the database")

            # Unpack the dish data
            dish_id, restaurant_id, image_url, dish_name, date, stars, dietary_restrictions = dish_in_db

            # Create a Dish object
            return Dish(id=dish_id, restaurant_id=restaurant_id, image_url=image_url,
                        dish_name=dish_name, date=date, stars=stars,
                        dietary_restrictions=utility.listify(dietary_restrictions))

    
    def get_restaurant(self, restaurant_id):
        """Retrieve details of a restaurant with the provided ID
    
        Args:
            restaurant_id (str): The ID of the restaurant to retrieve.
            
        Returns:
            dict: A dictionary containing the details of the retrieved restaurant.
            
        Raises:
            LookupError: If the specified restaurant ID does not exist in the database.
        """
        
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
            
            # Return this restaurant object
            return Restaurant(*restaurant_in_db)
   
    
    def get_dishes_from_restaraunt(self, restaurant_id):
        """Returns a list of dishes associated with a given restaurant ID.
    
        Args:
            restaurant_id (str): The ID of the restaurant from which to retrieve dishes.
            
        Returns:
            List: A list of dishes associated with the restaurant.
            
        Raises:
            ValueError: If the specified restaurant ID does not exist in the database.
            LookupError: If the restaurant does not have any associated dish IDs.
        """
        
        # Use context manager for database connection
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            
            # Get the restaurant so we can access its Dish IDs
            cursor.execute('''
                    SELECT dish_ids FROM restaurants WHERE id = ?
                ''', (restaurant_id,))
            
            dish_ids_tuple = cursor.fetchone()   

            if dish_ids_tuple is None:
                raise ValueError(f"Dish with ID {dish_id} not found in the database")

            # Gets a tuple whose first element is the dish_ids represented as a comma separated string
            
            # If there are no IDs raise an error-- each restaurant must have a list of dish_ids.
            if len(dish_ids_tuple) == 0:
                raise LookupError("ERROR: There are no dish IDs provided for this restaurant.")
            
            dish_list = []
            
            # Iterate through each dish and add it to the list of dishes for this particular restaurant
            for dish_id in dish_ids_tuple[0].split(","):
                # First ID will be empty, so continue to next iteration with real ID
                if dish_id == "":
                    continue
                dish_id = dish_id.strip()
                curr_dish = self.get_dish(dish_id)
                dish_list.append(curr_dish)

            # Return the list of dishes
            return dish_list
                
    def update_dish(self, dish_id, **kwargs):
        # Build the SQL query dynamically based on the provided keyword arguments
        sql_query = 'UPDATE dishes SET '
        params = []

        # Iterate through each keyword argument, add it to the query and SQL parameter list
        for field, value in kwargs.items():
            if field == 'dietary_restrictions':
                # If the field is 'dietary_restrictions', stringify the value 
                value = utility.stringify(value)
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

        # Remove the trailing comma and space from the query
        sql_query = sql_query.rstrip(', ')

        # Add the WHERE clause to update the specific restaurant with the given restaurant_id
        sql_query += ' WHERE id = ?'
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
                INSERT INTO restaurants (id, restaurant_name, address, cuisine, latitude, longitude, dish_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (restaurant.id, restaurant.name, restaurant.address, restaurant.cuisine, str(restaurant.latitude), str(restaurant.longitude), ''))  # Initialize dish_ids as an empty string
            
        return restaurant.id

    def add_dish(self, dish):
        # Add a new dish to the 'dishes' table
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO dishes (id, restaurant_id, image_url, dish_name, date, stars, dietary_restrictions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (dish.id, dish.restaurant_id, dish.image_url, dish.dish_name, dish.date, str(dish.stars), utility.stringify(dish.dietary_restrictions)))

        # Update the 'dish_ids' of the corresponding restaurant if the dish ID is not already in the list
        with sqlite3.connect(self.name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT dish_ids FROM restaurants WHERE id = ?', (dish.restaurant_id,))
            existing_dish_ids = cursor.fetchone() # Gets a tuple with the existing dish IDs

            # Convert existing_dish_ids to a list using the listify utility function
            dish_id_list = utility.listify(existing_dish_ids)
            
            # Remove any NONE dish ids so there aren't any stray commas
            dish_id_list = [dish_id for dish_id in dish_id_list if dish_id]

            # Check if the dish ID is already in the list
            if str(dish.id) not in dish_id_list:
                dish_id_list.append(str(dish.id))
                
            # Join the updated dish_ids list back into a comma-separated string using the stringify utility function
            updated_dish_ids = utility.stringify(dish_id_list)

            # Update the 'dish_ids' of the restaurant
            cursor.execute('UPDATE restaurants SET dish_ids = ? WHERE id = ?', (updated_dish_ids, dish.restaurant_id))

        return dish.id

