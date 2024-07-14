import head
from head import *
import xml.etree.ElementTree as ET
import xml.dom.minidom
import time
import copy

'''
- <data>：根元素，表示整个 XML 数据。
- <cfgdata>：包含了配置数据的元素。
- <ports_tas>：表示一个 TAS（Time Aware Shaper）端口的配置。
- <port>：指定 TAS 端口的编号。
- <qbv_isenable>：指定 TAS 端口是否启用 IEEE 802.1Qbv 功能。
- <admin_base_time>：指定 TAS 端口的基准时间。
- <pitHs>：指定基准时间的高位秒。
- <pitMs>：指定基准时间的中位秒。
- <pitLs>：指定基准时间的低位秒。
- <admin_cycle_time>：指定 TAS 端口的周期时间。
- <pitHs>：指定周期时间的高位秒。
- <pitMs>：指定周期时间的中位秒。
- <pitLs>：指定周期时间的低位秒。
- <admin_cycle_time_extn>：指定 TAS 端口的扩展周期时间。
- <pitHs>：指定扩展周期时间的高位秒。
- <pitMs>：指定扩展周期时间的中位秒。
- <pitLs>：指定扩展周期时间的低位秒。
- <admin_ctl_list_len>：指定 TAS 端口的控制列表长度。
- <gate_states>：表示一个门状态的配置。
- <num>：指定门的编号。
- <admin_din>：指定门的控制输入。
- <update_indic>：指定配置数据的更新指示。
'''


class QbvXmlGenMode:
    def __init__(self):
        # self.root = ET.Element("data")
        # self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        # self.cfgdata = ET.SubElement(self.root, "cfgdata")
        # self.cfgdata.set("xmlns", "http://www.fc-ae.com/qbv")

        self.cfgdata = ET.Element("cfgdata")
        self.cfgdata.set("xmlns", "http://www.fc-ae.com/qbv")
        self.root = self.cfgdata

    def generate_xml(self, file_name):
        tree = ET.ElementTree(self.root)
        tree.write(file_name)

        # 格式化
        # 读取生成的XML文件
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 使用xml.dom.minidom对XML进行格式化
        dom = xml.dom.minidom.parseString(xml_data)
        formatted_xml = dom.toprettyxml(indent="  ")
        # 将格式化后的XML写回文件
        with open(file_name, 'w') as f:
            f.write(formatted_xml)
            f.close()

        # 删除第一行： <?xml version="1.0" ?>
        # 读取XML文件内容
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 删除声明
        xml_data = xml_data.replace('<?xml version="1.0" ?>\n', '')
        # 将修改后的内容写回文件
        with open(file_name, 'w') as f:
            f.write(xml_data)

    def add_port_tas(self, port_, qbv_isenable_, pitHs1, pitMs1, pitLs1,
                     pitHs2, pitMs2, pitLs2, pitHs3, pitMs3, pitLs3,
                     admin_ctl_list_len_):
        ports_tas = ET.SubElement(self.cfgdata, "ports_tas")

        port = ET.SubElement(ports_tas, "port")
        port.text = str(port_)

        qbv_isenable = ET.SubElement(ports_tas, "qbv_isenable")
        qbv_isenable.text = str(qbv_isenable_)

        admin_base_time = ET.SubElement(ports_tas, "admin_base_time")
        pitHs = ET.SubElement(admin_base_time, "pitHs")
        pitHs.text = str(pitHs1)
        pitMs = ET.SubElement(admin_base_time, "pitMs")
        pitMs.text = str(pitMs1)
        pitLs = ET.SubElement(admin_base_time, "pitLs")
        pitLs.text = str(pitLs1)

        admin_cycle_time = ET.SubElement(ports_tas, "admin_cycle_time")
        pitHs = ET.SubElement(admin_cycle_time, "pitHs")
        pitHs.text = str(pitHs2)
        pitMs = ET.SubElement(admin_cycle_time, "pitMs")
        pitMs.text = str(pitMs2)
        pitLs = ET.SubElement(admin_cycle_time, "pitLs")
        pitLs.text = str(pitLs2)

        admin_cycle_time_extn = ET.SubElement(ports_tas, "admin_cycle_time_extn")
        pitHs = ET.SubElement(admin_cycle_time_extn, "pitHs")
        pitHs.text = str(pitHs3)
        pitMs = ET.SubElement(admin_cycle_time_extn, "pitMs")
        pitMs.text = str(pitMs3)
        pitLs = ET.SubElement(admin_cycle_time_extn, "pitLs")
        pitLs.text = str(pitLs3)

        admin_ctl_list_len = ET.SubElement(ports_tas, "admin_ctl_list_len")
        admin_ctl_list_len.text = str(admin_ctl_list_len_)

        return ports_tas

    def add_gate_states(self, ports_tas, num_, admin_din_):
        gate_states = ET.SubElement(ports_tas, "gate_states")
        num = ET.SubElement(gate_states, "num")
        num.text = str(num_)
        admin_din = ET.SubElement(gate_states, "admin_din")
        admin_din.text = str(admin_din_)

    def add_update_indic(self, update_indic_):
        update_indic = ET.SubElement(self.cfgdata, "update_indic")
        update_indic.text = str(update_indic_)


