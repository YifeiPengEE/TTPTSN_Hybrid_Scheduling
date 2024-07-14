from head import *
import random



class ttpSchedToolClass:
    def __init__(self):
        print('ttpSchedToolClass')

    #按周期排序：trafficClass._flowObjList = sorted(trafficClass._flowObjList, key=lambda x: x._period)
    #按flowId排序：trafficClass._flowObjList = sorted(trafficClass._flowId, key=lambda x: x._period)
    #说明，在计算tsn->TTP延时的时候，为了结果更具有一般性，应该让结果按照flowId排序
    def vNodeSlotCreate(self,trafficClass):
        trafficClass._flowObjList = sorted(trafficClass._flowObjList, key=lambda x: x._period)
        cnt = 0
        lastPeriod = 0
        lastVnodeName = 'vNode'+str(cnt)
        for flow in trafficClass._flowObjList:
             if lastPeriod == flow._period:
                 insNum = int(flow._period / trafficClass._gcd)
                 if trafficClass._vNodeSet.get(lastVnodeName) == None:
                     trafficClass._vNodeSet[lastVnodeName] = [flow]
                 else:
                     if len(trafficClass._vNodeSet[lastVnodeName]) < insNum:
                         trafficClass._vNodeSet[lastVnodeName].append(flow)
                     elif len(trafficClass._vNodeSet[lastVnodeName]) == insNum:
                         cnt = cnt + 1
                         lastVnodeName = 'vNode'+str(cnt)
                         trafficClass._vNodeSet[lastVnodeName] = [flow]
             else:
                 lastPeriod = flow._period
                 cnt = cnt + 1
                 lastVnodeName = 'vNode' + str(cnt)
                 trafficClass._vNodeSet[lastVnodeName] = [flow]

        for key, value in trafficClass._vNodeSet.items():
            print(key)
            for flow in value:
                print('flowId = ',flow._flowId,'flowPeriod = ',flow._period)






    def schedMethod(self,trafficClass,UnionFlag,TTPTDMADur):
        slotDur = int(TTPTDMADur / len(trafficClass._flowObjList))
        delta = TTPTDMADur - slotDur * len(trafficClass._flowObjList)
        print('delta = ',delta)
        if UnionFlag == False:
            startPit = random.randint(0,trafficClass._hyperPeriod)
            for flow in trafficClass._flowObjList:
                tmpQbvWin = [startPit, startPit + slotDur]
                flow._startOffset = startPit
                flow._assignQbv.append(tmpQbvWin)
                flow._assignQbvDetail.append(tmpQbvWin)
                startPit += slotDur



        else:
            startPit = 0
            for flow in trafficClass._flowObjList:
                tmpQbvWin = [startPit, startPit + flow._flowDur]
                flow._startOffset = startPit
                flow._assignQbv.append(tmpQbvWin)
                flow._assignQbvDetail.append(tmpQbvWin)
                startPit += slotDur

        trafficClass._flowObjList[-1]._assignQbv[-1][1] = trafficClass._flowObjList[-1]._assignQbv[-1][1] + delta






    #该函数完成时隙分配
    def assignTimeSlot(self,trafficClass,tsnWinList,TTPTDMADur,flag=False):
        trafficClass._netGateFlowIdList = []
        flowNum = trafficClass._flowNum
        slotDur = TTPTDMADur / trafficClass._flowNum
        insNum = int(trafficClass._hyperPeriod/TTPTDMADur)
        print('slotDur = ',slotDur,'flowNum = ',flowNum)
        if flag == False:
            trafficClass._netGateFlowIdList.append(trafficClass._flowObjList[flowNum-4]._flowId)
            trafficClass._netGateFlowIdList.append(trafficClass._flowObjList[flowNum - 3]._flowId)
            trafficClass._netGateFlowIdList.append(trafficClass._flowObjList[flowNum - 2]._flowId)
            trafficClass._netGateFlowIdList.append(trafficClass._flowObjList[flowNum - 1]._flowId)

            return trafficClass
        else:
            bitCnt = 0
            index = 0
            for win in tsnWinList:
                bitNum = int((win[1]-win[0]))
                bitCnt += bitNum
                print('bitCnt = ',bitCnt)
                if bitCnt >= 200 * 8 :
                    index = int(win[1]/slotDur)
                    index = int(index/insNum)
                    bitCnt -= 200 * 8
                    if index == flowNum - 1:
                        trafficClass._netGateFlowIdList.append(0)
                    else:
                        trafficClass._netGateFlowIdList.append(index)

            trafficClass._netGateFlowIdList.append(flowNum-1)
            if len(trafficClass._netGateFlowIdList) == 1:
                trafficClass._netGateFlowIdList.append(0)

            print('sss trafficClass._netGateFlowIdList = ',trafficClass._netGateFlowIdList)
            tmp = trafficClass._netGateFlowIdList
            trafficClass._netGateFlowIdList = list(set(tmp))
            trafficClass._netGateFlowIdList.sort()
            print('sss trafficClass._netGateFlowIdList = ', trafficClass._netGateFlowIdList)


            while len(trafficClass._netGateFlowIdList) != 4:
                #查找欧式距离最远的点
                tempMins = []
                for i in range(len(trafficClass._netGateFlowIdList)):
                    if i==len(trafficClass._netGateFlowIdList)-1:
                        break
                    a = trafficClass._netGateFlowIdList[i]
                    b = trafficClass._netGateFlowIdList[i+1]
                    tempMins.append(b - a)
                tempMinsMax = copy.deepcopy(tempMins)
                MaxValue = max(tempMinsMax)
                MaxValueIdex = tempMins.index(MaxValue)
                MaxValue = int(MaxValue/2)+1
                a = trafficClass._netGateFlowIdList[MaxValueIdex]
                b = trafficClass._netGateFlowIdList[MaxValueIdex+1]
                if a + MaxValue != b:
                    a += MaxValue
                else:
                    a += (MaxValue - 1)
                trafficClass._netGateFlowIdList.insert(MaxValueIdex+1,a)






            return trafficClass



