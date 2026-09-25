import os
import urllib.error
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .utils import is_skyview_owner
from .views import (
    KST, _fetch_github_archive_info, _fetch_toss_archive_info,
    _get_toss_local_archive_dir, _get_toss_token,
)

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


@override_settings(SKYVIEW_OWNER_USERNAMES=["owner"])
class TestTossReportsPortalViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="owner", password="password123", is_staff=True)
        cls.non_owner = User.objects.create_user(username="other", password="password123")

    def setUp(self):
        archive = tempfile.TemporaryDirectory()
        self.addCleanup(archive.cleanup)
        self.archive_dir = Path(archive.name)
        self.manifest = {
            "date_list": ["2026-09-25", "2026-08-17", "2026-07-29"],
            "missing_dates": ["2026-08-07", "2026-08-25"],
            "dates": [],
        }
        for date_str, run_ids in (
            ("2026-09-25", ["36072393214"]),
            ("2026-08-17", ["31971754794", "32038289382"]),
            ("2026-07-29", ["30436015887"]),
        ):
            runs = []
            for index, run_id in enumerate(run_ids):
                relative = f"{date_str.replace('-', '/')}/report_run-{run_id}.html"
                target = self.archive_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(f"<!doctype html><html><body>Report {run_id}</body></html>", encoding="utf-8")
                runs.append({
                    "run_id": run_id, "time": ["05:51:32", "23:14:03"][index],
                    "is_default": run_id == run_ids[-1],
                    "is_derived_html": date_str == "2026-07-29",
                    "rel_html_path": f"archive/{relative}",
                })
            self.manifest["dates"].append({
                "date": date_str, "runs": runs, "run_count": len(runs),
                "default_run_id": run_ids[-1], "default_html_path": runs[-1]["rel_html_path"],
            })
        self.write_manifest()
        local_patch = patch("skyview.views._get_toss_local_archive_dir", return_value=self.archive_dir)
        local_patch.start()
        self.addCleanup(local_patch.stop)
        network_patch = patch("skyview.views.urllib.request.urlopen")
        self.urlopen = network_patch.start()
        self.urlopen.side_effect = AssertionError("Unexpected network access")
        self.addCleanup(network_patch.stop)

    def write_manifest(self):
        (self.archive_dir / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def report_url(self, date_str="2026-09-25", run_id=None):
        kwargs = {"date_str": date_str}
        if run_id:
            kwargs["run_id"] = run_id
        return reverse("toss_reports_api_view_run" if run_id else "toss_reports_api_view", kwargs=kwargs)

    def assert_forbidden(self):
        for url in (reverse("toss_reports"), reverse("toss_reports_api_list"), self.report_url(), self.report_url(run_id="36072393214")):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
        self.urlopen.assert_not_called()

    def test_anonymous_user_access_is_forbidden(self):
        self.assert_forbidden()

    def test_non_owner_user_access_is_forbidden(self):
        self.client.force_login(self.non_owner)
        self.assert_forbidden()

    def test_owner_access_portal_main(self):
        self.client.force_login(self.owner)
        res = self.client.get(reverse("toss_reports"))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "skyview/toss_reports.html")
        self.assertEqual(res.context["selected_date"], "2026-09-25")
        self.assertEqual(res.context["selected_run_id"], "36072393214")
        self.assertContains(res, 'sandbox="allow-scripts allow-popups"')
        self.assertNotContains(res, "allow-same-origin")
        for text in ('loading="lazy"', 'method="post"', 'action="/admin/logout/?next=/"', "csrfmiddlewaretoken", "date-list-panel", "하루 2회 실행", 'href="/private-reports/"'):
            self.assertContains(res, text)
        self.assertNotContains(res, 'class="run-picker"')

    def test_owner_access_api_view_success(self):
        self.client.force_login(self.owner)
        res = self.client.get(self.report_url())
        self.assertContains(res, "Report 36072393214")
        self.assertEqual(res.headers["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(res.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(res.headers["X-Frame-Options"], "SAMEORIGIN")
        self.assertEqual(res.headers["Cache-Control"], "no-store, private, no-cache, must-revalidate")
        self.urlopen.assert_not_called()

    @patch("skyview.views._fetch_toss_archive_info")
    def test_unissued_date_returns_404(self, info):
        self.client.force_login(self.owner)
        for date_str in ("2026-08-07", "2026-08-25"):
            self.assertContains(self.client.get(self.report_url(date_str)), "보고서가 발행되지 않았습니다", status_code=404)
        info.assert_not_called()

    @patch("skyview.views._fetch_toss_archive_info")
    def test_invalid_date_format_returns_400(self, info):
        self.client.force_login(self.owner)
        for date_str in ("invalid-date", "2026-8-17", "2026-08-17suffix"):
            with self.subTest(date=date_str):
                self.assertEqual(self.client.get(self.report_url(date_str)).status_code, 400)
        info.assert_not_called()

    def test_multi_run_date_targeting(self):
        self.client.force_login(self.owner)
        for run_id in ("31971754794", "32038289382"):
            self.assertContains(self.client.get(self.report_url("2026-08-17", run_id)), f"Report {run_id}")
        self.assertContains(self.client.get(self.report_url("2026-08-17")), "Report 32038289382")
        res = self.client.get(reverse("toss_reports"), {"date": "2026-08-17", "run_id": "31971754794"})
        self.assertEqual(res.context["selected_run_id"], "31971754794")
        self.assertEqual(len(res.context["runs"]), 2)
        for text in ('class="run-picker"', "05:51:32", "23:14:03", f'src="{self.report_url("2026-08-17", "31971754794")}"'):
            self.assertContains(res, text)

    def test_unknown_date_or_run_does_not_serve_another_report(self):
        self.client.force_login(self.owner)
        for url in (self.report_url("2026-08-01"), self.report_url("2026-08-17", "unknown"), self.report_url("2026-08-17", "36072393214")):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_period_filter_and_selected_date_fallback(self):
        self.client.force_login(self.owner)
        query = {"period": "custom", "start_date": "2026-08-01", "end_date": "2026-08-31", "date": "2026-09-25", "run_id": "unknown"}
        res = self.client.get(reverse("toss_reports"), query)
        self.assertEqual(res.context["dates"], ["2026-08-17"])
        self.assertEqual(res.context["selected_date"], "2026-08-17")
        self.assertEqual(res.context["selected_run_id"], "32038289382")
        data = self.client.get(reverse("toss_reports_api_list"), query).json()
        self.assertEqual(data, {"ok": True, "dates": ["2026-08-17"], "all_dates": self.manifest["date_list"], "manifest": self.manifest})

    @patch("skyview.views.datetime")
    def test_recent_three_days_filter(self, clock):
        clock.now.return_value = datetime(2026, 9, 27, tzinfo=KST)
        clock.strptime = datetime.strptime
        self.client.force_login(self.owner)
        res = self.client.get(reverse("toss_reports"), {"period": "3days"})
        self.assertEqual(res.context["dates"], ["2026-09-25"])
        self.assertEqual(res.context["start_date"], "2026-09-25")
        self.assertEqual(res.context["end_date"], "2026-09-27")

    def test_empty_period_and_empty_archive(self):
        self.client.force_login(self.owner)
        res = self.client.get(reverse("toss_reports"), {"period": "custom", "start_date": "2025-01-01", "end_date": "2025-01-02"})
        self.assertContains(res, "선택한 기간")
        self.assertTrue(res.context["has_no_reports_in_period"])
        self.assertNotContains(res, 'id="report-frame"')
        self.manifest = {"date_list": [], "dates": []}
        self.write_manifest()
        res = self.client.get(reverse("toss_reports"))
        self.assertContains(res, "보관된 보고서가 없습니다.")
        self.assertNotContains(res, 'id="report-frame"')

    def test_derived_report_notice(self):
        self.client.force_login(self.owner)
        res = self.client.get(reverse("toss_reports"), {"date": "2026-07-29"})
        self.assertContains(res, "Markdown에서 복원한 보고서")
        self.assertContains(res, 'data-legacy-date="true"')
        self.assertContains(self.client.get(self.report_url("2026-07-29")), "Report 30436015887")

    def test_manifest_path_cannot_escape_archive(self):
        self.client.force_login(self.owner)
        for path in ("archive/../../secret.html", "/secret.html", "archive/C:/secret.html", r"archive/..\secret.html", "https://example.com/report.html"):
            with self.subTest(path=path):
                self.manifest["dates"][0]["runs"][0]["rel_html_path"] = path
                self.write_manifest()
                self.assertEqual(self.client.get(self.report_url()).status_code, 400)
        self.urlopen.assert_not_called()

    def test_missing_local_html_uses_github_raw_contents(self):
        self.client.force_login(self.owner)
        relative = self.manifest["dates"][0]["runs"][0]["rel_html_path"].removeprefix("archive/")
        (self.archive_dir / relative).unlink()
        self.urlopen.side_effect = None
        self.urlopen.return_value.__enter__.return_value.read.return_value = b"<html>GitHub report</html>"
        with patch("skyview.views._get_toss_token", return_value="test-token"):
            res = self.client.get(self.report_url())
        self.assertContains(res, "GitHub report")
        request = self.urlopen.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/reports/archive/" + relative))
        self.assertEqual(request.get_header("Accept"), "application/vnd.github.raw+json")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    def test_remote_report_errors(self):
        self.client.force_login(self.owner)
        relative = self.manifest["dates"][0]["runs"][0]["rel_html_path"].removeprefix("archive/")
        (self.archive_dir / relative).unlink()
        for code, expected in ((404, 404), (403, 502), (500, 502)):
            with self.subTest(code=code):
                self.urlopen.side_effect = urllib.error.HTTPError("url", code, "secret details", None, None)
                res = self.client.get(self.report_url())
                self.assertEqual(res.status_code, expected)
                self.assertNotContains(res, "secret details", status_code=expected)
        self.urlopen.side_effect = urllib.error.URLError("secret details")
        self.assertEqual(self.client.get(self.report_url()).status_code, 502)

    def test_manifest_error_is_displayed_and_apis_fail_closed(self):
        (self.archive_dir / "manifest.json").write_text("not JSON", encoding="utf-8")
        self.client.force_login(self.owner)
        res = self.client.get(reverse("toss_reports"))
        self.assertContains(res, "보관 목록 형식이 올바르지 않습니다")
        self.assertNotContains(res, 'id="report-frame"')
        self.assertEqual(self.client.get(reverse("toss_reports_api_list")).status_code, 502)
        self.assertEqual(self.client.get(self.report_url()).status_code, 502)

    def test_logout_requires_csrf_and_clears_session(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)
        self.client.get(reverse("toss_reports"))
        logout_url = reverse("admin:logout") + "?next=/"
        self.assertEqual(self.client.post(logout_url).status_code, 403)
        token = self.client.cookies["csrftoken"].value
        self.assertIn(self.client.post(logout_url, {"csrfmiddlewaretoken": token}).status_code, (200, 302))
        self.assert_forbidden()

    def test_navigation_links_for_anonymous_and_owner(self):
        res = self.client.get(reverse("about"))
        self.assertContains(res, 'href="/admin/login/?next=/toss-reports/"')
        self.assertContains(res, 'data-tooltip="Login (Email)"')
        self.client.force_login(self.owner)
        res = self.client.get(reverse("about"))
        self.assertContains(res, 'href="/toss-reports/" data-tooltip="Toss Premarket"')


class TestTossArchiveHelpers(SimpleTestCase):
    def test_toss_token_precedence_and_shared_fallback(self):
        with patch.dict(os.environ, {"TOSS_AGENT_GITHUB_TOKEN": " toss-token ", "EMAIL_AGENT_GITHUB_TOKEN": "email-token"}, clear=True):
            self.assertEqual(_get_toss_token(), "toss-token")
            del os.environ["TOSS_AGENT_GITHUB_TOKEN"]
            self.assertEqual(_get_toss_token(), "email-token")

    def test_local_override_requires_manifest_and_needs_no_token(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"TOSS_REPORTS_LOCAL_PATH": folder}, clear=True):
            self.assertIsNone(_get_toss_local_archive_dir())
            manifest = {"date_list": ["2026-09-25"], "dates": []}
            (Path(folder) / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8-sig")
            self.assertEqual(_get_toss_local_archive_dir(), Path(folder))
            with patch("skyview.views.urllib.request.urlopen") as network:
                self.assertEqual(_fetch_toss_archive_info(), (manifest, ["2026-09-25"], None))
                network.assert_not_called()

    @patch("skyview.views._get_toss_local_archive_dir", return_value=None)
    @patch("skyview.views.urllib.request.urlopen")
    def test_github_manifest_raw_fetch_and_missing_token(self, network, local):
        manifest = {"date_list": ["2026-09-25"], "dates": []}
        network.return_value.__enter__.return_value.read.return_value = json.dumps(manifest).encode()
        with patch.dict(os.environ, {"TOSS_AGENT_GITHUB_TOKEN": "test-token"}, clear=True):
            self.assertEqual(_fetch_toss_archive_info(), (manifest, ["2026-09-25"], None))
        request = network.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.github.com/repos/tonykks/Toss_Invest_Agent/contents/premarket/github/reports/archive/manifest.json")
        self.assertEqual(request.get_header("Accept"), "application/vnd.github.raw+json")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
        network.reset_mock()
        with patch.dict(os.environ, {}, clear=True):
            manifest, dates, error = _fetch_toss_archive_info()
        self.assertEqual((manifest, dates), ({}, []))
        self.assertIn("TOSS_AGENT_GITHUB_TOKEN", error)
        network.assert_not_called()

    @patch("skyview.views._get_toss_local_archive_dir", return_value=None)
    @patch("skyview.views._get_toss_token", return_value="test-token")
    @patch("skyview.views.urllib.request.urlopen")
    def test_github_manifest_errors(self, network, token, local):
        for exc, message in (
            (urllib.error.HTTPError("url", 403, "secret", None, None), "인증/권한 오류"),
            (urllib.error.HTTPError("url", 500, "secret", None, None), "HTTP 오류"),
            (urllib.error.URLError("secret"), "불러오지 못했습니다"),
        ):
            network.side_effect = exc
            manifest, dates, error = _fetch_toss_archive_info()
            self.assertEqual((manifest, dates), ({}, []))
            self.assertIn(message, error)
            self.assertNotIn("secret", error)
        network.side_effect = None
        for invalid in ([], {"date_list": "invalid"}, {"dates": [None]}, {"dates": [{"date": "2026-09-25", "runs": [None]}]}):
            network.return_value.__enter__.return_value.read.return_value = json.dumps(invalid).encode()
            self.assertIn("형식이 올바르지 않습니다", _fetch_toss_archive_info()[2])
