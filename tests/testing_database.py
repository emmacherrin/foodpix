from models.restaurant import Restaurant
from models.dish import Dish
from database import DB
import json, utils.utility as utility, unittest, sqlite3
            
def util_create_clear(db_name):
    db = DB(db_name)
    db.clear_db()
    db.create_db()
    return db

def util_restaurants_and_dishes(db):
    # Initialize restaurants and add them to database
    restaurants = [
        Restaurant(None, "Spencer's Sandwiches", "26694 Humber St, Huntington Woods, MI", "American", "123.3", "321.3", ""),
        Restaurant(None, "Marni's Meatballs", "123 Huntington St, Cleveland, Ohio", "American", "123.3", "321.3", "")
    ]
    
    for restaurant in restaurants:
        db.add_restaurant(restaurant)
        
    # Initialize 9 dishes and add them to database
    dishes = [
        Dish(None, restaurants[0].id, "Turkey Club Sandwich", "image_test.jpg", "14-07-2023", 4, ""),
        Dish(None, restaurants[1].id, "Penne Alfredo", "image_test1.jpg", "12-05-2023", 5, ["vegetarian"]),
        Dish(None, restaurants[0].id, "Grilled Cheese", "image_test2.jpg", "12-05-2023", 3, ["vegetarian"]),
        Dish(None, restaurants[1].id, "Spaghetti Bolognese", "image_test3.jpg", "15-07-2023", 4, ""),
        Dish(None, restaurants[0].id, "BLT Sandwich", "image_test4.jpg", "18-06-2023", 4, ""),
        Dish(None, restaurants[1].id, "Fettuccine Alfredo", "image_test5.jpg", "20-06-2023", 5, ["vegetarian", "gluten free"]),
        Dish(None, restaurants[0].id, "Chicken Avocado Wrap", "image_test6.jpg", "22-06-2023", 4, []),
        Dish(None, restaurants[0].id, "Veggie Wrap", "image_test7.jpg", "22-06-2023", 4, ["vegetarian", "vegan"]),
        Dish(None, restaurants[1].id, "Rigatoni Carbonara", "image_test8.jpg", "23-06-2023", 5, [])
    ]
    
    for dish in dishes:
        db.add_dish(dish)
    return (restaurants, dishes) # Tuple storing restaurants and dishes

def test_util_listify():
    str1 = "Emma, Brie, Spencer"
    list1 = utility.listify(str1)
    print(list1)
    print(utility.stringify(list1))

def test_adding_restaurants():
    """_summary_
    Creates a database, adds two restaurants, and adds dishes
    """ 
    
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
  
    # Add restaraunts to the database
    r1 = Restaurant(id=None, name="Spencer's Sandwiches", address="26694 Humber St, Huntington Woods, MI", cuisine="American", latitude="123.3", longitude="321.3")
    db.add_restaurant(r1)

    r2 = Restaurant(id=None, name="Marni's Meatballs", address="123 Huntington St, Cleveland, Ohio", cuisine="American", latitude="123.3", longitude="321.3")
    db.add_restaurant(r2)
    
    # Get one restaurant
    print("\n\n RESTAURANT \n")
    print(db.get_restaurant(r1.id).to_dict())
    
    # Print all the restaurants 
    print(utility.obj_to_json(db.get_all_restaurants()))
    
def test_adding_dishes():
    """_summary_
    Creates a database, adds two restaurants, and adds dishes
    """
    
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
    
    #Add restaraunts to the database
    r1 = Restaurant(None, "Spencer's Sandwiches", "26694 Humber St, Huntington Woods, MI", "American", "123.3", "321.3", "")
    r1_id = db.add_restaurant(r1)
    r2 = Restaurant(None, "Marni's Meatballs", "123 Huntington St, Cleveland, Ohio", "American", "123.3", "321.3", "")
    r2_id = db.add_restaurant(r2)
    
    #Add dishes to the database
    d1 = Dish(None, r1_id, "Tuna Fish sandwich", "image_test.jpg", "14-07-2023", 3, "pescatarian")
    d1_id = db.add_dish(d1)
    d2 = Dish(None, r2_id, "Red sauce pasta", "image_test1.jpg", "12-05-2023", 5, ["gluten free", "vegan"])
    d2_id = db.add_dish(d2) 
    d3 = Dish(None, r1_id, "Salad", "image_test1.jpg", "12-05-2023", 5, ["gluten free", "vegan"])
    d3_id = db.add_dish(d3) 

    # Get one dish
    print("\n\n DISH \n")
    print(db.get_dish(d2_id))
    
    # Should print each dish as a list and should update respective restaurants
    print("\n\n DISHES \n")
    print(utility.obj_to_json(db.get_all_dishes()))
    
    print("\n\n RESTAURANTS \n")
    print(utility.obj_to_json(db.get_all_restaurants()))
    
