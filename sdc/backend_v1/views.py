from django.shortcuts import render
import django_filters
from rest_framework import viewsets, filters
from rest_framework.response import Response
from core.models import *
from .serializer import ProductSerializer, RecipeQuerySerializer, HistorySerializer
from rest_framework.decorators import action
from .qr_decoder import MyDecoder
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class RecipeQueryViewSet(viewsets.ModelViewSet):
    queryset = RecipeQuery.objects.all()
    serializer_class = RecipeQuerySerializer
    
    def create(self, request):
        # POST   :  /api/recipes/
        serializer = RecipeQuerySerializer(data = request.data)
        if serializer.is_valid():
            obj = serializer.save()

            decoder = MyDecoder(obj.image.path, obj.oven)
            channels_with_qr = decoder.decode(settings.INVERT_IMAGE_WHEN_DECODE)

            if 'code' in channels_with_qr:
                return Response(status = 200, data = {'status': 'error', 'data': channels_with_qr})

            response = {
                'status': 'success',
            }
            data = {
                'requestId': str(obj.pk)
            }
            
            for channel in channels_with_qr:
                if 'qr' in channel.keys():
                    print(channel['qr'])
                    try:
                        p = Product.objects.get(qr = channel['qr'])
                    except ObjectDoesNotExist:
                        return Response(status=200, data={'status': 'error', 'data': MyDecoder.INTERNAL_ERROR})
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
                    
                    channel['hasQr'] = True
                    channel['product'] = dict_product
                    channel['recipes'] = dict_list_recipe
                    del channel['qr']
                else:
                    channel['hasQr'] = False

            data['channels'] = channels_with_qr
            response['data'] = data

            print(data)
            return Response(status=200, data=response)
        else:
            print(str(serializer.errors))
            return Response(status=200, data={'status': 'error', 'data': MyDecoder.INVALID_PARAMETERS})



class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all()
    serializer_class = HistorySerializer

    # POST /api/history/
    def create(self, request):
        serializer = HistorySerializer(data = request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(status = 200, data={'status': 'success'})
        else:
            return Response(status = 200, data={'status': 'error', 'data': MyDecoder.INVALID_PARAMETERS})