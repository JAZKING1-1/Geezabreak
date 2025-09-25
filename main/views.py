from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Feedback, Referral, Criterion, VolunteerInterest
from .forms import ReferralForm, ReferralChildFormSet
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.db import transaction
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.views import View
from .models import Comment
import logging
from django.templatetags.static import static
from django.contrib import messages
from core.emails import send_form_email

# Set up logging for email issues
logger = logging.getLogger(__name__)

def _form_recipients():
    recipients_setting = getattr(settings, "FORMS_TO_EMAIL", "")
    if isinstance(recipients_setting, (list, tuple)):
        return [email.strip() for email in recipients_setting if email and email.strip()]
    return [email.strip() for email in str(recipients_setting).split(',') if email and email.strip()]

def home(request):
    logger = logging.getLogger(__name__)
    logger.info("Home view called")
    if not request.session.get('visited_home'):
        request.session['visited_home'] = True
        request.session.save()
    try:
        comments = Comment.objects.filter(approved=True).order_by('-created_at')[:10]
        logger.info(f"Comments: {comments}")
    except Exception as e:
        logger.error(f"Error getting comments: {e}")
        comments = []
    # Provide default impact images for the story wall if view doesn't pass them
    available = [
        'images/1.jpg', 'images/2.jpg', 'images/3.jpg', 'images/4.jpg',
        'images/i3.jpg', 'images/i5.jpg', 'images/i7.jpg'
    ]
    testimonials = [
        "Geeza Break gave us the breathing space we truly needed as a family.",
        "The kids always look forward to their playtime with Geeza Break staff.",
        "Having someone to trust made all the difference for us.",
        "They don't just support the children – they support the whole family.",
        "Geeza Break helped us find joy in the little moments again.",
        "The team always makes us feel valued and understood.",
        "Our home feels lighter and happier since Geeza Break stepped in.",
        "Consistent, caring, and always ready to listen – that's Geeza Break.",
        "My child's confidence has grown so much thanks to the positive play sessions.",
        "Geeza Break turned a very stressful time into a hopeful journey."
    ]

    def make_list(n, offset=0):
        out = []
        for i in range(n):
            p = available[i % len(available)]
            caption = testimonials[(i + offset) % len(testimonials)]
            out.append({'src': static(p), 'alt': 'Geeza Break moment', 'caption': caption})
        return out

    impact_top = make_list(10)
    impact_bottom = make_list(10, offset=5) # Use different testimonials for bottom row

    return render(request, 'main/home.html', {
        'comments': comments,
        'impact_images': impact_top,
        'impact_images_bottom': impact_bottom,
    })

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

def services(request):
    return render(request, 'main/services.html')

def extra_support(request):
    return render(request, "main/extra_support.html")

def get_help(request):
    return render(request, 'main/get_help.html')

