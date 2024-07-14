
from head import *
import time
#本文复现论文《ILP-based multiperiod flow routing and scheduling method in time-sensitive network》

class ilpbasedMultiFlowSchedMethod():
    def __init__(self):
        print('ilpbasedMultiFlowSchedMethod')
        self.init()
        self.dbgTool = debugToolClass()

    def init(self):
        self.problem = Cplex()
        # self.problem.set_problem_type(Cplex.problem_type.MILP)
        # 设置求解时间限制为 10 秒
        self.problem.parameters.timelimit.set(head.CPLEX_MAX_TIME_LIMITATION)
        self.problem.parameters.mip.limits.solutions.set(head.CPLEX_MAX_SOLUTION_NUM)
        self.problem.parameters.mip.tolerances.mipgap.set(head.CPLEX_MAX_GAP)  # 设置MIP间隙
        self.problem.parameters.emphasis.numerical.set(1)  # 强调数值精度以避免数值问题
        # 设置参数，指定找到一个可行解后就停止搜索
        # self.problem.parameters.mip.limits.solutions = 1
        # self.problem.parameters.lpmethod.set(self.problem.parameters.lpmethod.values.auto)  # 自动选择求解算法
        # 设置工作内存大小为 4096MB
        # self.problem.parameters.workmem = 4096
        # self.problem.parameters.parallel.set(1)  # 启用并行计算

        self.minmax = "minmax"
        self.tsnlptool = tsnLpTool()
        self.startCnt = 0

    def route(self, netTopo, tf):

        start_time = time.time()
        self.tsnlptool.genRouteLpVars(netTopo, tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genRouteLpVars execution_time = ', execution_time)


        # 获取帧有效约束
        start_time = time.time()
        self.tsnlptool.genFlowValidLpVars(netTopo, tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genFlowValidLpVars execution_time = ', execution_time)


        start_time = time.time()
        self.startCnt = self.tsnlptool.genRouteSrcNodeDstNodeConstraints(tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genRouteSrcNodeDstNodeConstraints execution_time = ', execution_time)

        start_time = time.time()
        self.startCnt = self.tsnlptool.genRouteSwitchConstraints(netTopo, tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genRouteSwitchConstraints execution_time = ', execution_time)

        start_time = time.time()
        self.startCnt = self.tsnlptool.genRouteBandwithConstraints(netTopo, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genRouteBandwithConstraints execution_time = ', execution_time)

    def sched(self, netTopo, tf):
        # 获取路由序变量
        start_time = time.time()
        self.tsnlptool.genRouteOrderLpVars(netTopo, tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genRouteOrderLpVars execution_time = ', execution_time)


        #获取调度变量
        start_time = time.time()
        self.tsnlptool.genSchedLpVars(netTopo, tf, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genSchedLpVars execution_time = ', execution_time)




        start_time = time.time()
        self.startCnt = self.tsnlptool.genFlowValidConstraints(tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genFlowValidConstraints execution_time = ', execution_time)


        start_time = time.time()
        self.startCnt = self.tsnlptool.genSchedE2ELatencyConstraints(tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genSchedE2ELatencyConstraints execution_time = ', execution_time)

        start_time = time.time()
        self.startCnt = self.tsnlptool.genSchedLinkConflicLessConstraints(netTopo, tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genSchedLinkConflicLessConstraints execution_time = ', execution_time)
        #
        start_time = time.time()
        self.startCnt = self.tsnlptool.genSchedE2ERouteOrderConstraints(netTopo, tf, self.problem, self.startCnt)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genSchedE2ERouteOrderConstraints execution_time = ', execution_time)

        # start_time = time.time()
        # self.startCnt = self.tsnlptool.setNoChooseRouteToZeroConstraints(netTopo, tf, self.problem, self.startCnt)
        # end_time = time.time()
        # execution_time = end_time - start_time
        # print('setNoChooseRouteToZeroConstraints execution_time = ', execution_time)



        # #flow plan
        # self.problem.variables.add(obj=[1], lb=[0.0], ub=[tf._hyperPeriod], types="C", names=["minmax"])
        # self.startCnt = self.tsnlptool.flowspanConstraints(netTopo, tf, self.problem, self.startCnt,self.minmax)
        # self.tsnlptool.genMinFlowspanConstraints(netTopo, self.problem,self.minmax)
    def solve(self, netTopo, tf):
        start_time = time.time()
        self.tsnlptool.genMinStartPitConstraints(netTopo, self.problem)
        end_time = time.time()
        execution_time = end_time - start_time
        print('genMinStartPitConstraints execution_time = ', execution_time)
        # self.problem.write("tsnLpTool2.lp")

        try:
            start_time = time.time()
            self.problem.solve()
            end_time = time.time()
            execution_time = end_time - start_time
            print('solve execution_time = ', execution_time)
            self.tsnlptool.printSolution(self.problem)
            self.problem.solution.get_objective_value()

            start_time = time.time()
            self.tsnlptool.fromLpToRoute(tf, self.problem)
            end_time = time.time()
            execution_time = end_time - start_time
            print('fromLpToRoute execution_time = ', execution_time)

            start_time = time.time()
            self.tsnlptool.calcQbvForeachFlowDetail(tf, self.problem)
            end_time = time.time()
            execution_time = end_time - start_time
            print('fromLpToRoute execution_time = ', execution_time)
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
            self.tsnlptool.fromLpToRoute(tf, self.problem)
            end_time = time.time()
            execution_time = end_time - start_time
            print('fromLpToRoute execution_time = ', execution_time)

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
        try:
            self.problem.solve()
            self.problem.solution.get_objective_value()
            return 0

        except exceptions.CplexSolverError as e:
            print("CPLEX solver error:", e)
            print("No feasible solution found.")
            return -1

    def routeSolve(self, netTopo, tf):
        # 设置求解目标
        self.tsnlptool.genMaxSchedAbleConstraints(tf, self.problem)
        # self.problem.write("tsnLpRouteTool.lp")
        self.problem.solve()
        # self.tsnlptool.printSolution(self.problem)
        self.tsnlptool.fromLpToRoute(tf, self.problem)



