from pyzbar import pyzbar
from PIL import Image, ImageDraw
import cv2
import numpy as np
import sys
import scipy.misc
import numpy
import json
from core.models import Product
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# 画像ファイルの指定

class MyDecoder:
    QR_NOT_FOUND = {'code': 100, 'message': 'QRコードを検出できませんでした'}
    MULTIPLE_PRODUCTS_IN_CHANNEL = {'code': 101, 'message': '同一チャネルに複数商品が存在します'}
    INVALID_PARAMETERS = {'code': 102, 'message': 'パラメータが不正です'}
    INTERNAL_ERROR = {'code': 200, 'message': '内部エラーが発生しました'}

    def __init__(self, image_path, oven):
        self.image_path = image_path
        self.oven = oven
    
    def _find_point(self, x1, y1, x2, y2, x, y):
        if (x > x1 and x < x2 and 
            y > y1 and y < y2) : 
            return True
        else : 
            return False

    def _draw_rectangle(self, coordinates, color, width=1):
        canvas = Image.open(self.image_path)
        draw = ImageDraw.Draw(canvas)
        for i in range(width):
            rect_start = (coordinates[0][0] - i, coordinates[0][1] - i)
            rect_end = (coordinates[1][0] + i, coordinates[1][1] + i)
            draw.rectangle((rect_start, rect_end), outline = color)
        del draw
        canvas.save(self.image_path, quality = 95)

    def _preprocess(self):
        processed_img_path = self.image_path + '_processed.jpg'
        img = cv2.imread(self.image_path)
        mask = cv2.inRange(img, (0,0,0), (150,150,150))
        thresholded = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        img = 255-thresholded
        scipy.misc.imsave(processed_img_path, img)
        self.image_path = processed_img_path
        return processed_img_path


    def decode(self, doesInvert):
        if doesInvert:
            self._preprocess()

        img = cv2.imread(self.image_path)
        barcodes = pyzbar.decode(img)

        has_valid_qr = False

        for barcode in barcodes:
            print(barcode.data.decode('utf-8'))
            try:
                Product.objects.get(qr = barcode.data.decode('utf-8'))
                has_valid_qr = True
            except ObjectDoesNotExist:
                continue
            except:
                return self.INTERNAL_ERROR

        if not has_valid_qr:
            return self.QR_NOT_FOUND

        height_in_pix, width_in_pix, _ = img.shape
        pix_per_mm_x = width_in_pix / oven.floor_width_in_mm
        pix_per_mm_y = height_in_pix / oven.floor_height_in_mm

        #channels = json.loads(self.oven.channel_info)
        channels = OvenChannel.objects.filter(oven = oven)

        result = []
        for ch in channels:
            top_left = (ch.x_offset_in_mm * pix_per_mm_x, ch.y_offset_in_mm * pix_per_mm_y)
            bottom_right = ( ch.x_offset_in_mm * pix_per_mm_x + ch.width_in_mm * pix_per_mm_x, ch.y_offset_in_mm * pix_per_mm_y + ch.height_in_mm * pix_per_mm_y)
            draw_rectangle((top_left, bottom_right), color = 'red', width = 3)
            temp = {'id': ch.seq }
            for barcode in barcodes:
                
                partialIn = False
                for point in barcode.polygon:
                    if find_point(ch.x_offset_in_mm * pix_per_mm_x, ch.y_offset_in_mm * pix_per_mm_y, ch.x_offset_in_mm * pix_per_mm_x + ch.width_in_mm * pix_per_mm_x, ch.y_offset_in_mm * pix_per_mm_y + ch.height_in_mm * pix_per_mm_y, point.x, point.y):
                        partialIn = True

                if partialIn:
                    if 'qr' in temp.keys() and temp['qr'] != barcode.data.decode('utf-8'):
                        return Errors.MULTIPLE_PRODUCTS_IN_CHANNEL
                    else:
                        temp['qr'] = barcode.data.decode('utf-8')
            result.append(temp)
        return result
