from flask import request
import re

def validate_expiry(expiry):
    # Regular expressions used to check if the expiry is formatted correctly.
    if re.search("^0/0/0$", expiry):
        return False
    valid = re.search("^(0?[0-9]|[12][0-9]|3[01])/(0?[0-9]|1[0-1])/\\d+$", expiry)
    return valid

def sanitise_input(input):
    # Regular expressions used to check if any sql commands are includeed.
    sanitised = re.sub("\\*|select|insert|drop|update|delete|;|union|#|--", "", input, flags=re.I)
    return sanitised

def sanitise_all(input_list):
    fields = []
    # Loop through the list of keys sanitising one by one.
    for field in input_list:
        input = request.form.get(field)
        sanitised_input = sanitise_input(input)
        fields.append(sanitised_input.strip())
    return fields

