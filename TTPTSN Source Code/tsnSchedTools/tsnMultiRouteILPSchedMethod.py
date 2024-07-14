import copy
from head import *
#本代码是基于tsnRecurSchedMethod算法的基础上，研发的基于ILP的调度算法
#实验发现tsnRecurSchedMethod算法提供的路由策略很牛逼，但是调度策略非常不尽人意
#所以本算法采用tsnRecurSchedMethod算法中的路由策略，但是调度采用ILP进行

class tsnMultiRouteILPSchedMethod():
    def __init__(self):
        print('tsnMultiRouteILPSchedMethod')
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
        self.netOpTool.routeMethod(netTopoClass,trafficClass, _hop_c=0.2, _bd_c=0.2, _fn_c=0.2, _dn_c=0.2, _DoCL_c=0.2, _DoC_c=0.2
                    , M=10)
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
        self.startCnt = self.tsnlptool.genSchedE2ELatencyConstraints(tf, self.problem, self.startCnt)
        self.startCnt = self.tsnlptool.genSchedLinkConflicLessConstraints(netTopo, tf, self.problem, self.startCnt)
        # #
        self.startCnt = self.tsnlptool.genSchedE2ERouteOrderConstraints(netTopo, tf, self.problem, self.startCnt)
        # self.startCnt = self.tsnlptool.setNoChooseRouteToZeroConstraints(netTopo, tf, self.problem, self.startCnt)



    def solve(self, netTopo, tf):
        # self.problem.write("OrrTsnSchedTool.lp")
        # 设置求解目标
        self.tsnlptool.genMinStartPitConstraints(netTopo, self.problem)
        try:
            self.problem.solve()
            # self.tsnlptool.printSolution(self.problem)
            self.tsnlptool.fromLpToRoute(tf, self.problem)
            self.tsnlptool.calcQbvForeachFlowDetail(tf, self.problem)

        except exceptions.CplexSolverError as e:
            print("CPLEX solver error:", e)
            print("No feasible solution found.")

    def useForIncreaseSolve(self, netTopo, tf):
        try:
            self.problem.solve()
            return 0

        except exceptions.CplexSolverError as e:
            print("CPLEX solver error:", e)
            print("No feasible solution found.")
            return -1

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
