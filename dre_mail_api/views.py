from django.shortcuts import render

from dre_mail_api.customResponses import CustomResponses
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status, permissions, \
    generics, filters, viewsets
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.db.models import Q


# Create your views here.

"""---------------AUTH ENDPOINTS-----------------"""
# > This class is used to create a user
class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterUserSerializer
    


# This view will allow authenticated users to update their profile.
# class UpdateProfileView(generics.RetrieveUpdateAPIView):
#     queryset = CustomUser.objects.all()
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = UserSerializer

    # def get_object(self, userID, requestID):
    #     '''
    #     Helper method to get the object with given userID
    #     '''
    #     try:

    #         if not userID:
    #             return CustomUser.objects.get(id=requestID)

    #         return CustomUser.objects.get(id=userID)
            
    #     except CustomUser.DoesNotExist:
    #         return None

    # Retrieve a user's details
    # def get(self, request, userID=None, *args, **kwargs):
    #     '''
    #     Retrieves the Todo with given userID
    #     '''
     
    #     userInstance = self.get_object(userID, request.user.id)

    #     if not userInstance:
    #         return Response(
    #             CustomResponses.errorResponse("User with specified ID does not exist."),
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     serializer = UpdateUserSerializer(userInstance)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # # Update a user's details
    # def update(self, request, userID=None, *args, **kwargs):
    #     '''
    #     Updates the todo item with given userID if exists
    #     '''
        

    #     try:

    #         # This is checking if the user is a superuser or if the user is trying to access their own
    #         # data.
        
    #         if CustomUser.objects.get(id=request.user.id).is_superuser == False \
    #             and userID is not None \
    #             and str(request.user.id) != userID:
    #             return Response(
    #                 CustomResponses.errorResponse("You do not have access to perform this action"),
    #                 status=status.HTTP_403_FORBIDDEN
    #             )

    #         # This is checking if the user is a superuser or if the user is trying to access their own
    #         # data.
    #         self.object = self.get_object(userID, request.user.id)

    #         if not self.object:
    #             return Response(
    #                 CustomResponses.errorResponse("User with specified ID does not exist."),
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
                
    #         data = {
    #             'first_name': request.data.get('first_name'),
    #             'last_name': request.data.get('last_name'),
    #             "email": request.data.get("email"),
    #             "username": request.data.get("username"),
    #             "avi": request.data.get("avi")
    #         }

    #         serializer = self.get_serializer(data=request.data)

    #         if serializer.is_valid():
                
    #             serializer.update(instance=self.object, validated_data=data)
    
    #             return Response(
    #                 CustomResponses.successResponse(serializer.data), 
    #                 status=status.HTTP_200_OK
    #             )

    #         return Response(
    #             CustomResponses.errorResponse(serializer.errors), 
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     except Exception as e:
    #         raise APIException(CustomResponses.errorResponse(e))


