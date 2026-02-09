from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Feedback, Referral, Criterion, VolunteerInterest
from .forms import ReferralForm, ReferralChildFormSet
from .fun_games import GAMES
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.db import transaction
from django.conf import settings
from django.views import View
from .models import Comment
import logging
import hashlib
import os
from django.templatetags.static import static
from django.contrib import messages
from django.views.decorators.http import require_GET
from .utils.mailer import send_form_email


def home(request):
    logger = logging.getLogger(__name__)
    logger.info("Home view called")

    if not request.session.get('visited_home'):
        request.session['visited_home'] = True
        request.session.save()

    try:
        comments = Comment.objects.filter(approved=True).order_by('-created_at')[:10]
        logger.info("Loaded %s approved comments for home page", len(comments))
    except Exception as exc:  # pragma: no cover – defensive logging
        logger.exception("Error retrieving approved comments: %s", exc)
        comments = []

    available = [
        {
            'src': static('images/i3.jpg'),
            'caption': 'Creative arts session with volunteers.',
            'alt': 'Volunteer leading an arts activity with young people',
        },
        {
            'src': static('images/i5.jpg'),
            'caption': 'Supporting families since 1992.',
            'alt': 'Geeza Break team at a community gathering',
        },
        {
            'src': static('images/i7.jpg'),
            'caption': 'Every visit builds confidence and joy.',
            'alt': 'Child holding craft materials and smiling',
        },
        {
            'src': static('images/2.jpg'),
            'caption': 'Respite time lets families recharge.',
            'alt': 'Family walking together in the park',
        },
        {
            'src': static('images/3.jpg'),
            'caption': 'Volunteers bring enthusiasm and care.',
            'alt': 'Geeza Break volunteer high-fiving a child',
        },
        {
            'src': static('images/4.jpg'),
            'caption': 'Community events connect kinship carers.',
            'alt': 'Group of carers meeting at a local centre',
        },
    ]

    def make_list(count: int, offset: int = 0):
        if not available:
            return []
        total = len(available)
        items = []
        for idx in range(count):
            original = available[(idx + offset) % total]
            items.append({
                'src': original['src'],
                'caption': original.get('caption'),
                'alt': original.get('alt'),
            })
        return items

    impact_top = make_list(10)
    impact_bottom = make_list(10, offset=5)

    return render(
        request,
        'main/home.html',
        {
            'comments': comments,
            'impact_images': impact_top,
            'impact_images_bottom': impact_bottom,
        },
    )

def landing(request):
    logger = logging.getLogger(__name__)
    logger.info("Landing view called")
    try:
        return render(request, 'main/landing.html')
    except Exception as e:
        logger.error(f"Error in landing view: {e}")
        raise

def about(request):
    from .models import TeamMember
    from datetime import date
    import re

    today = date.today()

    month_map = {m.lower(): i for i, m in enumerate([
        '', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'
    ])}

    def parse_joined(s: str):
        if not s:
            return date(today.year, 1, 1)
        # Try patterns like '7 October 2024', 'October 2024', 'Jan 2024', '2020', 'January 2024'
        # Normalize double spaces
        s_norm = re.sub(r"\s+", " ", s.strip())
        # Full day month year
        m = re.match(r"^(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})$", s_norm)
        if m:
            day = int(m.group('day'))
            month = month_map.get(m.group('month').lower(), 1)
            year = int(m.group('year'))
            return date(year, month, min(day, 28))
        # Month year
        m = re.match(r"^(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})$", s_norm)
        if m:
            month = month_map.get(m.group('month').lower(), 1)
            year = int(m.group('year'))
            return date(year, month, 1)
        # Year only
        m = re.search(r"(\d{4})", s_norm)
        if m:
            year = int(m.group(1))
            return date(year, 1, 1)
        return date(today.year, 1, 1)

    def tenure_string(join_dt: date):
        # Compute years with 1 decimal; if under 1 year show months
        delta_days = (today - join_dt).days
        if delta_days < 30:
            return "Joined recently"
        years = delta_days / 365.25
        if years < 1:
            months = int(delta_days / 30.44)
            return f"{months} months since {join_dt.year}"
        # 1 decimal
        years_fmt = f"{years:.1f}".rstrip('0').rstrip('.')
        return f"{years_fmt} years since {join_dt.year}"

    raw_members = list(TeamMember.objects.all())
    enriched = []
    for m in raw_members:
        jd = parse_joined(m.joined_date)
        # attach helper attrs (no leading underscore so Django template allows access)
        m.join_date_parsed = jd
        m.tenure_display = tenure_string(jd)
        m.display_name = 'Nancy Ross' if m.name == 'Jane Wilson' else m.name
        # Explicit overrides as requested
        if m.display_name == 'Nancy Ross':
            m.tenure_display = 'January 2024'
        elif m.display_name == 'Elaine Mitchell':
            m.tenure_display = '6 years since 2020'
        elif m.display_name == 'Mark Mulholland':
            m.tenure_display = '15 years'
        enriched.append(m)

    enriched.sort(key=lambda x: (x.join_date_parsed, x.display_name.lower()))

    return render(request, 'main/about.html', {
        'team_members': enriched,
    })

