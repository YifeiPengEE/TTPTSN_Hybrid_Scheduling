import sys
sys.path.append('..')
from head import *
import time
import psutil

def actrualRouteAlg(topoMatrix,swNum,esNum,flowObjList):
    ourAlgFlag = 1
    ilpAlgFlag = 1
    enhanceAlgFlag = 1
    orrAlgFlag = 1
    # 网络评估
    evalBdLinkavgList = [0.0,0.0,0.0,0.0]
    evalBdLinkmaxList = [0.0,0.0,0.0,0.0]
    evalRoutelenFlowavgList = [0.0,0.0,0.0,0.0]
    evalRoutelenFlowmaxList = [0.0,0.0,0.0,0.0]
    evalArlfLinkavgList = [0.0,0.0,0.0,0.0]
    evalArlfLinkmaxList = [0.0,0.0,0.0,0.0]
    evalArdfNodeavgList = [0.0,0.0,0.0,0.0]
    evalArdfNodemaxList = [0.0,0.0,0.0,0.0]
    netEvalTool = network_eval_tools()
    networkOpTool = network_op_tools()
    if ourAlgFlag == 1:
        # x.创建调度器
        tsnRecurScheTool = tsnRecurSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, flowObjList)
        # x.进行路由
        tsnRecurScheTool.routeMethod(netTopo, tf)
        # 路由评估
        evalBdLinkavg 		= netEvalTool.eval_bd_linkavg(netTopo)
        evalBdLinkmax 		= netEvalTool.eval_bd_linkmax(netTopo)
        evalRoutelenFlowavg = netEvalTool.eval_routelen_flowavg(tf)
        evalRoutelenFlowmax = netEvalTool.eval_routelen_flowmax(tf)
        evalArlfLinkavg 	= netEvalTool.eval_arlf_linkavg(netTopo)
        evalArlfLinkmax 	= netEvalTool.eval_arlf_linkmax(netTopo)
        evalArdfNodeavg 	= netEvalTool.eval_ardf_nodeavg(netTopo)
        evalArdfNodemax 	= netEvalTool.eval_ardf_nodemax(netTopo)

        evalBdLinkavgList		[0]= evalBdLinkavg
        evalBdLinkmaxList 		[0]= evalBdLinkmax
        evalRoutelenFlowavgList [0]= evalRoutelenFlowavg
        evalRoutelenFlowmaxList [0]= evalRoutelenFlowmax
        evalArlfLinkavgList 	[0]= evalArlfLinkavg
        evalArlfLinkmaxList 	[0]= evalArlfLinkmax
        evalArdfNodeavgList 	[0]= evalArdfNodeavg
        evalArdfNodemaxList 	[0]= evalArdfNodemax

    if ilpAlgFlag == 1:
        # x.创建调度器
        ilpBasedMultiFlowTool = ilpbasedMultiFlowSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        # tf = trafficClass(netTopo, flowObjList)
        tf = trafficClass(netTopo, networkOpTool.flowSetRoutePostHandle_bandwith(flowObjList))
        # x.进行路由
        ilpBasedMultiFlowTool.route(netTopo, tf)
        ilpBasedMultiFlowTool.routeSolve(netTopo, tf)
        # 路由评估
        evalBdLinkavg 		= netEvalTool.eval_bd_linkavg(netTopo)
        evalBdLinkmax 		= netEvalTool.eval_bd_linkmax(netTopo)
        evalRoutelenFlowavg = netEvalTool.eval_routelen_flowavg(tf)
        evalRoutelenFlowmax = netEvalTool.eval_routelen_flowmax(tf)
        evalArlfLinkavg 	= netEvalTool.eval_arlf_linkavg(netTopo)
        evalArlfLinkmax 	= netEvalTool.eval_arlf_linkmax(netTopo)
        evalArdfNodeavg 	= netEvalTool.eval_ardf_nodeavg(netTopo)
        evalArdfNodemax 	= netEvalTool.eval_ardf_nodemax(netTopo)

        evalBdLinkavgList		[1]= evalBdLinkavg
        evalBdLinkmaxList 		[1]= evalBdLinkmax
        evalRoutelenFlowavgList [1]= evalRoutelenFlowavg
        evalRoutelenFlowmaxList [1]= evalRoutelenFlowmax
        evalArlfLinkavgList 	[1]= evalArlfLinkavg
        evalArlfLinkmaxList 	[1]= evalArlfLinkmax
        evalArdfNodeavgList 	[1]= evalArdfNodeavg
        evalArdfNodemaxList 	[1]= evalArdfNodemax


    if enhanceAlgFlag == 1:
        # x.创建调度器
        enhanceSchedTool = enhanceSchedAndThroughputSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, flowObjList)
        # x.进行路由
        enhanceSchedTool.route(netTopo, tf)
        # 路由评估
        evalBdLinkavg 		= netEvalTool.eval_bd_linkavg(netTopo)
        evalBdLinkmax 		= netEvalTool.eval_bd_linkmax(netTopo)
        evalRoutelenFlowavg = netEvalTool.eval_routelen_flowavg(tf)
        evalRoutelenFlowmax = netEvalTool.eval_routelen_flowmax(tf)
        evalArlfLinkavg 	= netEvalTool.eval_arlf_linkavg(netTopo)
        evalArlfLinkmax 	= netEvalTool.eval_arlf_linkmax(netTopo)
        evalArdfNodeavg 	= netEvalTool.eval_ardf_nodeavg(netTopo)
        evalArdfNodemax 	= netEvalTool.eval_ardf_nodemax(netTopo)

        evalBdLinkavgList		[2]= evalBdLinkavg
        evalBdLinkmaxList 		[2]= evalBdLinkmax
        evalRoutelenFlowavgList [2]= evalRoutelenFlowavg
        evalRoutelenFlowmaxList [2]= evalRoutelenFlowmax
        evalArlfLinkavgList 	[2]= evalArlfLinkavg
        evalArlfLinkmaxList 	[2]= evalArlfLinkmax
        evalArdfNodeavgList 	[2]= evalArdfNodeavg
        evalArdfNodemaxList 	[2]= evalArdfNodemax

    if orrAlgFlag == 1:
        # x.创建调度器
        OrrSchedTool = OrrTsnSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, flowObjList)
        # x.进行路由
        OrrSchedTool.route(netTopo, tf)
        # 路由评估
        evalBdLinkavg 		= netEvalTool.eval_bd_linkavg(netTopo)
        evalBdLinkmax 		= netEvalTool.eval_bd_linkmax(netTopo)
        evalRoutelenFlowavg = netEvalTool.eval_routelen_flowavg(tf)
        evalRoutelenFlowmax = netEvalTool.eval_routelen_flowmax(tf)
        evalArlfLinkavg 	= netEvalTool.eval_arlf_linkavg(netTopo)
        evalArlfLinkmax 	= netEvalTool.eval_arlf_linkmax(netTopo)
        evalArdfNodeavg 	= netEvalTool.eval_ardf_nodeavg(netTopo)
        evalArdfNodemax 	= netEvalTool.eval_ardf_nodemax(netTopo)

        evalBdLinkavgList		[3]= evalBdLinkavg
        evalBdLinkmaxList 		[3]= evalBdLinkmax
        evalRoutelenFlowavgList [3]= evalRoutelenFlowavg
        evalRoutelenFlowmaxList [3]= evalRoutelenFlowmax
        evalArlfLinkavgList 	[3]= evalArlfLinkavg
        evalArlfLinkmaxList 	[3]= evalArlfLinkmax
        evalArdfNodeavgList 	[3]= evalArdfNodeavg
        evalArdfNodemaxList 	[3]= evalArdfNodemax

    return evalBdLinkavgList,evalBdLinkmaxList\
        ,evalRoutelenFlowavgList,evalRoutelenFlowmaxList\
        ,evalArlfLinkavgList,evalArlfLinkmaxList\
        ,evalArdfNodeavgList,evalArdfNodemaxList

