from django.test import TestCase
from django.shortcuts import reverse

# Create your tests here.

class DreMailApiTestCase(TestCase):

    def setUp(self) -> None:
        self.users_url_v1 = reverse("v1.0:users")
        self.users_url_v1_1 = reverse("v1.1:users")

    def test_users_url(self):
        print(self.users_url_v1)
        print(self.users_url_v1_1)

