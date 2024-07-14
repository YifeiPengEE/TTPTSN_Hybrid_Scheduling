import copy
import matplotlib.pyplot as plt
from head import *
import head
import random
from time import *
import socket
from functools import reduce
from math import gcd
from time import *
import sys


'''
def main():
    print('ssss')

    period_list = [500000]  # 所有和时间相关得参数，单位是ns
    flowNum = 4

    # x.创建打印工具
    debugTool = debugToolClass()
    # x.创建流量生成器
    tgTool = trafficGeneratorToolClass()
    # x.创建调度器
    tsnRecurScheTool = tsnRecurSchedMethod()
    # x.创建绘画工具
    net_draw_tool = NetworkDrawTools(1, 1)

    # 验证重路由
    reRouteTopo = rerouteTopo()

    net_draw_tool.network_topo_plot(reRouteTopo._topology)
    net_draw_tool.network_topo_plot(reRouteTopo._topologyError)

    # x.生成netTopoClass
    netTopo = netTopoClass(reRouteTopo._topology, reRouteTopo._swNum, reRouteTopo._esNum)

    # x.生成flowObjList
    # flowObjList = tgTool.generateRandomFlows(netTopo, reRouteTopo._swNum, reRouteTopo._esNum, period_list, flowNum)
    flowObjList = tgTool.determGenerateRandomFlows(netTopo, 0, 1, period_list, flowNum)
    # x.分析流量
    tf = trafficClass(netTopo, flowObjList)
    # x.打印
    debugTool.printTrafficClass(tf)

    # x.进行路由
    tsnRecurScheTool.routeMethod(netTopo, tf)

    # x.进行调度
    tsnRecurScheTool.schedMethod(netTopo, tf)
    print('normal')
    # debugTool.printFlowObjListRoute(tf)
    debugTool.printFlowObjQbv(tf)

    # x.构造故障
    newTopo = reRouteTopo._topologyError
    rerouteFlowIdList = [0, 1, 2, 3]

    print('reroute')
    # .进行重调度
    rerouteTf = tsnRecurScheTool.reRouteMethod(netTopo, tf, newTopo, rerouteFlowIdList)
    debugTool.printFlowObjQbv(rerouteTf)
    # debugTool.printFlowObjListRoute(rerouteTf)

    print('end')
'''

# XML文件统一保存路径
tsnm_workspace_init = "C:/tsnm_workspace/init"
tsnm_workspace_recov = "C:/tsnm_workspace/recov"


def udp_recv(sock):
    print("Plan init.")
    topo_file_path_init = tsnm_workspace_init + "/topo_desc.xml"
    flow_file_path_init = tsnm_workspace_init + "/flow_desc.xml"
    plan_file_path, flow_list, netTopo, tf, tsnRecurScheTool = calculate_init(topo_file_path_init, flow_file_path_init, tsnm_workspace_init)

    # while True:
    # 收报文
    data, addr = sock.recvfrom(1500)
    # print(f"Received data from {addr}: {data.decode()}")

    # 解析TLV
    # topo_file_path, flow_file_path = TlvProcMode.decode_plan_req_tlv(data)
    # print("topo_file_path=" + topo_file_path)
    # print("flow_file_path=" + flow_file_path)
    # if topo_file_path == '' or flow_file_path == '':
    #     continue

    print("Plan recovery.")
    topo_file_path_recov = tsnm_workspace_recov + "/topo_desc.xml"
    calculate_rec(topo_file_path_recov, tsnm_workspace_recov, flow_list, netTopo, tf, tsnRecurScheTool)

    packet = TlvProcMode.create_plan_resp_tlv(plan_file_path)
    sock.sendto(packet, addr)


