from firesdk.firebase_functions.firebaseconn import *
from firesdk.models import PermissionBuffer

from enum import Enum

"""
Types of permissions. Least to most restrictive.

 - any
 - any authenticated users - them
 - basic users - them
 - manager users - their department
 - superuser (requires an actual user instance)

"""


class Permission(Enum):
    any_authenticated = 'any_authenticated'
    any_authenticated_manager_or_basic = 'any_authenticated_manager_or_basic'
    basic = 'basic'
    manager = 'manager'
    superuser = 'superuser'


# always requires a token, even though superuser perm doesn't use it. In this case, the token can be any valid token.
def check_perms(meta, user, permission_type, requested_company, requested_email_or_department):  # encode email first
    try:
        token = meta['HTTP_AUTHORIZATION']
    except KeyError:
        raise ValueError('No token found')

    try:
        cookie = meta['HTTP_COOKIE']
    except KeyError:
        raise ValueError('No session found')

    try:
        buffer = PermissionBuffer.objects.get(session_id=cookie)
    except PermissionBuffer.DoesNotExist:
        buffer = None

    if not verify_token(token, user, permission_type, buffer, requested_company, requested_email_or_department):
        raise ValueError('Invalid credentials/token')
    else:
        print('Permission Granted!')


# HERE: in this function, get the HTTP_COOKIE from META.
# if cookie != 'Not set', check the PermissionBuffer for an existing permission level account type.
# use a new func which takes permission_type and permission_level as args.
# this new func should return a boolean value whether or not the permission_level has permission to make a request of
# # permission_type level.

# Problem: when a user first opens the app, they may be unauthorized. However, this changes after login.
# how can we update the PermissionBuffer? change it in a sign in func? but that doesn't query this server. Look at swift
# code to see if there is a way we can update it.


def verify_token(token, user, permission_type, buffer, requested_company, requested_email_or_department):

    if buffer is None:
        raise ValueError('Invalid session')
    if buffer.is_obsolete:
        raise ValueError('Session expired')

    if permission_type == Permission.any_authenticated:
        return permission_any_authenticated(token, buffer, requested_company, requested_email_or_department)
    elif permission_type == Permission.any_authenticated_manager_or_basic:
        return permission_any_authenticated_manager_or_basic(token, buffer, requested_company,
                                                             requested_email_or_department)
    elif permission_type == Permission.basic:
        return permission_basic(token, buffer, requested_company, requested_email_or_department)
    elif permission_type == Permission.manager:
        return permission_manager(token, buffer, requested_company, requested_email_or_department)
    elif permission_type == Permission.superuser:
        return permission_superuser(user)
    else:
        print('Invalid permission type:', permission_type)
        return False


# no external requests. Therefore, no buffer check needed
def permission_any_authenticated(token, buffer, requested_company, requested_email):
    print('permission_any_authenticated')

    parsed_token = parse_token(token)

    # if parse_token(token) did not work
    if len(parsed_token) != 2:
        raise ValueError('Failed to parse token')

    token_dict = parsed_token[0]

    token_company = parsed_token[1]
    token_encoded_email = encode_email(token_dict['email'])

    if token_company == requested_company and token_encoded_email == requested_email:
        buffer.company = token_company
        buffer.encoded_email = token_encoded_email
        buffer.save()
        return True
    else:
        raise ValueError('Permission denied')


