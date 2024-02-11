from django.contrib import admin

from .models import User, Auction_listing,Bid, Comment, Category, WatchlistItem

admin.site.register(User)
admin.site.register(Auction_listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(WatchlistItem)
