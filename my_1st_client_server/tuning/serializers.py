from rest_framework import serializers
from .models import Car, TuningOption

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class TuningOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TuningOption
        fields = '__all__'