def gen_all_qbv_xml(net_topo, hyper_period, topo_xml_anls_mode, workspace):
    # 规划结果已经填入link.occupyWindowList中

    node_xml_dict = {}  # 字典：节点->xml对象

    pitHs = (hyper_period & 0xFFFFFFFF0000000000000000) >> 64
    pitMs = (hyper_period & 0xFFFFFFFF00000000) >> 32
    pitLs = hyper_period & 0xFFFFFFFF

    default_dist = 0
    default_priority = 5

    for node in net_topo._nodeSet:
        # 初始化用于存储xml对象的字典
        qbv_xml = QbvXmlGenMode()
        node_xml_dict[node] = qbv_xml

        if len(node._egressLink) == 0:
            print(f"node{node._nodeId} has no egress link.")
            continue

        # print(f"node{node._nodeId} _egressLink:")
        # for l in node._egressLink:
        #     print(f"linkName<{l._linkName}>: srcId={l._srcNode._deviceId}, dstId={l._dstNode._deviceId}")

        link_list = node._egressLink
        # link_list = sorted(node._egressLink,
        #                    key=lambda x: topo_xml_anls_mode.get_src_port_id(x._srcNode._deviceId, x._dstNode._deviceId))

        flag = False
        for link in link_list:
            if len(link._occupyWindowList) > 0:
                flag = True
        if not flag:  # node所有链路的_occupyWindowList都为空，跳过这个node
            print(f"No new config file for node{node._deviceId}.")
            continue

        for link in link_list:
            # 先判断该链路上是否有流
            if len(link._occupyWindowList) == 0:
                print("Empty link: " + link._linkName)
                continue

            for dur in link._occupyWindowList:
                dur[0] += 20000
                dur[1] += 20000

            duration_list = []
            if link._occupyWindowList[0][0] > 0:
                duration_list.append([-1, link._occupyWindowList[0][0] - 0])
            duration_list.append([default_priority, link._occupyWindowList[0][1] - link._occupyWindowList[0][0]])

            for i in range(1, len(link._occupyWindowList)):
                if (link._occupyWindowList[i][0] - link._occupyWindowList[i - 1][1]) > 0:
                    duration_list.append([-1, link._occupyWindowList[i][0] - link._occupyWindowList[i - 1][1]])
                duration_list.append([default_priority, link._occupyWindowList[i][1] - link._occupyWindowList[i][0]])

            if (hyper_period - link._occupyWindowList[-1][1]) > 0:
                duration_list.append([-1, hyper_period - link._occupyWindowList[-1][1]])

            '''
            start_time = 0
            end_time = 0
            for i in range(len(link.occupyWindowList)):
                if link.occupyWindowList[i][0] - end_time <= dist:
                    end_time = link.occupyWindowList[i][1]
                else:
                    if end_time - start_time != 0:
                        duration_list.append((default_priority, end_time - start_time))    # 优先级为0的时隙
                    duration_list.append((-1, link.occupyWindowList[i][0] - end_time))   # 门全关的时隙

                    start_time = link.occupyWindowList[i][0]
                    end_time = link.occupyWindowList[i][1]

            if (traffic_analysis._hyper_period - link.occupyWindowList[-1][1]) > dist:
                duration_list.append((-1, traffic_analysis._hyper_period - link.occupyWindowList[-1][1]))
            '''

            src_port_id = topo_xml_anls_mode.get_src_port_id(link._srcNode._deviceId, link._dstNode._deviceId)
            if src_port_id is None:
                continue
            ports_tas = qbv_xml.add_port_tas(src_port_id, 0, 0, 0, 0, pitHs, pitMs, pitLs, 0, 0, 0, len(duration_list))

            for i in range(len(duration_list)):
                priority = duration_list[i][0]
                duration = duration_list[i][1]

                admin_din = (int(duration / 8)) << 8
                if priority == -1:
                    admin_din += ((0x01 << 7) | 0x01)
                else:
                    admin_din += ((0x01 << priority) | (0x01 << 7) | 0x01)
                qbv_xml.add_gate_states(ports_tas, i, admin_din)

        qbv_xml.add_update_indic(int(time.time()))

        qbv_xml.generate_xml(workspace + "/qbv_recv_node" + str(node._deviceId) + ".xml")