def submit_feedback(request):
    print("Feedback view called")
    if request.method == 'POST':
        try:
            feedback = Feedback(
                name=request.POST.get('name'),
                contact_number=request.POST.get('contact_number'),
                email=request.POST.get('email'),
                service_used=request.POST.get('service_used'),
                message=request.POST.get('message')
            )
            feedback.save()
            
            # Send feedback email using Mailjet
            subject = f"New Feedback from {feedback.name}"
            body = f"""
                <h2>New Feedback Submission</h2>
                <p><b>Name:</b> {feedback.name}</p>
                <p><b>Email:</b> {feedback.email}</p>
                <p><b>Phone:</b> {feedback.contact_number}</p>
                <p><b>Service Used:</b> {feedback.get_service_used_display()}</p>
                <p><b>Message:</b><br>{feedback.message}</p>
            """
            
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email='"Devansh Sharma" <devansh.sharma@geezabreak.org.uk>',
                to=_form_recipients(),
                headers={'Reply-To': feedback.email}
            )
            msg.content_subtype = "html"
            
            try:
                msg.send(fail_silently=False)
                print(f"Feedback email sent successfully for {feedback.name}")
            except Exception as e:
                print("EMAIL ERROR:", str(e))
                return JsonResponse({'status': 'error', 'message': f'Email error: {str(e)}'})
            
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
        print("DEBUG: _save_and_redirect called")
        try:
            self.object = form.save()
            print(f"DEBUG: Referral saved with ID: {self.object.id}")
            formset.instance = self.object
            formset.save()
            print(f"DEBUG: Formset saved, {formset.save()} children saved")
            print("DEBUG: Calling _send_emails")
            # Build children summary from saved ReferralChild objects
            try:
                from .models import ReferralChild
                children_qs = ReferralChild.objects.filter(referral=self.object)
                children = []
                for c in children_qs:
                    children.append({
                        'full_name': getattr(c, 'full_name', ''),
                        'dob': getattr(c, 'dob', None).isoformat() if getattr(c, 'dob', None) else '',
                        'relationship': getattr(c, 'relationship', ''),
                        'has_asn': bool(getattr(c, 'has_asn', False)),
                        'school_nursery': getattr(c, 'school_nursery', ''),
                    })
            except Exception:
                children = []

            # Pass the cleaned form data to the email builder so all submitted fields are included
            self._send_emails(self.object, form_data=getattr(form, 'cleaned_data', None), children=children)
            print("DEBUG: _send_emails completed, redirecting to success URL")
            return redirect(self.get_success_url())
        except Exception as e:
            print(f"DEBUG: Exception in _save_and_redirect: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _send_emails(self, referral: Referral, form_data=None, children=None):
        """
        Send email notification about a new referral using Mailjet.
        """
        print(f"DEBUG: _send_emails called for referral ID: {referral.id}")
        logger.info(f"Preparing email notification for referral ID: {referral.id}")
        
        try:
            print("DEBUG: Building email message")
            # If form_data provided, build the email body from submitted fields
            from django.db.models.query import QuerySet

            def fmt_value(v):
                if isinstance(v, QuerySet):
                    return ', '.join(str(x) for x in v)
                if isinstance(v, (list, tuple, set)):
                    return ', '.join(str(x) for x in v)
                if isinstance(v, bool):
                    return 'Yes' if v else 'No'
                if v is None:
                    return ''
                return str(v)

            body = '<h2>New Referral Submission</h2>'
            if form_data:
                for field, value in form_data.items():
                    # Skip internal values like management forms or cleaned QueryDict markers
                    try:
                        label = field.replace('_', ' ').title()
                    except Exception:
                        label = str(field)
                    body += f"<p><b>{label}:</b> {fmt_value(value)}</p>"
            else:
                # Fallback: build body from referral model attributes (safe subset)
                model_vals = {}
                for attr in ['primary_carer_name','referrer_name','referrer_email','referrer_phone','address_line1','address_line2','city','postcode','reason','joint_visit_required']:
                    val = getattr(referral, attr, None)
                    if val is not None:
                        label = attr.replace('_',' ').title()
                        body += f"<p><b>{label}:</b> {fmt_value(val)}</p>"

            # Append children information if available
            if children and isinstance(children, (list, tuple)) and len(children) > 0:
                body += '<h3>Children</h3>'
                for i, c in enumerate(children, start=1):
                    body += f"<p><b>Child {i}:</b> {fmt_value(c.get('full_name',''))} — DOB: {fmt_value(c.get('dob',''))} — Relationship: {fmt_value(c.get('relationship',''))} — ASN: {fmt_value(c.get('has_asn',''))}</p>"

            # If children not provided, attempt to load from DB
            if (not children) and hasattr(referral, 'id'):
                try:
                    from .models import ReferralChild
                    kids = ReferralChild.objects.filter(referral=referral)
                    if kids.exists():
                        body += '<h3>Children</h3>'
                        for i, k in enumerate(kids, start=1):
                            dob = getattr(k, 'dob', None)
                            dob_str = dob.isoformat() if dob else ''
                            body += f"<p><b>Child {i}:</b> {getattr(k,'full_name','')} — DOB: {dob_str} — Relationship: {getattr(k,'relationship','')} — ASN: {'Yes' if getattr(k,'has_asn',False) else 'No'}</p>"
                except Exception:
                    pass

            subject = f"Referral: {getattr(referral, 'primary_carer_name', 'Referral')} ({getattr(referral, 'postcode', '')})"

            print("DEBUG: Creating EmailMessage")
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email='"Devansh Sharma" <devansh.sharma@geezabreak.org.uk>',
                to=_form_recipients(),
                headers={'Reply-To': (form_data.get('referrer_email') if form_data and form_data.get('referrer_email') else getattr(referral, 'referrer_email', 'devansh.sharma@geezabreak.org.uk'))}
            )
            msg.content_subtype = "html"
            print("DEBUG: Sending email")
            msg.send(fail_silently=False)
            print("DEBUG: Email sent successfully")
            
            # Log success
            print(f"Referral email notification sent successfully for {referral.primary_carer_name}")
            logger.info(f"Email notification sent successfully for referral ID: {referral.id}")
            
            # Save a record of the sent email to database
            referral.email_sent = True
            referral.save(update_fields=['email_sent'])
            print("DEBUG: Email sent flag updated in database")
            
        except Exception as e:
            # Detailed error logging
            error_msg = f"ERROR sending email notification: {str(e)}"
            print(error_msg)
            print(f"DEBUG: Exception details: {str(e)}")
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to send email notification for referral ID: {referral.id}, Error: {str(e)}")
            
            # Ensure email_sent is set to False if sending failed
            referral.email_sent = False
            referral.save(update_fields=['email_sent'])
            print("DEBUG: Email sent flag set to False due to error")
            
            # Don't re-raise the exception to avoid breaking the form submission
            # The referral is still saved to the database, just the email failed

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
        print("DEBUG: Calling _send_emails from ReferralReviewView")
        # Try to include children and any session form data when sending email
        session_data = request.session.get('referral_draft') or {}
        form_data = session_data.get('ref') if isinstance(session_data, dict) else None
        children = session_data.get('children') if isinstance(session_data, dict) else None
        try:
            ReferralCreateView()._send_emails(r, form_data=form_data, children=children)
        except Exception as e:
            print(f"DEBUG: _send_emails from ReferralReviewView raised: {e}")
        print("DEBUG: Clearing session and redirecting to thanks page")
        request.session.pop('referral_draft', None)
        return redirect(reverse_lazy('main:referral_thanks'))


