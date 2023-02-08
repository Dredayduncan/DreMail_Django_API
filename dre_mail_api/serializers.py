from rest_framework import serializers
from django.contrib.auth.models import User

from dre_mail_api.customResponses import CustomResponses
from .models import *

"""--------------- AUTH SERIALIZERS ---------------"""

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
            raise serializers.ValidationError(
                CustomResponses.errorResponse("Password fields didn't match.")
            )

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                CustomResponses.errorResponse("Old password is not correct")
            )
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.id != instance.id:
            raise serializers.ValidationError(
                CustomResponses.errorResponse("You dont have permission for this user.")
            )

        instance.set_password(validated_data['new_password'])
        instance.is_active = True
        instance.save()

        return instance


"""--------------- USER SERIALIZERS ---------------"""


# This class is used to update the user's first name, last name, email, and username
class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError(
                CustomResponses.errorResponse("This email is already in use.")
            )
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError(
                CustomResponses.errorResponse("This username is already in use.")
            )
        return value

    def update(self, instance, validated_data):

        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.username = validated_data['username']

        instance.save()

        return instance


# This class is used to update the user's first name, last name, email, and username
class UpdateAVISerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailUser
        fields = ['avi']

    def update(self, instance, validated_data):

        # delete current image from directory
        instance.avi.delete()

        # store the new image
        instance.avi = validated_data['avi']
        instance.save()

        return instance


"""------------------ EMAIL GROUP SERIALIZERS -----------------"""

class EmailGroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EmailGroup
        fields = "__all__"

"""------------------ EMAIL SERIALIZERS -----------------"""


# This is a serializer for the Email model, and it has an attachment field that is a FileField.
class EmailSerializer(serializers.ModelSerializer):
    attachment = serializers.FileField(required=False)

    class Meta:
        model = Email
        fields = "__all__"


class EmailTransferSerializer(serializers.ModelSerializer):
    email = EmailSerializer()
    recipient = EmailUserSerializer(read_only=True)
    sender = EmailUserSerializer(read_only=True)
    recipient_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = EmailTransfer
        fields = ["id", "sender", "recipient", "recipient_id", 'email', "unread", "dateSent"]
        extra_kwargs = {
            "unread": {
                "read_only": True
            },
            "dateSent": {
                "read_only": True
            }
        }

    def validate_recipient_id(self, value):
        """
        If the user exists, and the user is not the same as the user sending the email, then return the
        value
        
        :param value: The value of the field being validated
        :return: The value of the recipient.
        """
        try:
            
            user = self.context['request'].user

            if EmailUser.objects.filter(id=value).exists() == False:
                raise CustomResponses.errorResponse("User with specified ID does not exist.")


            if EmailUser.objects.get(user__id=user.id) == EmailUser.objects.get(id=value):
                raise CustomResponses.errorResponse("You cannot send an email to yourself")

            
            return value
        except Exception as e:
            raise serializers.ValidationError(
                CustomResponses.errorResponse(e)
            )


    def create(self, validated_data):
        """
        It's creating a new email object and saving it to the database. It's creating a new draft object
        and saving it to the database
        
        :param validated_data: It's the data that has been validated by the serializer
        :return: It's returning the emailTransfer object.
        """
    

        # It's creating a new email object and saving it to the database.
        email = Email(
            subject = validated_data['email'].get("subject"),
            message = validated_data['email'].get("message"),
            attachment = validated_data['email'].get('attachment')
        )

        email.save()

        
        # It's creating a new draft object and saving it to the database.
        emailTransfer = EmailTransfer(
            recipient = EmailUser.objects.get(id=validated_data.get('recipient_id')),
            sender = EmailUser.objects.get(user__id=self.context['request'].user.id),
            email = email
        )

        emailTransfer.save()

        return emailTransfer


# The InboxSerializer class is a ModelSerializer that serializes the EmailTransfer model 
# for the inbox. It has a nested EmailSerializer and EmailUserSerializer
class InboxSerializer(serializers.ModelSerializer):
    email = EmailSerializer(read_only=True)
    sender = EmailUserSerializer(read_only=True)

    class Meta:
        model = EmailTransfer
        fields = ["id", "sender", 'email', "unread", "dateSent"]
        extra_kwargs = {
            "unread": {
                "read_only": True
            },
            "dateSent": {
                "read_only": True
            },
        }

