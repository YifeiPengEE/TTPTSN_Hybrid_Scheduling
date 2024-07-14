from networkTools.debugToolClass import *
from head import *

class network_eval_tools:
    # 类说明：该类提供网络的评估工具,端到端延迟、抖动以及失效概率评估，评估算法包括网络演算、累加、概率等
    # 类版本：v0.3
    # 类版本说明：当前版本仅提供最简单的算法

    def __init__(self):
        print('network_eval_tools 构造函数')
        self.dbug = debugToolClass()

    def evalSchedulableRatio(self,trafficClass):
        print('schedulable_ratio 计算可调度性')
        # print('total traffic num = ' + str(traffic_analysis._traffic_num))
        assignNum = trafficClass.assigned_traffic_num_statistic(trafficClass._flowObjList)
        ttNum = trafficClass._flowNum
        # print('assigned num = ' + str(traffic_analysis._assigned_traffic_num))
        ratio = assignNum / ttNum * 100
        print('schedulable_ratio = '
              + str(ratio)
              + '%')
        return ratio
    def evalRouteAbleRatio(self,trafficClass):
        print('evalRouteAbleRatio 计算路由性')
        # print('total traffic num = ' + str(traffic_analysis._traffic_num))
        flowNum = 0
        for flow in trafficClass._flowObjList:
            if flow._isRouted == AssignStatus.Assigned:
                flowNum = flowNum + 1
        return flowNum
    def eval_link_max_load(self, net_topo, traffic_analysis):
        print("eval_link_max_load 计算流数量最多的链路上的流数量")
        link_load_list = []
        max_load = 0
        max_load_cnt = 0

        for path in net_topo.link_set_:
            link_load_list.append(len(path.flow_set))

        max_load = max(link_load_list)
        max_load_cnt = link_load_list.count(max_load)
        print("流数量最多的链路上的流数量 = ",max_load,"其条数为 = ",max_load_cnt)
        return max_load,max_load_cnt

    def eval_link_utilization(self, net_topo, traffic_analysis):
        print('link_utilization 链路利用率计算')

    def eval_net_link_utilization(self, net_topo, traffic_analysis):
        print('net_link_utilization 整个网络链路总利用率计算')
        cnt = 0
        for path in net_topo.link_set_:
            if len(path.flow_set) > 0:
                cnt += 1
        return cnt/len(net_topo.link_set_)

    def eval_time_cacul(self, net_topo, traffic_analysis):
        print('solve_time_cacul 求解耗时计算')

    def eval_result_cross(self, net_topo, traffic_analysis):
        print('solve_result_cross 判断任意link上规划的门是否存在重叠')
        for link in net_topo.link_set_:
            if link == None :
                return
            print('link name = ' + link.link_name)
            for res1 in link.flow_set:

                if res1 == []:
                    continue
                for res2 in link.flow_set:
                    if res2 == []:
                        continue
                    if res1[0] != res2[0]:
                        if (res1[1]>=res2[1] and res1[1]<res2[2]) or (res1[2]<res2[2] and res1[2]>res2[1]):
                            print('验证失败，traffic shchedule error !!!!')
                            self.dbug.debug_print_one_shcdule_result(res1)
                            self.dbug.debug_print_one_shcdule_result(res2)
                            return
        print('验证完成，未发现调度结果重叠')

    #路由相关平均函数：平均长度
    def route_eval_avge_routelen(self, net_topo, traffic_analysis):
        print("平均路径长度计算")
        total_assigned_route_len = 0
        total_flow_cnt = 0
        #每条流路由长度之和除以流的数量
        for item in traffic_analysis._test_traffic:
            if item.is_assigned == head.AssignStatus.Assigned :
                total_assigned_route_len = total_assigned_route_len + len(item._assign_path)
                total_flow_cnt = total_flow_cnt + 1

        print("平均路径长度为 = ",total_assigned_route_len/total_flow_cnt)
        return total_assigned_route_len/total_flow_cnt

    #实现最小最大归一化
    def minmaxNormalization(self,x,xmax,xmin):

        return (x-xmin)/(xmax-xmin)

    #评估路由总跳数
    def est_route_hop(self,route):

        value = self.minmaxNormalization(len(route),head.DEFAULT_MAX_HOP,2)

        return 1-value
    #评估路由已占用带宽
    def est_route_bandwith(self,route):
        value = 0
        bandwidth = 0
        for link in route:
            bandwidth += link._occupyBw
        bandwidth /= len(route)

        value = self.minmaxNormalization(bandwidth,head.DEFAULT_LINK_MAX_BANDWIDTH,0)

        return 1 - value

    #评估路由链路已占用流个数
    def est_route_flownum(self,route):
        value = 0
        flownum = 0
        for link in route:
            flownum += len(link._flowSet)

        flownum /= len(route)
        value = self.minmaxNormalization(flownum,head.TOTAL_FLOW_NUM,0)

        return 1 - value

    #评估路由设备已占用流个数：
    def est_route_devnum(self,route):
        value = 0
        devnum = 0

        sw_set = []
        for i in range(len(route)-1):
            sw_set.append(route[i]._dstNode)

        for node in sw_set:
            for link in node._egressLink:
                devnum += len(link._flowSet)


        value = self.minmaxNormalization(devnum,head.TOTAL_FLOW_NUM * (len(route)-1),0)

        return 1 - value

    #评估路由DoCL：值越接近1说明排布后，出端口和入端口一致性高
    def est_route_DoCL(self,route):
        value = 0

        for i in range(len(route) - 1):
            # 使用循环计算相同元素的个数
            count_common_elements = 0
            for item in route[i]._flowSet:
                if item in route[i+1]._flowSet:
                    count_common_elements += 1

            if len(route[i+1]._flowSet) == 0:
                value += 1.0
            elif count_common_elements == 0:
                value += 0.0
            else:
                value += count_common_elements / max(len(route[i]._flowSet),len(route[i+1]._flowSet))

        # print("value = ",value)
        value = self.minmaxNormalization(value, len(route) - 1, 0)

        return value

    #评估路由DoC:值越接近1说明冲突越小
    def est_route_DoC(self,route,period):
        value = 0

        for link in route:
            cnt = 0
            for item in link._flowSet:
                flow = item
                if flow._period % period == 0 or period % flow._period == 0:
                    cnt += 1

            if len(link._flowSet) == 0:
                value += 1.0
            else:
                value += cnt / len(link._flowSet)

        value = self.minmaxNormalization(value, len(route), 0)
        return value

    #评估网络拓扑上链路平均带宽
    def eval_bd_linkavg(self,netTopoClass):
        #1.统计每条链路的
        total_linknum = 0
        total_bd = 0
        for link in netTopoClass._linkSet:
            total_linknum += 1
            if len(link._flowSet) > 0:
                total_bd += link._occupyBw

        #2.计算平均带宽
        return round(total_bd/total_linknum,3)

    #评估网络拓扑上链路最大带宽
    def eval_bd_linkmax(self, netTopoClass):
        max_bd = 0.0
        for link in netTopoClass._linkSet:
            if max_bd < link._occupyBw:
                max_bd = link._occupyBw
        return max_bd


    #评估网络拓扑上链路最大带宽的链路数量
    def eval_bd_linkmax_link_num(self, net_topo):

        max_bd = self.eval_bd_linkmax(net_topo)
        avg_bd = self.eval_bd_linkavg(net_topo)
        link_num = 0
        for link in net_topo.link_set_:
            if max_bd * 0.8 < link.occupy_bandwith:
                link_num += 1
        return link_num

    #评估流的路径平均长度
    def eval_routelen_flowavg(self,trafficClass):
        #1.统计每条流
        flow_num = trafficClass._flowNum
        total_flow_route_len = 0
        for flow in trafficClass._flowObjList:
            # print("len(flow._assign_path) = ",len(flow._assign_path))
            total_flow_route_len += len(flow._assignPath)

        #2.计算平均路由长度
        return round(total_flow_route_len/flow_num,3)
    #评估流的最大长度
    def eval_routelen_flowmax(self,trafficClass):
        #1.统计每条流
        max_flow_route_len = 0
        for flow in trafficClass._flowObjList:
            if max_flow_route_len < len(flow._assignPath):
                max_flow_route_len = len(flow._assignPath)

        #2.计算平均路由长度
        return max_flow_route_len
    #评估链路平均流数量
    def eval_arlf_linkavg(self,netTopoClass):
        #1.统计每条链路的
        total_linknum = 0
        total_arlf = 0
        for link in netTopoClass._linkSet:
            total_linknum += 1
            if len(link._flowSet) > 0:
                total_arlf += link._occupyFlowCnt

        #2.计算平均流数量
        return round(total_arlf/total_linknum,3)
    #评估链路最大流数量
    def eval_arlf_linkmax(self,netTopoClass):
        #1.统计每条链路的
        max_arlf = 0
        for link in netTopoClass._linkSet:
            if max_arlf < link._occupyFlowCnt:
                max_arlf = link._occupyFlowCnt

        #2.计算最大流数量
        return max_arlf

    #评估链路最大流数量的程度
    def eval_arlf_linkmax_num(self,net_topo):
        max_arlf = self.eval_arlf_linkmax(net_topo)
        num_arlf = 0
        #1.统计每条链路的
        for link in net_topo._linkSet:
            if max_arlf * 0.8 < link._occupyFlowCnt:
                num_arlf += 1

        return num_arlf

    #评估节点平均流数量
    def eval_ardf_nodeavg(self,net_topo):
        #1.统计每台设备的
        total_nodenum = 0
        total_ardf = 0
        for node in net_topo._swSet:
            total_nodenum += 1
            if node._flowCnt > 0:
                total_ardf += node._flowCnt

        #2.计算平均流数量
        return round(total_ardf/total_nodenum,3)
    #评估节点最大流数量
    def eval_ardf_nodemax(self, net_topo):
        # 1.统计每台设备的
        max_ardf = 0
        for node in net_topo._swSet:
            if max_ardf < node._flowCnt:
                max_ardf = node._flowCnt

        # 2.计算平均流数量
        return max_ardf

    #评估节点最大流数量程度
    def eval_ardf_nodemax_num(self, net_topo):
        # 1.统计每台设备的
        max_ardf = self.eval_ardf_nodemax(net_topo)
        num_ardf = 0
        for node in net_topo._swSet:
            if max_ardf * 0.8 <= node._flowCnt:
                num_ardf += 1


        return num_ardf

    '''
        分析求解结果，将求解的每个窗口加入到
        链路的occupyWindowList窗口中去，用于最终分析
        bus guard的数量
    '''
    def evalBgNum(self,netTopoClass):
        for link in netTopoClass._linkSet:
            if len(link._flowSet) != 0:
                for flow in link._flowSet:
                    qbv_window_list = flow._assignQbv
                    for qbv_window in qbv_window_list:
                        if len(link._occupyWindowList) == 0:
                            link._occupyWindowList.append(qbv_window)

                        else:
                            add_succ = 0
                            cover_pos_1 = -1
                            cover_pos_2 = -1
                            for window in link._occupyWindowList:
                                if qbv_window[0]<= window[1]+0.1 and qbv_window[1]>window[1]:
                                    window[1] = qbv_window[1]
                                    add_succ = 1
                                    cover_pos_1 = link._occupyWindowList.index(window)
                                elif qbv_window[1]>= window[0]-0.1 and qbv_window[0]< window[0]:
                                    window[0] = qbv_window[0]
                                    add_succ = 1
                                    cover_pos_2 = link._occupyWindowList.index(window)

                            if add_succ == 0:
                                link._occupyWindowList.append(qbv_window)

                            if cover_pos_1>=0 and cover_pos_2>=0:
                                w1 = link._occupyWindowList[cover_pos_1]
                                w2 = link._occupyWindowList[cover_pos_2]
                                w1w2 = w1+w2
                                w1w2_min = min(w1w2)
                                w1w2_max = max(w1w2)
                                w1w2 = [w1w2_min,w1w2_max]
                                link._occupyWindowList.pop(cover_pos_1)
                                link._occupyWindowList.pop(cover_pos_2-1)
                                link._occupyWindowList.append(w1w2)


        total_bg = 0
        for link in netTopoClass._linkSet:
            # print("link name = ", link._linkName)
            # print("link window set = ",link._occupyWindowList)
            total_bg += len(link._occupyWindowList)
        # print("total_bg = ",total_bg)
        return total_bg