# 用于生成拓扑描述XML的类
class TopoXmlGenMode:
    def __init__(self):
        self.root = ET.Element("data")
        # self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.topo_data = ET.SubElement(self.root, "topo_data")
        # self.topo_data.set("xmlns", "http://www.fc-ae.com:topo")

        self.node_ports_dict = {}  # 节点和端口的映射
        self.node_addr_dict = {}  # 节点和管理地址的映射
        self.node_sum = 0  # 整个拓扑的节点数
        self.link_sum = 0  # 整个拓扑的链路数

    def add_node(self, node_id, man_addr="NULL"):
        if node_id in self.node_ports_dict.keys():  # node_id已经存在
            return
        self.node_ports_dict[node_id] = {}
        self.node_addr_dict[node_id] = man_addr
        self.node_sum += 1

    def add_link(self, src_node_id, src_port_id, dst_node_id, dst_port_id):
        if src_port_id not in self.node_ports_dict[src_node_id].keys():
            self.node_ports_dict[src_node_id][src_port_id] = {}

        if dst_node_id not in self.node_ports_dict[src_node_id][src_port_id]:
            self.link_sum += 1

        self.node_ports_dict[src_node_id][src_port_id][dst_node_id] = dst_port_id  # 无论是否已加入都更新一下

    def gen_topo_xml(self, file_name):
        node_num_obj = ET.SubElement(self.topo_data, "node_sum")
        node_num_obj.text = str(self.node_sum)

        link_num_obj = ET.SubElement(self.topo_data, "link_sum")
        link_num_obj.text = str(self.link_sum)

        nodes_obj = ET.SubElement(self.topo_data, "nodes")

        local_node_id_sorted_list = sorted(list(self.node_ports_dict.keys()))  # 按照node_id从小到大生成
        for local_node_id in local_node_id_sorted_list:
            local_node = ET.SubElement(nodes_obj, "node")

            local_node_id_obj = ET.SubElement(local_node, "node_id")
            local_node_id_obj.text = str(local_node_id)

            local_man_addr_obj = ET.SubElement(local_node, "man_addr")
            local_man_addr_obj.text = self.node_addr_dict[local_node_id]

            local_link_num_obj = ET.SubElement(local_node, "link_num")
            local_link_num_obj.text = str(self.link_sum)

            local_ports_obj = ET.SubElement(local_node, "ports")

            local_port_id_sorted_list = sorted(list(self.node_ports_dict[local_node_id].keys()))  # 根据port_id从小到大生成
            for local_port_id in local_port_id_sorted_list:
                local_port = ET.SubElement(local_ports_obj, "port")

                local_port_id_obj = ET.SubElement(local_port, "port_id")
                local_port_id_obj.text = str(local_port_id)

                local_neighbors_obj = ET.SubElement(local_port, "neighbors")

                remote_node_id_sorted_list = sorted(list(self.node_ports_dict[local_node_id][local_port_id].keys()))
                for remote_node_id in remote_node_id_sorted_list:
                    neighbor_obj = ET.SubElement(local_neighbors_obj, "neighbor")

                    remote_node_id_obj = ET.SubElement(neighbor_obj, "node_id")
                    remote_node_id_obj.text = str(remote_node_id)

                    remote_man_addr_obj = ET.SubElement(neighbor_obj, "man_addr")
                    remote_man_addr_obj.text = str(self.node_addr_dict[remote_node_id])

                    remote_port_id_obj = ET.SubElement(neighbor_obj, "port_id")
                    remote_port_id_obj.text = str(self.node_ports_dict[local_node_id][local_port_id][remote_node_id])

        # 生成XML
        tree = ET.ElementTree(self.root)
        tree.write(file_name)

        # 格式化XML
        # 读取生成的XML文件
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 使用xml.dom.minidom对XML进行格式化
        dom = xml.dom.minidom.parseString(xml_data)
        formatted_xml = dom.toprettyxml(indent="  ")
        # 将格式化后的XML写回文件
        with open(file_name, 'w') as f:
            f.write(formatted_xml)

        # 删除第一行
        # 读取XML文件内容
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 删除声明
        xml_data = xml_data.replace('<?xml version="1.0" ?>\n', '')
        # 将修改后的内容写回文件
        with open(file_name, 'w') as f:
            f.write(xml_data)


