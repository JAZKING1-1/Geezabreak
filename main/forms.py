import re
from django import forms
from django.forms import inlineformset_factory
from .models import Referral, ReferralChild, Criterion

UK_POSTCODE_RE = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}$", re.I)

class ReferralForm(forms.ModelForm):
    # Section 3 criteria dynamic checklist
    criteria = forms.ModelMultipleChoiceField(
        queryset=Criterion.objects.filter(active=True).order_by("order", "label"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    criteria_other = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Optional — if not listed"})
    )

    class Meta:
        model = Referral
        fields = [
            "referrer_agency","referrer_name","referrer_email","referrer_phone","preferred_contact_times",
            "primary_carer_name","address_line1","address_line2","city","postcode",
            "interpreter_required","preferred_language",
            "is_rereferral","last_support_when",
            "srv_family_support","srv_respite_sitting","srv_respite_care","srv_geezachance","srv_kinship_care",
            "reason",
            "hscp_locality","ward","neighbourhood",
            # new criteria fields
            "criteria","criteria_other",
            "consent_privacy","consent_media",
        ]
        widgets = {
            "referrer_email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "referrer_phone": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "Optional"}),
            "preferred_contact_times": forms.TextInput(attrs={"placeholder": "e.g., Weekdays 10–2"}),
            "address_line1": forms.TextInput(attrs={"autocomplete": "address-line1"}),
            "address_line2": forms.TextInput(attrs={"autocomplete": "address-line2"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "postcode": forms.TextInput(attrs={"autocomplete": "postal-code", "placeholder": "G31 4ST"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_postcode(self):
        pc = (self.cleaned_data.get("postcode") or "").strip().upper()
        if not UK_POSTCODE_RE.match(pc):
            raise forms.ValidationError("Please enter a valid UK postcode (e.g. G31 4ST).")
        return pc

    def clean(self):
        cleaned = super().clean()
        services = [
            cleaned.get("srv_family_support"),
            cleaned.get("srv_respite_sitting"),
            cleaned.get("srv_respite_care"),
            cleaned.get("srv_geezachance"),
            cleaned.get("srv_kinship_care"),
        ]
        if not any(services):
            raise forms.ValidationError("Please select at least one service requested.")

        if cleaned.get("interpreter_required") and not (cleaned.get("preferred_language") or "").strip():
            self.add_error("preferred_language", "Please tell us the preferred language.")

        if cleaned.get("is_rereferral") and not (cleaned.get("last_support_when") or "").strip():
            self.add_error("last_support_when", "Please tell us approximately when we last supported this family.")

        if not cleaned.get("consent_privacy"):
            self.add_error("consent_privacy", "You must accept the privacy notice to submit.")
        return cleaned


class ReferralChildForm(forms.ModelForm):
    dob = forms.DateField(
        input_formats=["%d/%m/%Y", "%Y-%m-%d"],
        widget=forms.DateInput(attrs={"placeholder": "DD/MM/YYYY"})
    )

    class Meta:
        model = ReferralChild
        fields = ["full_name", "dob", "relationship", "has_asn", "school_nursery"]
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "school_nursery": forms.TextInput(attrs={"placeholder": "Optional"}),
        }


ReferralChildFormSet = inlineformset_factory(
    Referral, ReferralChild,
    form=ReferralChildForm,
    fields=["full_name", "dob", "relationship", "has_asn", "school_nursery"],
    extra=1, can_delete=True
)


from .models import VolunteerInterest, ROLE_CHOICES

class VolunteerInterestForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="I’m interested in"
    )
    consent_contact = forms.BooleanField(
        required=True,
        label="I consent to Geeza Break contacting me about volunteering/placements."
    )

    class Meta:
        model = VolunteerInterest
        fields = [
            "full_name", "email", "phone", "roles", "availability",
            "is_student", "course_or_discipline", "message", "consent_contact"
        ]
        widgets = {
            "availability": forms.TextInput(attrs={"placeholder": "e.g., Weekday mornings / Evenings / Weekends"}),
            "course_or_discipline": forms.TextInput(attrs={"placeholder": "e.g., Social Work (Hons), Year 3"}),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us anything helpful (experience, start date, etc.)"}),
        }
        labels = {
            "full_name": "Full name",
            "is_student": "I’m a student",
            "course_or_discipline": "Course / Discipline",
        }
