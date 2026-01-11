from urllib import request
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, Category, Bid, Comment, ListingForm


def index(request):
    return render(request, "auctions/index.html", context={
        "listings": AuctionListing.objects.all()
    })


def categories(request):
    return render(request, "auctions/categories.html", context={
        "categories": Category.objects.all()
    })


def category(request, category_name):
    matching = [category for category in Category.objects.all()
                if category.shortname == category_name]

    if not matching:
        return HttpResponseRedirect(reverse("categories"))
    category = matching[0]

    return render(request, "auctions/index.html", context={
        "listings": filter(lambda listing: listing.category == category, AuctionListing.objects.all()),
        "category_name": category.name
    })


def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", context={
                "form": form
            })
        
    return render(request, "auctions/create.html", context={
        "form": ListingForm()
    })


def listing(request, listing_id):

    listing = AuctionListing.objects.get(id=listing_id)
    is_watching = request.user.watchlist.all().filter(id=listing_id).exists()
    is_seller = listing.seller == request.user
    is_winner = listing.winning_bidder == request.user

    if request.method == "POST":
        # Handle tap of the add or remove from watchlist button
        if "watch" in request.POST:
            if is_watching:
                request.user.watchlist.remove(listing)
            else:
                request.user.watchlist.add(listing)
            request.user.save()

        # Handle bid submission
        elif "bid_amount" in request.POST:
            bid_amount = request.POST["bid_amount"]
            current_price = listing.current_price

            if float(bid_amount) > float(current_price):
                bid = Bid(bidder=request.user, listing=listing, amount=bid_amount)
                bid.save()

        # Handle close listing action
        elif "close" in request.POST and is_seller:
            listing.is_active = False
            listing.save()

        # Handle comment submission
        elif "comment" in request.POST:
            comment_content = request.POST["comment"]
            comment = Comment(author=request.user, listing=listing, content=comment_content)
            comment.save()
        
        # All actions redirect back to listing page
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))

    return render(request, "auctions/listing.html", context={
        "listing": listing,
        "is_watching": is_watching,
        "is_seller": is_seller,
        "is_winner": is_winner,
        "comments": listing.comments.all()
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def watchlist(request):
    return render(request, "auctions/index.html", context={
        "category_name": "Your Watchlist",
        "listings": request.user.watchlist.all()
    })
