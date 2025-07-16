# Project - By: Arctain - Wed Jul 29 2024
import sensor, image, time, math
import ustruct
from pyb import UART, LED
from target import findRects, findRectsCenters, convertToList, findChess
from ttl import getData, sendCommand, sendDataToBlueTooth, posToIndex, countToIndex, moveToIndex, getDestination, convertCommand
from board import isBoardEmpty, detectMove
blackThreshold  = (0, 43, -30, 13, -22, 9)
whiteThreshold  = (59, 100, -30, 13, -22, 9)
boardThreshold = 65000
board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
boardBefore = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
# AI执棋, 由串口通信接收 黑1 白-1
sideAI = 0
rectMatrix = []
count = 0
sensor.reset()
sensor.set_pixformat(sensor.RGB565)# LAB (l_lo，l_hi，a_lo，a_hi，b_lo，b_hi)
sensor.set_framesize(sensor.QVGA) #QQVGA: 160x120
sensor.set_windowing((80, 40, 160, 160 ))
sensor.skip_frames(n=2000) #在更改设置后，跳过n张照片，等待感光元件变稳定
sensor.set_auto_gain(False) #使用颜色识别时需要关闭自动自动增益
sensor.set_auto_whitebal(False)#使用颜色识别时需要关闭自动自动白平衡
clock = time.clock() #Track FPS

# stm32
uart01 = UART(3, 115200) # 串口UART(3)是P4-TX P5-RX, 串口UART(1)是P0-RX P1-TX
# 蓝牙
uart02 = UART(1, 9600)
# TTL串口至少需要4根线：TXD，RXD，GND, VCC。TXD是发送端，RXD是接收端，GND是地线; 连线的时候，需要把OpenMV的RXD连到另一个MCU的TXD，TXD连到RXD
# uart01.init(19200, bits=8, parity=None, stop=1 ) # (波特率, 有效数据位, 校验位, 停止位)
# uart02.init(9600, bits=8, parity=None, stop=1 )
def containsElement(array, target):
    # 遍历二维数组
    for row in array:  # 遍历每一行
        for element in row:  # 遍历每一行中的每一个元素
            if element == target:  # 检查元素是否等于目标值
                return True  # 找到目标元素，返回 True
    return False  # 遍历完仍未找到，返回 False

def getValueFrom3dArray(arr_3d, layer_row):
    layer, row = layer_row  # 解包层和行
    # 检查输入维度是否合法
    if (0 <= layer < len(arr_3d)) and (0 <= row < len(arr_3d[layer])):
        return arr_3d[layer][row]  # 返回对应的列（所有列的值）
    else:
        return None  # 如果输入的层或行不合法，返回 None

# 输入: 1-9 : 49-57
# 返回值: board坐标
def commandToList(num):
    # 将数字调整为从0开始的索引
    if num <= 57 and num >=49:
        index = num - 49
    elif num <=75 and num >= 67:
        index = num - 67
    # 定义行和列
    rows = 3
    cols = 3

    # 计算行和列
    row = index // cols
    col = index % cols
    pos = [row, col]
    print("pos: ", pos)
    return pos

# 参数: img, 黑棋阈值, 白棋阈值
# 返回值: 二维数组board, 黑1, 白-1, 空0
def findBlob(img, blackThreshold, whiteThreshold):
    board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    # rect = img.find_rects(threshold = boardThreshold)
    roi = [25, 25, 110, 110]
    # 如果未检测到棋盘或检测到了多个棋盘, 直接return []
    #if len(rect) != 1:
    #    return []
    # 只在棋盘范围内检测棋子
    # roi = rect[0].rect()
    blackBlobs = img.find_blobs([blackThreshold], x_stride=15, y_stride=15, pixels_threshold=150)
    whiteBlobs = img.find_blobs([whiteThreshold], x_stride=15, y_stride=15, pixels_threshold=200)
    global rectMatrix
    rectMatrix = [
                  [(43, 43), (79, 43), (116, 43)],
                  [(43, 79), (79, 79), (116, 79)],
                  [(43, 116), (79, 116), (116, 116)]
              ]
    #if (rectMatrix[0][0][0] == -1):
     #    如果未检测到棋盘, 返回-2
     #   board  = [[-2, -2, -2], [-2, -2, -2], [-2, -2, -2]]
    if blackBlobs:
        for b in blackBlobs:
            # 如果棋子长宽超出范围, 忽略
            if b.w() > 35 or b.h() > 35 or b.w() < 5 or b.h() < 5:
                continue
            # img.draw_rectangle((b.x(),b.y(),b.w(),b.h()),color=(255,255,255))
            img.draw_circle(b.cx(),b.cy(),int(b.w() / 2 ),color=(255,255,255))
            img.draw_cross(b.cx(), b.cy(),size=2,color=(255,255,255))
            img.draw_string(b.x(), (b.y()-10), "BLACK", color=(0,0,255))
            # print("cx: ",b.cx(),"cy: ",b.cy(),"color: ","BLACK")
            xy = convertToList(b.cx(), b.cy(), rectMatrix)
            board[xy[0]][xy[1]] = 1

    if whiteBlobs:
        for w in whiteBlobs:
            # 如果棋子长宽超出范围, 忽略
            if w.w() > 35 or w.h() > 35 or w.w() < 5 or w.h() < 5:
                continue
            img.draw_circle(w.cx(),w.cy(),int(w.w() / 2 ),color=(0,0,0))
            img.draw_cross(w.cx(), w.cy(),size=2,color=(0,0,0))
            img.draw_string(w.x(), (w.y()-10), "WHITE", color=(255,255,0))
            # print("cx: ",w.cx(),"cy: ",w.cy(),"color: ","WHITE")
            xy = convertToList(w.cx(), w.cy(), rectMatrix)
            board[xy[0]][xy[1]] = -1
    return board


