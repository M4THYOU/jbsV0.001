from django.core.validators import validate_email

class RegisteringUser():

    username = ""
    first_name = ""
    last_name = ""
    email = ""
    password = ""

    def __init__(self, username, first_name, last_name, email, password):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

        validate_email(email)
        self.email = email

        self.password = password