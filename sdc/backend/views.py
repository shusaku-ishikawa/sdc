from django.shortcuts import render
import django_filters
from rest_framework import viewsets, filters
from rest_framework.response import Response
from .models import Product, RecipeQuery, Recipe
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

            channels_with_qr = qr_decoder.decode_qrcode(obj.image.path, obj.oven)
            response = {
                'status': 'success',
            }
            data = {
                'requestId': str(obj.pk)
            }
            print(channels_with_qr)
            for channel in channels_with_qr:
                if 'qr' in channel.keys():
                    print(channel['qr'])
                    try:
                        p = Product.objects.get(qr = channel['qr'].decode('utf-8'))
                    except Product.DoesNotExist:
                        return Response(status=200, data={'status': 'error', 'code': 200})
                    recipes = Recipe.objects.filter(product = p)

                    dict_product = {
                        'name': p.name,
                        'manufacturer': p.manufacturer,
                        'seller': p.seller,
                        'ingredients': p.ingredients,
                        'allergens': p.allergens,
                        'calory': p.calory,
                        'otherInfo': p.other_info
                    }
                    dict_list_recipe = []
                    for r in recipes:
                        dic = {
                            'id': str(r.pk),
                            'name': r.name,
                            'recipe': r.recipe
                        }
                        dict_list_recipe.append(dic)
                    
                    channel['product'] = dict_product
                    channel['recipes'] = dict_list_recipe
                    del channel['qr']

            data['channels'] = channels_with_qr
            response['data'] = data

            print(data)
            return Response(status=200, data=response)
        else:
            print(str(serializer.errors))
            return Response(status=200, data={'status': 'error', 'code': 200})
