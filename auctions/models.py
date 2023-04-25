from xml.dom import ValidationErr
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import SuspiciousOperation


class User(AbstractUser):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

class Category(models.Model):
    title = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.title}"

class Auction_listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    title = models.CharField(max_length=64)
    price = models.IntegerField()
    description = models.CharField(max_length=1000)
    starting_bid = models.IntegerField()
    image = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)
    item_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="item_category", default='', null=True)
    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    sum = models.IntegerField()
    item = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name="item")
    bit_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder", default='')

    def clean(self):
        if self.sum <= self.item.price:
            raise SuspiciousOperation("Bid must be greater than the item price.")

class Comment(models.Model):
    commentator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentator")
    item = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name="commented_item")
    text = models.CharField(max_length=1000)
    def __str__(self):
        return f"{self.text}"

class WatchlistItem(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liker")
    liked = models.ForeignKey(Auction_listing, on_delete=models.CASCADE, related_name="liked")