def calculate_init(topo_file_name, flow_file_name, output_path):
    start_time = time()

    # x.创建打印工具
    # debugTool = debugToolClass()

    # x.创建调度器
    # tsnRecurScheTool = tsnRecurSchedMethod()
    # ttfcScheTool = ttfcRecurTTRCSlotSchedMethod()
    ttfcScheTool = tsnRecurSchedMethod()

    # 解析拓扑描述XML
    topo_xml_anls_mode = TopoXmlAnlsMode(topo_file_name)
    # topo_xml_anls_mode.print_dict_info()
    node_list = topo_xml_anls_mode.get_node_list()
    adj_matrix = topo_xml_anls_mode.get_adj_matrix()

    print(adj_matrix)
    # 生成net_topo对象
    print('node_list = ',node_list)
    netTopo = netTopoClass(adj_matrix, topo_xml_anls_mode.sw_sum, topo_xml_anls_mode.es_sum)

    # 解析流描述XML
    flow_xml_anls_mode = FlowXmlAnlsMode(flow_file_name, netTopo._nodeSet)
    # flow_xml_anls_mode.print_flow_list()
    flow_list = flow_xml_anls_mode.get_flow_list()

    # 拓扑绘制工具
    # net_draw_tool = NetworkDrawTools(1, 1)
    # net_draw_tool.network_topo_plot(adj_matrix)



    # 生成traffic anlysis
    print('flow_list = ',flow_list)
    dgTool = debugToolClass()
    tf = trafficClass(netTopo, flow_list)
    dgTool.printTrafficClass(tf)



    end_time = time()
    print(f"[init] Time for parsing files and generating objects:{end_time - start_time}")

    start_time = time()

    # x.进行路由
    route_start_time = time()
    # ttfcScheTool.route(netTopo, tf)
    ttfcScheTool.routeMethod(netTopo, tf)
    route_end_time = time()
    print(f"[init] Time for routing:{route_end_time - route_start_time}")


    # x.进行调度
    sche_start_time = time()
    ttfcScheTool.schedMethod(netTopo, tf)
    sche_end_time = time()
    print(f"[init] Time for scheduling:{sche_end_time - sche_start_time}")

    dgTool.printFlowObjListRoute(tf)
    # debugTool.printFlowObjQbv(tf)

    end_time = time()
    init_alg_time = end_time - start_time


    # 补丁：根据_idleWindowList计算_occupyWindowList排序
    for link in netTopo._linkSet:
        # print(f"link._linkName={link._linkName}")
        # print(f"_idleWindowList: {link._idleWindowList}")
        bt = 0
        for idle_slot in link._idleWindowList:
            et = idle_slot[0]
            if bt < et:
                link._occupyWindowList.append([bt, et])
            bt = idle_slot[1]
        if bt < tf._hyperPeriod:
            link._occupyWindowList.append([bt, tf._hyperPeriod])
        # if len(link._occupyWindowList) == 0:    # 说明整个超周期都处于关闭状态，但这里我把他改成整个周期都
        # print(f"_occupyWindowList: {link._occupyWindowList}")

    # 打印规划结果
    dgTool.printFlowObjQbv(tf)
    dgTool.printFlowObjHole(tf)
    # 开始计时
    start_time = time()

    # 生成Qbv XML
    gen_all_qbv_xml(netTopo, tf._hyperPeriod, topo_xml_anls_mode, output_path)

    # 生成规划XML
    plan_xml_gen_mode = PlanXmlGenMode(tf._hyperPeriod)
    dgTool.printFlowObjListRoute(tf)
    for flow in tf._flowObjList:
        flow_plan = {}
        for i in range(len(flow._assignPath)):

            link = flow._assignPath[i]
            link_name = link._linkName
            startOffset = flow._startOffset
            flowLen = flow._frameSize * 8

            flow_plan[link] = []
            for instance in range(int(tf._hyperPeriod / flow._period)):
                timeslot = [startOffset + instance * flow._period, startOffset + flowLen + instance * flow._period]
                flow_plan[link].append(copy.deepcopy(timeslot))
        plan_xml_gen_mode.add_flow_plan(flow, flow_plan)
    plan_xml_gen_mode.gen_plan_xml(output_path + "/plan_desc.xml")

    end_time = time()


    # 生成TTFC软件使用的规划XML
    ttfcPlanXml = TTFCPlanXmlGenMode()
    ttfcPlanXml.gen_plan_xml(tf,output_path + "/work_stream_beforea.xml")
    end_time = time()


    print(f"[init] Time for initial algorithm:{init_alg_time}")
    print(f"[init] Time for generating initial files:{end_time - start_time}")

    # 打印完成信息
    print("[init] Complete calculation!")

    # 返回规划结果文件路径
    with open(output_path + "/plan_desc.xml", 'r') as file:
        plan_file_name = os.path.abspath(file.name)
        print(plan_file_name)
        return plan_file_name, tf._flowObjList, netTopo, tf, ttfcScheTool


