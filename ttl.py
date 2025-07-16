# ttl - By: Arctain - Thu Jul 31 2024
import ustruct, re
from pyb import UART
from board import findBestMove, checkWinner
# $KMS:x,y,z,time!
'''
舵机操作指令:
#IndexPpwmTtime!
Index: 000-005对应六个舵机, 005控制夹子
pwm: 脉冲宽度, 范围 0500 - 2500
time: 时间, 范围 0000 - 9999 (ms) 可以设为0000
'''

co = 0
# 串口通信, 需要stm32端写对应算法
def sendData(uart, cx, cy):
    data = ustruct.pack('ii', int(cx), int(cy))
    print("you send: ", data)
    uart.write(data);
    for i in data:
        print("data： ",hex(i))
# 蓝牙串口通信
def sendDataToBlueTooth(uart, data):
    data = ustruct.pack("<bbb", 0xff, int(data), 0xfe)
    uart.write(data);
    print("you send:", data)
    for i in data:
        print("data： ",hex(i))
# 串口接收, 这里要做判断
# 返回值: String
def getData(uart):
    if uart.any():  # 检查是否有可用数据
        print("test")
        data = uart.read()  # 读取数据存入data
        if data:
            try:
                # 使用 utf-8 编码解码数据，忽略无法解码的字符
                # decodeData = data.decode('utf-8', errors='ignore')
                decodeData = data.decode()
                print("Received:", decodeData)  # 打印接收到的数据
                return decodeData
            except Exception as e:
                print("UnicodeDecodeError:", e)  # 捕获并打印错误信息
                return None  # 返回 None 表示解码失败
    return None

# 数据转换, 提取String中的int类型数据
# 返回值: int数组
def getInts(str):
    # 正则表达式 查找所有整数
    #findall()返回值是一个String数组
    numbers = re.findall(r'\d+', string)
    # 将String转换为int
    ints = [int(num) for num in numbers]
    return ints

# 1-9 A:65 B:66 C-K:67-75
# 蓝牙发送来的指令
# 指令转换, 参数是String
# 返回值: int
def convertCommand(receive):
    if len(receive) != 1:
        print("INVAILD_COMMAND_SYNTAX: LENTH")
        return None
    asc = ord(receive)
    # A B
    if asc == 65 or asc == 66:
        return asc
    # 1-9 之间 返回 49-57 , C-K:67-75
    elif (asc <= 57 and asc >=49) or (asc <=75 and asc >= 67):
        return asc
    else:
        print("INVAILD_COMMAND_SYNTAX: VALUE")
        return None

# 发送舵机操作指令
# $RST! 软件复位
# $DGT:0-10,1! 调用动作G0000-G0010组, 1次
# 参数: 一个int数组, 包含起始和结束两个索引
# 返回值: Void
def sendCommand(uart, indices):
    if indices == None:
        print("sendCommandTest")
        return
    elif len(indices) == 0:
        print("sendCommandTest")
        return
    command = "$DGT:" + str(indices[0]) + "-" + str(indices[1]) + ",1!"
    uart.write(command.encode('utf-8'))
    print("you send: ", command)

# 判断 com 类型 并返回坐标
# 返回值: 坐标数组(x, y)
def getDestination(com, sideAI, board):
    # 如果指令为空, 返回空数组
    if com == None:
        print("NONE_COMMAND")
        return []
    # 如果指令为0 - 8返回在棋盘中的对应坐标
    elif com >= 0 and com <= 2:
        return [2, com]
    elif com >= 3 and com <= 5:
        return [1, com - 3]
    elif com >= 6 and com <= 8:
        return [0, com - 6]
    elif com == 65 or com == 66:
        # 检查是否存在胜者
        # 如果有, 返回[-1, -1]
        winner = checkWinner(board)
        if winner == 1:
            print("BLACK WIN!")
            return [-1, -1]
        elif winner == -1:
            print("WHITE WIN!")
            return [-1, -1]


        # 寻找最优位置
        bestMove = findBestMove(board, sideAI)
        print("BEST MOVE: ", bestMove)
        if bestMove == None:
            print("BEST_MOVE_CANNOT_FIND")
            return []

        # 将棋盘坐标转换为位置坐标
        return bestMove
    else:
        print("INVAILD_COMMAND_SYNTAX")
        return []

# 将坐标变换为索引
# 返回值: 数组[beginIndex, endIndex]
def posToIndex(pos):
    # 定义坐标对应的索引
    indexMap = {
        (): [0, 0],
        (-1,): [-1, -1],
        (0, 0): [48, 52],
        (0, 1): [53, 57],
        (0, 2): [58, 62],
        (1, 0): [63, 66],
        (1, 1): [67, 70],
        (1, 2): [71, 74],
        (2, 0): [75, 78],
        (2, 1): [79, 82],
        (2, 2): [83, 85],
    }

    index = indexMap.get(tuple(pos), [0, 0])
    print("posToIndex: ", index)
    return index

def countToIndex(count, sideAI):
    # 如果AI执白, 运行后五个指令
    if sideAI == -1:
        count += 5

    # 定义计数到索引的映射
    countMap = {
        0: [1, 5],
        1: [6, 10],
        2: [11, 15],
        3: [16, 20],
        4: [21, 25],
        5: [26, 29],
        6: [30, 33],
        7: [34, 38],
        8: [39, 42],
        9: [43, 47],
    }

    return countMap.get(count, [0, 0])  # 默认情况下返回[0, 0]

def moveToIndex(pos):
    # 定义移动的索引映射
    moveMap = {
        (0, 0): [86, 89],
        (0, 1): [90, 94],
        (0, 2): [95, 98],
        (1, 0): [99, 102],
        (1, 1): [103, 106],
        (1, 2): [107, 110],
        (2, 0): [111, 114],
        (2, 1): [115, 118],
        (2, 2): [119, 122],
    }

    index = moveMap.get(tuple(pos), [0, 0])  # 默认情况下返回[0, 0]
    print("moveToIndex: ", index)
    return index

