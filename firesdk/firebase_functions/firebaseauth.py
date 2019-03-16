from .basefirebase import *
from firesdk.models import CompanyId
from firesdk.util.utils import user_to_dict
from .firebaseconn import add_user

import string
import random


def user_auth(user):
    email = user.get_email()
    password = generate_password(15)
    display_name = user.get_full_name()

    auth.create_user(
        email=email,
        password=password,
        display_name=display_name)

    email_password = (email, password)
    return email_password


def user_db(company, user):
    position = user.get_position()
    departments = user.get_departments()
    email = user.get_email()
    first_name = user.get_first_name()
    last_name = user.get_last_name()
    is_pt = user.get_is_pt()
    account_type = user.get_account_type()

    user_dict = user_to_dict(position, departments, email, first_name, last_name, is_pt, account_type)

    add_user(user_dict, company)


def email_user_password_tuple_list(email_passwords):
    pass


def register_user(company, user):
    email_password_tuple = user_auth(user)
    user_db(company, user)

    return email_password_tuple


def register_user_list(company, user_list):
    email_password_list = []

    for user in user_list:
        email_password_tuple = register_user(company, user)
        email_password_list.append(email_password_tuple)

    email_user_password_tuple_list(email_password_list)


def is_valid_company_code(code):
    is_valid = False

    for company in CompanyId.objects.all():
        if company.company_code == code:
            is_valid = True

    return is_valid


def generate_password(length):
    alphabet = string.ascii_letters + string.digits

    while True:
        password = ''.join(random.choice(alphabet) for _ in range(length))

        if any(c.islower() for c in password)\
                and any(c.isupper() for c in password)\
                and sum(c.isdigit() for c in password) >= 3:
            return password