def dbPrint(topoMatix, swNum, esNum,flowObjList):
    #x.创建打印工具
    debugTool = debugToolClass()
    #x.生成netTopoClass
    netTopo = netTopoClass(topoMatix, swNum, esNum)
    # x.分析流量
    tf = trafficClass(netTopo, flowObjList)
    #x.打印
    debugTool.printTrafficClass(tf)
    # x.创建绘画工具
    net_draw_tool = NetworkDrawTools(1, 1)
    net_draw_tool.networkTopoPlot(topoMatix,esNum,swNum)
    #x.打印邻接矩阵
    i=0
    for heng in topoMatix:
        print(i,' = ',heng)
        i = i + 1

def routeAlgCompare():
    # sys.setrecursionlimit(10000)


    maxTopoNum = 20
    messageLenRnge = (64,1000)
    messagePeriod = [100000,200000,400000,500000]
    messgaeNum = [50,100,150,200,250,300]

    # messageLenRnge = (64,1500)
    # messagePeriod = [1000000]
    # messgaeNum = [50]

    expTopo = {'small':[4,8],'medium':[8,16],'larger Medium':[16,32]}
    # expTopo = {'small': [8, 16]}
    #x.创建拓扑
    rG = randomGraph()

    #1.示例1生成k完全图
    swNum = 4
    esNum = 8

    for key, value in expTopo.items():
        swNum = value[0]
        esNum = value[1]
        #1.要做五次实验
        for flowNum in messgaeNum:

            flowCase_evalBdLinkavgList = [0.0, 0.0, 0.0, 0.0]
            flowCase_evalBdLinkmaxList = [0.0, 0.0, 0.0, 0.0]
            flowCase_evalRoutelenFlowavgList = [0.0, 0.0, 0.0, 0.0]
            flowCase_evalRoutelenFlowmaxList = [0.0, 0.0, 0.0, 0.0]
            flowCase_evalArlfLinkavgList = [0.0, 0.0, 0.0, 0.0]
            flowCase_evalArlfLinkmaxList = [0.0, 0.0, 0.0, 0.0]
            flowCase_evalArdfNodeavgList = [0.0, 0.0, 0.0, 0.0]
            flowCase_evalArdfNodemaxList = [0.0, 0.0, 0.0, 0.0]

            for _ in range(maxTopoNum):
                #随机邻接矩阵
                topoMatrix = rG.generate_network(esNum, swNum)
                # x.创建流量生成器
                tgTool = trafficGeneratorToolClass()
                flowObjList = tgTool.generateRandomTTRCFlows(swNum, esNum, messagePeriod,messageLenRnge, flowNum, 0)

                #debug
                # dbPrint(topoMatrix,swNum,esNum,flowObjList)
                evalBdLinkavgList, evalBdLinkmaxList, evalRoutelenFlowavgList, evalRoutelenFlowmaxList, evalArlfLinkavgList, evalArlfLinkmaxList, evalArdfNodeavgList, evalArdfNodemaxList = actrualRouteAlg(
                    topoMatrix, swNum, esNum, flowObjList)

                flowCase_evalBdLinkavgList = [x + y for x, y in zip(flowCase_evalBdLinkavgList, evalBdLinkavgList)]
                flowCase_evalBdLinkmaxList = [x + y for x, y in zip(flowCase_evalBdLinkmaxList, evalBdLinkmaxList)]
                flowCase_evalRoutelenFlowavgList = [x + y for x, y in
                                                    zip(flowCase_evalRoutelenFlowavgList, evalRoutelenFlowavgList)]
                flowCase_evalRoutelenFlowmaxList = [x + y for x, y in
                                                    zip(flowCase_evalRoutelenFlowmaxList, evalRoutelenFlowmaxList)]
                flowCase_evalArlfLinkavgList = [x + y for x, y in
                                                zip(flowCase_evalArlfLinkavgList, evalArlfLinkavgList)]
                flowCase_evalArlfLinkmaxList = [x + y for x, y in
                                                zip(flowCase_evalArlfLinkmaxList, evalArlfLinkmaxList)]
                flowCase_evalArdfNodeavgList = [x + y for x, y in
                                                zip(flowCase_evalArdfNodeavgList, evalArdfNodeavgList)]
                flowCase_evalArdfNodemaxList = [x + y for x, y in
                                                zip(flowCase_evalArdfNodemaxList, evalArdfNodemaxList)]

                print("evalBdLinkavgList = ", evalBdLinkavgList, "\r\n",
                      "evalBdLinkmaxList = ", evalBdLinkmaxList, "\r\n",
                      "evalRoutelenFlowavgList = ", evalRoutelenFlowavgList, "\r\n",
                      "evalRoutelenFlowmaxList = ", evalRoutelenFlowmaxList, "\r\n",
                      "evalArlfLinkavgList = ", evalArlfLinkavgList, "\r\n",
                      "evalArlfLinkmaxList = ", evalArlfLinkmaxList, "\r\n",
                      "evalArdfNodeavgList = ", evalArdfNodeavgList, "\r\n",
                      "evalArdfNodemaxList = ", evalArdfNodemaxList, "\r\n",
                      )


            flowCase_evalBdLinkavgList = [x / maxTopoNum for x in flowCase_evalBdLinkavgList]
            flowCase_evalBdLinkmaxList = [x / maxTopoNum for x in flowCase_evalBdLinkmaxList]
            flowCase_evalRoutelenFlowavgList = [x / maxTopoNum for x in flowCase_evalRoutelenFlowavgList]
            flowCase_evalRoutelenFlowmaxList = [x / maxTopoNum for x in flowCase_evalRoutelenFlowmaxList]
            flowCase_evalArlfLinkavgList = [x / maxTopoNum for x in flowCase_evalArlfLinkavgList]
            flowCase_evalArlfLinkmaxList = [x / maxTopoNum for x in flowCase_evalArlfLinkmaxList]
            flowCase_evalArdfNodeavgList = [x / maxTopoNum for x in flowCase_evalArdfNodeavgList]
            flowCase_evalArdfNodemaxList = [x / maxTopoNum for x in flowCase_evalArdfNodemaxList]

            fileName = './output/routeResult'+'/routeResult' + 'swNum'+swNum.__str__() + 'esNum'+esNum.__str__() +'flowNum'+flowNum.__str__()+'.txt'
            with open(fileName, 'w') as f:
                f.write('\n'+'flowCase_evalBdLinkavgList = ')
                for item in flowCase_evalBdLinkavgList:
                    f.write(item.__str__() + ',')
                f.write('\n'+'flowCase_evalBdLinkmaxList = ')
                for item in flowCase_evalBdLinkmaxList:
                    f.write(item.__str__() + ',')
                f.write('\n'+'flowCase_evalRoutelenFlowavgList = ')
                for item in flowCase_evalRoutelenFlowavgList:
                    f.write(item.__str__() + ',')
                f.write('\n'+'flowCase_evalRoutelenFlowmaxList = ')
                for item in flowCase_evalRoutelenFlowmaxList:
                    f.write(item.__str__() + ',')
                f.write('\n'+'flowCase_evalArlfLinkavgList = ')
                for item in flowCase_evalArlfLinkavgList:
                    f.write(item.__str__() + ',')
                f.write('\n'+'flowCase_evalArlfLinkmaxList = ')
                for item in flowCase_evalArlfLinkmaxList:
                    f.write(item.__str__() + ',')
                f.write('\n'+'flowCase_evalArdfNodeavgList = ')
                for item in flowCase_evalArdfNodeavgList:
                    f.write(item.__str__() + ',')
                f.write('\n'+'flowCase_evalArdfNodemaxList = ')
                for item in flowCase_evalArdfNodemaxList:
                    f.write(item.__str__() + ',')


