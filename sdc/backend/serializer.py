from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import Product, Maker, RecipeQuery, Oven
from django.core.exceptions import ObjectDoesNotExist


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('qr', 'name', 'height', 'width', 'qr_at_height', 'qr_at_width')

class RecipeQuerySerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    oven = serializers.SlugRelatedField(queryset=Oven.objects.all(), slug_field='code')
    class Meta:
        model = RecipeQuery
        fields = ['image', 'oven',]