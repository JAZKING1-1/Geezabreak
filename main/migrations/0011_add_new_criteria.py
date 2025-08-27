from django.db import migrations

CRITERIA_TO_ADD = [
    ("child-mental-health", "Child/young person mental health"),
    ("safeguarding-child-protection", "Safeguarding / child protection"),
    ("addiction-substance-misuse", "Addiction / substance misuse"),
    ("criminal-justice-experience", "Experience of the criminal justice system"),
    ("kinship-care-criterion", "Kinship care"),
]

def add_criteria(apps, schema_editor):
    Criterion = apps.get_model('main', 'Criterion')
    # Determine starting order as max existing order + 1
    try:
        start_order = Criterion.objects.order_by('-order').values_list('order', flat=True).first() or 0
    except Exception:
        start_order = 0
    order = start_order + 1
    existing_slugs = set(Criterion.objects.filter(key__in=[c[0] for c in CRITERIA_TO_ADD]).values_list('key', flat=True))
    for key, label in CRITERIA_TO_ADD:
        if key in existing_slugs:
            # Ensure it's active
            Criterion.objects.filter(key=key).update(active=True)
            continue
        Criterion.objects.create(key=key, label=label, active=True, order=order)
        order += 1


def reverse(apps, schema_editor):
    Criterion = apps.get_model('main', 'Criterion')
    Criterion.objects.filter(key__in=[c[0] for c in CRITERIA_TO_ADD]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0010_referral_joint_visit_required'),
    ]

    operations = [
        migrations.RunPython(add_criteria, reverse),
    ]
