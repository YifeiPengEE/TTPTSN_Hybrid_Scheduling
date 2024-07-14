import copy
import matplotlib.pyplot as plt
from head import *
import cplex
import random
from time import *

class tsnRecurSchedMethod:
    def __init__(self):
        # print('tsnRecurSchedMethod')
        self.net_op_tools = network_op_tools()
        self.net_eval_tools = network_eval_tools()
        #路由评估权重
        self.hop_c = 0.2
        self.bd_c = 0.2
        self.fn_c = 2
        self.dn_c = 2
        self.DoCL_c = 0.2
        self.DoC_c = 0.2

    def list_maxindex(self,x_list):

        ele_value = 0
        ele_index = 0
        cnt = 0

        for ele in x_list:
            if ele_value < ele:
                ele_value = ele
                ele_index = cnt

            cnt += 1

        return ele_index


    #-------------------------------------------------
    #函数名称：flowSetRoutePostHandle_bandwith
    #输入参数：对于流集合进行后处理，路由后重新排序在进行调度，按照带宽大小进行排序
    #输出参数：无
    #函数描述：对流的调度前处理
    #-------------------------------------------------
    def flowSetRoutePostHandle_bandwith(self,flowObjList):
        oriFlowset = flowObjList
        routeSucessFlowObjList = []
        orderRouteSucessFlowObjList = []
        #1.获取路由成功的flowObj集合
        for flow in flowObjList:
            if flow._assignPath != []:
                routeSucessFlowObjList.append(flow)

        orderRouteSucessFlowObjList = sorted(routeSucessFlowObjList, key=lambda x: x._flowBandwith)


        return orderRouteSucessFlowObjList

    #-------------------------------------------------
    #函数名称：flowSetRoutePostHandle
    #输入参数：对于流集合进行后处理，路由后重新排序在进行调度
    #输出参数：无
    #函数描述：对流的调度前处理
    #-------------------------------------------------
    def flowSetRoutePostHandle(self,flowObjList):
        oriFlowset = flowObjList
        postFlowObjList = []

        for flow in oriFlowset:
            if postFlowObjList == []:
                postFlowObjList.append(flow)
                continue

            post_flow_value = []
            # 将flow与当前post_flow_set中的流进行比较，进而确定应该插入哪个位置

            for post_flow in postFlowObjList:
                # 判断flow 与 post_flow链路的重叠程度
                # print('flow = ',end='')
                # for link in flow._assign_path:
                #     print(link.link_name,',',end='')
                # print('')
                #
                # print('post_flow = ', end='')
                # for link in post_flow._assign_path:
                #     print(link.link_name,',',end='')
                # print('')


                same_value = len(list(set(flow._assignPath) & set(post_flow._assignPath)))
                post_flow_value.append(same_value)

            max_value = max(post_flow_value)
            max_value_index = post_flow_value.index(max_value)
            postFlowObjList.insert(max_value_index, flow)


        return postFlowObjList
    #-------------------------------------------------
    #函数名称：routeMethod
    #输入参数：tsnRecurSchedMethod算法的路由算法
    #输出参数：无
    #函数描述：用于求出每条流的路径
    #-------------------------------------------------
    def routeMethod(self,netTopoClass,trafficClass):

        self.net_op_tools.routeMethod(netTopoClass,trafficClass, _hop_c=0.2, _bd_c=0.2, _fn_c=0.2, _dn_c=0.2, _DoCL_c=0.2, _DoC_c=0.2
                    , M=10)

            #5.由于当前只测试路由，路由完成就意味着flow分配完成
            # flow.is_assigned = head.AssignStatus.Assigned
            # #debug
            # best_route_linkname = []
            # for link in best_route:
            #     best_route_linkname.append(link._linkName)
            # print("route_value_set = ",route_value_set,"best_route index = ",max(route_value_set),"best_route = ",best_route_linkname)
    #cut-through转发模式时延估计
    def CFlatency_calc(self,hop):
        #CF：cut-through forward
        return hop * (head.DEFAULT_LINK_DELAY + head.DEFAULT_PROC_DELAY)
    '''
        利用递归的方法，判断当前时隙是否可以排布该业务
    '''

    def link_idlewin_judge(self,hop,flow,idle_slot,trafficClass,offset):
        # print("link_idlewin_judge flow id = ",flow.flow_id," hop = ",hop," max_hop = ",len(flow._assign_path),"offset = ",offset)
        if hop == len(flow._assignPath):
            return 1
        else:

            link = flow._assignPath[hop]
            flow_period = flow._period
            flow_insnum = int(trafficClass._hyperPeriod / flow_period)
            flow_dur = flow._flowDur
            can_assign_flag = [0] * flow_insnum

            # print("link name = ", link.link_name,"flow_period = ",flow_period,"flow_insnum = ",flow_insnum)
            # 判断当前流的第一个实例是否可以排布在这个空隙
            for i in range(flow_insnum):
                start_pit = idle_slot[0] + i * flow_period + self.CFlatency_calc(hop) + offset
                end_pit = start_pit + flow_dur


                # 判断当前时隙对应的每个实例是否都空闲
                for slot in link._idleWindowList:
                    # print("ins_num = ",i,
                    #     "slot = ",slot ," size = ",slot[1]-slot[0],
                    #       "[start_pit , end_pit] = [",start_pit,",",end_pit,"]"," size = ",end_pit-start_pit)
                    if slot[0] <= start_pit and end_pit <= slot[1] and can_assign_flag[i] == 0:
                        can_assign_flag[i] = 1
                        break
                    else:
                        continue
                # print("can_assign_flag = ",can_assign_flag)
                if can_assign_flag[i] == 0:
                    break

            if sum(can_assign_flag) == flow_insnum:
                return self.link_idlewin_judge(hop + 1, flow , idle_slot,trafficClass,offset)
            else:
                #得到偏移量
                fault_index = can_assign_flag.index(0)
                start_pit = idle_slot[0] + fault_index * flow_period + self.CFlatency_calc(hop) + offset

                for slot in link._idleWindowList:
                    if slot[0] >= start_pit and slot[1] - slot[0] >= flow_dur:

                        # print("slot[0] = ",slot[0],"start_pit = ",start_pit," offset = ",offset)

                        return slot[0] - start_pit+ offset

                return 0

    '''
        利用递归的方法，删除空闲时隙
    '''
    def link_idlewin_del(self,hop,flow,idle_slot,trafficClass,offset):
        if hop < 0:
            return 1
        else:
            link = flow._assignPath[hop]
            flow_period = flow._period
            flow_insnum = int(trafficClass._hyperPeriod / flow_period)
            flow_dur = flow._flowDur

            # 表示当前时隙可以排布
            for i in reversed(range(flow_insnum)):
                start_pit = idle_slot[0] + i * flow_period + self.CFlatency_calc(hop) + offset
                end_pit = start_pit + flow_dur
                delete_index = -1
                # 判断当前时隙对应的每个实例是否都空闲
                for slot in link._idleWindowList:
                    if slot[0] == start_pit and end_pit == slot[1]:
                        delete_index = link._idleWindowList.index(slot)
                    elif slot[0] == start_pit and end_pit < slot[1]:
                        slot[0] = end_pit
                    elif slot[0] < start_pit and end_pit == slot[1]:
                        slot[1] = start_pit
                    elif slot[0] < start_pit and end_pit < slot[1]:
                        delete_index = link._idleWindowList.index(slot)
                    else:
                        continue

                if delete_index >= 0:
                    handle_slot = link._idleWindowList[delete_index]
                    if handle_slot[0] == start_pit and end_pit == handle_slot[1]:
                        link._idleWindowList.pop(delete_index)
                    elif handle_slot[0] < start_pit and end_pit < handle_slot[1]:
                        new_slot1 = copy.deepcopy([handle_slot[0], start_pit])
                        new_slot2 = copy.deepcopy([end_pit, handle_slot[1]])
                        link._idleWindowList.pop(delete_index)
                        link._idleWindowList.append(new_slot1)
                        link._idleWindowList.append(new_slot2)
            # 排序
            link._idleWindowList = sorted(link._idleWindowList, key=lambda x: x[0])
            self.link_idlewin_del(hop-1, flow, idle_slot, trafficClass,offset)
    '''
        第一个版本算法：该算法就是简单的搜索然后插空
    '''
    def schedMethod(self,netTopoClass,trafficClass):
        #[startPit,endPit]
        for flow in trafficClass._flowObjList:
            # print("flow id = ",flow.flow_id)
            can_assign = 0
            can_assign_index = -1

            if flow._assignPath == []:
                continue
            link = flow._assignPath[0]

            for idle_slot in link._idleWindowList:
                offset = 0
                while idle_slot[0] + offset <= idle_slot[1] :
                    can_assign = self.link_idlewin_judge(0,flow,idle_slot,trafficClass,offset)

                    if can_assign <= 1:
                        # print('sched error')
                        break

                    offset = can_assign

                if can_assign == 1:
                    can_assign_index = link._idleWindowList.index(idle_slot)
                    flow._startOffset = idle_slot[0] + offset
                    break
                elif can_assign == 0:
                    continue

            if can_assign_index >= 0:
                first_del_slot = link._idleWindowList[can_assign_index]
                # print("flow start time = ", first_del_slot)
                self.link_idlewin_del(len(flow._assignPath)-1,flow,first_del_slot,trafficClass,offset)

        self.calcQbvForeachFlowDetail(trafficClass)
            # for link in flow._assignPath:
            #     print("link name = ",link._linkName)
            #     print("idle window = ",link._idleWindowList)
        # print("schdule % = ",traffic_analysis._assigned_traffic_num/traffic_analysis._traffic_num * 100,"%")


    #-------------------------------------------------
    #函数名称：calcQbvForeachFlowDetail
    #输入参数：trafficClass
    #输出参数：无
    #函数描述：根据调度结果，获取每个流在每条路径上的实际情况。
    # 该版本详细标注了路径名称和各条路径上的信息。
    #-------------------------------------------------
    def calcQbvForeachFlowDetail(self,trafficClass):
        for flow in trafficClass._flowObjList:

            if flow._assignPath == [] or flow._startOffset < 0:
                continue
            trafficClass._assignFlowNum += 1
            flow._isAssigned = head.AssignStatus.Assigned

            flag = 0
            startoffset = flow._startOffset
            hop = 0
            flow_period = flow._period
            flow_insnum = int(trafficClass._hyperPeriod / flow_period)
            flow_dur = flow._flowDur

            for link in flow._assignPath:
                winList = []
                linkName = link._linkName
                winList.append([linkName])
                for i in range(flow_insnum):
                    tmpStartPit = startoffset + i*flow_period
                    tmpEndPit = startoffset + i*flow_period + flow_dur
                    winList.append([tmpStartPit,tmpEndPit])
                    if flag == 0:
                        flow._assignQbv.append([tmpStartPit, tmpEndPit])
                flow._assignQbvDetail.append(winList)
                flag = 1
                # print('flow._assignQbv = ',flow._assignQbv)
                # print('flow._assignQbvDetail = ', flow._assignQbvDetail)

    # 重路由本质上是在tsn调度器基础上进行了封装
    def reRouteMethod(self, netTopoClass, trafficClass, newAdjMatrix, reSchedFlowIdList):
        if len(reSchedFlowIdList) == 0:
            print('Error')
            return -1

        # x.备份原有邻接矩阵
        bpAdjMatrix = netTopoClass._adjMatrix
        netTopoClass._adjMatrix = newAdjMatrix
        # x.获取重调度的flowlist
        reSchedFlowObjList = []
        for flowId in reSchedFlowIdList:
            for flow in trafficClass._flowObjListOri:
                if flow._flowId == flowId:
                    reSchedFlowObjList.append(flow)

        # x.创建用来冲调度的trafficClass
        reSchedTf = head.trafficClass(netTopoClass, reSchedFlowObjList, reSchedFlag=True)

        # x.重路由
        self.routeMethod(netTopoClass, reSchedTf)

        # x.重调度
        self.schedMethod(netTopoClass, reSchedTf)
        # x.还原邻接矩阵
        netTopoClass._adjMatrix = bpAdjMatrix

        return reSchedTf

