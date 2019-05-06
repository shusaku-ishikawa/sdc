from django.shortcuts import render
import django_filters
from rest_framework import viewsets, filters
from rest_framework.response import Response
from .models import *
from .serializer import *
from rest_framework.decorators import action
from .modules.qr_extractor import *
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class RecipeQueryErrorCode:
    QR_NOT_FOUND = {'code': 100, 'message': 'QRコードを検出できませんでした'}
    MULTIPLE_PRODUCTS_IN_CHANNEL = {'code': 101, 'message': '同一チャネルに複数商品が存在します'}
    INVALID_PARAMETERS = {'code': 102, 'message': 'パラメータが不正です'}
    INTERNAL_ERROR = {'code': 200, 'message': '内部エラーが発生しました'}

class RecipeQueryViewSet(viewsets.ModelViewSet):
    queryset = RecipeQuery.objects.all()
    serializer_class = RecipeQuerySerializer
    
    

    def create(self, request):
        # POST   :  /api/recipes/
        serializer = RecipeQuerySerializer(data = request.data)
        if serializer.is_valid():
            obj = serializer.save()
            cv2_image = cv2.imread(obj.image.path)
            height_in_pix, width_in_pix, _ = cv2_image.shape
            pix_per_mm_x = width_in_pix / obj.oven.floor_width_in_mm
            pix_per_mm_y = height_in_pix / obj.oven.floor_height_in_mm

            extractor = QRExtractor(cv2_image, pix_per_mm_x, pix_per_mm_y)

            # QRコードを検知できなかった場合
            if not extractor.extract():
                return Response(status = 200, data = {'status': 'error', 'data': RecipeQueryErrorCode.QR_NOT_FOUND})
            
            # 3か所のスクエアを描画
            extractor.draw_three_square()
            
            # 商品を検知
            barcodes, coodinates = extractor.find_products()
            
            channels = OvenChannelSerializer(data = obj.oven.channels.all(), many = True)
            
            response = {
                'status': 'success',
            }
            data = {
                'requestId': str(obj.pk)
            }
            channel_for_response_list = []
            for channel in obj.oven.channels.all():
                
                channel_for_response = {
                    'id': channel.seq
                } 
                channel_coord = extractor.draw_channel(channel)
                for barcode in barcodes:
                    if Polygon(coodinates[0]).intersection(Polygon(channel_coord)).area > 0:
                        if 'product_found' in channel_for_response:
                            print('単一チャネルに複数商品が含まれています')
                            return
                        else:
                            channel_for_response['product_found'] = barcode.data.decode('utf-8')
                
                        try:
                            p = Product.objects.get(qr = channel_for_response['product_found'])
                        except ObjectDoesNotExist:
                            return Response(status=200, data={'status': 'error', 'data': RecipeQueryErrorCode.INTERNAL_ERROR})
                        
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
                        
                        channel_for_response['hasQr'] = True
                        channel_for_response['product'] = dict_product
                        channel_for_response['recipes'] = dict_list_recipe
                        channel_for_response_list.append(channel_for_response)

            data['channels'] = channel_for_response_list
            response['data'] = data
            cv2.imwrite('output.png', extractor.draw)
          

            return Response(status=200, data=response)
        else:
            print(str(serializer.errors))
            return Response(status=200, data={'status': 'error', 'data': RecipeQueryErrorCode.INVALID_PARAMETERS})



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
            print(str(serializer.errors))
            return Response(status = 200, data={'status': 'error', 'data': MyDecoder.INVALID_PARAMETERS})