import os
import pandas as pd
import numpy as np
#啊，这个类就用来到处各种各样的结果吧

class resultExportClass :
    def __init__(self):
        print('resultExportClass')

    # 解析数据并创建DataFrame
    def parse_txt_file(self,filepath,testName):
        topology = filepath.split(testName)[-1].split('flowNum')[0]

        flow = filepath.split('flowNum')[-1].replace('.txt', '')
        with open(filepath, 'r') as file:
            lines = file.readlines()

        data = {}
        for line in lines:
            if "=" in line:
                key, value = line.split('=')
                data[key.strip()] = list(map(float, value.strip().strip(',').split(',')))

        return topology, flow, data


    def exportRouteMessage(self):
        # 创建一个空的DataFrame
        columns = pd.MultiIndex.from_product([['Our', 'ILP2021', 'NWPSP2016', 'ORR2022'], ['100', '200', '300', '400', '500']],
                                             names=['Algorithm', 'Flow'])
        index = pd.MultiIndex.from_product(
            [['swNum4esNum8', 'swNum8esNum16', 'swNum16esNum32'],
             ['flowCase_evalBdLinkavgList', 'flowCase_evalBdLinkmaxList', 'flowCase_evalRoutelenFlowavgList',
                'flowCase_evalRoutelenFlowmaxList',
                'flowCase_evalArlfLinkavgList', 'flowCase_evalArlfLinkmaxList', 'flowCase_evalArdfNodeavgList',
                'flowCase_evalArdfNodemaxList']
             ],
             names=['Topology', 'Metric']
        )
        df = pd.DataFrame(index=index, columns=columns, dtype=np.float64)

        # 映射拓扑名到Excel表中的行标签
        topology_mapping = {
            'swNum4esNum8': 'swNum4esNum8',
            'swNum8esNum16': 'swNum8esNum16',
            'swNum16esNum32': 'swNum16esNum32'
        }
        algNameList = ['Our', 'ILP2021', 'NWPSP2016', 'ORR2022']
        # 处理每个文件并更新DataFrame
        testName = 'routeResult'
        folder_path = '../ttptsn/output/routeResult/'  # 指定文件夹路径
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            if file_name.endswith('.txt'):
                filepath = os.path.join(folder_path, file_name)
                topology, flow, data = self.parse_txt_file(filepath,testName)
                for key, values in data.items():
                    for i, alg_value in enumerate(values):
                        df.loc[(topology_mapping[topology], key), (algNameList[i], flow)] = alg_value

        # 保存为Excel文件
        with pd.ExcelWriter('../output/result/'+testName+'Output.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer)

        print("Excel文件已保存!")

    def exportbgNumMessage(self,testName,statisticVarName):
        # 创建一个空的DataFrame
        columns = pd.MultiIndex.from_product([['Our', 'ILP2021', 'NWPSP2016', 'ORR2022'], ['100', '200', '300', '400', '500']],
                                             names=['Algorithm', 'Flow'])
        index = pd.MultiIndex.from_product(
            [['swNum4esNum8', 'swNum8esNum16', 'swNum16esNum32'],
             [statisticVarName]
             ],
             names=['Topology', 'Metric']
        )
        df = pd.DataFrame(index=index, columns=columns, dtype=np.float64)

        # 映射拓扑名到Excel表中的行标签
        topology_mapping = {
            'swNum4esNum8': 'swNum4esNum8',
            'swNum8esNum16': 'swNum8esNum16',
            'swNum16esNum32': 'swNum16esNum32'
        }
        algNameList = ['Our', 'ILP2021', 'NWPSP2016', 'ORR2022']
        # 处理每个文件并更新DataFrame
        folder_path = '../ttptsn/output/'+testName+'/'  # 指定文件夹路径
        file_list = os.listdir(folder_path)
        for file_name in file_list:
            if file_name.endswith('.txt'):
                filepath = os.path.join(folder_path, file_name)
                topology, flow, data = self.parse_txt_file(filepath,testName)
                for key, values in data.items():
                    for i, alg_value in enumerate(values):
                        df.loc[(topology_mapping[topology], key), (algNameList[i], flow)] = alg_value

        # 保存为Excel文件
        with pd.ExcelWriter('../output/result/'+testName+'Output.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer)

        print("Excel文件已保存!")

if __name__ == '__main__':
    # main2()
    resultExportTool = resultExportClass()


    #导出路由结果
    resultExportTool.exportRouteMessage()
    #导出保护带结果
    resultExportTool.exportbgNumMessage('bgResult','flowCase_evalBgNum')
    #可调度性
    resultExportTool.exportbgNumMessage('schedableRatioResult', 'flowCase_evalSchedable')
    #求解时间
    resultExportTool.exportbgNumMessage('timeResult', 'flowCase_evalRuningTime')