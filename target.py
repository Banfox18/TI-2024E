# target - By: Arctain - Wed Jul 29 2024

import image
from math import fabs

def reshape(array2D, l, r, c):
    array3D = [[[0 for c in range(c)] for r in range(r)] for l in range(l)]  # 预先定义三层
    for layer in range(l):  # 层数
        for row in range(r):  # 行数
            for col in range(c):  # 列数
                index = layer * 3 + row  # 计算原始数组的索引
                array3D[layer][row][col] = array2D[index][col]
    return array3D


# 参数: img对象
# 返回值: 二维数组[row][column], 包含每一个矩形对角的x, y坐标: 序号为左上角开始顺时针
def findRects(img):
    # 遍历出每一个矩形
    rects = img.find_rects(threshold = 15000)# return一个 img.rect 对象的list
    # coordinates = [[[0 for c in range(2)] for r in range(3)] for l in range(3)]
    # allRectsCorners = []
    sp = []
    for r in rects:
        # 如果棋盘识别错误, 直接返回[]
        if r.w() < 60 or r.h() < 60:
            return []
        img.draw_rectangle(r.rect(), color = (255, 0, 0))
        corners = r.corners()
        # for p in corners: img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))
        # 棋盘格特征点设置 左上角开始顺时针
        # 将 corners 的每个点转换为整数，一次性计算关键点的坐标

        num_corners = len(corners)
        # 边框上的点
        for i in range(num_corners):
            # 计算当前角和下一个角的中间点
            start = corners[i]
            end = corners[(i + 1) % num_corners]  # 循环连接最后一个和第一个
            sp.append([int(start[0]), int(start[1])])  # 添加当前点

            for j in range(1, 3):  # 生成两个中间点
                sp.append([
                    int(start[0] + j * (end[0] - start[0]) / 3),
                    int(start[1] + j * (end[1] - start[1]) / 3)
                ])
        # 内点
        sp.extend([
                    [int(sp[11][0] + 1 * (sp[4][0] - sp[11][0]) / 3), int(sp[11][1] + 1 * (sp[4][1] - sp[11][1]) / 3)],
                    [int(sp[11][0] + 2 * (sp[4][0] - sp[11][0]) / 3), int(sp[11][1] + 2 * (sp[4][1] - sp[11][1]) / 3)],
                    [int(sp[10][0] + 2 * (sp[5][0] - sp[10][0]) / 3), int(sp[10][1] + 2 * (sp[5][1] - sp[10][1]) / 3)],
                    [int(sp[10][0] + 1 * (sp[5][0] - sp[10][0]) / 3), int(sp[10][1] + 1 * (sp[5][1] - sp[10][1]) / 3)]
                ])
        # 绘制线条
        line_pairs = [
            (sp[0], sp[3]), (sp[11], sp[4]), (sp[10], sp[5]),
            (sp[9], sp[6]), (sp[0], sp[9]), (sp[1], sp[8]),
            (sp[2], sp[7]), (sp[3], sp[6])
        ]

        for start, end in line_pairs:
            img.draw_line(start[0], start[1], end[0], end[1], color=(0, 255, 0))
        # print(len(sp))

    return sp

