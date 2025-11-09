# Generated migration for new referral fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_merge_0010_volunteerinterest_0011_add_new_criteria'),
    ]

    operations = [
        # Add the contact number field as nullable first
        migrations.AddField(
            model_name='referral',
            name='primary_carer_contact_number',
            field=models.CharField(help_text='Mandatory contact number for the family', max_length=20, verbose_name='Contact number', null=True, blank=True),
        ),
        # Add other optional fields
        migrations.AddField(
            model_name='referral',
            name='primary_carer_dob',
            field=models.DateField(blank=True, help_text='Date of birth of the parent/carer', null=True, verbose_name='Date of birth (Parent/Carer)'),
        ),
        migrations.AddField(
            model_name='referral',
            name='ethnicity',
            field=models.CharField(blank=True, choices=[('white_british', 'White British'), ('white_irish', 'White Irish'), ('white_other', 'White Other'), ('mixed_white_black_caribbean', 'Mixed White and Black Caribbean'), ('mixed_white_black_african', 'Mixed White and Black African'), ('mixed_white_asian', 'Mixed White and Asian'), ('mixed_other', 'Mixed Other'), ('asian_indian', 'Asian Indian'), ('asian_pakistani', 'Asian Pakistani'), ('asian_bangladeshi', 'Asian Bangladeshi'), ('asian_chinese', 'Asian Chinese'), ('asian_other', 'Asian Other'), ('black_african', 'Black African'), ('black_caribbean', 'Black Caribbean'), ('black_other', 'Black Other'), ('arab', 'Arab'), ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say')], help_text='Ethnicity of the family', max_length=50, verbose_name='Ethnicity'),
        ),
        migrations.AddField(
            model_name='referral',
            name='referral_reason',
            field=models.CharField(blank=True, choices=[('family_support_needed', 'Family Support Needed'), ('respite_care_required', 'Respite Care Required'), ('child_behavioral_issues', 'Child Behavioral Issues'), ('parent_disability', 'Parent Disability'), ('mental_health_conditions', 'Mental Health Conditions'), ('financial_difficulties', 'Financial Difficulties'), ('social_isolation', 'Social Isolation'), ('housing_issues', 'Housing Issues'), ('domestic_violence', 'Domestic Violence'), ('substance_abuse', 'Substance Abuse'), ('kinship_care_support', 'Kinship Care Support'), ('additional_support_needs', 'Additional Support Needs'), ('other', 'Other')], help_text='Primary reason for this referral', max_length=50, verbose_name='Reason for referral'),
        ),
    ]