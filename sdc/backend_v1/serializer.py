from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from core.models import *
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

class HistoryByChannelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source = 'channel')
    recipeApplied = serializers.SlugRelatedField(source = 'recipe', queryset=Recipe.objects.all(), slug_field='pk')
    surfTempBefore = serializers.FloatField(source = 'surf_temp_before')
    surfTempAfter = serializers.FloatField(source = 'surf_temp_after')
    secondsTaken = serializers.IntegerField(source = 'seconds_taken')
    class Meta:
        model = HistoryByChannel
        fields = ['id', 'recipeApplied','surfTempBefore', 'surfTempAfter', 'secondsTaken']

class HistorySerializer(serializers.ModelSerializer):
    unixtimestamp = serializers.IntegerField(source = 'cooked_at')
    requestId = serializers.SlugRelatedField(source = 'corresponding_query', queryset=RecipeQuery.objects.all(), slug_field='pk')
    channels = HistoryByChannelSerializer(many = True, write_only = True)
    powerConsumed = serializers.FloatField(source = 'power_consumed')
    #otherInfo = serializers.CharField(source = 'other_info')
    class Meta:
        model = History
        fields = ['unixtimestamp', 'requestId','channels', 'powerConsumed', 'otherInfo']
    
    def create(self, validated_data):
        channels = validated_data.pop('channels')
        history = History.objects.create(**validated_data)

        for ch in channels:
            channel = HistoryByChannel(**ch)
            channel.history = history
            channel.save()
        return history