class ReferralThanksView(TemplateView):
    template_name = 'main/referral_thanks.html'

def fun_zone(request):
    games = [
        {'title': 'Memory Match', 'url': 'https://www.memozor.com/memory-games', 'thumb': 'images/games/memory.jpg', 'category': 'iq', 'desc': 'Improve your memory by matching cards!'},
        {'title': 'Math Playground', 'url': 'https://www.mathplayground.com/', 'thumb': 'images/games/math.jpg', 'category': 'iq', 'desc': 'Solve math puzzles and logic games.'},
        {'title': 'Simon Says', 'url': 'https://www.memozor.com/simon-game', 'thumb': 'images/games/simon.jpg', 'category': 'iq', 'desc': 'Repeat the color sequence.'},
        {'title': 'Sudoku for Kids', 'url': 'https://www.primarygames.com/puzzles/sudoku/', 'thumb': 'images/games/sudoku.jpg', 'category': 'iq', 'desc': 'Simple sudoku puzzles for beginners.'},
        {'title': 'Pattern Blocks', 'url': 'https://www.nctm.org/Classroom-Resources/Illuminations/Interactives/Pattern-Blocks/', 'thumb': 'images/games/pattern.jpg', 'category': 'iq', 'desc': 'Build and recognize patterns.'},
        {'title': 'Space Invaders', 'url': 'https://www.retrogames.cc/arcade-games/space-invaders.html', 'thumb': 'images/games/space-invaders.jpg', 'category': 'arcade', 'desc': 'Classic arcade shooter. Quick reflexes needed!'},
        {'title': 'Pac-Man', 'url': 'https://www.google.com/doodles/30th-anniversary-of-pac-man', 'thumb': 'images/games/pacman.jpg', 'category': 'arcade', 'desc': 'Eat the dots, avoid ghosts!'},
        {'title': 'Tetris', 'url': 'https://tetris.com/play-tetris', 'thumb': 'images/games/tetris.jpg', 'category': 'arcade', 'desc': 'Fit the falling blocks.'},
        {'title': 'Snake', 'url': 'https://playsnake.org/', 'thumb': 'images/games/snake.jpg', 'category': 'arcade', 'desc': 'Grow your snake, don’t hit the wall.'},
        {'title': 'Flappy Bird', 'url': 'https://flappybird.io/', 'thumb': 'images/games/flappy.jpg', 'category': 'arcade', 'desc': 'Tap to fly through pipes.'},
        {'title': 'Drawing Pad', 'url': 'https://sketch.io/sketchpad/', 'thumb': 'images/games/draw.jpg', 'category': 'creative', 'desc': 'Express creativity by painting online.'},
        {'title': 'Online Piano', 'url': 'https://www.onlinepianist.com/virtual-piano', 'thumb': 'images/games/piano.jpg', 'category': 'creative', 'desc': 'Play music with your keyboard.'},
        {'title': 'Coloring Book', 'url': 'https://www.thecolor.com/', 'thumb': 'images/games/coloring.jpg', 'category': 'creative', 'desc': 'Color fun pictures online.'},
        {'title': 'Make a Comic', 'url': 'https://www.makebeliefscomix.com/Comix/', 'thumb': 'images/games/comic.jpg', 'category': 'creative', 'desc': 'Create your own comic strips.'},
        {'title': 'LEGO Builder', 'url': 'https://www.lego.com/en-us/kids/build', 'thumb': 'images/games/lego.jpg', 'category': 'creative', 'desc': 'Build with virtual LEGO bricks.'},
        {'title': 'Jigsaw Puzzles', 'url': 'https://www.jigsawplanet.com/', 'thumb': 'images/games/jigsaw.jpg', 'category': 'puzzle', 'desc': 'Solve digital jigsaws.'},
        {'title': '2048', 'url': 'https://play2048.co/', 'thumb': 'images/games/2048.jpg', 'category': 'puzzle', 'desc': 'Slide tiles to reach 2048.'},
        {'title': 'Minesweeper', 'url': 'https://minesweeperonline.com/', 'thumb': 'images/games/minesweeper.jpg', 'category': 'puzzle', 'desc': 'Classic logic puzzle game.'},
        {'title': 'Tangram', 'url': 'https://www.transum.org/Maths/Investigation/Tangram/', 'thumb': 'images/games/tangram.jpg', 'category': 'puzzle', 'desc': 'Arrange shapes to match a picture.'},
        {'title': 'Chess for Kids', 'url': 'https://www.chesskid.com/play/fast', 'thumb': 'images/games/chess.jpg', 'category': 'strategy', 'desc': 'Play chess with hints and tips.'},
    ]
    return render(request, 'main/fun_zone.html', {'games': games})

