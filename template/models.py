from django.db import models
from django.contrib.auth.models import User


class MembershipPlan(models.Model):
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=60)
    name = models.CharField(max_length=100)
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.CharField(max_length=255)
    features = models.TextField(help_text="Enter one feature per line.")
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    @property
    def feature_list(self):
        return [feature for feature in self.features.splitlines() if feature.strip()]

    def __str__(self):
        return self.name


class PlanEnrollment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="plan_enrollment")
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name="enrollments")
    selected_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.plan.name}"


class ContactEnquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"
