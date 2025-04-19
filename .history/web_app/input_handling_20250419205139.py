from flask import Flask, jsonify, render_template, request, url_for, Response
import re

class InputHandling():

    def validate_expiry(self, expiry):
        # Regular expressions used to check if the expiry is formatted correctly.
        if re.search("^0/0/0$", expiry):
            return False
        valid = re.search("^(0?[0-9]|[12][0-9]|3[01])/(0?[0-9]|1[0-2])/\\d+$", expiry)
        return valid

    def sanitise_input(self, input):
        # Regular expressions used to check if any sql commands are includeed.
        invalid = re.sub("\\*|select|insert|drop|update|delete|;|union|#|--", "", input)
        return invalid

    def sanitise_all(self, input_list):
        # Loop through the list of keys.
        for field in input_list:
            input = request.form.get(field).lower()
            self.sanitise_input(input)