# 将sp参数转换为中心点位置坐标
# 参数: sp
# 返回值: 三维数组[layer][row][column], column为中心点坐标
def findRectsCenters(sp):
    # 验证输入长度
    if len(sp) != 16:
        print("INVALID_SP_LENGTH: ", len(sp))
        return [[[-1 for _ in range(2)] for _ in range(3)] for _ in range(3)]

    # 初始化中心点数组
    centers = [[[-1 for _ in range(2)] for _ in range(3)] for _ in range(3)]

    # 中心点计算索引对
    index_pairs = [
        (0, 12), (1, 13), (2, 4),
        (11, 15), (12, 14), (13, 5),
        (10, 8), (15, 7), (14, 6)
    ]

    # 填充中心点数组
    for i, (a, b) in enumerate(index_pairs):
        centers[i // 3][i % 3][0] = (sp[a][0] + sp[b][0]) / 2
        centers[i // 3][i % 3][1] = (sp[a][1] + sp[b][1]) / 2

    return centers



# 将坐标变换为board 中的序号
# 参数: x, y, 三维数组
# 返回值: [row,col](行,列)
def convertToList(cx, cy, coor):
    xy = [-1, -1]
    # 三维数组里的layer 对应行, row 对应列, column对应xy坐标
    for l in range(3):
        for r in range(3):
            # 误差可调
            if (fabs(cx - coor[l][r][0]) < 12 and fabs(cy - coor[l][r][1]) < 12):
                xy[0] = l
                xy[1] = r
                return xy
    return xy

# 返回值: 三维数组[layer][row][column], column为中心点坐标
def getPositions(img):
    # 遍历出每一个矩形
    rects = img.find_rects(threshold = boardThreshold)# return一个 img.rect 对象的list
    # coordinates = [[[0 for c in range(2)] for r in range(3)] for l in range(3)]
    # allRectsCorners = []
    sp = []
    for r in rects:
        # 如果棋盘识别错误, 直接返回[]
        if r.w() < 100 or r.h() < 100:
            continue
        print("test")
        corners = r.corners()
        # 棋盘格特征点设置 左上角开始顺时针
        # 将 corners 的每个点转换为整数，一次性计算关键点的坐标
        num_corners = len(corners)
        # 边框上的点
        for i in range(num_corners):
            # 计算当前角和下一个角的中间点
            start = corners[i]
            end = corners[(i + 1) % num_corners]  # 循环连接最后一个和第一个
            sp.append([int(start[0]), int(start[1])])  # 添加当前点

            for j in range(1, 3):  # 生成两个中间点
                sp.append([
                    int(start[0] + j * (end[0] - start[0]) / 3),
                    int(start[1] + j * (end[1] - start[1]) / 3)
                ])
        # 内点
        sp.extend([
                    [int(sp[11][0] + 1 * (sp[4][0] - sp[11][0]) / 3), int(sp[11][1] + 1 * (sp[4][1] - sp[11][1]) / 3)],
                    [int(sp[11][0] + 2 * (sp[4][0] - sp[11][0]) / 3), int(sp[11][1] + 2 * (sp[4][1] - sp[11][1]) / 3)],
                    [int(sp[10][0] + 2 * (sp[5][0] - sp[10][0]) / 3), int(sp[10][1] + 2 * (sp[5][1] - sp[10][1]) / 3)],
                    [int(sp[10][0] + 1 * (sp[5][0] - sp[10][0]) / 3), int(sp[10][1] + 1 * (sp[5][1] - sp[10][1]) / 3)]
                ])
    return findRectsCenters(sp)

# 识别准备区的棋子
# 参数: status: 1黑, -1白
# 返回值: 二维数组, [棋子序号][棋子位置坐标]
def findChess(img, blackThreshold, whiteThreshold, status):
    threshold = []
    roi = []
    st = ""
    # 先判断status, 如果为1, 用黑色阈值; 为-1, 用白色阈值
    if status == 1:
        threshold = blackThreshold
        roi = [1, 1, 50, 120]
        st = "BLACK"
    elif status == -1:
        threshold = whiteThreshold
        roi = [111, 1, 50, 120]
        st = "WHITE"
    else:
        print("INVAILD_CHESS_STATUS")
        return []

    chess = img.find_blobs([threshold], x_stride=13, y_stride=13, pixels_threshold=200, roi = roi)

    chessPositions = []

    if chess:
        for c in chess:
            # 如果棋子长宽超出范围, 忽略
            if c.w() > 30 or c.h() > 30 or c.w() < 20 or c.h() < 20:
                continue

            centerX = c.cx()
            centerY = c.cy()
            chessPositions.append((centerX, centerY))

            img.draw_circle(centerX, centerY,int(c.w() / 2 ),color=(255,255,255))
            img.draw_cross(centerX, centerY,size=2,color=(255,255,255))
            img.draw_string(c.x(), (c.y()-10), st, color=(0,0,255))

    # 按照 y 坐标排序 (升序)
    chessPositions.sort(key=lambda pos: pos[1])

    # 将坐标转换为二维数组格式
    sortedChessArray = [[index + 1, pos] for index, pos in enumerate(chessPositions)]

    # 在棋子中心绘制编号
    for index, (x, y) in enumerate(chessPositions):
        img.draw_string(x, y, str(index + 1), color=(255, 0, 0))  # 用红色绘制编号

    return sortedChessArray  # 返回排序后的二维数组


# UNICODE: A 65 B 66 C 67 D 68 E 69 F 70

# G 71 H 72 I 73 J 74 K 75 L 76 M 77 N 78 O 79 P 80

# Q 81 R 82 S 83 T 84 U 85 V 86 W 87 X 88 Y 89 Z 90

# a 97 b 98 c 99 d 100 e 101 f 102 g 103 h 104 i 105

# j 106 k 107 l 108 m 109 n 110 o 111 p 112 q 113 r 114

# s 115 t 116 u 117 v 118 w 119 x 120 y 121 z 122
