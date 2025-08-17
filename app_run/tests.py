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
