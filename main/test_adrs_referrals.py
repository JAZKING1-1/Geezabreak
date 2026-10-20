from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Referral


class ADRSReferralTests(TestCase):
    def referral_data(self, **overrides):
        data = {
            "referrer_name": "Example ADRS Worker",
            "referrer_email": "worker@example.com",
            "primary_carer_name": "Example Parent",
            "primary_carer_contact_number": "01415550123",
            "address_line1": "1 Example Street",
            "city": "Glasgow",
            "postcode": "G31 4ST",
            "hscp_locality": "NE",
            "ward": "9",
            "srv_adrs": "on",
            "consent_privacy": "on",
            "children-TOTAL_FORMS": "0",
            "children-INITIAL_FORMS": "0",
            "children-MIN_NUM_FORMS": "0",
            "children-MAX_NUM_FORMS": "1000",
        }
        data.update(overrides)
        return data

    def test_adrs_link_preselects_service_without_changing_generic_form(self):
        url = reverse("main:referral")
        response = self.client.get(url, {"service": "adrs"})
        self.assertTrue(response.context["form"]["srv_adrs"].value())
        self.assertContains(response, "This service accepts referrals from an ADRS worker.")
        for query in ({}, {"service": "unknown"}):
            response = self.client.get(url, query)
            self.assertFalse(response.context["form"]["srv_adrs"].value())
        self.assertEqual(Referral.objects.count(), 0)

    @patch("main.views.send_form_email", return_value=True)
    @patch("builtins.print")
    def test_adrs_only_submission_is_saved_and_included_in_email(self, _print, send):
        response = self.client.post(reverse("main:referral"), self.referral_data())
        self.assertRedirects(response, reverse("main:referral_thanks"))
        referral = Referral.objects.get()
        self.assertTrue(referral.srv_adrs)
        self.assertFalse(referral.srv_respite_sitting)
        send.assert_called_once()
        self.assertIn("Services Requested: ADRS Respite Sitting", send.call_args.args[1])
        self.assertIn("ADRS Respite Sitting", send.call_args.kwargs["html_body"])

    @patch("main.views.send_form_email", return_value=True)
    @patch("builtins.print")
    def test_review_flow_retains_adrs_choice_through_confirmation(self, _print, send):
        response = self.client.post(
            reverse("main:referral"), self.referral_data(action="review")
        )
        self.assertRedirects(response, reverse("main:referral_review"))
        self.assertEqual(Referral.objects.count(), 0)
        send.assert_not_called()
        response = self.client.get(reverse("main:referral_review"))
        self.assertContains(response, "ADRS Respite Sitting")
        response = self.client.post(reverse("main:referral_review"))
        self.assertRedirects(response, reverse("main:referral_thanks"))
        self.assertTrue(Referral.objects.get().srv_adrs)
        send.assert_called_once()
        self.assertIn("Services Requested: ADRS Respite Sitting", send.call_args.args[1])

    @patch("main.views.send_form_email", return_value=True)
    @patch("builtins.print")
    def test_query_does_not_override_staffs_submitted_service_choice(self, _print, send):
        data = self.referral_data(srv_family_support="on")
        data.pop("srv_adrs")
        response = self.client.post(reverse("main:referral") + "?service=adrs", data)
        self.assertRedirects(response, reverse("main:referral_thanks"))
        referral = Referral.objects.get()
        self.assertFalse(referral.srv_adrs)
        self.assertTrue(referral.srv_family_support)
        self.assertIn("Services Requested: Family Support", send.call_args.args[1])

    @patch("main.views.send_form_email")
    @patch("builtins.print")
    def test_adrs_link_does_not_allow_submission_with_no_service(self, _print, send):
        data = self.referral_data()
        data.pop("srv_adrs")
        response = self.client.post(reverse("main:referral") + "?service=adrs", data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please select at least one service requested.")
        self.assertFalse(response.context["form"]["srv_adrs"].value())
        self.assertEqual(Referral.objects.count(), 0)
        send.assert_not_called()


class ServiceReferralLinkTests(TestCase):
    def test_service_pages_use_the_correct_referral_destinations(self):
        response = self.client.get(reverse("main:services"))
        self.assertContains(response, 'href="/referral/?service=adrs"', count=1)
        self.assertContains(response, "For ADRS workers.")
        response = self.client.get(reverse("main:brighter_beginnings"))
        self.assertContains(response, 'href="https://form.jotform.com/253312026680348"', count=2)
        self.assertContains(response, 'href="https://www.facebook.com/geezabreak92/"')
        self.assertContains(response, "Call 0141 573 2900")

    def test_existing_service_addresses_redirect_to_services_sections(self):
        for route, section in (
            ("main:adrs_respite_sitting", "adrs-respite-sitting"),
            ("main:family_support_groups", "family-support-group-work"),
        ):
            with self.subTest(route=route):
                self.assertRedirects(
                    self.client.get(reverse(route)),
                    reverse("main:services") + "#" + section,
                )
