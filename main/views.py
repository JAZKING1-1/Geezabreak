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

    # Sort ascending by join date then display name
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
            from core.emails import send_form_email
            try:
                send_form_email(
                    subject=f"New Feedback from {feedback.name}",
                    template_name="emails/feedback.html",
                    context={"feedback": feedback}
                )
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
        self.object = None
        form = self.get_form()
        child_formset = ReferralChildFormSet(request.POST, prefix='children')
        action = request.POST.get('action', 'submit')
        if action == 'review':
            if form.is_valid() and child_formset.is_valid():
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
                return redirect('main:referral_review')
            return self.render_invalid(form, child_formset)
        # direct submit
        if form.is_valid() and child_formset.is_valid():
            return self._save_and_redirect(form, child_formset)
        return self.render_invalid(form, child_formset)

    @transaction.atomic
    def _save_and_redirect(self, form, formset):
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        self._send_emails(self.object)
        return redirect(self.get_success_url())

    def _send_emails(self, referral: Referral):
        """
        Send email notification about a new referral using Mailjet.
        """
        from core.emails import send_form_email
        
        logger.info(f"Preparing email notification for referral ID: {referral.id}")
        
        try:
            # Send email using Mailjet
            send_form_email(
                subject=f"Referral: {referral.primary_carer_name} ({referral.postcode})",
                template_name="emails/referral.html",
                context={"referral": referral}
            )
            
            # Log success
            print(f"Referral email notification sent successfully for {referral.primary_carer_name}")
            logger.info(f"Email notification sent successfully for referral ID: {referral.id}")
            
            # Save a record of the sent email to database
            referral.email_sent = True
            referral.save(update_fields=['email_sent'])
            
        except Exception as e:
            # Detailed error logging
            error_msg = f"ERROR sending email notification: {str(e)}"
            print(error_msg)
            logger.error(f"Failed to send email notification for referral ID: {referral.id}, Error: {str(e)}")
            
            # Ensure email_sent is set to False if sending failed
            referral.email_sent = False
            referral.save(update_fields=['email_sent'])
            
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
        data = request.session.get('referral_draft')
        if not data:
            return redirect('main:referral')
        ref = data['ref'].copy()
        crit_ids = ref.pop('criteria_ids', [])
        # create referral (exclude M2M for now)
        r = Referral.objects.create(**{k:v for k,v in ref.items() if k not in ['criteria','criteria_other']})
        if crit_ids:
            r.criteria.set(Criterion.objects.filter(id__in=crit_ids))
        if ref.get('criteria_other'):
            r.criteria_other = ref['criteria_other']
            r.save(update_fields=['criteria_other'])
        from .models import ReferralChild
        for c in data['children']:
            ReferralChild.objects.create(
                referral=r,
                full_name=c['full_name'],
                dob=c['dob'],
                relationship=c['relationship'],
                has_asn=c['has_asn'],
                school_nursery=c['school_nursery'],
            )
        ReferralCreateView()._send_emails(r)
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

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name","").strip()
        email = request.POST.get("email","").strip()
        phone = request.POST.get("phone","").strip()
        message = request.POST.get("message","").strip()

        if not (name and email and message):
            messages.error(request, "Please fill in your name, email, and message.")
            return redirect("main:contact")

        subject = f"Website Contact: {name}"
        body = (
            f"New message from the Geeza Break website\n\n"
            f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\n"
            f"Message:\n{message}\n"
        )

        # Send to both inboxes you monitor
        recipients = ["info@geezabreak.org.uk", "ds16022004@gmail.com"]  # adjust as needed
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)

        messages.success(request, "Thanks for reaching out — we'll be in touch soon.")
        return redirect("main:contact")

    return render(request, "main/contact.html")

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
    """
    Test view to verify email functionality.
    - GET: Shows a test form with email settings
    - POST: Sends a test email and returns JSON response
    """
    import sys
    import datetime
    
    # Common email configuration settings
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@geezabreak.org.uk')
    recipient_list = getattr(settings, 'REFERRAL_NOTIFICATION_RECIPIENTS', ['ds16022004@gmail.com'])
    
    # Handle GET request - display the test form
    if request.method == 'GET':
        context = {
            'email_backend': settings.EMAIL_BACKEND,
            'from_email': from_email,
            'recipients': recipient_list,
        }
        return render(request, 'main/test_email.html', context)
    
    # Handle POST request - send test email and return JSON response
    # Prepare response data
    response_data = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email_backend': settings.EMAIL_BACKEND,
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'django_settings': {
            'DEBUG': settings.DEBUG,
            'DEFAULT_FROM_EMAIL': from_email,
            'REFERRAL_NOTIFICATION_RECIPIENTS': recipient_list,
        }
    }
    
    try:
        # Check if we have recipients
        if not recipient_list:
            logger.error("No recipients configured for test email")
            response_data['success'] = False
            response_data['message'] = "No recipients configured. Check REFERRAL_NOTIFICATION_RECIPIENTS in settings."
            return JsonResponse(response_data)
        
        # Get email settings
        subject = 'Geeza Break Email Test'
        message = (
            f"This is a test email sent at {datetime.datetime.now()}\n\n"
            f"This email confirms that the Geeza Break website's email notification system is working.\n\n"
            f"Email configuration:\n"
            f"- Backend: {settings.EMAIL_BACKEND}\n"
            f"- From: {from_email}\n"
            f"- To: {', '.join(recipient_list)}\n\n"
            f"If you received this email, your referral notifications should be working correctly."
        )
        
        # Log the attempt
        logger.info(f"Attempting to send test email to {recipient_list}")
        print(f"\n{'='*40}\nSending test email to {recipient_list}\n{'='*40}")
        
        # For better diagnostics, try all methods separately
        send_results = []
        
        # Method 1: Using send_mail
        try:
            send_mail(
                subject=f"{subject} (send_mail method)",
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            send_results.append("send_mail: SUCCESS")
            print("send_mail method: SUCCESS")
        except Exception as e1:
            err_msg = f"send_mail method failed: {str(e1)}"
            send_results.append(err_msg)
            print(err_msg)
            logger.exception("send_mail failed in test_email view")
        
        # Method 2: Using EmailMessage
        try:
            email = EmailMessage(
                subject=f"{subject} (EmailMessage method)",
                body=message,
                from_email=from_email,
                to=recipient_list,
            )
            email.send(fail_silently=False)
            send_results.append("EmailMessage: SUCCESS")
            print("EmailMessage method: SUCCESS")
        except Exception as e2:
            err_msg = f"EmailMessage method failed: {str(e2)}"
            send_results.append(err_msg)
            print(err_msg)
            logger.exception("EmailMessage failed in test_email view")
        
        # Method 3: Using Mailjet
        try:
            from core.emails import send_form_email
            send_form_email(
                subject=f"{subject} (Mailjet method)",
                template_name="emails/feedback.html",  # Using feedback template for test
                context={
                    "feedback": type('TestFeedback', (), {
                        'name': 'Test User',
                        'contact_number': '01234567890',
                        'email': 'test@example.com',
                        'service_used': 'test',
                        'get_service_used_display': lambda: 'Test Service',
                        'message': message
                    })()
                }
            )
            send_results.append("Mailjet: SUCCESS")
            print("Mailjet method: SUCCESS")
        except Exception as e3:
            err_msg = f"Mailjet method failed: {str(e3)}"
            send_results.append(err_msg)
            print(err_msg)
            logger.exception("Mailjet failed in test_email view")
        
        # Check if at least one method worked
        success = any("SUCCESS" in result for result in send_results)
        
        if success:
            logger.info("Test email sent successfully by at least one method")
            response_data['success'] = True
            response_data['message'] = (
                f"Test email sent to {', '.join(recipient_list)}. "
                f"Check your inbox and spam folder. Results: {', '.join(send_results)}"
            )
        else:
            logger.error("All email methods failed")
            response_data['success'] = False
            response_data['message'] = f"All email methods failed: {', '.join(send_results)}"
            response_data['error_details'] = send_results
        
        print(f"{'='*40}\nTest email result: {'SUCCESS' if success else 'FAILED'}\n{'='*40}\n")
        return JsonResponse(response_data)
    
    except Exception as e:
        logger.exception("Unexpected error in test_email view")
        print(f"Error in test_email view: {str(e)}")
        import traceback
        traceback.print_exc()
        
        response_data['success'] = False
        response_data['message'] = f"Unexpected error: {str(e)}"
        response_data['error_details'] = traceback.format_exc()
        
        return JsonResponse(response_data)

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
    from core.emails import send_form_email

    if request.method == 'POST':
        form = VolunteerInterestForm(request.POST)
        if form.is_valid():
            # Save the volunteer interest
            volunteer_interest = form.save()

            # Send email notification using Mailjet
            try:
                send_form_email(
                    subject=f"New Volunteer Interest from {volunteer_interest.full_name}",
                    template_name="emails/volunteer.html",
                    context={"volunteer": volunteer_interest}
                )
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

        subject = f"Website Contact: {name}"
        body = (
            f"New message from the Geeza Break website\n\n"
            f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\n"
            f"Message:\n{message}\n"
        )

        # Send to both inboxes you monitor
        recipients = ["info@geezabreak.org.uk", "ds16022004@gmail.com"]  # adjust as needed
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)

        messages.success(request, "Thanks for reaching out — we'll be in touch soon.")
        return redirect("main:contact")

    return render(request, "main/contact.html")

def test_mailjet(request):
    """
    A simple test endpoint to send a Mailjet email and verify everything works.
    Visiting /test-mailjet/ in the browser should trigger this email.
    """
    try:
        # Build dummy context data for template rendering
        dummy_ref = {
            "child_name": "Test Child",
            "parent_name": "Test Parent",
            "email": "test@example.com",
            "phone": "0000",
            "notes": "This is a test email triggered from the test_mailjet view.",
        }

        # Call the Mailjet email helper
        send_form_email(
            subject="✅ Test Email from Geeza Break (Mailjet Integration)",
            template_name="emails/referral.html",  # reuse referral template for now
            context={"ref": dummy_ref},
        )
        return HttpResponse("✅ Mailjet test email sent successfully. Check your Outlook inbox.")
    except Exception as e:
        return HttpResponse(f"❌ Mailjet test failed: {e}")
