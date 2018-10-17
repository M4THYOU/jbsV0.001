import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

from firebase_testing import settings

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


def set_availability(day, start_hour, end_hour):
    pass
