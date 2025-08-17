# from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase
from django.conf import settings
from .models import Run
from django.contrib.auth.models import User


class CompanyInfoTestCase(APITestCase):
    """
    Test case for getting Company Information
    """

    def setUp(self):
        self.result = settings.COMPANY_INFORMATION
        self.url = reverse("get_company_details")

    def test_get_info(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["company_name"], self.result["company_name"])
        self.assertEqual(response.data["slogan"], self.result["slogan"])
        self.assertEqual(response.data["contacts"], self.result["contacts"])


class RunTestCase(APITestCase):
    """
    Test case for Run instances
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.run1 = Run.objects.create(athlete=self.user, comment="cool")
        self.url_list = reverse("runs-list")

    def test_get_runs(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["comment"], self.run1.comment)
        self.assertEqual(response.data[0]["id"], self.run1.id)
        self.assertEqual(response.data[0]["athlete"], self.run1.athlete.id)


class UsersTestCase(APITestCase):
    """
    Test case for getting Users based on is_staff property and Query Params
    """

    def setUp(self):
        self.coach = User.objects.create_user(
            username="coachuser", password="password123", is_staff=True
        )
        self.athlete = User.objects.create_user(
            username="athleteuser", password="password123"
        )
        self.superuser = User.objects.create_superuser(
            username="my_super", password="password123"
        )
        self.url_list_coach = "/api/users/?type=coach"
        self.url_list_athlete = "/api/users/?type=athlete"
        self.url_list_random = "/api/users/?type=test"
        self.url_list_without_params = "/api/users"

    def test_get_coaches(self):
        response = self.client.get(self.url_list_coach)
        self.assertEqual(response.data[0]["type"], "coach")

    def test_get_athletes(self):
        response = self.client.get(self.url_list_athlete)
        self.assertEqual(response.data[0]["type"], "athlete")

    def test_get_random(self):
        response = self.client.get(self.url_list_random)
        self.assertEqual(len(response.data), 2)
