from django.shortcuts import render
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework import permissions
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics

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

class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailUserSerializer
    
    # Create a user
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''

        try:
            userData = {
                'first_name': request.data.get('user.first_name'),
                'last_name': request.data.get('user.last_name'),
                'username': request.data.get('user.username'),
                "email": request.data.get('user.email'),
                "password": request.data.get('user.password')
            }

            emailUserData = {
                "user": userData,
                "avi": request.data.get("avi")

            }

            serializer = EmailUserSerializer(data=emailUserData)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise APIException(errorResponse(e))



class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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


class UserView(generics.ListAPIView):

    # Add permission to check if a user is authenticated 
    permission_classes = [permissions.IsAuthenticated]
    queryset = EmailUser.objects.all()
    serializer_class = EmailUserSerializer
    # query
    filterset_fields = ['user__id']


class UserDetailView(APIView):
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

        if userInstance == False:
            return Response(
                errorResponse("You do not have access to perform this action"),
                status=status.HTTP_403_FORBIDDEN
            )

        if not userInstance:
            return Response(
                errorResponse("User with specified ID does not exists."),
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EmailUserSerializer(userInstance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update a user's details
    def put(self, request, userID=None, *args, **kwargs):
        '''
        Updates the todo item with given userID if exists
        '''

        # This is checking if the user is a superuser or if the user is trying to access their own
        # data.
        if User.objects.get(id=request.user.id).is_superuser == False and userID is not None and request.user.id != userID:
            return Response(
                errorResponse("You do not have access to perform this action"),
                status=status.HTTP_403_FORBIDDEN
            )

        # This is checking if the user is a superuser or if the user is trying to access their own
        # data.
        userInstance = self.get_object(userID, request.user.id)
        if not userInstance:
            return Response(
                errorResponse("User with specified ID does not exists."),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        userData = {
            'first_name': request.data.get('user.first_name'),
            'last_name': request.data.get('user.last_name'),
            'username': request.data.get('user.username'),
            "email": request.data.get('user.email'),
            "password": request.data.get('user.password')
        }

        emailUserData = {
            "user": userData,
            "avi": request.data.get("avi")

        }

        serializer = EmailUserSerializer(instance=userInstance, data=emailUserData, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a user
    def delete(self, request, userID=None, *args, **kwargs):
        '''
        Deletes the user with given id if exists
        '''
        userInstance = self.get_object(userID, request.user.id)

        # This is checking if the user is a superuser or if the user is trying to access their own
        # data.
        if User.objects.get(id=request.user.id).is_superuser == False and request.user.id != userID:
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

        userInstance.delete()
        return Response(successResponse("User has been deleted."), 
            status=status.HTTP_200_OK
        )