class CData:
    '''
    每一行数据对应一个CData对象
    '''
    def __init__(self, time:str, prn:str,L1_Pseudo,L2_Pseudo,L5_Pseudo,L1_Phase,L2_Phase,L5_Phase):
        self.time = time
        self.prn = prn
        self.L1_Pseudo = L1_Pseudo
        self.L2_Pseudo = L2_Pseudo
        self.L5_Pseudo = L5_Pseudo
        self.L1_Phase = L1_Phase
        self.L2_Phase = L2_Phase
        self.L5_Phase = L5_Phase

    @classmethod
    def fromstr(cls,data:str):
        # UTC Time, PRN, L1_Pseudo(m), L2_Pseudo(m), L5_Pseudo(m), L1_Phase(cycle), L2_Phase(cycle), L5_Phase(cycle)
        l = data.split(',')
        return cls(l[0],l[1],float(l[2]),float(l[3]),float(l[4]),float(l[5]),float(l[6]),float(l[7]))

class CSat:
    '''
    存储一个卫星的所有历元数据
    data_list按照历元顺序存储
    '''
    def __init__(self,SatName:str):
        self.SatName = SatName
        self.data_list = []

    def addData(self,data:CData):
        self.data_list.append(data)
        self.data_list.sort(key=lambda x:x.time)


