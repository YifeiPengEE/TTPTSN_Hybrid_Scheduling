from head import *
import head


class netTopoClass:
    # 类描述：net_topo为拓扑操作的基础类，该类主要完成由邻接矩阵到节点、链路等列表的转化；
    # 类版本：v0.3；
    # 当前版本说明：
    #     ①当前版支持终端系统多端口；
    #     ②当前版本输入为二维0-1邻接矩阵；
    #     ③要求输入的邻接矩阵，必须前SW_num行为交换机，后ES_num行为端系统；

    def __init__(self,adjMtrix,SW_num,ES_num):
        print('我是netTopoClass的构造函数')
        self._swNum = SW_num
        self._esNum = ES_num
        self._nodeNum = SW_num + ES_num
        self._nodeSet = []  # 节点列表
        self._swSet = []  # 交换机列表
        self._esSet = []  # 终端列表
        self._linkSet = []  # 双向链路列表，表示双向链路对，每一对的link_id互为相反数
        self._directAdjMatrix = []
        self._adjMatrix = []
        self._RCadjMatrix = []

        self._adjMatrix = copy.deepcopy(adjMtrix)

        #x.定义私有变量
        self._routeVarX = []


        #1.创建设备
        for i in range(len(self._adjMatrix)):
            if i < SW_num:
                self.initAddNode(head.NodeType.Switch)
            elif i >= SW_num:
                self.initAddNode(head.NodeType.EndStation)
            else:
                continue
        #2.初始化节点类的link集合与变量集合
        # for i in range(SW_num+ES_num):
        #     for j in range(SW_num + ES_num):
        #         self._nodeSet[i]._ingressLink.append([])
        #         self._nodeSet[i]._egressLink.append([])
        # for i in range(SW_num+ES_num):
        #     for j in range(SW_num + ES_num):
        #         self._nodeSet[i]._exgressVari.append([])
        #         self._nodeSet[i]._ingressVari.append([])
        #3.根据邻接矩阵创link对象，并将link对象插入
        i = 0
        for item in self._adjMatrix:
            j = 0
            for node_id in item:
                # 添加链路
                if node_id == 1:
                    link = linkClass(self._linkSet.__len__()
                                              ,self._nodeSet[i]
                                              ,self._nodeSet[j]
                                              )
                    self._linkSet.append(link)
                    self._directAdjMatrix[i][j] = link
                    self._nodeSet[i]._egressLink.append(link)
                    self._nodeSet[j]._ingressLink.append(link)
                    self._nodeSet[i]._link.append(link)
                j = j + 1
            i = i + 1

    #-------------------------------------------------
    #函数名称：initAddNode
    #输入参数：nodeType节点类型
    #输出参数：无
    #函数描述：用于创建并初始化节点对象
    #-------------------------------------------------
    def initAddNode(self, nodeType):
        """
        添加节点
        :param node_type: 节点类型
        :return:
        """
        if nodeType == head.NodeType.EndStation:
            node = nodeClass(self._esSet.__len__(), nodeType,self._nodeSet.__len__())
            self._esSet.append(node)
        elif nodeType == head.NodeType.Switch:
            node = nodeClass(self._swSet.__len__(), nodeType, self._nodeSet.__len__())
            self._swSet.append(node)
        else:
            return None
        self._nodeSet.append(node)
        self._directAdjMatrix.append([None] * self._nodeSet.__len__())
        for row in self._directAdjMatrix:    # 维护每行长度相等
            row.extend([None] * (self._nodeSet.__len__() - row.__len__()))
        return node