def actrualSchedAlgRunningTime(topoMatrix,swNum,esNum,flowObjList):
    ourHeristicAlgFlag = 1
    ourILPAlgFlag = 1
    orrAlgFlag = 1
    enhanceAlgFlag = 1
    ilpAlgFlag = 0

    #调度算法评估
    evalRuningTime = [0.0,0.0,0.0,0.0,0.0]
    networkEvalTool = network_eval_tools()
    networkOpTool = network_op_tools()
    if ourHeristicAlgFlag == 1:
        start_time = time.time()
        # x.创建调度器
        tsnStpRecurScheTool = tsnRecurSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        # tf = trafficClass(netTopo, flowObjList)
        tf = trafficClass(netTopo, networkOpTool.flowSetRoutePostHandle_bandwith(flowObjList))

        # x.进行路由
        tsnStpRecurScheTool.routeMethod(netTopo, tf)
        tf._flowObjList = networkOpTool.flowSetRoutePostHandle(tf._flowObjList)
        # x.进行调度
        tsnStpRecurScheTool.schedMethod(netTopo, tf)

        # 计算并打印执行时间
        end_time = time.time()
        execution_time = end_time - start_time
        evalRuningTime[0] = execution_time

    if ourILPAlgFlag == 1:
        start_time = time.time()
        # x.创建调度器
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, networkOpTool.flowSetRoutePostHandle_bandwith(flowObjList))
        # x.进行路由
        SchedTool = tsnMultiRouteILPSchedMethod()
        SchedTool.route(netTopo, tf)
        tf._flowObjList = networkOpTool.flowSetRoutePostHandle(tf._flowObjList)
        SchedTool.sched(netTopo, tf)
        SchedTool.solveMaxSchedable(netTopo, tf)
        # 计算并打印执行时间
        end_time = time.time()
        execution_time = end_time - start_time
        evalRuningTime[1] = execution_time

    if orrAlgFlag == 1:
        start_time = time.time()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, flowObjList)
        # x.进行路由
        SchedTool = OrrTsnSchedMethod()

        SchedTool.route(netTopo, tf)
        SchedTool.sched(netTopo, tf)
        SchedTool.solveMaxSchedable(netTopo, tf)
        # 计算并打印执行时间
        end_time = time.time()
        execution_time = end_time - start_time
        evalRuningTime[2] = execution_time

    if enhanceAlgFlag == 1:
        start_time = time.time()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, flowObjList)
        # x.进行路由
        SchedTool = enhanceSchedAndThroughputSchedMethod()

        SchedTool.route(netTopo, tf)
        SchedTool.sched(netTopo, tf)
        SchedTool.solveMaxSchedable(netTopo, tf)
        # 计算并打印执行时间
        end_time = time.time()
        execution_time = end_time - start_time
        evalRuningTime[3] = execution_time

    if ilpAlgFlag == 1:
        start_time = time.time()
        # x.创建调度器
        ilpBasedMultiFlowTool = ilpbasedMultiFlowSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, flowObjList)

        # x.进行路由
        ilpBasedMultiFlowTool.route(netTopo, tf)
        ilpBasedMultiFlowTool.sched(netTopo, tf)
        ilpBasedMultiFlowTool.solveMaxSchedable(netTopo, tf)

        # 计算并打印执行时间
        end_time = time.time()
        execution_time = end_time - start_time
        evalRuningTime[4] = execution_time


    return evalRuningTime

