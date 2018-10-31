from firesdk.models import CompanyId

from .basefirebase import *

from random import randint


def get_all_users():
    users_ref = db.collection(u'users')
    documents = users_ref.get()

    users = []

    for doc in documents:
        users.append(doc.to_dict())

    return users


def generate_schedule(weeks):
    user_list = get_all_users()

    # do magic in here to make schedule
    # this is where the fancy algorithm would go.
    try:
        num_of_weeks = int(weeks)
    except ValueError:
        return None

    new_user_list = []

    for user in user_list:
        # days uses one-hot encoding, 1 = true AND 0 = false
        schedule = []
        days = {'sunday': randint(0, 1), 'monday': randint(0, 1),
                'tuesday': randint(0, 1), 'wednesday': randint(0, 1),
                'thursday': randint(0, 1), 'friday': randint(0, 1),
                'saturday': randint(0, 1)}

        for i in range(num_of_weeks):
            schedule.append(days)

        user['days_working'] = schedule

        new_user_list.append(user)

    return new_user_list


def get_company_by_name(name):
    companies_ref = db.collection('companies').where('name', '==', name).limit(1).get()

    for current_company in companies_ref:
        return db.collection('companies').document(current_company.id)


def get_department_by_company_and_name(company, department):
    current_company = get_company_by_name(company)
    current_department = current_company.collection('departments').document(department)

    return current_department


# START POSTING TO DB


def add_company(company_dict):
    name = company_dict['name']
    data = {
        'name': name
    }

    new_company = db.collection('companies').document()
    new_company.set(data)

    CompanyId.objects.create(name=name, company_code=new_company.id)

    for dept in company_dict['departments']:
        new_dept = new_company.collection('departments').document(dept)
        new_dept.set({'name': dept})


def add_user(user_dict, company, department):
    encoded_email = user_dict['encoded_email']
    del user_dict['encoded_email']

    current_department = get_department_by_company_and_name(company, department)
    current_department.collection('users').document(encoded_email).set(user_dict)


def set_availability(availability_dict, company, department, email):
    current_department = get_department_by_company_and_name(company, department)

    user = current_department.collection('users').document(email)
    user.update({'availability': availability_dict})


def set_needs(needs_dict, company, department):
    current_department = get_department_by_company_and_name(company, department)
    current_department.update({'needs': needs_dict['needs'], 'shiftLength': needs_dict['shiftLength']})

# END POSTING TO DB

# **************************************


def get_company_from_local_db(company):
    company_id = CompanyId.objects.get(name=company).company_code
    current_company = db.collection('companies').document(company_id)

    return current_company


def get_department_from_local_db(company, department):
    current_company = get_company_from_local_db(company)
    current_department = current_company.collection('departments').document(department)

    return current_department

# START GETTING FROM DB


def get_users(company, department):
    current_department = get_department_from_local_db(company, department)

    users_ref = current_department.collection('users')
    user_docs = users_ref.get()

    users = []
    for user in user_docs:
        users.append(user.to_dict())

    return users


def get_user(company, department, email):
    current_department = get_department_from_local_db(company, department)

    user_ref = current_department.collection('users').document(email)
    user = user_ref.get()
    user_dict = user.to_dict()

    return user_dict


def get_needs(company, department):
    current_department = get_department_from_local_db(company, department).get()
    department_dict = current_department.to_dict()

    return department_dict


# END GETTING FROM DB
