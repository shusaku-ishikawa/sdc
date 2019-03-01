from pyzbar.pyzbar import decode
from PIL import Image
import cv2

# 画像ファイルの指定

def decode_code(image_path):
    try:
        img = cv2.imread(image_path)
        mask = cv2.inRange(img, (0,0,0), (60,60,60))
        thresholded = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        inverted = 255-thresholded

       
        data = decode(inverted)
        
        print(data)
        # コード内容を出力
        return {'success': data[0][0].decode('utf-8', 'ignore')}
    except:
        return {'error': 'デコードに失敗しました'}

