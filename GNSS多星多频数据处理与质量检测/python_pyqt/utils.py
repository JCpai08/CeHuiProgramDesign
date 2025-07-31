from myclass import CSat,CData

def list2str(result_list):
    """
    将周跳探测结果列表转化为字符串
    :param result_list:
    :return:
    """
    return '\n'.join([f"{item['time']}:{item['isJump']}" for item in result_list])+'\n'

def detect_jump_single(sat:CSat,params,threshold=0.3):
    """
    单频周跳探测
    :param sat: 待探测的单星对象数据
    :param params: 常量参数
    :param threshold: 周跳检测值阈值 单位(周) 假设噪声标准差0.1周 3*sigma=0.3
    :return: dict list length=历元数量-1
    """
    data_list = sat.data_list
    isJump_list = []
    for i in range(1,len(data_list)):
        curr:CData = data_list[i]
        prev:CData = data_list[i-1]
        dPhi = curr.L1_Phase - prev.L1_Phase
        dP = curr.L1_Pseudo - prev.L1_Pseudo
        #计算周跳检测值
        output = dPhi - params['lambda']['L1'] / params['c'] * dP
        isJump_list.append({
            'time':f'{prev.time}->{curr.time}',
            'isJump':False if output < threshold else True
             })
    return isJump_list

def detect_jump_dual_1(sat:CSat,params,threshold=0.5):
    """
    双频周跳探测 电离层残差法
    :param sat: 待探测的单星对象数据
    :param params: 常量参数
    :param threshold: 周跳检测值阈值 单位(周)
    :return: dict list length=历元数量-1
    """
    data_list = sat.data_list
    isJump_list = []
    for i in range(1,len(data_list)):
        curr:CData = data_list[i]
        prev:CData = data_list[i-1]
        dPhi1 = curr.L1_Phase - prev.L1_Phase
        dPhi2 = curr.L2_Phase - prev.L2_Phase
        #计算周跳检测值
        output = dPhi1 - params['f']['L1'] / params['f']['L2'] * dPhi2
        isJump_list.append({
            'time':f'{prev.time}->{curr.time}',
            'isJump':False if output < threshold else True
             })
    return isJump_list

def detect_jump_dual_MW(sat:CSat,params,threshold=0.5):
    """
    双频周跳探测 使用MW组合
    :param sat: 待探测的单星对象数据
    :param params: 常量参数
    :param threshold: 周跳检测值阈值
    :return: dict list length=历元数量-1
    """
    data_list = sat.data_list
    isJump_list = []
    f1,f2,lambda_w = params['f']['L1'],params['f']['L2'],params['lambda_w']
    for i in range(1,len(data_list)):
        curr:CData = data_list[i]
        prev:CData = data_list[i-1]
        Nw_curr = curr.L1_Phase - curr.L2_Phase - (f1*curr.L1_Pseudo+f2*curr.L2_Pseudo) / ((f1+f2)*lambda_w)
        Nw_prev = prev.L1_Phase - prev.L2_Phase - (f1*prev.L1_Pseudo+f2*prev.L2_Pseudo) / ((f1+f2)*lambda_w)
        #计算周跳检测值
        output = Nw_curr - Nw_prev
        isJump_list.append({
            'time':f'{prev.time}->{curr.time}',
            'isJump':False if output < threshold else True
             })
    return isJump_list

def detect_jump_triple(sat:CSat,params,threshold=0.5):
    """
    三频周跳探测 
    :param sat: 待探测的单星对象数据
    :param params: 常量参数
    :param threshold: 周跳检测值阈值
    :return: dict list length=历元数量-1
    """
    data_list = sat.data_list
    isJump_list = []
    f1,f2,f5 = params['f']['L1'],params['f']['L2'],params['f']['L5']
    for i in range(1,len(data_list)):
        curr:CData = data_list[i]
        prev:CData = data_list[i-1]
        Lif_curr = (f1*curr.L1_Phase - f2*curr.L2_Phase + f5*curr.L5_Phase) / (f1-f2+f5)
        Lif_prev = (f1 * prev.L1_Phase - f2 * prev.L2_Phase + f5 * prev.L5_Phase) / (f1 - f2 + f5)
        #计算周跳检测值
        output = Lif_curr - Lif_prev
        isJump_list.append({
            'time':f'{prev.time}->{curr.time}',
            'isJump':False if output < threshold else True
             })
    return isJump_list

def computeCMC(dis_pseudo,phase,lam):
    """
    计算伪距减载波CMC
    :param dis_pseudo:伪距
    :param phase:载波相位(单位：周)
    :param lam:载波波长
    :return:CMC float
    """
    return dis_pseudo - phase * lam

def computeCMC_diff(sat:CSat,params):
    """
    时间差分 计算卫星的所有历元CMC差值
    使用L1计算CMC
    :param sat: 需要进行误差估计的单星对象数据
    :param params: 常量参数
    :return: list
    """
    data_list = sat.data_list
    CMC_diff_list = []
    for i in range(1,len(data_list)):
        curr:CData = data_list[i]
        prev:CData = data_list[i-1]
        curr_CMC = computeCMC(curr.L1_Pseudo,curr.L1_Phase,params['lambda']['L1'])
        prev_CMC = computeCMC(prev.L1_Pseudo, prev.L1_Phase, params['lambda']['L1'])
        CMC_diff_list.append(curr_CMC - prev_CMC)
    return CMC_diff_list

def get_denoise_dis(sat:CSat,params):
    """
    通过hatch滤波平滑伪距
    :param sat: 需要进行误差估计的单星对象数据
    :param params: 常量参数
    :return: dict
    """
    data_list = sat.data_list
    n = len(data_list)
    dis = {
        'L1':[{'time':data_list[0].time,'dis': data_list[0].L1_Pseudo}], # 初始化平滑后的伪距列表 Ps(1) = P(1)
        'L2':[{'time':data_list[0].time,'dis': data_list[0].L2_Pseudo}],
        'L5':[{'time':data_list[0].time,'dis': data_list[0].L5_Pseudo}]
    }
    for i in range(2, n + 1):  # 历元2-n
        curr: CData = data_list[i - 1]
        prev: CData = data_list[i - 2]
        weight_i = 1 / i
        curr_time = curr.time
        prev_time = prev.time
        # L1频段伪距滤波
        P_i = curr.L1_Pseudo
        dPhase = curr.L1_Phase - prev.L1_Phase
        lam = params['lambda']['L1']
        Ps_i = weight_i * P_i + (1 - weight_i) * (dis['L1'][i - 2]['dis'] + dPhase * lam)
        dis['L1'].append({'time':curr_time,'dis':Ps_i})
        # L2频段伪距滤波
        P_i = curr.L2_Pseudo
        dPhase = curr.L2_Phase - prev.L2_Phase
        lam = params['lambda']['L2']
        Ps_i = weight_i * P_i + (1 - weight_i) * (dis['L2'][i - 2]['dis'] + dPhase * lam)
        dis['L2'].append({'time':curr_time,'dis':Ps_i})
        # L5频段伪距滤波
        P_i = curr.L5_Pseudo
        dPhase = curr.L5_Phase - prev.L5_Phase
        lam = params['lambda']['L5']
        Ps_i = weight_i * P_i + (1 - weight_i) * (dis['L5'][i - 2]['dis'] + dPhase * lam)
        dis['L5'].append({'time':curr_time,'dis':Ps_i})
    return dis
