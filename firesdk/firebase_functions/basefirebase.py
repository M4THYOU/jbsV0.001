import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

from firebase_testing import settings
import os

cred_path = os.path.join(settings.BASE_DIR, 'serviceAccount.json')

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()
