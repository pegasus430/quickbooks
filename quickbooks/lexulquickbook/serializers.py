from rest_framework import serializers
from .models import Customer, Qwc


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields =  '__all__'

class QwcSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qwc
        fields =  ["username","qbtype","run_every_minutes"]