def schedAlgTimeCompare():
    #这个是用来对比计算时间
    # sys.setrecursionlimit(10000)


    maxTopoNum = 10
    messageLenRnge = (64,1500)
    # messagePeriod = [1000000,2000000,4000000,5000000]
    # messgaeNum = [100,200,300,400,500]

    messagePeriod = [1000000,2000000,4000000,5000000]
    messgaeNum = [50,100,150,200,250,300]

    # expTopo = {'small':[4,8],'medium':[8,16],'larger Medium':[16,32]}
    expTopo = {'medium': [8, 16], 'larger Medium': [16, 32]}
    # expTopo = {'small': [4,8]}

    #x.创建拓扑
    rG = randomGraph()

    #1.示例1生成k完全图
    swNum = 4
    esNum = 8

    for key, value in expTopo.items():
        swNum = value[0]
        esNum = value[1]
        #1.要做五次实验
        for flowNum in messgaeNum:
            flowCase_evalRuningTime = [0.0,0.0,0.0,0.0,0.0]
            for _ in range(maxTopoNum):
                print('swNum = ',swNum,',esNum = ',esNum,',flowNum = ',flowNum,',TopoNum = ',_)
                #随机邻接矩阵
                topoMatrix = rG.generate_network(esNum, swNum)
                # x.创建流量生成器
                tgTool = trafficGeneratorToolClass()
                flowObjList = tgTool.generateRandomTTRCFlows(swNum, esNum, messagePeriod,messageLenRnge, flowNum, 0)

                #debug
                # dbPrint(topoMatrix,swNum,esNum,flowObjList)
                evalRuningTime = actrualSchedAlgRunningTime(topoMatrix, swNum, esNum, flowObjList)

                flowCase_evalRuningTime = [x + y for x, y in zip(flowCase_evalRuningTime, evalRuningTime)]

            flowCase_evalRuningTime = [x / maxTopoNum for x in flowCase_evalRuningTime]
            print("flowCase_evalRuningTime = ", flowCase_evalRuningTime, "\r\n")


            fileName = './output/timeResult'+'/timeResult' + 'swNum'+swNum.__str__() + 'esNum'+esNum.__str__() +'flowNum'+flowNum.__str__()+'.txt'
            with open(fileName, 'w') as f:
                f.write('\n'+'flowCase_evalRuningTime = ')
                for item in flowCase_evalRuningTime:
                    f.write(item.__str__() + ',')

            if flowCase_evalRuningTime[1] > 540 and \
                 flowCase_evalRuningTime[2] > 540 and\
                 flowCase_evalRuningTime[3] > 540:
                break

