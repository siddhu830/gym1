from django.contrib import admin
from .models import ContactEnquiry, MembershipPlan, PlanEnrollment


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "monthly_price", "active", "featured", "position")
    list_editable = ("active", "featured", "position")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "category")


@admin.register(PlanEnrollment)
class PlanEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "selected_at")
    list_select_related = ("user", "plan")
    search_fields = ("user__username", "user__email", "plan__name")
    readonly_fields = ("selected_at",)


@admin.register(ContactEnquiry)
class ContactEnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone")
    readonly_fields = ("created_at",)
