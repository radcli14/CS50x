
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("follow/<str:username>", views.follow_user, name="follow_user"),
    path("following", views.following, name="following"),
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("register", views.register, name="register")
]
