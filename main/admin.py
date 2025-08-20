from django.contrib import admin
from .models import Feedback, Referral, ReferralChild, Criterion, TeamMember

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
	list_display = ("name", "service_used", "created_at")
	search_fields = ("name", "email")
	list_filter = ("service_used",)

class ReferralChildInline(admin.TabularInline):
    model = ReferralChild
    extra = 0

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
	list_display = ("primary_carer_name", "postcode", "hscp_locality", "ward", "created_at")
	list_filter = ("hscp_locality", "ward", "srv_family_support", "srv_respite_sitting", "srv_respite_care", "srv_geezachance", "srv_kinship_care")
	search_fields = ("primary_carer_name", "referrer_name", "postcode")
	inlines = [ReferralChildInline]

@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
	list_display = ("label", "key", "order", "active")
	list_editable = ("order", "active")
	search_fields = ("label", "key")
	ordering = ("order", "label")

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
	list_display = ("name", "role_title", "order")
	list_editable = ("order",)
	search_fields = ("name", "role_title")
	ordering = ("order", "name")
