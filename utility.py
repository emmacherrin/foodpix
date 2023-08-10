def listify(string_or_list):
    # If parameter is a list, return the list
    if isinstance(string_or_list, list):
        return string_or_list
    # If the parameter is a string, the string formatted as a list (each separate element indicated by comma)
    elif isinstance(string_or_list, str):
        return [item.strip() for item in string_or_list.split(',') if item.strip()]
    elif isinstance(string_or_list, tuple):
        return list(string_or_list)
    # Return an empty list by default (should never get here)
    else:
        return []
    
def stringify(string_or_list):
    # If the input is already a string, return it
    if isinstance(string_or_list, str):
        return string_or_list
    # If the input is a list, join the elements with commas and return the resulting string
    elif isinstance(string_or_list, list):
        return ', '.join(str(item) for item in string_or_list)
    # If it's a tuple, join the elements with commas and return the resulting string
    elif isinstance(string_or_list, list):
        return ', '.join(str(item) for item in string_or_list)
    # Return an empty string by default (should never get here)
    else:
        return ''