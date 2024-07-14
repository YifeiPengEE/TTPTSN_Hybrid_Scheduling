from head import *
import head
import copy


class trafficClass:
    # 类说明：该类对flowObjList进行解析，用于感知所有流的共同特性，比如超周期，数量等等

    # netTopo网络拓扑临界矩阵
    # flowObjList：流对象列表
    # ttFlowPercentage:TT流占总带宽的百分比
    # rcFlowPercentage:RC流占总带宽的百分比
    # reSchedFlag：重调度模式
    # _flowObjList:存放所有流
    # _TTflowObjList:存放RC流
    # _RCflowObjList:存放RC流
    # 如果需要解析其他变量，再进行添加
    def __init__(self, netTopo, flowObjList, ttFlowPercentage=0.4, rcFlowPercentage=0.4, reSchedFlag=False):
        self._netTopo = netTopo
        self._flowObjList = copy.deepcopy(flowObjList)
        self._TTflowObjList = []
        self._RCflowObjList = []
        for flow in self._flowObjList:
            if flow._flowType == 'TT':
                self._TTflowObjList.append(flow)
            elif flow._flowType == 'RC':
                self._RCflowObjList.append(flow)

        self._flowNum = len(self._flowObjList)
        self._assignedTrafficNum = 0
        self._assignFlowNum = 0
        self._periodSet = []
        self._ttFlowPercentage = ttFlowPercentage
        self._rcFlowPercentage = rcFlowPercentage
        # 0.将self._flowObjList与self._netTopo绑定
        for flow in self._flowObjList:
            # print('flow._srcNodeId = ',flow._srcNodeId)
            # print('flow._dstNodeId = ', flow._dstNodeId)
            flow._srcNode = self._netTopo._esSet[flow._srcNodeId]
            flow._dstNode = self._netTopo._esSet[flow._dstNodeId]

        # 1.求解flowObjList的超周期
        # 周期的单位为纳秒
        for flow in self._flowObjList:
            for ele in self._periodSet:
                if ele == flow._period:
                    break
            self._periodSet.append(flow._period)

        lcm = self._periodSet[0]
        s_gcd = self._periodSet[0]
        for period in self._periodSet[1:]:
            lcm = int(lcm * period / gcd(lcm, period))
            s_gcd = gcd(s_gcd, period)
        self._hyperPeriod = lcm
        self._gcd = s_gcd

        # 2.初始化每条链路的空闲窗口
        if reSchedFlag == False:
            for link in self._netTopo._linkSet:
                link._idleWindowList.append([0.0, self._hyperPeriod])

        # 3.计算一个超周期的总bit数
        self._totalBit = 0
        for flow in self._flowObjList:
            intNum = int(self._hyperPeriod / flow._period)
            self._totalBit += flow._frameSize * 8 * intNum

        # 定义一些私有变量
        # 网关会用到的私有变量
        self._netGateFlowIdList = []  # 该集合中放置网关流id
        self._vFlowSet = []  # 该字典存放虚拟节点集合
        self._vNodeSlot = {}  # 字典中存放的是{'vNode1':[maxBytes,[startPit,endPit]],'vNode2':[maxDur,[startPit,endPit]],...}
        # 重调度的时候会使用的变量
        self._flowObjListOri = copy.deepcopy(flowObjList)  # 用于备份传入的flowObjList，重调度的时候会用到

    def assigned_traffic_num_statistic(self, flowObjList):
        _assignedTrafficNum = 0
        for item in flowObjList:
            if item._isAssigned == head.AssignStatus.Assigned:
                _assignedTrafficNum += 1

        return _assignedTrafficNum

    def assignedRouteNumStatistic(self, flowObjList):
        _assignedTrafficNum = 0
        for item in flowObjList:
            if item._isRouted == head.AssignStatus.Assigned:
                _assignedTrafficNum += 1

        return _assignedTrafficNum

    # 按周期排序：trafficClass._flowObjList = sorted(trafficClass._flowObjList, key=lambda x: x._period)
    # 按flowId排序：trafficClass._flowObjList = sorted(trafficClass._flowId, key=lambda x: x._period)
    # 说明，在计算tsn->TTP延时的时候，为了结果更具有一般性，应该让结果按照flowId排序
    def ttpVflowHandler(self):
        self._flowObjList = sorted(self._flowObjList, key=lambda x: x._period)
        cnt = -1
        lastPeriod = 0
        insCnt = 0
        vflowSet = []

        maxByte = 0
        for flow in self._flowObjList:
            vflowIdSet = []
            if lastPeriod == flow._period:
                insNum = int(flow._period / self._gcd)
                if insCnt < insNum:
                    if maxByte < flow._frameSize:
                        maxByte = flow._frameSize
                    vflowSet[cnt]._frameSize = maxByte
                    insCnt = insCnt + 1
                    self._vFlowSet[cnt].append(flow._flowId+1)

                elif insCnt == insNum:
                    cnt = cnt + 1
                    insCnt = 1
                    lastPeriod = flow._period
                    maxByte = flow._frameSize
                    vflowSet.append(
                        flowClass(cnt, 0, flow._srcNode, flow._dstNode, flow._srcNode._nodeId, flow._dstNode._nodeId, 0, self._gcd,
                                  self._gcd, 0, maxByte, 1))
                    vflowIdSet.append(flow._flowId+1)
                    self._vFlowSet.append(vflowIdSet)
            else:
                insCnt = 1
                cnt = cnt + 1
                lastPeriod = flow._period
                maxByte = flow._frameSize
                vflowSet.append(
                    flowClass(cnt, 0, flow._srcNode, flow._dstNode, flow._srcNode._nodeId, flow._dstNode._nodeId, 0, self._gcd, self._gcd, 0,
                              maxByte, 1))

                vflowIdSet.append(flow._flowId+1)
                self._vFlowSet.append(vflowIdSet)

        print('self._vFlowSet = ',self._vFlowSet)
        #更新
        self._flowObjList = vflowSet
        self._TTflowObjList = vflowSet
        self._hyperPeriod = self._gcd
        self._flowNum = len(self._flowObjList)
