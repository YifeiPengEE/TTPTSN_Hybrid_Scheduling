from head import *
import time

#《Enhancing Schedulability and Throughput of Time-Triggered Traffic in IEEE 802.1Qbv Time-Sensitive Networks》
class enhanceSchedAndThroughputSchedMethod():
    def __init__(self):
        print('enhanceSchedAndThroughputSchedMethod')
        self.problem = Cplex()
        self.tsnlptool = tsnLpTool()
        self.dbgTool = debugToolClass()
        self.startCnt = 0
        self.netOpTool = network_op_tools()
        self.problem.parameters.timelimit.set(head.CPLEX_MAX_TIME_LIMITATION)
        self.problem.parameters.mip.limits.solutions.set(head.CPLEX_MAX_SOLUTION_NUM)
        self.problem.parameters.mip.tolerances.mipgap.set(head.CPLEX_MAX_GAP)  # 设置MIP间隙
        self.problem.parameters.emphasis.numerical.set(1)  # 强调数值精度以避免数值问题
    def route(self, netTopoClass, trafficClass):
        for flow in trafficClass._flowObjList:
            pathLinkSet = self.netOpTool.bfsSpPath(netTopoClass,flow)

            routeValid = 1
            for link in pathLinkSet:
                if link._occupyBw + flow._flowBandwith > head.DEFAULT_LINK_MAX_BANDWIDTH:
                    routeValid = 0
                    break

            if routeValid :
                flow._isRouted = head.AssignStatus.Assigned
                flow._assignPath = pathLinkSet
                # 5.将链路加入各条流中
                for link in pathLinkSet:
                    link.addFlowObjToLink(flow)
                    link._occupyBw += flow._flowBandwith
                    link._occupyFlowCnt += 1
                    if link._dstNode._nodeType == head.NodeType.Switch:
                        link._dstNode._flowCnt += 1

        # self.dbgTool.printFlowObjListRoute(trafficClass)


    def sched(self, netTopo, tf):
        #获取路由变量
        self.tsnlptool.genRouteLpVars(netTopo, tf, self.problem)
        # 获取路由序变量
        self.tsnlptool.genRouteOrderLpVars(netTopo, tf, self.problem)
        # 获取帧有效约束
        self.tsnlptool.genFlowValidLpVars(netTopo, tf, self.problem)
        #获取调度变量
        self.tsnlptool.genSchedLpVars(netTopo, tf, self.problem)

        self.startCnt = self.tsnlptool.genFlowValidConstraints(tf, self.problem, self.startCnt)
        self.startCnt = self.tsnlptool.genSchedE2ELatencyConstraints(tf, self.problem, self.startCnt)
        self.startCnt = self.tsnlptool.genSchedLinkConflicLessConstraints(netTopo, tf, self.problem, self.startCnt)
        # # #
        self.startCnt = self.tsnlptool.genSchedE2ERouteOrderConstraints(netTopo, tf, self.problem, self.startCnt)
        # self.startCnt = self.tsnlptool.setNoChooseRouteToZeroConstraints(netTopo, tf, self.problem, self.startCnt)


    def schedOld(self, netTopo, tf):
        #获取路由变量
        self.tsnlptool.genRouteLpVars(netTopo, tf, self.problem)
        # 获取路由序变量
        self.tsnlptool.genRouteOrderLpVarsOld(netTopo, tf, self.problem)
        # 获取帧有效约束
        self.tsnlptool.genFlowValidLpVars(netTopo, tf, self.problem)
        #获取调度变量
        self.tsnlptool.genSchedLpVars(netTopo, tf, self.problem)

        self.startCnt = self.tsnlptool.genFlowValidConstraints(tf, self.problem, self.startCnt)
        self.startCnt = self.tsnlptool.genSchedE2ELatencyConstraints(tf, self.problem, self.startCnt)

        self.startCnt = self.tsnlptool.genSchedLinkConflicLessConstraintsOld(netTopo, tf, self.problem, self.startCnt)

        # #
        self.startCnt = self.tsnlptool.genSchedE2ERouteOrderConstraintsOld(netTopo, tf, self.problem, self.startCnt)
        # self.startCnt = self.tsnlptool.setNoChooseRouteToZeroConstraints(netTopo, tf, self.problem, self.startCnt)


    def solve(self, netTopo, tf):
        # self.problem.write("NwPsptsnLpTool.lp")
        # 设置求解目标
        self.tsnlptool.genMinStartPitConstraints(netTopo, self.problem)
        try:
            self.problem.solve()
            # self.tsnlptool.printSolution(self.problem)
            self.problem.solution.get_objective_value()
            self.tsnlptool.calcQbvForeachFlowDetail(tf, self.problem)

        except exceptions.CplexSolverError as e:
            print("CPLEX solver error:", e)
            print("No feasible solution found.")


    def solveMaxSchedable(self, netTopo, tf):
        start_time = time.time()
        self.tsnlptool.genMaxSchedAbleConstraints(tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genMaxSchedAbleConstraints execution_time = ', execution_time)
        # self.problem.write("tsnLpTool22.lp")
        # self.tsnlptool.printConflictConstraints(self.problem)
        try:
            start_time = time.time()
            self.problem.solve()
            end_time = time.time()
            execution_time = end_time - start_time
            print('solve execution_time = ', execution_time)
            # self.tsnlptool.printSolution(self.problem)

            self.problem.solution.get_objective_value()


            start_time = time.time()
            self.tsnlptool.calcQbvForeachFlowDetail(tf, self.problem)
            # self.dbgTool.printFlowObjQbv(tf)
            end_time = time.time()
            execution_time = end_time - start_time
            print('fromLpToRoute execution_time = ', execution_time)
            mip_gap = self.problem.solution.MIP.get_mip_relative_gap()

            return self.tsnlptool.getSchedableFlowCnt(self.problem),mip_gap

        except exceptions.CplexSolverError as e:

            print("CPLEX solver error:", e)
            print("No feasible solution found.")
            return -1





    def useForIncreaseSolve(self, netTopo, tf):
        # self.problem.write("NwPsptsnLpTool.lp")
        try:
            self.problem.solve()
            self.problem.solution.get_objective_value()
            # self.tsnlptool.printSolution(self.problem)
            return 0

        except exceptions.CplexSolverError as e:
            print("CPLEX solver error:", e)
            print("No feasible solution found.")



            return -1