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

# It creates a new user and a new emailUser, and then saves them both
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

# It's a serializer that validates the old password, the new password, and the confirmation of the new
# password
class ChangePasswordSerializer(serializers.ModelSerializer):

    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)
 
    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.id != instance.id:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        instance.set_password(validated_data['new_password'])
        instance.is_active = True
        instance.save()

        return instance

# This class is used to update the user's first name, last name, email, and username
class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    avi = serializers.ImageField(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'avi')


    # def validate_email(self, value):
    #     user = self.context['request'].user
    #     if User.objects.exclude(id=user.id).filter(email=value).exists():
    #         raise serializers.ValidationError({"email": "This email is already in use."})
    #     return value

    # def validate_username(self, value):
    #     user = self.context['request'].user
    #     if User.objects.exclude(id=user.id).filter(username=value).exists():
    #         raise serializers.ValidationError({"username": "This username is already in use."})
    #     return value

    def update(self, instance, validated_data):

        emailUser = EmailUser.objects.get(user=instance)


        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.username = validated_data['username']

        if validated_data['avi'] is not None:
            # delete current image from directory

            emailUser.avi = validated_data['avi']
            emailUser.save()

        instance.save()

        return instance