def test_get_dishes_from_restaurant():
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
    
    # Instantiates dishes and restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)

    #print(db.get_all_dishes())
    
    print("Restaurant 1")
    print(utility.obj_to_json(db.get_dishes_from_restaraunt(restaurants[0].id)))  
    
    print("Restaurant 2")  
    print(utility.obj_to_json(db.get_dishes_from_restaraunt(restaurants[1].id)))  

def test_get_all_dishes_date_asc():
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
    
    # Instantiates dishes and restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)
    print(utility.obj_to_json(db.get_all_dishes("date_asc")))  

def test_get_all_dishes_date_desc():
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
    
    # Instantiates dishes and restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)
    print(utility.obj_to_json(db.get_all_dishes("date_desc")))  

def test_get_all_dishes_stars_asc():
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
    
    # Instantiates dishes and restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)
    print(utility.obj_to_json(db.get_all_dishes("stars_asc")))  

def test_get_all_dishes_stars_desc():
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
    
    # Instantiates dishes and restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)
    print(utility.obj_to_json(db.get_all_dishes("stars_desc")))  

def test_update_dish():
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
    
    # Instantiates dishes and restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)
    
    # Gets a dish we are looking at updating
    dish = dishes[3]
    
    # Print the original details about the dish for comparison
    print("ORIGINAL DISH")
    print(dish)
    
    #Update the dish with new values
    db.update_dish(dish_id=dish.id, stars=5, dietary_restrictions=["nut-free", "dairy-free"])
    print("UPDATED DISH")
    print(db.get_dish(dish_id=dish.id))

def test_update_restaurant():
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")

    # Instantiates restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)
    
    print("ORIGINAL RESTAURANT")
    print(utility.obj_to_json(db.get_restaurant(restaurants[0].id)))

    
    # Define new values to update the restaurant
    new_values = {
        'restaurant_name': "Updated Restaurant",
        'address': "123 Updated St",
        'cuisine': "Italian",
        'longitude': 111.111,
        'dish_ids': ""
    }
    
    # Update the restaurant
    db.update_restaurant(restaurant_id=restaurants[0].id, **new_values)
    
    # Print the updated restaurant details
    updated_restaurant = db.get_restaurant(restaurants[0].id)
    print("UPDATED RESTAURANT")
    print(utility.obj_to_json(db.get_restaurant(updated_restaurant.id)))

def test_delete_dish():
    db = util_create_clear("restaurant_app.db")

    # Instantiates restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)
    
    #We are going to delete dish "Chicken Avocado Wrap" at index 6 from restaurant "Spencer's Sandwiches" at index 0
    
    # Original dishes at Spencer's sandwiches
    print("ORIGINAL DISHES AT SPENCER'S SANDWICHES")
    print(f"Restaurant ID: {restaurants[0].id}") #TODO: Delete this line
    original_dishes = db.get_dishes_from_restaurant(restaurants[0].id)
    print(utility.obj_to_json(original_dishes))
    
    db.delete_dish(dishes[6].id)
    
    print("UPDATED DISHES AT SPENCER'S SANDWICHES")
    print(utility.obj_to_json(db.get_dishes_from_restaurant(restaurants[0].id)))

def test_delete_restaurant():
    db = util_create_clear("restaurant_app.db")

    # Instantiate restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)
    
    # Add a new restaurant to test deletion
    new_restaurant = Restaurant("Test Restaurant", "123 Test St", "Test Cuisine", 0.0, 0.0, [])
    db.add_restaurant(new_restaurant)
    
    # Add dishes to the new restaurant
    for i in range(3):
        new_dish = Dish("Test Dish " + str(i), new_restaurant.id, "test.jpg", "Test Dish Description", "01-01-2023", i, [])
        db.add_dish(new_dish)
    
    print("ORIGINAL DISHES AT TEST RESTAURANT")
    print(f"Restaurant ID: {new_restaurant.id}")
    original_dishes = db.get_dishes_from_restaurant(new_restaurant.id)
    print(utility.obj_to_json(original_dishes))
    
    db.delete_restaurant(new_restaurant.id)
    
    print("RESTAURANTS AFTER DELETION")
    print(utility.obj_to_json(db.get_all_restaurants()))

def test_get_dishes_with_dietary_restrictions():
    db = util_create_clear("restaurant_app.db")

    # Instantiate restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)

    conditions = ["dietary_restrictions LIKE ?", "stars < ?",]
    parameters = ("%vegetarian%", 5)
    result = db.custom_query('dishes', conditions, parameters=parameters)
    for dish in result:
        print(dish.dish_name, dish.dietary_restrictions, dish.stars)
    
def main():
   #test_adding_restaurants()
   #test_adding_dishes()
   #test_get_dishes_from_restaurant()
   #test_get_all_dishes_date_asc()
   #test_get_all_dishes_date_desc()
   #test_get_all_dishes_stars_asc()
   #test_get_all_dishes_stars_desc()
   #test_update_dish()
   #test_update_restaurant()
   #test_delete_dish()
   test_delete_restaurant()
   #test_get_dishes_with_dietary_restrictions()
   
if __name__ == "__main__":
    main()