if __name__ == '__main__':
    print('ssss')

    period_list = [500000]  # 所有和时间相关得参数，单位是ns
    flowNum = 4

    #x.创建打印工具
    debugTool = debugToolClass()
    #x.创建流量生成器
    tgTool = trafficGeneratorToolClass()
    # x.创建调度器
    tsnRecurScheTool = tsnRecurSchedMethod()
    #x.创建绘画工具
    net_draw_tool = NetworkDrawTools(1, 1)

    #验证重路由
    reRouteTopo = rerouteTopo()

    net_draw_tool.network_topo_plot(reRouteTopo._topology)
    net_draw_tool.network_topo_plot(reRouteTopo._topologyError)

    #x.生成netTopoClass
    netTopo = netTopoClass(reRouteTopo._topology, reRouteTopo._swNum, reRouteTopo._esNum)

    # x.生成flowObjList
    # flowObjList = tgTool.generateRandomFlows(netTopo, reRouteTopo._swNum, reRouteTopo._esNum, period_list, flowNum)
    flowObjList = tgTool.determGenerateRandomFlows(netTopo,0,1, period_list, flowNum)
    # x.分析流量
    tf = trafficClass(netTopo, flowObjList)
    #x.打印
    debugTool.printTrafficClass(tf)

    # x.进行路由
    tsnRecurScheTool.routeMethod(netTopo, tf)

    # x.进行调度
    tsnRecurScheTool.schedMethod(netTopo, tf)
    print('normal')
    # debugTool.printFlowObjListRoute(tf)
    debugTool.printFlowObjQbv(tf)
    #x.构造故障
    newTopo = reRouteTopo._topologyError
    rerouteFlowIdList = [0,1,2,3]

    print('reroute')
    #.进行重调度
    rerouteTf = tsnRecurScheTool.reRouteMethod(netTopo,tf,newTopo,rerouteFlowIdList)
    debugTool.printFlowObjQbv(rerouteTf)
    # debugTool.printFlowObjListRoute(rerouteTf)

    print('end')