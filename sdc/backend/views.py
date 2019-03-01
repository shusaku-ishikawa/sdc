from django.shortcuts import render
import django_filters
from rest_framework import viewsets, filters
from rest_framework.response import Response
from .models import Product, RecipeQuery
from .serializer import ProductSerializer, RecipeQuerySerializer
from rest_framework.decorators import action
from . import qr_decoder

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class RecipeQueryViewSet(viewsets.ModelViewSet):
    queryset = RecipeQuery.objects.all()
    serializer_class = RecipeQuerySerializer
    
    def create(self, request):
        # POST   :  /api/users/
        serializer = RecipeQuerySerializer(data = request.data)
        if serializer.is_valid():
            obj = serializer.save()
            ret = qr_decoder.decode_code(obj.image.path)
            return Response(status=200, data=ret)

        else:
            return Response(status=500, data={'error': True})