# It's a class that inherits from the UpdateAPIView class and it's used to update a user's password
class ChangePasswordView(generics.UpdateAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, userID, requestID):
        '''
        Helper method to get the object with given userID
        '''
        try:

            if not userID:
                return CustomUser.objects.get(id=requestID)

            return CustomUser.objects.get(id=userID)
            
        except CustomUser.DoesNotExist:
            return None

    # Update a user's details
    def update(self, request, userID=None, *args, **kwargs):
        '''
        Updates the todo item with given userID if exists
        '''

        try:

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
            if CustomUser.objects.get(id=request.user.id).is_superuser == False \
                and userID is not None \
                and str(request.user.id) != userID:
                return Response(
                    CustomResponses.errorResponse("You do not have access to perform this action"),
                    status=status.HTTP_403_FORBIDDEN
                )

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
            self.object = self.get_object(userID, request.user.id)

            if not self.object:
                return Response(
                    CustomResponses.errorResponse("User with specified ID does not exist."),
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            data = {
                'old_password': request.data.get('old_password'),
                'new_password': request.data.get('new_password'),
                "confirm_password": request.data.get("confirm_password")
            }

            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                
                serializer.update(instance=self.object, validated_data=data)
    
                return Response(CustomResponses.successResponse("Password reset successful"), status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            raise APIException(CustomResponses.errorResponse(e))


# It takes a refresh token, blacklists it, and returns a success message
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # logout a user and destroy their token
    def post(self, request):
        try:

            if request.data.get('refresh') is None:
                return Response(CustomResponses.errorResponse("refresh cannot be empty"), status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            successMessage = CustomResponses.successResponse("You have been logged out successfully.")
            return Response(successMessage)
        except Exception as e:
            raise APIException(CustomResponses.errorResponse(e))
            


"""-------------------- USER ENDPOINTS --------------------"""


# This model view set comprises all the actions that can be taken towards a user including
# retrieving their information, deleting their account and updating their account.
class UserViewSet(viewsets.ModelViewSet):

    # Add permission to check if a user is authenticated 
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['id']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'user__email']
    http_method_names = ['get', 'delete', 'patch']

    def destroy(self, request, *args, **kwargs):

        # Only allow users to delete their own accounts
        if self.request.user.id != self.get_object().id:
            return Response(
                CustomResponses.errorResponse("You do not have access to perform this action"),
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):

        # Only allow users to update their own accounts
        if self.request.user.id != self.get_object().id:
            return Response(
                CustomResponses.errorResponse("You do not have access to perform this action"),
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request, *args, **kwargs)


"""--------------- EMAIL GROUP ENDPOINTS ---------------"""

class EmailGroupViewSet(viewsets.ModelViewSet):
    queryset = EmailGroup.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailGroupSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name'] 


    def destroy(self, request, *args, **kwargs):

        if self.get_object().creator.id != self.request.user.id:
            return Response(
                CustomResponses.errorResponse("You do not have access to perform this action"),
                status=status.HTTP_400_BAD_REQUEST
            )


        return super().destroy(request, *args, **kwargs)


    def get_queryset(self):

        currentUser = CustomUser.objects.get(id=self.request.user.id)

        return EmailGroup.objects.filter(
            Q(creator = currentUser) | Q(members=currentUser)
        ).distinct()


    @action(detail=True, serializer_class=UserSerializer, search_fields=['members__user__username'])
    def members(self, request, pk=None):

        groupMembers = self.get_object().members.all()

        page = self.paginate_queryset(groupMembers)
    
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(groupMembers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], serializer_class=EmailGroupMemberSerializer)
    def add_member(self, request, pk=None):

        try:

            self.get_object().members.add(CustomUser.objects.get(id=request.data.get("id")))

            return Response(
                CustomResponses.successResponse("Member has been added successfully")
            )

        except Exception as e:
            raise APIException(CustomResponses.errorResponse(e))

    @action(detail=True, methods=['post'], serializer_class=EmailGroupMemberSerializer)
    def remove_member(self, request, pk=None):

        try:

            # check if the user is removing themselves by checking if no id was submitted
            if request.data.get("id") is None or request.data.get("id") == "":

                # leave the group
                self.get_object().members.remove(
                    CustomUser.objects.get(
                        id=self.request.user.id
                    )
                )

                return Response(
                    CustomResponses.successResponse("You have successfully left the group")
                )
            

            # revoke access if the person trying to remove the member is 
            # not the creator of the group or the member themselves
            if self.get_object().creator != CustomUser.objects.get(id=self.request.user.id):
                return Response(
                CustomResponses.errorResponse("You do not have access to perform this action"),
                status=status.HTTP_400_BAD_REQUEST
            )

            # Get the user to remove and remove them from the group
            userToRemove = CustomUser.objects.get(
                id=request.data.get("id")
            )

            self.get_object().members.remove(
                userToRemove
            )

            return Response(
                CustomResponses.successResponse("Member has been removed successfully"),
                status=status.HTTP_200_OK
            )

        except Exception as e:
            raise APIException(CustomResponses.errorResponse(e))




"""--------------- EMAIL ENDPOINTS ---------------"""

# This is a viewset that allows the admin to view and edit emails.
class EmailViewSet(viewsets.ModelViewSet):
    serializer_class = EmailSerializer
    queryset = Email.objects.all()
    permission_classes = [permissions.IsAdminUser]

# This class is a viewset that allows you to create, retrieve, update, and delete drafts
class DraftViewSet(viewsets.ModelViewSet):
    serializer_class = DraftSerializer
    queryset = Drafts.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class EmailTransferViewSet(viewsets.ModelViewSet):
    serializer_class = EmailTransferSerializer
    queryset = EmailTransfer.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sender', 'recipient']
    search_fields = [
        'email__subject', 
        "email__message", 
        "recipient__user__first_name",
        "recipient__user__last_name",
        "recipient__user__username",
        "recipient__user__email",
        "sender__user__first_name",
        "sender__user__last_name",
        "sender__user__username",
        "sender__user__email",
    ] 

    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):


        unread = self.request.query_params.get("unread", None)

        if unread is None:
            return super().get_queryset()

        queryset = EmailTransfer.objects.all()

        return queryset.filter(
            unread=unread
        )

    def destroy(self, request, *args, **kwargs):
        """
        I'm trying to create a new Trash object, and save it to the database
        
        :param request: The request object
        :return: A response object
        """

        # Checking if the sender of the email is the same as the user who is trying to delete the
        # email. If it is, it will return an error message.
        try:
            if self.get_object().sender == CustomUser.objects.get(id=self.request.user.id):
                return Response(CustomResponses.errorResponse("You are unable to delete an email you sent"), status=status.HTTP_400_BAD_REQUEST)

            # Check if the email is in trash
            if Trash.objects.filter(
                    emailTransfer=self.get_object(), 
                    deleter=CustomUser.objects.get(id=self.request.user.id)
                ).exists():

                # permanently delete the email
                self.get_object().email.delete()

                return Response(CustomResponses.successResponse("Email has been permanently deleted"))


            # Move email to deleted Emails (trash)
            deleteEmail = Trash(
                deleter = CustomUser.objects.get(id=self.request.user.id),
                emailTransfer = self.get_object()
            )

            deleteEmail.save();
            return Response(CustomResponses.successResponse("Successfully moved email to Trash"))

        except Exception as e:
            return Response(CustomResponses.errorResponse(e))


    @action(detail=False, serializer_class=InboxSerializer, methods=['get', 'post'])
    def inbox(self, request):

        # Check if the user sends a post request and move the email to the respective table
        if self.request.method == "POST":

            try:

                # Getting the email_id from the request.data and then getting the emailTransfer object
                # from the database.
                emailTransfer = EmailTransfer.objects.get(
                    id=self.request.data.get("email_id")
                )

                # Getting the User object from the database.
                User = CustomUser.objects.get(
                    id=self.request.user.id
                )

                # The below code is a function that is used to move emails to different folders.
                match(request.data.get("destination")):

                    case "favorites":
                        favorites = Favorites(
                            favoriter = User,
                            emailTransfer = emailTransfer
                        )

                        favorites.save()

                        return Response(
                            CustomResponses.successResponse("Email has been added to favorites")
                        )

                    case "junk":
                        junk = Junk(
                            junker = User,
                            emailTransfer = emailTransfer
                        )

                        junk.save()

                        return Response(
                            CustomResponses.successResponse("Email has been added to junk")
                        )

                    case "spam":
                        spam = Spam(
                            spammer = User,
                            emailTransfer = emailTransfer
                        )

                        spam.save()

                        return Response(
                            CustomResponses.successResponse("Email has been added to spam")
                        )

            except Exception as e:
                raise APIException(CustomResponses.errorResponse(e))

        
        # Getting the query parameter "unread" from the request.
        unread = self.request.query_params.get("unread", None)

        # Getting the user object from the database.
        user = CustomUser.objects.get(
            id=self.request.user.id
        )

        # Getting all the deleted emails ids of the user.
        trashedEmailIDs = list(Trash.objects.filter(
            deleter=user
        ).values_list("emailTransfer__id", flat=True))

       # Filtering the spammer and getting the values of the emailTransfer__id.
        spamEmailIDs = list(Spam.objects.filter(
            spammer=user
        ).values_list("emailTransfer__id", flat=True))

        # Filtering the Spam model for the user and then returning the emailTransfer__id
        junkEmailIDs = list(Junk.objects.filter(
            junker=user
        ).values_list("emailTransfer__id", flat=True))


        # Get inbox
        inbox = EmailTransfer.objects.exclude(
            id__in=trashedEmailIDs + spamEmailIDs + junkEmailIDs,
        ).filter(
            Q(group__isnull=True) | Q(group__members=user),
            recipient=user
        )

        
        # Filtering the emails based on the unread status.

        if unread is not None:
            inbox = inbox.filter(unread=unread)

        page = self.paginate_queryset(inbox)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(inbox, many=True)
        return Response(serializer.data)


    @action(detail=False, serializer_class=ReadStatusUpdateSerializers, methods=['post'])
    def update_read_status(self, request):

        try:

            serializer = self.get_serializer(data=request.data)
            self.object = EmailTransfer.objects.get(id=request.data.get("id"))
            

            if serializer.is_valid():
                
                
                serializer.update(instance=self.object, validated_data=request.data)
    
                return Response(
                    CustomResponses.successResponse(
                        "Successfully updated unread status"
                    ), 
                    status=status.HTTP_200_OK
                )

            return Response(CustomResponses.errorResponse(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            raise APIException(CustomResponses.errorResponse(e))
        

    
    @action(detail=False, serializer_class=SentEmailSerializer)
    def sent_emails(self, request):

        # Getting the User object from the database.
        user = CustomUser.objects.get(
            id=self.request.user.id
        )
        
        sentEmails = EmailTransfer.objects.filter(sender=user)

        page = self.paginate_queryset(sentEmails)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(sentEmails, many=True)
        return Response(serializer.data)


    @action(detail=False, serializer_class=EmailActionSerializer, methods=['get', 'post'])
    def trash(self, request):

        # Check if the user sends a post request and move the email back to inbox
        if self.request.method == "POST":
            self.create(request=request)
            return Response(CustomResponses.successResponse("Email has been moved back to inbox")
        )

        # Getting the user object from the database.
        user = CustomUser.objects.get(
            id=self.request.user.id
        )
        
        trash = Trash.objects.filter(deleter=user)

        page = self.paginate_queryset(trash)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(trash, many=True)
        return Response(serializer.data)


    @action(detail=False, serializer_class=EmailActionSerializer, methods=['get', 'post'])
    def spam(self, request):

        # Check if the user sends a post request and move the email back to inbox
        if self.request.method == "POST":
            self.create(request=request)
            return Response(CustomResponses.successResponse("Email has been moved back to inbox"))

        # Getting the user object from the database.
        user = CustomUser.objects.get(
            id=self.request.user.id
        )
        
        spam = Spam.objects.filter(spammer=user)

        page = self.paginate_queryset(spam)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(spam, many=True)
        return Response(serializer.data)


    @action(detail=False, serializer_class=EmailActionSerializer, methods=['get', 'post'])
    def junk(self, request):

        # Check if the user sends a post request and move the email back to inbox
        if self.request.method == "POST":
            
            self.create(request=request)
            return Response(CustomResponses.successResponse("Email has been moved back to inbox"))

        # Getting the user object from the database.
        user = CustomUser.objects.get(
            id=self.request.user.id
        )
        
        junk = Junk.objects.filter(junker=user)

        page = self.paginate_queryset(junk)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(junk, many=True)
        return Response(serializer.data)


    @action(detail=False, serializer_class=EmailActionSerializer, methods=['get', 'post'])
    def favorites(self, request):

        # Check if the user sends a post request and move the email back to inbox
        if self.request.method == "POST":
            self.create(request=request)
            return Response(CustomResponses.successResponse("Email has been moved back to inbox"))

        # Getting the user object from the database.
        user = CustomUser.objects.get(
            id=self.request.user.id
        )
        
        favorites = Favorites.objects.filter(favoriter=user)

        page = self.paginate_queryset(favorites)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)


