from rest_framework import serializers

from serverauth.user_class import RegisteringUser

class RegisteringUserSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=256)


    def create(self, validated_data):
        return RegisteringUser(**validated_data)

    """
    def update(self, registering_user, validated_data):
        registering_user.username = validated_data.get('username', )"""
