from pickle import TRUE
from play import AI,Play
import math                        
import random           
import numpy as np

def ParameterSetting():
    problem = "othello_opt"         
    varNum = 3         
    # 搜索空间上下限           
    xMin = [0.01, 1, 10]         
    xMax = [0.05, 5, 50]
    tInitial = 100.0           
    tFinal  = 60             
    # 降温参数
    alpha    = 0.8              
    # 内循环运行次数
    innerLoopLen = 5     
    # 搜索步长       
    step   = 0.5               
    return problem, varNum, xMin, xMax, tInitial, tFinal, alpha, innerLoopLen, step

def calculate(xNew,xNow):
    solValue=0
    black_player=AI('X',xNew[0],xNew[1],xNew[2])
    white_player=AI('O',xNow[0],xNow[1],xNow[2])
    play=Play(black_player,white_player)
    result=play.playOthello()
    if result==0:
    #xNew更优
        solValue+=1
    return solValue
    
def SA(varNum,xMin,xMax,tInitial,tFinal,alpha,innerLoopLen,step):
# 初始化开始
    # 创建数组
    xInitial = np.zeros((varNum))   
    for v in range(varNum):
        xInitial[v] = random.uniform(xMin[v], xMax[v])
    xNew = np.zeros((varNum))      
    xNow = np.zeros((varNum))        
    xBest = np.zeros((varNum))      
    xNow[:]  = xInitial[:]     
    xBest[:] = xInitial[:]
    print('x_Initial:{:.6f},{:.6f},\t'.format(xInitial[0], xInitial[1]))
    # 外循环次数
    recordIter = []     
    # 当前解的目标函数值            
    recordxNow = []  
    # 最佳解的目标函数值              
    recordxBest = []         
    # 劣质解的接受概率      
    recordPBad = []     
    # 外循环迭代次数，温度状态数            
    kIter = 0          
    # 总计内循环次数            
    innerIterSum = 0
    # 内循环次数
    nInnerIter = innerLoopLen
#初始化结束

#算法开始
    # 外循环开始
    tNow = tInitial               
    while tNow >= tFinal:
        # 获得优质解、接受优解、拒绝劣解的次数
        kBetter = 0                 
        kBadAccept = 0       
        kBadRefuse = 0           

        #内循环开始
        for k in range(nInnerIter):   
            innerIterSum += 1      

            # 产生新解：只改一个解
            xNew[:] = xNow[:]
            v = random.randint(0, varNum-1)  
            xNew[v] = xNow[v] + step * (xMax[v]-xMin[v]) * random.normalvariate(0, 1)
            # 保证新解范围内
            xNew[v] = max(min(xNew[v], xMax[v]), xMin[v])  

            # 能量差简化为1
            deltaE = 1

            # 按 Metropolis 准则接受新解，如果新解的目标函数好于当前解，则接受新解
            if calculate(xNew,xNow):
                accept = True
                kBetter += 1
            else:  
                pAccept = math.exp(-deltaE / tNow) 
                if pAccept > random.random():
                    accept = TRUE
                    kBadAccept += 1
                else:
                    accept = False 
                    kBadRefuse += 1

            # 保存新解
            # 如果接受新解，则将新解保存为当前解
            if accept == True:  
                xNow[:] = xNew[:]
                # 如果新解的目标函数好于最优解，则将新解保存为最优解
                if calculate(xNew,xBest):  
                    xBest = xNew
                    xBest[:] = xNew[:]
                    # 可变搜索步长，逐步减小搜索范围，提高搜索精度
                    step = step*0.99  
                    
        # 内循环结束，保存数据
        # 劣质解的接受概率
        pBadAccept = kBadAccept / (kBadAccept + kBadRefuse)  
        # 当前外循环次数
        recordIter.append(kIter)  
        recordxNow.append(xNow) 
        recordxBest.append(xBest)  
        #四位小数
        recordPBad.append(round(pBadAccept, 4)) 
        # 定时输出一下劣解接受概率
        if kIter%10 == 0:                           
            print('i:{},t(i):{:.2f}, badAccept:{:.6f}'.\
                format(kIter, tNow, pBadAccept))

        # 降温
        tNow = tNow * alpha
        kIter = kIter + 1
    #外循环结束
#算法结束

    return kIter,xBest,xNow,recordIter,recordxNow,recordxBest,recordPBad

# 结果校验与输出
def ResultOutput(problem,varNum,xBest,kIter,recordxNow,recordxBest,recordPBad,recordIter):
    print("\n优化结果:")
    for i in range(varNum):
        print('\tx[{}] = {:.6f}'.format(i,xBest[i]))
        
    return

def main():
    [problem, varNum, xMin, xMax, tInitial, tFinal, alpha, innerLoopLen, step] = ParameterSetting()
    [kIter,xBest,xNow,recordIter,recordxNow,recordxBest,recordPBad] \
        = SA(varNum,xMin,xMax,tInitial,tFinal,alpha,innerLoopLen,step)
    ResultOutput(problem, varNum,xBest,kIter,recordxNow,recordxBest,recordPBad,recordIter)

if __name__ == '__main__':
    main()