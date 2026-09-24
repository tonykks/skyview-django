import os
import urllib.error
from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .utils import is_skyview_owner
from .views import _fetch_github_archive_info

User = get_user_model()


class TestOwnerAuthUtils(TestCase):
    def setUp(self):
        self.owner_user = User.objects.create_user(username="owner", password="password123")
        self.normal_user = User.objects.create_user(username="johndoe", password="password123")
        self.superuser = User.objects.create_superuser(username="superadmin", password="password123")

    @override_settings(SKYVIEW_OWNER_USERNAMES=[])
    def test_missing_configuration_denies_all_including_superuser(self):
        self.assertFalse(is_skyview_owner(None))
        self.assertFalse(is_skyview_owner(self.normal_user))
        self.assertFalse(is_skyview_owner(self.owner_user))
        self.assertFalse(is_skyview_owner(self.superuser))

    @override_settings(SKYVIEW_OWNER_USERNAMES=["owner"])
    def test_configured_owner_controls_access_strictly(self):
        self.assertFalse(is_skyview_owner(None))
        self.assertFalse(is_skyview_owner(self.normal_user))
        self.assertTrue(is_skyview_owner(self.owner_user))
        self.assertFalse(is_skyview_owner(self.superuser))

    @override_settings(SKYVIEW_OWNER_USERNAMES=["TONY"])
    def test_case_insensitive_owner_username_matching(self):
        tony_upper = User.objects.create_user(username="TONY_U", password="password123")
        tony_lower = User.objects.create_user(username="tony", password="password123")
        tony_mixed = User.objects.create_user(username="Tony_M", password="password123")
        self.assertTrue(is_skyview_owner(tony_lower))