# 用于解析拓扑描述XML的类
class TopoXmlAnlsMode:
    def __init__(self, filename):
        self.filename = filename
        self.tree = ET.parse(filename)

        self.root = self.tree.getroot()
        print('self.root = ', self.root)
        self.node_ports_dict = {}  # 邻接关系字典: 本地节点ID -> {本地端口ID -> {邻接节点ID -> 邻接端口ID} }
        self.adj_matrix = []

        self.init()
        self._analyse_xml_1()  # 执行解析函数

    def init(self):
        self.node_sum = int(self.root.find("topo_data/node_sum").text)
        self.sw_sum = int(self.root.find("topo_data/sw_sum").text)
        self.es_sum = int(self.root.find("topo_data/es_sum").text)
        self.link_sum = int(self.root.find("topo_data/link_sum").text)
        self.node_list = [None] * self.node_sum  # 节点ID -> 节点对象
        print(f"node_sum={self.node_sum}, sw_sum={self.sw_sum}, es_num={self.es_sum}, link_sum={self.link_sum}")

    def _analyse_xml_1(self):
        local_node_obj_list = self.root.findall("topo_data/nodes/node")  # root是<data>元素
        for local_node_obj in local_node_obj_list:
            local_node_id = int(local_node_obj.find("node_id").text)
            local_device_type = int(local_node_obj.find("device_type").text)

            local_man_addr = local_node_obj.find("man_addr").text

            if local_node_id not in self.node_list:  # 未记录过
                if local_device_type == head.NodeType.Switch.value:
                    local_node = nodeClass(local_node_id, head.NodeType.Switch, local_node_id)
                elif local_device_type == head.NodeType.EndStation.value:
                    local_node = nodeClass(local_node_id - self.sw_sum, head.NodeType.EndStation, local_node_id)
                else:
                    print(f"Error in local device_type:{local_device_type}")
                    continue
                local_node.mng_addr = local_man_addr.split('/')[0]
                local_node.mng_port = int(local_man_addr.split('/')[1])
                self.node_list[local_node_id] = local_node

            if local_node_id not in self.node_ports_dict:
                self.node_ports_dict[local_node_id] = {}

            local_port_obj_list = local_node_obj.findall("ports/port")
            for local_port_obj in local_port_obj_list:
                local_port_id = int(local_port_obj.find("port_id").text)
                if local_port_id not in self.node_ports_dict[local_node_id]:
                    self.node_ports_dict[local_node_id][local_port_id] = {}

                neighbor_obj_list = local_port_obj.findall("neighbors/neighbor")
                for neighbor_obj in neighbor_obj_list:
                    remote_node_id = int(neighbor_obj.find("node_id").text)
                    remote_device_type = int(neighbor_obj.find("device_type").text)
                    remote_mng_addr = neighbor_obj.find("man_addr").text
                    remote_port_id = int(neighbor_obj.find("port_id").text)

                    if remote_node_id not in self.node_list:
                        if remote_device_type == head.NodeType.Switch.value:
                            remote_node = nodeClass(remote_node_id, head.NodeType.Switch, remote_node_id)
                        elif remote_device_type == head.NodeType.EndStation.value:
                            remote_node = nodeClass(remote_node_id, head.NodeType.EndStation,
                                                    remote_node_id - self.sw_sum)
                        else:
                            print(f"Error in remote device_type:{remote_device_type}")
                            continue
                        remote_node.mng_addr = remote_mng_addr.split('/')[0]
                        remote_node.mng_port = int(remote_mng_addr.split('/')[1])
                        self.node_list[remote_node_id] = remote_node

                    self.node_ports_dict[local_node_id][local_port_id][remote_node_id] = remote_port_id

    def _analyse_xml_2(self):
        for node_id in range(self.node_sum):
            if node_id < self.sw_sum:
                node = nodeClass(node_id, head.NodeType.Switch, node_id)
            else:
                node = nodeClass(node_id, head.NodeType.EndStation, node_id)
            self.node_list.append(node)

        local_node_obj_list = self.root.findall("topo_data/nodes/node")  # root是<data>元素
        for local_node_obj in local_node_obj_list:
            local_node_id = int(local_node_obj.find("node_id").text)
            local_device_type = int(local_node_obj.find("device_type").text)
            local_man_addr = local_node_obj.find("man_addr").text

            local_node = self.node_list[local_node_id]
            local_node.mng_addr = local_man_addr.split('/')[0]
            local_node.mng_port = int(local_man_addr.split('/')[1])

            if local_node_id not in self.node_ports_dict:
                self.node_ports_dict[local_node_id] = {}

            local_port_obj_list = local_node_obj.findall("ports/port")
            for local_port_obj in local_port_obj_list:
                local_port_id = int(local_port_obj.find("port_id").text)
                if local_port_id not in self.node_ports_dict[local_node_id]:
                    self.node_ports_dict[local_node_id][local_port_id] = {}

                neighbor_obj_list = local_port_obj.findall("neighbors/neighbor")
                for neighbor_obj in neighbor_obj_list:
                    remote_node_id = int(neighbor_obj.find("node_id").text)
                    remote_device_type = int(neighbor_obj.find("device_type").text)
                    remote_mng_addr = neighbor_obj.find("man_addr").text
                    remote_port_id = int(neighbor_obj.find("port_id").text)

                    remote_node = self.node_list[remote_node_id]
                    remote_node.mng_addr = remote_mng_addr.split('/')[0]
                    remote_node.mng_port = int(remote_mng_addr.split('/')[1])

                    self.node_ports_dict[local_node_id][local_port_id][remote_node_id] = remote_port_id

    def get_src_port_id(self, src_node_id, dst_node_id):
        for local_port_id, remote_node_dict in self.node_ports_dict[src_node_id].items():
            if dst_node_id in remote_node_dict.keys():
                return local_port_id

    def print_dict_info(self):
        for local_node_id, local_ports_dict in self.node_ports_dict.items():
            print(f"node{local_node_id}")
            for local_port_id, remote_node_dict in local_ports_dict.items():
                print(f"\tport{local_port_id}: ", end='')
                for remote_node_id, remote_port_id in remote_node_dict.items():
                    print(f"node{remote_node_id}_port{remote_port_id}, ", end='')
                print('')

    def get_node_ports_dict(self):  # 获取src_node_id的每个端口的对端节点id及其对应端口id
        return copy.copy(self.node_ports_dict)  # 只拷贝容器

    def get_node_list(self):
        sorted_node_list = sorted(self.node_list, key=lambda node: node._deviceId)
        return copy.copy(sorted_node_list)  # 只拷贝容器

    def get_adj_matrix(self):
        if len(self.adj_matrix) != 0:
            return copy.copy(self.adj_matrix)  # 只拷贝容器

        self.adj_matrix = [[0 for j in range(self.node_sum)] for i in range(self.node_sum)]
        for local_node_id in range(self.node_sum):
            if local_node_id in self.node_ports_dict:
                local_ports_dict = self.node_ports_dict[local_node_id]
                for local_port_id, remote_node_dict in local_ports_dict.items():
                    for remote_node_id, remote_port_id in remote_node_dict.items():
                        self.adj_matrix[local_node_id][remote_node_id] = 1
                        self.adj_matrix[remote_node_id][local_node_id] = 1
        return copy.copy(self.adj_matrix)


