from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """
    Use when availability is not needed.
    """
    email = serializers.CharField(max_length=254)
    name = serializers.DictField(child=serializers.CharField(max_length=256))
    position = serializers.CharField(max_length=256)
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


class AvailabilitySerializer(serializers.Serializer):
    """
    Use for individual availability, when the user is specified.
    """
    availability = serializers.DictField(child=serializers.DictField(child=serializers.IntegerField(min_value=0,
                                                                                                    max_value=23)))

    def create(self, validated_data):
        print('AvailabilitySerializer created.')


class NeedsSerializer(serializers.Serializer):
    """
    Use for the needs of a department.
    """
    needs = serializers.DictField(child=serializers.ListField())
    shiftLength = serializers.DictField(child=serializers.IntegerField(min_value=0, max_value=24))
