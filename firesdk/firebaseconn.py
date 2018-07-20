import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from firebase_testing import settings
import os

cred_path = os.path.join(settings.BASE_DIR, 'serviceAccount.json')

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

def get_all_users():
    users_ref = db.collection(u'users')
    documents= users_ref.get()

    users = []

    for doc in documents:
        users.append(u'{}'.format(doc.to_dict()))

    return users

def generate_schedule():
    user_list = get_all_users()

    #do magic in here to make schedule
    for user in user_list:
        pass