# 用于生成流量描述XML的类
class FlowXmlGenMode:
    def __init__(self):
        self.root = ET.Element("data")
        # self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.flow_data = ET.SubElement(self.root, "flow_data")
        # self.topo_data.set("xmlns", "http://www.fc-ae.com:topo")

        self.flow_info_list = []

    def add_flow(self, flow_id, src_id, dst_id, priority, period, jitter, deadline, frame_size, redundancy):
        self.flow_info_list.append(
            [flow_id, src_id, dst_id, priority, period, jitter, deadline, frame_size, redundancy])

    def add_flows(self, flow_info_list):
        self.flow_info_list.extend(flow_info_list)

    def gen_flow_xml(self, file_name):
        flow_sum_obj = ET.SubElement(self.flow_data, "flow_sum")
        flow_sum_obj.text = str(len(self.flow_info_list))

        flows_obj = ET.SubElement(self.flow_data, "flows")
        for flow_info in self.flow_info_list:
            index = 0

            flow_obj = ET.SubElement(flows_obj, "flow")

            flow_id_obj = ET.SubElement(flow_obj, "flowID")
            flow_id_obj.text = str(flow_info[index])
            index += 1

            flow_src_id_obj = ET.SubElement(flow_obj, "srcID")
            flow_src_id_obj.text = str(flow_info[index])
            index += 1

            flow_dst_id_obj = ET.SubElement(flow_obj, "dstID")
            flow_dst_id_obj.text = str(flow_info[index])
            index += 1

            flow_priority_obj = ET.SubElement(flow_obj, "priority")
            flow_priority_obj.text = str(flow_info[index])
            index += 1

            flow_period_obj = ET.SubElement(flow_obj, "period")
            flow_period_obj.text = str(flow_info[index])
            index += 1

            flow_jitter_obj = ET.SubElement(flow_obj, "jitter")
            flow_jitter_obj.text = str(flow_info[index])
            index += 1

            flow_deadline_obj = ET.SubElement(flow_obj, "deadline")
            flow_deadline_obj.text = str(flow_info[index])
            index += 1

            flow_frame_size_obj = ET.SubElement(flow_obj, "frame_size")
            flow_frame_size_obj.text = str(flow_info[index])
            index += 1

            flow_redundancy_obj = ET.SubElement(flow_obj, "redundancy")
            flow_redundancy_obj.text = str(flow_info[index])
            index += 1

        # 生成XML
        tree = ET.ElementTree(self.root)
        tree.write(file_name)

        # 格式化XML
        # 读取生成的XML文件
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 使用xml.dom.minidom对XML进行格式化
        dom = xml.dom.minidom.parseString(xml_data)
        formatted_xml = dom.toprettyxml(indent="  ")
        # 将格式化后的XML写回文件
        with open(file_name, 'w') as f:
            f.write(formatted_xml)

        # 删除第一行
        # 读取XML文件内容
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 删除声明
        xml_data = xml_data.replace('<?xml version="1.0" ?>\n', '')
        # 将修改后的内容写回文件
        with open(file_name, 'w') as f:
            f.write(xml_data)