while(True):
    clock.tick()
    # img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0).binary([boardThreshold])# 从感光芯片获得一张图像并且进行畸变校正
    img = sensor.snapshot()
    # global count, boardBefore
    board = findBlob(img, blackThreshold, whiteThreshold)# 该方法运行后, 可以用rectMatrix调用棋盘九个中心点坐标
    #print("board: ", board)
    #print("rectMatrix: ", rectMatrix)
    if isBoardEmpty(board):# 检查棋盘是否为空, 如果为空, 将count置零
        count = 0

    receive = getData(uart02)
    # 如果串口未检测到数据, 跳过这一帧
    #receive = "A"
    if receive == None:
        continue
    # 如果棋盘数量非法, 跳过
    #if len(board) == 0:
    #    print("INVAILD_BOARD_AMOUNT: ", len(board))
    #    continue

    # 棋盘包含非法元素, 跳过
    #if containsElement(board, -2):
    #    print("INVAILD_BOARD_CONTAINMENT")
    #    continue
    boardMove = detectMove(boardBefore, board)
    #boardMove = []
    if len(boardMove) != 0:
        print("BOARD_CHANGED")
        # 拿起修改的棋子
        sendCommand(uart01, moveToIndex(boardMove[1]))
        #time.sleep(5)
        sendCommand(uart01, posToIndex(boardMove[0]))
        continue
    boardBefore = board
    # 蓝牙发送来的指令 1-9 -> 黑0-8; A -> 97; B -> 98; C-K
    # 指令转换, 参数是String
    com = convertCommand(receive)
    print("command: ", com)
    if com == None:
         # 格式错误, 直接跳过
         continue
    # 设置ai执棋方
    elif com == 65:
        sideAI = 1
        # 到准备区拿棋子
        print("count: ", count)
        sendCommand(uart01, countToIndex(count, sideAI))
        #time.sleep(5)
        # 到棋盘上放棋子
        sendCommand(uart01, posToIndex(getDestination(com, sideAI, board)))
        time.sleep(5)
        sendDataToBlueTooth(uart02, 1)
        count += 1
    elif com == 66:
        sideAI = -1
        # 到准备区拿棋子
        print("count: ", count)
        sendCommand(uart01, countToIndex(count, sideAI))
        #time.sleep(5)
        # 到棋盘上放棋子
        sendCommand(uart01, posToIndex(getDestination(com, sideAI, board)))
        time.sleep(5)
        sendDataToBlueTooth(uart02, 1)
        count += 1
    elif (com <= 57 and com >=49) or (com <=75 and com >= 67):
        if com <= 57 and com >=49:
            sideAI = 1
            # 到准备区拿棋子
            print("count: ", count)
            sendCommand(uart01, countToIndex(count, sideAI))
            #time.sleep(5)
            # 到棋盘上放棋子
            sendCommand(uart01, posToIndex(commandToList(com)))

        elif com <=75 and com >= 67:
            sideAI = -1
            print("count: ", count)
            sendCommand(uart01, countToIndex(count, sideAI))
            #time.sleep(5)
            sendCommand(uart01, posToIndex(commandToList(com)))
        count += 1

