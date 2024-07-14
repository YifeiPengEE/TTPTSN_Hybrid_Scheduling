from head import *
import random
class trafficGeneratorToolClass:
    # 类描述：该类实现自动生成测试用例；
    # 类版本：v0.3；
    # 当前版本说明：
    #     ①当前版本只能生成流量；
    #     ②当前版本输入为net_topo类，[周期范围]，[帧长度]，[DDL范围],冗余级别
    # ex:
    #     [周期范围] = [2ms,4ms,8ms]:实际从这三种周期中任意选择；
    #     [帧长度] = [min_size , max_size];长度从这个范围内任意选择整数；
    #     [DDL范围] = [a,b,c]:实际从这三种DDL中任意选择；
    #     [Jitter范围] = [a,b,c]:实际从这三种Jitter中任意选择；
    #     [priority范围] = [0，1，2，3，4，5，6，7]:实际从集合任意选择；并且7为最高优先级
    #     并且如果冗余度不为1的话，会使用subflow_id参数


    def __init__(self):
        print('trafficGeneratorToolClass 构造函数')

    #-------------------------------------------------
    #函数名称：generateDetermTTRCFlows
    #输入参数：交换机数量，端系统数量，周期列表，产生的流数量
    #输出参数：生成流列表
    #函数描述：用于产生随机源->目的，随机长度的流量的TT帧和RC帧
    #-------------------------------------------------
    def generateDtermTTRCFlows(self):
        flowList = []
        flowId = 0
        flowList = self.determGenerateRandomFlows(None,0,1, [1000000], 1,_priorityList=[5],_lenRange=(500,500),_flowStartId = flowId,_flowType = 'RC')
        flowId = flowId + 1
        flowList = flowList + self.determGenerateRandomFlows(None,0,1,  [2000000], 1,_priorityList=[5],_lenRange=(1000,1000),_flowStartId = flowId,_flowType = 'RC')
        flowId = flowId + 1
        flowList = flowList + self.determGenerateRandomFlows(None,1,2,  [1000000], 1,_priorityList=[5],_lenRange=(1000,1000),_flowStartId = flowId,_flowType = 'RC')
        flowId = flowId + 1
        flowList = flowList + self.determGenerateRandomFlows(None,2,3,  [2000000], 1,_priorityList=[5],_lenRange=(1000,1000),_flowStartId = flowId,_flowType = 'RC')
        flowId = flowId + 1
        flowList = flowList + self.determGenerateRandomFlows(None,3,4,  [1000000], 1,_priorityList=[5],_lenRange=(1000,1000),_flowStartId = flowId,_flowType = 'RC')
        flowId = flowId + 1
        flowList = flowList + self.determGenerateRandomFlows(None,4,5,  [1000000], 1,_priorityList=[5],_lenRange=(1000,1000),_flowStartId = flowId,_flowType = 'RC')
        flowId = flowId + 1
        flowList = flowList + self.determGenerateRandomFlows(None,5,6,  [1000000], 1,_priorityList=[5],_lenRange=(1000,1000),_flowStartId = flowId,_flowType = 'RC')
        flowId = flowId + 1
        flowList = flowList + self.determGenerateRandomFlows(None,6,7,  [1000000], 1,_priorityList=[5],_lenRange=(1000,1000),_flowStartId = flowId,_flowType = 'RC')
        flowId = flowId + 1
        flowList = flowList + self.determGenerateRandomFlows(None,7,1,  [1000000], 1,_priorityList=[5],_lenRange=(1000,1000),_flowStartId = flowId,_flowType = 'RC')

        #flowId = flowId + flowList.__len__()
        return flowList
    #-------------------------------------------------
    #函数名称：generateDetemTTRCFlows
    #输入参数：交换机数量，端系统数量，周期列表，产生的流数量
    #输出参数：生成流列表
    #函数描述：用于产生随机源->目的，随机长度的流量的TT帧和RC帧
    #-------------------------------------------------
    def generateRandomTTRCFlows(self,sw_num, es_num, period_list,lenRange=(72, 1542), TTFlowNum = 0,RCFlowNum = 0):
        flowList = []
        flowId = 0
        flowList = self.generateRandomFlows(0,sw_num, es_num, period_list, TTFlowNum,_lenRange=lenRange,_flowStartId = flowId,_flowType = 'TT')
        flowId = flowId + flowList.__len__()
        flowList = flowList + self.generateRandomFlows(0, sw_num, es_num, period_list, RCFlowNum,_priorityList=[5],_lenRange=lenRange, _flowStartId=flowId,
                                            _flowType='RC')

        # flowId = flowId + flowList.__len__()
        # flowList = flowList + self.generateRandomFlows(0, sw_num, es_num, period_list, RCFlowNum,_priorityList=[4],_lenRange=lenRange, _flowStartId=flowId,
        #                                     _flowType='RC')
        return flowList
    #-------------------------------------------------
    #函数名称：generateRandomFlows
    #输入参数：交换机数量，端系统数量，周期列表，产生的流数量
    #输出参数：生成流列表
    #函数描述：用于产生随机源->目的，随机长度的流量
    #-------------------------------------------------
    def generateRandomFlows(self,netTopo,sw_num, es_num, period_list, flow_num,_priorityList=[7],_lenRange=(72, 1542),_flowStartId = 0,_flowType = 'TT'):
        flow_list = []
        flow_id = _flowStartId

        for p in range(0, flow_num):
            src = random.randint(sw_num, sw_num + es_num - 1)
            dst = random.randint(sw_num, sw_num + es_num - 1)
            # src = sw_num
            # dst = sw_num + es_num - 1
            while src == dst:
                dst = random.randint(sw_num, sw_num + es_num - 1)

            # src_node = netTopo._esSet[src - sw_num]
            # des_node = netTopo._esSet[dst - sw_num]
            srcNodeId = src - sw_num
            desNodeId = dst - sw_num

            period = random.sample(period_list,1)[0]
            priority = random.choice(_priorityList)
            # print(period)
            flow_list.append(
                # flowClass(flow_id, 0, src_node, des_node, 0, period, period, 0, , 1))
                # flowClass(flow_id, 0, None, None,0,1, priority, period, period, 0, random.randint(_lenRange[0], _lenRange[1]), 1,flowType = _flowType))
                flowClass(flow_id, 0, None, None,srcNodeId,desNodeId, priority, period, period, 0, random.randint(_lenRange[0], _lenRange[1]), 1,flowType = _flowType))
                # flowClass(flow_id, 0, None, None, srcNodeId, desNodeId, priority, period, period, 0, 1000,
                #           1, flowType=_flowType))
            flow_id += 1
        return flow_list
    #-------------------------------------------------
    #函数名称：determGenerateRandomFlows
    #输入参数：
    #输出参数：生成流列表
    #函数描述：生成源和目的确定的流量
    #-------------------------------------------------
    def determGenerateRandomFlows(self,netTopo,src_id,des_id, period_list, flow_num,_priorityList=[7],_lenRange=(20, 20),_flowStartId = 0,_flowType = 'TT'):
        #该函数生成特定源和目的的流
        flow_list = []
        flow_id = _flowStartId
        for p in range(0, flow_num):
            # src_node = netTopo._esSet[src_id]
            # des_node = netTopo._esSet[des_id]
            srcNodeId = src_id
            dstNodeId = des_id
            period = random.sample(period_list,1)[0]
            priority = random.sample(_priorityList,1)[0]
            flow_list.append(
                flowClass(flow_id, 0, None, None,srcNodeId,dstNodeId, priority, period, period, 0, random.randint(_lenRange[0], _lenRange[1]), 1,flowType = _flowType))
            flow_id += 1

        return flow_list
    #-------------------------------------------------
    #函数名称：determGenerateRandomFlows
    #输入参数：
    #输出参数：生成流列表
    #函数描述：生成源和目的确定的流量<一种基于联合规划的CAN-TSN网关实时性分析方法_王莎.pdf>
    #-------------------------------------------------
    def genCanMessage(self,src_id,des_id):
        #该函数生成特定源和目的的流
        flow_list = []

        BpUs = 0.0625  # 即，每个us发送0.0625个字节，在512Kbps的速率下得到
        flow_list.append(flowClass(0, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 230 * BpUs, 1))
        flow_list.append(flowClass(1, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(2, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 250 * BpUs, 1))
        flow_list.append(flowClass(3, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 170 * BpUs, 1))
        flow_list.append(flowClass(4, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 250 * BpUs, 1))
        flow_list.append(flowClass(11, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(12, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(15, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(16, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 250 * BpUs, 1))
        flow_list.append(flowClass(22, 0, None, None, src_id, des_id, 0, 10000000, 10000000, 0, 270 * BpUs, 1))

        flow_list.append(flowClass(6, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(7, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(8, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(9, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 250 * BpUs, 1))
        flow_list.append(flowClass(17, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(18, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(19, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(20, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 170 * BpUs, 1))
        flow_list.append(flowClass(23, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 170 * BpUs, 1))
        flow_list.append(flowClass(24, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(25, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(26, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(28, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(29, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(30, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))

        flow_list.append(flowClass(10, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(14, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(21, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(27, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(31, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))

        flow_list.append(flowClass(5, 0, None, None, src_id, des_id, 0, 25000000, 25000000, 0, 190 * BpUs, 1))
        flow_list.append(flowClass(13, 0, None, None, src_id, des_id, 0, 200000000, 200000000, 0, 270 * BpUs, 1))


        #32~64
        flow_list.append(flowClass(32, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(33, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 230 * BpUs, 1))
        flow_list.append(flowClass(34, 0, None, None, src_id, des_id, 0, 200000000, 200000000, 0, 190 * BpUs, 1))
        flow_list.append(flowClass(35, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))
        # flow_list.append(flowClass(36, 0, None, None, src_id, des_id, 0, 12000000, 12000000, 0, 250 * BpUs, 1))
        flow_list.append(flowClass(37, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 150 * BpUs, 1))
        flow_list.append(flowClass(38, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(39, 0, None, None, src_id, des_id, 0, 15000000, 15000000, 0, 150 * BpUs, 1))
        flow_list.append(flowClass(40, 0, None, None, src_id, des_id, 0, 15000000, 15000000, 0, 270 * BpUs, 1))
        # flow_list.append(flowClass(41, 0, None, None, src_id, des_id, 0, 14000000, 14000000, 0, 150 * BpUs, 1))
        flow_list.append(flowClass(42, 0, None, None, src_id, des_id, 0, 20000000, 20000000, 0, 150 * BpUs, 1))
        flow_list.append(flowClass(43, 0, None, None, src_id, des_id, 0, 20000000, 20000000, 0, 150 * BpUs, 1))
        flow_list.append(flowClass(44, 0, None, None, src_id, des_id, 0, 20000000, 20000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(45, 0, None, None, src_id, des_id, 0, 50000000, 50000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(46, 0, None, None, src_id, des_id, 0, 50000000, 50000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(47, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 270 * BpUs, 1))
        flow_list.append(flowClass(48, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 190 * BpUs, 1))
        flow_list.append(flowClass(49, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 190 * BpUs, 1))
        flow_list.append(flowClass(50, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(51, 0, None, None, src_id, des_id, 0, 25000000, 25000000, 0, 150 * BpUs, 1))
        flow_list.append(flowClass(52, 0, None, None, src_id, des_id, 0, 100000000, 100000000, 0, 190 * BpUs, 1))
        flow_list.append(flowClass(53, 0, None, None, src_id, des_id, 0, 1000000000, 1000000000, 0, 210 * BpUs, 1))
        flow_list.append(flowClass(54, 0, None, None, src_id, des_id, 0, 25000000, 25000000, 0, 150 * BpUs, 1))
        # flow_list.append(flowClass(55, 0, None, None, src_id, des_id, 0, 31000000, 31000000, 0, 210 * BpUs, 1))
        # flow_list.append(flowClass(56, 0, None, None, src_id, des_id, 0, 32000000, 32000000, 0, 170 * BpUs, 1))
        # flow_list.append(flowClass(57, 0, None, None, src_id, des_id, 0, 33000000, 33000000, 0, 210 * BpUs, 1))
        # flow_list.append(flowClass(58, 0, None, None, src_id, des_id, 0, 33000000, 33000000, 0, 190 * BpUs, 1))
        # flow_list.append(flowClass(59, 0, None, None, src_id, des_id, 0, 33000000, 33000000, 0, 210 * BpUs, 1))
        # flow_list.append(flowClass(60, 0, None, None, src_id, des_id, 0, 34000000, 34000000, 0, 270 * BpUs, 1))
        # flow_list.append(flowClass(61, 0, None, None, src_id, des_id, 0, 34000000, 34000000, 0, 250 * BpUs, 1))
        # flow_list.append(flowClass(62, 0, None, None, src_id, des_id, 0, 36000000, 36000000, 0, 210 * BpUs, 1))
        # flow_list.append(flowClass(63, 0, None, None, src_id, des_id, 0, 36000000, 36000000, 0, 170 * BpUs, 1))


        return flow_list
    #-------------------------------------------------
    #函数名称：genSpecificFlows
    #输入参数：根据flow_spec_list创建flowClass对象列表
    #输出参数：生成流列表
    #函数描述：用于根据flow_spec_list产生对应的流对象，可以用作和别的软件的接口
    #-------------------------------------------------
    def genSpecificFlows(self,netTopo, flow_spec_list):
        flow_list = []
        flow_id = 0
        for flow_spec in flow_spec_list:
            src_node_id = flow_spec[0]
            dst_node_id = flow_spec[1]
            priority = flow_spec[2]
            period = flow_spec[3]
            ddl = flow_spec[4]
            jitter = flow_spec[5]
            frame_size = flow_spec[6]
            rdd = flow_spec[7]
            path_list = flow_spec[8]
            src_node = [node for node in netTopo._esSet if node._nodeId == src_node_id][0]
            dst_node = [node for node in netTopo._esSet if node._nodeId == dst_node_id][0]
            for rdd_index in range(rdd):
                flow = flowClass(flow_id, rdd_index, src_node, dst_node, priority, period, ddl, jitter, frame_size, rdd)
                # 分配路由
                if len(path_list) > 0:  # 指定路由
                    for i in range(len(path_list[rdd_index]) - 1):
                        s_id = path_list[rdd_index][i]
                        d_id = path_list[rdd_index][i + 1]
                        for link in netTopo._linkSet:
                            if link._srcNode._nodeId == s_id and link._dstNode._nodeId == d_id:
                                flow._assignPath.append(link)
                                break
                # 添加到flow_list中
                flow_list.append(flow)
            flow_id += 1
        return flow_list

    # def generate_random_TTP_flows(self,TTP_node_num):
    #     flow_list = []
    #     flow_id = 0
    #     for p in range(0, TTP_node_num):
    #         node = Node(p,head.NodeType.TTP_ES,p)
    #         node.node_name = "TTP_ES" + str(p)
    #         dur = randint(head.TTP_Min_dur, head.TTP_Max_dur)
    #         flow_list.append(
    #             Flow(flow_id, 0, node, node, 0, dur, dur, 0, dur, 1, head.Protocol.TTP))
    #
    #         flow_id += 1
    #
    #     return flow_list
    #
    #
    #
    #
    def indicate_flows(self,netTopo,sw_num):
        flow_list = []
        flow_id = 0

        flow_list.append(
            flowClass(0, 0,None, None,netTopo._esSet[1 - sw_num]._nodeId, netTopo._esSet[2 - sw_num]._nodeId, 0, 1000000,
                 1000000, 0, 2500, 1))
        flow_list.append(
            flowClass(1, 0, None, None,netTopo._esSet[1 - sw_num]._nodeId, netTopo._esSet[2 - sw_num]._nodeId, 0, 5000000,
                 5000000, 0, 2500, 1))
        # flow_list.append(
        #     Flow(2, 0, self._net_topo.es_set_[1 - sw_num], self._net_topo.es_set_[2 - sw_num], 0, 10000000,
        #          10000000, 0, 125, 1,head.Protocol.TSN))
        # flow_list.append(
        #     Flow(3, 0, self._net_topo.es_set_[1 - sw_num], self._net_topo.es_set_[2 - sw_num], 0, 5000000,
        #          5000000, 0, 125, 1,head.Protocol.TSN))
        return flow_list
