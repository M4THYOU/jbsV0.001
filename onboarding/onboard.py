from firesdk.firebase_functions.firebaseconn import add_company, add_user, get_company_code_by_name
from firesdk.firebase_functions.firebaseauth import generate_password, auth
from firebase_admin.auth import AuthError

from firesdk.util.utils import company_to_dict, user_to_dict, org_names_filter

from django.core import mail
from django.template.loader import render_to_string

import csv
from random import randint
from smtplib import SMTPException


def parse_csv(path_to_csv):
    """
    Path
    :param path_to_csv: Filepath to the csv file with a list of users in the new client company.
    :return: Dict with structure: {'company': String, 'departments': [String], 'users': [{}, {}, {}]}
    """
    company_name = ''
    departments_dict = {}
    users = []

    with open(path_to_csv, 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            company_name = org_names_filter(row[0])
            user_departments = row[1].split(', ')
            for department in user_departments:
                departments_dict[org_names_filter(department)] = True

            last_name = row[2]
            first_name = row[3]
            email = row[4]
            position = row[5]
            is_pt = bool(row[6])
            account_type = int(row[7])

            current_user_dict = {
                'last_name': last_name,  # type string
                'first_name': first_name,  # type string
                'email': email,  # type string
                'position': position,  # type string
                'departments': user_departments,  # type list of strings
                'company': company_name,  # type string
                'is_pt': is_pt,  # type int 0 for full time or 1 for part time. Can be bool as well
                'account_type': account_type,  # type int 0 for basic, 1 for manager, 2 for master
                'status': 'active'  # type string 'active', 'leave', 'remove'
            }
            users.append(current_user_dict)

    departments_list = list(departments_dict.keys())

    parsed_company_dict = {
        'company': company_name, 'departments': departments_list, 'users': users
    }

    return parsed_company_dict


def add_single_user(user_dict, company):
    """
    Adds a single user to a company.
    :param user_dict: Dict of the user containing last_name (string), first_name (string), email (string), position
    (string), departments([string]), is_pt (Bool), account_type (int), status (string)
    :param company: Name of the company, assumed to be unfiltered.
    :return: A dict of data containing everything needed for emailing the user their onboarding info.
    """
    last_name = user_dict['last_name']
    first_name = user_dict['first_name']
    full_name = first_name + ' ' + last_name
    email = user_dict['email']
    position = user_dict['position']
    departments = user_dict['departments']
    is_pt = user_dict['is_pt']
    account_type = user_dict['account_type']
    status = user_dict['status']

    auto_generated_password = generate_password(randint(10, 15))
    is_already_added = False
    try:
        auth.create_user(
            email=email,
            password=auto_generated_password,
            display_name=full_name
        )
    except AuthError:
        is_already_added = True

    user_dict = user_to_dict(position, departments, email, first_name, last_name, is_pt, account_type, status)
    add_user(user_dict, org_names_filter(company))

    email_dict = {
        'email_address': email,
        'temp_password': auto_generated_password,
        'first_name': first_name,
        'company_name': company,
        'is_already_added': is_already_added
    }
    return email_dict


def email_single_user(email_dict, company_code, open_new_connection=True):
    """
    Adds a single user to a company.
    :param email_dict: Dict of the user's email info containing email_address (string), temp_password (string),
    first_name (string), company_name (string), is_already_added (Bool).
    :param company_code: String of the current company code the user is being added to.
    :param open_new_connection: If a mail.connection() has already been established outside the scope of this function
    set this flag to False. Else, leave it as true.
    """
    if open_new_connection:
        connection = mail.get_connection()
        connection.open()

    email_dict['company_code'] = company_code
    email_address = email_dict['email_address']

    if email_dict['is_already_added']:
        email_subject = 'Welcome back to The Hive'
        email_html = render_to_string('emails/welcome-back-password.html', email_dict)
    else:
        email_subject = 'Welcome to The Hive'
        email_html = render_to_string('emails/welcome-password.html', email_dict)

    try:
        mail.send_mail(email_subject, email_html, 'jbs.wolfe@gmail.com', [email_address],
                       fail_silently=False, html_message=email_html)
    except SMTPException as e:
        print(e)

    if open_new_connection:
        connection.close()


def add_new_users(new_client_dict):
    """
    :param new_client_dict: Dict with structure {'company': String, 'departments': [String], 'users': [{}, {}, {}]}
    :return: list of dicts with structure {'email_address': String, 'temp_password': String, 'first_name': String,
    'company_name': String}
    email address, temp password, and first name of the users. (email, temp_password, first_name).
    """
    company = new_client_dict['company']

    user_passwords = []

    for user in new_client_dict['users']:
        email_dict = add_single_user(user, company)
        user_passwords.append(email_dict)

    return user_passwords


def email_temp_passwords(email_dict_list, company_code):
    connection = mail.get_connection()
    connection.open()

    # Email the users.
    for email_dict in email_dict_list:
        email_single_user(email_dict, company_code, open_new_connection=False)

    # Email myself the temp_password list in case any emails fail to send.
    email_string = '\n'.join(str(user) for user in email_dict_list)
    mail.send_mail('TEST', email_string, 'jbs.wolfe@gmail.com', ['mathyou.wolfe@gmail.com'],
                   fail_silently=False)

    connection.close()


def create_new_client(path_to_csv):
    """
    :return: The company code.
    """
    new_client_dict = parse_csv(path_to_csv)
    company_dict = company_to_dict(new_client_dict['company'], new_client_dict['departments'])

    # Create the company in databases and then add the users
    add_company(company_dict)
    email_data = add_new_users(new_client_dict)

    # email the user their password and the company code
    company_code = get_company_code_by_name(org_names_filter(new_client_dict['company']))
    email_temp_passwords(email_data, company_code)
