import matplotlib.pyplot as plt
import sys
import networkx as nx
import numpy as np
class NetworkDrawTools:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        plt.figure()

    def networkTopoPlot(self, adjmtix,esNum,swNum):
        # Example adjacency matrix
        adj_matrix = np.array(adjmtix)

        # Create a graph from the adjacency matrix
        G = nx.from_numpy_matrix(adj_matrix)

        # Create a dictionary to map node indices to device IDs
        # device_ids = {i: f'Device {i}' for i in range(len(adjmtix))}
        device_ids = {}
        for i in range(len(adjmtix)) :
            if i < swNum:
                device_ids[i] = f'Switch {i}'
            else:
                device_ids[i] = f'Es {i-swNum}'

        # Draw the network graph
        pos = nx.spring_layout(G)  # Position nodes using a spring layout
        nx.draw(G, pos, with_labels=False, node_size=500, node_color='skyblue')

        # Add labels to nodes
        labels = {node: device_ids[node] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)

        plt.show()
    def network_topo_plot(self, adjmtix):
        # Example adjacency matrix
        adj_matrix = np.array(adjmtix)

        # Create a graph from the adjacency matrix
        G = nx.from_numpy_matrix(adj_matrix)

        # Create a dictionary to map node indices to device IDs
        device_ids = {i: f'Device {i}' for i in range(len(adjmtix))}

        # Draw the network graph
        pos = nx.spring_layout(G)  # Position nodes using a spring layout
        nx.draw(G, pos, with_labels=False, node_size=500, node_color='skyblue')

        # Add labels to nodes
        labels = {node: device_ids[node] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)

        plt.show()

    def draw_runtime(self, flowNumList, solutionTimeList):
        plt.subplot(self.row, self.col, 1)
        plt.xlabel("flow num")
        plt.ylabel("runtime")
        plt.title("runtime")
        plt.plot(flowNumList, solutionTimeList)

        plt.tight_layout()
        plt.show()

    def draw_sche_ratio(self, flowNumList, scheRatioList):
        plt.subplot(self.row, self.col, 2)
        plt.xlabel("flow num")
        plt.ylabel("success num/flow num")
        plt.title("success ratio")
        plt.plot(flowNumList, scheRatioList)

    def draw_link_max_load(self, flowNumList, linkMaxLoad):
        plt.subplot(self.row, self.col, 3)
        plt.xlabel("flow num")
        plt.ylabel("max load")
        plt.title("max load")
        plt.plot(flowNumList, linkMaxLoad)

    def draw_link_max_load(self, flowNumList, linkUsedRatio):
        plt.subplot(self.row, self.col, 4)
        plt.xlabel("flow num")
        plt.ylabel("link used ratio")
        plt.title("used link num/link num")
        plt.plot(flowNumList, linkUsedRatio)

        plt.tight_layout()
        plt.show()

    def do_eval(self):
        print("----------------------------------------------------------------------------")
        print(self.__class__.__name__ + "::" + sys._getframe().f_code.co_name + "()")
        print("flowNumList=", end='')
        print(self.flowNumList)
        print("solutionTimeList=", end='')
        print(self.solutionTimeList)
        print("scheRatioList=", end='')
        print(self.scheRatioList)
        print("linkMaxLoad=", end='')
        print(self.linkMaxLoad)
        print("linkUsedRatio=", end='')
        print(self.linkUsedRatio)

        if (len(self.flowNumList) == len(self.solutionTimeList)
            and len(self.flowNumList) == len(self.scheRatioList)
            and len(self.flowNumList) == len(self.linkMaxLoad)
            and len(self.flowNumList) == len(self.linkUsedRatio)):
                self.show_eval_result()
        else:
            print("Incorrect length of list.")
