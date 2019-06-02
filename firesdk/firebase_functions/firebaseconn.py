from firesdk.models import CompanyId

from .basefirebase import *
from firesdk.util.utils import org_names_filter, department_list_to_dict, int_to_account_type, AccountType, encode_email

from random import randint


def get_all_users():
    basic_users_ref = db.collection(u'basic_users')
    manager_users_ref = db.collection(u'manager_users')

    basic_user_documents = basic_users_ref.get()
    manager_user_documents = manager_users_ref.get()

    users = []

    for doc in basic_user_documents:
        users.append(doc.to_dict())

    for doc in manager_user_documents:
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


def add_user(user_dict, company):
    account_type = int_to_account_type(user_dict['account_type'])

    if account_type == AccountType.basic:
        add_basic_user(user_dict, company)
    elif account_type == AccountType.manager:
        add_manager_user(user_dict, company)
    elif account_type == AccountType.master:
        add_master_user(user_dict, company)


def add_basic_user(user_dict, company):
    company_code = get_company_code_by_name(company)

    user_dict['primary_department'] = org_names_filter(user_dict['departments'][0])

    departments = []
    for department in user_dict['departments']:
        department_doc = db.document('companies/' + company_code + '/departments/' + org_names_filter(department))
        departments.append(department_doc)

    user_dict['departments'] = departments

    new_user_dict = {
        'email': user_dict['email'],
        'name': user_dict['name'],
        'position': user_dict['position'],
        'primary_department': user_dict['primary_department'],
        'account_type': user_dict['account_type']
    }

    new_onboarding = {
        'is_password_changed': False,
        'is_onboard_complete': False
    }

    new_avail = {
        'is_part_time': user_dict['is_part_time'],
        'departments': departments
    }

    encoded_email = user_dict['encoded_email']
    current_company = get_company_by_name(company)

    current_company.collection('basic_users').document(encoded_email).set(new_user_dict)
    current_company.collection('basic_users').document(encoded_email + '/scheduling/onboarding').set(new_onboarding)
    current_company.collection('basic_users').document(encoded_email + '/scheduling/availability').set(new_avail)


def add_manager_user(user_dict, company):
    user_dict['primary_department'] = org_names_filter(user_dict['departments'][0])

    new_user_dict = {
        'email': user_dict['email'],
        'name': user_dict['name'],
        'position': user_dict['position'],
        'primary_department': user_dict['primary_department'],
        'account_type': user_dict['account_type']
    }

    new_onboarding = {
        'is_password_changed': False,
        'is_onboard_complete': False
    }

    new_avail = {
        'is_part_time': user_dict['is_part_time'],
    }

    encoded_email = user_dict['encoded_email']
    current_company = get_company_by_name(company)

    current_company.collection('manager_users').document(encoded_email).set(new_user_dict)
    current_company.collection('manager_users').document(encoded_email + '/scheduling/onboarding').set(new_onboarding)
    current_company.collection('manager_users').document(encoded_email + '/scheduling/availability').set(new_avail)


def add_master_user(user_dict, company):
    pass


def set_availability(availability_dict, company, email):
    availability = get_user_availability_ref(company, email)
    availability.update(availability_dict)


def set_needs(needs_dict, company, department):
    needs = get_department_needs_ref(company, department)
    # needs.update({'needs': needs_dict['needs'], 'shiftLength': needs_dict['shiftLength']})
    needs.set(needs_dict, merge=True)


def set_department_schedule(schedule_dict, company, department):
    schedule = get_department_schedule_ref(company, department)
    schedule.set(schedule_dict)


def set_all_users_schedule(schedule_dict, company, department, merge=True):
    all_department_basic_users = get_users(company, department)

    for user in all_department_basic_users:
        email = user['email']

        exact_times = {}
        positions = {}
        schedule = {}

        for date_string, users_dict in schedule_dict['exactTimes'].items():
            if email in users_dict:
                exact_times[date_string] = users_dict[email]
                positions[date_string] = schedule_dict['positions'][date_string][email]
                schedule[date_string] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                print(schedule_dict['schedules'][date_string])
                for hour, user_list in schedule_dict['schedules'][date_string].items():
                    if email in user_list:
                        schedule[date_string][int(hour)] = 1
                    else:
                        schedule[date_string][int(hour)] = 0

        user_schedule = {
            'exact_times': exact_times,
            'positions': positions,
            'schedule': schedule
        }

        set_user_schedule(user_schedule, company, email, merge)


def set_user_schedule(days_dict, company, email, merge):
    """
    days: dictionary of days of the week. Each item is a list of 24 hours working (or not) said day.
    0 = not working, 1 = working
    """
    encoded_email = encode_email(email)

    schedule = get_user_schedule_ref(company, encoded_email)
    schedule.set(days_dict, merge=merge)


