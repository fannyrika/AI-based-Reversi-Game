from func_timeout import func_timeout, FunctionTimedOut
import datetime
from grid import Grid
from copy import deepcopy
INF=9999999

class Me:
    def __init__(self, type):
        self.type = type
    

    def GetNextStatus(self, grid):
        if self.type == "X":
            gamer = "黑棋"
        else:
            gamer = "白棋"
        while True:
            action = input(
                    "请'{}-{}'输入: ".format(gamer,self.type))

            if action == "Q" or action == 'q':
                return "Q"
            else:
                row, col = action[1].upper(), action[0].upper()

                if row in '12345678' and col in 'ABCDEFGH':
                    if action in grid.GetLegalPos(self.type):
                        return action
                else:
                    print("重新输入")

class AI:
    d = 0
    MAXd = 3
    def __init__(self,type,gapW,cornerW,mobilityW):
        self.gapW, self.cornerW, self.mobilityW=gapW,cornerW,mobilityW
        self.type=type
        
    def setWeight(self,gapW, cornerW, mobilityW):
        self.gapW, self.cornerW, self.mobilityW=gapW, cornerW, mobilityW
        
    def evaluate(self,grid,type):
        '''
        (1) f(局面) = 子力(我的子数 - 对手的子数)
        (2) g(局面) = 角(我控制的 - 对手控制的)
        (3) h(局面) = 机动性(我可以走的)
        组合这些函数来构成一个评价函数：eval = gapWeight·f + cornerWeight·g + mobilityWeight·h
        '''
        black_num, white_num=grid.countBoth()
        if type == 'X':
            gap=black_num-white_num
        else:
            gap=white_num-black_num
        value=int(self.gapW*gap +self.cornerW*grid.countCorners(type) +self.mobilityW*len( list(grid.GetLegalPos(type) )))
        return value

    def miniMax(self,grid,type,a,b):
        if self.d > self.MAXd:  #end
            if type == self.type:
                return None, self.evaluate(grid,type)
            else:
                return None, -self.evaluate(grid,type)

        if type == 'X':
            typeNext ='O'
        else:
            typeNext ='X'
        action_list = list(grid.GetLegalPos(type))
        if len(action_list) == 0:
            if len(list(grid.GetLegalPos(typeNext))) == 0:
                return None,self.evaluate(grid,type)
            return self.miniMax(grid,typeNext,a,b)
        
        max = -INF
        min = INF
        action = None

        for p in action_list:

            flipped_pos = grid.NextStatus(p,type)
            self.d += 1
            p1, current = self.miniMax(grid,typeNext,a,b)
            self.d -= 1
            grid.BP(p,flipped_pos,type)
            
            # alpha-beta 剪枝
            if type == self.type:
                if current > a:
                    if current > b:
                        return p,current
                    a = current
                if current > max:
                    max = current
                    action = p

            else:
                if current < b:
                    if current < a:
                        return p,current
                    b = current
                if current < min:
                    min = current
                    action = p
        if type == self.type:
            return action,max
        else:
            return action,min         


    def GetNextStatus(self, grid):
        if self.type == 'X':
            gamer_name = '黑棋'
        else:
            gamer_name = '白棋'
        print("轮到 {}-{} 落子".format(gamer_name, self.type))
        action_list = list(grid.GetLegalPos(self.type))
        
        action, weight = self.miniMax(grid,self.type,-INF,INF)
        print("本次落子得分：",weight)

        if len(action_list) == 0:
            return None
        print(action_list)
        print(action)
        return action

