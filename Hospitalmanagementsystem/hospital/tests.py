from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import *
# Create your tests here.

class LoginAPITestCase(TestCase): 
    def setUp(self):
        self.client = APIClient()
        self.username = 'usesrname'
        self.password = 'password'
        self.user = CustomUser.objects.create_user(username = self.username, password = self.password)
        self.url = reverse('rest_framework:login')

    def test_login(self):
        data = {'username': self.username, 'password': self.password}
        response = self.client.post(self.url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        data = {'username': self.username,'password': 'testpass123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

