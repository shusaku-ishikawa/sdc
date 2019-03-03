from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from .models import Product, Maker, RecipeQuery, Oven
from django.core.exceptions import ObjectDoesNotExist


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('qr', 'name', 'height', 'width', 'qr_at_height', 'qr_at_width')


class RecipeQuerySerializer(serializers.Serializer):
    image = Base64ImageField()
    ovenId = serializers.CharField(max_length = 255)

    def create(self, validated_data):
        image = validated_data.pop('image')
        oven = Oven.objects.get(code = validated_data.pop('ovenId'))
        return RecipeQuery.objects.create(image = image,oven = oven)

    def validate_oven_code(self, oven_code):
        
        oven = Oven.objects.get(code = oven_code)
            
        return oven_code
        