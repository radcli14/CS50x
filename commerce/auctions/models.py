from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm, TextInput, Textarea, NumberInput, Select

class User(AbstractUser):
    watchlist = models.ManyToManyField('AuctionListing', blank=True, related_name="watched_by")


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name
    
    @property
    def shortname(self):
        return self.name.replace(" ", "_").lower()


class AuctionListing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.seller.username} starting at ${self.starting_bid}"
    
    @property
    def current_price(self):
        return self.highest_bid.amount if self.highest_bid else self.starting_bid

    @property
    def highest_bid(self):
        return self.bids.order_by('-amount').first()
    
    @property
    def winning_bidder(self):
        return self.highest_bid.bidder if self.highest_bid else None


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"${self.amount} by {self.bidder.username} on {self.listing.title}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()

    def __str__(self):
        return f"Comment by {self.author.username} on {self.listing.title}: {self.content[:20]}..."
    

class ListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'image_url', 'category', 'starting_bid']
        widgets = {
            "title": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Provide a short name for your listing"
                }),
            "description": Textarea(attrs={
                "class": "form-control",
                "style": "max-height: 96px;",
                "placeholder": "Write a few sentences about your item"
                }),
            "image_url": TextInput(attrs={
                "class": "form-control",
                "placeholder": "Supply a link to an image (optional)"
                }),
            "category": Select(attrs={
                "class": "form-control",
                "style": "width: 256px;"
            }),
            "starting_bid": NumberInput(attrs={
                "class": "form-control",
                "style": "width: 256px;",
                "placeholder": "Minimum price (USD)",
                "min": "0",
                "step": "0.01"
                }),
        }
