from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class MainUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
 
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'email')
        extra_kwargs = {
            'password': {"write_only": True}
        }


class EmailUserSerializer(serializers.ModelSerializer):
    user = MainUserSerializer(read_only=False)

    class Meta:
        model = EmailUser
        fields = ["user", "avi"]

    def create(self, validated_data):
        """Create and return a new user."""

        user = User(
            email = validated_data['user']['email'],
            first_name = validated_data['user']['first_name'],
            last_name = validated_data['user']['last_name'],
            username = validated_data['user']['username']
        )

        user.set_password(validated_data['user']['password'])
        user.save()

        emailUser = EmailUser(
            avi = validated_data['avi'],
            user = user
        )

        emailUser.save()

        return emailUser