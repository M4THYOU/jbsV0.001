import xlwt, xlrd
import names


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
        ws.write(row, 0, last)
        ws.write(row, 1, first)
        ws.write(row, 2, 'fakeEmail@gmail.com')
        row += 1

    wb.save('sample_users.xls')


def create_data():
    user_count = 100

    name_list = generate_users(user_count)
    last_name_list = name_list[0]
    first_name_list = name_list[1]

    users_to_xls(last_name_list, first_name_list)


###############################################################


def read_xls():
    pass