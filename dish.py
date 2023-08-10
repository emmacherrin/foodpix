from typing import Optional, List
import sqlite3, os, json, utility, uuid
from uuid import UUID, uuid4
class Dish:
    def __init__(self, id: Optional[str] = None, restaurant_id: Optional[int] = None,
                 dish_name: Optional[str] = None, image_url: Optional[str] = None,
                 date: Optional[str] = None, stars: Optional[int] = None,
                 dietary_restrictions: Optional[List[str]] = None):
        self.id = id if id is not None else str(uuid.uuid4())  # Assign a new UUID if id is None
        self.restaurant_id = restaurant_id
        self.dish_name = dish_name
        self.image_url = image_url
        self.date = date
        self.stars = int(stars) if stars is not None else None
        self.dietary_restrictions = utility.listify(dietary_restrictions)
        
    def __str__(self):
        dish_json = json.dumps(self.to_dict(), indent=4)
        return dish_json
    
    def to_dict(self):
        data = {
            "id": self.id,
            "restaurant_id": self.restaurant_id,
            "image_url": self.image_url,
            "dish_name": self.dish_name,
            "date": self.date,
            "stars": self.stars,
            "dietary_restrictions": self.dietary_restrictions
        }
        return data

