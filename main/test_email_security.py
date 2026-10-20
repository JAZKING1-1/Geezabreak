from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Referral
from .utils.mailer import send_form_email


class EmailAdministrationSecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_user(
            username="release-admin", is_staff=True
        )
        cls.member = get_user_model().objects.create_user(username="release-member")
        cls.referral = Referral.objects.create(
            referrer_name="Example worker",
            referrer_email="worker@example.invalid",
            primary_carer_name="Example parent",
            ward=9,
            srv_adrs=True,
        )

    def protected_urls(self):
        return [
            reverse("main:email_status"),
            reverse("main:resend_email", args=[self.referral.pk]),
            reverse("main:mailjet_debug"),
            reverse("main:test_email"),
            reverse("main:test_referral_email"),
        ]

    @patch("main.views.send_form_email")
    def test_anonymous_visitors_cannot_read_records_or_send_diagnostic_mail(self, send):
        for url in self.protected_urls():
            for method in ("get", "post"):
                with self.subTest(url=url, method=method):
                    response = getattr(self.client, method)(url)
                    self.assertEqual(response.status_code, 302)
                    self.assertTrue(response.url.startswith("/admin/login/?next="))
                    self.assertNotContains(response, "Example parent", status_code=302)
        send.assert_not_called()

    @patch("main.views.send_form_email")
    def test_non_admin_accounts_cannot_access_email_administration(self, send):
        self.client.force_login(self.member)
        for url in self.protected_urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.post(url).status_code, 302)
        send.assert_not_called()

    @patch("main.views.send_form_email")
    def test_admin_get_requests_cannot_trigger_email(self, send):
        self.client.force_login(self.admin)
        for url in self.protected_urls()[1:]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 405)
        send.assert_not_called()

    @patch("main.views.send_form_email", return_value=True)
    def test_admin_resend_requires_csrf_and_dashboard_supplies_token(self, send):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        url = reverse("main:resend_email", args=[self.referral.pk])
        self.assertEqual(client.post(url).status_code, 403)
        send.assert_not_called()
        dashboard = client.get(reverse("main:email_status"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertIn("csrftoken", dashboard.cookies)
        response = client.post(url, HTTP_X_CSRFTOKEN=dashboard.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.referral.refresh_from_db()
        self.assertTrue(self.referral.email_sent)
        send.assert_called_once()
        self.assertIn("ADRS Respite Sitting", send.call_args.kwargs["html_body"])

    @patch("main.views.send_form_email")
    def test_all_diagnostic_posts_require_csrf(self, send):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        for url in self.protected_urls()[1:]:
            with self.subTest(url=url):
                self.assertEqual(client.post(url).status_code, 403)
        send.assert_not_called()


class MailjetConfigurationTests(TestCase):
    @override_settings(MAILJET_API_KEY="fictional-key", MAILJET_API_SECRET="fictional-secret")
    @patch("main.utils.mailer.Client")
    def test_mailer_uses_configured_keys_and_preserves_recipients_and_reply_to(self, client):
        client.return_value.send.create.return_value.status_code = 200
        result = send_form_email(
            "Example subject", "Example body", ["office@example.invalid"],
            html_body="<p>Example body</p>", reply_to_email="worker@example.invalid"
        )
        self.assertTrue(result)
        client.assert_called_once_with(
            auth=("fictional-key", "fictional-secret"), version="v3.1"
        )
        message = client.return_value.send.create.call_args.kwargs["data"]["Messages"][0]
        self.assertEqual(
            {entry["Email"] for entry in message["To"]},
            {"office@example.invalid", "devansh.sharma@geezabreak.org.uk"},
        )
        self.assertEqual(message["ReplyTo"]["Email"], "worker@example.invalid")
