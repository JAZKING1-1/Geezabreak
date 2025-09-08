from django.urls import path
from . import views
from .views import ReferralCreateView, ReferralThanksView, ReferralReviewView

app_name = "main"

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path("extra-support/", views.extra_support, name="extra_support"),
    path('contact/', views.contact, name='contact'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('submit-comment/', views.submit_comment, name='submit_comment'),
    # Use the new ReferralCreateView directly at /referral/
    path('referral/', ReferralCreateView.as_view(), name='referral'),
    path('referral/new/', ReferralCreateView.as_view(), name='referral_create'),  # optional alias
    path('referral/review/', ReferralReviewView.as_view(), name='referral_review'),
    path('referral/thanks/', ReferralThanksView.as_view(), name='referral_thanks'),
    path('fun-zone/', views.fun_zone, name='fun_zone'),
    path('news/', views.news, name='news'),
    path('volunteer/', views.volunteer, name='volunteer'),
    path('fundraise/', views.fundraise, name='fundraise'),
    path('partners/', views.partners, name='partners'),
    path('donate/', views.donate, name='donate'),
    # Email testing and monitoring routes
    path('test-email/', views.test_email, name='test_email'),
    path('email-status/', views.email_status, name='email_status'),
    path('resend-email/<int:referral_id>/', views.resend_email, name='resend_email'),
]
