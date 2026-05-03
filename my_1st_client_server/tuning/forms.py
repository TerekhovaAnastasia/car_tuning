from django import forms
from .models import Order, Car
import json


class OrderForm(forms.ModelForm):
    vin_id = forms.CharField(
        max_length=20,
        required=False,
        label='VIN автомобиля',
        widget=forms.TextInput(attrs={
            'placeholder': 'Например: XTA210990Y2766389',
        })
    )

    class Meta:
        model = Order
        fields = ['user', 'car', 'base_price', 'tuning_options', 'total_price']
        widgets = {
            'tuning_options': forms.HiddenInput(),
            'total_price': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['car'].required = False
        self.fields['base_price'].required = False
        self.fields['tuning_options'].required = False
        self.fields['total_price'].required = False

    def clean_tuning_options(self):
        data = self.cleaned_data.get('tuning_options')
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                data = []
        return data if data else []

    def clean_total_price(self):
        data = self.cleaned_data.get('total_price')
        try:
            return int(data) if data else 0
        except:
            return 0

    def clean(self):
        cleaned_data = super().clean()
        vin = cleaned_data.get('vin_id')
        car = cleaned_data.get('car')

        if not vin and not car:
            raise forms.ValidationError('Введите VIN или выберите автомобиль из списка')

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        vin = self.cleaned_data.get('vin_id')
        car = self.cleaned_data.get('car')

        # Если введён VIN — ищем или создаём авто
        if vin:
            car, created = Car.objects.get_or_create(
                vin_id=vin,
                defaults={'base_price': 500000, 'description': 'Новый автомобиль'}
            )

        if car:
            order.car = car
            if not order.base_price:
                order.base_price = car.base_price

        if not order.base_price:
            order.base_price = 500000

        order.tuning_options = self.cleaned_data.get('tuning_options', [])
        order.total_price = self.cleaned_data.get('total_price', 0)

        if commit:
            order.save()
        return order