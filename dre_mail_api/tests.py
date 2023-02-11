from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Create your tests here.
User = get_user_model()

class TestVersioning(TestCase):

    def setUp(self):
        self.users_url_v1 = reverse("v1.0:register")
        # self.users_url_v1_1 = reverse("v1.1:users")

    def test_users_url(self):
        self.assertEquals(self.users_url_v1, "/v1/api/register/")


# We're testing the register endpoint.
class TestRegisterUser(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        # data for the object
        data = {
            "first_name": "dre",
            "last_name": "day",
            "username": "dreday",
            "email": "randomEmail@gmail.com",
            "password": "password"
        }
        
        response = self.client.post('/v1/api/register/', data, format='json')
      
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'dre')
        self.assertEqual(response.data['last_name'], 'day')
        self.assertEqual(response.data['username'], 'dreday')
        self.assertEqual(response.data['email'], 'randomEmail@gmail.com')


# This class tests the EmailTransferViewSet class.
class TestEmailTransferViewSet(TestCase):
        
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test_user@gmail.com', password='password', username='user')
        self.client.login(email='test_user@gmail.com', password='password')
        # create recipient
        self.recipient = User.objects.create_user(email='recipient@gmail.com', password='password', username="recipient")
        self.email_id = None

        self.test_create_email()


    def test_create_email(self):

        # data for the object
        data = {
            
            "recipient_id": self.recipient.id,
            "email": {
                "message": "This is a test message",
                "subject": "This is a test subject"
            }
        }
        
        response = self.client.post('/v1/api/emailTransfers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email']['message'], "This is a test message")
        self.assertEqual(response.data['email']['subject'], "This is a test subject")
        self.assertEqual(response.data['recipient']['email'], "recipient@gmail.com")
        self.email_id = response.data['id']


    def test_get_email(self):

        response = self.client.get(f'/v1/api/emailTransfers/{self.email_id}')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email']['message'], "This is a test message")
        self.assertEqual(response.data['email']['subject'], "This is a test subject")


    def test_delete_email(self):
        response = self.client.delete(f'/v1/api/emailTransfers/{self.email_id}')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_update_object(self):
        data = {
            # data for the object
            "recipient_id": self.recipient.id,
            "email": {
                "message": "This is another test message",
                "subject": "This is another test subject"
            }
        }

        response = self.client.put('/v1/api/emailTransfers/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    

    

