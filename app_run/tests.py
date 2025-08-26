# from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase
from django.conf import settings
from .models import Run, Challenge, StatusChoices, Position
from django.contrib.auth.models import User
from rest_framework import status


class CompanyInfoTestCase(APITestCase):
    """
    Test case for getting Company Information
    """

    def setUp(self):
        self.result = settings.COMPANY_INFORMATION
        self.url = reverse("get_company_details")

    def test_get_info(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["comment"], self.run1.comment)
        self.assertEqual(response.data[0]["id"], self.run1.id)
        self.assertEqual(response.data[0]["athlete"], self.run1.athlete.id)
        self.assertEqual(response.data[0]["athlete_data"]["id"], self.run1.athlete.id)
        self.assertEqual(response.data[0]["status"], StatusChoices.INIT)


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


class UsersSearch(APITestCase):
    """
    Test case for searching by first_name or last_name
    """

    def setUp(self):
        self.my_user = User.objects.create_user(
            username="coachuser",
            password="password123",
            first_name="first",
            last_name="last",
        )
        self.url_first = "/api/users/?search=fir"
        self.url_last = "/api/users/?search=la"

    def test_search(self):
        response = self.client.get(self.url_first)
        self.assertEqual(response.data[0]["id"], self.my_user.id)


class ChangeRunStatusTest(APITestCase):
    """
    Test case for changing status
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.run1 = Run.objects.create(athlete=self.user, comment="cool")
        self.run_in_progress = Run.objects.create(
            athlete=self.user, comment="cool", status=StatusChoices.IN_PROGRESS
        )
        self.url_start = f"/api/runs/{self.run1.id}/start/"
        self.url_start_wrong = f"/api/runs/{self.run_in_progress.id}/start/"
        self.url_stop = f"/api/runs/{self.run_in_progress.id}/stop/"
        self.url_stop_wrong = f"/api/runs/{self.run1.id}/stop/"
        self.url_no_run = f"/api/runs/3/start/"

    def test_status_change_no_run(self):
        response = self.client.post(self.url_no_run)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_status_change_start(self):
        response = self.client.post(self.url_start)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_status_change_start_wrong(self):
        response = self.client.post(self.url_start_wrong)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_status_change_stop(self):
        response = self.client.post(self.url_stop)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_status_wrong_stop(self):
        response = self.client.post(self.url_stop_wrong)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetAthleteInfoTest(APITestCase):
    """
    Test case for getting additional info about an athlete
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.url = f"/api/athlete_info/{self.user.id}/"
        self.valid_payload = {
            "goals": "yo!",
            "weight": 98,
        }
        self.invalid_payload = {"goals": "yo!", "weight": 901}
        self.invalid_payload2 = {"weight": 99}

    def test_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put(self):
        response = self.client.put(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_invalid(self):
        response = self.client.put(self.url, self.invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_invalid2(self):
        response = self.client.put(self.url, self.invalid_payload2, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetChallengesTest(APITestCase):
    """
    Test case for getting Challenges
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        for i in range(9):
            Run.objects.create(
                athlete=self.user, comment=f"run {i}", status=StatusChoices.FINISHED
            )
        self.run_to_stop = Run.objects.create(
            athlete=self.user, comment="run 10", status=StatusChoices.IN_PROGRESS
        )
        self.url = f"/api/runs/{self.run_to_stop.id}/stop/"

    def test_stop_run_creates_challenge(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.run_to_stop.refresh_from_db()  # make sure that status has been changed
        self.assertEqual(self.run_to_stop.status, StatusChoices.FINISHED)
        self.assertTrue(Challenge.objects.filter(athlete=self.user).exists())


class PositionTest(APITestCase):
    """
    Test case for Position instances
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.run1 = Run.objects.create(
            athlete=self.user, comment="cool", status=StatusChoices.IN_PROGRESS
        )
        self.position1 = Position.objects.create(
            run=self.run1, latitude="89.0", longitude="179.9"
        )
        self.url_delete = f"/api/positions/{self.position1.id}/"
        self.url_create = "/api/positions/"
        self.valid_payload = {
            "run": self.run1.id,
            "latitude": "89.0",
            "longitude": "179.9",
        }
        self.invalid_latitude = {
            "run": self.run1.id,
            "latitude": "90.1",
            "longitude": "179.9",
        }
        self.invalid_longtitude = {
            "run": self.run1.id,
            "latitude": "80.1",
            "longitude": "-180.9",
        }
        self.invalid_float_digits = {
            "run": self.run1.id,
            "latitude": "80.1",
            "longitude": "-170.99999",
        }

    def test_create_position(self):
        response = self.client.post(self.url_create, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Position.objects.filter(id=response.data["id"]).exists())

    def test_create_wrong_position(self):
        response = self.client.post(
            self.url_create, self.invalid_latitude, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wrong_position2(self):
        response = self.client.post(
            self.url_create, self.invalid_longtitude, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wrong_position3(self):
        response = self.client.post(
            self.url_create, self.invalid_float_digits, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_position(self):
        response = self.client.delete(self.url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
