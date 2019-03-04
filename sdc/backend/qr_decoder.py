from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sys
import scipy.misc
import numpy
import json

# 画像ファイルの指定
def find_point(x1, y1, x2,  
              y2, x, y) : 
    if (x > x1 and x < x2 and 
        y > y1 and y < y2) : 
        return True
    else : 
        return False

def decode_qrcode(image_path, oven):
    
    img =cv2.imread(image_path)
    mask = cv2.inRange(img, (0,0,0), (60,60,60))
    thresholded = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    inverted = 255-thresholded

    # # Create figure and axes
    #
    scipy.misc.imsave(image_path + '_inverted.jpg', inverted)
    barcodes = decode(inverted)
    
    fig,ax = plt.subplots(1)
    # Display the image
    ax.imshow(Image.open(image_path + '_inverted.jpg'))

    

    if len(barcodes) == 0:
        return {'error': 'QRコードが見つかりませんでした'}

    height_in_pix, width_in_pix, color_channels = img.shape
    pix_per_mm_x = width_in_pix / oven.floor_width_in_mm
    pix_per_mm_y = height_in_pix / oven.floor_height_in_mm

    channels = json.loads(oven.channel_info)
    print(channels)
    result = []
    for ch in channels:
        temp = {'id': ch['id']}
        hasCode = False
        for barcode in barcodes:
            allIn = True
            partialIn = False
            for point in barcode.polygon:
                if find_point(ch["x_offset"]*pix_per_mm_x, ch["y_offset"]*pix_per_mm_y, ch["x_offset"]*pix_per_mm_x + ch["width"]*pix_per_mm_x, ch["y_offset"]*pix_per_mm_y + ch["height"]*pix_per_mm_y, point.x, point.y):
                    partialIn = True
                else:
                    allIn = False
            
            if partialIn:
                if hasCode:
                    return {'error': '同一チャネルに複数商品があります'}
                else:
                    if not allIn:
                        return {'error': 'チャネルを跨って置かれています'}
                    else:
                        temp['qr'] = barcode.data
                        hasCode = True
        result.append(temp)
    return result