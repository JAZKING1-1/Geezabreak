"""Public service information; no staff records or payroll access."""
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_safe

from .brighter_content import BRIGHTER_BIO, TESTIMONIALS


@require_safe
def brighter_beginnings(request):
    return render(request, 'main/brighter/brighter_beginnings.html', {
        'title': 'Brighter Beginnings', 'service_page': 'brighter',
        'bio': BRIGHTER_BIO, 'testimonials': TESTIMONIALS,
    })


@require_safe
def family_support_groups(request):
    return redirect(reverse('main:services') + '#family-support-group-work')


@require_safe
def adrs_respite_sitting(request):
    return redirect(reverse('main:services') + '#adrs-respite-sitting')
