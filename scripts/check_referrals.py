import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')
django.setup()
from main.models import Referral
qs = Referral.objects.all().order_by('-created_at')[:10]
for r in qs:
    print(r.id, r.created_at.isoformat(), r.email_sent)
