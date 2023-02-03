from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class MainUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email')


class EmailUserSerializer(serializers.ModelSerializer):
    user = MainUserSerializer(read_only=True)

    class Meta:
        model = EmailUser
        fields = ["avi", "user"]