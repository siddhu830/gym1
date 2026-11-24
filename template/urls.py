from django.urls import path
from template import views

urlpatterns = [
    path("", views.home, name="home"),
    path("classes/", views.classes, name="classes"),
    path("trainers/", views.trainers, name="trainers"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("plans/<slug:slug>/join/", views.join_plan, name="join_plan"),
]