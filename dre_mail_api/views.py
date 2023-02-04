from django.shortcuts import render
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework import permissions
from .models import *
from django.views.decorators.csrf import csrf_protect 
from rest_framework_simplejwt.tokens import RefreshToken

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

class BlacklistRefreshView(APIView):
    def post(self, request):
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        successMessage = successResponse("You have been logged out successfully.")
        return Response(successMessage)


class RegisterUserView(APIView):
    # Create a user
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''
        data = {
            'first_name': request.data['first_name'],
            'last_name': request.data['last_name'],
            'username': request.user['username'],
            "email": request.user['email'],
            "password": request.user['password']
        }

        serializer = EmailUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmailUserView(APIView):

    # Add permission to check if a user is authenticated 
    permission_classes = [permissions.IsAuthenticated]

    # Get a user's info
    def get(self, request, *args, **kwargs):
        '''
        Return the info of given requested user
        '''

        try:
    
            users = EmailUser.objects.all()
            serializer = EmailUserSerializer(users, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            raise APIException(e)


class EmailUserDetailView(APIView):
    # add permission to check if user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, userID, requestID):
        '''
        Helper method to get the object with given userID
        '''
        try:

            return EmailUser.objects.get(user__id=userID)
            
        except EmailUser.DoesNotExist:
            return None

    # Retrieve a user's details
    def get(self, request, userID, *args, **kwargs):
        '''
        Retrieves the Todo with given userID
        '''
     
        userInstance = self.get_object(userID, request.user.id)

        if userInstance == False:
            return Response(
                {"message": "You do not have access to perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not userInstance:
            return Response(
                {"message": "User with specified ID does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EmailUserSerializer(userInstance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update a user's details
    def put(self, request, userID, *args, **kwargs):
        '''
        Updates the todo item with given userID if exists
        '''
        userInstance = self.get_object(userID, request.user.id)
        if not userInstance:
            return Response(
                {"message": "User with specified ID does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if userInstance == False:
            return Response(
                {"message": "You do not have access to perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )

        print(request.data)

        data = {
            'first_name': request.data['first_name'], 
            'last_name': request.data['last_name'], 
            'username': request.user['username'],
            "email": request.user['email'],
            "password": request.user['password']
        }

        serializer = EmailUserSerializer(instance = userInstance, data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a user
    def delete(self, request, userID, *args, **kwargs):
        '''
        Deletes the user with given id if exists
        '''
        userInstance = self.get_object(userID, request.user.id)

        if userInstance == False:
            return Response(
                {"message": "You do not have access to perform this action"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not userInstance:
            return Response(
                {"message": "User with specified ID does not exists."},  
                status=status.HTTP_400_BAD_REQUEST
            )
        userInstance.delete()
        return Response(
            {"message": "User has been deleted."}, 
            status=status.HTTP_200_OK
        )