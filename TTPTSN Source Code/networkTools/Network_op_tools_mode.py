import sys
import heapq
import copy
from head import *
from queue import PriorityQueue
from pulp import *
import random
from collections import deque
class network_op_tools:
    # 类说明：该类提供网络操作工具，包括最短路径求解算法，Steiner Tree算法，流量规划算法等
    # 类版本：v0.1
    # 类版本说明：当前版本仅提供最简单的算法
    def __init__(self):
        print('network_op_tools 构造函数')
        self.dbgTool = debugToolClass()
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

    def bfs_shortest_path(self,adj_matrix, start, end):
        # 创建一个队列用于BFS
        queue = deque()
        # 创建一个集合用于记录已访问的节点
        visited = set()
        # 创建一个字典用于存储节点间的父子关系，以便路径重构
        parent = {}
        # 将起始节点入队
        queue.append(start)
        # 标记起始节点为已访问
        visited.add(start)
        # BFS遍历
        while queue:
            current_node = queue.popleft()
            # 如果当前节点是目标节点，重构并返回路径
            if current_node == end:
                path = []
                while current_node is not None:
                    path.append(current_node)
                    current_node = parent.get(current_node)
                return path[::-1]
            # 探索当前节点的邻居节点
            for neighbor, connected in enumerate(adj_matrix[current_node]):
                if connected == 1 and neighbor not in visited:
                    # 将邻居节点入队
                    queue.append(neighbor)
                    # 标记邻居节点为已访问
                    visited.add(neighbor)
                    # 存储节点间的父子关系以便路径重构
                    parent[neighbor] = current_node
        # 如果没有找到路径
        return None

    #利用bfs求解最短路径
    def bfsSpPath(self, netTopoClass, flowObj):
        path_link_set = []
        srcDevId = flowObj._srcNode._deviceId
        dstDevId = flowObj._dstNode._deviceId

        pathDeviceIdSet = self.bfs_shortest_path(netTopoClass._adjMatrix,srcDevId,dstDevId)

        if pathDeviceIdSet != []:
            for i in range(pathDeviceIdSet.__len__() - 1):
                path_link_set.append(netTopoClass._directAdjMatrix
                                     [pathDeviceIdSet[i]][pathDeviceIdSet[i + 1]]
                                     )

        return path_link_set
    # 该最短路径算法返回的是link对象
    def spFlowobjLinkobj(self, netTopoClass, flowObj):
        srcNodeName = flowObj._srcNode._nodeName
        dstNodeName = flowObj._dstNode._nodeName

        pathLinkSet = self.shortest_path_linkobj(netTopoClass, srcNodeName, dstNodeName)


        return pathLinkSet
    def shortest_path_linkobj(self, netTopoClass, srcNodeName, desNodeName):
        path_link_set = []
        # 函数输入：输入网络拓扑、源节点与目的节点
        # 函数输出：按照源->目的排序的link_set
        # print('research shortest path...')

        # 1.进行节点名称与节点ID的转化
        for item in netTopoClass._nodeSet:
            # print(item._nodeName)
            if srcNodeName == item._nodeName:
                srcNode = item

        # 2.获取最短路径树
        tree = self.shortest_path_tree(netTopoClass, srcNode)
        # 3.获取最短路径，以节点形式呈现
        for item in tree:
            if item[-1]._nodeName == desNodeName:
                path_node_mode = item

        # 4.获取最短路径，以链路集合的形式呈现
        for i in range(path_node_mode.__len__() - 1):
            path_link_set.append(netTopoClass._directAdjMatrix
                                 [path_node_mode[i]._deviceId][path_node_mode[i + 1]._deviceId]
                                 )

        # for item in path_link_set:
        #     print("("+str(item.srcNode._deviceId)+","+str(item.dst_node._deviceId)+")"+  '->', end='')
        #     # print(item.link_name+'->', end='')
        # print("")

        return path_link_set

    def shortest_path_tree(self, netTopoClass, srcNode):
        # print('research shortest path tree...')
        """
        根据Topo中的adjacency_matrix编写最短路径树算法，源节点为src，代价是Link中的cost
        :param src: 源节点
        :return: 以二维列表形式返回最短路径树，每个子列表表示从源节点到该节点的路径
        该算法实现思路是，
            ①使用Dijkstra 算法获取邻接表，邻接表存储了最短路径下，各个节点的父节点；
            ②从各个终端节点反推出一条到达源节点的路径；
            ③最终输出tree为一个二维list，其中一维为src节点到各个节点的路径list
        """
        # 初始化

        dist = [float('inf')] * netTopoClass._nodeSet.__len__()
        visited = [False] * netTopoClass._nodeSet.__len__()
        prev = [-1] * netTopoClass._nodeSet.__len__()
        dist[srcNode._deviceId] = 0
        # Dijkstra算法
        for i in range(netTopoClass._nodeSet.__len__()):
            # 找到未访问节点中距离最小的节点
            min_dist = float('inf')
            u = -1
            for j in range(netTopoClass._nodeSet.__len__()):
                if not visited[j] and dist[j] < min_dist:
                    min_dist = dist[j]
                    u = j
            if u == -1:
                break
            visited[u] = True
            # 更新与u相邻节点的距离

            for v in range(netTopoClass._nodeSet.__len__()):
                if not visited[v] and netTopoClass._directAdjMatrix[u][v] is not None:
                    alt = dist[u] + netTopoClass._directAdjMatrix[u][v].cost
                    if alt < dist[v]:
                        dist[v] = alt
                        prev[v] = u
        # 构造最短路径树
        tree = [[] for i in range(netTopoClass._nodeSet.__len__())]
        for i in range(netTopoClass._nodeSet.__len__()):
            if i == srcNode._deviceId:
                continue
            path = []
            j = i
            while j != -1:
                path.insert(0, netTopoClass._nodeSet[j])
                j = prev[j]
            tree[i] = path
        # 剔除掉空的行，即从自身到自身的路径
        for path in tree:
            if path.__len__() == 0:
                tree.remove(path)
        # 将结果记录下来
        # self.shortest_tree[srcNode] = tree
        # 返回该最短路径树
        return tree

    def add_flow_to_eachtopolink(self,trafficClass):

        for flow in trafficClass._flowObjList:
            # print('flow._assignPath = ',flow._assignPath)
            for path in flow._assignPath:
                # print('link_name=' + path._linkName)
                path.addFlowObjToLink(flow)

                #初始化未规划时隙窗口
                if len(path._idleWindowList) == 0:
                    path._idleWindowList.append([0.0,float(trafficClass._hyperPeriod)])


    def del_flow_to_eachtopolink(self,traffic_analysis):
        # print("add_flow_to_eachtopolink")
        for flow in traffic_analysis._test_traffic:
            # print("flow_id=" + str(flow.flow_id))
            for path in flow._assign_path:
                # print('link_name=' + path.link_name)
                path.flow_set.clear()

    def get_route_foreach_flow(self, netTopoClass, trafficClass):
        #要根据网络拓扑和带规划流量，给出每条流了的路径,求解出来的流对应的route保存在流中
        for flow in trafficClass._flowObjList:
            flow._assignPath.clear()
        self.unlimited_ksp_route_method(netTopoClass, trafficClass._flowObjList,1)
        # for flow in traffic_analysis._test_traffic:
        #     flow._assign_path.clear()
        #     flow._assign_path = self.shortest_path_linkobj(net_topo,flow.source_node.node_name,flow.dest_node.node_name)

    #该最短路径返回的是节点对
    #ex:
    #   ( 9 , 0 )( 0 , 3 )( 3 , 5 )( 5 , 7 )( 7 , 15 )
    def shortest_path_nodepair(self,adj_matrix, src, dst):

        n = len(adj_matrix)
        dist = [sys.maxsize] * n  # 用sys.maxsize代替无穷大整数
        prev = [None] * n
        dist[src] = 0
        queue = [(0, src)]

        while queue:
            path_len, v = heapq.heappop(queue)
            if path_len == dist[v]:
                for w, edge_len in enumerate(adj_matrix[v]):
                    if edge_len != 0 and path_len + edge_len < dist[w]:
                        dist[w] = path_len + edge_len
                        heapq.heappush(queue, (dist[w], w))
                        prev[w] = v


        path, v = [], dst
        while v is not None:
            # path.append(v)              # 以单节点的形式返回
            path.append((prev[v], v))  # 以节点对的形式返回
            v = prev[v]
        path.reverse()

        return dist[dst], path[1:]  # 剔除掉第一个(None, x)

    # 删除子图的不相交路由算法
    def delsubG_disjoint_route_method(self,net_topo, flow_list):

        # 收集所有flow_id
        id_set = set()     # 无重复元素的集合
        for flow in flow_list:
            id_set.add(flow.flow_id)

        # 对每组冗余流执行：
        for fid in id_set:
            # 选出具有相同flow_id的冗余流
            flow_group = [flow for flow in flow_list if flow.flow_id == fid]
            djt_routes_map = []  # [(cost, path)]
            # 深拷贝一份邻接链表
            adj_matrix_dup = copy.deepcopy(net_topo.adjacency_matrix_)
            # 为这组冗余流寻找不相交最短路径
            for flow in flow_group:

                cost, path = self.shortest_path_nodepair(adj_matrix_dup, flow.source_node.node_id, flow.dest_node.node_id)
                if len(path) > 0:   # 成功找到一条
                    djt_routes_map.append(path)
                    flow.route = path
                    # 移除该最短路
                    for node_pair in path:
                        adj_matrix_dup[node_pair[0]][node_pair[1]] = 0
                        adj_matrix_dup[node_pair[1]][node_pair[0]] = 0
                    # print_adj_matrix(adj_matrix_dup)
                else:
                    # print("break")
                    break

            if len(djt_routes_map) != flow_group[0].redundancy :
                # print("not found!!")
                djt_routes_map.clear()
            else:
                for flow in flow_group:
                    flow.is_assigned = head.AssignStatus.Assigned
                    tmp_route = djt_routes_map.pop()
                    route_link_set = []
                    for t_path in tmp_route:
                        route_link_set.append(net_topo.direct_adjacency_matrix_[t_path[0]][t_path[1]])
                    flow._assign_path = route_link_set

    #将[0,1,2,3]这样子的路径集合，改为[(0,1),(1,2),(2,3)]这样的集合
    def change_list_to_tuple(self,route):
        k = 0
        des_tuple = []
        for ele in route:
            if k == 0:
                k = k +1
                continue
            des_tuple.append((route[k-1],route[k]))
            k = k + 1

        return des_tuple

    # 将[0,1,2,3]这样子的路径集合，改为[link_obj,link_obj,...,link_obj]这样的集合
    def change_route_to_linkobj(self,net_topo,route_list):
        route_obj = []
        route_pair = self.change_list_to_tuple(route_list)

        for link in route_pair:
            route_obj.append(net_topo._directAdjMatrix[link[0]][link[1]])

        return route_obj




    # 无限制KSP
    def unlimited_ksp(self,adj_matrix, src_node_id, dst_node_id, k,netTopoClass,flow_bd):  # 可能有回路
        '''
        有限制KSP，不存在回路
            :param adj_matrix:
            :param src_node_id:
            :param dst_node_id:
            :param k:
            :return:
        '''


        ksp_routes = []

        # Initialize the queue
        queue = PriorityQueue()
        queue.put((0, [src_node_id]))
        while not queue.empty() and len(ksp_routes) < k:
            (cost, path) = queue.get()
            current_node = path[-1]

            if current_node == dst_node_id and cost <= 7:
                # ksp_routes.append((cost, path))
                ksp_routes.append(self.change_list_to_tuple(path))
            else:
                for neighbor in range(len(adj_matrix[current_node])):

                    if adj_matrix[current_node][neighbor] != 0:
                        linkobj = netTopoClass._directAdjMatrix[current_node][neighbor]

                    if adj_matrix[current_node][neighbor] != 0 and neighbor not in path \
                            and linkobj._occupyBw+flow_bd <= head.DEFAULT_LINK_MAX_BANDWIDTH:  # if neighbor exists and not in path

                        total_cost = cost + adj_matrix[current_node][neighbor]
                        temp_path = list(path)
                        temp_path.append(neighbor)
                        queue.put((total_cost, temp_path))
        return ksp_routes

    # 无限制KSP，路由策略
    def unlimited_ksp_route_method(self,netTopoClass, flowObjList,k):
        # 收集所有flow_id
        id_set = set()     # 无重复元素的集合
        for flow in flowObjList:
            id_set.add(flow._flowId)

        # 对每组冗余流执行：
        for fid in id_set:
            # 选出具有相同flow_id的冗余流
            flow_group = [flow for flow in flowObjList if flow._flowId == fid]
            djt_routes_map = []  # [(cost, path)]
            # 深拷贝一份邻接链表
            adj_matrix_dup = copy.deepcopy(netTopoClass._adjMatrix)

            flow_bd = 8*flow_group[0]._frameSize/(flow_group[0]._period ) * 1000
            # 为这组冗余流寻找不相交最短路径
            djt_routes_map = self.unlimited_ksp(adj_matrix_dup, flow_group[0]._srcNode._deviceId, flow_group[0]._dstNode._deviceId,k,netTopoClass,flow_bd)
            # print('flow_group[0]._redundancy = ',flow_group[0]._redundancy,'djt_routes_map = ',djt_routes_map)
            if len(djt_routes_map) < flow_group[0]._redundancy :
                djt_routes_map.clear()
            else:
                for flow in flow_group:
                    flow.is_routed = head.AssignStatus.Assigned
                    # tmp_route = djt_routes_map.pop()
                    tmp_route = random.sample(djt_routes_map,1)[0]
                    # print("tmp_route = ",tmp_route)
                    route_link_set = []
                    for t_path in tmp_route:
                        linkobj = netTopoClass._directAdjMatrix[t_path[0]][t_path[1]]
                        linkobj._occupyBw += 8*flow._frameSize/(flow._period ) * 1000
                        route_link_set.append(linkobj)
                    flow._assignPath = route_link_set

    # ILP路由策略
    def ILP_route_method(self,netTopoClass, trafficClass):
        #Step1:初始化决策变量，每个节点维护ingress_ilp集合与egress_ilp集合
        # ex：假设节点1与节点2相连
        # egress_ilp = [
        #     [X1, 2, fid1、X1, 2, fid2、X1, 2, fid3], 该节点该端口对应链路对应的决策变量集合
        # ]
        flow_list = trafficClass._flowObjList
        id_set = set()     # 无重复元素的集合
        for flow in flow_list:
            id_set.add(flow._flowId)


        i = 0
        for item in netTopoClass._adjMatrix:
            j = 0
            for ele in item:
                if ele != 0:
                    tmp_ilp = []
                    for fid in id_set:
                        tmp_variname = "X_SN" + i.__str__() + "_DN" + j.__str__() + "_fid" + str(fid)

                        ilp_veri = LpVariable(tmp_variname,cat=const.LpBinary)

                        netTopoClass._nodeSet[i]._exgressVari[j].append(ilp_veri)
                        netTopoClass._nodeSet[j]._ingressVari[i].append(ilp_veri)
                        netTopoClass._routeVarX.append(ilp_veri)

                j = j + 1
            i = i + 1
        # 2.创建ILP求解器
        # 创建问题实例，求最小极值
        prob = LpProblem("The ILP Route Problem", LpMinimize)  # LpMinimize LpMaximize
        # 添加目标方程

        prob += (lpSum(
            netTopoClass._routeVarX[i] for i in range(len(netTopoClass._routeVarX))
        ))

        # 3.添加路由约束
        # 源端系统的出度之和等于冗余度
        # 目的端系统的入度之和等于冗余度
        # 其他节点出度之和等于入度之和
        # 收集所有flow_id
        id_set = set()     # 无重复元素的集合
        for flow in flow_list:
            id_set.add(flow._flowId)

        # 对每组冗余流执行：
        for fid in id_set:
            # 选出具有相同flow_id的冗余流
            flow_group = [flow for flow in flow_list if flow._flowId == fid]
            src_node = flow_group[0]._srcNode
            des_node = flow_group[0]._dstNode
            rl = flow_group[0]._redundancy
            # 3.1源端系统的出度之和等于冗余度
            egress_ilp_list = []
            for port in src_node._exgressVari:
                if port != []:
                    egress_ilp_list.append(port[fid])
            prob += lpSum(egress_ilp_list[i] for i in range(len(egress_ilp_list))) == rl
            ingress_ilp_list = []
            for port in src_node._ingressVari:
                if port != []:
                    ingress_ilp_list.append(port[fid])
            prob += lpSum(ingress_ilp_list[i] for i in range(len(ingress_ilp_list))) == 0
            # 3.2目的端系统的入度之和等于冗余度
            egress_ilp_list = []
            for port in des_node._exgressVari:
                if port != []:
                    egress_ilp_list.append(port[fid])
            prob += lpSum(egress_ilp_list[i] for i in range(len(egress_ilp_list))) == 0
            ingress_ilp_list = []
            for port in des_node._ingressVari:
                if port != []:
                    ingress_ilp_list.append(port[fid])
            prob += lpSum(ingress_ilp_list[i] for i in range(len(ingress_ilp_list))) == rl
            # 3.3其余节点出度之和等于入度之和
            for node in netTopoClass._nodeSet:
                if node != src_node and node != des_node:
                    egress_ilp_list = []
                    for port in node._exgressVari:
                        if port != []:
                            egress_ilp_list.append(port[fid])

                    ingress_ilp_list = []
                    for port in node._ingressVari:
                        if port != []:
                            ingress_ilp_list.append(port[fid])
                    prob += lpSum(egress_ilp_list[i] for i in range(len(egress_ilp_list))) == lpSum(ingress_ilp_list[i] for i in range(len(ingress_ilp_list)))

        # 4.对每条链路进行带宽约束，暂未实现


        # 5.lp文件保存该优化问题的信息，可以用文本编辑器打开
        prob.writeLP("ILP route solver.lp")

        # 6.求解
        prob.solve()

        #7. 得到最优值时，各决策变量的取值，如果没有找到最优值，则输出None
        # 如果成功得到了最优值，则会输出 Optimal
        if LpStatus[prob.status] == 'Infeasible':
            print('路由失败')
            ret = False
        else:
            print('路由成功')
            ret = True
        # for v in prob.variables():
        #     print(v.name, "=", v.varValue)

        #8.将ILP求解的结果解析成路径的形式
        id_set = set()     # 无重复元素的集合
        for flow in flow_list:
            id_set.add(flow._flowId)
        # 对每组冗余流执行：
        for fid in id_set:

            # 选出具有相同flow_id的冗余流
            flow_group = [flow for flow in flow_list if flow._flowId == fid]
            src_node = flow_group[0]._srcNode
            des_node = flow_group[0]._dstNode
            # print('src_node = ',src_node._nodeName,'des_node = ',des_node._nodeName)
            rl = flow_group[0]._redundancy


            # 先判断出冗余路径个数是否合理，是否与RL相同
            egress_cnt = 0
            for port in src_node._exgressVari:
                if port != [] and port[fid].varValue == 1.0:
                    egress_cnt = egress_cnt + 1
            ingress_cnt = 0
            for port in des_node._ingressVari:
                if port != [] and port[fid].varValue == 1.0:
                    ingress_cnt = ingress_cnt + 1



            if egress_cnt != rl or ingress_cnt != rl:
                # print("flow id = ", fid, "src_node = ", src_node.node_id, "des_node = ", des_node.node_id, "rl = ", rl,
                #       end=" ")
                # print("current route fail")
                continue
            # else:
                # print("flow id = ", fid, "src_node = ", src_node.node_id, "des_node = ", des_node.node_id, "rl = ", rl,
                #       end=" ")
                # print("current route success")
                # continue
            # 递归的生成几条路径
            ilp_route = []
            for i in range(rl):
                once_ilp_route = []
                self.ilp_route_recur(netTopoClass,src_node,des_node,once_ilp_route,fid)
                ilp_route.append(once_ilp_route)

            # print('ilp_route = ',ilp_route)

            #8.2 将调度结果加入流中
            for flow in flow_group:
                flow._isAssigned = head.AssignStatus.Assigned
                tmp_route = ilp_route.pop()

                route_link_set = []
                for t_path in tmp_route:
                    route_link_set.append(netTopoClass._directAdjMatrix[t_path[0]][t_path[1]])

                flow._assignPath.clear()
                flow._assignPath = route_link_set


    def ilp_route_recur(self,netTopoClass,src_node,des_node,ilp_route,fid):
        if src_node == des_node:
            return

        next_node_id = 0
        for port in src_node._exgressVari:
            if port != [] and port[fid].varValue == 1.0:
                port[fid].varValue = 0.0
                ilp_route.append((src_node._deviceId,next_node_id))
                self.ilp_route_recur(netTopoClass,netTopoClass._nodeSet[next_node_id],des_node,ilp_route,fid)
                return
            else:
                next_node_id = next_node_id + 1

    #根据邻接矩阵，源节点，目的节点以及最大跳数约束，遍历出所有的路径
    def find_paths_with_max_length(self,adj_matrix, source, destination, max_length,_directAdjMatrix,flowBd,maxBd):
        def dfs(current_node, path, length):
            if current_node == destination:
                if length <= max_length:
                    paths.append(path[:])
                return

            visited[current_node] = True

            for next_node, has_edge in enumerate(adj_matrix[current_node]):
                # print('next_node = ',next_node,'has_edge = ',has_edge,'adj_matrix = ', adj_matrix)
                if has_edge and not visited[next_node] \
                        and length < max_length \
                        and _directAdjMatrix[current_node][next_node]._occupyBw + flowBd <= maxBd:
                    path.append(next_node)
                    dfs(next_node, path, length + 1)
                    path.pop()

            visited[current_node] = False

        paths = []
        visited = [False] * len(adj_matrix)
        dfs(source, [source], 0)
        return paths

    # 定义一个函数，用于返回二维集合的一维子集的长度
    def get_sublist_length(self,sublist):
        return len(sublist)
    #根据邻接矩阵和跳数约束，随机选出k条路由
    def random_find_k_paths(self,k,adj_matrix, source, destination, max_length,_directAdjMatrix,flowBd,maxBd):
        paths = []
        resultPaths = []

        # print('source._deviceId = ',source._deviceId,'destination._deviceId = ',destination._deviceId,'adj_matrix = ',adj_matrix)
        paths = self.find_paths_with_max_length(adj_matrix, source._deviceId, destination._deviceId, max_length,_directAdjMatrix,flowBd,maxBd)

        if len(paths)<= k:
            return paths
        else:
            #获得排序集合
            pathsOrderSet = sorted(paths, key=self.get_sublist_length)
            part1 = int(k/3) + 1
            part2 = int(k - part1)
            for i in range(part1):
                resultPaths.append(pathsOrderSet[i])
            for item in resultPaths:
                paths.remove(item)
            return resultPaths + random.sample(paths,part2)


    #-------------------------------------------------
    #函数名称：kRouteMethod
    #输入参数：根据输入权重、总共寻找M条路经，然后根据权重从中选择出k跳路径
    #输出参数：无
    #函数描述：用于求出每条流的路径
    #-------------------------------------------------
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

    def routeMethod(self, netTopoClass, trafficClass
                    , _hop_c=0.2, _bd_c=0.2, _fn_c=0.2, _dn_c=0.2, _DoCL_c=0.2, _DoC_c=0.2
                    , M=10):
        netEvalTool = network_eval_tools()
        hop_c = _hop_c  # 跳数权重
        bd_c = _bd_c  # 带宽权重
        fn_c = _fn_c  # 链路流数量权重
        dn_c = _dn_c  # 设备流数量权重
        DoCL_c = _DoCL_c  # 压缩影响度权重
        DoC_c = _DoC_c  # 冲突度权重

        for flow in trafficClass._flowObjList:
            if flow._isRouted == head.AssignStatus.Assigned:
                continue
            # 1.为这条流选出M条路由
            route_set = []
            route_value_set = []

            tmp_route_set = self.random_find_k_paths(M, netTopoClass._adjMatrix
                                                             , flow._srcNode, flow._dstNode, head.DEFAULT_MAX_HOP
                                                     ,netTopoClass._directAdjMatrix,flow._flowBandwith,head.DEFAULT_LINK_MAX_BANDWIDTH)
            # route_set.append(self.spFlowobjLinkobj(netTopoClass, flow))


            # 2.将这M跳路由改为正确的route_obj的格式
            for path in tmp_route_set:
                route_set.append(self.change_route_to_linkobj(netTopoClass, path))


            # self.dbgTool.printRouteSet(route_set)
            # 3.评估这些路由
            # print("-->route_ser 评估：")
            for route in route_set:
                eval_hop = netEvalTool.est_route_hop(route)
                eval_bandwith = netEvalTool.est_route_bandwith(route)
                # print('eval_bandwith = ',eval_bandwith)
                if eval_bandwith<0.001:
                    # print('bandwith error')
                    route_value_set.append(head.INF_MINUS)
                    continue #超出带宽限制了已经
                eval_flownum = netEvalTool.est_route_flownum(route)

                eval_devnum = netEvalTool.est_route_devnum(route)
                eval_DoCL = netEvalTool.est_route_DoCL(route)
                eval_DoC = netEvalTool.est_route_DoC(route, flow._period)
                # print("hop = ",eval_hop,
                #       "eval_bandwith = ",eval_bandwith)
                routeValue = hop_c * eval_hop + bd_c * eval_bandwith + fn_c * eval_flownum
                + dn_c * eval_devnum + DoCL_c * eval_DoCL + DoC_c * eval_DoC

                route_value_set.append(round(routeValue, 3))
                # route_value_set.append(eval_bandwith)

            # print("评估结束 <--")
            # print("route_value_set = ",route_value_set)
            if route_value_set.count(head.INF_MINUS) >= len(route_value_set):
                # print('666666666666')
                #当前流无法调度了
                continue


            best_route = route_set[self.list_maxindex(route_value_set)]
            flow._isRouted = head.AssignStatus.Assigned
            # 4.将流加入各条链路中
            flow._assignPath.clear()
            for link in best_route:
                flow._assignPath.append(link)
            # 5.将链路加入各条流中
            for link in best_route:
                link.addFlowObjToLink(flow)
                link._occupyBw += flow._flowBandwith
                link._occupyFlowCnt += 1
                if link._dstNode._nodeType == head.NodeType.Switch:
                    link._dstNode._flowCnt += 1


    '''
        我们给出多个版本的预处理函数:根据帧大小的预处理函数
    '''
    def routeTTAndRCMethod(self, netTopoClass, trafficClass
                    , _RCadjMatrix ,_hop_c=0.2, _bd_c=0.2, _fn_c=0.2, _dn_c=0.2, _DoCL_c=0.2, _DoC_c=0.2
                    , M=10):
        netEvalTool = network_eval_tools()
        hop_c = _hop_c  # 跳数权重
        bd_c = _bd_c  # 带宽权重
        fn_c = _fn_c  # 链路流数量权重
        dn_c = _dn_c  # 设备流数量权重
        DoCL_c = _DoCL_c  # 压缩影响度权重
        DoC_c = _DoC_c  # 冲突度权重

        for flow in trafficClass._flowObjList:
            if flow._isRouted == head.AssignStatus.Assigned :
                continue
            # 1.为这条流选出M条路由
            route_set = []
            route_value_set = []
            tmp_route_set = []
            if flow._flowType=='TT':
                tmp_route_set = self.random_find_k_paths(M, netTopoClass._adjMatrix
                                                             , flow._srcNode, flow._dstNode, head.DEFAULT_MAX_HOP
                                                     ,netTopoClass._directAdjMatrix,flow._flowBandwith,head.DEFAULT_LINK_MAX_BANDWIDTH)
            elif flow._flowType=='RC':
                tmp_route_set = self.random_find_k_paths(1, _RCadjMatrix
                                                         , flow._srcNode, flow._dstNode, head.DEFAULT_MAX_HOP
                                                         , netTopoClass._directAdjMatrix, flow._flowBandwith,
                                                         head.DEFAULT_LINK_MAX_BANDWIDTH)
            # route_set.append(self.spFlowobjLinkobj(netTopoClass, flow))


            # 2.将这M跳路由改为正确的route_obj的格式
            for path in tmp_route_set:
                route_set.append(self.change_route_to_linkobj(netTopoClass, path))


            # self.dbgTool.printRouteSet(route_set)
            # 3.评估这些路由
            # print("-->route_ser 评估：")
            for route in route_set:
                eval_hop = netEvalTool.est_route_hop(route)
                eval_bandwith = netEvalTool.est_route_bandwith(route)
                # print('eval_bandwith = ',eval_bandwith)
                if eval_bandwith<0.001:
                    # print('bandwith error')
                    route_value_set.append(head.INF_MINUS)
                    continue #超出带宽限制了已经
                eval_flownum = netEvalTool.est_route_flownum(route)

                eval_devnum = netEvalTool.est_route_devnum(route)
                eval_DoCL = netEvalTool.est_route_DoCL(route)
                eval_DoC = netEvalTool.est_route_DoC(route, flow._period)
                # print("hop = ",eval_hop,
                #       "eval_bandwith = ",eval_bandwith)
                routeValue = hop_c * eval_hop + bd_c * eval_bandwith + fn_c * eval_flownum
                + dn_c * eval_devnum + DoCL_c * eval_DoCL + DoC_c * eval_DoC

                route_value_set.append(round(routeValue, 3))
                # route_value_set.append(eval_bandwith)

            # print("评估结束 <--")
            # print("route_value_set = ",route_value_set)
            if route_value_set.count(head.INF_MINUS) >= len(route_value_set):
                # print('666666666666')
                #当前流无法调度了
                continue


            best_route = route_set[self.list_maxindex(route_value_set)]
            flow._isRouted = head.AssignStatus.Assigned
            # 4.将流加入各条链路中
            flow._assignPath.clear()
            for link in best_route:
                flow._assignPath.append(link)
            # 5.将链路加入各条流中
            for link in best_route:
                link.addFlowObjToLink(flow)
                link._occupyBw += flow._flowBandwith
                link._occupyFlowCnt += 1
                if link._dstNode._nodeType == head.NodeType.Switch:
                    link._dstNode._flowCnt += 1
    '''
       将交换机之间的环破除掉
    '''
    def dfs_remove_cycles(self,graph, node, visited, parent, sw_num):
        visited[node] = True
        for neighbor in range(sw_num):
            if graph[node][neighbor] == 1:
                if not visited[neighbor]:
                    if not self.dfs_remove_cycles(graph, neighbor, visited, node, sw_num):
                        return False
                elif neighbor != parent:
                    # This edge forms a cycle, so remove it
                    graph[node][neighbor] = 0
                    graph[neighbor][node] = 0
                    return False
        return True

    def remove_cycles(self,adj_matrix, sw_num):
        visited = [False] * len(adj_matrix)

        for i in range(sw_num):
            if not visited[i]:
                self.dfs_remove_cycles(adj_matrix, i, visited, -1, sw_num)

        return adj_matrix
    '''
        我们给出多个版本的预处理函数:根据帧大小的预处理函数
    '''
    def prehandle_framesize_base(self,traffic_set):
        wait_order_list = []
        tmp_wait_order_list = []
        for flow in traffic_set:
            tmp_wait_order_list.append([flow.frame_size,flow])
        wait_order_list = copy.deepcopy(tmp_wait_order_list)
        wait_order_list = sorted(wait_order_list, key=lambda x: x[0])

        wair_order_list_first_lie = []
        for item in wait_order_list:
            wair_order_list_first_lie.append(item[1])

        return wair_order_list_first_lie

    '''
        我们给出多个版本的预处理函数:根据占用带宽的预处理函数
    '''
    def prehandle_flowbandwith_base(self,traffic_set):
        wait_order_list = []
        tmp_wait_order_list = []
        for flow in traffic_set:
            tmp_wait_order_list.append([flow.frame_size*8/flow.period,flow])
        wait_order_list = copy.deepcopy(tmp_wait_order_list)
        wait_order_list = sorted(wait_order_list, key=lambda x: x[0], reverse=True)

        wair_order_list_first_lie = []
        for item in wait_order_list:
            wair_order_list_first_lie.append(item[1])

        return wair_order_list_first_lie

    '''
        我们给出多个版本的预处理函数:根据周期进行排序
    '''
    def prehandle_period_base(self,traffic_set):
        wait_order_list = []
        tmp_wait_order_list = []
        for flow in traffic_set:
            tmp_wait_order_list.append([flow.period,flow])
        wait_order_list = copy.deepcopy(tmp_wait_order_list)
        wait_order_list = sorted(wait_order_list, key=lambda x: x[0], reverse=True)

        wair_order_list_first_lie = []
        for item in wait_order_list:
            wair_order_list_first_lie.append(item[1])

        return wair_order_list_first_lie