def set_department_time_off_requests(time_off_dict, company, department, email):
    time_off_ref = get_department_time_off_ref(company, department)
    user_time_off_requests = {
        email: time_off_dict
    }
    time_off_ref.set(user_time_off_requests, merge=True)


def set_single_department_time_off_request(time_off_dict, company, department, email):
    time_off_ref = get_department_time_off_ref(company, department)
    time_off = time_off_ref.get()
    existing_time_off_dict = time_off.to_dict()

    updating_date = time_off_dict['date']
    updating_reason = time_off_dict['reason']
    updating_status = time_off_dict['status']

    if existing_time_off_dict is not None:
        existing_time_off_dict[email]['reasons'][updating_date] = updating_reason
        existing_time_off_dict[email]['statuses'][updating_date] = updating_status
    else:
        existing_time_off_dict = {
            email: {
                'reasons': {
                    updating_date: updating_reason
                },
                'statuses': {
                    updating_date: updating_status
                }
            }
        }

    time_off_ref.set(existing_time_off_dict)


def update_single_department_time_off_request_no_reason(time_off_dict, company, department, email):
    time_off_ref = get_department_time_off_ref(company, department)
    time_off = time_off_ref.get()
    existing_time_off_dict = time_off.to_dict()

    updating_date = time_off_dict['date']
    updating_status = time_off_dict['status']

    if existing_time_off_dict is not None:
        existing_time_off_dict[email]['statuses'][updating_date] = updating_status
    else:
        existing_time_off_dict = {
            email: {
                'statuses': {
                    updating_date: updating_status
                }
            }
        }

    print(existing_time_off_dict)
    print(updating_date, updating_status)

    time_off_ref.set(existing_time_off_dict, merge=True)


def set_user_time_off_requests(time_off_days_dict, company, email):
    encoded_email = encode_email(email)

    time_off = get_user_time_off_ref(company, encoded_email)
    time_off.set(time_off_days_dict)


def set_user_time_off_requests_merge(time_off_days_dict, company, email):
    encoded_email = encode_email(email)

    time_off = get_user_time_off_ref(company, encoded_email)
    time_off.set(time_off_days_dict, merge=True)


def set_single_time_off_request(time_off_dict, company, email):
    encoded_email = encode_email(email)

    time_off_ref = get_user_time_off_ref(company, encoded_email)
    time_off = time_off_ref.get()
    existing_time_off_dict = time_off.to_dict()

    updating_date = time_off_dict['date']
    updating_reason = time_off_dict['reason']
    updating_status = time_off_dict['status']

    if existing_time_off_dict is not None:
        existing_time_off_dict['reasons'][updating_date] = updating_reason
        existing_time_off_dict['statuses'][updating_date] = updating_status
    else:
        existing_time_off_dict = {
            'reasons': {
                updating_date: updating_reason
            },
            'statuses': {
                updating_date: updating_status
            }
        }

    time_off_ref.set(existing_time_off_dict)


def update_single_time_off_request_no_reason(time_off_dict, company, email):
    encoded_email = encode_email(email)

    time_off_ref = get_user_time_off_ref(company, encoded_email)
    time_off = time_off_ref.get()
    existing_time_off_dict = time_off.to_dict()

    updating_date = time_off_dict['date']
    updating_status = time_off_dict['status']

    if existing_time_off_dict is not None:
        existing_time_off_dict['statuses'][updating_date] = updating_status
    else:
        existing_time_off_dict = {
            'statuses': {
                updating_date: updating_status
            }
        }

    time_off_ref.set(existing_time_off_dict, merge=True)


def add_metric_event(events):
    metrics_ref = db.collection('metrics')

    for event in events:
        print(event)
        new_event = metrics_ref.document()
        new_event.set(event)


def set_department_saved_shifts(shifts_dict, company, department):
    saved_shifts_ref = get_department_saved_shifts_ref(company, department)
    # saved_shifts = saved_shifts_ref.get()
    # saved_shifts_dict = saved_shifts.to_dict()

    saved_shifts_ref.set(shifts_dict)


# END POSTING TO DB

# START DELETING FROM DB

def delete_department_time_off_request(date, company, department, email):
    time_off_ref = get_department_time_off_ref(company, department)
    time_off = time_off_ref.get()
    existing_time_off_dict = time_off.to_dict()

    try:
        del existing_time_off_dict[email]['reasons'][date]
        del existing_time_off_dict[email]['statuses'][date]
    except KeyError:
        print('Date,', date + ', does not exist.')
        return

    time_off_ref.set(existing_time_off_dict)