class EmailActionSerializer(serializers.ModelSerializer):
    emailTransfer = InboxSerializer(read_only=True)
    email_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Trash
        fields = ['email_id', 'emailTransfer']
        extra_kwargs = {
            "unread": {
                "read_only": True
            },
            "dateSent": {
                "read_only": True
            }
        }

    def validate_id(self, value):
        try:

            if EmailTransfer.objects.filter(id=value).exists() == False:
                raise CustomResponses.errorResponse("Email with specified ID does not exist.")

            return value
        except Exception as e:
            raise CustomResponses.errorResponse(e)

    def create(self, validated_data):
        """
        It's creating a new email object and saving it to the database. It's creating a new draft object
        and saving it to the database
        
        :param validated_data: It's the data that has been validated by the serializer
        :return: It's returning the emailTransfer object.
        """

        try:
            endpoint = self.context['request'].get_full_path()
            endpointType = endpoint.split("/")[-1]

            # Remove the email from their respective Models
            
            # Deleting the email from the trash.
            if endpointType == "trash":
       
                return Trash.objects.get(
                    deleter=EmailUser.objects.get(user__id=self.context['request'].user.id),
                    emailTransfer=EmailTransfer.objects.get(id=validated_data.get("email_id"))
                ).delete()

            # Deleting the email from spam.
            elif endpointType == "spam":
                return Spam.objects.get(
                    spammer=EmailUser.objects.get(user__id=self.context['request'].user.id),
                    emailTransfer=EmailTransfer.objects.get(id=validated_data.get("email_id"))
                ).delete()
                
            # Deleting the email from junk.
            elif endpointType == 'junk':
                return Junk.objects.get(
                    junker=EmailUser.objects.get(user__id=self.context['request'].user.id),
                    emailTransfer=EmailTransfer.objects.get(id=validated_data.get("email_id"))
                ).delete()

            # Deleting the email from favorite.
            else:
                return Favorites.objects.get(
                    favoriter=EmailUser.objects.get(user__id=self.context['request'].user.id),
                    emailTransfer=EmailTransfer.objects.get(id=validated_data.get("email_id"))
                ).delete()

        
        except Exception as e:
            raise serializers.ValidationError(CustomResponses.errorResponse(e))


# The SentEmailSerializer class is a serializer for the EmailTransfer model. It has a nested
# serializer for the Email model and a nested serializer for the EmailUser model
class SentEmailSerializer(serializers.ModelSerializer):
    email = EmailSerializer()
    recipient = EmailUserSerializer(read_only=True)

    class Meta:
        model = EmailTransfer
        fields = ["id", "recipient", 'email', "dateSent"]
        extra_kwargs = {
            "dateSent": {
                "read_only": True
            }
        }


# It's creating a draft and saving it to the database
class DraftSerializer(serializers.ModelSerializer):
    email = EmailSerializer()

    class Meta:
        model = Drafts
        fields = ['id', 'email']

    def create(self, validated_data):
        """
        It's creating a new email object and saving it to the database
        
        :param validated_data: The data that was validated by the serializer
        :return: The draft object.
        """
        """Create and return a draft."""

        # It's creating a new email object and saving it to the database.
        email = Email(
            subject = validated_data['email'].get("subject"),
            message = validated_data['email'].get("message"),
            attachment = validated_data['email'].get('attachment')
        )

        email.save()

        
        # It's creating a new draft object and saving it to the database.
        draft = Drafts(
            drafter = EmailUser.objects.get(user__id=self.context['request'].user.id),
            email = email
        )

        draft.save()

        return draft

    def update(self, instance, validated_data):
        """
        It's creating a new email object and saving it to the database
        
        :param validated_data: The data that was validated by the serializer
        :return: The draft object.
        """
        """Create and return a draft."""


        # It's creating a new email object and saving it to the database.

        instance.email.subject = validated_data['email'].get("subject")
        instance.email.message = validated_data['email'].get("message")
        instance.email.attachment = validated_data['email'].get('attachment')

        instance.email.save()

        return instance