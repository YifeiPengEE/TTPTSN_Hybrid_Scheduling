from head import *

#《Online Rerouting and Rescheduling of Time-Triggered Flows for Fault Tolerance in Time-Sensitive Networkin》
class OrrTsnSchedMethod():
    def __init__(self):
        print('OrrTsnSchedMethod')
        self.problem = Cplex()
        self.tsnlptool = tsnLpTool()
        self.problem.parameters.timelimit.set(head.CPLEX_MAX_TIME_LIMITATION)
        self.problem.parameters.mip.limits.solutions.set(head.CPLEX_MAX_SOLUTION_NUM)
        self.problem.parameters.mip.tolerances.mipgap.set(head.CPLEX_MAX_GAP)  # 设置MIP间隙
        self.problem.parameters.emphasis.numerical.set(1)  # 强调数值精度以避免数值问题
        self.startCnt = 0
        self.netOpTool = network_op_tools()
        self.dbgTool = debugToolClass()

    def route(self, netTopoClass, trafficClass):

        start_time = time.time()
        self.netOpTool.routeMethod(netTopoClass,trafficClass
                                   ,_hop_c=0.2,_bd_c=0.2,_fn_c=0.2,_dn_c=0.0,_DoCL_c=0.0,_DoC_c=0.0,M=3)

        # 计算并打印执行时间
        end_time = time.time()
        execution_time = end_time - start_time
        print('route execution_time = ',execution_time)

        # self.dbgTool.printFlowObjListRoute(trafficClass)

    def sched(self, netTopo, tf):
        #获取路由变量
        start_time = time.time()
        self.tsnlptool.genRouteLpVars(netTopo, tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genrouteILP execution_time = ',execution_time)
        # 获取路由序变量
        start_time = time.time()
        self.tsnlptool.genRouteOrderLpVars(netTopo, tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genXILP execution_time = ',execution_time)
        # 获取帧有效约束
        start_time = time.time()
        self.tsnlptool.genFlowValidLpVars(netTopo, tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genFlowValidLpVars execution_time = ', execution_time)
        #获取调度变量
        start_time = time.time()
        self.tsnlptool.genSchedLpVars(netTopo, tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genStartTimeILP execution_time = ',execution_time)


        start_time = time.time()
        self.startCnt = self.tsnlptool.genFlowValidConstraints(tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('gen genFlowValidConstraints execution_time = ',execution_time)


        start_time = time.time()
        self.startCnt = self.tsnlptool.genSchedE2ELatencyConstraints(tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('gen genSchedE2ELatencyConstraints execution_time = ',execution_time)

        start_time = time.time()
        self.startCnt = self.tsnlptool.genSchedLinkConflicLessConstraints(netTopo, tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('gen genSchedLinkConflicLessConstraints execution_time = ',execution_time)
        # #
        start_time = time.time()
        self.startCnt = self.tsnlptool.genSchedE2ERouteOrderConstraints(netTopo, tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('gen genSchedE2ERouteOrderConstraints execution_time = ',execution_time)

        start_time = time.time()
        self.startCnt = self.tsnlptool.setNoChooseRouteToZeroConstraints(netTopo, tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('gen setNoChooseRouteToZeroConstraints execution_time = ',execution_time)

        # 设置求解目标
        # self.tsnlptool.genMinStartPitConstraints(netTopo, self.problem)

    def solve(self, netTopo, tf):
        # self.problem.write("OrrTsnSchedTool.lp")

        try:
            start_time = time.time()
            self.problem.solve()
            end_time = time.time()
            execution_time = end_time - start_time
            print('problem.solve execution_time = ', execution_time)
            # self.tsnlptool.printSolution(self.problem)
            self.problem.solution.get_objective_value()

            start_time = time.time()
            self.tsnlptool.calcQbvForeachFlowDetail(tf, self.problem)
            end_time = time.time()
            execution_time = end_time - start_time
            print('gen Qbv execution_time = ', execution_time)

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
        # self.problem.write("OrrTsnSchedTool.lp")
        try:
            self.problem.solve()
            self.problem.solution.get_objective_value()
            # self.tsnlptool.printSolution(self.problem)
            # print('current solve status = ',self.problem.get_stats())
            return 0

        except exceptions.CplexSolverError as e:
            print("CPLEX solver error:", e)
            print("No feasible solution found.")
            return -1