class Play(object):
    def __init__(self, blackGamer, whiteGamer):
        self.grid = Grid()
        self.current_gamer = None
        self.blackGamer = blackGamer
        self.whiteGamer = whiteGamer
        self.blackGamer.type = "X"
        self.whiteGamer.type = "O"
    
    def printWhoWon(self, winIndex):
        print(['胜者为黑棋', '胜者为白棋', '平局'][winIndex])

    def changeGamer(self, blackGamer, whiteGamer):
        if self.current_gamer is None:
            return blackGamer
        else:
            if self.current_gamer == self.blackGamer:
                return whiteGamer
            else:
                return blackGamer

    def foul(self, is_timeout=False, is_board=False, is_legal=False):
        if self.current_gamer == self.blackGamer:
            win_type = '白棋 - O'
            loss_type = '黑棋 - X'
            winIndex = 1
        else:
            win_type = '黑棋 - X'
            loss_type = '白棋 - O'
            winIndex = 0

        if is_timeout:
            print('\n{} 超时, {} 胜'.format(loss_type, win_type))
        if is_legal:
            print('\n{} 落子 3 次不符合规则,故 {} 胜'.format(loss_type, win_type))
        if is_board:
            print('\n{} 擅自改动棋盘判输,故 {} 胜'.format(loss_type, win_type))

        gap = 0

        return winIndex, gap
        
    def gameOver(self):
        b_list = list(self.grid.GetLegalPos('X'))
        w_list = list(self.grid.GetLegalPos('O'))

        overFlag = len(b_list) == 0 and len(w_list) == 0  

        return overFlag

    def playOthello(self):
        # 初始化胜负结果和棋子差
        winIndex = None
        gap = -1

        # 游戏开始
        print('\n---Game Start\n')
        # 棋盘初始化
        self.grid.see()
        while True:
            self.current_gamer = self.changeGamer(self.blackGamer, self.whiteGamer)
            start_time = datetime.datetime.now()
            type = "X" if self.current_gamer == self.blackGamer else "O"
            # 获取当前下棋方合法落子位置
            legal_actions = list(self.grid.GetLegalPos(type))
            if len(legal_actions) == 0:
                if self.gameOver():
                    # 游戏结束，双方都没有合法位置
                    winIndex, gap = self.grid.whoWon()
                    break
                else:
                    # 另一方有合法位置,切换下棋方
                    continue

            grid = deepcopy(self.grid.mygrid)

            # legal_actions 不等于 0 则表示当前下棋方有合法落子位置
            try:
                for i in range(0, 3):
                    # 获取落子位置
                    action = func_timeout(60, self.current_gamer.GetNextStatus,kwargs={'grid': self.grid})
                    if action not in legal_actions:
                        # 判断当前下棋方落子是否符合合法落子,如果不合法,则需要对方重新输入
                        print("不合法，请重新落子")
                        continue
                    else:
                        # 落子合法则直接 break
                        break
                else:
                    # 落子3次不合法
                    winIndex, gap = self.foul(is_legal=True)
                    break
            except FunctionTimedOut:
                # 落子超时，结束游戏
                winIndex, gap = self.foul(is_timeout=True)
                break

            # 结束时间
            end_time = datetime.datetime.now()
            if grid != self.grid.mygrid:
                # 修改棋盘，结束游戏
                winIndex, gap = self.foul(is_board=True)
                break
            if action is None:
                continue
            else:
                # 统计一步所用的时间
                es_time = (end_time - start_time).seconds
                if es_time > 60:
                    # 该步超过60秒则结束比赛。
                    print('\n{} 超时'.format(self.current_gamer))
                    winIndex, gap = self.foul(is_timeout=True)
                    break

                # 当前玩家颜色，更新棋局
                self.grid.NextStatus(action, type)
                # 显示当前棋盘
                self.grid.see()

                # 判断游戏是否结束
                if self.gameOver():
                    # 游戏结束
                    winIndex, gap = self.grid.whoWon()  # 得到赢家 0,1,2
                    break

        print('\n---End of the game\n')
        self.grid.see()
        self.printWhoWon(winIndex)


        if winIndex is not None and gap > -1:
            return winIndex

def main():
    blackGamer = AI("X", 0.025044, 4.541892, 37.444960)
    whiteGamer = Me("O")
    play = Play(blackGamer, whiteGamer)
    play.playOthello()

if __name__ == '__main__':
    main()