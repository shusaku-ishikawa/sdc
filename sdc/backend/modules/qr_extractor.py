import math
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from pyzbar import pyzbar
from shapely.geometry.polygon import Polygon
from ..models import *

class MathHelper:
    @staticmethod
    def count_children(hierarchy, parent, inner=False):
        if parent == -1:
            return 0
        elif not inner:
            return MathHelper.count_children(hierarchy, hierarchy[parent][2], True)
        return 1 + MathHelper.count_children(hierarchy, hierarchy[parent][0], True) + MathHelper.count_children(hierarchy, hierarchy[parent][2], True)

    @staticmethod
    def has_square_parent(hierarchy, squares, parent):
        if hierarchy[parent][3] == -1:
            return False
        if hierarchy[parent][3] in squares:
            return True
        return MathHelper.has_square_parent(hierarchy, squares, hierarchy[parent][3])

    @staticmethod
    def get_center(c):
        m = cv2.moments(c)
        return [int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])]

    @staticmethod
    def get_angle(p1, p2):
        x_diff = p2[0] - p1[0]
        print('x_diff = ' + str(x_diff))
        y_diff = p2[1] - p1[1]
        print('y_diff = ' + str(y_diff))
        return math.degrees(math.atan2(y_diff, x_diff))

    @staticmethod
    def get_midpoint(p1, p2):
        return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]

    @staticmethod
    def get_farthest_points(contour, center):
        distances = []
        distances_to_points = {}
        for point in contour:
            point = point[0]
            d = math.hypot(point[0] - center[0], point[1] - center[1])
            distances.append(d)
            distances_to_points[d] = point
        distances = sorted(distances)
        return [distances_to_points[distances[-1]], distances_to_points[distances[-2]]]

    @staticmethod
    def line_intersection(line1, line2):
        x_diff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        y_diff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(x_diff, y_diff)
        if div == 0:
            return [-1, -1]

        d = (det(*line1), det(*line2))
        x = det(d, x_diff) / div
        y = det(d, y_diff) / div
        return [int(x), int(y)]

    @staticmethod
    def extend(a, b, length, int_represent=False):
        length_ab = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
        if length_ab * length <= 0:
            return b
        result = [b[0] + (b[0] - a[0]) / length_ab * length, b[1] + (b[1] - a[1]) / length_ab * length]
        if int_represent:
            return [int(result[0]), int(result[1])]
        else:
            return result

    @staticmethod
    def rotate(origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        ox, oy = origin
        px, py = point

        qx = int(ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy))
        qy = int(oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy))
        return qx, qy

