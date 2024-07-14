from head import *
import head
# 流的数据结构和方法
class flowClass:

    def __init__(self, flowId, subflowId ,srcNode, dstNode,srcNodeId,dstNodeId, priority,
                 period, deadline, jitter, frameSize, redundancy,flowType = 'TT'):
        #下面子流ID是为了解决冗余或者组播的问题，冗余流或者组播流的flowId是一样的，但是其副本的subflowId不同；
        self._flowId = flowId
        self._subflowId = subflowId
        self._srcNode = srcNode
        self._dstNode = dstNode
        self._srcNodeId = srcNodeId
        self._dstNodeId = dstNodeId
        self._priority = priority
        self._period = period
        self._jitter = jitter
        self._deadline = deadline
        self._frameSize = frameSize
        self._flowDur = self._frameSize * head.TSN_CLK
        self._flowBandwith = self._frameSize/self._period * 1000 #Mbps
        self._redundancy = redundancy
        self._isRouted = head.AssignStatus.Unassigned
        self._isAssigned = head.AssignStatus.Unassigned
        self._assignPath = []
        self._assignQbv = []
        self._assignQbvDetail = []
        self._startOffset = -1.0
        self._flowType = flowType

        self._rcDelay = 0.0

        #用于时隙化的规划
        self._holeIndexList = []
        #用于线性规划/整数线性规划的变量
        self._FlowValidLpVars = []
        self._RouteLpVars = []
        self._RouteOrderLpVars = {}
        self._SchedLpVars = []



