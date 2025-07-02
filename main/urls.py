from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('get-help/', views.get_help, name='get_help'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('submit-comment/', views.submit_comment, name='submit_comment'),
    path('referral/', views.referral, name='referral'),
    path('fun-zone/', views.fun_zone, name='fun_zone'),
]
