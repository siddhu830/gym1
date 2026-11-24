from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.views.decorators.http import require_POST
from .models import ContactEnquiry, MembershipPlan, PlanEnrollment


def home(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()
        if not name or not email:
            messages.error(request, "Please provide your name and email address.")
        elif not _is_valid_email(email):
            messages.error(request, "Please provide a valid email address.")
        else:
            ContactEnquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=message,
            )
            messages.success(request, "Thanks! Your enquiry has been received.")
        return redirect("home")
    plans = MembershipPlan.objects.filter(active=True)
    return render(request, "template/home.html", {"plans": plans})


def _is_valid_email(email):
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def classes(request):
    return render(request, "template/class.html")


def trainers(request):
    return render(request, "template/trainers.html")


def _activate_pending_plan(request, user):
    slug = request.session.pop("pending_plan_slug", None)
    if not slug:
        return False
    try:
        plan = MembershipPlan.objects.get(slug=slug, active=True)
    except MembershipPlan.DoesNotExist:
        messages.error(request, "That membership plan is no longer available.")
        return False
    PlanEnrollment.objects.update_or_create(user=user, defaults={"plan": plan})
    messages.success(request, f"You selected the {plan.name} plan.")
    return True


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        errors = []

        if not username or not email or not password1:
            errors.append("Please complete all required fields.")
        if email and not _is_valid_email(email):
            errors.append("Enter a valid email address.")
        if password1 != password2:
            errors.append("The passwords do not match.")
        if email and User.objects.filter(email__iexact=email).exists():
            errors.append("An account with this email already exists.")
        if username and User.objects.filter(username__iexact=username).exists():
            errors.append("That username is already taken.")
        if password1:
            try:
                validate_password(password1, user=User(username=username, email=email))
            except ValidationError as exc:
                errors.extend(exc.messages)

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "template/signup.html", status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
        )
        login(request, user)
        if _activate_pending_plan(request, user):
            return redirect(f"{reverse('home')}#plans")
        return redirect("home")
    return render(request, "template/signup.html")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        users = User.objects.filter(email__iexact=email)
        if users.count() != 1:
            messages.error(request, "Invalid email or password.")
        else:
            user = authenticate(
                request,
                username=users.first().username,
                password=password,
            )
            if user is None:
                messages.error(request, "Invalid email or password.")
            else:
                login(request, user)
                if not request.POST.get("remember"):
                    request.session.set_expiry(0)
                if _activate_pending_plan(request, user):
                    return redirect(f"{reverse('home')}#plans")
                return redirect("home")
    return render(request, "template/login.html")


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect("home")


@require_POST
def join_plan(request, slug):
    try:
        plan = MembershipPlan.objects.get(slug=slug, active=True)
    except MembershipPlan.DoesNotExist as exc:
        raise Http404("Membership plan not found.") from exc

    if not request.user.is_authenticated:
        request.session["pending_plan_slug"] = plan.slug
        return redirect("signup")

    PlanEnrollment.objects.update_or_create(user=request.user, defaults={"plan": plan})
    messages.success(request, f"You selected the {plan.name} plan.")
    return redirect(f"{reverse('home')}#plans")
