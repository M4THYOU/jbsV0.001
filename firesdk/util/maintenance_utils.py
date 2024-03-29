from firesdk.models import PermissionBuffer

from firesdk.firebase_functions.firebaseconn import *
from .utils import month_delta

from datetime import datetime

# from firesdk.util.maintenance_utils import *


def cleanup_all_schedule_dates():
    for company in CompanyId.objects.all():
        cleanup_company_schedule_dates(company.name)


def cleanup_company_schedule_dates(company_name):
    company_ref = get_company_from_local_db(company_name)

    for user_document_snapshot in company_ref.collection('basic_users').get():
        user_dict = user_document_snapshot.to_dict()
        email = user_dict['email']
        encoded_email = encode_email(email)

        schedule_ref = get_user_schedule_ref(company_name, encoded_email)
        # get_user_time_off_ref(company_name, email)

        cleanup_user_schedule_dates(schedule_ref)

    cleanup_department_schedule_dates(company_name, company_ref)


def cleanup_user_schedule_dates(schedule_ref):
    schedule = schedule_ref.get()
    schedule_dict = schedule.to_dict()

    if schedule_dict is None:
        return

    current_date = datetime.now()
    two_months_prior_date = month_delta(current_date, -2)

    days_to_delete = []
    for date_string in schedule_dict['exact_times']:
        date = datetime.strptime(date_string, '%d/%m/%Y')

        if date < two_months_prior_date:
            days_to_delete.append(date_string)

    changes_made = False
    for date_string in days_to_delete:
        del schedule_dict['exact_times'][date_string]
        del schedule_dict['positions'][date_string]
        del schedule_dict['schedule'][date_string]

        changes_made = True

    if changes_made:
        schedule_ref.set(schedule_dict)


def cleanup_department_schedule_dates(company_name, company_ref):
    for department_document_snapshot in company_ref.collection('departments').get():
        department_dict = department_document_snapshot.to_dict()
        department_name = department_dict['name']

        department_schedule_ref = get_department_schedule_ref(company_name, department_name)
        department_schedule = department_schedule_ref.get()
        department_schedule_dict = department_schedule.to_dict()

        if department_schedule_dict is None:
            continue

        current_date = datetime.now()
        two_months_prior_date = month_delta(current_date, -2)

        days_to_delete = []
        for date_string in department_schedule_dict['exactTimes']:
            date = datetime.strptime(date_string, '%d/%m/%Y')

            if date < two_months_prior_date:
                days_to_delete.append(date_string)

        changes_made = False
        for date_string in days_to_delete:
            del department_schedule_dict['exactTimes'][date_string]
            del department_schedule_dict['positions'][date_string]
            del department_schedule_dict['schedules'][date_string]

            changes_made = True

        if changes_made:
            department_schedule_ref.set(department_schedule_dict)


def cleanup_permission_buffer():
    for buffer in PermissionBuffer.objects.all():
        if buffer.is_obsolete:
            print(buffer)
            buffer.delete()