def actrualSchedAlgSchedableA(topoMatrix,swNum,esNum,flowObjList):

    # 2.1
    # 对比our启发式、
    # OurILP、
    # ORR、
    # EnhancingSchedulability
    # 以及ilpbasedMultiFlowSchedMethod五个算法，这里由于都应用了
    # ILP的思想，导致求解速度满，所以只求解30/60/90/120/150几种情况


    ourHeristicAlgFlag = 1
    ourILPAlgFlag = 1
    orrAlgFlag = 1
    enhanceAlgFlag = 1
    ilpAlgFlag = 0


    #调度算法评估
    networkEvalTool = network_eval_tools()
    networkOpTool = network_op_tools()
    dbgTool = debugToolClass()
    evalSchedable = [0.0,0.0,0.0,0.0,0.0]
    evalMinGap = [0.0, 0.0, 0.0, 0.0, 0.0]
    if ourHeristicAlgFlag == 1:
        # x.创建调度器
        tsnStpRecurScheTool = tsnRecurSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        # tf = trafficClass(netTopo, flowObjList)
        tf = trafficClass(netTopo, networkOpTool.flowSetRoutePostHandle_bandwith(flowObjList))

        # x.进行路由
        tsnStpRecurScheTool.routeMethod(netTopo, tf)
        tf._flowObjList = networkOpTool.flowSetRoutePostHandle(tf._flowObjList)
        # x.进行调度
        tsnStpRecurScheTool.schedMethod(netTopo, tf)
        # dbgTool.printTrafficClass(tf)
        # dbgTool.printFlowObjQbv(tf)
        schedableRatio = networkEvalTool.evalSchedulableRatio(tf)
        evalSchedable[0] = schedableRatio
        evalMinGap[0] = 0.0

    if ourILPAlgFlag == 1:
        # x.创建调度器
        flowNum = len(flowObjList)
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, networkOpTool.flowSetRoutePostHandle_bandwith(flowObjList))
        # x.进行路由
        SchedTool = tsnMultiRouteILPSchedMethod()
        SchedTool.route(netTopo, tf)
        tf._flowObjList = networkOpTool.flowSetRoutePostHandle(tf._flowObjList)
        # print('nwpspAlg networkEvalTool.evalRouteAbleRatio(tf) = ', networkEvalTool.evalRouteAbleRatio(tf))
        SchedTool.sched(netTopo, tf)
        result,gap = SchedTool.solveMaxSchedable(netTopo, tf)
        evalSchedable[1] = result/flowNum * 100
        evalMinGap[1] = gap * 100

    if orrAlgFlag == 1:
        flowNum = len(flowObjList)
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, flowObjList)
        # x.进行路由
        SchedTool = OrrTsnSchedMethod()

        SchedTool.route(netTopo, tf)
        SchedTool.sched(netTopo, tf)
        result,gap = SchedTool.solveMaxSchedable(netTopo, tf)
        evalSchedable[2] = result/flowNum*100
        evalMinGap[2] = gap * 100
    if enhanceAlgFlag == 1:
        flowNum = len(flowObjList)
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        tf = trafficClass(netTopo, flowObjList)
        # x.进行路由
        SchedTool = enhanceSchedAndThroughputSchedMethod()

        SchedTool.route(netTopo, tf)
        SchedTool.sched(netTopo, tf)
        result,gap = SchedTool.solveMaxSchedable(netTopo, tf)
        evalSchedable[3] = result/flowNum*100
        evalMinGap[3] = gap * 100

    if ilpAlgFlag == 1:
        flowNum = len(flowObjList)
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        flowObjIncreaseList = flowObjList
        tf = trafficClass(netTopo, flowObjIncreaseList)
        # x.进行路由
        SchedTool = ilpbasedMultiFlowSchedMethod()
        SchedTool.route(netTopo, tf)
        SchedTool.sched(netTopo, tf)
        result,gap = SchedTool.solveMaxSchedable(netTopo, tf)
        if result == -1:result = 0
        evalSchedable[4] = result/flowNum * 100
        evalMinGap[4] = gap * 100


    return evalSchedable,evalMinGap



