import sqlite3, os, json, utility
from models import Restaurant
from models import Dish
from database_errors import RestaurantNotFoundError, DishNotFoundError, DuplicateDishError, DuplicateRestaurantError, DatabaseQueryError
class DB:
    def __init__(self, name):
        self.name = name
        self.create_db()
        self.all_restaurants = {} # Dictionary of with key restaurant ID and value set containing each dish id correspondign to the restaurant
            
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
        try:
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
        except Exception as e:
            raise DatabaseQueryError("Retrieve all restaurants from database", e)
    
    def get_all_dishes(self, order="default"):
        try:
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
        except Exception as e:
            raise DatabaseQueryError("Retrieve all dishes from database", str(e))
        
    def get_dish(self, dish_id):
        # If the dish is not in the database, don't even try to fetch it
        if not self.util_dish_in_db(dish_id):
            raise DishNotFoundError(dish_id)

        try:
            # Use context manager for the database connection
            with sqlite3.connect(self.name) as conn:
                cursor = conn.cursor()

                # Get the dish where this unique ID in the parameter exists
                cursor.execute('''
                    SELECT * FROM dishes WHERE id = ?
                ''', (dish_id,))

                dish_in_db = cursor.fetchone()

                # Unpack the dish data
                dish_id, restaurant_id, image_url, dish_name, date, stars, dietary_restrictions = dish_in_db

                # Create a Dish object
                return Dish(id=dish_id, restaurant_id=restaurant_id, image_url=image_url,
                            dish_name=dish_name, date=date, stars=stars,
                            dietary_restrictions=utility.listify(dietary_restrictions))
        except Exception as e:
            raise DatabaseQueryError(f"Retrieve dish with ID {dish_id} from database", str(e))

    def get_restaurant(self, restaurant_id):
        # Make sure the restaurant is in the database
        if not self.util_restaurant_in_db(restaurant_id):
            raise RestaurantNotFoundError(restaurant_id)
            
        try:
            # Use context manager for the database connection
            with sqlite3.connect(self.name) as conn:
                cursor = conn.cursor()
                
                # Get the restaurant with this ID
                cursor.execute('''
                    SELECT * FROM restaurants WHERE id = ?
                ''', (restaurant_id,))

                restaurant_in_db = cursor.fetchone()
                
                # Return this restaurant object
                return Restaurant(*restaurant_in_db)
        except Exception as e:
            raise DatabaseQueryError(f"Retrieve restaurant {restaurant_id} from database", str(e))
    
    def get_dishes_from_restaurant(self, restaurant_id):
        # Make sure the restaurant is in the database
        if not self.util_restaurant_in_db(restaurant_id):
            raise RestaurantNotFoundError(restaurant_id)
        try:
            dish_ids = self.all_restaurants.get(restaurant_id, set())  # Get the set of dish IDs for the restaurant
            
            dish_list = []
            
            for dish_id in dish_ids:
                curr_dish = self.get_dish(dish_id)
                dish_list.append(curr_dish)
            
            return dish_list
        except Exception as e:
            raise DatabaseQueryError(f"Retrieve dishes from restaurant {restaurant_id} in database", str(e))
    
    def update_dish(self, dish_id, **kwargs):
        # Make sure the dish is in the database
        if not self.util_dish_in_db(dish_id):
            raise DishNotFoundError(dish_id)
        try:     
            # If a 'restaurant_id' is specified to update the dish with, make sure it exists
            if 'restaurant_id' in kwargs and self.util_restaurant_in_db(kwargs['restaurant_id']) is False:
                raise RestaurantNotFoundError()
            # Build the SQL query dynamically based on the provided keyword arguments
            sql_query = 'UPDATE dishes SET '
            params = []

            # User can't update the dish's ID
            if 'id' in kwargs():
                raise KeyError("ERROR: User is not allowed to update the dish 'id'")
            
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
        except Exception as e:
            #Make a dictionary containing keyword arguments and cast to a string
            kwargs_str = json.dumps({field: value for field, value in kwargs.items()}) 
            raise DatabaseQueryError(f"Update dish {dish_id} in database with fields: {kwargs_str}", str(e))
              
    def update_restaurant(self, restaurant_id, **kwargs):
        # Make sure the restaurant is in the database
        if not self.util_restaurant_in_db(restaurant_id):
            raise RestaurantNotFoundError(restaurant_id)
            
        try:
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
                cursor.execute(sql_query, params)
        except Exception as e:
            # Make a dictionary containing keyword arguments and cast to a string
            kwargs_str = json.dumps({field: value for field, value in kwargs.items()})
            raise DatabaseQueryError(f"Update restaurant {restaurant_id} in database with fields: {kwargs_str}", str(e))

    
    def add_restaurant(self, restaurant):
        # Don't add the restaurant if it was already added
        if self.util_restaurant_in_db(restaurant.id) is True:
            raise DuplicateRestaurantError(restaurant.id)
        
        try:
            # Add this restaurant to the dict containing all restaurants and validate that it isn't already in the database
            self.all_restaurants[restaurant.id] = set()

            # Add a new restaurant to the 'restaurants' table
            with sqlite3.connect(self.name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO restaurants (id, restaurant_name, address, cuisine, latitude, longitude, dish_ids)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (restaurant.id, restaurant.name, restaurant.address, restaurant.cuisine, str(restaurant.latitude), str(restaurant.longitude), ''))  # Initialize dish_ids as an empty string
                
            return restaurant.id
        except Exception as e:
            raise DatabaseQueryError("Insert restaurant with ID {restaurant.id} into the database", e)

    def add_dish(self, dish):
        # If dish was already added to the database, raise error
        if self.util_dish_in_db(dish.id):
            raise DuplicateDishError(dish.id)
        
        # Verify that the restaurant exists that we are trying to add to
        if not self.util_restaurant_in_db(dish.restaurant_id):
            raise RestaurantNotFoundError(dish.restaurant_id)
        
        try:
            # Add a new dish to the 'dishes' table
            with sqlite3.connect(self.name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO dishes (id, restaurant_id, image_url, dish_name, date, stars, dietary_restrictions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (dish.id, dish.restaurant_id, dish.image_url, dish.dish_name, dish.date, str(dish.stars), utility.stringify(dish.dietary_restrictions)))
        except Exception as e:
            raise DatabaseQueryError(f"Insert dish with ID {dish.id} to the database", e)
        
        try:        
            # Update the 'dish_ids' of the corresponding restaurant using the all_restaurants member variable
            with sqlite3.connect(self.name) as conn:
                cursor = conn.cursor()
                
                # Get the set of dish_ids for the restaurant
                restaurant_dish_ids = self.all_restaurants.get(dish.restaurant_id, set())
                
                # Add the new dish_id to the set of dish_ids for this restaurant
                restaurant_dish_ids.add(dish.id)
                
                # Convert the set back to a comma-separated string
                updated_dish_ids = ", ".join(restaurant_dish_ids)

                # Update the 'dish_ids' of the restaurant
                cursor.execute('UPDATE restaurants SET dish_ids = ? WHERE id = ?', (updated_dish_ids, dish.restaurant_id))
                
                return dish.id
        except Exception as e:
            raise DatabaseQueryError(f"Update 'dish_ids' list for restaurant {dish.restaurant_id} by inserting dish id {dish.id}", e)

    def delete_dish(self, dish_id):
        if self.util_dish_in_db is False:
            raise DishNotFoundError(dish_id)
        try:
            # Retrieve the dish to be deleted
            dish = self.get_dish(dish_id)
            
            # Delete the dish from the 'dishes' table
            with sqlite3.connect(self.name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))

            # Update the 'dish_ids' of the corresponding restaurant using the update_restaurant method
            self.all_restaurants[dish.restaurant_id].remove(dish_id)
            updated_dish_ids_str = ", ".join(self.all_restaurants[dish.restaurant_id])
            self.update_restaurant(restaurant_id=dish.restaurant_id, dish_ids=updated_dish_ids_str)
            

        except Exception as e:
            raise DatabaseQueryError(f"Delete dish with ID {dish_id}", e)
    
    def delete_restaurant(self, restaurant_id):
        try:
            # Check if the restaurant exists
            if not self.util_restaurant_in_db(restaurant_id):
                raise RestaurantNotFoundError(restaurant_id)

            # Delete the dishes associated with the restaurant - create a copy of the set so we can safely delete without set changed size error
            dish_ids_to_delete = set(self.all_restaurants[restaurant_id])
            for dish_id in dish_ids_to_delete:
                self.delete_dish(dish_id)

            # Delete the restaurant from the 'restaurants' table
            with sqlite3.connect(self.name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM restaurants WHERE id = ?", (restaurant_id,))

            # Remove the restaurant from the all_restaurants dictionary
            del self.all_restaurants[restaurant_id]
        except Exception as e:
            raise DatabaseQueryError(f"Delete restaurant with ID {restaurant_id}", e)    
    
    def custom_query(self, table_name, conditions, order_by=None, parameters=None):
        """
        Retrieve rows from the specified table based on the provided conditions and optional sorting.

        Args:
            table_name (str): Name of the table to query. (MUST be either 'restaurants' or 'dishes')
            conditions (List[str]): List of SQL WHERE clause conditions, e.g., ["stars = ?", "cuisine = ?"].
            order_by (str, optional): Column to sort by and sorting direction, e.g., "stars DESC". Default is None.
            parameters (tuple, optional): Values to replace placeholders in conditions, e.g., (4, "Italian").

        Returns:
            List[object]: List of objects representing the retrieved rows.

        Example:
            # Retrieve all dishes with 4 or more stars
            conditions = ["stars >= ?"]
            parameters = (4,)
            result = custom_query('dishes', conditions, parameters=parameters)
            for dish in result:
                print(dish.dish_name, dish.stars)

            # Retrieve Italian dishes with 3 or more stars, sorted by stars in descending order
            conditions = ["cuisine = ?", "stars >= ?"]
            parameters = ("Italian", 3)
            order_by = "stars DESC"
            result = custom_query('dishes', conditions, order_by=order_by, parameters=parameters)
            for dish in result:
                print(dish.dish_name, dish.stars)

            # Retrieve dishes with 'Main St' in their address, sorted by dish name in ascending order
            conditions = ["address LIKE ?"]
            parameters = ("%Main St%",)
            order_by = "dish_name ASC"
            result = custom_query('dishes', conditions, order_by=order_by, parameters=parameters)
            for dish in result:
                print(dish.dish_name, dish.address)

            # Retrieve dishes with multiple dietary restrictions, i.e., vegetarian and gluten-free
            conditions = ["dietary_restrictions LIKE ?", "dietary_restrictions LIKE ?"]
            parameters = ("%vegetarian%", "%gluten-free%")
            result = custom_query('dishes', conditions, parameters=parameters)
            for dish in result:
                print(dish.dish_name, dish.dietary_restrictions)

        """
        query = f'''
            SELECT *
            FROM {table_name}
            WHERE {' AND '.join(conditions)}
        '''
        if order_by:
            query += f' ORDER BY {order_by}'
        
        try:
            with sqlite3.connect(self.name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, parameters)
                
                # Instantiate list of items based on object type indicated by tablename
                if table_name == 'restaurants':
                    result = [Restaurant(*row) for row in cursor.fetchall()]
                elif table_name == 'dishes':
                    result = [Dish(*row) for row in cursor.fetchall()]
                else:
                    raise ValueError(f"Unsupported table name: {table_name}")

            return result
        except Exception as e:
            raise DatabaseQueryError(f"Query table with query {query}", e)

    def util_restaurant_in_db(self, restaurant_id_in) -> bool:
        # Iterate through each restaurant ID (key)
        for restaurant_id in self.all_restaurants:
            if restaurant_id == restaurant_id_in:
                return True # The restaurant does exist in the database
                
        return False # The restaurant does NOT exist in the database
                    
    def util_dish_in_db(self, dish_id_in) -> bool:
        # Iterate through each "row" of the dict-- each restaurant and its affiliate dish IDs
        for restaurant_ids, dish_ids in self.all_restaurants.items():
            # Iterate through each corresponding dish ID for this restaurant
            if (dish_ids is not None):
                for dish_id in dish_ids:
                    if dish_id == dish_id_in:
                        return True # The dish does exist in the database
        return False # The dish does NOT exist in the database
    