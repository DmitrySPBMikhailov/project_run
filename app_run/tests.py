# from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase
from django.conf import settings


class CompanyInfoTestCase(APITestCase):
    def setUp(self):
        self.result = settings.COMPANY_INFORMATION
        self.url = reverse("get_company_details")

    def test_get_info(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["company_name"], self.result["company_name"])
        self.assertEqual(response.data["slogan"], self.result["slogan"])
        self.assertEqual(response.data["contacts"], self.result["contacts"])
