import os
import sys

# Ensure project root in path
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geezabreak.settings')

import django
from django.template.loader import get_template

django.setup()

try:
    t = get_template('main/about.html')
    print('Template parsed OK')
except Exception as e:
    print('Template parse error:')
    import traceback
    traceback.print_exc()
    sys.exit(1)