def schedAlgScheableCompareA():
    # 这个是用来对比可调度性的
    sys.setrecursionlimit(1000000)

    maxTopoNum = 10
    messageLenRnge = (500, 1500)
    messagePeriod = [100000, 200000, 400000, 500000]
    messgaeNum = [50,100,150,200,250,300]

    # messagePeriod = [100000]
    # messgaeNum = [500]
    # messgaeNum = [200]

    expTopo = {'small':[4,8],'medium':[8,16],'larger Medium':[16,32]}
    # expTopo = { 'medium': [8, 16], 'larger Medium': [16, 32]}
    # expTopo = {'small': [16, 32]}

    # x.创建拓扑
    rG = randomGraph()

    # 1.示例1生成k完全图
    swNum = 4
    esNum = 8
    sbx = []
    for key, value in expTopo.items():
        swNum = value[0]
        esNum = value[1]
        # 1.要做五次实验
        for flowNum in messgaeNum:
            flowCase_evalSchedable = [0.0, 0.0, 0.0, 0.0, 0.0]
            flowCase_evalMinGap = [0.0, 0.0, 0.0, 0.0, 0.0]
            for _ in range(maxTopoNum):
                print('swNum = ', swNum, ',esNum = ', esNum, ',flowNum = ', flowNum, ',TopoNum = ', _)
                # 随机邻接矩阵
                topoMatrix = rG.generate_network(esNum, swNum)
                # x.创建流量生成器
                tgTool = trafficGeneratorToolClass()
                flowObjList = tgTool.generateRandomTTRCFlows(swNum, esNum, messagePeriod, messageLenRnge, flowNum,
                                                             0)

                # debug
                # dbPrint(topoMatrix,swNum,esNum,flowObjList)
                evalSchedable,evalMinGap = actrualSchedAlgSchedableA(topoMatrix, swNum, esNum, flowObjList)

                flowCase_evalSchedable = [x + y for x, y in zip(flowCase_evalSchedable, evalSchedable)]
                flowCase_evalMinGap = [x + y for x, y in zip(flowCase_evalMinGap, evalMinGap)]

            flowCase_evalSchedable = [x / maxTopoNum for x in flowCase_evalSchedable]
            flowCase_evalMinGap = [x / maxTopoNum for x in flowCase_evalMinGap]

            print("flowCase_evalSchedable = ", flowCase_evalSchedable, "\r\n")
            print("flowCase_evalMinGap = ", flowCase_evalMinGap, "\r\n")

            fileName = './output/schedableRatioResult' + '/AschedableRatioResult' + 'swNum' + swNum.__str__() + 'esNum' + esNum.__str__() + 'flowNum' + flowNum.__str__() + '.txt'
            with open(fileName, 'w') as f:
                f.write('\n' + 'flowCase_evalSchedable = ')
                for item in flowCase_evalSchedable:
                    f.write(item.__str__() + ',')

                f.write('\n' + 'flowCase_evalMinGap = ')
                for item in flowCase_evalMinGap:
                    f.write(item.__str__() + ',')

            if flowCase_evalSchedable[0] > flowCase_evalSchedable[1] and \
                 flowCase_evalSchedable[0] > flowCase_evalSchedable[2] and\
                 flowCase_evalSchedable[0] > flowCase_evalSchedable[3]:
                break




