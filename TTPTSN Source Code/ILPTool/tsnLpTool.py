from head import *
import time


# 我看到了太多基于整数规划的例子，这些例子存在很多共性的地方，于是乎我将这些共性的地方做成这个库

class tsnLpTool:
    def __init__(self):
        print('tsnLpTool')

    def printSolution(self, problem):
        # Print the solution
        print("Solution status = ", problem.solution.get_status())
        print("varible name  = ", problem.variables.get_names())
        print("Solution value  = ", problem.solution.get_objective_value())
        print("Values          = ", problem.solution.get_values())
        print("var num = ", len(problem.variables.get_names()))

        nameList = problem.variables.get_names()
        resultList = problem.solution.get_values()
        for name in nameList:
            index = nameList.index(name)
            print(name, ' = ', resultList[index])

    def printConstraintsVars(self, constraintNames, constraintRows, constraintSenses, constraintRhs):
        print("***----------------------------**")
        print('constraintNames = ', constraintNames)
        print('constraintRows = ', constraintRows)
        print('constraintSenses = ', constraintSenses)
        print('constraintRhs = ', constraintRhs)

    ########################################################
    ##  路由相关函数
    ########################################################
    # 用于路由的变量被放置在link类和flow类中
    def genRouteLpVars(self, netTopoClass, trafficClass, problem):
        coffList = []
        lbList = []
        ubList = []
        typesList = ""
        namesList = []
        routedFlowNum = trafficClass.assignedRouteNumStatistic(trafficClass._flowObjList)
        print('routedFlowNum = ', routedFlowNum)
        # 决策变量route
        for flow in trafficClass._flowObjList:
            if routedFlowNum <= 0 and flow._assignPath == []:
                srcNode = flow._srcNode
                dstNode = flow._dstNode

                for link in netTopoClass._linkSet:

                    if link._srcNode == srcNode or link._srcNode == dstNode \
                            or link._dstNode == srcNode or link._dstNode == dstNode \
                            or (
                            link._srcNode._nodeType == head.NodeType.Switch and link._dstNode._nodeType == head.NodeType.Switch):
                        tmpVariName = "r_" + link._linkName + "_flowid" + int(
                            flow._flowId).__str__() + "_subflowid" + int(
                            flow._subflowId).__str__()
                        coffList.append(0)
                        lbList.append(0)
                        ubList.append(1)
                        typesList += "I"
                        namesList.append(tmpVariName)
                        # 存储变量
                        link._RouteLpVars[flow] = tmpVariName
                        flow._RouteLpVars.append(tmpVariName)
            elif routedFlowNum > 0 and flow._assignPath != []:

                for link in flow._assignPath:
                    tmpVariName = "r_" + link._linkName + "_flowid" + int(
                        flow._flowId).__str__() + "_subflowid" + int(
                        flow._subflowId).__str__()
                    coffList.append(0)
                    lbList.append(1)
                    ubList.append(1)
                    typesList += "I"
                    namesList.append(tmpVariName)
                    # 存储变量
                    link._RouteLpVars[flow] = tmpVariName
                    flow._RouteLpVars.append(tmpVariName)
        problem.variables.add(obj=coffList, lb=lbList, ub=ubList, types=typesList, names=namesList)
        # print("var num = ", len(problem.variables.get_names()))
        # print(problem.variables.get_names())

    # 生成源节点与目的节点关于路由的约束（本质上是针对出度和入度进行的约束）
    def genRouteSrcNodeDstNodeConstraints(self, trafficClass, problem, startCnt):
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt

        for flow in trafficClass._flowObjList:
            if flow._assignPath == []:
                srcNode = flow._srcNode
                srcEgressLinkSet = srcNode._egressLink
                srcIgressLinkSet = srcNode._ingressLink
                dstNode = flow._dstNode
                dstIgressLinkSet = dstNode._ingressLink
                dstEgressLinkSet = dstNode._egressLink
                # ①源节点egress约束
                tmpCrowName = []
                tmpCrowCoff = []
                for link in srcEgressLinkSet:
                    tmpCrowName.append(link._RouteLpVars[flow])
                    tmpCrowCoff.append(1)
                tmpCrowName.append(flow._FlowValidLpVars[0])
                tmpCrowCoff.append(-flow._redundancy)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintSenses.append("E")
                constraintRhs.append(0)
                constraintCnt += 1
                # ②源节点igress约束
                tmpCrowName = []
                tmpCrowCoff = []
                for link in srcIgressLinkSet:
                    tmpCrowName.append(link._RouteLpVars[flow])
                    tmpCrowCoff.append(1)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintSenses.append("E")
                constraintRhs.append(0)
                constraintCnt += 1
                # ③目的egress节点约束
                tmpCrowName = []
                tmpCrowCoff = []
                for link in dstEgressLinkSet:
                    tmpCrowName.append(link._RouteLpVars[flow])
                    tmpCrowCoff.append(1)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintSenses.append("E")
                constraintRhs.append(0)
                constraintCnt += 1
                # ④目的节点ingress约束
                tmpCrowName = []
                tmpCrowCoff = []
                for link in dstIgressLinkSet:
                    tmpCrowName.append(link._RouteLpVars[flow])
                    tmpCrowCoff.append(1)
                tmpCrowName.append(flow._FlowValidLpVars[0])
                tmpCrowCoff.append(-flow._redundancy)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintSenses.append("E")
                constraintRhs.append(0)
                constraintCnt += 1

        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)

        print(problem.linear_constraints.get_names())

        return constraintCnt

    # 生成交换机关于路由的约束（本质上是出度==入度,但是要求需要针对各个流来考虑）
    # 并且要求，出度的和或入度的和小于等于1
    def genRouteSwitchConstraints(self, netTopoClass, trafficClass, problem, startCnt):
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt

        # 1.出度==入度
        for flow in trafficClass._flowObjList:
            for node in netTopoClass._swSet:
                swEgressLinkSet = node._egressLink
                swIgressLinkSet = node._ingressLink

                tmpCrowName = []
                tmpCrowCoff = []
                for link in swIgressLinkSet:
                    if flow._assignPath == [] and link._RouteLpVars.get(flow) != None:
                        tmpCrowName.append(link._RouteLpVars[flow])
                        tmpCrowCoff.append(1)

                for link in swEgressLinkSet:
                    if flow._assignPath == [] and link._RouteLpVars.get(flow) != None:
                        tmpCrowName.append(link._RouteLpVars[flow])
                        tmpCrowCoff.append(-1)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintSenses.append("E")
                constraintRhs.append(0)
                constraintCnt += 1

        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)

        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        # 2.出度的和或入度的和小于等于1,这里我们只对入度进行限定
        for flow in trafficClass._flowObjList:
            for node in netTopoClass._swSet:
                swIgressLinkSet = node._ingressLink

                tmpCrowName = []
                tmpCrowCoff = []
                for link in swIgressLinkSet:
                    if flow._assignPath == [] and link._RouteLpVars.get(flow) != None:
                        tmpCrowName.append(link._RouteLpVars[flow])
                        tmpCrowCoff.append(1)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintSenses.append("L")
                constraintRhs.append(1)
                constraintCnt += 1
        #
        # for flow in trafficClass._flowObjList:
        #     for node in netTopoClass._swSet:
        #         swEgressLinkSet = node._egressLink
        #
        #         tmpCrowName = []
        #         tmpCrowCoff = []
        #         for link in swEgressLinkSet:
        #             if flow._assignPath == []:
        #                 tmpCrowName.append(link._RouteLpVars[flow])
        #                 tmpCrowCoff.append(1)
        #
        #
        #         constraintNames.append("C" + constraintCnt.__str__())
        #         constraintRows.append([tmpCrowName, tmpCrowCoff])
        #         constraintSenses.append("L")
        #         constraintRhs.append(1)
        #         constraintCnt += 1

        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)
        # print(problem.linear_constraints.get_names())

        return constraintCnt

    # 链路总带宽约束
    def genRouteBandwithConstraints(self, netTopoClass, problem, startCnt):
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt

        for link in netTopoClass._linkSet:
            flowSet = list(link._RouteLpVars.keys())
            if flowSet == []:
                continue
            tmpCrowName = []
            tmpCrowCoff = []
            tmpFlowLinkRate = 0.0
            for flow in flowSet:
                tmpCrowName.append(link._RouteLpVars.get(flow))
                tmpCrowCoff.append(flow._flowBandwith)  # 乘以1000是为了转化为MBps
                # tmpCrowName.append(flow._FlowValidLpVars[0])
                # tmpCrowCoff.append(flow._flowBandwith)  # 乘以1000是为了转化为MBps
                #
                # tmpFlowLinkRate = tmpFlowLinkRate + flow._flowBandwith
            # print("C",constraintCnt.__str__(),'tmpFlowLinkRate = ',tmpFlowLinkRate)
            constraintNames.append("C" + constraintCnt.__str__())
            constraintRows.append([tmpCrowName, tmpCrowCoff])
            constraintSenses.append("L")
            # constraintRhs.append(head.DEFAULT_LINK_MAX_BANDWIDTH + tmpFlowLinkRate)
            constraintRhs.append(head.DEFAULT_LINK_MAX_BANDWIDTH )
            constraintCnt += 1
        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)
        return constraintCnt

    # 将LP求解的结果还原为路径
    def routeLpRecur(self, link, srcNode, dstNode, onceLpRoute, flow, problem):
        # shendu = shendu + 1
        # print('shendu = ',shendu)
        if srcNode == dstNode:
            return
        srcNode = link._dstNode
        for link in srcNode._egressLink:
            if link._RouteLpVars.get(flow) and problem.solution.get_values(link._RouteLpVars[flow]) == 1.0:
                onceLpRoute.append(link)
                self.routeLpRecur(link, srcNode, dstNode, onceLpRoute, flow, problem)

    def fromLpToRoute(self, trafficClass, problem):
        idSet = set()  # 无重复元素的集合
        for flow in trafficClass._flowObjList:
            if flow._assignPath == []:
                idSet.add(flow._flowId)
        # 对每组冗余流执行：
        for fid in idSet:
            # 选出具有相同flow_id的冗余流
            flowRedunGroup = [flow for flow in trafficClass._flowObjList if flow._flowId == fid]
            srcNode = flowRedunGroup[0]._srcNode
            dstNode = flowRedunGroup[0]._dstNode
            rl = flowRedunGroup[0]._redundancy
            # 先判断出冗余路径个数是否合理，是否与RL相同
            egressCnt = 0
            for flow in flowRedunGroup:
                for link in srcNode._egressLink:
                    if problem.solution.get_values(link._RouteLpVars[flow]) == 1.0:
                        egressCnt = egressCnt + 1
            ingressCnt = 0
            for flow in flowRedunGroup:
                for link in dstNode._ingressLink:
                    if problem.solution.get_values(link._RouteLpVars[flow]) == 1.0:
                        ingressCnt = ingressCnt + 1
            if egressCnt != rl or ingressCnt != rl:
                # print("flow id = ", fid, "srcNode = ", srcNode.node_id, "dstNode = ", dstNode.node_id, "rl = ", rl,
                #       end=" ")
                # print("current route fail")
                continue
            # else:
            # print("flow id = ", fid, "srcNode = ", srcNode.node_id, "dstNode = ", dstNode.node_id, "rl = ", rl,
            #       end=" ")
            # print("current route success")
            # continue
            # 递归的生成几条路径
            ilpRoute = []
            for flow in flowRedunGroup:
                srcNode = flowRedunGroup[0]._srcNode
                dstNode = flowRedunGroup[0]._dstNode
                onceLpRoute = []
                for link in srcNode._egressLink:
                    if problem.solution.get_values(link._RouteLpVars[flow]) == 1.0:
                        onceLpRoute.append(link)
                        self.routeLpRecur(link, srcNode, dstNode, onceLpRoute, flow, problem)
                ilpRoute.append(onceLpRoute)
            # print(ilpRoute)
            # 8将调度结果加入流中
            for i in range(rl):
                flow._assignPath.clear()
                flow._assignPath = ilpRoute[i]

                # 打印
                # for link in flow._assignPath:
                #     print(link._linkName,end=',')
                # print()
        for flow in trafficClass._flowObjList:
            if flow._assignPath == []:
                continue
            # 9.将链路加入各条流中
            for link in flow._assignPath:
                link.addFlowObjToLink(flow)
                link._occupyBw += flow._flowBandwith
                link._occupyFlowCnt += 1
                if link._dstNode._nodeType == head.NodeType.Switch:
                    link._dstNode._flowCnt += 1

    ########################################################
    ##  路径序
    ########################################################
    # 我们用变量O来指定路径序，如果不做路径序的话，效果会差很多
    def genRouteOrderLpVars(self, netTopoClass, trafficClass, problem):
        coffList = []
        lbList = []
        ubList = []
        typesList = ""
        namesList = []
        routedFlowNum = trafficClass.assignedRouteNumStatistic(trafficClass._flowObjList)
        flowNum = len(trafficClass._flowObjList)
        # 决策变量t
        flowCnt = 0

        if routedFlowNum <= 0:
            for flow1 in trafficClass._flowObjList:
                flowCnt = flowCnt + 1
                if trafficClass._flowObjList.count(flow1) <= 0:
                    break
                for flow2 in trafficClass._flowObjList[flowCnt:flowNum]:
                    if flowCnt == flowNum or trafficClass._flowObjList.count(flow2) <= 0:
                        break

                    gcd = math.gcd(flow1._period, flow2._period)
                    tmpVariName = "O_" + int(flow1._flowId).__str__() + "_" + int(flow2._flowId).__str__()
                    coffList.append(0)
                    lbList.append(-5)
                    ubList.append(5)
                    typesList += "I"
                    namesList.append(tmpVariName)

                    flow1._RouteOrderLpVars[flow2] = tmpVariName
                    flow2._RouteOrderLpVars[flow1] = tmpVariName
        else:
            for flow1 in trafficClass._flowObjList:
                flowCnt = flowCnt + 1
                if trafficClass._flowObjList.count(flow1) <= 0:
                    break
                if flow1._isRouted == head.AssignStatus.Unassigned:
                    continue

                for flow2 in trafficClass._flowObjList[flowCnt:flowNum]:
                    if flowCnt == flowNum or trafficClass._flowObjList.count(flow2) <= 0:
                        break
                    if flow2._isRouted == head.AssignStatus.Unassigned:
                        continue

                    gcd = math.gcd(flow1._period, flow2._period)
                    tmpVariName = "O_" + int(flow1._flowId).__str__() + "_" + int(flow2._flowId).__str__()
                    coffList.append(0)
                    lbList.append(-5)
                    ubList.append(5)
                    typesList += "I"
                    namesList.append(tmpVariName)

                    flow1._RouteOrderLpVars[flow2] = tmpVariName
                    flow2._RouteOrderLpVars[flow1] = tmpVariName

        problem.variables.add(obj=coffList, lb=lbList, ub=ubList, types=typesList, names=namesList)
        # print(problem.variables.get_names())

    def genRouteOrderLpVarsOld(self, netTopoClass, trafficClass, problem):
        coffList = []
        lbList = []
        ubList = []
        typesList = ""
        namesList = []
        routedFlowNum = trafficClass.assignedRouteNumStatistic(trafficClass._flowObjList)
        flowNum = len(trafficClass._flowObjList)
        # 决策变量t
        flowCnt = 0

        if routedFlowNum <= 0:
            for flow1 in trafficClass._flowObjList:
                flowCnt = flowCnt + 1
                if trafficClass._flowObjList.count(flow1) <= 0:
                    break
                for flow2 in trafficClass._flowObjList[flowCnt:flowNum]:
                    if flowCnt == flowNum or trafficClass._flowObjList.count(flow2) <= 0:
                        break

                    gcd = math.gcd(flow1._period, flow2._period)
                    tmpVariName = "O_" + int(flow1._flowId).__str__() + "_" + int(flow2._flowId).__str__()
                    coffList.append(0)
                    lbList.append(0)
                    ubList.append(1)
                    typesList += "C"
                    namesList.append(tmpVariName)

                    flow1._RouteOrderLpVars[flow2] = tmpVariName
                    flow2._RouteOrderLpVars[flow1] = tmpVariName
        else:
            for flow1 in trafficClass._flowObjList:
                flowCnt = flowCnt + 1
                if trafficClass._flowObjList.count(flow1) <= 0:
                    break
                if flow1._isRouted == head.AssignStatus.Unassigned:
                    continue

                for flow2 in trafficClass._flowObjList[flowCnt:flowNum]:
                    if flowCnt == flowNum or trafficClass._flowObjList.count(flow2) <= 0:
                        break
                    if flow2._isRouted == head.AssignStatus.Unassigned:
                        continue

                    gcd = math.gcd(flow1._period, flow2._period)
                    tmpVariName = "O_" + int(flow1._flowId).__str__() + "_" + int(flow2._flowId).__str__()
                    coffList.append(0)
                    lbList.append(0)
                    ubList.append(1)
                    typesList += "C"
                    namesList.append(tmpVariName)

                    flow1._RouteOrderLpVars[flow2] = tmpVariName
                    flow2._RouteOrderLpVars[flow1] = tmpVariName

        problem.variables.add(obj=coffList, lb=lbList, ub=ubList, types=typesList, names=namesList)
        # print(problem.variables.get_names())

    ########################################################
    ##  是否选择这个流
    ########################################################
    def genFlowValidLpVars(self, netTopoClass, trafficClass, problem):
        coffList = []
        lbList = []
        ubList = []
        typesList = ""
        namesList = []
        flowNum = len(trafficClass._flowObjList)
        routedFlowNum = trafficClass.assignedRouteNumStatistic(trafficClass._flowObjList)
        # 决策变量t
        if routedFlowNum <= 0:
            for flow in trafficClass._flowObjList:
                if trafficClass._flowObjList.count(flow) <= 0:
                    break

                tmpVariName = "X_" + int(flow._flowId).__str__()
                coffList.append(0)
                lbList.append(0)
                ubList.append(1)
                typesList += "B"
                namesList.append(tmpVariName)

                flow._FlowValidLpVars.append(tmpVariName)
        else:
            for flow in trafficClass._flowObjList:
                if trafficClass._flowObjList.count(flow) <= 0:
                    break
                if flow._isRouted == head.AssignStatus.Unassigned:
                    continue
                tmpVariName = "X_" + int(flow._flowId).__str__()
                coffList.append(0)
                lbList.append(0)
                ubList.append(1)
                typesList += "B"
                namesList.append(tmpVariName)

                flow._FlowValidLpVars.append(tmpVariName)

        problem.variables.add(obj=coffList, lb=lbList, ub=ubList, types=typesList, names=namesList)
        # print(problem.variables.get_names())

    ########################################################
    ##  调度相关函数
    ########################################################
    # 该函数会根据当前流是否已经完成路由规划生成对应的tLp变量
    def genSchedLpVars(self, netTopoClass, trafficClass, problem):
        coffList = []
        lbList = []
        ubList = []
        typesList = ""
        namesList = []
        routedFlowNum = trafficClass.assignedRouteNumStatistic(trafficClass._flowObjList)
        # inf = trafficClass._hyperPeriod * 10
        inf = 0.0
        # 决策变量t
        for flow in trafficClass._flowObjList:

            if routedFlowNum <= 0 and flow._assignPath == []:
                # 表示当前流尚未规划路径
                srcNode = flow._srcNode
                dstNode = flow._dstNode

                for link in netTopoClass._linkSet:

                    if link._srcNode == srcNode or link._srcNode == dstNode \
                            or link._dstNode == srcNode or link._dstNode == dstNode \
                            or (
                            link._srcNode._nodeType == head.NodeType.Switch and link._dstNode._nodeType == head.NodeType.Switch):
                        tmpVariName = "t_" + link._linkName + "_flowid" + int(
                            flow._flowId).__str__() + "_subflowid" + int(
                            flow._subflowId).__str__()
                        coffList.append(0.0)
                        lbList.append(-10 * inf)
                        ubList.append(flow._period - flow._flowDur)
                        typesList += "I"
                        namesList.append(tmpVariName)

                        flow._SchedLpVars.append(tmpVariName)
                        link._SchedLpVars[flow] = tmpVariName
            elif routedFlowNum > 0 and flow._assignPath != []:
                for link in flow._assignPath:
                    tmpVariName = "t_" + link._linkName + "_flowid" + int(
                        flow._flowId).__str__() + "_subflowid" + int(
                        flow._subflowId).__str__()
                    coffList.append(0.0)
                    lbList.append(-10 * inf)
                    ubList.append(flow._period - flow._flowDur)
                    typesList += "I"
                    namesList.append(tmpVariName)

                    flow._SchedLpVars.append(tmpVariName)
                    link._SchedLpVars[flow] = tmpVariName

        problem.variables.add(obj=coffList, lb=lbList, ub=ubList, types=typesList, names=namesList)

        # print(problem.variables.get_names())

    # 流选中约束
    # 只有被选中的流，其起始时间才允许在0-hyperPeriod之间，否则不能大于零
    # 起始时刻约束：t_ILP≥0+inf(x_ILP -1)
    # 截止时刻约束:t_ILP + (ins-1) * period + maxHop*delay + flowDur≤hyperiod + inf(x_ILP -1) ===>放缩后 ===> t_ILP ≤ hyperiod + inf(x_ILP -1)
    # ===>t_ILP ≤ hyperiod + hyperiod(x_ILP -1) ===> t_ILP - hyperiod * x_ILP ≤0
    def genFlowValidConstraints(self, trafficClass, problem, startCnt):
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt
        inf = trafficClass._hyperPeriod * 10
        # 1.起始时刻约束
        for flow in trafficClass._flowObjList:
            if trafficClass._flowObjList.count(flow) <= 0:
                break

            srcNode = flow._srcNode
            srcEgressLinkset = srcNode._egressLink
            for link in srcEgressLinkset:

                tmpCrowName = []
                tmpCrowCoff = []

                if link._SchedLpVars.get(flow) == None:
                    continue
                src_t_ILP = link._SchedLpVars[flow]
                X_Ilp = flow._FlowValidLpVars[0]

                tmpCrowName.append(src_t_ILP)
                tmpCrowName.append(X_Ilp)
                tmpCrowCoff.append(1)
                tmpCrowCoff.append(-inf)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintSenses.append("G")
                constraintRhs.append(-inf)
                constraintCnt += 1

        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)

        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        # 2.截止时刻约束
        for flow in trafficClass._flowObjList:
            if trafficClass._flowObjList.count(flow) <= 0:
                break

            srcNode = flow._srcNode
            srcEgressLinkset = srcNode._egressLink
            hyperiod = trafficClass._hyperPeriod
            for link in srcEgressLinkset:

                tmpCrowName = []
                tmpCrowCoff = []

                if link._SchedLpVars.get(flow) == None:
                    continue
                src_t_ILP = link._SchedLpVars[flow]
                X_Ilp = flow._FlowValidLpVars[0]

                tmpCrowName.append(src_t_ILP)
                tmpCrowName.append(X_Ilp)
                tmpCrowCoff.append(-1)
                tmpCrowCoff.append(hyperiod)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintSenses.append("G")
                constraintRhs.append(0.0)
                constraintCnt += 1

        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)

        return constraintCnt

    # 端到端延时约束
    def genSchedE2ELatencyConstraints(self, trafficClass, problem, startCnt):

        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt
        inf = trafficClass._hyperPeriod * 10
        for flow in trafficClass._flowObjList:
            srcNode = flow._srcNode
            srcEgressLinkset = srcNode._egressLink
            dstNode = flow._dstNode
            dstIgressLinkset = dstNode._ingressLink
            flowTd = flow._flowDur
            for src_link in srcEgressLinkset:
                if src_link._SchedLpVars.get(flow) != None:
                    for dst_link in dstIgressLinkset:
                        if dst_link._SchedLpVars.get(flow) != None:
                            tmpCrowName = []
                            tmpCrowCoff = []

                            src_t_ILP = src_link._SchedLpVars.get(flow)
                            dst_t_ILP = dst_link._SchedLpVars.get(flow)
                            src_r_ILP = src_link._RouteLpVars.get(flow)
                            dst_r_ILP = dst_link._RouteLpVars.get(flow)

                            tmpCrowName.append(src_t_ILP)
                            tmpCrowName.append(dst_t_ILP)
                            tmpCrowCoff.append(1)
                            tmpCrowCoff.append(-1)
                            tmpCrowName.append(src_r_ILP)
                            tmpCrowName.append(dst_r_ILP)
                            tmpCrowCoff.append(-inf)
                            tmpCrowCoff.append(-inf)

                            constraintNames.append("C" + constraintCnt.__str__())
                            constraintRows.append([tmpCrowName, tmpCrowCoff])
                            constraintSenses.append("G")
                            constraintRhs.append(
                                - flow._deadline + flowTd - 2 * inf
                            )
                            # self.printConstraintsVars(constraintNames,constraintRows,constraintSenses,constraintRhs)
                            # tmpCrowName.append(src_t_ILP)
                            # tmpCrowName.append(dst_t_ILP)
                            # tmpCrowCoff.append(-1)
                            # tmpCrowCoff.append(1)
                            #
                            # constraintNames.append("C" + constraintCnt.__str__())
                            # constraintRows.append([tmpCrowName, tmpCrowCoff])
                            # constraintSenses.append("L")
                            # constraintRhs.append(
                            #     flow._deadline - flowTd
                            # )
                            constraintCnt += 1

        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)

        return constraintCnt

    # 链路无冲突约束v2:版本升级了，现在采用“性周期任务可排布满足性定理”进行处理
    # 参见论文《基于时间触发协议的VMS网络解耦合规划方法研究》与《时间敏感网络中基于ＩＬＰ的动态流量均衡调度算法》
    # ［ｖｉ，ｖｊ］∈Ｅ，ｆａ，ｆｂ ∈Ｆ，ａ≠ｂ：
    # ｒ＝ （ｔ［ｖｉ，ｖｊ］，ｆａ －ｔ［ｖｉ，ｖｊ］，ｆｂ）ｍｏｄ（ｇｃｄ（Ｔａ，Ｔｂ））；
    # ｔ＿ｔｒａｎｂ －Ｍ × （２－ｌｏ［ｖｉ，ｖｊ］，ｆａ －ｌｏ［ｖｉ，ｖｊ］，ｆｂ）≤ｒ≤
    # ｇｃｄ（Ｔａ，Ｔｂ）－ｔ＿ｔｒａｎａ ＋Ｍ × （２－ｌｏ［ｖｉ，ｖｊ］，ｆａ －
    # ｌｏ［ｖｉ，ｖｊ］，ｆｂ）
    def genSchedLinkConflicLessConstraints(self, netTopoClass, trafficClass, problem, startCnt):
        # 2.3无冲突约束：每条链路上任意两个流不冲突
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt
        inf = trafficClass._hyperPeriod * 10
        for link in netTopoClass._linkSet:
            flowSet = list(link._SchedLpVars.keys())

            # 遍历每条链路上的流
            flowLen = len(flowSet)
            # print(flowLen)
            if flowLen < 2:
                continue
            for i in range(flowLen):
                if i == flowLen - 1:
                    continue
                else:
                    for j in range(i + 1, flowLen):
                        flow1 = flowSet[i]
                        flow1_period = flowSet[i]._period
                        flow1_repeatcnt = int(trafficClass._hyperPeriod / flow1_period)
                        flow1_td = flowSet[i]._frameSize * head.TSN_CLK
                        flow1_t_ILP = link._SchedLpVars.get(flow1)
                        flow1_r_ILP = link._RouteLpVars.get(flow1)
                        X1 = flow1._FlowValidLpVars[0]

                        flow2 = flowSet[j]
                        flow2_period = flowSet[j]._period
                        flow2_repeatcnt = int(trafficClass._hyperPeriod / flow2_period)
                        flow2_td = flowSet[j]._frameSize * head.TSN_CLK
                        flow2_t_ILP = link._SchedLpVars.get(flow2)
                        flow2_r_ILP = link._RouteLpVars.get(flow2)
                        X2 = flow2._FlowValidLpVars[0]

                        O_f1f2 = flow1._RouteOrderLpVars[flow2]
                        gcd_T1_T2 = math.gcd(flow1_period, flow2_period)
                        # z = 'z_' + str(flow1._flowId) + str(flow2._flowId)
                        # problem.variables.add(obj=[0.0], lb=[-cplex.infinity], ub=[cplex.infinity], names=[z],
                        #                       types=["I"])  # 辅助变量z
                        z = O_f1f2
                        # 小于号约束
                        tmpCrowName = []
                        tmpCrowCoff = []
                        tmpCrowName.append(flow1_t_ILP)
                        tmpCrowCoff.append(1)
                        tmpCrowName.append(flow2_t_ILP)
                        tmpCrowCoff.append(-1)
                        tmpCrowName.append(z)
                        tmpCrowCoff.append(-gcd_T1_T2)

                        tmpCrowName.append(X1)
                        tmpCrowCoff.append(-inf)
                        tmpCrowName.append(X2)
                        tmpCrowCoff.append(-inf)

                        tmpCrowName.append(flow1_r_ILP)
                        tmpCrowCoff.append(-inf)
                        tmpCrowName.append(flow2_r_ILP)
                        tmpCrowCoff.append(-inf)

                        constraintSenses.append("G")
                        constraintRhs.append(flow2_td - 4 * inf)

                        constraintNames.append("C" + constraintCnt.__str__())
                        constraintRows.append([tmpCrowName, tmpCrowCoff])
                        constraintCnt += 1

                        # 大于号约束
                        tmpCrowName = []
                        tmpCrowCoff = []
                        tmpCrowName.append(flow1_t_ILP)
                        tmpCrowCoff.append(1)
                        tmpCrowName.append(flow2_t_ILP)
                        tmpCrowCoff.append(-1)
                        tmpCrowName.append(z)
                        tmpCrowCoff.append(-gcd_T1_T2)

                        tmpCrowName.append(X1)
                        tmpCrowCoff.append(inf)
                        tmpCrowName.append(X2)
                        tmpCrowCoff.append(inf)

                        tmpCrowName.append(flow1_r_ILP)
                        tmpCrowCoff.append(inf)
                        tmpCrowName.append(flow2_r_ILP)
                        tmpCrowCoff.append(inf)

                        constraintSenses.append("L")
                        constraintRhs.append(gcd_T1_T2 + 4 * inf - flow1_td)

                        constraintNames.append("C" + constraintCnt.__str__())
                        constraintRows.append([tmpCrowName, tmpCrowCoff])
                        constraintCnt += 1

        # self.printConstraintsVars(constraintRows,constraintSenses,constraintRhs,constraintNames)
        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)
        return constraintCnt

    def genSchedLinkConflicLessConstraintsOri(self, netTopoClass, trafficClass, problem, startCnt):
        # 2.3无冲突约束：每条链路上任意两个流不冲突
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt
        inf = trafficClass._hyperPeriod * 10
        for link in netTopoClass._linkSet:
            flowSet = list(link._SchedLpVars.keys())

            # 遍历每条链路上的流
            flowLen = len(flowSet)
            # print(flowLen)
            if flowLen < 2:
                continue
            for i in range(flowLen):
                if i == flowLen - 1:
                    continue
                else:
                    for j in range(i + 1, flowLen):
                        flow1 = flowSet[i]
                        flow1_period = flowSet[i]._period
                        flow1_repeatcnt = int(trafficClass._hyperPeriod / flow1_period)
                        flow1_td = flowSet[i]._frameSize * head.TSN_CLK
                        flow1_t_ILP = link._SchedLpVars.get(flow1)
                        flow1_r_ILP = link._RouteLpVars.get(flow1)
                        X1 = flow1._FlowValidLpVars[0]

                        flow2 = flowSet[j]
                        flow2_period = flowSet[j]._period
                        flow2_repeatcnt = int(trafficClass._hyperPeriod / flow2_period)
                        flow2_td = flowSet[j]._frameSize * head.TSN_CLK
                        flow2_t_ILP = link._SchedLpVars.get(flow2)
                        flow2_r_ILP = link._RouteLpVars.get(flow2)
                        X2 = flow2._FlowValidLpVars[0]

                        O_f1f2 = flow1._RouteOrderLpVars[flow2]
                        gcd_T1_T2 = math.gcd(flow1_period, flow2_period)
                        z = 'z_' + str(flow1._flowId) + str(flow2._flowId)
                        problem.variables.add(obj=[0], lb=[-trafficClass._hyperPeriod * 10], ub=[trafficClass._hyperPeriod * 10], names=[z],
                                              types=["I"])  # 辅助变量z

                        # print('z = ',z)
                        # mod约束，但是需要放缩

                        # ①放缩的第一部分 l1-l2≤M(1-4)
                        tmpCrowName = []
                        tmpCrowCoff = []
                        tmpCrowName.append(flow1_t_ILP)
                        tmpCrowCoff.append(1)
                        tmpCrowName.append(flow2_t_ILP)
                        tmpCrowCoff.append(-1)
                        tmpCrowName.append(z)
                        tmpCrowCoff.append(-gcd_T1_T2)
                        tmpCrowName.append(O_f1f2)
                        tmpCrowCoff.append(-1)
                        tmpCrowName.append(X1)
                        tmpCrowCoff.append(inf)
                        tmpCrowName.append(X2)
                        tmpCrowCoff.append(inf)

                        constraintSenses.append("L")
                        constraintRhs.append(2 * inf)

                        constraintNames.append("C" + constraintCnt.__str__())
                        constraintRows.append([tmpCrowName, tmpCrowCoff])
                        constraintCnt += 1
                        # ②放缩的第二部分 l1-l2≥-M(1-r)
                        tmpCrowName = []
                        tmpCrowCoff = []
                        tmpCrowName.append(flow1_t_ILP)
                        tmpCrowCoff.append(1)
                        tmpCrowName.append(flow2_t_ILP)
                        tmpCrowCoff.append(-1)
                        tmpCrowName.append(z)
                        tmpCrowCoff.append(-gcd_T1_T2)
                        tmpCrowName.append(O_f1f2)
                        tmpCrowCoff.append(-1)
                        tmpCrowName.append(X1)
                        tmpCrowCoff.append(-inf)
                        tmpCrowName.append(X2)
                        tmpCrowCoff.append(-inf)

                        constraintSenses.append("G")
                        constraintRhs.append(-2 * inf)

                        constraintNames.append("C" + constraintCnt.__str__())
                        constraintRows.append([tmpCrowName, tmpCrowCoff])
                        constraintCnt += 1

                        # 小于号约束
                        tmpCrowName = []
                        tmpCrowCoff = []
                        tmpCrowName.append(O_f1f2)
                        tmpCrowCoff.append(1)
                        tmpCrowName.append(flow1_r_ILP)
                        tmpCrowCoff.append(-inf)
                        tmpCrowName.append(flow2_r_ILP)
                        tmpCrowCoff.append(-inf)

                        constraintSenses.append("G")
                        constraintRhs.append(flow2_td - 2 * inf)

                        constraintNames.append("C" + constraintCnt.__str__())
                        constraintRows.append([tmpCrowName, tmpCrowCoff])
                        constraintCnt += 1

                        # 大于号约束
                        tmpCrowName = []
                        tmpCrowCoff = []
                        tmpCrowName.append(O_f1f2)
                        tmpCrowCoff.append(1)
                        tmpCrowName.append(flow1_r_ILP)
                        tmpCrowCoff.append(inf)
                        tmpCrowName.append(flow2_r_ILP)
                        tmpCrowCoff.append(inf)

                        constraintSenses.append("L")
                        constraintRhs.append(gcd_T1_T2 + 2 * inf - flow1_td)

                        constraintNames.append("C" + constraintCnt.__str__())
                        constraintRows.append([tmpCrowName, tmpCrowCoff])
                        constraintCnt += 1

        # self.printConstraintsVars(constraintRows,constraintSenses,constraintRhs,constraintNames)
        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)
        return constraintCnt

    # 链路无冲突约束
    # x: 0:f2 > f1, 1: f1 >= f2;
    # f2 - f1 - L1 >= O*(-2 * Inf) + (R1 + R2 - 2) * INF
    # f1 - f2 - L3 >= (1-O)*(-2 * Inf) + (R1 + R2 - 2) * INF

    def genSchedLinkConflicLessConstraintsOld(self, netTopoClass, trafficClass, problem, startCnt):
        # 2.3无冲突约束：每条链路上任意两个流不冲突
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt
        inf = trafficClass._hyperPeriod * 10
        for link in netTopoClass._linkSet:
            flowSet = list(link._SchedLpVars.keys())

            # 遍历每条链路上的流
            flowLen = len(flowSet)
            # print(flowLen)
            if flowLen < 2:
                continue
            for i in range(flowLen):
                if i == flowLen - 1:
                    continue
                else:
                    for j in range(i + 1, flowLen):
                        flow1 = flowSet[i]
                        flow1_period = flowSet[i]._period
                        flow1_repeatcnt = int(trafficClass._hyperPeriod / flow1_period)
                        flow1_td = flowSet[i]._frameSize * head.TSN_CLK
                        flow1_t_ILP = link._SchedLpVars.get(flow1)
                        flow1_r_ILP = link._RouteLpVars.get(flow1)

                        flow2 = flowSet[j]
                        flow2_period = flowSet[j]._period
                        flow2_repeatcnt = int(trafficClass._hyperPeriod / flow2_period)
                        flow2_td = flowSet[j]._frameSize * head.TSN_CLK
                        flow2_t_ILP = link._SchedLpVars.get(flow2)
                        flow2_r_ILP = link._RouteLpVars.get(flow2)

                        x = flow1._RouteOrderLpVars[flow2]

                        for m in range(flow1_repeatcnt):
                            for n in range(flow2_repeatcnt):

                                if m * flow1_period == n * flow2_period:

                                    # x = 0时，下面的约束生效
                                    tmpCrowName = []
                                    tmpCrowCoff = []
                                    tmpCrowName.append(flow2_t_ILP)
                                    tmpCrowCoff.append(1)
                                    tmpCrowName.append(flow1_t_ILP)
                                    tmpCrowCoff.append(-1)
                                    tmpCrowName.append(x)
                                    tmpCrowCoff.append(2 * inf)
                                    tmpCrowName.append(flow1_r_ILP)
                                    tmpCrowCoff.append(-inf)
                                    tmpCrowName.append(flow2_r_ILP)
                                    tmpCrowCoff.append(-inf)
                                    constraintSenses.append("G")
                                    constraintRhs.append(flow1_td
                                                         - 2 * inf)

                                    constraintNames.append("C" + constraintCnt.__str__())
                                    constraintRows.append([tmpCrowName, tmpCrowCoff])
                                    constraintCnt += 1

                                    # x = 1的时候下面的约束生效
                                    tmpCrowName = []
                                    tmpCrowCoff = []
                                    tmpCrowName.append(flow1_t_ILP)
                                    tmpCrowCoff.append(1)
                                    tmpCrowName.append(flow2_t_ILP)
                                    tmpCrowCoff.append(-1)
                                    tmpCrowName.append(x)
                                    tmpCrowCoff.append(-2 * inf)
                                    tmpCrowName.append(flow1_r_ILP)
                                    tmpCrowCoff.append(-inf)
                                    tmpCrowName.append(flow2_r_ILP)
                                    tmpCrowCoff.append(-inf)
                                    constraintSenses.append("G")
                                    constraintRhs.append(flow2_td
                                                         - 4 * inf)

                                    constraintNames.append("C" + constraintCnt.__str__())
                                    constraintRows.append([tmpCrowName, tmpCrowCoff])
                                    constraintCnt += 1

                                elif m * flow1_period < n * flow2_period:
                                    tmpCrowName = []
                                    tmpCrowCoff = []
                                    tmpCrowName.append(flow2_t_ILP)
                                    tmpCrowCoff.append(1)
                                    tmpCrowName.append(flow1_t_ILP)
                                    tmpCrowCoff.append(-1)
                                    tmpCrowName.append(flow1_r_ILP)
                                    tmpCrowCoff.append(-inf)
                                    tmpCrowName.append(flow2_r_ILP)
                                    tmpCrowCoff.append(-inf)
                                    constraintSenses.append("G")

                                    constraintRhs.append(flow1_td
                                                         + m * flow1_period
                                                         - n * flow2_period
                                                         - 2 * inf)

                                    constraintNames.append("C" + constraintCnt.__str__())
                                    constraintRows.append([tmpCrowName, tmpCrowCoff])
                                    constraintCnt += 1
                                else:
                                    tmpCrowName = []
                                    tmpCrowCoff = []
                                    tmpCrowName.append(flow1_t_ILP)
                                    tmpCrowName.append(flow2_t_ILP)
                                    tmpCrowCoff.append(1)
                                    tmpCrowCoff.append(-1)
                                    tmpCrowName.append(flow1_r_ILP)
                                    tmpCrowCoff.append(-inf)
                                    tmpCrowName.append(flow2_r_ILP)
                                    tmpCrowCoff.append(-inf)

                                    constraintSenses.append("G")
                                    constraintRhs.append(flow2_td
                                                         + n * flow2_period
                                                         - m * flow1_period
                                                         - 2 * inf)

                                    constraintNames.append("C" + constraintCnt.__str__())
                                    constraintRows.append([tmpCrowName, tmpCrowCoff])
                                    constraintCnt += 1

        # self.printConstraintsVars(constraintRows,constraintSenses,constraintRhs,constraintNames)
        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses, rhs=constraintRhs,
                                       names=constraintNames)
        return constraintCnt

    # 路径顺序约束
    # 更新了一个版本，现在对于==约束采用方所的方式进行约束
    # ①l1-l2≤M(1-r);②l1-l2≥-M(1-r);
    def genSchedE2ERouteOrderConstraints(self, netTopoClass, trafficClass, problem, startCnt):
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt
        inf = trafficClass._hyperPeriod * 10
        for flow in trafficClass._flowObjList:
            for node in netTopoClass._swSet:
                for linkIn in node._ingressLink:
                    if linkIn._SchedLpVars.get(flow) != None:
                        for linkEx in node._egressLink:
                            if linkEx._SchedLpVars.get(flow) != None:
                                # 第一部分约束
                                tmpCrowName = []
                                tmpCrowCoff = []
                                tmpCrowName.append(linkEx._SchedLpVars[flow])
                                tmpCrowCoff.append(-1.0)
                                tmpCrowName.append(linkIn._SchedLpVars[flow])
                                tmpCrowCoff.append(1.0)
                                tmpCrowName.append(linkEx._RouteLpVars[flow])
                                tmpCrowCoff.append(-inf)

                                constraintNames.append("C" + constraintCnt.__str__())
                                constraintRows.append([tmpCrowName, tmpCrowCoff])
                                constraintSenses.append("G")
                                constraintRhs.append(- inf)  # flow._frameSize * head.TSN_CLK
                                # print('constraintCnt = ',constraintCnt)
                                constraintCnt += 1

                                # 第二部分约束
                                tmpCrowName = []
                                tmpCrowCoff = []
                                tmpCrowName.append(linkEx._SchedLpVars[flow])
                                tmpCrowCoff.append(1.0)
                                tmpCrowName.append(linkIn._SchedLpVars[flow])
                                tmpCrowCoff.append(-1.0)
                                tmpCrowName.append(linkEx._RouteLpVars[flow])
                                tmpCrowCoff.append(-inf)

                                constraintNames.append("C" + constraintCnt.__str__())
                                constraintRows.append([tmpCrowName, tmpCrowCoff])
                                constraintSenses.append("G")
                                constraintRhs.append(- inf)  # flow._frameSize * head.TSN_CLK
                                # print('constraintCnt = ',constraintCnt)
                                constraintCnt += 1

        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses,
                                       rhs=constraintRhs,
                                       names=constraintNames)
        return constraintCnt

    # 路径顺序约束
    def genSchedE2ERouteOrderConstraintsOld(self, netTopoClass, trafficClass, problem, startCnt):
        constraintNames = []
        constraintRows = []
        constraintSenses = []
        constraintRhs = []
        constraintCnt = startCnt
        inf = trafficClass._hyperPeriod * 10
        for flow in trafficClass._flowObjList:
            for node in netTopoClass._swSet:
                for linkIn in node._ingressLink:
                    if linkIn._SchedLpVars.get(flow) != None:
                        for linkEx in node._egressLink:
                            if linkEx._SchedLpVars.get(flow) != None:
                                tmpCrowName = []
                                tmpCrowCoff = []

                                tmpCrowName.append(linkIn._SchedLpVars[flow])
                                tmpCrowCoff.append(-1.0)
                                tmpCrowName.append(linkEx._SchedLpVars[flow])
                                tmpCrowCoff.append(1.0)
                                tmpCrowName.append(linkEx._RouteLpVars[flow])
                                tmpCrowCoff.append(-inf)

                                constraintNames.append("C" + constraintCnt.__str__())
                                constraintRows.append([tmpCrowName, tmpCrowCoff])
                                constraintSenses.append("E")
                                constraintRhs.append(- inf)  # flow._frameSize * head.TSN_CLK
                                # print('constraintCnt = ',constraintCnt)
                                constraintCnt += 1

        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintSenses,
                                       rhs=constraintRhs,
                                       names=constraintNames)
        return constraintCnt

    # flowspan约束
    def flowspanConstraints(self, netTopoClass, trafficClass, problem, startCnt, minmax):
        constraint_names = []
        constraint_rows = []
        constraint_senses = []
        constraint_rhs = []
        constraint_cnt = startCnt
        for link in netTopoClass._linkSet:
            t_ILP_set = list(link._SchedLpVars.values())
            if t_ILP_set == []:
                continue

            for t_ILP in t_ILP_set:
                tmp_crow_name = []
                tmp_crow_coff = []

                tmp_crow_name.append(t_ILP)
                tmp_crow_name.append(minmax)
                tmp_crow_coff.append(1)
                tmp_crow_coff.append(-1)

                constraint_names.append("C" + constraint_cnt.__str__())
                constraint_rows.append([tmp_crow_name, tmp_crow_coff])
                constraint_senses.append("L")
                constraint_rhs.append(0)
                constraint_cnt += 1

        problem.linear_constraints.add(lin_expr=constraint_rows, senses=constraint_senses, rhs=constraint_rhs,
                                       names=constraint_names)
        return startCnt

    # 对于未选中的路，要求其对应的t_ILP=0
    def setNoChooseRouteToZeroConstraints(self, netTopoClass, trafficClass, problem, startCnt):
        constraintNames = []
        constraintRows = []
        constraintRenses = []
        constraintRhs = []
        constraintCnt = startCnt
        inf = trafficClass._hyperPeriod * 10
        for link in netTopoClass._linkSet:
            t_ILP_set = list(link._SchedLpVars.values())
            r_ILP_set = list(link._RouteLpVars.values())

            for i in range(len(t_ILP_set)):
                tmpCrowName = []
                tmpCrowCoff = []

                tmpCrowName.append(t_ILP_set[i])
                tmpCrowName.append(r_ILP_set[i])
                tmpCrowCoff.append(1)
                tmpCrowCoff.append(-inf)

                constraintNames.append("C" + constraintCnt.__str__())
                constraintRows.append([tmpCrowName, tmpCrowCoff])
                constraintRenses.append("L")
                constraintRhs.append(0)
                constraintCnt += 1
        problem.linear_constraints.add(lin_expr=constraintRows, senses=constraintRenses, rhs=constraintRhs,
                                       names=constraintNames)
        return constraintCnt

    # -------------------------------------------------
    # 函数名称：calcQbvForeachFlowDetail
    # 输入参数：trafficClass
    # 输出参数：无
    # 函数描述：根据调度结果，获取每个流在每条路径上的实际情况。
    # 该版本详细标注了路径名称和各条路径上的信息。
    # -------------------------------------------------
    def calcQbvForeachFlowDetail(self, trafficClass, problem):
        print('tsnLptool calcQbvForeachFlowDetail')
        ILPVariableNameList = problem.variables.get_names()
        ILPVariableValueList = problem.solution.get_values()
        for flow in trafficClass._flowObjList:
            flag = 0

            if flow._assignPath == [] or flow._assignPath[0]._SchedLpVars.get(flow) == None:
                # print('route error')
                continue
            index = ILPVariableNameList.index(flow._FlowValidLpVars[0])
            flowValid = ILPVariableValueList[index]

            if flowValid <= 0:
                continue
            # 标记
            trafficClass._assignFlowNum += 1
            flow._isAssigned = head.AssignStatus.Assigned

            link = flow._assignPath[0]

            index = ILPVariableNameList.index(link._SchedLpVars.get(flow))
            startoffset = ILPVariableValueList[index]
            flow_period = flow._period
            flow_insnum = int(trafficClass._hyperPeriod / flow_period)
            flow_dur = flow._flowDur

            for link in flow._assignPath:
                winList = []
                linkName = link._linkName
                winList.append([linkName])
                for i in range(flow_insnum):
                    tmpStartPit = startoffset + i * flow_period
                    tmpEndPit = startoffset + i * flow_period + flow_dur
                    winList.append([tmpStartPit, tmpEndPit])
                    if flag == 0:
                        flow._assignQbv.append([tmpStartPit, tmpEndPit])
                flow._assignQbvDetail.append(winList)
                flag = 1

    def calcQbvForeachFlow(self, trafficClass, problem):
        print('tsnLptool calcQbvForeachFlowDetail')
        ILPVariableNameList = problem.variables.get_names()
        ILPVariableValueList = problem.solution.get_values()
        for flow in trafficClass._flowObjList:
            flag = 0

            if flow._assignPath == [] or flow._assignPath[0]._SchedLpVars.get(flow) == None:
                # print('route error')
                continue
            index = ILPVariableNameList.index(flow._FlowValidLpVars[0])
            flowValid = ILPVariableValueList[index]

            if flowValid <= 0:
                continue
            # 标记
            trafficClass._assignFlowNum += 1
            flow._isAssigned = head.AssignStatus.Assigned

            link = flow._assignPath[0]

            index = ILPVariableNameList.index(link._SchedLpVars.get(flow))
            startoffset = ILPVariableValueList[index]
            flow_period = flow._period
            flow_insnum = int(trafficClass._hyperPeriod / flow_period)
            flow_dur = flow._flowDur

            for link in flow._assignPath:
                winList = []
                # linkName = link._linkName
                # winList.append([linkName])
                for i in range(flow_insnum):
                    tmpStartPit = startoffset + i * flow_period
                    tmpEndPit = startoffset + i * flow_period + flow_dur
                    winList.append([tmpStartPit, tmpEndPit])
                    if flag == 0:
                        flow._assignQbv.append([tmpStartPit, tmpEndPit])
                flow._assignQbvDetail.append(winList)
                flag = 1

    ########################################################
    ##  一些默认的优化目标
    ########################################################
    # 最大化可调度的流数量
    def genMaxSchedAbleConstraints(self, trafficClass, problem):
        var_names = []
        objective = []
        for flow in trafficClass._flowObjList:
            if len(flow._FlowValidLpVars) == 0:
                continue
            var_names.append(flow._FlowValidLpVars[0])
            objective.append(1.0)
            # 使用目标函数的系数
        problem.objective.set_linear(list(zip(var_names, objective)))
        problem.objective.set_sense(problem.objective.sense.maximize)

    # 最小化起始时间
    def genMinStartPitConstraints(self, netTopoClass, problem):
        var_names = []
        objective = []
        for link in netTopoClass._linkSet:
            t_ILP_set = list(link._SchedLpVars.values())
            if t_ILP_set == []:
                continue

            for t_ILP in t_ILP_set:
                var_names.append(t_ILP)
                objective.append(1.0)
            # 使用目标函数的系数
        problem.objective.set_linear(list(zip(var_names, objective)))
        problem.objective.set_sense(problem.objective.sense.minimize)

    # 最小化flowspan
    def genMinFlowspanConstraints(self, netTopoClass, problem, minmax):
        # 增加目标
        var_names = []
        objective = []
        var_names.append(minmax)
        objective.append(1)
        # 使用目标函数的系数
        problem.objective.set_linear(list(zip(var_names, objective)))
        problem.objective.set_sense(problem.objective.sense.minimize)

    # 最小化链路使用数量
    def genMinLinkUsageConstraints(self, netTopoClass, problem):
        var_names = []
        objective = []
        for link in netTopoClass._linkSet:
            r_ILP_set = list(link._RouteLpVars.values())
            if r_ILP_set == []:
                continue

            for r_ILP in r_ILP_set:
                var_names.append(r_ILP)
                objective.append(1.0)
        # 使用目标函数的系数
        problem.objective.set_linear(list(zip(var_names, objective)))
        problem.objective.set_sense(problem.objective.sense.minimize)

    def printConflictConstraints(self, problem):
        problem.conflict.refine(problem.conflict.all_constraints())
        output_fname = r"conflict.txt"
        problem.conflict.write(output_fname)
        with open(output_fname, "r") as f:
            print(f.read())

    def getSchedableFlowCnt(self, problem):
        validFrameCnt = 0
        nameList = problem.variables.get_names()
        resultList = problem.solution.get_values()
        for name in nameList:
            if name.find("X_") != -1:
                index = nameList.index(name)
                if resultList[index] == 1:
                    validFrameCnt = validFrameCnt + 1
        return validFrameCnt


