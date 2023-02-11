from rest_framework import serializers
from dre_mail_api.customResponses import CustomResponses
from .models import *

"""--------------- AUTH SERIALIZERS ---------------"""

class RegisterUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
 
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'email', 'avi')
        extra_kwargs = {
            'password': {"write_only": True}
        }

    def validate_email(self, value):

        pattern = re.compile("^\w+(@dremail.com)$")
        if not pattern.match(value):
            raise serializers.ValidationError("Invalid email format. Your email should end with @dremail.com")

        return value


    def create(self, validated_data):
        """Create and return a new user."""

        try:

            user = CustomUser(
                email = validated_data.get('email'),
                first_name = validated_data.get('first_name'),
                last_name = validated_data.get('last_name'),
                username = validated_data.get('username')
            )

            user.set_password(validated_data.get('password'))
            user.avi = validated_data.get('avi')
            user.save()

            return user

        except Exception as e:
            raise serializers.ValidationError(e)

       


# It creates a new user and a new User, and then saves them both
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'email', "avi"]


# It's a serializer that validates the old password, the new password, and the confirmation of the new
# password
class ChangePasswordSerializer(serializers.ModelSerializer):

    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)
 
    class Meta:
        model = CustomUser
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

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


"""--------------- USER SERIALIZERS ---------------"""


# This class is used to update the user's first name, last name, email, and username
class UpdateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email')


    def validate_email(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError(
                CustomResponses.errorResponse("This email is already in use.")
            )
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(id=user.id).filter(username=value).exists():
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
        model = CustomUser
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
        fields = ['id', 'name', 'description']

    def create(self, validated_data):

        currentUser = CustomUser.objects.get(id=self.context['request'].user.id)

        #  provide the info for the group
        emailGroup = EmailGroup(
            name = validated_data.get("name"),
            description = validated_data.get("description"),
            creator = currentUser
        )

        # create the group
        emailGroup.save()

        # Add the creator as a member
        emailGroup.members.add(currentUser)

        

        return emailGroup


class EmailGroupMemberSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id']



"""------------------ EMAIL SERIALIZERS -----------------"""


# This is a serializer for the Email model, and it has an attachment field that is a FileField.
class EmailSerializer(serializers.ModelSerializer):
    attachment = serializers.FileField(required=False)

    class Meta:
        model = Email
        fields = "__all__"


class EmailTransferSerializer(serializers.ModelSerializer):
    email = EmailSerializer()
    recipient = UserSerializer(read_only=True)
    group = EmailGroupSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    recipient_id = serializers.IntegerField(write_only=True, required=False)
    group_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = EmailTransfer
        fields = ["id", "sender", "recipient", "group", 'email', "unread", "dateSent", "recipient_id", "group_id"]
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

            if CustomUser.objects.filter(id=value).exists() == False:
                raise CustomResponses.errorResponse("User with specified ID does not exist.")


            if CustomUser.objects.get(id=user.id) == CustomUser.objects.get(id=value):
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

        if validated_data.get("recipient_id") is None and validated_data.get("group_id") is None:
            raise serializers.ValidationError(
                CustomResponses.errorResponse("Email recipient has not been specified")
            )

    

        # It's creating a new email object and saving it to the database.
        email = Email(
            subject = validated_data['email'].get("subject"),
            message = validated_data['email'].get("message"),
            attachment = validated_data['email'].get('attachment')
        )

        email.save()

        
        # It's creating a new draft object and saving it to the database.
        emailTransfer = EmailTransfer(
            sender = CustomUser.objects.get(id=self.context['request'].user.id),
            email = email
        )

        if validated_data.get("recipient_id") is None:
            emailTransfer.group = EmailGroup.objects.get(id=validated_data.get("group_id"))
        else:
            emailTransfer.recipient = CustomUser.objects.get(id=validated_data.get('recipient_id'))

        emailTransfer.save()

        return emailTransfer


# The InboxSerializer class is a ModelSerializer that serializes the EmailTransfer model 
# for the inbox. It has a nested EmailSerializer and UserSerializer
class InboxSerializer(serializers.ModelSerializer):
    email = EmailSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    group = EmailGroupSerializer(read_only=True)
    email_id = serializers.IntegerField(required=True, write_only=True)
    destination = serializers.ChoiceField(required=True, write_only=True, choices=['favorites', 'junk', 'spam'])

    class Meta:
        model = EmailTransfer
        fields = ["id", "sender", 'group', 'email', "unread", "dateSent", "email_id", "destination"]
        extra_kwargs = {
            "unread": {
                "read_only": True
            },
            "dateSent": {
                "read_only": True
            },
        }


# This class is used to update the read status of an email
class ReadStatusUpdateSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = EmailTransfer
        fields = ["id", "unread"]


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
                    deleter=CustomUser.objects.get(id=self.context['request'].user.id),
                    emailTransfer=EmailTransfer.objects.get(id=validated_data.get("email_id"))
                ).delete()

            # Deleting the email from spam.
            elif endpointType == "spam":
                return Spam.objects.get(
                    spammer=CustomUser.objects.get(id=self.context['request'].user.id),
                    emailTransfer=EmailTransfer.objects.get(id=validated_data.get("email_id"))
                ).delete()
                
            # Deleting the email from junk.
            elif endpointType == 'junk':
                return Junk.objects.get(
                    junker=CustomUser.objects.get(id=self.context['request'].user.id),
                    emailTransfer=EmailTransfer.objects.get(id=validated_data.get("email_id"))
                ).delete()

            # Deleting the email from favorite.
            else:
                return Favorites.objects.get(
                    favoriter=CustomUser.objects.get(id=self.context['request'].user.id),
                    emailTransfer=EmailTransfer.objects.get(id=validated_data.get("email_id"))
                ).delete()

        
        except Exception as e:
            raise serializers.ValidationError(CustomResponses.errorResponse(e))


# The SentEmailSerializer class is a serializer for the EmailTransfer model. It has a nested
# serializer for the Email model and a nested serializer for the User model
class SentEmailSerializer(serializers.ModelSerializer):
    email = EmailSerializer()
    recipient = UserSerializer(read_only=True)

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
            drafter = CustomUser.objects.get(id=self.context['request'].user.id),
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