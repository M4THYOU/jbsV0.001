from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """
    Use when availability is not needed.
    """
    email = serializers.CharField(max_length=254)
    name = serializers.DictField(child=serializers.CharField(max_length=256))
    position = serializers.CharField(max_length=256)
    # departments = serializers.ListField(child=serializers.DictField(child=serializers.CharField(max_length=256)))
    primary_department = serializers.CharField(max_length=256)
    account_type = serializers.IntegerField(min_value=0, max_value=2)
    is_part_time = serializers.BooleanField()

    def create(self, validated_data):
        print('UserSerializer created.')


class UserSerializerWithAvailability(UserSerializer):
    """
    Use when getting the availability of more than 1 user, or that user's identifier is not known.
    """
    availability = serializers.DictField(child=serializers.DictField(child=serializers.IntegerField(min_value=0,
                                                                                                    max_value=23)))

    def create(self, validated_data):
        print('UserSerializerWithAvailability created.')


class LoginBoolsSerializer(serializers.Serializer):
    """
    Use for getting individual user login booleans, is_password_changed and is_onboard_complete.
    """
    is_password_changed = serializers.BooleanField()
    is_onboard_complete = serializers.BooleanField()

    def create(self, validated_data):
        print('LoginBoolsSerializer created.')

########################################################################################################################


class AvailabilitySerializer(serializers.Serializer):
    """
    Use only as nested serializer of AvailabilitySerializer for the actual availability.
    """

    departments = serializers.ListField(child=serializers.DictField(child=serializers.CharField(max_length=256)))
    is_part_time = serializers.BooleanField()

    hours = serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=84))
    shifts = serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=7))

    sunday = serializers.DictField()
    monday = serializers.DictField()
    tuesday = serializers.DictField()
    wednesday = serializers.DictField()
    thursday = serializers.DictField()
    friday = serializers.DictField()
    saturday = serializers.DictField()

    def create(self, validated_data):
        print('AvailabilityDaySerializer created.')


class FullAvailabilitySerializer(serializers.Serializer):
    """
    Use for full availability of a department.
    """

    users = serializers.DictField(serializers.DictField(child=AvailabilitySerializer()))


########################################################################################################################


class NeedsSerializer(serializers.Serializer):
    """
    Use for the needs of a department.
    """
    needs = serializers.DictField(child=serializers.ListField())
    shiftLength = serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=24))


class OpenHoursSerializer(serializers.Serializer):
    """
    Use for the OpenHours of a department.
    """
    sunday = serializers.DictField(child=serializers.FloatField())
    monday = serializers.DictField(child=serializers.FloatField())
    tuesday = serializers.DictField(child=serializers.FloatField())
    wednesday = serializers.DictField(child=serializers.FloatField())
    thursday = serializers.DictField(child=serializers.FloatField())
    friday = serializers.DictField(child=serializers.FloatField())
    saturday = serializers.DictField(child=serializers.FloatField())


class AccountTypeSerializer(serializers.Serializer):
    """
    Use for the AccountType of a user.
    """
    account_type = serializers.IntegerField(min_value=0, max_value=2)


class FullScheduleSerializer(serializers.Serializer):
    """
    Use for the department's full schedule.
    """
    exactTimes = serializers.DictField(child=serializers.DictField(child=serializers.CharField(max_length=30)))
    positions = serializers.DictField(child=serializers.DictField(child=serializers.CharField(max_length=100)))
    schedules = serializers.DictField(child=serializers.DictField(
        child=serializers.ListField(child=serializers.CharField(max_length=254))))


class UserScheduleSerializer(serializers.Serializer):
    """
    Use for an individual user's full schedule.
    """
    exact_times = serializers.DictField(child=serializers.CharField(max_length=30))
    positions = serializers.DictField(child=serializers.CharField(max_length=100))
    schedule = serializers.DictField(child=serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=1)))


class TimeOffSerializer(serializers.Serializer):
    """
    Use for an individual user's time off requests.
    """
    reasons = serializers.DictField(child=serializers.CharField(max_length=400))
    statuses = serializers.DictField(child=serializers.DictField(child=serializers.BooleanField()))


class FullTimeOffSerializer(serializers.Serializer):
    """
    Use for all of a department's time off requests.
    """
    time_off_requests = serializers.ListField(child=serializers.DictField(child=serializers.CharField(max_length=400)))
