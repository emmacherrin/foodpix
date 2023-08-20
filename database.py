import mysql.connector
import json, uuid
from models import Restaurant
from models import Dish
from database_errors import RestaurantNotFoundError, DishNotFoundError, DuplicateDishError, DuplicateRestaurantError, DatabaseQueryError
from utils.utility import listify, stringify


class DB:
    """Database handler for managing restaurant and dish data.

    This class provides methods to interact with an SQLite database containing restaurant and dish information.
    It allows for CRUD (Create, Read, Update, Delete) operations on the database.

    Args:
        name (str): The name of the SQLite database.

    Attributes:
        name (str): The name of the SQLite database.
        all_restaurants (dict): A dictionary with restaurant IDs as keys and sets of dish IDs as values.

    Example:
        db = DB("restaurant_app.db")
    """ 
    def __init__(self, host, name, user=None, password=None):
        self.host = host
        self.user = user
        self.password = password
        self.name = name
        self.create_db()
        self.all_restaurants = {}
    
    def create_db(self):
        """Create the necessary tables in the database if they don't already exist.

        This method automatically creates the 'restaurants', 'dishes' and 'users' tables in the MySQL database
        if they are not already present. 

        Args:
            None

        Returns:
            None
        
        Note:
            - This method is automatically invoked when creating a new instance of the DB class.
              There's typically no need to call it directly.
            - Each restaurant is affiliated with a user_id, but each dish is not. To access the user_id 
              affiliated with a dish, you must access the dish's restuarant, then the user_id affiliated 
              with that restuarant.
            
        """
        try:
            # Create a connection to the MySQL database
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.name)
            cursor = conn.cursor()

            # Create the "users" table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id CHAR(36) PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
            ''')

            # Create the "restaurants" table if it doesn't exist
            cursor.execute('''
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

            # Create the "dishes" table if it doesn't exist
            cursor.execute('''
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
            conn.commit()
            conn.close()

        except Exception as e:
            raise DatabaseQueryError("Create tables in database", str(e))
                
    def clear_db(self):
        """Delete the database file.

        This method checks if the database file with the provided name already exists,
        and if it does, it deletes the file. This action effectively clears the database,
        providing a new, empty starting point.

        Args:
            None

        Returns:
            None
        """
        try:
            # Create a connection to the MySQL database
            conn = mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.name)
            cursor = conn.cursor()

            # Drop the "dishes" table if it exists
            cursor.execute("DROP TABLE IF EXISTS dishes")

            # Drop the "restaurants" table if it exists
            cursor.execute("DROP TABLE IF EXISTS restaurants")
            
            # Drop the "users" table if it exists
            cursor.execute("DROP TABLE IF EXISTS users")

            # Commit the changes and close the connection
            conn.commit()
            conn.close()
        except Exception as e:
            raise DatabaseQueryError("Clear tables in database", str(e))

    def get_all_restaurants(self):
        """Retrieve a list of all restaurants stored in the database.

        This method retrieves and returns a list of all restaurant objects present in the 'restaurants' table
        of the database. Each restaurant object is represented as an instance of the 'Restaurant' class.

        Returns:
            list[Restaurant]: A list of all restaurant objects in the database.

        Raises:
            DatabaseQueryError: If there is an issue while retrieving the restaurants from the database.
        """
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                query = "SELECT * FROM restaurants"
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    restaurants = cursor.fetchall()

                restaurant_objects = []
                for restaurant_data in restaurants:
                    restaurant_id = restaurant_data['id']
                    restaurant_object = self.get_restaurant(restaurant_id)
                    restaurant_objects.append(restaurant_object)

                return restaurant_objects
        except Exception as e:
            raise DatabaseQueryError("Retrieve all restaurants from database", str(e))

    
    def get_all_dishes(self, order="name_asc"):
        """Retrieve a list of all dishes stored in the database.

        This method retrieves and returns a list of all dish objects present in the 'dishes' table
        of the database. Each dish object is represented as an instance of the 'Dish' class.

        Args:
            order (str, optional): Specifies the sorting order of retrieved dishes.
                Possible values: "date_asc", "date_desc", "stars_asc", "stars_desc", "name_asc", "name_desc.
                Default value is "default".

        Returns:
            list[Dish]: A list of all dish objects in the database.

        Raises:
            ValueError: If the 'order' parameter value is not one of the allowed values.
            DatabaseQueryError: If there is an issue while retrieving the dishes from the database.
        """
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                query = "SELECT * FROM dishes"

                if order.lower() == "date_asc":
                    query += " ORDER BY date ASC"
                elif order.lower() == "date_desc":
                    query += " ORDER BY date DESC"
                elif order.lower() == "stars_desc":
                    query += " ORDER BY stars DESC"
                elif order.lower() == "stars_asc":
                    query += " ORDER BY stars ASC"
                elif order.lower() == "name_asc":
                    query += " ORDER BY name ASC"
                elif order.lower() == "name_desc":
                    query += " ORDER BY name DESC"
                
                # Fetch each row as a dictionary
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    dishes = cursor.fetchall()

                dishes_list = [Dish(**dish) for dish in dishes]
                return dishes_list
        except Exception as e:
            raise DatabaseQueryError("Retrieve all dishes from database", str(e))
        
    def get_dish(self, dish_id):
        """Retrieve a specific dish from the database by its unique ID.

        This method retrieves a specific dish from the 'dishes' table of the database using its unique ID.
        The dish object is represented as an instance of the 'Dish' class.

        Args:
            dish_id (str): The unique identifier of the dish to retrieve.

        Returns:
            Dish: The dish object representing the retrieved dish.

        Raises:
            DishNotFoundError: If the specified dish ID does not exist in the database.
            DatabaseQueryError: If there is an issue while retrieving the dish from the database.
        """ 
        try:
            # Make sure the dish is in the database
            if not self.util_dish_in_db(dish_id):
                raise DishNotFoundError(dish_id)
            
            # Establish a connection to the database
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                query = "SELECT * FROM dishes WHERE id = %s"
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (dish_id,))
                dish_in_db = cursor.fetchone()
                
                if not dish_in_db:
                    raise DishNotFoundError(dish_id)
                
                return Dish(**dish_in_db)
        except Exception as e:
            raise DatabaseQueryError(f"Retrieve dish with ID {dish_id} from database", str(e))

    def get_restaurant(self, restaurant_id):
        """Retrieve a specific restaurant from the database by its ID.

        This method retrieves a specific restaurant from the 'restaurants' table of the database using its unique ID.
        The restaurant object is represented as an instance of the 'Restaurant' class.

        Args:
            restaurant_id (str): The unique identifier of the restaurant to retrieve.

        Returns:
            Restaurant: The restaurant object representing the retrieved restaurant.

        Raises:
            RestaurantNotFoundError: If the specified restaurant ID does not exist in the database.
            DatabaseQueryError: If there is an issue while retrieving the restaurant from the database.
        """
        try:
            # Establish a connection to the database
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                query = "SELECT * FROM restaurants WHERE id = %s"
                cursor = conn.cursor()
                cursor.execute(query, (restaurant_id,))
                restaurant_in_db = cursor.fetchone()

                if not restaurant_in_db:
                    raise RestaurantNotFoundError(restaurant_id)

                return Restaurant(*restaurant_in_db)
        except Exception as e:
            raise DatabaseQueryError(f"Retrieve restaurant {restaurant_id} from database", str(e))
        
    def get_dishes_from_restaurant(self, restaurant_id):
        """Retrieve all dishes associated with a specific restaurant from the database.

        This method retrieves all dishes that are associated with a specific restaurant from the database.
        The dishes are represented as a list of instances of the 'Dish' class.

        Args:
            restaurant_id (str): The unique identifier of the restaurant for which to retrieve the dishes.

        Returns:
            list[Dish]: A list of Dish objects representing the dishes associated with the restaurant.

        Raises:
            RestaurantNotFoundError: If the specified restaurant ID does not exist in the database.
            DatabaseQueryError: If there is an issue while retrieving the dishes from the database.
        """
        try:
            # Make sure the restaurant is in the database
            if not self.util_restaurant_in_db(restaurant_id):
                raise RestaurantNotFoundError(restaurant_id)
            
            # Establish a connection to the database
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                query = "SELECT * FROM dishes WHERE restaurant_id = %s"
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (restaurant_id,))
                dishes_in_db = cursor.fetchall()
                
                dish_list = [Dish(**dish) for dish in dishes_in_db]
                return dish_list
        except Exception as e:
            raise DatabaseQueryError(f"Retrieve dishes from restaurant {restaurant_id} in database", str(e))
    
    def update_record(self, record_id, table_name, **kwargs):
        """
        Update a record in the specified table. 

        Args:
            record_id (str): The ID of the record to be updated.
            table_name (str): Name of the table to update. Must be either 'dishes' or 'restaurants'.
            **kwargs: Keyword arguments representing the fields and values to update.

        Raises:
            DishNotFoundError: If the specified dish is not found in the database.
            RestaurantNotFoundError: If the specified restaurant is not found in the database.
            KeyError: If the 'id' field is provided in kwargs, as the ID cannot be updated.
            DatabaseQueryError: If there is an issue while updating the record in the database.
            
        Note:
            This method is automatically invoked when calling the 'update' functions for Dish and Restaurant.
            There's typically no need to call this function directly.
        """
        try:
            # ... (existing code)

            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                cursor = conn.cursor()
                update_fields = []
                params = []
                for field, value in kwargs.items():
                    if field == 'dietary_restrictions':
                        value = json.dumps(value)  # Serialize list to a JSON string
                    update_fields.append(f"{field} = %s")
                    params.append(value)
                params.append(record_id)
                update_query = ", ".join(update_fields)
                query = f"UPDATE {table_name} SET {update_query} WHERE id = %s"
                cursor.execute(query, params)
        except Exception as e:
            kwargs_str = json.dumps(kwargs)
            class_name = "restaurant" if table_name == "restaurants" else "dish"
            raise DatabaseQueryError(f"Update {class_name} {record_id} in database with fields: {kwargs_str}", str(e))
   
    def update_dish(self, dish_id, **kwargs):
        """
        Update a dish record in the database with the specified dish ID.

        Args:
            dish_id (str): The unique identifier of the dish to be updated.
            **kwargs: Keyword arguments containing the fields to be updated.(Can be any number of these possible arguments)
                Possible keyword arguments include:
                - dish_name (str): The new name of the dish.
                - image_url (str): The new URL of the dish's image.
                - date (str): The new date the dish was added (YYYY-MM-DD).
                - stars (int): The new star rating of the dish (0 to 5).
                - dietary_restrictions (list): The new list of dietary restrictions.

        Raises:
            DishNotFoundError: If the specified dish ID is not found in the database.
            DatabaseQueryError: If there is an issue while updating the dish record.

        Example:
            # Update the name and stars of a dish
            update_dish('add3ac49-8b7a-4147-914f-3d3b9b103ed7', dish_name='New Name', stars=4)
        """
        try:
            self.update_record(dish_id, 'dishes', **kwargs)
        except Exception as e:
            raise DatabaseQueryError(f"Update dish {dish_id} in database", str(e))


    def update_restaurant(self, restaurant_id, **kwargs):
        """
        Update a restaurant record in the database with the specified restaurant ID.

        Args:
            restaurant_id (str): The unique identifier of the restaurant to be updated. (Can be any number of these possible arguments)
            **kwargs: Keyword arguments containing the fields to be updated.
                Possible keyword arguments include:
                - restaurant_name (str): The new name of the restaurant.
                - address (str): The new address of the restaurant.
                - cuisine (str): The new cuisine type of the restaurant.
                - latitude (float): The new latitude coordinate of the restaurant.
                - longitude (float): The new longitude coordinate of the restaurant.

        Raises:
            RestaurantNotFoundError: If the specified restaurant ID is not found in the database.
            DatabaseQueryError: If there is an issue while updating the restaurant record.

        Example:
            # Update the name and cuisine of a restaurant
            update_restaurant('add3ac49-8b7a-4147-914f-3d3b9b103ed7', restaurant_name='New Name', cuisine='Italian')
        """
        try:
            self.update_record(restaurant_id, 'restaurants', **kwargs)
        except Exception as e:
            raise DatabaseQueryError(f"Update restaurant {restaurant_id} in database", str(e))

    
    def add_restaurant(self, restaurant):
        """
        Add a new restaurant to the database.

        Args:
            restaurant (Restaurant): The restaurant object to be inserted.

        Returns:
            str: The ID of the restaurant that was inserted via this function

        Raises:
            DuplicateRestaurantError: If the restaurant with the same ID is already in the database.
            DatabaseQueryError: If there is an issue while inserting the restaurant record.

        Example:
            # Create a new restaurant object
            new_restaurant = Restaurant(id='add3ac49-8b7a-4147-914f-3d3b9b103ed7', name='New Restaurant', address='123 Humber St',
                                        cuisine='American', latitude=123.45, longitude=-123.45)

            # Add the restaurant to the database
            restaurant_id = add_restaurant(new_restaurant)
        """
        if self.util_restaurant_in_db(restaurant.id):
            raise DuplicateRestaurantError(restaurant.id)

        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO restaurants (id, restaurant_name, address, cuisine, latitude, longitude, dish_ids)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (restaurant.id, restaurant.name, restaurant.address, restaurant.cuisine, restaurant.latitude, restaurant.longitude, ''))

            return restaurant.id
        except Exception as e:
            raise DatabaseQueryError(f"Insert restaurant with ID {restaurant.id} into the database", str(e))

    def add_dish(self, dish):
        """
        Insert a new dish to the database and update the corresponding restaurant's dish_ids.

        Args:
            dish (Dish): The dish object to be added.

        Returns:
            str: The ID of the added dish.

        Raises:
            DuplicateDishError: If the dish with the same ID is already in the database.
            RestaurantNotFoundError: If the corresponding restaurant does not exist in the database.
            DatabaseQueryError: If there is an issue while inserting the dish record or updating dish_ids.

        Example:
            # Create a new dish object and retrieve the corresponding restaurant
            new_dish = Dish(id='add3ac49-8b7a-4147-914f-3d3b9b103ed7', restaurant_id='5ef5c49d-27de-4f28-a399-2b87bb324594', dish_name='New Dish',
                            image_url='https://example.com/dish.jpg', date='2023-08-10', stars=4,
                            dietary_restrictions=['Gluten-Free', 'Vegetarian'])

            # Add the dish to the database and update the restaurant's dish_ids
            dish_id = add_dish(new_dish)
        """
        # If dish was already added to the database, raise error
        if self.util_dish_in_db(dish.id):
            raise DuplicateDishError(dish.id)

        if not self.util_restaurant_in_db(dish.restaurant_id):
            raise RestaurantNotFoundError(dish.restaurant_id)

        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO dishes (id, restaurant_id, image_url, dish_name, date, stars, dietary_restrictions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (dish.id, dish.restaurant_id, dish.image_url, dish.dish_name, dish.date, dish.stars, json.dumps(dish.dietary_restrictions)))
        except Exception as e:
            raise DatabaseQueryError(f"Insert dish with ID {dish.id} into the database", str(e))
        
        try:
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                cursor = conn.cursor()

                # Get the set of dish_ids for the restaurant
                restaurant_dish_ids = self.all_restaurants.get(dish.restaurant_id, set())
                
                # Add the new dish_id to the set of dish_ids for this restaurant
                restaurant_dish_ids.add(dish.id)
                
                # Convert the set back to a comma-separated string
                updated_dish_ids = ", ".join(restaurant_dish_ids)

                # Update the 'dish_ids' of the restaurant
                cursor.execute('UPDATE restaurants SET dish_ids = %s WHERE id = %s', (updated_dish_ids, dish.restaurant_id))

                return dish.id
        except Exception as e:
            raise DatabaseQueryError(f"Update 'dish_ids' list for restaurant {dish.restaurant_id} by inserting dish id {dish.id}", str(e))

    def delete_dish(self, dish_id):
        """
        Delete a dish record from the database and update the corresponding restaurant's dish_ids
        by deleting that dish UUID from the list

        Args:
            dish_id (str): The UUID of the dish to be deleted.

        Raises:
            DishNotFoundError: If the dish with the specified UUID is not found in the database.
            DatabaseQueryError: If there is an issue while deleting the dish record or updating dish_ids for the restaurant.

        Example:
            # Delete a dish with UUID 'd39ad9a4-6a98-4c9b-83ad-63a69c24b3e7'
            delete_dish('d39ad9a4-6a98-4c9b-83ad-63a69c24b3e7')
        """
        if not self.util_dish_in_db(dish_id):
            raise DishNotFoundError(dish_id)
        try:
            # Retrieve the dish to be deleted
            dish = self.get_dish(dish_id)

            # Delete the dish from the 'dishes' table
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM dishes WHERE id = %s", (dish_id,))

            # Update the 'dish_ids' of the corresponding restaurant
            restaurant_dish_ids = self.all_restaurants[dish.restaurant_id]
            restaurant_dish_ids.remove(dish_id)
            updated_dish_ids_str = ", ".join(restaurant_dish_ids)
            self.update_restaurant(restaurant_id=dish.restaurant_id, dish_ids=updated_dish_ids_str)

        except Exception as e:
            raise DatabaseQueryError(f"Delete dish with ID {dish_id}", str(e))


    def delete_restaurant(self, restaurant_id):
        """
        Delete a dish record from the database and delete the corresponding restaurant's dish_ids.
        Essentially, delete the restaurant and everything connected to it.

        Args:
            dish_id (str): The UUID of the dish to be deleted.

        Raises:
            DishNotFoundError: If the dish with the specified UUID is not found in the database.
            DatabaseQueryError: If there is an issue while deleting the dish record or updating dish_ids for the restaurant.

        Example:
            # Delete a dish with UUID 'd39ad9a4-6a98-4c9b-83ad-63a69c24b3e7'
            delete_dish('d39ad9a4-6a98-4c9b-83ad-63a69c24b3e7')
        """
        try:
            if not self.util_restaurant_in_db(restaurant_id):
                raise RestaurantNotFoundError(restaurant_id)

            dish_ids_to_delete = set(self.all_restaurants[restaurant_id])
            for dish_id in dish_ids_to_delete:
                self.delete_dish(dish_id)

            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM restaurants WHERE id = %s", (restaurant_id,))

            del self.all_restaurants[restaurant_id]
        except Exception as e:
            raise DatabaseQueryError(f"Delete restaurant with ID {restaurant_id}", str(e))

    
    def custom_query(self, table_name, conditions, order_by=None, parameters=None):
        """
        Retrieve rows from the specified table based on the provided conditions and optional sorting.

        Args:
            table_name (str): Name of the table to query. (MUST be either 'restaurants' or 'dishes')
            conditions (list[str]): list of SQL WHERE clause conditions, e.g., ["stars = ?", "cuisine = ?"].
            order_by (str, optional): Column to sort by and sorting direction, e.g., "stars DESC". Default is None.
            parameters (tuple, optional): Values to replace placeholders in conditions, e.g., (4, "Italian").

        Returns:
            list[object]: list of objects representing the retrieved rows.

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
            with mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.name
            ) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, parameters)

                result = []
                for row in cursor.fetchall():
                    if table_name == 'restaurants':
                        result.append(Restaurant(**row))
                    elif table_name == 'dishes':
                        result.append(Dish(**row))
                    else:
                        raise ValueError(f"Unsupported table name: {table_name}")

            return result
        except Exception as e:
            raise DatabaseQueryError(f"Query table with query {query}", str(e))
        
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
    