from django import forms
from django.forms import Form, ModelForm

from auctions.models import Listing


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description',
                  'starting_bid', 'category', 'image_url']
        labels = {
            'starting_bid': "Starting Bid",
            'image_url': "Image URL"
        }
