from django.db import models

# Existing models

class Feedback(models.Model):
    SERVICE_CHOICES = [
        ('respite', 'Respite Care'),
        ('wellbeing', 'Wellbeing Support'),
        ('parenting', 'Parenting Workshops'),
        ('kinship', 'Kinship Care'),
        ('other', 'Other')
    ]
    
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    service_used = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.name} - {self.service_used}"


# --- Geography choices for Referral ---
HSCP_LOCALITIES = [
    ("NE", "North East"),
    ("NW", "North West"),
    ("S",  "South"),
]

GLASGOW_WARDS = [
    (1, "Linn"), (2, "Newlands/Auldburn"), (3, "Greater Pollok"), (4, "Cardonald"),
    (5, "Govan"), (6, "Pollokshields"), (7, "Langside"), (8, "Southside Central"),
    (9, "Calton"), (10, "Anderston/City/Yorkhill"), (11, "Hillhead"), (12, "Victoria Park"),
    (13, "Garscadden/Scotstounhill"), (14, "Drumchapel/Anniesland"), (15, "Maryhill"),
    (16, "Canal"), (17, "Springburn/Robroyston"), (18, "East Centre"), (19, "Shettleston"),
    (20, "Baillieston"), (21, "North East"), (22, "Dennistoun"), (23, "Partick East/Kelvindale"),
]


class Referral(models.Model):
    # Referrer (agency)
    referrer_agency = models.CharField(max_length=120, blank=True)
    referrer_name = models.CharField(max_length=120)
    referrer_email = models.EmailField()
    referrer_phone = models.CharField(max_length=40, blank=True)
    preferred_contact_times = models.CharField(max_length=120, blank=True)

    # Family / person referred
    primary_carer_name = models.CharField("Parent/Carer name", max_length=120)
    address_line1 = models.CharField(max_length=160)
    address_line2 = models.CharField(max_length=160, blank=True)
    city = models.CharField(max_length=80, default="Glasgow")
    postcode = models.CharField(max_length=10)

    # Language / interpreter
    interpreter_required = models.BooleanField(default=False)
    preferred_language = models.CharField(max_length=80, blank=True)
    joint_visit_required = models.BooleanField(
        default=False,
        help_text="Tick if a joint visit with another professional is required."
    )

    # Re-referral
    is_rereferral = models.BooleanField(default=False)
    last_support_when = models.CharField(
        max_length=20,
        blank=True,
        help_text="Month/Year is fine (e.g. 05/2023)"
    )

    # Services (simple booleans for now)
    srv_family_support = models.BooleanField(default=False)
    srv_respite_sitting = models.BooleanField(default=False)
    srv_respite_care = models.BooleanField(default=False)
    srv_geezachance = models.BooleanField(default=False)
    srv_kinship_care = models.BooleanField(default=False)

    reason = models.TextField("Brief reason for referral / goals", blank=True)

    # Geography
    hscp_locality = models.CharField("HSCP locality", max_length=2, choices=HSCP_LOCALITIES)
    ward = models.IntegerField(choices=GLASGOW_WARDS)
    neighbourhood = models.CharField(max_length=120, blank=True)

    # Section 3 – criteria (ManyToMany managed list) + optional free text
    # These are added in a later iteration to capture key referral need areas.
    # Criterion objects are editable/orderable in admin without code changes.
    criteria = models.ManyToManyField("Criterion", blank=True, related_name="referrals")
    criteria_other = models.CharField(max_length=240, blank=True)

    # Consent
    consent_privacy = models.BooleanField(
        default=False,
        help_text="I agree to Geeza Break's privacy notice."
    )
    consent_media = models.BooleanField(
        default=False,
        help_text="I consent to photos being taken and used for Geeza Break marketing."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False, help_text="Flag indicating if notification email was sent")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.primary_carer_name} ({self.postcode}) – {self.created_at:%Y-%m-%d}"


class ReferralChild(models.Model):
    REL_CHOICES = [
        ("son", "Son"),
        ("daughter", "Daughter"),
        ("stepchild", "Step-child"),
        ("foster", "Foster child"),
        ("other", "Other"),
    ]

    referral = models.ForeignKey("Referral", related_name="children", on_delete=models.CASCADE)
    full_name = models.CharField("Child name", max_length=120)
    dob = models.DateField("Date of birth")
    relationship = models.CharField(max_length=16, choices=REL_CHOICES)
    has_asn = models.BooleanField("Additional support needs / disability", default=False)
    school_nursery = models.CharField("School/Nursery (optional)", max_length=160, blank=True)

    class Meta:
        ordering = ["dob", "full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.dob:%d/%m/%Y})"


class Criterion(models.Model):
    """Referral criteria items (editable list)."""
    key = models.SlugField(unique=True)
    label = models.CharField(max_length=140)
    help_text = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "label"]

    def __str__(self):
        return self.label


class TeamMember(models.Model):
    """Team member profiles for the 'Meet Our Team' section"""
    name = models.CharField(max_length=100)
    role_title = models.CharField(max_length=100)
    joined_date = models.CharField(max_length=100, help_text="When you came on board as a trustee")
    reason_for_joining = models.TextField(help_text="Why you got involved in supporting Geeza Break")
    role_description = models.TextField(help_text="What your role entails")
    favorite_aspect = models.TextField(help_text="What you like best about being a Geeza Break Trustee")
    fun_fact = models.TextField(help_text="Fun fact/what you like to do 'for a break' when you have the chance")
    image = models.ImageField(upload_to='team_members/', blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, help_text="Path to image in static folder (e.g. 'images/staff/1t.jpg')")
    order = models.PositiveIntegerField(default=0, help_text="Display order on the page")
    
    class Meta:
        ordering = ["order", "name"]
        
    def __str__(self):
        return f"{self.name} - {self.role_title}"
