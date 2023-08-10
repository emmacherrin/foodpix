from restaurant import Restaurant
from dish import Dish
from foodpix import DB
import json, utility

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
    
    # Get all restaurants
    all_restaurants = db.get_all_restaurants()
    restaurant_dicts = [restaurant.to_dict() for restaurant in all_restaurants]
    print(json.dumps(restaurant_dicts))

    
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
    print(json.dumps(db.get_all_dishes()))
    
    print("\n\n RESTAURANTS \n")
    print(json.dumps(db.get_all_restaurants()))
    
def test_get_dishes_from_restaurant():
    # Create a new connection to the database, clear everything that is in it and start fresh
    db = util_create_clear("restaurant_app.db")
    
    # Instantiates dishes and restaurants with sample values
    restaurants, dishes = util_restaurants_and_dishes(db)

    print(db.get_all_dishes())
    
    print("Restaurant 1")
    print(json.dumps(db.get_dishes_from_restaraunt(restaurants[0].id)))  
    
    print("Restaurant 2")  
    print(json.dumps(db.get_dishes_from_restaraunt(restaurants[1].id)))    


def main():
   test_adding_restaurants()
   # test_adding_dishes()
   #test_get_dishes_from_restaurant()


if __name__ == "__main__":
    main()
    