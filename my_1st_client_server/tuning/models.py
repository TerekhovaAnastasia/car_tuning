from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    vin_id = models.CharField(
        max_length=20,
        primary_key=True,
        unique=True,
        editable=False
    )
    base_price = models.IntegerField(default=500000)
    description = models.CharField(max_length=255, default='базовая комплектация')

    def __str__(self):
        return f"Автомобиль {self.vin_id}"

class TuningOption(models.Model):
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='tuning_options'
    )
    type = models.CharField(max_length=50)
    price_multiplier = models.FloatField()
    price_addition = models.IntegerField(default=0)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"Тюнинг {self.type} для {self.car.vin_id}"

class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    base_price = models.PositiveIntegerField()
    tuning_options = models.JSONField()
    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.id} от {self.user.username}"