# 用于解析流量描述XML的类
class FlowXmlAnlsMode:
    def __init__(self, flow_xml_filename, node_list):
        self.filename = flow_xml_filename
        self.tree = ET.parse(self.filename)
        self.root = self.tree.getroot()
        self.node_dict = {}  # 节点ID到节点对象的映射
        self.flow_list = []
        self.node_list = node_list

        # 解析XML
        self._analyse_xml()

    def _analyse_xml(self):
        # 遍历节点ID到节点对象的映射
        for node in self.node_list:
            self.node_dict[node._deviceId] = node

        flow_obj_list = self.root.findall("flow_data/flows/flow")  # root是<data>元素
        print(f"Len of flow_obj_list:{len(flow_obj_list)}")
        for flow_obj in flow_obj_list:
            if flow_obj is None:
                print(f"flow_obj{flow_obj} is None")
                continue
            flow_id = int(flow_obj.find("flowID").text)
            flow_src_id = int(flow_obj.find("srcID").text)
            flow_dst_id = int(flow_obj.find("dstID").text)
            flow_priority = int(flow_obj.find("priority").text)
            flow_period = int(flow_obj.find("period").text)
            flow_jitter = int(flow_obj.find("jitter").text)
            flow_deadline = int(flow_obj.find("deadline").text)
            flow_frame_size = int(flow_obj.find("frameSize").text)
            flow_redundancy = int(flow_obj.find("redundancy").text)

            for subflow_id in range(flow_redundancy):
                if (flow_src_id not in self.node_dict) or (flow_dst_id not in self.node_dict):
                    print(f"flow_src_id{flow_src_id} in self.node_dict:{flow_src_id in self.node_dict}, "
                          f"flow_dst_id{flow_dst_id} in self.node_dict:{flow_dst_id in self.node_dict}")
                    continue

                flow = flowClass(flow_id, subflow_id, None, None,
                                 self.node_dict[flow_src_id]._nodeId, self.node_dict[flow_dst_id]._nodeId,
                                 flow_priority,
                                 flow_period, flow_deadline, flow_jitter, flow_frame_size, flow_redundancy)

                self.flow_list.append(flow)

    def get_flow_list(self):
        return copy.copy(self.flow_list)

    def print_flow_list(self):
        print("flow_list:")
        for flow in self.flow_list:
            print(f"<flow_id={flow._flowId}, subflow_id={flow._subflowId}, src_node_id={flow._srcNodeId}, "
                  f"dst_node_id={flow._dstNodeId}, priority={flow._priority}, period={flow._period}, "
                  f"deadline={flow._deadline}, jitter={flow._jitter}, frame_size={flow._frameSize}, "
                  f"redundancy={flow._redundancy}>")


