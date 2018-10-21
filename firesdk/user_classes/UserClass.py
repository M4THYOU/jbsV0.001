import datetime
from random import randint, choice

from firesdk.utils import Day


class UserClass:

    existing_users = 0

    def __init__(self, company, department, position, email, first_name, last_name, is_part_time=True):
        # Properties
        self.company = company
        self.department = department
        self.position = position
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_part_time = is_part_time

        # Availability
        self.sunday_hours = []
        self.monday_hours = []
        self.tuesday_hours = []
        self.wednesday_hours = []
        self.thursday_hours = []
        self.friday_hours = []
        self.saturday_hours = []

        self.min_hours_per_week = None
        self.max_hours_per_week = None
        self.min_shifts_per_week = None
        self.max_shifts_per_week = None

        self.number_of_days_available = None

        self.basic_availability_range = None
        self.daily_availability_range = None

        self.schedule = None

        # Calculated Availability
        self.days_available = []

        # General Statistics
        self.week_hours_for_current_schedule = None
        self.avg_hours_per_week = None

        # Testing Booleans
        self.is_availability_set = False
        self.is_basic_availability_range_set = False
        self.is_daily_availability_range_set = False
        self.is_schedule_set = False

    def get_company(self):
        return self.company

    def set_company(self, company):
        self.company = company

    def get_department(self):
        return self.department

    def set_department(self, department):
        self.department = department

    def get_position(self):
        return self.position

    def set_position(self, position):
        self.position = position

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email

    def get_first_name(self):
        return self.first_name

    def set_first_name(self, first_name):
        self.first_name = first_name

    def get_last_name(self):
        return self.last_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def get_is_part_time(self):
        return self.is_part_time

    def set_is_part_time(self, is_part_time):
        self.is_part_time = is_part_time

    def get_sunday_hours(self):
        return self.sunday_hours

    def set_sunday_hours(self, sunday_hours):
        self.sunday_hours = sunday_hours

    def get_monday_hours(self):
        return self.monday_hours

    def set_monday_hours(self, monday_hours):
        self.monday_hours = monday_hours

    def get_tuesday_hours(self):
        return self.tuesday_hours

    def set_tuesday_hours(self, tuesday_hours):
        self.tuesday_hours = tuesday_hours

    def get_wednesday_hours(self):
        return self.wednesday_hours

    def set_wednesday_hours(self, wednesday_hours):
        self.wednesday_hours = wednesday_hours

    def get_thursday_hours(self):
        return self.thursday_hours

    def set_thursday_hours(self, thursday_hours):
        self.thursday_hours = thursday_hours

    def get_friday_hours(self):
        return self.friday_hours

    def set_friday_hours(self, friday_hours):
        self.friday_hours = friday_hours

    def get_saturday_hours(self):
        return self.saturday_hours

    def set_saturday_hours(self, saturday_hours):
        self.saturday_hours = saturday_hours

    def get_min_hours(self):
        return self.min_hours_per_week

    def set_min_hours(self, min_hours_per_week):
        self.min_hours_per_week = min_hours_per_week

    def get_max_hours(self):
        return self.max_hours_per_week

    def set_max_hours(self, max_hours_per_week):
        self.max_hours_per_week = max_hours_per_week

    def get_min_shifts(self):
        return self.min_shifts_per_week

    def set_min_shifts(self, min_shifts_per_week):
        self.min_shifts_per_week = min_shifts_per_week

    def get_max_shifts(self):
        return self.max_shifts_per_week

    def set_max_shifts(self, max_shifts_per_week):
        self.max_shifts_per_week = max_shifts_per_week

    # START - DO WORK WITH THESE METHODS LATER
    def get_week_hours_for_current_schedule(self):
        return self.week_hours_for_current_schedule

    def set_week_hours_for_current_schedule(self, hours):
        self.week_hours_for_current_schedule = hours

    def get_avg_hours_per_week(self):
        return self.avg_hours_per_week

    def set_avg_hours_per_week(self, avg_hours_per_week):
        self.avg_hours_per_week = avg_hours_per_week
    # END - DO WORK WITH THESE METHODS LATER

    def get_is_availability_set(self):
        return self.is_availability_set

    def set_is_availability_set(self, is_set):
        self.is_availability_set = is_set

    def get_is_basic_availability_range_set(self):
        return self.is_basic_availability_range_set

    def set_is_basic_availability_range_set(self, is_set):
        self.is_basic_availability_range_set = is_set

    def get_is_daily_availability_range_set(self):
        return self.is_daily_availability_range_set

    def set_is_daily_availability_range_set(self, is_set):
        self.is_daily_availability_range_set = is_set

    def get_is_schedule_set(self):
        return self.is_schedule_set

    def set_is_schedule_set(self, is_set):
        self.is_schedule_set = is_set

    def get_basic_availability_range(self):
        return self.basic_availability_range

    def set_basic_availability_range(self, basic_availability_range):
        self.basic_availability_range = basic_availability_range
        self.set_is_basic_availability_range_set(True)

    def get_daily_availability_range(self):
        return self.daily_availability_range

    def set_daily_availability_range(self, daily_availability_range):
        self.daily_availability_range = daily_availability_range
        self.set_is_daily_availability_range_set(True)

    def get_schedule(self):
        return self.schedule

    def set_schedule(self, schedule):
        self.schedule = schedule
        self.set_is_schedule_set(True)

    # Calculated Availability
    def set_days_available(self):
        days_available = []

        if self.get_sunday_hours() is None:
            days_available.append(0)
        else:
            days_available.append(1)
        if self.get_monday_hours() is None:
            days_available.append(0)
        else:
            days_available.append(1)
        if self.get_tuesday_hours() is None:
            days_available.append(0)
        else:
            days_available.append(1)
        if self.get_wednesday_hours() is None:
            days_available.append(0)
        else:
            days_available.append(1)
        if self.get_thursday_hours() is None:
            days_available.append(0)
        else:
            days_available.append(1)
        if self.get_friday_hours() is None:
            days_available.append(0)
        else:
            days_available.append(1)
        if self.get_saturday_hours() is None:
            days_available.append(0)
        else:
            days_available.append(1)

        self.days_available = days_available

        self.check_availability()

    def get_days_available(self):
        return self.days_available

    def get_number_of_days_available(self):
        return self.get_days_available().count(1)

    def set_availability(self, sunday_hours, monday_hours,
                         tuesday_hours, wednesday_hours, thursday_hours,
                         friday_hours, saturday_hours, min_hours, max_hours,
                         min_shifts, max_shifts):

        self.set_day_hours(Day.sunday, sunday_hours)
        self.set_day_hours(Day.monday, monday_hours)
        self.set_day_hours(Day.tuesday, tuesday_hours)
        self.set_day_hours(Day.wednesday, wednesday_hours)
        self.set_day_hours(Day.thursday, thursday_hours)
        self.set_day_hours(Day.friday, friday_hours)
        self.set_day_hours(Day.saturday, saturday_hours)
        self.set_min_hours(min_hours)
        self.set_max_hours(max_hours)
        self.set_min_shifts(min_shifts)
        self.set_max_shifts(max_shifts)

        self.set_days_available()

        self.check_availability()
        self.set_is_availability_set(True)

    def check_availability(self):
        if self.get_number_of_days_available() < self.get_max_shifts():
            self.number_of_days_available = self.get_max_shifts()

        min_shift_length = self.get_department().get_min_shift_length()

        availability_dict = self.get_all_availabilities_dict()

        for day, availability in availability_dict.items():

            if availability is not None:
                first_hour = availability[0].hour
                last_hour = availability[1].hour
                number_of_hours = last_hour - first_hour

                while number_of_hours < min_shift_length:
                    if last_hour < 23:
                        availability[1] = datetime.time(availability[1].hour + 1)
                    else:
                        availability[0] = datetime.time(availability[0].hour - 1)

                    number_of_hours = availability[1].hour - availability[0].hour

                self.set_day_hours(day, availability)

    def set_day_hours(self, day, hours):
        if day == Day.sunday:
            self.set_sunday_hours(hours)
        elif day == Day.monday:
            self.set_monday_hours(hours)
        elif day == Day.tuesday:
            self.set_tuesday_hours(hours)
        elif day == Day.wednesday:
            self.set_wednesday_hours(hours)
        elif day == Day.thursday:
            self.set_thursday_hours(hours)
        elif day == Day.friday:
            self.set_friday_hours(hours)
        elif day == Day.saturday:
            self.set_saturday_hours(hours)
        else:
            raise ValueError('Invalid \'day\' specified.')

    def get_all_availabilities_dict(self):
        sunday = self.get_sunday_hours()
        monday = self.get_monday_hours()
        tuesday = self.get_tuesday_hours()
        wednesday = self.get_wednesday_hours()
        thursday = self.get_thursday_hours()
        friday = self.get_friday_hours()
        saturday = self.get_saturday_hours()

        availabilities = {Day.sunday: sunday, Day.monday: monday, Day.tuesday: tuesday, Day.wednesday: wednesday,
                          Day.thursday: thursday, Day.friday: friday, Day.saturday: saturday}

        return availabilities

    def update_values(self):
        self.set_days_available()

    def __str__(self):
        return (self.get_first_name() + ' ' + self.get_last_name() + ' - ' +
                self.get_position() + ' at ' + self.get_company())

    def availability_to_string(self):

        availability = ('Min Hours: ' + str(self.get_min_hours()) + '\n' +
                        'Max Hours: ' + str(self.get_max_hours()) + '\n' +
                        'Min Shifts: ' + str(self.get_min_shifts()) + '\n' +
                        'Max Shifts: ' + str(self.get_max_shifts()) + '\n')

        days = [self.get_sunday_hours(), self.get_monday_hours(),
                self.get_tuesday_hours(), self.get_wednesday_hours(),
                self.get_thursday_hours(), self.get_friday_hours(),
                self.get_saturday_hours()]

        for day in days:
            raw_hours = day

            if raw_hours is None:
                availability += 'Unavailable\n'
                continue

            start_hour_d = datetime.datetime.strptime(str(raw_hours[0])[:5], '%H:%M')
            end_hour_d = datetime.datetime.strptime(str(raw_hours[1])[:5], '%H:%M')

            start_hour = start_hour_d.strftime('%I:%M %p')
            end_hour = end_hour_d.strftime('%I:%M %p')

            if day == self.get_sunday_hours():
                time_string = str('Sunday: ' + start_hour + ' - ' + end_hour + '\n')
            elif day == self.get_monday_hours():
                time_string = str('Monday: ' + start_hour + ' - ' + end_hour + '\n')
            elif day == self.get_tuesday_hours():
                time_string = str('Tuesday: ' + start_hour + ' - ' + end_hour + '\n')
            elif day == self.get_wednesday_hours():
                time_string = str('Wednesday: ' + start_hour + ' - ' + end_hour + '\n')
            elif day == self.get_thursday_hours():
                time_string = str('Thursday: ' + start_hour + ' - ' + end_hour + '\n')
            elif day == self.get_friday_hours():
                time_string = str('Friday: ' + start_hour + ' - ' + end_hour + '\n')
            elif day == self.get_saturday_hours():
                time_string = str('Saturday: ' + start_hour + ' - ' + end_hour + '\n')
            else:
                time_string = 'An error occurred geting the time.'

            availability += time_string

        return availability
