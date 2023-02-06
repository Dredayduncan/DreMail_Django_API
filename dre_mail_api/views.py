from django.shortcuts import render
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status, permissions, \
    generics, filters, viewsets
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

def successResponse(message):
    return {
        "detail": message
    }

def errorResponse(message):
    return {
       "error": {
        "detail": message
       }
    }

# Create your views here.

"""---------------AUTH ENDPOINTS-----------------"""
# > This class is used to create a user
class RegisterUserView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailUserSerializer
    


# This view will allow authenticated users to update their profile.
class UpdateProfileView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def get_object(self, userID, requestID):
        '''
        Helper method to get the object with given userID
        '''
        try:

            if not userID:
                return User.objects.get(id=requestID)

            return User.objects.get(id=userID)
            
        except User.DoesNotExist:
            return None

    # Retrieve a user's details
    def get(self, request, userID=None, *args, **kwargs):
        '''
        Retrieves the Todo with given userID
        '''
     
        userInstance = self.get_object(userID, request.user.id)

        if not userInstance:
            return Response(
                errorResponse("User with specified ID does not exists."),
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UpdateUserSerializer(userInstance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update a user's details
    def update(self, request, userID=None, *args, **kwargs):
        '''
        Updates the todo item with given userID if exists
        '''

        try:

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
        
            if User.objects.get(id=request.user.id).is_superuser == False \
                and userID is not None \
                and str(request.user.id) != userID:
                return Response(
                    errorResponse("You do not have access to perform this action"),
                    status=status.HTTP_403_FORBIDDEN
                )

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
            self.object = self.get_object(userID, request.user.id)

            if not self.object:
                return Response(
                    errorResponse("User with specified ID does not exists."),
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            data = {
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
                "email": request.data.get("email"),
                "username": request.data.get("username"),
                "avi": request.data.get("avi")
            }

            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                
                serializer.update(instance=self.object, validated_data=data)
    
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            raise APIException(errorResponse(e))


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
                return User.objects.get(id=requestID)

            return User.objects.get(id=userID)
            
        except User.DoesNotExist:
            return None

    # Update a user's details
    def update(self, request, userID=None, *args, **kwargs):
        '''
        Updates the todo item with given userID if exists
        '''

        try:

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
            if User.objects.get(id=request.user.id).is_superuser == False \
                and userID is not None \
                and str(request.user.id) != userID:
                return Response(
                    errorResponse("You do not have access to perform this action"),
                    status=status.HTTP_403_FORBIDDEN
                )

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
            self.object = self.get_object(userID, request.user.id)

            if not self.object:
                return Response(
                    errorResponse("User with specified ID does not exists."),
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
    
                return Response(successResponse("Password reset successful"), status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            raise APIException(errorResponse(e))


# It takes a refresh token, blacklists it, and returns a success message
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # logout a user and destroy their token
    def post(self, request):
        try:

            if request.data.get('refresh') is None:
                return Response(errorResponse("refresh cannot be empty"), status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            successMessage = successResponse("You have been logged out successfully.")
            return Response(successMessage)
        except Exception as e:
            raise APIException(errorResponse(e))
            


"""-------------------- USER ENDPOINTS --------------------"""

# This class is used to update the AVI of a user
class UpdateAVIView(generics.UpdateAPIView):
    queryset = EmailUser.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateAVISerializer

    def get_object(self, userID, requestID):
        '''
        Helper method to get the object with given userID
        '''
        try:

            if not userID:
                return EmailUser.objects.get(user__id=requestID)

            return EmailUser.objects.get(user__id=userID)
            
        except EmailUser.DoesNotExist:
            return None

    # Update a user's details
    def update(self, request, userID=None, *args, **kwargs):
        '''
        Updates the todo item with given userID if exists
        '''

        try:

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
            if User.objects.get(id=request.user.id).is_superuser == False \
                and userID is not None \
                and str(request.user.id) != userID:
                return Response(
                    errorResponse("You do not have access to perform this action"),
                    status=status.HTTP_403_FORBIDDEN
                )

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
            self.object = self.get_object(userID, request.user.id)

            if not self.object:
                return Response(
                    errorResponse("User with specified ID does not exists."),
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            data = {
                "avi": request.data.get("avi")
            }

            serializer = self.get_serializer(data=data)

            if serializer.is_valid():
                
                serializer.update(instance=self.object, validated_data=data)
    
                return Response(successResponse("Successfully updated the AVI"), status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            raise APIException(errorResponse(e))

# This class is a ListAPIView that returns a list of all users, and allows you to filter by user id,
# first name, last name, username, and email
class UserView(generics.ListAPIView):

    # Add permission to check if a user is authenticated 
    permission_classes = [permissions.IsAuthenticated]
    queryset = EmailUser.objects.all()
    serializer_class = EmailUserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user__id']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'user__email']


# This class is used to retrieve and delete a user
class UserDetailView(generics.RetrieveDestroyAPIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmailUserSerializer

    def get_object(self, userID, requestID):
        '''
        Helper method to get the object with given userID
        '''
        try:

            if not userID:
                return EmailUser.objects.get(user__id=requestID)

            return EmailUser.objects.get(user__id=userID)
            
        except EmailUser.DoesNotExist:
            return None

    # Retrieve a user's details
    def get(self, request, userID=None, *args, **kwargs):
        '''
        Retrieves the Todo with given userID
        '''
     
        userInstance = self.get_object(userID, request.user.id)

        if not userInstance:
            return Response(
                errorResponse("User with specified ID does not exists."),
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EmailUserSerializer(userInstance)
        return Response(serializer.data, status=status.HTTP_200_OK)


    # Delete a user
    def delete(self, request, userID=None, *args, **kwargs):
        '''
        Deletes the user with given id if exists
        '''

        try:
            userInstance = self.get_object(userID, request.user.id)

            # This is checking if the user is a superuser or if the user is trying to access their own
            # data.
            if User.objects.get(id=request.user.id).is_superuser == False \
                and userID is not None \
                and str(request.user.id) != userID:
                return Response(
                    errorResponse("You do not have access to perform this action"),
                    status=status.HTTP_403_FORBIDDEN
                )

            # This is checking if the user exists. If the user does not exist, it will return an error
            # message.
            if not userInstance:
                return Response(
                    errorResponse("User with specified ID does not exists."),  
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            user = userInstance.user
            userInstance.delete()
            user.delete()
            return Response(successResponse("User has been deleted."), 
                status=status.HTTP_200_OK
            )

        except Exception as e:
            raise APIException(errorResponse(e))


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