def email_status(request):
    """
    Display the status of email notifications for referrals
    """
    # Get recent referrals ordered by creation date (newest first)
    referrals = Referral.objects.all().order_by('-created_at')[:20]
    
    # Get email settings
    context = {
        'referrals': referrals,
        'email_backend': settings.EMAIL_BACKEND,
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'not set'),
        'recipients': getattr(settings, 'REFERRAL_NOTIFICATION_RECIPIENTS', []),
    }
    
    return render(request, 'main/email_status.html', context)

def resend_email(request, referral_id):
    """
    Resend email notification for a specific referral
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
        
    try:
        # Get the referral
        referral = Referral.objects.get(id=referral_id)
        
        # Use the existing send_emails method
        print(f"Attempting to resend email for referral #{referral_id}")
        
        # Create a temporary instance of ReferralCreateView to access _send_emails method
        view_instance = ReferralCreateView()
        view_instance._send_emails(referral)
        
        return JsonResponse({
            'success': True,
            'message': f"Email notification for referral #{referral_id} has been resent successfully."
        })
        
    except Referral.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f"Referral #{referral_id} not found."
        })
        
    except Exception as e:
        print(f"Error resending email: {str(e)}")
        import traceback
        error_details = traceback.format_exc()
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'message': f"Failed to resend email: {str(e)}",
            'error_details': error_details
        })

def test_email(request):
    subject = "Test Email from Geeza Break Website"
    body = """
        <h2>Hello Devansh,</h2>
        <p>This is a test email sent from the Geeza Break Django site using Mailjet.</p>
        <p>If you see this in your Outlook inbox, Mailjet + Django integration works! ✅</p>
    """

    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email='"Devansh Sharma" <devansh.sharma@geezabreak.org.uk>',  # use your validated sender
        to=_form_recipients(),       # recipient list
        headers={'Reply-To': "devansh.sharma@geezabreak.org.uk"}          # will later become visitor email
    )
    msg.content_subtype = "html"
    try:
        msg.send(fail_silently=False)
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
        form = VolunteerInterestForm(request.POST)
        if form.is_valid():
            # Save the volunteer interest
            volunteer_interest = form.save()

            # Send email notification using Mailjet
            subject = f"New Volunteer Interest from {volunteer_interest.full_name}"
            body = f"""
                <h2>New Volunteer Interest</h2>
                <p><b>Name:</b> {volunteer_interest.full_name}</p>
                <p><b>Email:</b> {volunteer_interest.email}</p>
                <p><b>Phone:</b> {volunteer_interest.phone}</p>
                <p><b>Roles:</b> {volunteer_interest.roles}</p>
                <p><b>Availability:</b> {volunteer_interest.availability}</p>
                <p><b>Is Student:</b> {'Yes' if volunteer_interest.is_student else 'No'}</p>
                <p><b>Course/Discipline:</b> {volunteer_interest.course_or_discipline}</p>
                <p><b>Message:</b><br>{volunteer_interest.message}</p>
                <p><b>Consent to Contact:</b> {'Yes' if volunteer_interest.consent_contact else 'No'}</p>
            """
            
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email='"Devansh Sharma" <devansh.sharma@geezabreak.org.uk>',
                to=_form_recipients(),
                headers={'Reply-To': volunteer_interest.email}
            )
            msg.content_subtype = "html"
            
            try:
                msg.send(fail_silently=False)
                print(f"Volunteer interest email sent successfully for {volunteer_interest.full_name}")
                messages.success(request, 'Thank you for your interest! We will be in touch soon.')
            except Exception as e:
                print(f"EMAIL ERROR for volunteer interest: {str(e)}")
                messages.error(request, 'Your interest was recorded but there was an issue sending the email. Please try again later.')

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
        name = request.POST.get("name","").strip()
        email = request.POST.get("email","").strip()
        phone = request.POST.get("phone","").strip()
        message = request.POST.get("message","").strip()

        if not (name and email and message):
            messages.error(request, "Please fill in your name, email, and message.")
            return redirect("main:contact")

        # Send email notification using Mailjet
        subject = f"Website Contact: {name}"
        body = f"""
            <h2>New Contact Form Submission</h2>
            <p><b>Name:</b> {name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Phone:</b> {phone}</p>
            <p><b>Message:</b><br>{message}</p>
        """
        
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email='"Devansh Sharma" <devansh.sharma@geezabreak.org.uk>',
            to=_form_recipients(),
            headers={'Reply-To': email}
        )
        msg.content_subtype = "html"
        
        try:
            msg.send(fail_silently=False)
            messages.success(request, "Thanks for reaching out — we'll be in touch soon.")
        except Exception as e:
            messages.error(request, f"There was an error sending your message: {str(e)}")
            return redirect("main:contact")

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

        # Send email using the same method as the actual referral form
        from core.emails import send_form_email
        send_form_email(
            subject=f"Referral: {mock_referral.primary_carer_name} ({mock_referral.postcode})",
            template_name="emails/referral.html",
            context={"referral": mock_referral}
        )

        return HttpResponse("✅ Test referral email sent to Outlook. Check your inbox!")

    except Exception as e:
        return HttpResponse(f"❌ Test referral email failed: {str(e)}")
