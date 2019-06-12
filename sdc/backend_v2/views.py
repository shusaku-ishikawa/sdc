from django.shortcuts import render
import django_filters
from rest_framework import viewsets, filters
from rest_framework.response import Response
from core.models import *
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
        
        # パラメータチェック
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
            # QR解析失敗時
            if len(barcodes) == 0:
                return Response(status = 200, data = {'status': 'error', 'data': RecipeQueryErrorCode.QR_NOT_FOUND})

            #channels = OvenChannelSerializer(data = obj.oven.channels.all(), many = True)
            
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
                shapes = []
                for x, y in channel_coord:
                    shapes.append({ 'x': x, 'y': y })
                channel_for_response['shape'] = shapes

                
                for qr_data in barcodes:
                    
                    # 一定面積被っている場合
                    if Polygon(coodinates[0]).intersection(Polygon(channel_coord)).area > settings.MIN_AREA_TO_RECONGNIZE:
                        # 既に別の商品がそのチャネルに存在する場合
                        if 'product_found' in channel_for_response and channel_for_response['product_found'] != qr_data:
                            return Response(status = 200, data = {'status': 'error', 'data': RecipeQueryErrorCode.MULTIPLE_PRODUCTS_IN_CHANNEL})
                        else:
                            # その商品がサーバで登録されている場合
                            try:
                                channel_for_response['product_found'] = qr_data
                                p = Product.objects.get(qr = channel_for_response['product_found'])
                                
                            except ObjectDoesNotExist:
                                continue

                        recipes = Recipe.objects.filter(product = p)
                      
                        serialized_product = ProductSerializer(p, many = False).data
                        serialized_recipes = RecipeSerializer(recipes, many = True).data


                        channel_for_response['product'] = serialized_product
                        channel_for_response['recipes'] = serialized_recipes
                        
                channel_for_response_list.append(channel_for_response)

            product_for_response_list = []
            for product_coords in coodinates:
                p = []
                for x, y in product_coords:
                    p.append({ 'x':x, 'y': y })
                product_for_response_list.append({'shape': p})
            
            data['channels'] = channel_for_response_list
            data['products'] = product_for_response_list

            response['data'] = data
            cv2.imwrite(obj.image.path + '_processed.png', extractor.draw)
          

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
            return Response(status = 200, data={'status': 'error', 'data': RecipeQueryErrorCode.INVALID_PARAMETERS})