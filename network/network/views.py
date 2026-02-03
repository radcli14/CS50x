from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import json

from .models import User, Post


def index(request):
    """Main pain, displaying 'New Post' field and 'All Posts'"""
    # If a user posted, update the database, and redirect to index
    if request.method == "POST":
        content = request.POST["content"]
        author = request.user
        post = Post(author=author, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    
    # Show the index page with all posts
    posts = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    post_page = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "page": post_page
    })


def follow_user(request, username):
    """Endpoint to follow or unfollow a user."""
    if request.method == "GET":
        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse("User not found.", status=404)

        # The response, which JS will use to update the front end
        response = {}

        # Follow or unfollow, depending on prior state
        user = request.user
        if user_to_follow in user.follows.all():
            user.follows.remove(user_to_follow)
            response["status"] = "unfollowed"
        else:
            user.follows.add(user_to_follow)
            response["status"] = "followed"

        response["follower_count"] = user_to_follow.followers.count()
        return HttpResponse(json.dumps(response), status=200)
    else:
        return HttpResponse("Invalid request method.", status=400)


def like_post(request, post_id):
    """Entpoint to like or unlike a post."""
    if request.method == "POST":
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return HttpResponse("Post not found.", status=404)

        user = request.user
        if user in post.liked_by.all():
            post.liked_by.remove(user)
        else:
            post.liked_by.add(user)

        return HttpResponse("Successfully liked/unliked post.", status=200)
    else:
        return HttpResponse("Invalid request method.", status=400)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def profile(request, username):
    """View for a user's profile page."""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "network/profile.html", {
            "message": "User does not exist."
        })

    return render(request, "network/profile.html", {
        "profile_user": user,
        "posts": user.posts.all().order_by("-timestamp")
    })


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
