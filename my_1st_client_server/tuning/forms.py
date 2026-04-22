from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'user',
            'car',
            'base_price',
            'tuning_options',
            'total_price'
        ]
