from rest_framework.test import APIClient
from account.models import Account
from django.utils import timezone
from django.test import TestCase
from datetime import timedelta
from os import environ
import json

API_URL = "http://localhost/api/accounts/"

TEST_USER_TOKEN = environ.get("TEST_USER_TOKEN", "")
TEST_USERNAME = environ.get("TEST_USERNAME", "")
TEST_USER_ID = environ.get("TEST_USER_ID", 0)


class AccountModelTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        obj = Account.create(username=TEST_USERNAME)
        obj.id = TEST_USER_ID
        obj.save()

    # def test_create_and_delete_user(self):
    #     data = {
    #         "email": "user_test_only_purpose@gmail.com",
    #         "username": "user_test_only_purpose",
    #         "password": "password"
    #     }
    #     response = self.client.post(API_URL, data=data)
    #     self.assertEqual(response.status_code, 201)
    #     token = response.json()["token"]
    #     user_id = response.json()["id"]
    #     self.client.credentials(HTTP_AUTHORIZATION=f"token {token}")
    #     response = self.client.delete(f"{API_URL}{user_id}/")
    #     self.assertEqual(response.status_code, 204)

    def test_get_user(self):
        response = self.client.get(API_URL)
        self.assertEqual(response.status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION=f"wrong token")
        response = self.client.get(API_URL)
        self.assertEqual(response.status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION=f"token {TEST_USER_TOKEN}")
        response = self.client.get(API_URL)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"{API_URL}{TEST_USER_ID}/")
        self.assertEqual(response.status_code, 200)

    def test_get_user_by_id(self):
        response = self.client.get(f"{API_URL}{TEST_USER_ID}/")
        self.assertEqual(response.status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION=f"token {TEST_USER_TOKEN}")
        response = self.client.get(f"{API_URL}0/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get(f"{API_URL}{TEST_USER_ID}/")
        self.assertEqual(response.status_code, 200)

    def test_create_user(self):
        data = {"username": "test username"}
        response = self.client.post(API_URL, data=data)
        self.assertEqual(response.status_code, 400)
        data = {"email": "test_email@test.com"}
        response = self.client.post(API_URL, data=data)
        self.assertEqual(response.status_code, 400)
        data = {"email": "test_email@test.com",
                "password": "password", "username": TEST_USERNAME}
        response = self.client.post(API_URL, data=data)
        self.assertEqual(response.status_code, 400)

    def test_update_user(self):
        data = {"username": TEST_USERNAME}
        response = self.client.patch(f"{API_URL}{TEST_USER_ID}/", data=data)
        self.assertEqual(response.status_code, 403)
        response = self.client.put(f"{API_URL}{TEST_USER_ID}/", data=data)
        self.assertEqual(response.status_code, 403)
        self.client.credentials(HTTP_AUTHORIZATION=f"token {TEST_USER_TOKEN}")
        response = self.client.patch(f"{API_URL}{TEST_USER_ID}/", data=data)
        self.assertEqual(response.status_code, 200)
        response = self.client.put(f"{API_URL}{TEST_USER_ID}/", data=data)
        self.assertEqual(response.status_code, 200)
