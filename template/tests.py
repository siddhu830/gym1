from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import ContactEnquiry, MembershipPlan, PlanEnrollment


class FitPlanViewTests(TestCase):
    def test_home_and_classes_pages_render(self):
        home_response = self.client.get(reverse("home"))
        classes_response = self.client.get(reverse("classes"))
        trainers_response = self.client.get(reverse("trainers"))
        login_response = self.client.get(reverse("login"))
        signup_response = self.client.get(reverse("signup"))

        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, "/static/template/css/style.")
        self.assertContains(home_response, "Essential")
        self.assertEqual(classes_response.status_code, 200)
        self.assertContains(classes_response, "Strength Training")
        self.assertEqual(trainers_response.status_code, 200)
        self.assertEqual(trainers_response.content.decode().count('class="trainer-card"'), 5)
        self.assertEqual(login_response.status_code, 200)
        self.assertContains(login_response, 'class="auth-brand"')
        self.assertEqual(signup_response.status_code, 200)
        self.assertContains(signup_response, 'class="auth-brand"')

    def test_nav_shows_login_for_guests_and_logout_for_users(self):
        guest_response = self.client.get(reverse("home"))
        self.assertContains(guest_response, 'href="/login/">Login</a>')

        user = User.objects.create_user(username="fituser", password="safe-password-47")
        self.client.force_login(user)
        member_response = self.client.get(reverse("home"))
        self.assertContains(member_response, ">Logout</button>")
        self.assertNotContains(member_response, 'href="/login/">Login</a>')
        self.assertContains(member_response, 'href="/#plans">Join Now</a>')

    def test_guest_plan_selection_completes_after_signup(self):
        plan = MembershipPlan.objects.get(slug="plus")
        response = self.client.post(reverse("join_plan", args=[plan.slug]))

        self.assertRedirects(response, reverse("signup"))
        response = self.client.post(
            reverse("signup"),
            {
                "username": "planuser",
                "email": "planuser@example.com",
                "password1": "a-very-strong-password-47",
                "password2": "a-very-strong-password-47",
            },
        )

        self.assertRedirects(response, f"{reverse('home')}#plans")
        self.assertEqual(PlanEnrollment.objects.get().plan, plan)

    def test_member_plan_selection_is_saved_and_updated(self):
        user = User.objects.create_user(username="fituser", password="safe-password-47")
        self.client.force_login(user)
        plus = MembershipPlan.objects.get(slug="plus")
        premium = MembershipPlan.objects.get(slug="premium")

        self.client.post(reverse("join_plan", args=[plus.slug]))
        self.client.post(reverse("join_plan", args=[premium.slug]))

        self.assertEqual(PlanEnrollment.objects.count(), 1)
        self.assertEqual(PlanEnrollment.objects.get(user=user).plan, premium)

    def test_signup_creates_user_and_logs_them_in(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "fituser",
                "email": "fituser@example.com",
                "password1": "a-very-strong-password-47",
                "password2": "a-very-strong-password-47",
            },
        )

        self.assertRedirects(response, reverse("home"))
        user = User.objects.get(username="fituser")
        self.assertTrue(user.check_password("a-very-strong-password-47"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "fituser",
                "email": "fituser@example.com",
                "password1": "a-very-strong-password-47",
                "password2": "different-password-47",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="fituser").exists())

    def test_login_authenticates_by_email(self):
        User.objects.create_user(
            username="fituser",
            email="fituser@example.com",
            password="a-very-strong-password-47",
        )

        response = self.client.post(
            reverse("login"),
            {"email": "FITUSER@example.com", "password": "a-very-strong-password-47"},
        )

        self.assertRedirects(response, reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_contact_form_saves_enquiry(self):
        response = self.client.post(
            reverse("home"),
            {
                "name": "Fit User",
                "email": "fituser@example.com",
                "phone": "1234567890",
                "message": "I want to learn about memberships.",
            },
        )

        self.assertRedirects(response, reverse("home"))
        enquiry = ContactEnquiry.objects.get()
        self.assertEqual(enquiry.name, "Fit User")
        self.assertEqual(enquiry.message, "I want to learn about memberships.")

    def test_contact_form_rejects_invalid_email(self):
        self.client.post(
            reverse("home"),
            {"name": "Fit User", "email": "not-an-email"},
        )

        self.assertFalse(ContactEnquiry.objects.exists())