def actrualSchedAlgSchedableB(topoMatrix,swNum,esNum,flowObjList):

    # 2.2
    # our启发式、Our启发式+预处理、Our启发式+后处理、our启发式+不做任何处理


    ourAlgFlag = 1
    ourPrehandleAlgFlag = 1
    ourPosthandleAlgFlag = 1
    ourNonehandleAlgFlag = 1


    #调度算法评估
    networkEvalTool = network_eval_tools()
    networkOpTool = network_op_tools()
    dbgTool = debugToolClass()
    evalSchedable = [0.0,0.0,0.0,0.0]
    if ourAlgFlag == 1:
        # x.创建调度器
        tsnStpRecurScheTool = tsnRecurSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        # tf = trafficClass(netTopo, flowObjList)
        tf = trafficClass(netTopo, networkOpTool.flowSetRoutePostHandle_bandwith(flowObjList))

        # x.进行路由
        tsnStpRecurScheTool.routeMethod(netTopo, tf)
        tf._flowObjList = networkOpTool.flowSetRoutePostHandle(tf._flowObjList)
        # x.进行调度
        tsnStpRecurScheTool.schedMethod(netTopo, tf)
        # dbgTool.printTrafficClass(tf)
        # dbgTool.printFlowObjQbv(tf)
        schedableRatio = networkEvalTool.evalSchedulableRatio(tf)
        evalSchedable[0] = schedableRatio

    if ourPrehandleAlgFlag == 1:
        # x.创建调度器
        tsnStpRecurScheTool = tsnRecurSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        # tf = trafficClass(netTopo, flowObjList)
        tf = trafficClass(netTopo, networkOpTool.flowSetRoutePostHandle_bandwith(flowObjList))

        # x.进行路由
        tsnStpRecurScheTool.routeMethod(netTopo, tf)
        # x.进行调度
        tsnStpRecurScheTool.schedMethod(netTopo, tf)
        # dbgTool.printTrafficClass(tf)
        # dbgTool.printFlowObjQbv(tf)
        schedableRatio = networkEvalTool.evalSchedulableRatio(tf)
        evalSchedable[1] = schedableRatio

    if ourPosthandleAlgFlag == 1:
        # x.创建调度器
        tsnStpRecurScheTool = tsnRecurSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        # tf = trafficClass(netTopo, flowObjList)
        tf = trafficClass(netTopo, flowObjList)

        # x.进行路由
        tsnStpRecurScheTool.routeMethod(netTopo, tf)
        tf._flowObjList = networkOpTool.flowSetRoutePostHandle(tf._flowObjList)
        # x.进行调度
        tsnStpRecurScheTool.schedMethod(netTopo, tf)
        # dbgTool.printTrafficClass(tf)
        # dbgTool.printFlowObjQbv(tf)
        schedableRatio = networkEvalTool.evalSchedulableRatio(tf)
        evalSchedable[2] = schedableRatio
    if ourNonehandleAlgFlag == 1:
        # x.创建调度器
        tsnStpRecurScheTool = tsnRecurSchedMethod()
        # x.生成netTopoClass
        netTopo = netTopoClass(topoMatrix, swNum, esNum)
        # x.分析流量
        # tf = trafficClass(netTopo, flowObjList)
        tf = trafficClass(netTopo, flowObjList)

        # x.进行路由
        tsnStpRecurScheTool.routeMethod(netTopo, tf)
        # x.进行调度
        tsnStpRecurScheTool.schedMethod(netTopo, tf)
        # dbgTool.printTrafficClass(tf)
        # dbgTool.printFlowObjQbv(tf)
        schedableRatio = networkEvalTool.evalSchedulableRatio(tf)
        evalSchedable[3] = schedableRatio


    return evalSchedable



