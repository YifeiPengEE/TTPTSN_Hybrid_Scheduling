import head
from sympy import symbols, Piecewise, Eq, solve,Expr,Interval,Max,Min
import numpy as np
import matplotlib.pyplot as plt
import copy

class networkCalusculusToolsClass:
    def __init__(self):
        print('networkCalusculusToolsClass')

    def drawNCCurve(self,x, piecewise_functions, startPit, endPit, pitNum,lineColor='red',lineName='curve'):
        # 计算对应的 y 值并画出曲线
        # print('piecewise_functions = ', piecewise_functions)
        # 生成 x 值
        x_values = np.linspace(startPit, endPit, pitNum)

        # 将 SymPy 函数转换为 NumPy 函数
        piecewise_np = np.vectorize(lambda x_val: piecewise_functions.subs(x, x_val), otypes=[float])

        # 计算对应的 y 值
        y_values = piecewise_np(x_values)
        # 画出曲线
        plt.plot(x_values, y_values, lineColor, label=lineName)
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Piecewise Function')
        plt.legend()
        plt.grid(True)


    def createNormalNCCurve(self,curWinList, slope, startOffset, durTime):
        # 1.根据winList和startOffset调整出实际的actWinList
        # 1.1调整窗口偏移
        for win in curWinList:
            win[0] += startOffset
            win[1] += startOffset

        # 声明符号变量
        x = symbols('x')

        # 定义分段函数的列表
        piecewiseFunctionsList = []

        # 在循环中定义分段函数
        winNum = len(curWinList)
        bitCnt = 0
        for winCnt in range(winNum + 1):
            if winCnt == winNum:
                lastWin = curWinList[winCnt - 1]
                # 最后一段
                condition = (x >= lastWin[1])
                expression = bitCnt
                piecewiseFunctionsList.append((expression, condition))
            elif winCnt == 0:
                win = curWinList[winCnt]
                # 第一段
                condition = (x < win[0])
                expression = 0
                piecewiseFunctionsList.append((expression, condition))
                # 第二段
                condition = (x >= win[0]) & (x < win[1])
                expression = slope * (x - win[0]) + bitCnt
                piecewiseFunctionsList.append((expression, condition))
                bitCnt += win[1] - win[0]
            else:
                curWin = curWinList[winCnt]
                lastWin = curWinList[winCnt - 1]
                # 第一段
                condition = (x >= lastWin[1]) & (x < curWin[0])
                expression = bitCnt
                piecewiseFunctionsList.append((expression, condition))
                # 第二段
                condition = (x >= curWin[0]) & (x < curWin[1])
                expression = slope * (x - curWin[0]) + bitCnt
                piecewiseFunctionsList.append((expression, condition))
                bitCnt += curWin[1] - curWin[0]
        # print('piecewiseFunctionsList = ', piecewiseFunctionsList)

        piecewise_function = Piecewise(*piecewiseFunctionsList)
        # self.drawNCCurve(x, piecewise_function, 0, 2 * durTime, 1000)

        return piecewise_function

    def createReverseNCCurve(self, curWinList, slope, startOffset, durTime):
        delta = 0
        # 1.根据winList和startOffset调整出实际的actWinList
        # 1.1调整窗口偏移
        for win in curWinList:
            win[0] += startOffset
            win[1] += startOffset
         # 声明符号变量
        x = symbols('x')
        # 定义分段函数的列表
        piecewiseFunctionsList = []
        # 在循环中定义分段函数
        winNum = len(curWinList)
        bitCnt = 0
        deltaCnt = 0
        for winCnt in range(winNum + 1):
            if winCnt == winNum:
                lastWin = curWinList[winCnt - 1]
                # 第一段
                condition = (x >= bitCnt)
                expression = lastWin[1]
                piecewiseFunctionsList.append((expression, condition))
            elif winCnt == 0:
                win = curWinList[winCnt]
                # 第一段
                condition = (x<delta)
                expression = win[0]
                piecewiseFunctionsList.append((expression, condition))
                print(piecewiseFunctionsList)
                # 第二段
                diff = win[1] - win[0]
                condition = (x >= bitCnt+delta) & (x < bitCnt + diff)
                expression = (1/slope) * (x-bitCnt) + win[0]
                piecewiseFunctionsList.append((expression, condition))
                bitCnt += diff
            else:
                curWin = curWinList[winCnt]
                lastWin = curWinList[winCnt - 1]
                # 第一段
                condition = (x >= bitCnt) & (x < bitCnt + delta)
                expression = curWin[0]
                piecewiseFunctionsList.append((expression, condition))
                # 第二段
                diff = curWin[1] - curWin[0]
                condition = (x >= bitCnt+delta) & (x < bitCnt + diff)
                expression = (1/slope) * (x-bitCnt) + curWin[0]
                piecewiseFunctionsList.append((expression, condition))
                bitCnt += diff
        # print('piecewiseFunctionsList = ', piecewiseFunctionsList)

        piecewise_function = Piecewise(*piecewiseFunctionsList)
        # self.drawNCCurve(x, piecewise_function, 0, 2 * durTime, 1000)

        return piecewise_function

    # -------------------------------------------------
    # 函数名称：createNCCurve
    # 输入参数：
    # 输出参数：返回曲线（本质上是个分段函数）
    # 函数描述：
    # ①函数用于将Qbv的时隙结果，转化为网络演算中的曲线。Qbv的时隙输
    # 入转化为网络演算曲线，而对于TSN来说，事实上分段函数就足够表示所有网络演算中可能遇到的曲线了;
    #  ②其次为了方便计算，我们需要生成一条正常曲线，还需要生成一条反函数曲线，用来计算延时相关信息
    # -------------------------------------------------

    def createNCCurve(self,winList, slope, startOffset, durTime):
        # print('changeQbvToNC')
        curNormalWinList = copy.deepcopy(winList)
        curReverseWinList = copy.deepcopy(winList)
        normalNCCurve = self.createNormalNCCurve(curNormalWinList, slope, startOffset, durTime)
        reverseNCCureve = self.createReverseNCCurve(curReverseWinList, slope, startOffset, durTime)

        return normalNCCurve,reverseNCCureve


    def findMaxValue(self,piecewise_function,lowBound,highBound):
        #目前采用蒙特卡洛的方式获取最大值
        # 声明符号变量
        x = symbols('x')

       # 生成 x 值
        x_values = np.linspace(lowBound, highBound, 1000)

        # 将 SymPy 函数转换为 NumPy 函数
        piecewise_np = np.vectorize(lambda x_val: piecewise_function.subs(x, x_val), otypes=[float])

        # 计算对应的 y 值
        y_values = piecewise_np(x_values)


        max_values = y_values
        # 找到最大的最大值
        global_max_value = max(max_values)
        # print('max_values = ',max_values)
        # print(f"在范围 {lowBound,highBound} 内的最大值: {global_max_value}")
        return global_max_value

    def NCCalcLatency(self,winArrive,slopeArrive,startOffsetArrive,durTimeArrive
                      ,winService, slopeService, startOffsetService,durTimeService
                      ,lowBound,highBound,grun,drawFlag = False):
        x = symbols('x')
        arriveCurve, arriveCurveReverse = self.createNCCurve(winArrive, slopeArrive, startOffsetArrive, durTimeArrive)
        serviceCurve, serviceCurveReverse = self.createNCCurve(winService, slopeService, startOffsetService,
                                                                 durTimeService)

        # realServiceCurveReverse = Max(arriveCurveReverse, serviceCurveReverse)
        if drawFlag == True:
            self.drawNCCurve(x, arriveCurveReverse, lowBound, highBound, grun, 'red', 'arriveCurveReverse')
            self.drawNCCurve(x, serviceCurveReverse, lowBound, highBound, grun, 'green', 'serviceCurveReverse')
            # self.drawNCCurve(x, realServiceCurveReverse, lowBound, highBound, grun, 'black', 'realServiceCurveReverse')
            self.drawNCCurve(x, serviceCurveReverse - arriveCurveReverse, lowBound, highBound, grun, 'blue',
                             'Latency(ns)')
            plt.show()

        return self.findMaxValue(serviceCurveReverse - arriveCurveReverse,lowBound,highBound)

    def NCCalcBacklog(self,winArrive,slopeArrive,startOffsetArrive,durTimeArrive
                      ,winService, slopeService, startOffsetService,durTimeService
                      ,lowBound,highBound,grun,drawFlag = False):
        x = symbols('x')
        arriveCurve, arriveCurveReverse = self.createNCCurve(winArrive, slopeArrive, startOffsetArrive, durTimeArrive)
        serviceCurve, serviceCurveReverse = self.createNCCurve(winService, slopeService, startOffsetService,
                                                                 durTimeService)
        # realServiceCurve = Min(arriveCurve, serviceCurve)
        if drawFlag == True:
            self.drawNCCurve(x, arriveCurve, lowBound, highBound, grun, 'red', 'arriveCurve')
            self.drawNCCurve(x, serviceCurve, lowBound, highBound, grun, 'green', 'serviceCurve')
            # self.drawNCCurve(x, realServiceCurve, lowBound, highBound, grun, 'black', 'realServiceCurve')
            self.drawNCCurve(x, arriveCurve - serviceCurve, lowBound, highBound, grun, 'blue', 'Backlog(bit)')
            plt.show()

        return self.findMaxValue(arriveCurve - serviceCurve,lowBound,highBound)

    # -------------------------------------------------
    # 函数名称：createAffineCurve
    # 输入参数：r:增长率；sigma：突发量；grun是粒度，单位是ns；hP是是超周期，单位是ns
    # 输出参数：返回曲线（本质上是个分段函数）
    # 函数描述：
    # #仿射曲线一般形式为Rt+σ，也可以表示为R(t-D)其中D为延时，这里我们应该允许两种指定方式
    # 返回值，则返回list
    # -------------------------------------------------
    def createAffineCurve(self,r=500,sigma=100,grun = 1000,hP = 1000000):
        # 定义分段函数
        piecewiseFunctionsList = []
        x = symbols('x')
        # 第一段
        condition = (x <= 0)
        expression = sigma
        piecewiseFunctionsList.append((expression, condition))

        # 第二段
        condition = (x > 0)
        expression = (r * x ) / head.DEFAULT_ONE_MICRIOSEC + sigma
        piecewiseFunctionsList.append((expression, condition))

        piecewise_function = Piecewise(*piecewiseFunctionsList)
        self.drawNCCurve(x, piecewise_function, 0, 10, 100)
        # 生成 x 值
        x_values = [i for i in range(0, hP, grun)]
        # print(x_values)
        # 将 SymPy 函数转换为 NumPy 函数
        piecewise_np = np.vectorize(lambda x_val: piecewise_function.subs(x, x_val), otypes=[float])
        y_values = piecewise_np(x_values)
        # print(y_values)

        return  x_values,list(y_values)


    # -------------------------------------------------
    # 函数名称：createLatencyCurve
    # 输入参数：R:增长率；D：延时；grun是粒度，单位是ns；hP是是超周期，单位是ns
    # R的单位为Mbps
    # 输出参数：返回曲线（本质上是个分段函数）
    # 函数描述：
    # #仿射曲线一般形式为Rt+σ，也可以表示为R(t-D)其中D为延时，这里我们应该允许两种指定方式
    # 返回值，则返回list
    # -------------------------------------------------
    def createLatencyCurve(self,R=500,D=0,grun = 1000,hP = 1000000):
        print('R = ',R,'D = ',D,'grun = ',grun,'hP = ',hP)
        # 定义分段函数
        piecewiseFunctionsList = []
        x = symbols('x')
        # 第一段
        condition = (x <= D)
        expression = 0
        piecewiseFunctionsList.append((expression, condition))
        # 第二段
        condition = (x > D)
        expression = R * (x - D) / head.DEFAULT_ONE_MICRIOSEC
        piecewiseFunctionsList.append((expression, condition))

        piecewise_function = Piecewise(*piecewiseFunctionsList)
        self.drawNCCurve(x, piecewise_function, 0, 10, 100)
        # 生成 x 值
        x_values = [i for i in range(0, int(hP), int(grun))]
        # print(x_values)
        # 将 SymPy 函数转换为 NumPy 函数
        piecewise_np = np.vectorize(lambda x_val: piecewise_function.subs(x, x_val), otypes=[float])
        y_values = piecewise_np(x_values)


        return  x_values,list(y_values)
    # -------------------------------------------------
    # 函数名称：minPlusCov(f,g)
    # 输入参数：f:参与最小加卷积的f函数对应的point list；
    # g:参与最小加卷积的g函数对应的point list；
    # 输出参数：返回曲线（本质上是个分段函数）
    # 返回值：最小加卷积后的list
    # 函数描述：
    # -------------------------------------------------
    def minPlusCov(self,f, g):
        """
        对两个列表 f 和 g 进行卷积操作。
        列表的索引表示 t，函数计算并返回一个列表，每个索引 t 的元素
        是从 f(t-s) + g(s) 的值中找到的最小值，其中 s 在 0 到 t 之间。

        参数:
        f -- 第一个列表，表示函数 f 的值
        g -- 第二个列表，表示函数 g 的值

        返回值:
        result -- 一个列表，包含每个 t 索引位置的按照卷积规则计算出的最小值
        """
        # 初始化结果列表
        result = []
        # print('f = ',f)
        # print('g = ',g)
        # 计算结果列表中每个索引 t 的值
        for t in range(len(f)):
            # 计算 f(t-s) + g(s) 的最小值
            infimum = min(f[t - s] + g[s] for s in range(t + 1))
            # 将最小值添加到结果列表
            result.append(infimum)

        # 绘图
        # plt.figure(figsize=(20, 5))
        # plt.plot(f, label='f', marker='o', linestyle='-', color='blue')
        # plt.plot(g, label='g', marker='o', linestyle='-', color='green')
        # plt.plot(result, label='Result', marker='o', linestyle='-', color='black')
        # plt.title('Convolution of f and g')
        # plt.xlabel('Index (t)')
        # plt.ylabel('Value')
        # plt.grid(True)
        # plt.show()
        # print('ttttt = ', result)
        return result
    # -------------------------------------------------
    # 函数名称：worseLogback(self,f, g)
    # 函数别名：minPlusCov(f,g)(0)
    # 输入参数：f:参与最小加卷积的f函数对应的point list；
    # g:参与最小加卷积的g函数对应的point list；
    # 输出参数：本质上是利用最小加解卷积求得最差挤压
    # 函数描述：
    # -------------------------------------------------
    def worseLogback(self,f, g):
        """
        对两个列表 f 和 g 进行反卷积操作。
        列表的索引表示 t，函数计算并返回一个列表，每个索引 t 的元素
        是从 f(t+u) - g(u) 的值中找到的最大值，其中 u 在 0 到 len(f) 之间。已证明u处于这区间可以取到最大值

        参数:
        f -- 第一个列表，表示函数 f 的值
        g -- 第二个列表，表示函数 g 的值

        返回值:
        result -- 一个列表，包含每个 t 索引位置的按照卷积规则计算出的最大值（函数只返回t0时刻的值）
        """
        # 初始化结果列表
        result = []

        # 计算结果列表中每个索引 t 的值
        # for t in range(len(f)):
        #只计算t0的结果
        t = 0
        # 计算 f(t-s) + g(s) 的最小值
        infimum = max(f[t + u] - g[u] for u in range(0, len(f)))
        # 将最小值添加到结果列表
        result.append(infimum)
        return result[0]
    # -------------------------------------------------
    # 函数名称：worseDelay(self,f, g)
    # 函数别名：minPlusCov(f,g)(-d)
    # 输入参数：f:参与最小加卷积的f函数对应的point list；
    # g:参与最小加卷积的g函数对应的point list；
    # 输出参数：本质上是利用最小加解卷积求得最差延时
    # 函数描述：如果返回-1则说明求解错误
    # -------------------------------------------------
    def worstDelay(self,f, g,timeDur = 1.0):
        print('len(f) = ', f.__len__(), 'len(g) = ',g.__len__())
        MAX = len(f)  # 计算列表的长度
        # 遍历所有可能的t值
        for t in range(0, -MAX, -1):  # t的范围是0到-MAX（不包括）
            all_satisfy = True  # 假设对于这个t，所有u都满足条件
            # 遍历所有可能的u值
            for u in range(-t, MAX):
                if t + u >= MAX or f[t + u] - g[u] > 0:  # 检查f(t+u)-g(u)是否≤0
                    all_satisfy = False
                    break  # 如果有一个u不满足条件，跳出内层循环
            if all_satisfy:  # 如果对于当前的t，所有u都满足条件
                return -t * timeDur  # 返回-t的值
        return -1  # 如果没有找到符合条件的t，返回-1





