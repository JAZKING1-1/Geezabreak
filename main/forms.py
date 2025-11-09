import re
from django import forms
from django.forms import inlineformset_factory
from .models import Referral, ReferralChild, Criterion, GLASGOW_WARDS, ETHNICITY_CHOICES, REFERRAL_REASON_CHOICES

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

    # Override consent_privacy to make it required
    consent_privacy = forms.BooleanField(
        required=True,
        label="I agree to Geeza Break's privacy notice."
    )
    consent_media = forms.BooleanField(
        required=False,
        label="I consent to photos being taken and used for Geeza Break marketing."
    )

    class Meta:
        model = Referral
        fields = [
            "referrer_agency","referrer_name","referrer_email","referrer_phone","preferred_contact_times",
            "primary_carer_name","primary_carer_contact_number","primary_carer_dob","ethnicity",
            "address_line1","address_line2","city","postcode","referral_reason",
            "interpreter_required","preferred_language",
            "joint_visit_required",
            "is_rereferral","last_support_when",
            "srv_family_support","srv_respite_sitting","srv_respite_care","srv_geezachance","srv_kinship_care",
            "reason",
            "hscp_locality","ward","neighbourhood",
            # new criteria fields
            "criteria","criteria_other",
        ]
        widgets = {
            "referrer_email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "referrer_phone": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "Optional"}),
            "preferred_contact_times": forms.TextInput(attrs={"placeholder": "e.g., Weekdays 10–2"}),
            "primary_carer_contact_number": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "e.g., 0141 555 1234"}),
            "primary_carer_dob": forms.DateInput(attrs={"type": "date"}),
            "ethnicity": forms.Select(attrs={"class": "form-select"}),
            "referral_reason": forms.Select(attrs={"class": "form-select"}),
            "address_line1": forms.TextInput(attrs={"autocomplete": "address-line1"}),
            "address_line2": forms.TextInput(attrs={"autocomplete": "address-line2"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "postcode": forms.TextInput(attrs={"autocomplete": "postal-code", "placeholder": "G31 4ST"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }

    # --- Dynamic Ward Restriction (server-side) ---
    RESTRICT_TRIGGER_FIELDS = [
        "srv_family_support", "srv_respite_sitting", "srv_respite_care"
    ]
    RESTRICTED_WARD_IDS = {9, 17, 19, 20, 21, 22, 18}  # Calton, Springburn/Robroyston, Shettleston, Baillieston, North East, Dennistoun, East Centre

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default city if not provided
        if not self.data and not self.initial.get('city'):
            self.initial['city'] = 'Glasgow'
            
        # Add placeholder for ethnicity and referral reason dropdowns
        self.fields['ethnicity'].empty_label = "Select ethnicity (optional)"
        self.fields['referral_reason'].empty_label = "Select reason for referral"
        
        # If bound and any trigger service selected then shrink ward choices
        if self.is_bound:
            data = self.data
            trigger_on = any(self._coerce_bool(data.get(f)) for f in self.RESTRICT_TRIGGER_FIELDS)
            if trigger_on:
                # Filter GLASGOW_WARDS preserving label order in desired display order
                desired_order = [9, 17, 19, 20, 21, 22, 18]
                ward_map = {vid: label for vid, label in GLASGOW_WARDS if vid in self.RESTRICTED_WARD_IDS}
                restricted_choices = [(vid, ward_map[vid]) for vid in desired_order if vid in ward_map]
                self.fields['ward'].choices = restricted_choices
                self.fields['ward'].help_text = (self.fields['ward'].help_text or '') + " (Filtered for selected service(s))"

    def _coerce_bool(self, v):
        return str(v).lower() in {"1","true","on","yes"}

    def clean_postcode(self):
        pc = (self.cleaned_data.get("postcode") or "").strip().upper()
        if not UK_POSTCODE_RE.match(pc):
            raise forms.ValidationError("Please enter a valid UK postcode (e.g. G31 4ST).")
        return pc

    def clean_primary_carer_contact_number(self):
        contact_number = self.cleaned_data.get("primary_carer_contact_number")
        if not contact_number or not contact_number.strip():
            raise forms.ValidationError("Contact number is required.")
        
        # Basic UK phone number validation
        cleaned_number = ''.join(filter(str.isdigit, contact_number))
        if len(cleaned_number) < 10 or len(cleaned_number) > 11:
            raise forms.ValidationError("Please enter a valid UK phone number.")
        
        return contact_number.strip()

    def clean(self):
        cleaned = super().clean()
        print(f"DEBUG: Form clean() called with cleaned_data keys: {list(cleaned.keys())}")
        
        services = [
            cleaned.get("srv_family_support"),
            cleaned.get("srv_respite_sitting"),
            cleaned.get("srv_respite_care"),
            cleaned.get("srv_geezachance"),
            cleaned.get("srv_kinship_care"),
        ]
        print(f"DEBUG: Services selected: {services}")
        if not any(services):
            print("DEBUG: No services selected - raising validation error")
            raise forms.ValidationError("Please select at least one service requested.")

        if cleaned.get("interpreter_required") and not (cleaned.get("preferred_language") or "").strip():
            print("DEBUG: Interpreter required but no preferred language - adding error")
            self.add_error("preferred_language", "Please tell us the preferred language.")

        if cleaned.get("is_rereferral") and not (cleaned.get("last_support_when") or "").strip():
            print("DEBUG: Is rereferral but no last support when - adding error")
            self.add_error("last_support_when", "Please tell us approximately when we last supported this family.")

        # Enforce ward restriction regardless of client-side JS
        trigger_on = any(cleaned.get(f) for f in self.RESTRICT_TRIGGER_FIELDS)
        ward_val = cleaned.get('ward')
        if trigger_on and ward_val and ward_val not in self.RESTRICTED_WARD_IDS:
            print(f"DEBUG: Ward restriction violated - ward {ward_val} not in restricted wards")
            self.add_error('ward', "Selected ward is not available for chosen service(s).")
        print(f"DEBUG: Form clean() completed, errors: {self.errors}")
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        relationship_field = self.fields["relationship"]
        # Ensure the dropdown prompts users to select an option explicitly
        choices = [(value, label) for value, label in relationship_field.choices if value]
        relationship_field.choices = [("", "— Select relationship —")] + choices
        relationship_field.widget.attrs.update({
            "required": "required",
            "aria-required": "true",
            "class": (relationship_field.widget.attrs.get("class", "") + " required-field").strip(),
        })


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
        label="I’m interested in",
        required=True
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Convert comma-separated string back to list for form display
            if self.instance.roles:
                self.initial['roles'] = self.instance.roles.split(',')

    def clean_roles(self):
        """Convert list of roles to comma-separated string for model storage"""
        roles = self.cleaned_data.get('roles')
        if roles:
            return ','.join(roles)
        return ''
