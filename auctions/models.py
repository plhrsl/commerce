
from email.policy import default
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"


class Listing(models.Model):
    CATEGORIES = (
        ("1", "Apparel and accessories"),
        ("2", "Auto and parts"),
        ("3", "Book, music and video"),
        ("4", "Computer, technology and eletronics"),
        ("5", "Furniture"),
        ("6", "Health, personal care and beauty"),
        ("7", "Office"),
        ("8", "Toys and hobby"),
        ("9", "Other")
    )
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, related_name="listings", default=0)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=256)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    category = models.CharField(
        max_length=256, choices=CATEGORIES, default="9")
    image_url = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    watchers = models.ManyToManyField(
        User, blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.id}: {self.title}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.current_bid = self.starting_bid
        super(Listing, self).save(*args, **kwargs)


class Bid(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE)

    def __str__(self):
        return f"${self.bid} by {self.bidder} on {self.listing}"


class Comment(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments", default=None)
    content = models.TextField(max_length=256)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"Comment {self.id} by {self.user}"
