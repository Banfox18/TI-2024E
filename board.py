# board - By: Arctain - Wed Jul 30 2024
import math
"""
检测两个棋盘的棋子位置是否发生变化。

:param board_before: 变动前的棋盘（3x3二维数组）
:param board_after: 变动后的棋盘（3x3二维数组）
:return: 如果位置发生变化返回[[变动前的位置], [变动后的位置]]，
         否则返回空数组
"""
def detectMove(board_before, board_after):
    # 检查棋盘的规模是否一致
    if len(board_before) != len(board_after) or len(board_before[0]) != len(board_after[0]):
        raise ValueError("棋盘规模不一致")

    # 1. 检测棋子数量是否相同
    count_before = sum(cell != 0 for row in board_before for cell in row)
    count_after = sum(cell != 0 for row in board_after for cell in row)

    if count_before != count_after:
        return []  # 棋子数量不同，返回空数组

    # 2. 查找移动的棋子
    before_position = None
    after_position = None

    for i in range(len(board_before)):
        for j in range(len(board_before[i])):
            if board_before[i][j] != board_after[i][j]:  # 检查棋子是否发生变化
                if before_position is None and board_before[i][j] != 0:  # 检测变动前的位置
                    before_position = [i, j]  # 记录变动前的位置（行, 列）
                if after_position is None and board_after[i][j] != 0:  # 检测变动后的位置
                    after_position = [i, j]  # 记录变动后的棋子位置（行, 列）

    if before_position and after_position:
        return [before_position, after_position]  # 返回位置，格式为[[前位置], [后位置]]

    return []  # 如果没有检测到变化, 返回空数组

# 检查是否有胜利方
def checkWinner(board):
    for row in board:
        if sum(row) == 3:
            return 1
        if sum(row) == -3:
            return -1

    for col in range(3):
        if board[0][col] + board[1][col] + board[2][col] == 3:
            return 1
        if board[0][col] + board[1][col] + board[2][col] == -3:
            return -1

    if board[0][0] + board[1][1] + board[2][2] == 3 or board[0][2] + board[1][1] + board[2][0] == 3:
        return 1
    if board[0][0] + board[1][1] + board[2][2] == -3 or board[0][2] + board[1][1] + board[2][0] == -3:
        return -1

    return 0

# 检查棋盘是否满
def isMovesLeft(board):
    for row in board:
        if 0 in row:
            return True
    return False

# 检查棋盘是否空
def isBoardEmpty(board):
    for row in board:
        if row == [0, 0, 0]:
            continue
        else:
            return False
    return True
# 检查是否有即将胜利的位置，并返回该位置
def checkImmediateWin(board, side):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                board[i][j] = side
                if checkWinner(board) == side:
                    board[i][j] = 0
                    return (i, j)
                board[i][j] = 0
    return None

# 评估值
# 参数: board
# 返回值: 1获胜为+10，-1获胜为-10，平局返回0
def evaluate(board, sideAI):

    winner = checkWinner(board)
    if winner == sideAI:
        return 10
    elif winner == -sideAI:
        return -10
    return 0

# 参数: board, 递归深度, boolean

def miniMax(board, depth, isMax, sideAI):
    score = evaluate(board, sideAI)

    if score == 10:
        return score - depth
    if score == -10:
        return score + depth
    if not isMovesLeft(board):
        return 0

    if isMax:
        best = -math.inf # math.inf: 无穷大, 任何与该数做比大小都返回False
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    board[i][j] = sideAI
                    best = max(best, miniMax(board, depth + 1, not isMax, sideAI))
                    board[i][j] = 0
        return best
    else:
        best = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    board[i][j] = sideAI
                    best = min(best, miniMax(board, depth + 1, not isMax, sideAI))
                    board[i][j] = 0
        return best

# 寻找电脑落子最优位置
def findBestMove(board, sideAI):
    # 1 检查电脑是否可以直接获胜
    win_move = checkImmediateWin(board, sideAI)
    if win_move:
        return win_move

    #2 检查玩家是否可以直接获胜，若可以则拦截
    block_move = checkImmediateWin(board, -sideAI)
    if block_move:
        return block_move

    best_val = -math.inf
    best_move = (-1, -1)
    # 遍历棋盘, 找到评估值最大的一步return
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                # 如果该格为空, 放子
                board[i][j] = sideAI
                # 调用递归
                move_val = miniMax(board, 0, False, sideAI)
                board[i][j] = 0
                # 如果放置后的评估值大于当前评估值, 则该步作为当前评估值
                if move_val > best_val:
                    best_move = (i, j)
                    best_val = move_val

    return best_move
