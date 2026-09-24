from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .utils import is_skyview_owner

User = get_user_model()


class TestOwnerAuthUtils(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(username="owner", password="password123")
        self.normal_user = User.objects.create_user(username="johndoe", password="password123")
        self.superuser = User.objects.create_superuser(username="superadmin", password="password123")

    def test_is_skyview_owner_evaluations(self):
        self.assertFalse(is_skyview_owner(None))
        self.assertFalse(is_skyview_owner(self.normal_user))
        self.assertTrue(is_skyview_owner(self.owner_user))
        self.assertTrue(is_skyview_owner(self.superuser))


class TestPrivateReportsPortalViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="password123")
        self.non_owner = User.objects.create_user(username="attacker", password="password123")

    def test_anonymous_user_access_is_forbidden(self):
        res1 = self.client.get(reverse("private_reports"))
        self.assertEqual(res1.status_code, 403)

        res2 = self.client.get(reverse("private_reports_api_list"))
        self.assertEqual(res2.status_code, 403)

        res3 = self.client.get(reverse("private_reports_api_view", kwargs={"date_str": "2026-09-17"}))
        self.assertEqual(res3.status_code, 403)

    def test_non_owner_user_access_is_forbidden(self):
        self.client.login(username="attacker", password="password123")
        
        res1 = self.client.get(reverse("private_reports"))
        self.assertEqual(res1.status_code, 403)

        res2 = self.client.get(reverse("private_reports_api_list"))
        self.assertEqual(res2.status_code, 403)

        res3 = self.client.get(reverse("private_reports_api_view", kwargs={"date_str": "2026-09-17"}))
        self.assertEqual(res3.status_code, 403)

    @patch("skyview.views._fetch_github_archive_list")
    def test_owner_access_portal_main(self, mock_list):
        mock_list.return_value = ["2026-09-17"]
        self.client.login(username="owner", password="password123")

        res = self.client.get(reverse("private_reports"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "2026-09-17")
        self.assertContains(res, "Email Agent 일일 브리핑 Portal")

    @patch("skyview.views._fetch_github_archive_list")
    def test_owner_access_api_list(self, mock_list):
        mock_list.return_value = ["2026-09-17"]
        self.client.login(username="owner", password="password123")

        res = self.client.get(reverse("private_reports_api_list"))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["dates"], ["2026-09-17"])

    def test_path_traversal_invalid_date_returns_400(self):
        self.client.login(username="owner", password="password123")

        res = self.client.get("/private-reports/api/view/../../etc/passwd/")
        self.assertEqual(res.status_code, 404)

        res2 = self.client.get(reverse("private_reports_api_view", kwargs={"date_str": "invalid-date"}))
        self.assertEqual(res2.status_code, 400)

    @patch("urllib.request.urlopen")
    def test_owner_access_api_view_success_and_security_headers(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<!DOCTYPE html><html><body>Test Report</body></html>"
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        self.client.login(username="owner", password="password123")
        res = self.client.get(reverse("private_reports_api_view", kwargs={"date_str": "2026-09-17"}))

        self.assertEqual(res.status_code, 200)
        self.assertIn("Cache-Control", res.headers)
        self.assertIn("no-store", res.headers["Cache-Control"])
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("Test Report", res.content.decode("utf-8"))

    @patch("urllib.request.urlopen")
    def test_github_api_failure_fails_closed(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection Refused")

        self.client.login(username="owner", password="password123")
        res = self.client.get(reverse("private_reports_api_view", kwargs={"date_str": "2026-09-17"}))

        self.assertEqual(res.status_code, 502)
        self.assertNotIn("token", res.content.decode("utf-8").lower())
