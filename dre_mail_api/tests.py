from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Create your tests here.
User = get_user_model()

class TestVersioning(TestCase):

    def setUp(self) -> None:
        self.users_url_v1 = reverse("v1.0:register")
        # self.users_url_v1_1 = reverse("v1.1:users")

    def test_users_url(self):
        self.assertEquals(self.users_url_v1, "/v1/api/register/")


class TestRegisterUser(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_register(self):
        data = {
            # data for the object
            "first_name": "dre",
            "last_name": "day",
            "username": "dreday",
            "email": "randomEmail@gmail.com",
            "password": "randomPassword1"
        }
        
        response = self.client.post('/v1/api/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], data['dre'])
        self.assertEqual(response.data['last_name'], data['day'])
        self.assertEqual(response.data['username'], data['dreday'])
        self.assertEqual(response.data['email'], data['randomEmail@gmail.com'])

class TestEmailTransferViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test_user@gmail.com', password='password')
        self.client.login(email='test_user@gmail.com', password='password')
        

    def test_send_email(self):

        data = {
            # data for the object
            "recipient_id": 1,
            "email": {
                "message": "This is a test message",
                "subject": "This is a test subject"
            }
        }
        response = self.client.post('/v1/api/emailTransfers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_object(self):
        data = {
            # data for the object
            "recipient_id": 1,
            "email": {
                "message": "This is a test message",
                "subject": "This is a test subject"
            }
        }
        response = self.client.put('/v1/api/emailTransfers/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_object(self):

        response = self.client.get('/v1/api/emailTransfers/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check the returned data
        print(response.data)

    def test_delete_object(self):
        response = self.client.delete('/v1/api/emailTransfers/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

