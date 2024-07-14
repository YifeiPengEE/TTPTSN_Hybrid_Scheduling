from head import *
import head
# 节点的数据结构和方法
class nodeClass:

    def __init__(self, nodeId, nodeType, deviceId):
        # 节点的基本属性
        self._nodeId = nodeId #节点ID
        self._nodeType = nodeType #节点类型，可以是TSN交换机，可以是TSN节点等等
        self._deviceId = deviceId #设备ID，一个网络中存在很多设备，这些设备可以是节点、可以是交换机等等，但是设备的ID号应该是全局唯一的
        self._egressLink = [] #存放节点链路集合
        self._ingressLink = []#存放节点链路集合
        self._link = []#存放节点链路集合
        self._flowCnt = 0
        if self._nodeType == head.NodeType.EndStation:
            self._maxPorts = head.DEFAULT_ES_MAX_PORTS
            self._remainPorts = head.DEFAULT_ES_MAX_PORTS
            self._nodeName = 'TSNNode' + str(self._nodeId)
        elif self._nodeType == head.NodeType.Switch:
            self._maxPorts = head.DEFAULT_SW_MAX_PORTS
            self._remainPorts = head.DEFAULT_SW_MAX_PORTS
            self._forwardDelay = head.DEFAULT_SW_FORWARD_DELAY
            self._nodeName = 'TSNSW' + str(self._nodeId)