def calculate_rec(topo_file_name, output_path, flow_list, netTopo, tf, tsnRecurScheTool):
    start_time = time()

    # debugTool = debugToolClass()

    # x.构造故障
    new_topo_xml_anls_mode = TopoXmlAnlsMode(topo_file_name)
    # new_topo_xml_anls_mode.print_dict_info()
    new_adj_matrix = new_topo_xml_anls_mode.get_adj_matrix()
    print(new_adj_matrix)
    # new_adj_matrix = [[0, 1, 1, 0, 1, 0],
    #                   [1, 0, 0, 0, 0, 0],
    #                   [1, 0, 0, 1, 0, 0],
    #                   [0, 0, 1, 0, 0, 1],
    #                   [1, 0, 0, 0, 0, 0],
    #                   [0, 0, 0, 1, 0, 0]]

    # 检索受影响的流
    rerouteFlowIdList = []
    for flow in flow_list:
        for link in flow._assignPath:
            # print(f"new_adj_matrix[{link._srcNode._deviceId}][{link._dstNode._deviceId}]={new_adj_matrix[link._srcNode._deviceId][link._dstNode._deviceId]}")
            if new_adj_matrix[link._srcNode._deviceId][link._dstNode._deviceId] == 0:
                rerouteFlowIdList.append(flow._flowId)
                break

    re_flow_num = len(rerouteFlowIdList)
    print(f"[recov] Len of rerouteFlowIdList = {re_flow_num}")
    if len(rerouteFlowIdList) == 0:
        print("[recov] No faulty in network.")
        return

    start_time = time()


    print(f"[recov] Reroute begins.")
    # .进行重调度
    rerouteTf = tsnRecurScheTool.reRouteMethod(netTopo, tf, new_adj_matrix, rerouteFlowIdList)

    end_time = time()
    print(f"[recov] Time for algorithm recovery:{end_time - start_time}")
    print(f"[recov] Time for algorithm recovery per flow:{(end_time - start_time) / re_flow_num}")

    start_time = time()

    # 生成Qbv XML
    gen_all_qbv_xml(netTopo, rerouteTf._hyperPeriod, new_topo_xml_anls_mode, output_path)

    # 生成规划XML
    plan_xml_gen_mode = PlanXmlGenMode(rerouteTf._hyperPeriod)
    for flow in rerouteTf._flowObjList:
        flow_plan = {}
        for i in range(len(flow._assignQbv)):
            assign_qbv = flow._assignQbv[i]
            link = flow._assignPath[i]
            link_name = link._linkName
            startOffset = flow._startOffset
            flowLen = flow._frameSize * 8

            flow_plan[link] = []
            for instance in range(int(rerouteTf._hyperPeriod / flow._period)):
                timeslot = [startOffset + instance * flow._period, startOffset + flowLen + instance * flow._period]
                flow_plan[link].append(copy.deepcopy(timeslot))
        plan_xml_gen_mode.add_flow_plan(flow, flow_plan)
    plan_xml_gen_mode.gen_plan_xml(output_path + "/plan_desc.xml")

    end_time = time()
    print(f"[recov] Time for generating recovery files:{end_time - start_time}")

    # 打印完成信息
    print("[recov] Complete recalculation!")

    # 返回规划结果文件路径
    with open(output_path + "/plan_desc.xml", 'r') as file:
        plan_file_path = os.path.abspath(file.name)
        print(plan_file_path)
        return plan_file_path, flow_list, netTopo, rerouteTf, tsnRecurScheTool


def main1():
    print(f"PID={os.getpid()}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定IP地址和端口号
    ip = '127.0.0.1'    # 监听本地接口
    port = 4444         # 自定义端口号
    sock.bind((ip, port))

    while True:
        print(f"Waiting for input...\n")
        in_str = input()     # 阻塞
        if in_str == "y":
            udp_recv(sock)


def udp_recv2(sock):
    while True:
        # 收报文
        print(f"Waiting for UDP packet...")
        data, addr = sock.recvfrom(1500)
        print(f"Receive data from {addr}")

        # 解析TLV
        topo_file_name, flow_file_name = TlvProcMode.decode_plan_req_tlv(data)
        print(f"topo_file_path:{topo_file_name}")
        print(f"flow_file_path:{flow_file_name}")
        if os.path.exists(topo_file_name) == '' or flow_file_name == '':
            print("Empty file path! Skip.")
            continue
        if os.path.isfile(topo_file_name) is False or os.path.isfile(flow_file_name) is False:
            print("Not a file! Skip.")
            continue

        plan_file_path = os.path.dirname(topo_file_name)
        print(f"plan_file_path:{plan_file_path}")
        plan_file_name, flow_list, netTopo, tf, tsnRecurScheTool = calculate_init(topo_file_name,
                                                                                  flow_file_name,
                                                                                  plan_file_path)

        print(f"Finish calculation: {plan_file_name}")

        packet = TlvProcMode.create_plan_resp_tlv(plan_file_name)
        sock.sendto(packet, addr)


def main2():
    print(f"PID={os.getpid()}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定IP地址和端口号
    ip = '127.0.0.1'    # 监听本地接口
    port = 4444         # 自定义端口号
    sock.bind((ip, port))

    udp_recv2(sock)



def genQbvPlan():
    # 解析TLV
    topo_file_name = 'D:/TSNPlan1_3/Qt/build-tsn_manager_v1-Desktop_Qt_5_13_1_MinGW_32_bit-Debug/output/topo_desc.xml'
    flow_file_name = 'D:/TSNPlan1_3/Qt/build-tsn_manager_v1-Desktop_Qt_5_13_1_MinGW_32_bit-Debug/output/flow_desc.xml'
    print(f"topo_file_path:{topo_file_name}")
    print(f"flow_file_path:{flow_file_name}")
    if os.path.exists(topo_file_name) == '' or flow_file_name == '':
        print("Empty file path! Skip.")
    if os.path.isfile(topo_file_name) is False or os.path.isfile(flow_file_name) is False:
        print("Not a file! Skip.")

    plan_file_path = os.path.dirname(topo_file_name)
    print(f"plan_file_path:{plan_file_path}")
    plan_file_name, flow_list, netTopo, tf, tsnRecurScheTool = calculate_init(topo_file_name,
                                                                              flow_file_name,
                                                                              plan_file_path)

if __name__ == '__main__':
    sys.setrecursionlimit(10000)
    # main2()
    genQbvPlan()