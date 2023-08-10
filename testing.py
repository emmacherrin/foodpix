from restaurant import Restaurant
from dish import Dish
from foodpix import DB
import json, utility

def util_create_clear(db_name):
    db = DB(db_name)
    db.clear_db()
    db.create_db()
    return db

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
    r1 = Restaurant("Spencer's Sandwiches", "26694 Humber St, Huntington Woods, MI", "American", "123.3", "321.3", "")
    db.add_restaurant(r1)
    r2 = Restaurant("Marni's Meatballs", "123 Huntington St, Cleveland, Ohio", "American", "123.3", "321.3", "")
    db.add_restaurant(r2)
    
    # Get all restaurants
    print(db.get_all_restaurants())
    
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
    
    print("\n\n RESTAURANT \n")
    print(db.get_restaurant(r1_id))
    
    # Should print each dish as a list and should update respective restaurants
    print("\n\n DISHES \n")
    print(db.get_all_dishes())
    
    print("\n\n RESTAURANTS \n")
    print(db.get_all_restaurants())
    


test_adding_dishes()   