def demoTestRouteLp():
    period_list = [500000]  # 所有和时间相关得参数，单位是ns
    flowNum = 4

    # x.创建打印工具
    debugTool = debugToolClass()
    # x.创建流量生成器
    tgTool = trafficGeneratorToolClass()
    # x.创建调度器
    problem = cplex.Cplex()
    problem.objective.set_sense(problem.objective.sense.minimize)
    tsnlptool = tsnLpTool()
    # x.创建绘画工具
    net_draw_tool = NetworkDrawTools(1, 1)

    # 验证重路由
    reRouteTopo = A380Net()

    net_draw_tool.network_topo_plot(reRouteTopo._topology)

    # x.生成netTopoClass
    netTopo = netTopoClass(reRouteTopo._topology, reRouteTopo._swNum, reRouteTopo._esNum)

    # x.生成flowObjList
    # flowObjList = tgTool.generateRandomFlows(netTopo, reRouteTopo._swNum, reRouteTopo._esNum, period_list, flowNum)
    flowObjList = tgTool.determGenerateRandomFlows(netTopo, 0, 1, period_list, flowNum)
    # x.分析流量
    tf = trafficClass(netTopo, flowObjList)
    # x.打印
    debugTool.printTrafficClass(tf)

    # 测试
    startCnt = 0
    tsnlptool.genRouteLpVars(netTopo, tf, problem)
    startCnt = tsnlptool.genRouteSrcNodeDstNodeConstraints(tf, problem, startCnt)
    startCnt = tsnlptool.genRouteSwitchConstraints(netTopo, tf, problem, startCnt)
    startCnt = tsnlptool.genRouteBandwithConstraints(netTopo, problem, startCnt)
    problem.write("tsnLpTool.lp")
    # Solve the problem
    problem.solve()
    tsnlptool.printSolution(problem)
    tsnlptool.fromLpToRoute(tf, problem)


