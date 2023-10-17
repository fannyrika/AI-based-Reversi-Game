import pysnooper
from copy import deepcopy
class Grid(object):
    def __init__(self):
        self.mygrid=[ ['*' for row in range(8)] for col in range(8)]
        self.mygrid[3][3], self.mygrid[4][4]='O','O'
        self.mygrid[3][4], self.mygrid[4][3]='X','X'
        self.empty='*'

    def count(self,type):
        num=0
        for row in range(8):
            for col in range(8):
                if self.mygrid[row][col]==type:
                    num+=1
        return num
    
    
    def __getitem__(self, index):
        return self.mygrid[index]
    def countBoth(self):
        black_num=0
        white_num=0
        for row in range(8):
            for col in range(8):
                if self.mygrid[row][col]=='X':
                    black_num+=1
                if self.mygrid[row][col]=='O':
                    white_num+=1
        return black_num,white_num
    
    def countCorners(self,type):
        cnt=0
        grid=self.mygrid
        if grid[0][0]==type:
            cnt += 1
        if grid[0][7]==type:
            cnt += 1
        if grid[7][7]==type:
            cnt += 1
        if grid[7][0]==type:
            cnt += 1
        return cnt
    
    def see(self, step_time=None, total_time=None):
        grid = self.mygrid
        print("棋局分布情况：")
        print("R\C A B C D E F G H")
        for row in range(8):
            print(str(row+1),' ', ' '.join(grid[row]))

    def whoWon(self):
        black_count, white_count = 0, 0
        for i in range(8):
            for j in range(8):
                if self.mygrid[i][j] == 'X':
                    black_count += 1
                if self.mygrid[i][j] == 'O':
                    white_count += 1
        if black_count > white_count:
            # 黑棋胜
            return 0, black_count - white_count
        elif black_count < white_count:
            # 白棋胜
            return 1, white_count - black_count
        elif black_count == white_count:
            # 表示平局，黑棋个数和白旗个数相等
            return 2, 0
        
    #@pysnooper.snoop("C:/Users/Administrator/Desktop/ai_lab2_log/debug.log", prefix="--*--")
    def NextStatus(self, action, type):
        # 判断action 是不是字符串，如果是则转化为数字坐标
        if isinstance(action, str):
            action = self.StrToArray(action)

        fliped = self.GetReverseGrid(action, type)

        if fliped:
            for flip in fliped:
                x, y = self.StrToArray(flip)
                self.mygrid[x][y] = type

            # 落子坐标
            x, y = action
            # 更改棋盘上 action 坐标处的状态，修改之后该位置属于 type[X,O,.]等三状态
            self.mygrid[x][y] = type
            return fliped
        else:
            # 没有反转子则落子失败
            return False
    
    def isWithinRange(self, x, y):
        return x >= 0 and x <= 7 and y >= 0 and y <= 7
    
    def StrToArray(self, position):
        row='12345678'.index(str(position[1]))
        col='ABCDEFGH'.index(str(position[0]))
        return row, col
    
    #输入元组
    def ArrayToStr(self, act_tuple):
        row,col=act_tuple
        return chr( ord('A')+col )+str(row+1) 

    def BP(self, action, flipped_pos, type):
        # 判断action 是不是字符串，如果是则转化为数字坐标
        if isinstance(action, str):
            action = self.StrToArray(action)

        self.mygrid[action[0]][action[1]] = self.empty
        # 如果 type == 'X'，则 op_type = 'O';否则 op_type = 'X'
        op_type = "O" if type == "X" else "X"

        for p in flipped_pos:
            if isinstance(p, str):
                p = self.StrToArray(p)
            self.mygrid[p[0]][p[1]] = op_type

    def GetReverseGrid(self, action, type):
        if isinstance(action, str):
            action = self.StrToArray(action)
        xstart, ystart = action

        # 如果该位置已经有棋子或者出界，返回 False
        if not self.isWithinRange(xstart, ystart) or self.mygrid[xstart][ystart] != self.empty:
            return False

        # 临时将type放到指定位置
        self.mygrid[xstart][ystart] = type
        # 棋手
        op_type = "O" if type == "X" else "X"

        # 要被翻转的棋子
        flipped_pos = []
        flipped_pos_board = []

        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0],
                                       [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection
            y += ydirection
            # 如果(x,y)在棋盘上，而且为对方棋子,则在这个方向上继续前进，否则循环下一个角度。
            if self.isWithinRange(x, y) and self.mygrid[x][y] == op_type:
                x += xdirection
                y += ydirection
                # 进一步判断点(x,y)是否在棋盘上，如果不在棋盘上，继续循环下一个角度,如果在棋盘上，则进行while循环。
                if not self.isWithinRange(x, y):
                    continue
                # 一直走到出界或不是对方棋子的位置
                while self.mygrid[x][y] == op_type:
                    # 如果一直是对方的棋子，则点（x,y）一直循环，直至点（x,y)出界或者不是对方的棋子。
                    x += xdirection
                    y += ydirection
                    # 点(x,y)出界了和不是对方棋子
                    if not self.isWithinRange(x, y):
                        break
                # 出界了，则没有棋子要翻转OXXXXX
                if not self.isWithinRange(x, y):
                    continue

                # 是自己的棋子OXXXXXXO
                if self.mygrid[x][y] == type:
                    while True:
                        x -= xdirection
                        y -= ydirection
                        # 回到了起点则结束
                        if x == xstart and y == ystart:
                            break
                        # 需要翻转的棋子
                        flipped_pos.append([x, y])

        # 将前面临时放上的棋子去掉，即还原棋盘
        self.mygrid[xstart][ystart] = self.empty  # restore the empty space

        # 没有要被翻转的棋子，则走法非法。返回 False
        if len(flipped_pos) == 0:
            return False

        for fp in flipped_pos:
            flipped_pos_board.append(self.ArrayToStr(fp))
        # 走法正常，返回翻转棋子的棋盘坐标
        return flipped_pos_board

    def GetLegalPos(self, type):
        direction = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]

        op_type = "O" if type == "X" else "X"
        # 统计 op_type 一方邻近的未落子状态的位置
        op_type_near_points = []

        grid = self.mygrid
        for i in range(8):
            # i 是行数，从0开始，j是列数，也是从0开始
            for j in range(8):
                # 判断棋盘[i][j]位子棋子的属性，如果是op_type，则继续进行下一步操作，
                # 否则继续循环获取下一个坐标棋子的属性
                if grid[i][j] == op_type:
                    # dx，dy 分别表示[i][j]坐标在行、列方向上的步长，direction 表示方向坐标
                    for dx, dy in direction:
                        x, y = i + dx, j + dy
                        # 表示x、y坐标值在合理范围，棋盘坐标点board[x][y]为未落子状态，
                        # 而且（x,y）不在op_type_near_points 中，统计对方未落子状态位置的列表才可以添加该坐标点
                        if 0 <= x <= 7 and 0 <= y <= 7 and grid[x][y] == self.empty and (
                                x, y) not in op_type_near_points:
                            op_type_near_points.append((x, y))
        l = [0, 1, 2, 3, 4, 5, 6, 7]
        legalList=[]
        for p in op_type_near_points:
            if self.GetReverseGrid(p, type):
                if p[0] in l and p[1] in l:
                    p = self.ArrayToStr(p)
                legalList.append(p)
        return legalList