class QRExtractor:    
    BLUR_VALUE = 3
    SQUARE_TOLERANCE = 0.15
    AREA_TOLERANCE = 0.15
    DISTANCE_TOLERANCE = 0.25
    WARP_DIM = 300
    SMALL_DIM = 29
    LINE_WEIGHT = 3

    def __init__(self, original_iamge, px_per_mm_x, px_per_mm_y, for_debug = False):
        self.original_iamge = original_iamge
        self.draw = original_iamge
        self.codes = []
        self.east_corners = []
        self.south_corners = []
        self.main_corners = []
        self.px_per_mm_x = px_per_mm_x
        self.px_per_mm_y = px_per_mm_y
        
        self.for_debug = for_debug

    """
    商品の中心を求めます
    input:
        angle : 傾き(度)
        offset_x : その商品の中心からのQRの相対位置(x方向)
        offset_y : その商品の中心からのQRの相対位置(y方向)
        code_x : 検知したQRの位置(x)
        code_y : 検知したQRの位置(y)
    return:
        x, y : 商品の中心
    """
    def _get_product_center(self, angle, offset_x, offset_y, code_x, code_y):
        
        x, y = MathHelper.rotate((code_x, code_y), (code_x - offset_x, code_y - offset_y), angle)
        cv2.drawMarker(self.draw, (x, y), 1, markerType=cv2.MARKER_CROSS, markerSize=40, thickness=5, line_type=cv2.LINE_8)
        
        return x, y

    """
    傾いた四角形を描きます
    input:
        x0 : x方向のずれ
        y0 : y方向のずれ
        width : 幅
        height : 高さ
        angle : 傾き(度)
    """
    def _draw_angled_rec(self, x0, y0, width, height, angle):
        _angle = angle * math.pi / 180.0
        b = math.cos(_angle) * 0.5
        a = math.sin(_angle) * 0.5
        pt0 = (int(x0 - a * height - b * width),
            int(y0 + b * height - a * width))
        pt1 = (int(x0 + a * height - b * width),
            int(y0 - b * height - a * width))
        pt2 = (int(2 * x0 - pt0[0]), int(2 * y0 - pt0[1]))
        pt3 = (int(2 * x0 - pt1[0]), int(2 * y0 - pt1[1]))
        
        cv2.line(self.draw, pt0, pt1, (255, 255, 255), 3)
        cv2.line(self.draw, pt1, pt2, (255, 255, 255), 3)
        cv2.line(self.draw, pt2, pt3, (255, 255, 255), 3)
        cv2.line(self.draw, pt3, pt0, (255, 255, 255), 3)

        return (pt0, pt1, pt2, pt3)


    """
    チャネルの枠を書きます
    input:
        channel : チャネル情報
    return:
        list : チャネルの頂点
    """
    def draw_channel(self, channel):
    
        x_offset = int(channel.x_offset_in_mm * self.px_per_mm_x)
        y_offset = int(channel.y_offset_in_mm * self.px_per_mm_y)
        width = int(channel.width_in_mm * self.px_per_mm_x)
        height = int(channel.height_in_mm * self.px_per_mm_y)

        channel_cordinates = ((x_offset, y_offset), (x_offset + width, y_offset),  (x_offset + width, y_offset + height), (x_offset, y_offset + height))
        
        cv2.line(self.draw, (x_offset, y_offset), (x_offset + width, y_offset), (255, 255, 0), 3)
        cv2.line(self.draw, (x_offset + width, y_offset), (x_offset + width, y_offset + height), (255, 255, 0), 3)
        cv2.line(self.draw, (x_offset + width, y_offset + height), (x_offset, y_offset + height), (255, 255, 0), 3)
        cv2.line(self.draw, (x_offset, y_offset + height), (x_offset, y_offset), (255, 255, 0), 3)

        return list(channel_cordinates)


    """
    商品の枠を書きます
    input:
        x_offsett : その商品の中心位置からのQR位置(x方向へのずれ)
        y_offset : その商品の中心位置からのQR位置(ｙ方向へのずれ)
    return:
        3d-list : 商品の頂点の配列
    """
    def find_products(self):
        for i in range(len(self.codes)):
            south = self.south_corners[i]
            east = self.east_corners[i]
            main = self.main_corners[i]
            code = self.codes[i]

            barcodes = pyzbar.decode(code)

            products = []
            for barcode in barcodes:
                if barcode.type == 'QRCODE':
                    barcode_data = barcode.data.decode('utf-8')

                    # get angle
                    main_center = MathHelper.get_center(main)
                    south_center = MathHelper.get_center(south)
                    east_center = MathHelper.get_center(east)
                    code_center = MathHelper.get_center(code)
                    print(code_center)
                    angle = MathHelper.get_angle(main_center, east_center)

                    p = Product.objects.get(qr = barcode_data)

                    px, py = self._get_product_center(angle, p.qr_x_offset_in_mm * self.px_per_mm_x, p.qr_y_offset_in_mm * self.px_per_mm_y, main_center[0], main_center[1])
                    
                    coords = self._draw_angled_rec(px, py, p.width_in_mm * self.px_per_mm_x, p.height_in_mm * self.px_per_mm_y, angle)
                    products.append(list(coords))
        return barcodes, products 

    """
    QRの3か所のマーカの場所を表示する
    input:
        N/A
    return:
        Boolean : if a barcode is detected or not.
    """
    def draw_three_square(self):
        for i in range(len(self.codes)):
            south = self.south_corners[i]
            east = self.east_corners[i]
            main = self.main_corners[i]
            code = self.codes[i]

            barcodes = pyzbar.decode(code)

            for barcode in barcodes:
                print('code:' + str(i) + '::' + str(barcode.data.decode('utf-8')))

                # east
                pts = east.reshape((-1,1,2))
                canvas = cv2.polylines(self.draw, [east], True, (0,255,255), self.LINE_WEIGHT )

                # south
                pts = south.reshape((-1,1,2))
                canvas = cv2.polylines(canvas, [south], True, (0,255,255), self.LINE_WEIGHT)
            
                # main
                pts = main.reshape((-1,1,2))
                canvas = cv2.polylines(canvas, [main], True, (0,255,255), self.LINE_WEIGHT)
        self.draw = canvas
    
    """
    QRの3か所のマーカの場所を表示する
    input:
        N/A
    return:
        N/A
    """
    def extract(self):
        output = self.original_iamge.copy()

        # ノイズ除去
        gray = cv2.cvtColor(self.original_iamge, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        gray = cv2.GaussianBlur(gray, (self.BLUR_VALUE, self.BLUR_VALUE), 0)
        edged = cv2.Canny(gray, 30, 200)

        # 輪郭と階層を取得
        contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        squares = []
        square_indices = []

        i = 0
        for c in contours:
            # 近似処理
            peri = cv2.arcLength(c, True) # 輪郭の長さ
            area = cv2.contourArea(c) # 面積
            approx = cv2.approxPolyDP(c, 0.03 * peri, True) # 3%の精度で頂点が最小の多角形に近似

            # 近似した結果四角形
            if len(approx) == 4:
                # 面積 > 25 and 辺から求めた面積とareaの誤差15％未満 and 長方形の子供が2つ以上 and 親がいない 
                if area > 25 and 1 - self.SQUARE_TOLERANCE < math.fabs((peri / 4) ** 2) / area < 1 + self.SQUARE_TOLERANCE and MathHelper.count_children(hierarchy[0], i) >= 2 and MathHelper.has_square_parent(hierarchy[0], square_indices, i) is False:
                    squares.append(approx)
                    square_indices.append(i)
            i += 1

        # 3箇所のマーカーを取得する
        main_corners = []
        east_corners = []
        south_corners = []
        tiny_squares = []
        rectangles = []

        # 輪郭を近似した結果四角形であったものを解析
        for square in squares:
            area = cv2.contourArea(square)
            center = MathHelper.get_center(square)
            peri = cv2.arcLength(square, True)

            similar = []
            tiny = []
            for other in squares:
                if square[0][0][0] != other[0][0][0]:
                    # 近似した結果の面積の差異が一定の閾値に収まるときに、その四角形を類似と判断
                    if math.fabs(area - cv2.contourArea(other)) / max(area, cv2.contourArea(other)) <= self.AREA_TOLERANCE:
                        similar.append(other)
                    # 辺の長さが自分のものの2分の1未満である差異はtinyマーカと判断
                    elif peri / 4 / 2 > cv2.arcLength(other, True) / 4:
                        tiny.append(other)

            if len(similar) >= 2:
                distances = []
                distances_to_contours = {}
                for sim in similar:
                    sim_center = MathHelper.get_center(sim)
                    #類似系までの距離を追加していく
                    d = math.hypot(sim_center[0] - center[0], sim_center[1] - center[1])
                    distances.append(d)
                    # その距離にある輪郭を追加
                    distances_to_contours[d] = sim
                distances = sorted(distances)
                #一番近い距離を二つ(つまりトリオ)
                closest_a = distances[-1]
                closest_b = distances[-2]

                # Determine if this square is the top left QR code indicator
                if max(closest_a, closest_b) < cv2.arcLength(square, True) * 2.5 and math.fabs(closest_a - closest_b) / max(closest_a, closest_b) <= self.DISTANCE_TOLERANCE:
                    # Determine placement of other indicators (even if code is rotated)
                    angle_a = MathHelper.get_angle(MathHelper.get_center(distances_to_contours[closest_a]), center)
                    #angle_a = _get_angle(center, _get_center(distances_to_contours[closest_a]))
                    
                    #angle_b = _get_angle(center, _get_center(distances_to_contours[closest_b])) 
                    angle_b = MathHelper.get_angle(MathHelper.get_center(distances_to_contours[closest_b]), center) 
    
                    if angle_a < angle_b or (angle_b < -90 and angle_a > 0):
                        east = distances_to_contours[closest_a]
                        south = distances_to_contours[closest_b]
                    else:
                        east = distances_to_contours[closest_b]
                        south = distances_to_contours[closest_a]
                    midpoint = MathHelper.get_midpoint(MathHelper.get_center(east), MathHelper.get_center(south))
                    
                    # Determine location of fourth corner
                    # Find closest tiny indicator if possible
                    min_dist = 10000
                    t = []
                    tiny_found = False
                    if len(tiny) > 0:
                        for tin in tiny:
                            tin_center = MathHelper.get_center(tin)
                            d = math.hypot(tin_center[0] - midpoint[0], tin_center[1] - midpoint[1])
                            if d < min_dist:
                                min_dist = d
                                t = tin
                        tiny_found = len(t) > 0 and min_dist < peri

                    diagonal = peri / 4 * 1.41421

                    if tiny_found:
                        # Easy, corner is just a few blocks away from the tiny indicator
                        tiny_squares.append(t)
                        offset = MathHelper.extend(midpoint, MathHelper.get_center(t), peri / 4 * 1.41421)
                    else:
                        # No tiny indicator found, must extrapolate corner based off of other corners instead
                        farthest_a = MathHelper.get_farthest_points(distances_to_contours[closest_a], center)
                        farthest_b = MathHelper.get_farthest_points(distances_to_contours[closest_b], center)
                        # Use sides of indicators to determine fourth corner
                        offset = MathHelper.line_intersection(farthest_a, farthest_b)
                        if offset[0] == -1:
                            # Error, extrapolation failed, go on to next possible code
                            continue
                        offset = MathHelper.extend(midpoint, offset, peri / 4 / 7)
                        if self.for_debug:
                            cv2.line(output, (farthest_a[0][0], farthest_a[0][1]), (farthest_a[1][0], farthest_a[1][1]), (0, 0, 255), 4)
                            cv2.line(output, (farthest_b[0][0], farthest_b[0][1]), (farthest_b[1][0], farthest_b[1][1]), (0, 0, 255), 4)

                    # Append rectangle, offsetting to farthest borders
                    rectangles.append([MathHelper.extend(midpoint, center, diagonal / 2, True), MathHelper.extend(midpoint, MathHelper.get_center(distances_to_contours[closest_b]), diagonal / 2, True), offset, MathHelper.extend(midpoint, MathHelper.get_center(distances_to_contours[closest_a]), diagonal / 2, True)])
                    self.east_corners.append(east)
                    self.south_corners.append(south)
                    self.main_corners.append(square)

        codes = []
        i = 0
        for rect in rectangles:
            i += 1
            # Draw rectangle
            vrx = np.array((rect[0], rect[1], rect[2], rect[3]), np.int32)
            vrx = vrx.reshape((-1, 1, 2))
            cv2.polylines(output, [vrx], True, (0, 255, 255), 1)
            # Warp codes and draw them
            wrect = np.zeros((4, 2), dtype="float32")
            wrect[0] = rect[0]

            wrect[1] = rect[1]
            wrect[2] = rect[2]
            wrect[3] = rect[3]
            dst = np.array([
                [0, 0],
                [self.WARP_DIM - 1, 0],
                [self.WARP_DIM - 1, self.WARP_DIM - 1],
                [0, self.WARP_DIM - 1]], dtype="float32")
            warp = cv2.warpPerspective(self.original_iamge, cv2.getPerspectiveTransform(wrect, dst), (self.WARP_DIM, self.WARP_DIM))
        
            # Increase contrast
            warp = cv2.bilateralFilter(warp, 11, 17, 17)
            warp = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
            small = cv2.resize(warp, (self.SMALL_DIM, self.SMALL_DIM), 0, 0, interpolation=cv2.INTER_CUBIC)
            _, small = cv2.threshold(small, 100, 255, cv2.THRESH_BINARY)
            codes.append(warp)

        self.codes = codes
        return len(codes) > 0