def delete_time_off_request(date, company, email):
    encoded_email = encode_email(email)

    time_off_ref = get_user_time_off_ref(company, encoded_email)
    time_off = time_off_ref.get()
    existing_time_off_dict = time_off.to_dict()

    try:
        del existing_time_off_dict['reasons'][date]
        del existing_time_off_dict['statuses'][date]
    except KeyError:
        print('Date,', date + ', does not exist.')
        return

    time_off_ref.set(existing_time_off_dict)


# END DELETING FROM DB

# **************************************


def get_company_name_by_company_code(company_code):
    company_name = CompanyId.objects.get(company_code=company_code).name

    return company_name


def get_company_code_by_name(name):
    company_code = CompanyId.objects.get(name=name).company_code

    return company_code


def get_company_from_local_db(company):
    company_id = CompanyId.objects.get(name=company).company_code
    current_company = db.collection('companies').document(company_id)

    return current_company


def get_department_from_local_db(company, department):
    current_company = get_company_from_local_db(company)
    current_department = current_company.collection('departments').document(department)

    return current_department

# START GETTING REFS FROM DB


def get_user_ref(company, email):
    current_company = get_company_by_name(company)

    if not current_company:
        print('Company \"' + company + '\" not found.')
        return

    user_ref = current_company.collection('basic_users').document(email)

    if not user_ref.get().exists:
        user_ref = current_company.collection('manager_users').document(email)
        user_ref.get()

    if not user_ref.get().exists:
        print('User:', email, 'not found in company:', company)
        print(current_company)
        user_ref = None
        # if you get none for this, it's probably because you forgot to encode the email with encode_email(email)

    return user_ref


def get_user_availability_ref(company, email):
    user = get_user_ref(company, email)
    availability = user.collection('scheduling').document('availability')

    return availability


def get_user_onboard_ref(company, email):
    user = get_user_ref(company, email)
    onboarding = user.collection('scheduling').document('onboarding')

    return onboarding


def get_user_schedule_ref(company, email):
    user = get_user_ref(company, email)
    schedule = user.collection('scheduling').document('schedule')

    return schedule


def get_user_time_off_ref(company, email):
    user = get_user_ref(company, email)
    time_off = user.collection('scheduling').document('time_off')

    return time_off


def get_department_needs_ref(company, department):
    current_department = get_department_from_local_db(company, department)
    needs = current_department.collection('scheduling').document('needs')

    return needs


def get_department_schedule_ref(company, department):
    current_department = get_department_from_local_db(company, department)
    schedule = current_department.collection('scheduling').document('schedule')

    return schedule


def get_department_saved_shifts_ref(company, department):
    current_department = get_department_from_local_db(company, department)
    saved_shifts = current_department.collection('scheduling').document('saved_shifts')

    return saved_shifts


def get_department_time_off_ref(company, department):
    current_department = get_department_from_local_db(company, department)
    time_off = current_department.collection('scheduling').document('time_off')

    return time_off


def get_user_collection_for_department_ref(company, department):
    current_company = get_company_by_name(company)
    users_ref = current_company.collection('basic_users')

    users_for_department_ref = users_ref.where('primary_department', '==', department)

    return users_for_department_ref


# END GETTING REFS FROM DB

# START GETTING FROM DB


def get_users(company, department):
    current_company = get_company_from_local_db(org_names_filter(company))
    department_name = org_names_filter(department)

    users_ref = current_company.collection('basic_users')
    user_docs = users_ref.where('primary_department', '==', department_name).get()

    users = []
    for user in user_docs:
        user_dict = user.to_dict()

        availability_ref = get_user_availability_ref(company, encode_email(user_dict['email']))
        availability = availability_ref.get()
        availability_dict = availability.to_dict()
        user_dict['is_part_time'] = availability_dict['is_part_time']

        # new_departments = department_list_to_dict(user_dict['departments'])

        # user_dict['departments'] = new_departments

        users.append(user_dict)

    return users


def get_user(company, email):  # make sure it's an encoded email.
    user_ref = get_user_ref(company, email)

    if not user_ref:
        print('User \"' + email + '\" not found at company \"' + company + '\".')
        return

    user = user_ref.get()
    user_dict = user.to_dict()

    availability_ref = get_user_availability_ref(company, email)
    availability = availability_ref.get()
    availability_dict = availability.to_dict()
    user_dict['is_part_time'] = availability_dict['is_part_time']

    return user_dict


def get_availability(company, email):
    availability_ref = get_user_availability_ref(company, email)
    availability = availability_ref.get()
    availability_dict = availability.to_dict()

    # departments are initially stored as Firestore references. This func changes them to strings.
    new_departments = department_list_to_dict(availability_dict['departments'])
    availability_dict['departments'] = new_departments

    return availability_dict