def community_flat(request):
    return render(request, "main/community_flat.html")


def healthz(request):
    return JsonResponse({
        "ok": True,
        "host": request.get_host(),
        "allowed_hosts": settings.ALLOWED_HOSTS,
    })


def services(request):
    return render(request, 'main/services.html')


def extra_support(request):
    return render(request, "main/extra_support.html")


def get_help(request):
    return render(request, 'main/get_help.html')


def cookies(request):
    return render(request, "main/cookies.html")


def sitemap(request):
    return render(request, "main/sitemap.html")


def submit_feedback(request):
    print("Feedback view called")
    if request.method == 'POST':
        if request.POST.get("company_website"):
            return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'} )
        try:
            feedback = Feedback(
                name=request.POST.get('name'),
                contact_number=request.POST.get('contact_number'),
                email=request.POST.get('email'),
                service_used=request.POST.get('service_used'),
                message=request.POST.get('message')
            )
            feedback.save()

            formatted_body = (
                "New Feedback Form Submission\n\n"
                f"Name: {feedback.name}\n"
                f"Email: {feedback.email}\n"
                f"Phone: {feedback.contact_number}\n"
                f"Service Used: {feedback.get_service_used_display()}\n"
                f"Message: {feedback.message}"
            )
            send_form_email(
                "Feedback Form Submission",
                formatted_body,
                settings.GENERAL_RECIPIENTS
            )

            return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def submit_comment(request):
    if request.method == 'POST':
        name = request.POST.get('name') or 'Anonymous'
        message = request.POST.get('message')
        if message:
            comment = Comment.objects.create(name=name, message=message)
            return JsonResponse({'status': 'success', 'name': comment.name, 'message': comment.message, 'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')})
        return JsonResponse({'status': 'error', 'message': 'Message is required.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

def referral(request):
    # Legacy simple template kept for backward compatibility; now use class-based view
    return render(request, 'main/referral.html')


def build_referral_email_content(referral, base_data=None, children=None):
    """Return subject, text, and HTML content for a referral notification."""

    def format_value(value):
        if value is None:
            return ''
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        if isinstance(value, (list, tuple, set)):
            return ', '.join(str(item) for item in value)
        if hasattr(value, 'all') and callable(value.all):
            return ', '.join(str(item) for item in value.all())
        return str(value)

    data = dict(base_data or {})

    if 'criteria' in data:
        criteria_value = data['criteria']
        if isinstance(criteria_value, (list, tuple, set)):
            data['criteria'] = [str(item) for item in criteria_value]
        elif hasattr(criteria_value, 'all') and callable(criteria_value.all):
            data['criteria'] = [str(item) for item in criteria_value.all()]
        elif criteria_value:
            data['criteria'] = [str(criteria_value)]

    if not data:
        field_order = [
            'referrer_name',
            'referrer_email',
            'referrer_phone',
            'primary_carer_name',
            'primary_carer_email',
            'primary_carer_phone',
            'address_line1',
            'address_line2',
            'city',
            'postcode',
            'reason',
            'support_history',
            'joint_visit_required',
            'criteria_other',
        ]
        for field in field_order:
            value = getattr(referral, field, None)
            if value not in (None, '', []):
                data[field] = value
        if hasattr(referral, 'criteria'):
            data['criteria'] = [str(item) for item in referral.criteria.all()]

    text_lines = ["New referral submission", ""]
    html_lines = ["<h2>New Referral Submission</h2>", "<ul>"]

    for field, value in data.items():
        if field in ['children']:
            continue
        label = field.replace('_', ' ').title()
        rendered = format_value(value)
        text_lines.append(f"{label}: {rendered}")
        html_lines.append(f"<li><strong>{label}:</strong> {rendered}</li>")
    html_lines.append("</ul>")

    if children is None:
        try:
            related = referral.referralchild_set.all()
            children = list(related)
        except Exception:  # pragma: no cover – relation may not exist in tests
            children = []
    else:
        children = list(children)

    if children:
        html_lines.append("<h3>Children</h3>")
        html_lines.append("<ul>")

    child_text_lines = []

    def child_attr(child, attr, default=''):
        if hasattr(child, attr):
            return getattr(child, attr) or default
        if isinstance(child, dict):
            return child.get(attr, default)
        return default

    for index, child in enumerate(children, start=1):
        dob = child_attr(child, 'dob')
        if hasattr(dob, 'isoformat'):
            dob_display = dob.isoformat()
        else:
            dob_display = dob or 'n/a'
        child_summary = (
            f"Child {index}: {child_attr(child, 'full_name', 'Unnamed')} – DOB: {dob_display} – "
            f"Relationship: {child_attr(child, 'relationship', 'n/a')} – "
            f"ASN: {'Yes' if child_attr(child, 'has_asn', False) else 'No'}"
        )
        child_text_lines.append(child_summary)
        html_lines.append(f"<li>{child_summary}</li>")

    if children:
        html_lines.append("</ul>")

    if child_text_lines:
        text_lines.append("")
        text_lines.append("Children:")
        text_lines.extend(child_text_lines)

    subject = "Referral: {} ({})".format(
        getattr(referral, 'primary_carer_name', 'Referral') or 'Referral',
        getattr(referral, 'postcode', '') or 'No postcode provided',
    )

    return subject, "\n".join(text_lines), "\n".join(html_lines)


class ReferralCreateView(CreateView):
    model = Referral
    form_class = ReferralForm
    template_name = 'main/referral_form.html'
    success_url = reverse_lazy('main:referral_thanks')

    def get(self, request, *args, **kwargs):
        print("🚨🚨🚨 REFERRAL FORM GET REQUEST RECEIVED 🚨🚨🚨")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['child_formset'] = ReferralChildFormSet(self.request.POST, prefix='children')
        else:
            ctx['child_formset'] = ReferralChildFormSet(prefix='children')
        return ctx

    def render_invalid(self, form, formset):
        return self.render_to_response(self.get_context_data(form=form, child_formset=formset))

    def post(self, request, *args, **kwargs):
        print("🚨🚨🚨 REFERRAL FORM POST REQUEST RECEIVED 🚨🚨🚨")
        print(f"POST data keys: {list(request.POST.keys())}")
        print(f"Action: {request.POST.get('action', 'NO ACTION')}")
        print("DEBUG: ReferralCreateView.post() called")
        if request.POST.get("company_website"):
            return redirect('main:referral_thanks')
        self.object = None
        form = self.get_form()
        child_formset = ReferralChildFormSet(request.POST, prefix='children')
        action = request.POST.get('action', 'submit')
        print(f"DEBUG: Action = {action}")

        if action == 'review':
            print("DEBUG: Processing review action")
            if form.is_valid() and child_formset.is_valid():
                print("DEBUG: Form and formset are valid for review")
                cd = form.cleaned_data.copy()
                # Make cleaned_data JSON-serializable for session storage
                for key, value in list(cd.items()):
                    if hasattr(value, "isoformat"):
                        cd[key] = value.isoformat()
                crit_ids = [c.id for c in cd.pop('criteria', [])]
                cd['criteria_ids'] = crit_ids
                kids = []
                for f in child_formset.forms:
                    if not f.cleaned_data or f.cleaned_data.get('DELETE'):
                        continue
                    d = f.cleaned_data
                    kids.append({
                        'full_name': d['full_name'],
                        'dob': d['dob'].isoformat(),
                        'relationship': d['relationship'],
                        'has_asn': bool(d['has_asn']),
                        'school_nursery': d.get('school_nursery',''),
                    })
                request.session['referral_draft'] = {'ref': cd, 'children': kids}
                request.session.modified = True
                print("DEBUG: Redirecting to review page")
                return redirect('main:referral_review')
            else:
                print("DEBUG: Form or formset invalid for review")
                print(f"DEBUG: Form errors: {form.errors}")
                print(f"DEBUG: Formset errors: {child_formset.errors}")
                print(f"DEBUG: Formset non_form_errors: {child_formset.non_form_errors()}")
            return self.render_invalid(form, child_formset)

        # direct submit
        print("DEBUG: Processing direct submit")
        print(f"DEBUG: Form is valid: {form.is_valid()}")
        print(f"DEBUG: Formset is valid: {child_formset.is_valid()}")
        print(f"DEBUG: Formset total forms: {child_formset.total_form_count()}")
        print(f"DEBUG: Formset initial forms: {child_formset.initial_form_count()}")
        
        if not form.is_valid():
            print(f"DEBUG: Form errors: {form.errors}")
        if not child_formset.is_valid():
            print(f"DEBUG: Formset errors: {child_formset.errors}")
            print(f"DEBUG: Formset non_form_errors: {child_formset.non_form_errors()}")
            # Debug each form in the formset
            for i, form_errors in enumerate(child_formset.errors):
                if form_errors:
                    print(f"DEBUG: Child form {i} errors: {form_errors}")
            for i, child_form in enumerate(child_formset.forms):
                if child_form.is_bound and not child_form.is_valid():
                    print(f"DEBUG: Child form {i} is invalid, data: {child_form.data}")

        if form.is_valid() and child_formset.is_valid():
            print("DEBUG: Both form and formset are valid, calling _save_and_redirect")
            return self._save_and_redirect(form, child_formset)
        else:
            print("DEBUG: Form or formset invalid, rendering invalid form")
        return self.render_invalid(form, child_formset)

    @transaction.atomic
    def _save_and_redirect(self, form, formset):
        logger = logging.getLogger(__name__)

        self.object = form.save()
        formset.instance = self.object
        saved_children = formset.save()
        print(f"DEBUG: Formset saved, {len(saved_children)} children saved")

        cleaned_data = form.cleaned_data.copy()
        criteria = cleaned_data.get('criteria')
        if criteria is not None:
            cleaned_data['criteria'] = [str(choice) for choice in criteria]

        subject, body_text, html_body = build_referral_email_content(
            self.object,
            base_data=cleaned_data,
            children=saved_children,
        )

        email_sent = send_form_email(
            subject,
            body_text,
            settings.REFERRAL_RECIPIENTS,
            html_body=html_body,
        )

        self.object.email_sent = email_sent
        self.object.save(update_fields=['email_sent'])

        if email_sent:
            logger.info("Referral email notification sent for referral ID %s", self.object.id)
        else:
            logger.error(
                "Mailjet failed to send referral notification for referral ID %s",
                self.object.id,
            )
            messages.error(
                self.request,
                "We saved your referral but the automatic email alert did not send. We'll resend it manually.",
            )

        return redirect(self.get_success_url())

class ReferralReviewView(View):
    template_name = 'main/referral_review.html'

    def get(self, request):
        data = request.session.get('referral_draft')
        if not data:
            return redirect('main:referral')
        ref = data['ref']
        crit_labels = list(Criterion.objects.filter(id__in=ref.get('criteria_ids', [])).values_list('label', flat=True))
        return render(request, self.template_name, { 'ref': ref, 'children': data['children'], 'criteria_labels': crit_labels })

    @transaction.atomic
    def post(self, request):
        print("DEBUG: ReferralReviewView.post called")
        data = request.session.get('referral_draft')
        if not data:
            print("DEBUG: No referral draft in session, redirecting to referral")
            return redirect('main:referral')
        ref = data['ref'].copy()
        crit_ids = ref.pop('criteria_ids', [])
        print(f"DEBUG: Creating referral with data: {ref}")
        # create referral (exclude M2M for now)
        r = Referral.objects.create(**{k:v for k,v in ref.items() if k not in ['criteria','criteria_other']})
        print(f"DEBUG: Referral created with ID: {r.id}")
        if crit_ids:
            r.criteria.set(Criterion.objects.filter(id__in=crit_ids))
            print(f"DEBUG: Set {len(crit_ids)} criteria")
        if ref.get('criteria_other'):
            r.criteria_other = ref['criteria_other']
            r.save(update_fields=['criteria_other'])
            print("DEBUG: Saved criteria_other")
        from .models import ReferralChild
        children_count = 0
        for c in data['children']:
            ReferralChild.objects.create(
                referral=r,
                full_name=c['full_name'],
                dob=c['dob'],
                relationship=c['relationship'],
                has_asn=c['has_asn'],
                school_nursery=c['school_nursery'],
            )
            children_count += 1
        print(f"DEBUG: Created {children_count} children")

        logger = logging.getLogger(__name__)
        subject, body_text, html_body = build_referral_email_content(
            r,
            children=r.referralchild_set.all(),
        )

        email_sent = send_form_email(
            subject,
            body_text,
            settings.REFERRAL_RECIPIENTS,
            html_body=html_body,
        )

        r.email_sent = email_sent
        r.save(update_fields=['email_sent'])

        if email_sent:
            logger.info("Referral email notification sent during review flow for referral ID %s", r.id)
        else:
            logger.error(
                "Mailjet failed to send referral notification during review flow for referral ID %s",
                r.id,
            )
        print("DEBUG: Clearing session and redirecting to thanks page")
        request.session.pop('referral_draft', None)
        return redirect(reverse_lazy('main:referral_thanks'))


class ReferralThanksView(TemplateView):
    template_name = 'main/referral_thanks.html'

def fun_zone(request):
    return render(request, 'main/fun_zone.html', {'games': GAMES})

def email_status(request):
    """Display the status of email notifications for referrals."""

    referrals = Referral.objects.all().order_by('-created_at')[:20]

    context = {
        'referrals': referrals,
        'email_backend': settings.EMAIL_BACKEND,
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'not set'),
        'recipients_referral': getattr(settings, 'REFERRAL_RECIPIENTS', []),
        'recipients_general': getattr(settings, 'GENERAL_RECIPIENTS', []),
    }

    return render(request, 'main/email_status.html', context)


def resend_email(request, referral_id):
    """Resend the email notification for a saved referral."""

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    try:
        referral = Referral.objects.get(id=referral_id)
    except Referral.DoesNotExist:
        return JsonResponse({'success': False, 'message': f"Referral #{referral_id} not found."})

    logger = logging.getLogger(__name__)
    subject, body_text, html_body = build_referral_email_content(referral)
    email_sent = send_form_email(
        subject,
        body_text,
        settings.REFERRAL_RECIPIENTS,
        html_body=html_body,
    )

    referral.email_sent = email_sent
    referral.save(update_fields=['email_sent'])

    if email_sent:
        logger.info("Referral email resent for referral ID %s", referral_id)
        return JsonResponse({
            'success': True,
            'message': f"Email notification for referral #{referral_id} has been resent successfully.",
        })

    logger.error("Mailjet failed when resending referral ID %s", referral_id)
    return JsonResponse({
        'success': False,
        'message': f"Referral #{referral_id} was updated but the email could not be resent. We'll retry manually.",
    })


@require_GET
def mailjet_debug(request):
    key = (settings.MAILJET_API_KEY or "").strip()
    secret = (settings.MAILJET_API_SECRET or "").strip()
    summary = {
        "DJANGO_ENV": os.environ.get("DJANGO_ENV", "<unset>"),
        "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
        "MAILJET_API_KEY_len": len(key),
        "MAILJET_API_SECRET_len": len(secret),
        "MAILJET_API_KEY_sig": hashlib.sha1(key.encode()).hexdigest()[:10] if key else "MISSING",
        "MAILJET_API_SECRET_sig": hashlib.sha1(secret.encode()).hexdigest()[:10] if secret else "MISSING",
        "REFERRAL_RECIPIENTS": settings.REFERRAL_RECIPIENTS,
        "GENERAL_RECIPIENTS": settings.GENERAL_RECIPIENTS,
    }
    ok = send_form_email(
        "Mailjet Debug Ping (local)",
        f"Runtime debug: {summary}",
        ["devansh.sharma@geezabreak.org.uk"],
    )
    summary["send_ok"] = ok
    return JsonResponse(summary)

def test_email(request):
    subject = "Test Email from Geeza Break Website"
    body = """
        <h2>Hello Devansh,</h2>
        <p>This is a test email sent from the Geeza Break Django site using Mailjet.</p>
        <p>If you see this in your Outlook inbox, Mailjet + Django integration works! ✅</p>
    """

    try:
        send_form_email(subject, body, settings.GENERAL_RECIPIENTS)
        return HttpResponse("✅ Test email sent successfully. Check Outlook inbox.")
    except Exception as e:
        return HttpResponse(f"❌ Email sending failed: {e}")

def terms(request):
    """Display terms and conditions page"""
    return render(request, 'main/terms.html')

def privacy_policy(request):
    """Display privacy policy page"""
    return render(request, 'main/privacy_policy.html')

def news(request):
    """Display news page"""
    return render(request, 'main/news.html')

def volunteer(request):
    """Handle volunteer interest form display and submission"""
    from .forms import VolunteerInterestForm
    from .models import VolunteerInterest

    if request.method == 'POST':
        if request.POST.get("company_website"):
            messages.success(
                request,
                "Thanks for submitting your volunteer interest form! We'll be in touch soon.",
            )
            return redirect('main:volunteer')
        form = VolunteerInterestForm(request.POST)
        if form.is_valid():
            # Save the volunteer interest
            volunteer_interest = form.save()

            # Send volunteer email using new mailer
            formatted_body = f"New Volunteer Form Submission\n\nName: {volunteer_interest.full_name}\nEmail: {volunteer_interest.email}\nPhone: {volunteer_interest.phone}\nRoles: {volunteer_interest.roles}\nAvailability: {volunteer_interest.availability}\nIs Student: {volunteer_interest.is_student}\nCourse: {volunteer_interest.course_or_discipline}\nMessage: {volunteer_interest.message}"
            send_form_email(
                "Volunteer Form Submission",
                formatted_body,
                settings.GENERAL_RECIPIENTS
            )
            
            messages.success(
                request,
                "Thanks for submitting your volunteer interest form! We'll be in touch soon.",
            )
            return redirect('main:volunteer')
        else:
            print("Volunteer form is invalid")
            print(form.errors)
    else:
        form = VolunteerInterestForm()

    return render(request, 'main/volunteer.html', {'form': form})

def fundraise(request):
    """Display fundraise page"""
    return render(request, 'main/fundraise.html')

def partners(request):
    """Display partners page"""
    return render(request, 'main/partners.html')

def donate(request):
    """Display donate page"""
    return render(request, 'main/donate.html')

def contact(request):
    if request.method == "POST":
        if request.POST.get("company_website"):
            messages.success(request, "Thanks for submitting your message! We'll be in touch soon.")
            return redirect("main:contact")
        name = request.POST.get("name","").strip()
        email = request.POST.get("email","").strip()
        phone = request.POST.get("phone","").strip()
        message = request.POST.get("message","").strip()

        if not (name and email and message):
            messages.error(request, "Please fill in your name, email, and message.")
            return redirect("main:contact")

        # Send contact email using new mailer
        formatted_body = f"New Contact Form Submission\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
        send_form_email(
            "Contact Form Submission",
            formatted_body,
            settings.GENERAL_RECIPIENTS
        )

        messages.success(request, "Thanks for submitting your message! We'll be in touch soon.")
        return redirect("main:contact")

    return render(request, "main/contact.html")

def test_referral_email(request):
    """
    Test view to send a sample referral email to Outlook
    """
    try:
        # Create a mock referral object
        from .models import Referral
        mock_referral = type('MockReferral', (), {
            'id': 999,
            'primary_carer_name': 'Test Parent',
            'primary_carer_email': 'test@example.com',
            'primary_carer_phone': '01234567890',
            'postcode': 'NE1 1AA',
            'referral_reason': 'Testing the referral email system',
            'joint_visit_required': True,
            'email_sent': False,
        })()

        # Send email using the new mailer
        formatted_body = f"Test Referral Email\n\nReferral ID: {mock_referral.id}\nName: {mock_referral.primary_carer_name}\nEmail: {mock_referral.primary_carer_email}\nPhone: {mock_referral.primary_carer_phone}\nPostcode: {mock_referral.postcode}\nReason: {mock_referral.referral_reason}\nJoint Visit: {mock_referral.joint_visit_required}"
        send_form_email(
            f"Referral: {mock_referral.primary_carer_name} ({mock_referral.postcode})",
            formatted_body,
            settings.REFERRAL_RECIPIENTS
        )

        return HttpResponse("✅ Test referral email sent to Outlook. Check your inbox!")

    except Exception as e:
        return HttpResponse(f"❌ Test referral email failed: {str(e)}")
