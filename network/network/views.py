from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import json

from .models import User, Post


def index(request):
    """Main page, displaying 'New Post' field and 'All Posts'"""
    # If this is an edit to an existing post, handle it, the basic HTTP response will render in a hidden iFrame
    edit_response = edit_post(request)
    if edit_response is not None:
        return edit_response
    
    # If a user posted, update the database, and redirect to index
    if request.method == "POST":
        content = request.POST["content"]
        author = request.user
        post = Post(author=author, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    
    # Show the index page with all posts
    posts = Post.objects.all().order_by("-timestamp")
    return render(request, "network/index.html", {
        "page": get_post_page(request, posts)
    })


def edit_post(request):
    """Endpoint to edit a post's content, returns an HTTPResponse if a post was found, otherwise None."""
    if request.method == "POST":
        # If there is a post_id field in the post data, then it came from the edit post form
        post_id = request.POST.get("post_id")
        if post_id is None:
            return None
        
        # Try to get the post being edited
        try:
            post_id = int(post_id)
            post = Post.objects.get(id=post_id)
        except (Post.DoesNotExist, ValueError):
            return HttpResponse("Post not found.", status=404)

        # Verify that the user is the author of this post (security check)
        if post.author != request.user:
            return HttpResponse("You do not have permission to edit this post.", status=403)

        # Update the post content
        post.content = request.POST.get("content", "")
        post.save()

        return HttpResponse(f"Post {post_id} successfully edited.", status=200)
    else:
        # No post ID was provided, so this is not an edit post request
        return None


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


def get_post_page(request, posts):
    """Helper function to paginate posts and return the appropriate page."""
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    post_page = paginator.get_page(page_number)
    return post_page


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
    # If this is an edit to an existing post, handle it, the basic HTTP response will render in a hidden iFrame
    edit_response = edit_post(request)
    if edit_response is not None:
        return edit_response
    
    # Check that the user exists, render an error if not found
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, "network/profile.html", {
            "message": "User does not exist."
        })

    # Render the user's profile page
    posts = user.posts.all().order_by("-timestamp")
    return render(request, "network/profile.html", {
        "profile_user": user,
        "page": get_post_page(request, posts)
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
