from .basefirebase import *
from firesdk.models import CompanyId


def is_valid_company_code(code):
    is_valid = False

    for company in CompanyId.objects.all():
        if company.company_code == code:
            is_valid = True

    return is_valid
