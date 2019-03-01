from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sys
import scipy.misc
import numpy

args = sys.argv
qr_width_in_cm = 1
qr_height_in_cm = 1
channels = [
    {
        "id": 1,
        "x": 0,
        "y": 0,
        "w": 10,
        "h": 15,
    },
    {
        "id": 2,
        "x": 10,
        "y": 0,
        "w": 10,
        "h": 15,
    },
    {
        "id": 3,
        "x": 0,
        "y": 15,
        "w": 10,
        "h": 15,
    },
    {
        "id": 4,
        "x": 10,
        "y": 15,
        "w": 10,
        "h": 15,
    },
]

def FindPoint(x1, y1, x2,  
              y2, x, y) : 
    if (x > x1 and x < x2 and 
        y > y1 and y < y2) : 
        return True
    else : 
        return False

if __name__ == "__main__" : 
    #image = cv2.imread(args[1])
    # data = decode(Image.open(args[1]))
    # print(data)
    # (x, y, w, h) = data[0].rect
    # print('cm / px in x-axis in this image is ' + str(qr_width_in_cm / w))
    # print('cm / px in y-axis in this image is ' + str(qr_height_in_cm / h))

    img =cv2.imread(args[1])
    # img = np.array(Image.open(args[1]), dtype=np.uint8)
    #mask = cv2.inRange(img, (0,0,0), (200,200,200))
    mask = cv2.inRange(img, (0,0,0), (60,60,60))

    thresholded = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    inverted = 255-thresholded

    # # Create figure and axes
    #
    scipy.misc.imsave(args[1] + '_inverted.jpg', inverted)
    barcodes = decode(inverted)
    #print (barcodes)

    fig,ax = plt.subplots(1)
    # # Display the image
    ax.imshow(Image.open(args[1] + '_inverted.jpg'))

    pix_per_cm = 0

    if len(barcodes) == 0:
        print('QRコードが見つかりませんでした')
        sys.exit(0)

    (x, y, w, h) = barcodes[0].rect
    a = numpy.array([barcodes[0].polygon[0].x, barcodes[0].polygon[0].y])
    b = numpy.array([barcodes[0].polygon[1].x, barcodes[0].polygon[1].y])
    u = b - a
    d_pix = numpy.linalg.norm(u)

    pix_per_cm = d_pix / qr_height_in_cm

    for ch in channels:
        hasCode = False
        for barcode in barcodes:
            allIn = True
            partialIn = False
            for point in barcode.polygon:
                if FindPoint(ch["x"]*pix_per_cm, ch["y"]*pix_per_cm, ch["x"]*pix_per_cm + ch["w"]*pix_per_cm, ch["y"]*pix_per_cm + ch["h"]*pix_per_cm, point.x, point.y):
                    partialIn = True
                else:
                    allIn = False
            
            if partialIn:
                if hasCode:
                    print("既にそのチャネルに商品があります")
                    sys.exit(0)
                else:
                    if not allIn:
                        print(str(ch["id"]) + ":チャネルを跨って置かれています。")
                        sys.exit(0)
                    else:
                        ch["data"] = barcode.data
                        hasCode = True
    print(channels)




        
    #     rect = patches.Rectangle((x, y),w,h,linewidth=1,edgecolor='r',facecolor='none')
    # # # Add the patch to the Axes
    # ax.add_patch(rect)

    for ch in channels:
        ch_rect = patches.Rectangle((ch.get("x") * pix_per_cm, ch.get("y") * pix_per_cm), ch.get("w") * pix_per_cm, ch.get("h") * pix_per_cm, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(ch_rect)
    plt.show()

    #data = decode(Image.open(image))

    #print(data[0][0].decode('utf-8', 'ignore'))