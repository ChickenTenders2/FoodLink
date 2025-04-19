import re

class input_handling():

    def validate_expiry(self, expiry):
        # Regular expressions used to check if the expiry is formatted correctly.
        if re.search("^0/0/0$", expiry):
            return False
        valid = re.search("^(0?[0-9]|[12][0-9]|3[01])/(0?[0-9]|1[0-2])/\\d+$", expiry)
        return valid

    def sanitise_input(self, input):
        # Regular expressions used to check if the expiry is formatted correctly.
        invalid = re.search("\\*|select|insert|drop|update|delete|;|union|#|--", input)
        return invalid

    def sanitise_all(self, request):
        for field, value in request:
            attack = sanitise_input(value)
            if attack:
                return jsonify({'success': False, 'error': str("Potential SQL injection detected.")})

