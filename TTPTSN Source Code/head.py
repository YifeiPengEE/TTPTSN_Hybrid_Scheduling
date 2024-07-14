import enum
from enum import Enum
import math
CPLEX_MAX_TIME_LIMITATION = 600
CPLEX_MAX_SOLUTION_NUM = 1000
CPLEX_MAX_GAP = 0.0
INF_MINUS = -9999999
#说明1：想了下，在这里统一定义下，copy指的是流的冗余，instance指的是流在一个超周期中重复的次数；
#说明2：注意所有时间相关的单位均为纳秒！！！
CPLEX_SOLVER_TIME_LIMIT = 100
TSN_CLK = 8 #ns
Debug_enable = 1
# DEFAULT_LINK_MAX_BANDWIDTH = 1000*1024*1024/8     # bps
# DEFAULT_LINK_MAX_BANDWIDTH = 1000     # bps
DEFAULT_LINK_MAX_BANDWIDTH = 1000/8     # MBps
DEFAULT_LINK_DELAY = 0   # us
DEFAULT_PROC_DELAY = 0

DEFAULT_SW_MAX_PORTS = 0
DEFAULT_SW_FORWARD_DELAY = 0    # us
DEFAULT_ES_MAX_PORTS = 0

DEFAULT_FLOW_JITTER = 0     # us
DEFAULT_MAX_HOP = 7
TOTAL_FLOW_NUM = 10
DEFAULT_ONE_MICRIOSEC = 1000
# DEFAULT_ES_PORT_DEQUE_NUM = 1
# DEFAULT_SW_PORT_DEQUE_NUM = 8


# 节点类型枚举，简写是枚举别名，方便打印和绘图
# @enum.unique
class NodeType(Enum):
    UN = 0              # 未指定角色
    Undefined = 0       # 未指定角色
    ES = 128            # 终端系统
    EndStation = 128    # 终端系统
    SW = 4              # 交换机
    Switch = 4          # 交换机
    TTP_ES = 3          # TTP端系统


# 流优先级枚举
@enum.unique
class FlowPriority(Enum):
    Priority0 = 0   # 数值越大，优先级越高
    Priority1 = 1
    Priority2 = 2
    Priority3 = 3
    Priority4 = 4
    Priority5 = 5
    Priority6 = 6
    Priority7 = 7


# 流冗余类型枚举
@enum.unique
class RedundancyType(Enum):
    Null = 0    # 无要求


# 流分配状态枚举
@enum.unique
class AssignStatus(Enum):
    Unassigned = 0      # 未分配
    Assigning = 1       # 正在分配
    Assigned = 2        # 已分配
    Invalid = 3         #无法调度

# 协议类型
@enum.unique
class Protocol(Enum):
    TSN = 0      # TSN
    TTP = 1       # TTP

# TTP的相关参数信息
TTP_PRP = 0
TTP_PSP = 0
TTP_IDLE = 0
TTP_FRAME_MAX = 256 * 8#bits
TTP_FRAME_MIN = 10 * 8#bits
TTP_MAX_NODE = 64
TTP_CLK = 200 #ns
# TTP_Min_dur = TTP_IDLE + TTP_PRP + TTP_FRAME_MIN * TTP_CLK
# TTP_Max_dur = TTP_IDLE + TTP_PRP + TTP_FRAME_MAX * TTP_CLK
TTP_Min_dur = 19940#19940ns
TTP_Max_dur = 423940#423940
#
# # TAS队列
# class TasDeq:
#     priority: int               # 优先级
#
#
# class Port:
#     port_id: int                # 端口ID(本地)
#     port_name: string           # 端口名
#     deque_set: list[TasDeq]      # 队列
#     link: Link

#基本库
from math import *
from cplex import *

#base/目录下
from base.flowClass import *
from base.linkClass import *
from base.nodeClass import *
from base.trafficClass import *
from base.netTopoClass import *
from base.use_case_mode import *
from base.resultExportClass import *

#/networkTools目录
from networkTools.Network_eval_tools_mode import *
from networkTools.Network_op_tools_mode import *
from networkTools.Network_draw_tools_mode import *
from networkTools.debugToolClass import *
from networkTools.networkCaluculusToolsClass import *
from networkTools.trafficGeneratorToolClass import *

#/ILP Tools
from ILPTool.tsnLpTool import *



#/tsnSchedTools目录
from tsnSchedTools.ilpbasedMultiperiodFlowRSClass import *
from tsnSchedTools.nwpspSchedMethod import *
from tsnSchedTools.OrrTsnSchedMethod import *
from tsnSchedTools.tsnMultiRouteILPSchedMethod import *
from tsnSchedTools.tsnRecurSchedMethod import *
from tsnSchedTools.tsnStpRecurSched import *
from tsnSchedTools.enhanceSchedAndThroughputSchedMethod import *


#/ttptsn
from ttptsn.ttpSchedToolClass import *

#/XMLGen目录
from XMLGen.TlvProcMode import *
from XMLGen.XmlProcMode import *
from XMLGen.GenXml import *
