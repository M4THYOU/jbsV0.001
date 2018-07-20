from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=256)
    firstName = serializers.CharField(max_length=256)
    lastName = serializers.CharField(max_length=256)
    email = serializers.EmailField(max_length=254)

    days_working = serializers.ListField(child=serializers.DictField())

    def create(self, validated_data):
        print("UserSerializer created")
