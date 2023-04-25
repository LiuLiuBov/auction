from audioop import maxpp
from pyexpat.errors import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Auction_listing, Category, Bid, WatchlistItem, Comment


def index(request):
    return render(request, "auctions/index.html",{
        "listings": Auction_listing.objects.filter(active = True)
    })

def closedlistings(request):
    return render(request, "auctions/index.html",{
        "listings": Auction_listing.objects.filter(active = False)
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

@login_required
def create_listing(request):
    if request.method == "POST":
        owner = request.user
        title = request.POST["title"]
        description = request.POST["description"]
        price = int(request.POST["price"])
        starting_bid = int(request.POST["starting_bid"])
        image = request.POST["image"]
        category_id = request.POST["category"]
        category = Category.objects.get(id=category_id)
        new_listing = Auction_listing(owner = owner, title = title, description = description, price = price, starting_bid = starting_bid, image = image, item_category = category)
        new_listing.save()
        return render(request, "auctions/index.html")

    return render(request, "auctions/create_listing.html",{
        "categories": Category.objects.all()
    })

def listing_page(request, title):
    error_message = None
    if request.user.is_authenticated:
      inWatchlist = False
      canClose = False
      isWinner = False
      uppercase_title = title.upper()
      listing = Auction_listing.objects.get(title=title)
      last_bid = Bid.objects.filter(item=listing).order_by('-sum').first()
      bid_count = Bid.objects.filter(item=listing).count()
      user = request.user
      if WatchlistItem.objects.filter(liker = user, liked = listing).exists():
          inWatchlist = True
      if listing.owner == user:
          canClose = True
      if listing.active == False and last_bid.bit_owner == request.user:
          isWinner = True
      comments = Comment.objects.filter(item = listing)
      comments_list = list(reversed(comments))
      return render(request, "auctions/listing_page.html",{
          "listing": listing,
          "bid_count": bid_count,
          "inWatchlist": inWatchlist,
          "canClose": canClose,
          "isWinner": isWinner,
          "comments": comments_list
      })
    else:
        return render(request, "auctions/login.html")

def place_bid(request, title):
    error_message = None # initialize the error message variable
    if request.method == "POST":
        if request.user.is_authenticated:
            listing = Auction_listing.objects.get(title=title)
            owner = request.user
            sum = int(request.POST["bid"])
           
            if ((sum == listing.price) or (sum < listing.price)):
               error_message = "Your bid must be higher than the current price."
            else:
               new_bid = Bid(sum=sum, item=listing, bit_owner=owner)
               new_bid.save()
               listing.price = new_bid.sum
               listing.save()
               return HttpResponseRedirect(reverse("listing_page", args=(listing.title,)))
        else:
            error_message = "You must be logged in to place a bid."
            return render(request, "auctions/login.html")
    else:
        listing = Auction_listing.objects.get(title=title)
        
    context = {
        "listing": listing,
        "error_message": error_message
    }
    return render(request, "auctions/listing_page.html", context)


def watchlist_add(request, title):
    item_to_save = Auction_listing.objects.get(title=title)
    liker = request.user
    if WatchlistItem.objects.filter(liker = liker, liked = item_to_save).exists():
        message = "The item is already in your watch list."
        return HttpResponseRedirect(reverse("listing_page", args=(item_to_save.title,)),{
            "message": message
        })
    else:
        created = WatchlistItem(liker = liker, liked = item_to_save)
        created.save()
        return HttpResponseRedirect(reverse("listing_page", args=(item_to_save.title,)))

def watchlist(request):
    user = request.user
    listings = WatchlistItem.objects.filter(liker = user)
    liked_items = [listing.liked for listing in listings]
    print(liked_items)
    return render(request, "auctions/watchlist.html",{
        "listings": liked_items
    })

def watchlist_delete(request, title):
    item_to_delete = Auction_listing.objects.get(title=title)
    liker = request.user
    WatchlistItem.objects.filter(liker = liker, liked = item_to_delete).delete()
    return HttpResponseRedirect(reverse("listing_page", args=(item_to_delete.title,)))

def make_inactive(request, title):
    current_user = request.user
    item_to_delete = Auction_listing.objects.get(title=title)
    item_to_delete.active = False
    item_to_delete.save()
    return HttpResponseRedirect(reverse("index"))

def comment(request, title):
    text = request.POST["comment"]
    item = Auction_listing.objects.get(title=title)
    new_comment = Comment(commentator = request.user, item = item, text = text)
    new_comment.save()
    return HttpResponseRedirect(reverse("listing_page", args=(item.title,)))


#def categories(request):
    allcategories = Category.objects.all
    pickedcategory = pick_category(request)
    category = Category.objects.get(title = pickedcategory)
    print(category)
    listings = Auction_listing.objects.filter(item_category = category)
    print(listings)
    return render(request, 'auctions/categories.html', {
        'categories': allcategories,
        'listings': listings
        })

#def pick_category(request):
    category_title = request.POST.get('category')
    category = Category.objects.get(title=category_title)
    return category

def category_list(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'auctions/category_list.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = Auction_listing.objects.filter(item_category=category, active=True)
    print(category)
    print(listings)
    context = {
        'category': category,
        'listings': listings
    }
    return render(request, 'auctions/category_detail.html', context)








