import sqlite3, os, json
from uuid import UUID, uuid4
from models.dish import Dish
from typing import Optional, List
import utility
class Restaurant:
    def __init__(self, id: Optional[str] = None, name: Optional[str] = None,
                 address: Optional[str] = None, cuisine: Optional[str] = None,
                 latitude: Optional[float] = None, longitude: Optional[float] = None,
                 dish_ids: Optional[List[str]] = None):
        self.id = id if id is not None else str(uuid4())  # Assign a new UUID if id is None
        self.name = name
        self.address = address
        self.cuisine = cuisine
        self.latitude = latitude
        self.longitude = longitude
        self.dish_ids = utility.listify(dish_ids)
        
    def to_dict(self):
        data = {
            "id": self.id,
            "restaurant_name": self.name,
            "address": self.address,
            "cuisine": self.cuisine,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "dish_ids": self.dish_ids
        }
        return data

