from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Feedback, Referral, Criterion
from .forms import ReferralForm, ReferralChildFormSet
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.db import transaction
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.views import View
from .models_comment import Comment
import logging
from django.templatetags.static import static
from django.contrib import messages
from .forms import VolunteerInterestForm
from .models import ROLE_CHOICES

# Set up logging for email issues
logger = logging.getLogger(__name__)

def home(request):
    if not request.session.get('visited_home'):
        request.session['visited_home'] = True
        request.session.save()
    comments = Comment.objects.filter(approved=True).order_by('-created_at')[:10]
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
    return render(request, 'main/landing.html')

def about(request):
    from .models import TeamMember
    team_members = TeamMember.objects.filter().order_by('order', 'name')
    return render(request, 'main/about.html', {'team_members': team_members})

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
            # Send feedback to email using EmailMessage with Reply-To
            subject = f"New Feedback from {feedback.name}"
            message = (
                f"Name: {feedback.name}\n"
                f"Contact Number: {feedback.contact_number}\n"
                f"Email: {feedback.email}\n"
                f"Service Used: {feedback.get_service_used_display()}\n"
                f"Message:\n{feedback.message}"
            )
            try:
                email = EmailMessage(
                    subject,
                    message,
                    'Geeza Break <ds16022004@gmail.com>',
                    ['ds16022004@gmail.com'],
                    headers={'Reply-To': feedback.email}
                )
                email.send(fail_silently=False)
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
        Send email notification about a new referral.
        Now with enhanced logging and error handling.
        """
        logger.info(f"Preparing email notification for referral ID: {referral.id}")
        
        # Get active services
        services = [lbl for lbl,flag in [
            ("Family Support", referral.srv_family_support),
            ("Respite Sitting", referral.srv_respite_sitting),
            ("Respite Care", referral.srv_respite_care),
            ("Geeza Chance", referral.srv_geezachance),
            ("Kinship Care", referral.srv_kinship_care),
        ] if flag]
        
        # Get criteria and child information
        crits = list(referral.criteria.values_list('label', flat=True))
        child_lines = [
            f" - {c.full_name} ({c.dob:%d/%m/%Y}) {c.get_relationship_display()} ASN:{'Y' if c.has_asn else 'N'}"
            for c in referral.children.all()
        ] or [' (No children listed)']
        
        # Format email body
        body = (
            f"New referral received\n\n"
            f"Parent/Carer: {referral.primary_carer_name}\n"
            f"Postcode: {referral.postcode}\n"
            f"HSCP: {referral.get_hscp_locality_display()} | Ward: {referral.get_ward_display()}\n"
            f"Services: {', '.join(services) or '-'}\n"
            f"Criteria: {', '.join(crits) or '-'}\n"
            f"Reason/Notes:\n{referral.reason}\n\n"
            f"Children:\n" + "\n".join(child_lines) + "\n\n" +
            f"Referrer Information:\n" +
            f"Name: {referral.referrer_name}\n" +
            f"Agency: {referral.referrer_agency}\n" +
            f"Email: {referral.referrer_email}\n" +
            f"Phone: {referral.referrer_phone}\n\n" +
            f"This notification was sent to: {', '.join(getattr(settings, 'REFERRAL_NOTIFICATION_RECIPIENTS', []))}"
        )
        
        # Get email settings
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@geezabreak.org.uk')
        to_admin = getattr(settings, 'REFERRAL_NOTIFICATION_RECIPIENTS', [])
        
        # Always print to console for debugging
        print("\n" + "="*80)
        print("REFERRAL NOTIFICATION")
        print("="*80)
        print(f"Email backend: {settings.EMAIL_BACKEND}")
        print(f"From: {from_email}")
        print(f"To: {to_admin}")
        print(f"Subject: Referral: {referral.primary_carer_name} ({referral.postcode})")
        print("-"*80)
        print(body)
        print("="*80 + "\n")
        
        # Check if we have recipients
        if not to_admin:
            print("WARNING: No email recipients configured. Please check REFERRAL_NOTIFICATION_RECIPIENTS in settings.")
            logger.warning("No email recipients configured for referral notifications")
            return
            
        try:
            print(f"Attempting to send email notification to {to_admin}")
            logger.info(f"Sending referral notification to {to_admin}")
            
            # Create email message with all necessary headers
            email = EmailMessage(
                subject=f"Referral: {referral.primary_carer_name} ({referral.postcode})",
                body=body,
                from_email=from_email,
                to=to_admin,
                reply_to=[referral.referrer_email] if referral.referrer_email else None,
            )
            
            # Send email with error reporting
            email.send(fail_silently=False)
            
            # Log success
            print(f"Email notification sent successfully to {to_admin}")
            logger.info(f"Email notification sent successfully for referral ID: {referral.id}")
            
            # Save a record of the sent email to database
            referral.email_sent = True
            referral.save(update_fields=['email_sent'])
            
        except Exception as e:
            # Detailed error logging
            print(f"ERROR sending email notification: {str(e)}")
            logger.error(f"Failed to send email notification for referral ID: {referral.id}, Error: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"Email backend: {settings.EMAIL_BACKEND}")
            print(f"Check that the email backend is correctly configured in settings.py")

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
    return render(request, 'main/contact.html')

def impact(request):
    return render(request, 'main/impact.html')

def news(request):
    return render(request, 'main/news.html')

def fundraise(request):
    return render(request, 'main/fundraise.html')

def partners(request):
    return render(request, 'main/partners.html')

def donate(request):
    return render(request, 'main/donate.html')

def news(request):
    return render(request, 'main/news.html')

def impact(request):
    return render(request, 'main/impact.html')

def get_help(request):
    return render(request, 'main/get_help.html')

def volunteer(request):
    if request.method == "POST":
        form = VolunteerInterestForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            # store roles as comma-separated keys
            entry.roles = ",".join(form.cleaned_data["roles"])
            entry.save()
            messages.success(request, "Thanks! We’ve received your interest and will be in touch.")
            return redirect("volunteer")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = VolunteerInterestForm()

    role_map = dict(ROLE_CHOICES)
    return render(request, "main/volunteer.html", {
        "form": form,
        "role_map": role_map,
    })

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
        
        # For better diagnostics, try both methods separately
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
