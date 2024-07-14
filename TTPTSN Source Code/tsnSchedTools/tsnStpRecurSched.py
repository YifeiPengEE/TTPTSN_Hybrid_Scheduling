from head import *
#我对比了orr和我们自己的算法，惊讶的发现我们自己算法的可调度性超高，我现在担心是不是我的调度算法有啥问题
#所以写了这样一个验证程序，即，采用stp选路，这样可以保证路是一样的，然后对比相同路径下recurSched算法和ILP算法的可调度性

class tsnStpRecurSched:
    def __init__(self):
        print('tsnStpRecurSched')
        self.netOpTool = network_op_tools()
    def routeMethod(self, netTopoClass, trafficClass):
        for flow in trafficClass._flowObjList:
            pathLinkSet = self.netOpTool.spFlowobjLinkobj(netTopoClass, flow)

            routeValid = 1
            for link in pathLinkSet:
                if link._occupyBw + flow._flowBandwith > head.DEFAULT_LINK_MAX_BANDWIDTH:
                    routeValid = 0
                    break

            if routeValid:
                flow._isRouted = head.AssignStatus.Assigned
                flow._assignPath = pathLinkSet
                # 5.将链路加入各条流中
                for link in pathLinkSet:
                    link.addFlowObjToLink(flow)
                    link._occupyBw += flow._flowBandwith
                    link._occupyFlowCnt += 1
                    if link._dstNode._nodeType == head.NodeType.Switch:
                        link._dstNode._flowCnt += 1
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
