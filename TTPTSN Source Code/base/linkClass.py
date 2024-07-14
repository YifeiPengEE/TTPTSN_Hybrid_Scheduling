from head import *
import head


# 单向链路的数据结构和方法
class linkClass:

    def __init__(self, linkId,srcNode,dstNode):
    #当前假设链路是单向的，是一条由源节点指向目的节点的有向线
    #链路的基本属性
        self._linkId = linkId #链路ID
        self._srcNodeDevId = srcNode._deviceId
        self._dstNodeDevId = dstNode._deviceId
        self._srcNode = srcNode #用于描述链路的源节点
        self._dstNode = dstNode
        self._linkName = self._srcNode._nodeName+'_'+self._dstNode._nodeName
        self._linkDelay = head.DEFAULT_LINK_DELAY
        self._linkRate = head.DEFAULT_LINK_MAX_BANDWIDTH
        self.cost = 1.0
    #链路的动态属性
        self._occupyBw = 0 #目前链路上的带宽
        self._occupyFlowCnt = 0 #目前链路上的流数量
        self._flowSet = [] #目前链路上的流的集合
        self._RCFlowSet = []  # 目前链路上的流的集合
        self._idleWindowList = [] #用于指示哪些空隙空闲
        self._occupyWindowList = []  # 用于指示哪些空隙已经被占用

        self._qavIdleSlopeList = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0] #存放的每个优先级对应的idleslope,-1代表不使用

        #用于分析RC业务延时
        self._alpha = []
        self._beta = []
        self._queueDelay = -1
        # 用于线性规划/整数线性规划的变量
        self._RouteLpVars = {}
        self._RouteOrderLpVars = {}
        self._SchedLpVars = {}



    def setRCFlowSet(self):
        if self._RCFlowSet == []:
            for flow in self._flowSet:
                if flow._flowType == 'RC':
                    self._RCFlowSet.append(flow)

    #-------------------------------------------------
    #函数名称：addFlowObjToLink
    #输入参数：flowObj流对象
    #输出参数：无
    #函数描述：将流加入当前链路的集合中
    #-------------------------------------------------
    def addFlowObjToLink(self,flowObj):
        # print('add flow '+ int(flow_id).__str__())
        self._flowSet.append(flowObj)
    # def addFlowToLink(self,flowId,flowSubId,flowStartPit,flowEndPit,flowObj,qbvWin):
    #     # print('add flow '+ int(flow_id).__str__())
    #     self._flowSet.append([flowId,flowSubId,flowStartPit,flowEndPit,flowObj,qbvWin])

