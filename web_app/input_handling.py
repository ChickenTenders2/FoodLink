from flask import request
import re

def validate_expiry(expiry):
    """
    Validates the expiry date format.

    Args:
        expiry (str): The expiry date string (expected format: DD/MM/YYYY or similar).

    Returns:
        MatchObject or None: Returns a match object if valid, or None if invalid.
    """

    # Regular expressions used to check if the expiry is formatted correctly.
    if re.search("^0/0/0$", expiry):
        return False
    valid = re.search("^(0?[0-9]|[12][0-9]|3[01])/(0?[0-9]|1[0-1])/\\d+$", expiry)
    return valid

def sanitise_input(input):
    """
    Removes potentially dangerous SQL keywords and symbols from the input.

    Args:
        input (str): User-provided input string.

    Returns:
        str: Sanitised string with dangerous patterns removed.
    """

    # Regular expressions used to check if any sql commands are includeed.
    sanitised = re.sub("\\*|select|insert|drop|update|delete|;|union|#|--", "", input, flags=re.I)
    return sanitised

def sanitise_all(input_list):
    """
    Retrieves and sanitises multiple form inputs from the request.

    Args:
        input_list (list): List of form field names to retrieve and sanitise.

    Returns:
        list: List of sanitised and stripped input values.
    """
    fields = []
    # Loop through the list of keys sanitising one by one.
    for field in input_list:
        input = request.form.get(field)
        sanitised_input = sanitise_input(input)
        fields.append(sanitised_input.strip())
    return fields