def demoTestRouteAndSchedLp():
    period_list = [500000, 1000000]  # 所有和时间相关得参数，单位是ns
    flowNum = 4

    # x.创建打印工具
    debugTool = debugToolClass()
    # x.创建流量生成器
    tgTool = trafficGeneratorToolClass()
    # x.创建调度器
    problem = cplex.Cplex()
    tsnlptool = tsnLpTool()
    # x.创建绘画工具
    net_draw_tool = NetworkDrawTools(1, 1)

    # 验证重路由
    reRouteTopo = A380Net()

    net_draw_tool.network_topo_plot(reRouteTopo._topology)

    # x.生成netTopoClass
    netTopo = netTopoClass(reRouteTopo._topology, reRouteTopo._swNum, reRouteTopo._esNum)

    # x.生成flowObjList
    # flowObjList = tgTool.generateRandomFlows(netTopo, reRouteTopo._swNum, reRouteTopo._esNum, period_list, flowNum)
    flowObjList = tgTool.determGenerateRandomFlows(netTopo, 0, 1, period_list, flowNum)
    # x.分析流量
    tf = trafficClass(netTopo, flowObjList)
    # x.打印
    debugTool.printTrafficClass(tf)

    # 测试
    startCnt = 0
    tsnlptool.genRouteLpVars(netTopo, tf, problem)
    startCnt = tsnlptool.genRouteSrcNodeDstNodeConstraints(tf, problem, startCnt)
    startCnt = tsnlptool.genRouteSwitchConstraints(netTopo, tf, problem, startCnt)
    startCnt = tsnlptool.genRouteBandwithConstraints(netTopo, problem, startCnt)

    tsnlptool.genSchedLpVars(netTopo, tf, problem)
    tsnlptool.genRouteOrderLpVars(netTopo, tf, problem)
    startCnt = tsnlptool.genSchedE2ELatencyConstraints(tf, problem, startCnt)
    startCnt = tsnlptool.genSchedLinkConflicLessConstraints(netTopo, tf, problem, startCnt)
    #
    startCnt = tsnlptool.genSchedE2ERouteOrderConstraints(netTopo, tf, problem, startCnt)
    startCnt = tsnlptool.setNoChooseRouteToZeroConstraints(netTopo, tf, problem, startCnt)
    # 设置求解目标
    tsnlptool.genMinStartPitConstraints(netTopo, problem)

    # problem.write("tsnLpTool.lp")
    # 获取结果
    start_time = time.time()
    problem.solve()
    # tsnlptool.printSolution(problem)
    tsnlptool.fromLpToRoute(tf, problem)
    tsnlptool.calcQbvForeachFlowDetail(tf, problem)

    # 计算并打印执行时间
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
    debugTool.printFlowObjQbv(tf)


if __name__ == '__main__':
    print('ssss')
    # demoTestRouteLp()

    demoTestRouteAndSchedLp()

