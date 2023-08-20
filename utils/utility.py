import json, math

def listify(input):
    """
    Convert a string or tuple into a list format. If already a list, returns as is.

    Args:
        input (str, list, tuple): The input string or list to be converted.

    Returns:
        list: A list representation of the input, where each element is separated by a comma.
    """
    if isinstance(input, list):
        return input
    elif isinstance(input, str):
        return [item.strip() for item in input.split(',') if item.strip()]
    elif isinstance(input, tuple):
        return list(input)
    else:
        return []

def stringify(input):
    """
    Convert a string, list, or tuple into a comma-separated string. If already a string, returns as is.

    Args:
        input (str, list, tuple): The input to be converted.

    Returns:
        str: A string representation of the input, with elements separated by commas.
    """
    if isinstance(input, str):
        return input
    elif isinstance(input, list):
        return ', '.join(str(item) for item in input)
    elif isinstance(input, tuple):
        return ', '.join(str(item) for item in input)
    else:
        return ''

    
def obj_to_json(obj_or_list):
    """
    Convert an object or a list of objects into a JSON formatted string.

    Args:
        obj_or_list (object or list): An object or a list of objects with a 'to_dict()' method that returns
            a dictionary representation of the object's attributes. If a single object
            is provided instead of a list, it will be converted to JSON directly.

    Returns:
        str: A JSON formatted string representing the object or the list of objects.

    Note:
        The objects in the provided list must implement a 'to_dict()' method to
        allow conversion to dictionary format for JSON serialization.
    """
    if isinstance(obj_or_list, list):
        obj_dicts = [obj.to_dict() for obj in obj_or_list]
    else:
        obj_dicts = obj_or_list.to_dict()

    return json.dumps(obj_dicts, indent=4)

import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the Earth's surface using the Haversine formula.

    Args:
        lat1 (float): Latitude of the first point in degrees.
        lon1 (float): Longitude of the first point in degrees.
        lat2 (float): Latitude of the second point in degrees.
        lon2 (float): Longitude of the second point in degrees.

    Returns:
        float: The distance between the two points in kilometers.

    Note:
        This function calculates the shortest distance between two points on the surface of a sphere,
        which approximates the Earth's shape. It uses the Haversine formula to do so. 

    Reference:
    https://en.wikipedia.org/wiki/Haversine_formula
    """
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Radius of the Earth in kilometers
    earth_radius = 6371.0
    
    # Calculate differences in coordinates
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    
    # Calculate Haversine formula components
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Calculate the distance
    distance = earth_radius * c
    
    return distance