# 用于生成规划结果描述XML的类
class PlanXmlGenMode:
    def __init__(self, hyper_period):
        self.root = ET.Element("data")
        # self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")
        self.plan_data = ET.SubElement(self.root, "plan_data")
        # self.topo_data.set("xmlns", "http://www.fc-ae.com:topo")
        self.flow_plan_dict = {}
        self.hyper_period = hyper_period

    def add_flow_plan(self, flow, flow_plan):
        self.flow_plan_dict[flow] = flow_plan

    def gen_plan_xml(self, file_name):
        flow_sum_obj = ET.SubElement(self.plan_data, "flow_sum")
        flow_sum_obj.text = str(len(self.flow_plan_dict))

        hyper_period_obj = ET.SubElement(self.plan_data, "hyper_period")
        hyper_period_obj.text = str(self.hyper_period)

        flows_obj = ET.SubElement(self.plan_data, "flows")

        sorted_flow_plan_dict = dict(sorted(self.flow_plan_dict.items(), key=lambda x: x[0]._flowId))  # 按flow_id升序排列
        for flow, plan_dict in sorted_flow_plan_dict.items():
            flow_obj = ET.SubElement(flows_obj, "flow")

            flow_id_obj = ET.SubElement(flow_obj, "flow_id")
            flow_id_obj.text = str(flow._flowId)

            route_obj = ET.SubElement(flow_obj, "route")

            for link in flow._assignPath:
                link_obj = ET.SubElement(route_obj, "link")

                src_node_id_obj = ET.SubElement(link_obj, "src_id")
                src_node_id_obj.text = str(link._srcNode._deviceId)

                dst_node_id_obj = ET.SubElement(link_obj, "dst_id")
                dst_node_id_obj.text = str(link._dstNode._deviceId)

                instances_obj = ET.SubElement(link_obj, "instances")

                instance_num_obj = ET.SubElement(instances_obj, "instance_num")
                instance_num_obj.text = str(len(plan_dict[link]))

                for instance_phy_index in range(len(plan_dict[link])):
                    instance_obj = ET.SubElement(instances_obj, "instance")

                    instance_id_obj = ET.SubElement(instance_obj, "instance_id")
                    instance_id_obj.text = str(instance_phy_index)

                    instance_begin_time = ET.SubElement(instance_obj, "begin_time")
                    instance_begin_time.text = str(plan_dict[link][instance_phy_index][0])

                    instance_end_time = ET.SubElement(instance_obj, "end_time")
                    instance_end_time.text = str(plan_dict[link][instance_phy_index][1])

        # 生成XML
        tree = ET.ElementTree(self.root)
        tree.write(file_name)

        # 格式化XML
        # 读取生成的XML文件
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 使用xml.dom.minidom对XML进行格式化
        dom = xml.dom.minidom.parseString(xml_data)
        formatted_xml = dom.toprettyxml(indent="  ")
        # 将格式化后的XML写回文件
        with open(file_name, 'w') as f:
            f.write(formatted_xml)

        # 删除第一行
        # 读取XML文件内容
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 删除声明
        xml_data = xml_data.replace('<?xml version="1.0" ?>\n', '')
        # 将修改后的内容写回文件
        with open(file_name, 'w') as f:
            f.write(xml_data)



class TTFCPlanXmlGenMode:
    def __init__(self):
        self.root = ET.Element("TTFCNetwork")
        # self.root.set("xmlns", "urn:ietf:params:xml:ns:netconf:base:1.0")

    def gen_plan_xml(self,trafficClass,file_name):

        for flow in trafficClass._TTflowObjList:

            for slot_num in flow._holeIndexList:

                if slot_num <=127:
                    self.message = ET.SubElement(self.root, "message ")
                    self.message.set("dest", 'ES'+str(flow._dstNode._nodeId+1))
                    self.message.set("source",'ES'+str(flow._srcNode._nodeId+1))
                    self.message.set("slot_num", str(slot_num+1))
                    self.message.text = " "

        # 生成XML
        tree = ET.ElementTree(self.root)
        tree.write(file_name)

        # 格式化XML
        # 读取生成的XML文件
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 使用xml.dom.minidom对XML进行格式化
        dom = xml.dom.minidom.parseString(xml_data)
        formatted_xml = dom.toprettyxml(indent="  ")
        # 将格式化后的XML写回文件
        with open(file_name, 'w') as f:
            f.write(formatted_xml)

        # 删除第一行
        # 读取XML文件内容
        with open(file_name, 'r') as f:
            xml_data = f.read()
        # 删除声明
        xml_data = xml_data.replace('<?xml version="1.0" ?>\n', '')
        # 将修改后的内容写回文件
        with open(file_name, 'w') as f:
            f.write(xml_data)



