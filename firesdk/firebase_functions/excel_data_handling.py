import xlwt
import xlrd
import names
from random import randint

from firesdk.user_classes.users import XLSUser


def generate_users(number_of_users):
    first_names = []
    last_names = []

    for _ in range(number_of_users):
        first_names.append(names.get_first_name())
        last_names.append(names.get_last_name())

    return [last_names, first_names]


def users_to_xls(last_names, first_names):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Users')
    row = 0

    for last, first in zip(last_names, first_names):
        departments = random_departments()
        departments_str = ','.join(departments)

        ws.write(row, 0, last)  # last name
        ws.write(row, 1, first)  # first name
        ws.write(row, 2, 'fakeEmail@gmail.com' + str(row))  # email
        ws.write(row, 3, 'Store Standards Associate' + str(randint(0, 2)))  # position
        ws.write(row, 4, departments_str)
        ws.write(row, 5, randint(0, 1))  # is part time - 0:False, 1:True
        ws.write(row, 6, 0)  # account_type - 0:Basic, 1: Manager, 2: Master
        row += 1

    wb.save('sample_users.xls')


def random_departments():
    possible_departments = ['Store Standards', 'GHS', 'Customer Service']
    number_of_departments = randint(1, 3)

    used_departments = set([])
    for _ in range(number_of_departments):
        index = randint(0, 2)
        used_departments.add(possible_departments[index])

    return list(used_departments)


def create_data():
    user_count = 100

    name_list = generate_users(user_count)
    last_name_list = name_list[0]
    first_name_list = name_list[1]

    users_to_xls(last_name_list, first_name_list)


###############################################################


def parse_json_from_excel(data):

    users = []
    for user in data:
        last_name = data[user]['lastName']
        first_name = data[user]['firstName']
        email = user
        position = data[user]['position']
        departments = data[user]['departments']
        is_pt = data[user]['isPt']
        account_type = data[user]['accountType']

        current_user = XLSUser(last_name, first_name, email, position, departments, is_pt, account_type)
        users.append(current_user)

    return users
