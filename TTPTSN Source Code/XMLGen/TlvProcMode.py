
FILE_PATH_TLV = 10
UL_HEAD_TOPO_TLV = 18
PLAN_HEAD_REQ_TLV = 28
PLAN_HEAD_RESP_TLV = 29


class Tlv:
    def __init__(self, type=0, length=0, info_string=''):
        self.type = type
        self.length = length
        self.info_string = info_string


class TlvProcMode:
    def __init__(self):
        return

    @staticmethod
    def get_tlv_from_data(data):
        tlv = Tlv()
        tlv.type = int.from_bytes(data[0:1], byteorder='little')
        tlv.length = int.from_bytes(data[1:3], byteorder='little')
        tlv.info_string = data[3:(3 + tlv.length)]
        return tlv

    @staticmethod
    def decode_plan_req_tlv(data):
        if int.from_bytes(data[0:1], byteorder='little') != PLAN_HEAD_REQ_TLV:
            print("Error in plan_head_req_tlv")
            return '', ''
        plan_head_req_tlv = TlvProcMode.get_tlv_from_data(data)
        data = data[1 + 2 + plan_head_req_tlv.length:]

        # print(f"plan_head_req_tlv.type={plan_head_req_tlv.type}, "
        #       f"plan_head_req_tlv.length={plan_head_req_tlv.length}, "
        #       f"plan_head_req_tlv.info_string={plan_head_req_tlv.info_string.decode()}")

        if int.from_bytes(data[0:1], byteorder='little') != FILE_PATH_TLV:
            print("Error in file_path_tlv of topo")
            return '', ''
        topo_file_tlv = TlvProcMode.get_tlv_from_data(data)
        topo_file_path = topo_file_tlv.info_string.decode()
        data = data[1 + 2 + topo_file_tlv.length:]

        # print(f"topo_file_tlv.type={topo_file_tlv.type}, "
        #       f"topo_file_tlv.length={topo_file_tlv.length}, "
        #       f"topo_file_tlv.info_string={topo_file_tlv.info_string.decode()}")

        if int.from_bytes(data[0:1], byteorder='little') != FILE_PATH_TLV:
            print("Error in file_path_tlv of flow")
            return topo_file_path, ''
        flow_file_tlv = TlvProcMode.get_tlv_from_data(data)
        flow_file_path = flow_file_tlv.info_string.decode()
        data = data[1 + 2 + flow_file_tlv.length:]

        # print(f"flow_file_tlv.type={flow_file_tlv.type}, "
        #       f"flow_file_tlv.length={flow_file_tlv.length}, "
        #       f"flow_file_tlv.info_string={flow_file_tlv.info_string.decode()}")

        return topo_file_path, flow_file_path

    @staticmethod
    def create_end_tlv():
        end_tlv = Tlv(0, 0)
        return end_tlv

    @staticmethod
    def create_plan_resp_tlv(plan_xml_path):
        plan_head_resp_tlv = Tlv(PLAN_HEAD_RESP_TLV, 4, "resp")
        plan_file_path_tlv = Tlv(FILE_PATH_TLV, len(plan_xml_path), plan_xml_path)
        end_tlv = TlvProcMode.create_end_tlv()

        packet = b''

        packet += plan_head_resp_tlv.type.to_bytes(1, byteorder='little')
        packet += plan_head_resp_tlv.length.to_bytes(2, byteorder='little')
        packet += plan_head_resp_tlv.info_string.encode()

        packet += plan_file_path_tlv.type.to_bytes(1, byteorder='little')
        packet += plan_file_path_tlv.length.to_bytes(2, byteorder='little')
        packet += plan_file_path_tlv.info_string.encode()

        packet += end_tlv.type.to_bytes(1, byteorder='little')
        packet += end_tlv.length.to_bytes(2, byteorder='little')
        packet += end_tlv.info_string.encode()

        return packet
