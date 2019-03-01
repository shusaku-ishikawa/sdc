from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import Product, Maker, RecipeQuery


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('qr', 'name', 'height', 'width', 'qr_at_height', 'qr_at_width')


class RecipeQuerySerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    class Meta:
        model = RecipeQuery
        fields = ('image', 'channels')
    def create(self, validated_data):
        image = validated_data.pop('image')
        channels = validated_data.pop('channels')
        return RecipeQuery.objects.create(image = image,channels = channels)
  