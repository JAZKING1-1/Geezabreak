from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from .forms import ReferralForm


class ReferralServiceAvailabilityTests(TestCase):
    def test_overnight_respite_is_not_available_on_new_referral_form(self):
        form = ReferralForm()

        self.assertNotIn("srv_respite_care", form.fields)
        self.assertIn("srv_respite_sitting", form.fields)
        self.assertNotIn(
            "respite_care_required",
            dict(form.fields["referral_reason"].choices),
        )

    @patch("builtins.print")
    def test_referral_page_does_not_offer_overnight_respite(self, _mock_print):
        response = self.client.get(reverse("main:referral"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="srv_respite_care"')
        self.assertNotContains(response, "Overnight respite in an approved carer's home")
        self.assertNotContains(response, "Respite Care Required")
        self.assertContains(response, 'name="srv_respite_sitting"')


class BrighterBeginningsPageTests(TestCase):
    def test_dedicated_page_contains_flyer_and_approved_parent_quotes(self):
        response = self.client.get(reverse("main:brighter_beginnings"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Brighter Beginnings")
        self.assertContains(response, "images/brighter-beginnings/flyer.jpg", count=3)
        for parent_name in ("Tracey", "Siobhan", "Heather", "Robyn", "Stacey", "Ramat"):
            self.assertContains(response, parent_name)
