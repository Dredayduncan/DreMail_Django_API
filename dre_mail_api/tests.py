from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Create your tests here.
User = get_user_model()

#how to create an admin object from get_user_model?

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

    def test_register_with_wrong_email(self):
        # data for the object
        data = {
            "first_name": "dre",
            "last_name": "day",
            "username": "dreday",
            "email": "randomEmail@gmail.com",
            "password": "password"
        }
        
        response = self.client.post('/v1/api/register/', data, format='json')
      
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register(self):
        # data for the object
        data = {
            "first_name": "dre",
            "last_name": "day",
            "username": "dreday",
            "email": "randomEmail@dremail.com",
            "password": "password"
        }
        
        response = self.client.post('/v1/api/register/', data, format='json')
      
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'dre')
        self.assertEqual(response.data['last_name'], 'day')
        self.assertEqual(response.data['username'], 'dreday')
        self.assertEqual(response.data['email'], 'randomEmail@dremail.com')


# This class tests the EmailTransferViewSet class.
class TestEmailTransferViewSet(TestCase):
        
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test_user@dremail.com', password='password', username='user')
        self.client.login(email='test_user@dremail.com', password='password')
        # create recipient
        self.recipient = User.objects.create_user(email='recipient@dremail.com', password='password', username="recipient")
        self.email_id = None

        self.create_email_transfer()


    def create_email_transfer(self):

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
        self.assertEqual(response.data['recipient']['email'], "recipient@dremail.com")
        self.email_id = response.data['id']


    def test_get_email_transfer(self):

        response = self.client.get(f'/v1/api/emailTransfers/{self.email_id}')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email']['message'], "This is a test message")
        self.assertEqual(response.data['email']['subject'], "This is a test subject")


    def test_delete_email_transfer(self):
        response = self.client.delete(f'/v1/api/emailTransfers/{self.email_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_update_email_transfer(self):
        data = {
            # data for the object
            "recipient_id": self.recipient.id,
            "email": {
                "message": "This is another test message",
                "subject": "This is another test subject"
            }
        }

        response = self.client.put(f'/v1/api/emailTransfers/{self.email_id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_move_email_to_spam(self):
        data = {
            # data for the object
            "email_id": self.email_id,
            "destination": "spam"
        }

        response = self.client.post(f'/v1/api/emailTransfers/inbox', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test removing the current instance of the class from the spam list.
        self.remove_from_spam()

    def test_move_email_to_favorites(self):
        data = {
            # data for the object
            "email_id": self.email_id,
            "destination": "favorites"
        }

        response = self.client.post(f'/v1/api/emailTransfers/inbox', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test removing the current instance of the class from the favorites list.
        self.remove_from_favorites()


    def test_move_email_to_junk(self):
        data = {
            # data for the object
            "email_id": self.email_id,
            "destination": "junk"
        }

        response = self.client.post(f'/v1/api/emailTransfers/inbox', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test removing the item from the junk list.
        self.remove_from_junk()


    def remove_from_spam(self):
        data = {
            # data for the object
            "email_id": self.email_id,
        }

        response = self.client.post(f'/v1/api/emailTransfers/spam', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def remove_from_favorites(self):
        data = {
            # data for the object
            "email_id": self.email_id,
        }

        response = self.client.post(f'/v1/api/emailTransfers/favorites', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def remove_from_junk(self):
        data = {
            # data for the object
            "email_id": self.email_id,
        }

        response = self.client.post(f'/v1/api/emailTransfers/junk', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_read_status(self):
        data = {
            # data for the object
            "id": self.email_id,
        }

        response = self.client.post(f'/v1/api/emailTransfers/update_read_status', data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



# This class tests the EmailViewSet class.
class TestEmailViewSet(TestCase):
        
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email='admin@dremail.com', password='password', username='admin', is_superuser=True, is_staff=True)
        self.client.login(email='admin@dremail.com', password='password')
        self.email_id = None
        self.create_email()


    def test_user_create_email(self):
        """
        The function tests that a user can't create an email if they are not logged in
        """
        user = User.objects.create_user(email='test_user@dremail.com', password='password', username='user')
        self.client.login(email='test_user@dremail.com', password='password')

        # data for the object
        data = {
            
            "message": "This is a test message",
            "subject": "This is a test subject"
        }
        
        response = self.client.post('/v1/api/emails/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
      


    def create_email(self):

        # data for the object
        data = {
            
            "message": "This is a test message",
            "subject": "This is a test subject"
        }
        
        response = self.client.post('/v1/api/emails/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "This is a test message")
        self.assertEqual(response.data['subject'], "This is a test subject")
        self.email_id = response.data['id']


    def test_get_email(self):

        response = self.client.get(f'/v1/api/emails/{self.email_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "This is a test message")
        self.assertEqual(response.data['subject'], "This is a test subject")


    def test_delete_email(self):
        response = self.client.delete(f'/v1/api/emails/{self.email_id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_update_email(self):
        data = {
            # data for the object
            "message": "This is another test message",
            "subject": "This is another test subject"
        }

        response = self.client.put(f'/v1/api/emails/{self.email_id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "This is another test message")
        self.assertEqual(response.data['subject'], "This is another test subject")


class TestDraftViewSet(TestCase):
        
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test_user@dremail.com', password='password', username='user')
        self.client.login(email='test_user@dremail.com', password='password')
        self.email_id = None

        self.create_draft()


    def create_draft(self):

        # data for the object
        data = {
            "email": {
                "message": "This is a test message",
                "subject": "This is a test subject"
            }
        }
        
        response = self.client.post('/v1/api/drafts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email']['message'], "This is a test message")
        self.assertEqual(response.data['email']['subject'], "This is a test subject")
        self.email_id = response.data['email']['id']


    def test_get_draft(self):

        response = self.client.get(f'/v1/api/drafts/{self.email_id}')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email']['message'], "This is a test message")
        self.assertEqual(response.data['email']['subject'], "This is a test subject")


    def test_delete_draft(self):
        response = self.client.delete(f'/v1/api/drafts/{self.email_id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


    def test_update_draft(self):
        data = {
            # data for the object
            "email": {
                "message": "This is another test message",
                "subject": "This is another test subject"
            }
        }

        response = self.client.put(f'/v1/api/drafts/{self.email_id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# We're testing the UserViewSet class
class TestUserViewSet(TestCase):
        
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test_user@dremail.com', password='password', username='user')
        self.client.login(email='test_user@dremail.com', password='password')


    def test_create_user(self):
        """
        We're testing the create_user function in the UserViewSet class.
        The test should return a 405 because we have prohibited that method
        """

        # data for the object
        data = {
            "first_name": "dre",
            "last_name": "day",
            "username": "user",
            "email": "randomEmail@dremail.com",
            "password": "password"
        }
        
        response = self.client.post('/v1/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_get_user(self):

        response = self.client.get(f'/v1/api/users/{self.user.id}')
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user')
        self.assertEqual(response.data['email'], 'test_user@dremail.com')


    def test_delete_user(self):
        response = self.client.delete(f'/v1/api/users/{self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    
    def test_update_user(self):
        """
        The test_update_user function tests the update user endpoint, 
        and should return a 405 error code because we have restricted this method
        """
        data = {
            "first_name": "andrew",
            "last_name": "duncan",
            "username": "dreday1",
            "email": "random@dremail.com",
        }

        response = self.client.put(f'/v1/api/users/{self.user.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_user(self):
        data = {
            "first_name": "andrew",
            "last_name": "duncan",
            "username": "dreday1",
            "email": "random@dremail.com",
        }

        response = self.client.patch(f'/v1/api/users/{self.user.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'andrew')
        self.assertEqual(response.data['last_name'], 'duncan')
        self.assertEqual(response.data['username'], 'dreday1')
        self.assertEqual(response.data['email'], 'random@dremail.com')

    
# We're testing the create_user function in the UserViewSet class.
# The test should return a 405 because we have prohibited that method
class TestEmailGroupViewSet(TestCase):
        
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test_user@dremail.com', password='password', username='user')
        self.client.login(email='test_user@dremail.com', password='password')
        self.group_id = None

        self.create_email_group()


    def create_email_group(self):
        """
        We're testing the create_user function in the UserViewSet class.
        The test should return a 405 because we have prohibited that method
        """

        # data for the object
        data = {
            "name": "Test Group",
            "description": "This is a test group",
        }
        
        response = self.client.post('/v1/api/groups/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.group_id = response.data['id']
        self.assertEqual(response.data['name'], 'Test Group')
        self.assertEqual(response.data['description'], 'This is a test group')


    def test_get_email_group(self):

        response = self.client.get(f'/v1/api/groups/{self.group_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Group')
        self.assertEqual(response.data['description'], 'This is a test group')


    def test_delete_email_group(self):
        response = self.client.delete(f'/v1/api/groups/{self.group_id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    
    def test_update_email_group(self):
        """
        The test_update_user function tests the update user endpoint, 
        and should return a 405 error code because we have restricted this method
        """
        data = {
            "name": "Another Test Group",
            "description": "This is another test group",
        }

        response = self.client.put(f'/v1/api/groups/{self.group_id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Another Test Group')
        self.assertEqual(response.data['description'], 'This is another test group')

    
    def test_add_user_to_group(self):
        # data for the object
        data = {
            "id": self.user.id,
        }
        
        response = self.client.post(f'/v1/api/groups/{self.group_id}/add_member', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_remove_user_from_group(self):
        # data for the object
        data = {
            "id": self.user.id,
        }

        response = self.client.post(f'/v1/api/groups/{self.group_id}/remove_member', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_email_to_group(self):

        # data for the object
        data = {
            
            "group_id": self.group_id,
            "email": {
                "message": "This is a test message",
                "subject": "This is a test subject"
            }
        }
        
        response = self.client.post('/v1/api/emailTransfers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email']['message'], "This is a test message")
        self.assertEqual(response.data['email']['subject'], "This is a test subject")
        self.assertEqual(response.data['group']['name'], "Test Group")
