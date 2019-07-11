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
                'last_name': last_name,
                'first_name': first_name,
                'email': email,
                'position': position,
                'departments': user_departments,
                'company': company_name,
                'is_pt': is_pt,
                'account_type': account_type
            }
            users.append(current_user_dict)

    departments_list = list(departments_dict.keys())

    parsed_company_dict = {
        'company': company_name, 'departments': departments_list, 'users': users
    }

    return parsed_company_dict


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
        last_name = user['last_name']
        first_name = user['first_name']
        full_name = first_name + ' ' + last_name
        email = user['email']
        position = user['position']
        departments = user['departments']
        is_pt = user['is_pt']
        account_type = user['account_type']

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

        user_dict = user_to_dict(position, departments, email, first_name, last_name, is_pt, account_type)
        add_user(user_dict, org_names_filter(company))

        email_dict = {
            'email_address': email,
            'temp_password': auto_generated_password,
            'first_name': first_name,
            'company_name': company,
            'is_already_added': is_already_added
        }
        user_passwords.append(email_dict)

    return user_passwords


def email_temp_passwords(email_dict_list, company_code):
    connection = mail.get_connection()
    connection.open()

    # Email the users.
    for email_dict in email_dict_list:
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
