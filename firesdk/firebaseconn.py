import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('/testing-c86ad-firebase-adminsdk-tbrlf-b5352272e5.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def getUsers():
    users_ref = db.collection(u'users')
    documents= users_ref.get()

    users = []

    for doc in documents:
        users.append(u'{} -> {}'.format(doc.id, doc.to_dict()))

    return users