def schedAlgScheableCompareB():
    # 这个是用来对比可调度性的
    sys.setrecursionlimit(1000000)

    maxTopoNum = 20
    messageLenRnge = (64, 1500)
    messagePeriod = [100000, 200000, 400000, 500000]
    messgaeNum = [50,100,150,200,250,300]

    # messagePeriod = [100000]
    # messgaeNum = [500]
    # messgaeNum = [200]

    expTopo = {'small':[4,8],'medium':[8,16],'larger Medium':[16,32]}
    # expTopo = {'small': [4, 8]}

    # x.创建拓扑
    rG = randomGraph()

    # 1.示例1生成k完全图
    swNum = 4
    esNum = 8
    sbx = []
    for key, value in expTopo.items():
        swNum = value[0]
        esNum = value[1]
        # 1.要做五次实验
        for flowNum in messgaeNum:
            flowCase_evalSchedable = [0.0, 0.0, 0.0, 0.0]
            for _ in range(maxTopoNum):
                # 随机邻接矩阵
                topoMatrix = rG.generate_network(esNum, swNum)
                # x.创建流量生成器
                tgTool = trafficGeneratorToolClass()
                flowObjList = tgTool.generateRandomTTRCFlows(swNum, esNum, messagePeriod, messageLenRnge, flowNum,
                                                             0)

                # debug
                # dbPrint(topoMatrix,swNum,esNum,flowObjList)
                evalSchedable = actrualSchedAlgSchedableB(topoMatrix, swNum, esNum, flowObjList)

                flowCase_evalSchedable = [x + y for x, y in zip(flowCase_evalSchedable, evalSchedable)]

            flowCase_evalSchedable = [x / maxTopoNum for x in flowCase_evalSchedable]

            print("flowCase_evalSchedable = ", flowCase_evalSchedable, "\r\n")

            fileName = './output/schedableRatioResult' + '/BschedableRatioResult' + 'swNum' + swNum.__str__() + 'esNum' + esNum.__str__() + 'flowNum' + flowNum.__str__() + '.txt'
            with open(fileName, 'w') as f:
                f.write('\n' + 'flowCase_evalSchedable = ')
                for item in flowCase_evalSchedable:
                    f.write(item.__str__() + ',')

def set_process_affinity(n_cores):
    p = psutil.Process()  # 当前进程
    p.cpu_affinity(list(range(n_cores)))  # 设置进程 CPU 亲和性




if __name__ == '__main__':
    print('ssss')
    # 限制当前进程只能使用前两个核心
    set_process_affinity(6)
    #1.路由对比
    # routeAlgCompare()

    #1.1路由成功率对比
    # routeAbleAlgCompare()

    #2.运行时间对比
    # schedAlgTimeCompare()

    #3.可调度性对比,但是这里的可调度性，指的是我们在流量数量少的情况下的可调度性

    # schedAlgScheableCompareB()
    schedAlgScheableCompareA()