@override_settings(SKYVIEW_OWNER_USERNAMES=["owner"])
class TestPrivateReportsPortalViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = User.objects.create_user(username="owner", password="password123", is_staff=True)
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

    @patch("skyview.views._fetch_github_archive_info")
    def test_owner_access_portal_main_and_sandbox_security(self, mock_info):
        mock_info.return_value = (["2026-09-17"], None)
        self.client.login(username="owner", password="password123")

        res = self.client.get(reverse("private_reports"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "2026-09-17")
        self.assertContains(res, "새 탭에서 열기 ↗")
        content_str = res.content.decode("utf-8")
        self.assertIn("sandbox=", content_str)
        self.assertNotIn("allow-same-origin", content_str)
        self.assertNotIn("allow-scripts", content_str)
        self.assertIn("allow-popups", content_str)
        self.assertNotIn('<a href="/admin/logout/?next=/"', content_str)
        self.assertIn('method="post"', content_str)
        self.assertIn('action="/admin/logout/?next=/"', content_str)
        self.assertIn('csrfmiddlewaretoken', content_str)
        self.assertIn("date-list-panel", content_str)
        self.assertIn("date-item-btn", content_str)
        self.assertIn("selectDate", content_str)

    @patch("skyview.views._fetch_github_archive_info")
    def test_portal_logout_clears_session(self, mock_info):
        mock_info.return_value = (["2026-09-17"], None)
        self.client.login(username="owner", password="password123")

        # Initial owner access works
        res = self.client.get(reverse("private_reports"))
        self.assertEqual(res.status_code, 200)

        # POST to logout invalidates session
        logout_res = self.client.post("/admin/logout/?next=/")
        self.assertIn(logout_res.status_code, [200, 302])

        # Subsequent requests are forbidden
        res1 = self.client.get(reverse("private_reports"))
        self.assertEqual(res1.status_code, 403)

        res2 = self.client.get(reverse("private_reports_api_list"))
        self.assertEqual(res2.status_code, 403)

        res3 = self.client.get(reverse("private_reports_api_view", kwargs={"date_str": "2026-09-17"}))
        self.assertEqual(res3.status_code, 403)

    @patch("skyview.views._fetch_github_archive_info")
    def test_period_filter_all_returns_all_dates(self, mock_info):
        mock_info.return_value = (["2026-09-17", "2026-08-04", "2026-08-03"], None)
        self.client.login(username="owner", password="password123")

        res = self.client.get(reverse("private_reports") + "?period=all")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["dates"], ["2026-09-17", "2026-08-04", "2026-08-03"])

    @patch("skyview.views._fetch_github_archive_info")
    def test_period_filter_custom_range(self, mock_info):
        mock_info.return_value = (["2026-09-17", "2026-08-04", "2026-08-03"], None)
        self.client.login(username="owner", password="password123")

        res = self.client.get(reverse("private_reports") + "?period=custom&start_date=2026-08-01&end_date=2026-08-10")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context["dates"], ["2026-08-04", "2026-08-03"])

    @patch("skyview.views._fetch_github_archive_info")
    def test_empty_period_shows_no_reports_in_period_message(self, mock_info):
        mock_info.return_value = (["2026-08-04"], None)
        self.client.login(username="owner", password="password123")

        res = self.client.get(reverse("private_reports") + "?period=1day")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.context["has_no_reports_in_period"])
        self.assertContains(res, "선택한 기간")

    @patch("skyview.views._fetch_github_archive_info")
    def test_api_list_supports_period_filtering(self, mock_info):
        mock_info.return_value = (["2026-09-17", "2026-08-04", "2026-08-03"], None)
        self.client.login(username="owner", password="password123")

        res = self.client.get(reverse("private_reports_api_list") + "?period=custom&start_date=2026-08-01&end_date=2026-08-10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["dates"], ["2026-08-04", "2026-08-03"])

    @patch("skyview.views._fetch_github_archive_info")
    def test_owner_access_api_list(self, mock_info):
        mock_info.return_value = (["2026-09-17"], None)
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
        self.assertEqual(res.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertIn("Test Report", res.content.decode("utf-8"))

    @patch("urllib.request.urlopen")
    def test_github_api_failure_fails_closed(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection Refused")

        self.client.login(username="owner", password="password123")
        res = self.client.get(reverse("private_reports_api_view", kwargs={"date_str": "2026-09-17"}))

        self.assertEqual(res.status_code, 502)
        self.assertNotIn("token", res.content.decode("utf-8").lower())

    def test_fetch_github_archive_info_distinguishes_missing_token(self):
        with patch.dict(os.environ, {}, clear=True):
            dates, err = _fetch_github_archive_info()
            self.assertEqual(dates, [])
            self.assertIsNotNone(err)
            self.assertIn("EMAIL_AGENT_GITHUB_TOKEN", err)

    @patch("urllib.request.urlopen")
    def test_fetch_github_archive_info_distinguishes_http_error(self, mock_urlopen):
        err_404 = urllib.error.HTTPError("url", 404, "Not Found", None, None)
        mock_urlopen.side_effect = err_404
        with patch.dict(os.environ, {"EMAIL_AGENT_GITHUB_TOKEN": "fake_token"}, clear=True):
            dates, err = _fetch_github_archive_info()
            self.assertEqual(dates, [])
            self.assertIsNotNone(err)
            self.assertIn("인증/권한 오류", err)

    @patch('skyview.views._fetch_github_archive_info')
    def test_portal_responsive_layout_css_rules(self, mock_info):
        mock_info.return_value = (['2026-09-24', '2026-09-23'], None)
        self.client.login(username='owner', password='password123')

        res = self.client.get(reverse('private_reports'))
        self.assertEqual(res.status_code, 200)
        content_str = res.content.decode('utf-8')
        
        # Verify responsive CSS rules that guarantee iframe width > 760px on desktop/intermediate screens
        self.assertIn('@media (max-width: 1120px)', content_str)
        self.assertIn('min-width: 780px;', content_str)
        self.assertIn('width: 250px;', content_str)
