import head

class debugToolClass:
    # 类说明：该类提供网络一些通用打印模板
    # 类版本：v0.2
    # 类版本说明：当前版本仅提供最简单的算法
    def __init__(self):
        print('debug_class 该类提供一系列通用打印模板')
    #-------------------------------------------------
    #函数名称：printFlowObjList
    #输入参数：flowClass类的对象所构成的list
    #输出参数：无
    #函数描述：用于打印flowClass的对象所构成的list
    #-------------------------------------------------
    def printFlowObjList(self,flowObjList):
        if head.Debug_enable != 1:
            return
        for item in flowObjList:

            print('| item id = '+str(item._flowId)
                  + '| sub item id = ' + str(item._subflowId)
                  +'| src = '+item._srcNode._nodeName
                  +'| des = '+item._dstNode._nodeName
                  +'| priority = ' + str(item._priority)
                  +'| period = ' + str(item._period) + 'ns'
                  +'| ddl = ' + str(item._deadline) + 'ns'
                  +'| jit = ' + str(item._jitter) + 'ns'
                  +'| len = ' + str(item._frameSize) + 'byte'
                  + '| redundancy = ' + str(item._redundancy)
                  + '| flow_type = ' + 'TSN'
                  + '| is_assigned = ' + str(item._isAssigned)
                  +'| Mbps = ' + str(item._frameSize * 8 / item._period *1000000000 / 1000000)
                  )
    #-------------------------------------------------
    #函数名称：printTrafficClass
    #输入参数：trafficClass对象
    #输出参数：无
    #函数描述：用于打印解析后的流量集合
    #-------------------------------------------------
    def printTrafficClass(self,trafficClass):
        if head.Debug_enable != 1:
            return
        print('hyperiod = ' + str(trafficClass._hyperPeriod)+' ns')
        print('gcd = ' + str(trafficClass._gcd) +' ns')
        print('flowNum = ' + str(trafficClass._flowNum) +' 条')

        for item in trafficClass._flowObjList:

            if item._srcNode != None:

                print('| item id = '+str(item._flowId)
                      + '| sub item id = ' + str(item._subflowId)
                      +'| src = '+item._srcNode._nodeName
                      +'| des = '+item._dstNode._nodeName
                      +'| priority = ' + str(item._priority)
                      +'| period = ' + str(item._period) + 'ns'
                      +'| ddl = ' + str(item._deadline) + 'ns'
                      +'| jit = ' + str(item._jitter) + 'ns'
                      +'| len = ' + str(item._frameSize) + 'byte'
                      + '| redundancy = ' + str(item._redundancy)
                      + '| flow_type = ' + 'TSN'
                      + '| is_assigned = ' + str(item._isAssigned)
                      +'| MBps = ' + str(item._frameSize  / item._period *1000000000 / 1000000)
                      + '| flowType = ' + item._flowType
                      + '| worce E2E dur = ' + str(item._rcDelay))

            else:
                print('| item id = '+str(item._flowId)
                      + '| sub item id = ' + str(item._subflowId)
                      +'| priority = ' + str(item._priority)
                      +'| period = ' + str(item._period) + 'ns'
                      +'| ddl = ' + str(item._deadline) + 'ns'
                      +'| jit = ' + str(item._jitter) + 'ns'
                      +'| len = ' + str(item._frameSize) + 'byte'
                      + '| redundancy = ' + str(item._redundancy)
                      + '| flow_type = ' + 'TSN'
                      + '| is_assigned = ' + str(item._isAssigned)
                      +'| MBps = ' + str(item._frameSize  / item._period *1000000000 / 1000000)
                      + '| flowType = ' + item._flowType
                      + '| worce E2E dur = ' + str(item._rcDelay))

    def printFlowObjQbv(self,trafficClass):
        for flow in trafficClass._flowObjList:
            print('flowid = ',str(flow._flowId))
            print('_assignQbv = ',flow._assignQbvDetail)

    def printFlowObjHole(self,trafficClass):
        for flow in trafficClass._flowObjList:
            print('flowid = ',str(flow._flowId))
            print('_holeIndexList = ',flow._holeIndexList)


    def printFlowObj(self,flow):
        print('| item id = ' + str(flow._flowId)
              + '| sub item id = ' + str(flow._subflowId)
              + '| src = ' + flow._srcNode._nodeName
              + '| des = ' + flow._dstNode._nodeName
              + '| priority = ' + str(flow._priority)
              + '| period = ' + str(flow._period) + 'ns'
              + '| ddl = ' + str(flow._deadline) + 'ns'
              + '| jit = ' + str(flow._jitter) + 'ns'
              + '| len = ' + str(flow._frameSize) + 'byte'
              + '| redundancy = ' + str(flow._redundancy)
              + '| flow_type = ' + 'TSN'
              + '| is_assigned = ' + str(flow._isAssigned)
              + '| MBps = ' + str(flow._frameSize / flow._period * 1000000000 / 1000000)
              + '| flowType = ' + flow._flowType
              + '| worce E2E dur = ' + str(flow._rcDelay) )
    def printFlowObjListRoute(self,trafficClass):
        for flow in trafficClass._flowObjList:
            print('flowid = ', str(flow._flowId))
            for link in flow._assignPath:
                print(link._linkName,end=',')
            print('')
    def printRouteSet(self,routeSet):
        for item in routeSet:
            for link in item:
                print(link._linkName,end=',')
            print('')
    #
    #
    # def debug_print_path(self,path):
    #     if head.Debug_enable != 1:
    #         return
    #     for item in path:
    #         print(item.link_name + '->', end='')
    #     print('')
    #
    #
    # def debug_print_one_traffic(self,traffic_item):
    #     if head.Debug_enable != 1:
    #         return
    #     print('| item id = ' + str(traffic_item.flow_id)
    #           + '| src = ' + traffic_item.source_node.node_name
    #           + '| des = ' + traffic_item.dest_node.node_name
    #           + '| priority = ' + str(traffic_item.priority)
    #           + '| period = ' + str(traffic_item.period)
    #           + '| ddl = ' + str(traffic_item.deadline)
    #           + '| jit = ' + str(traffic_item.jitter)
    #           + '| len = ' + str(traffic_item.frame_size)
    #           + '| redundancy = ' + str(traffic_item.redundancy)
    #           + '| is_assigned = ' + str(traffic_item.is_assigned)
    #           )
    #
    # def debug_print_one_shcdule_result(self,scheduled_reult):
    #     print('flow_id = '+str(scheduled_reult[0])
    #           +',starttime = '+str(scheduled_reult[1])
    #           +',endtime = '+str(scheduled_reult[2]))
    #
    # def debug_print_flow_in_path(self, Link2):
    #     # 打印属于某条链路的所有流的ID
    #     if head.Debug_enable != 1:
    #         return
    #     print("debug_print_flow_in_path:  Link2=" + Link2.link_name, end='')
    #     for flow in Link2.flow_set:
    #         print('| flow_id = ' + str(flow[0]) + ', ', end='')
    #     print("\n")