def demoCreateAffineCurve():


    #创建网络演算工具
    NCtool = networkCalusculusToolsClass()

    x,f = NCtool.createAffineCurve(r=5,sigma=25,grun = 1,hP = 10)
    _,g = NCtool.createLatencyCurve(R=30,D=5,grun = 1,hP = 10)

    NCtool.minPlusCov(f,g)
    print('worst logBack = ',NCtool.worseLogback(f,g))
    print('worst delay = ', NCtool.worstDelay(f,g))
    # h = Piecewise((f, f < g), (g, f >= g))
    # NCtool.drawNCCurve(x, h, 0, 10, 100,lineColor='green')
    plt.show()


def demo1():
    x = symbols('x')
    #创建网络演算工具
    NCtool = networkCalusculusToolsClass()

    winArrive = [[0,1],[5,10],[20,30]]#
    slopeArrive = 1
    startOffsetArrive = 0
    durTimeArrive = 50

    winService = [[3,4],[20,35]]#
    slopeService = 1
    startOffsetService = 10
    durTimeService = 50
    # demo()

    #创建曲线
    # arriveCurve,arriveCurveReverse = NCtool.createNCCurve(winArrive,slopeArrive,startOffsetArrive,durTimeArrive)
    # serviceCurve,serviceCurveReverse = NCtool.createNCCurve(winService, slopeService, startOffsetService, durTimeService)
    #
    # NCtool.drawNCCurve(x, arriveCurve, 0, 2 * durTimeService, 1000,'red','arriveCurve')
    # NCtool.drawNCCurve(x, serviceCurve, 0, 2 * durTimeService, 1000,'green','serviceCurve')
    # NCtool.drawNCCurve(x, arriveCurve - serviceCurve, 0, 2 * durTimeService, 1000,'blue','zuocha')
    # plt.show()
    #
    # NCtool.drawNCCurve(x, arriveCurveReverse, 0, 16, 1000,'red','arriveCurveReverse')
    # NCtool.drawNCCurve(x, serviceCurveReverse, 0, 16, 1000, 'green', 'serviceCurveReverse')
    # NCtool.drawNCCurve(x, serviceCurveReverse - arriveCurveReverse, 0, 16, 1000, 'blue', 'zuocha')
    # plt.show()
    #
    # NCtool.findMaxValue(serviceCurveReverse - arriveCurveReverse,0,16)

    NCtool.NCCalcLatency(winArrive,slopeArrive,startOffsetArrive,2 * durTimeArrive
                         ,winService, slopeService, startOffsetService,2 * durTimeService
                         ,0,16,1000,True)

    NCtool.NCCalcBacklog(winArrive,slopeArrive,startOffsetArrive,2 * durTimeArrive
                         ,winService, slopeService, startOffsetService,2 * durTimeService
                         ,0,2 * durTimeService,1000,True)


if __name__ == '__main__':
    # demo1()
    demoCreateAffineCurve()


