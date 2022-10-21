
from xml.etree.ElementTree import Comment
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from auctions.forms import ListingForm

from .models import Bid, Comment, Listing, User


def index(request):
    return render(request, "auctions/index.html", {
        "active_listings":  Listing.objects.filter(active=True)
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


@login_required(login_url='login')
def create(request):

    # If it is a post request, checks if the form is valid, create a new listing and redirects to the listing page
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing_obj = form.save(commit=False)
            listing_obj.user = request.user
            listing_obj.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_obj.id,)))

    # Renders the listing creation form
    return render(request, "auctions/create.html", {
        "form": ListingForm()
    })


def listing(request, listing_id, message=None):
    try:
        listing_obj = Listing.objects.get(pk=listing_id)
        bids = listing_obj.bids.all()

        # Gets how many bids were placed on the listing
        bid_count = bids.count()

        # Checks if the current bid - if any - is from user - if authenticated
        current_bid_is_from_user = bids.get(
            bid=listing_obj.current_bid
        ).bidder == request.user if request.user.is_authenticated and bid_count > 0 else False

        # Checks if the listing is on the user's - if authenticated - watchlist
        is_watching = "checked" if request.user.is_authenticated and listing_obj in request.user.watchlist.all() else ""

        # Renders the listing page
        return render(request, "auctions/listing.html", {
            "listing": listing_obj,
            "category": dict(Listing.CATEGORIES)[listing_obj.category],
            "comments": listing_obj.comments.all(),
            "message": message,
            "bid_count": bid_count,
            "current_bid_is_from_user": current_bid_is_from_user,
            "is_watching": is_watching
        })
    except:
        return index(request)


@login_required(login_url='login')
def bid(request, listing_id):
    message = None
    listing_obj = Listing.objects.get(pk=listing_id)

    # Checks if the new bid's value is valid
    if not request.POST["bid"] or float(request.POST["bid"]) <= listing_obj.current_bid:
        message = "Your bid must be higher than the current bid!"
    else:

        # Places new bid from the authenticated user
        listing_obj.current_bid = float(request.POST["bid"])
        listing_obj.save()
        bid = Bid.objects.create(
            bid=float(request.POST["bid"]), listing=listing_obj, bidder=request.user)
        bid.save()
        message = "Successful bid!"

    # Redirects to the listing page
    return listing(request, listing_id, message)


@login_required(login_url='login')
def comment(request, listing_id):
    message = None

    # Checks if there's any content for the comment
    if not request.POST["content"]:
        message = "Provide some content for the comment!"
    else:

        # Creates new comment from the authenticated user
        comment = Comment.objects.create(user=request.user, listing=Listing.objects.get(
            pk=listing_id), content=request.POST["content"])
        comment.save()

    # Redirects to the listing page
    return listing(request, listing_id, message)


@login_required(login_url='login')
def close(request, listing_id):

    # Inactivates the listing
    listing_obj = Listing.objects.get(pk=listing_id)
    listing_obj.active = False
    listing_obj.save()

    # Redirects to the listing page
    return listing(request, listing_id)


@login_required(login_url='login')
def watch(request, listing_id):
    listing_obj = Listing.objects.get(pk=listing_id)

    # Checks if user is checking or unchecking the "watch" checkbox
    if request.POST.get("watch", False):
        listing_obj.watchers.add(request.user)
    else:
        listing_obj.watchers.remove(request.user)
    listing_obj.save()

    # Redirects to the listing page
    return listing(request, listing_id)


@login_required(login_url='login')
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": Listing.objects.filter(watchers=request.user)
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Listing.CATEGORIES
    })


def category(request, category):
    return render(request, "auctions/index.html", {
        "active_listings":  Listing.objects.filter(active=True, category=category),
        "category": dict(Listing.CATEGORIES)[category]
    })


def user(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, "auctions/index.html", {
        "active_listings":  Listing.objects.filter(active=True, user=user),
        "username": user.username
    })


@login_required(login_url='login')
def me(request):
    return render(request, "auctions/me.html", {
        "listings": Listing.objects.filter(user=request.user),
        "bids": reversed(Bid.objects.filter(bidder=request.user))
    })
