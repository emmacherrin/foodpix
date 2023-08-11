import json

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