def permission_any_authenticated_manager_or_basic(token, buffer, requested_company, requested_email_and_department):
    print('permission_any_authenticated_manager_or_basic')

    parsed_token = parse_token(token)

    # if parse_token(token) did not work
    if len(parsed_token) != 2:
        raise ValueError('Failed to parse token')

    token_dict = parsed_token[0]

    token_company = parsed_token[1]
    token_encoded_email = encode_email(token_dict['email'])

    requested_email = requested_email_and_department[0]
    requested_department = requested_email_and_department[1]

    # buffer check HERE - account_type
    if buffer.account_type:
        token_account_type = buffer.account_type
    else:
        user_dict = get_user(token_company, token_encoded_email)
        token_account_type = user_dict['account_type']

    if token_account_type == 0:
        # basic
        if token_company == requested_company and token_encoded_email == requested_email:
            buffer.company = token_company
            buffer.encoded_email = token_encoded_email
            buffer.account_type = token_account_type
            buffer.save()
            return True
        else:
            raise ValueError('Permission denied')

    elif token_account_type == 1:
        # manager
        # buffer check HERE - department
        if buffer.department:
            token_department = buffer.department
        else:
            user_dict = get_user(token_company, token_encoded_email)
            token_department = user_dict['primary_department']

        if token_company == requested_company and token_department == requested_department:
            buffer.company = token_company
            buffer.encoded_email = token_encoded_email
            buffer.department = token_department
            buffer.account_type = token_account_type
            buffer.save()
            return True
        else:
            raise ValueError('Permission denied')

    else:
        raise ValueError('Illegal account type for current request')


def permission_basic(token, buffer, requested_company, requested_email):
    print('permission_basic')

    parsed_token = parse_token(token)

    # if parse_token(token) did not work
    if len(parsed_token) != 2:
        raise ValueError('Failed to parse token')

    token_dict = parsed_token[0]

    token_company = parsed_token[1]
    token_encoded_email = encode_email(token_dict['email'])

    # buffer check HERE - account_type
    if buffer.account_type:
        token_account_type = buffer.account_type
    else:
        user_dict = get_user(token_company, token_encoded_email)
        token_account_type = user_dict['account_type']

    if token_account_type != 0:
        raise ValueError('Illegal account type for current request')

    print('companyA:', token_company)
    print('companyB:', requested_company)
    print('emailA:', token_encoded_email)
    print('emailB:', requested_email)

    if token_company == requested_company and token_encoded_email == requested_email:
        buffer.company = token_company
        buffer.encoded_email = token_encoded_email
        buffer.account_type = token_account_type
        buffer.save()
        return True
    else:
        raise ValueError('Permission denied')


def permission_manager(token, buffer, requested_company, requested_department):
    print('permission_manager')

    parsed_token = parse_token(token)

    # if parse_token(token) did not work
    if len(parsed_token) != 2:
        raise ValueError('Failed to parse token')

    token_dict = parsed_token[0]

    token_company = parsed_token[1]
    token_encoded_email = encode_email(token_dict['email'])

    # buffer check HERE department, account_type

    if buffer.department and buffer.account_type:
        print('BBB')
        token_department = buffer.department
        token_account_type = buffer.account_type
    else:
        print('AAA')
        user_dict = get_user(token_company, token_encoded_email)
        token_department = user_dict['primary_department']
        token_account_type = user_dict['account_type']

    if token_account_type != 1:
        raise ValueError('Illegal account type for current request')

    print('companyA:', token_company)
    print('companyB:', requested_company)
    print('departmentA:', token_department)
    print('departmentB:', requested_department)

    if token_company == requested_company and token_department == requested_department:
        buffer.company = token_company
        buffer.encoded_email = token_encoded_email
        buffer.department = token_department
        buffer.account_type = token_account_type
        buffer.save()
        return True
    else:
        raise ValueError('Permission denied')


def permission_superuser(user):
    print('permission_superuser')
    if user.is_superuser:
        print('superuser!')
        return True
    else:
        print('NOT superuser:', user)
        return False


def parse_token(token):
    if token is not None:
        token_split = token.rsplit('.', 1)
        auth_token = token_split[0]

        try:
            company_name = token_split[1]
        except IndexError:
            print('No company name in token')
            return []

        try:
            decoded_token = auth.verify_id_token(auth_token)
        except ValueError:
            print('Invalid token.')
            return []

        parsed_token = [decoded_token, company_name]
        return parsed_token

    else:
        return []