def get_login_bools(company, email):
    onboard_ref = get_user_onboard_ref(company, email)
    onboard = onboard_ref.get()
    onboard_dict = onboard.to_dict()

    return onboard_dict


def get_needs(company, department):
    needs_ref = get_department_needs_ref(company, department)
    needs = needs_ref.get()
    needs_dict = needs.to_dict()

    return needs_dict


def get_full_schedule(company, department):
    department_schedule_ref = get_department_schedule_ref(company, department)
    department_schedule = department_schedule_ref.get()
    department_schedule_dict = department_schedule.to_dict()

    return department_schedule_dict


def get_user_schedule(company, email):  # assumes email is already encoded
    schedule_ref = get_user_schedule_ref(company, email)
    schedule = schedule_ref.get()
    schedule_dict = schedule.to_dict()

    return schedule_dict


def get_user_time_off(company, email):  # assumes email is already encoded
    time_off_ref = get_user_time_off_ref(company, email)
    time_off = time_off_ref.get()
    time_off_dict = time_off.to_dict()

    return time_off_dict


def get_department_saved_shifts(company, department):
    saved_shifts_ref = get_department_saved_shifts_ref(company, department)
    saved_shifts = saved_shifts_ref.get()
    saved_shifts_dict = saved_shifts.to_dict()

    if saved_shifts_dict is None:
        return {}

    return saved_shifts_dict

# END GETTING FROM DB

# START SETTING LOGIN BOOLEANS


def set_login_bools(login_bools_dict, company, email):
    is_password_changed = login_bools_dict['is_password_changed']
    is_onboard_complete = login_bools_dict['is_onboard_complete']

    user = get_user_ref(company, email)
    onboarding = user.collection('scheduling').document('onboarding')
    onboarding.update({'is_password_changed': is_password_changed, 'is_onboard_complete': is_onboard_complete})

# END SETTING LOGIN BOOLEANS

# START PROMOTE/DEMOTE


def promote_to_manager(company, email):
    company_code = get_company_code_by_name(company)
    encoded_email = encode_email(email)

    basic_user_ref = db.document('companies/' + company_code + '/basic_users/' + encoded_email)

    availability_ref = db.document('companies/' + company_code + '/basic_users/' + encoded_email +
                                   '/scheduling/availability')
    onboarding_ref = db.document('companies/' + company_code + '/basic_users/' + encoded_email +
                                 '/scheduling/onboarding')

    basic_user = basic_user_ref.get()
    availability = availability_ref.get()
    onboarding = onboarding_ref.get()

    basic_user_dict = basic_user.to_dict()
    avail_dict = availability.to_dict()
    onboarding_dict = onboarding.to_dict()

    basic_user_dict['account_type'] = 1

    current_company = get_company_by_name(company)
    current_company.collection('manager_users').document(encoded_email).set(basic_user_dict)
    current_company.collection('manager_users').document(encoded_email + '/scheduling/onboarding').set(onboarding_dict)
    current_company.collection('manager_users').document(encoded_email + '/scheduling/availability').set(avail_dict)

    onboarding_ref.delete()
    availability_ref.delete()
    basic_user_ref.delete()


def demote_to_basic(company, email):
    company_code = get_company_code_by_name(company)
    encoded_email = encode_email(email)

    manager_user_ref = db.document('companies/' + company_code + '/manager_users/' + encoded_email)

    availability_ref = db.document('companies/' + company_code + '/manager_users/' + encoded_email +
                                   '/scheduling/availability')
    onboarding_ref = db.document('companies/' + company_code + '/manager_users/' + encoded_email +
                                 '/scheduling/onboarding')

    manager_user = manager_user_ref.get()
    availability = availability_ref.get()
    onboarding = onboarding_ref.get()

    manager_user_dict = manager_user.to_dict()
    avail_dict = availability.to_dict()
    onboarding_dict = onboarding.to_dict()

    print(manager_user_dict['account_type'])
    manager_user_dict['account_type'] = 0

    current_company = get_company_by_name(company)
    current_company.collection('basic_users').document(encoded_email).set(manager_user_dict)
    current_company.collection('basic_users').document(encoded_email + '/scheduling/onboarding').set(onboarding_dict)
    current_company.collection('basic_users').document(encoded_email + '/scheduling/availability').set(avail_dict)

    onboarding_ref.delete()
    availability_ref.delete()
    manager_user_ref.delete()


# END PROMOTE/DEMOTE # from firesdk.firebase_functions.firebaseconn import promote_to_manager