# 用于解析规划结果描述XML的类
# class PlanXmlAnlsMode:


def test_gen_flow_xml():
    flow_info_list = [[23, 56, 0, 1000000, 0, 1000000, 125, 1],
                      [23, 56, 0, 1000000, 0, 1000000, 125, 1]]

    flow_xml_gen_mode = FlowXmlGenMode()
    flow_xml_gen_mode.add_flows(flow_info_list)
    flow_xml_gen_mode.gen_flow_xml("xml/flow_desc.xml")


def test_anls_flow_xml(node_list):
    flow_xml_anls_mode = FlowXmlAnlsMode("xml/flow_desc.xml", node_list)
    flow_xml_anls_mode.print_flow_list()


def test_gen_topo_xml():
    topo_xml_gen_mode = TopoXmlGenMode()

    topo_xml_gen_mode.add_node(0)
    topo_xml_gen_mode.add_node(1)
    topo_xml_gen_mode.add_node(2)
    topo_xml_gen_mode.add_node(3)

    topo_xml_gen_mode.add_link(0, 0, 1, 0)
    topo_xml_gen_mode.add_link(1, 0, 0, 0)

    topo_xml_gen_mode.add_link(0, 1, 3, 1)
    topo_xml_gen_mode.add_link(3, 1, 0, 1)

    topo_xml_gen_mode.add_link(0, 2, 2, 0)
    topo_xml_gen_mode.add_link(2, 0, 0, 2)

    topo_xml_gen_mode.add_link(1, 1, 3, 0)
    topo_xml_gen_mode.add_link(3, 0, 1, 1)

    topo_xml_gen_mode.gen_topo_xml("xml/topo_desc.xml")


def test_gen_topo_xml_2():
    topo_xml_gen_mode = TopoXmlGenMode()

    topo_xml_gen_mode.add_node(0)
    topo_xml_gen_mode.add_node(1)
    topo_xml_gen_mode.add_node(2)
    topo_xml_gen_mode.add_node(3)
    topo_xml_gen_mode.add_node(4)
    topo_xml_gen_mode.add_node(5)

    topo_xml_gen_mode.add_link(0, 0, 1, 0)
    topo_xml_gen_mode.add_link(1, 0, 0, 0)

    topo_xml_gen_mode.add_link(0, 1, 5, 1)
    topo_xml_gen_mode.add_link(5, 1, 0, 1)

    topo_xml_gen_mode.add_link(0, 2, 2, 0)
    topo_xml_gen_mode.add_link(2, 0, 0, 2)

    topo_xml_gen_mode.add_link(1, 1, 3, 1)
    topo_xml_gen_mode.add_link(3, 1, 1, 1)

    topo_xml_gen_mode.add_link(2, 1, 4, 0)
    topo_xml_gen_mode.add_link(4, 0, 2, 1)

    topo_xml_gen_mode.add_link(3, 0, 5, 0)
    topo_xml_gen_mode.add_link(5, 0, 3, 0)

    topo_xml_gen_mode.gen_topo_xml("xml/topo_desc.xml")


def test_anls_topo_xml():
    topo_xml_anls_mode = TopoXmlAnlsMode("xml/topo_desc.xml")
    topo_xml_anls_mode.print_dict_info()


def test_gen_qbv_xml():
    qbv_xml = QbvXmlGenMode()

    ports_tas = qbv_xml.add_port_tas(0, 0, 0, 0, 1, 0, 0, 2000000, 0, 0, 3, 2)
    qbv_xml.add_gate_states(ports_tas, 0, 32000003)
    qbv_xml.add_gate_states(ports_tas, 1, 32000048)

    ports_tas = qbv_xml.add_port_tas(1, 0, 0, 0, 2, 0, 0, 6000000, 0, 0, 4, 3)
    qbv_xml.add_gate_states(ports_tas, 0, 64000005)
    qbv_xml.add_gate_states(ports_tas, 1, 64000040)
    qbv_xml.add_gate_states(ports_tas, 2, 64000192)

    qbv_xml.add_update_indic(1688439339)

    qbv_xml.generate_xml("xml/qbv_recv.xml")


def main():
    # test_gen_qbv_xml()
    # test_gen_topo_xml()
    test_gen_topo_xml_2()
    # test_anls_topo_xml()
    # test_gen_flow_xml()

    sys.exit()


if __name__ == '__main__':
    main()
