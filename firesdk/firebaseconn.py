import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from firebase_testing import settings
from firesdk.utils import Day
from .models import CompanyId

import os
from random import randint

cred_path = os.path.join(settings.BASE_DIR, 'serviceAccount.json')

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()


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


def set_availability(availability_dict, company, department, email):
    current_company = get_company_by_name(company)
    department = current_company.collection('departments').document(department)

    user = department.collection('users').document(email)
    user.update({'availability': availability_dict})


def add_user(user_dict, company, department):
    current_company = get_company_by_name(company)

    department = current_company.collection('departments').document(department)
    department.collection('users').document(user_dict['email']).set(user_dict)


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
