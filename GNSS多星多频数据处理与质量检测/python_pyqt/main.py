import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from GNSS_main import Ui_MainWindow
import sys
import math
from myclass import CData,CSat
from utils import detect_jump_single,detect_jump_dual_1,detect_jump_dual_MW,detect_jump_triple,list2str
from utils import computeCMC_diff
from utils import get_denoise_dis



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connectAction()
        self.sat_dict = {}
        self.satKey_list = []
        self.result = f''
        # 存储关键参数（频率、波长、阈值等）
        self.params = {
            'f': {'L1': 1575.42e6, 'L2': 1227.60e6, 'L5': 1176.45e6},  # 频率（Hz）
            'lambda': {'L1': 0.1903, 'L2': 0.2442, 'L5': 0.2548},  # 波长（米）
            'c': 299792458,  # 光速（米/秒）
            'threshold': {
                'single': 0.3,  # 单频L1周跳阈值（3σ）
                'dual': 0.5,  # 双频方法阈值
                'triple': 0.5  # 三频TG-IF组合阈值
            },
            'lambda_w': 0.86  # 宽巷波长（米）
        }

    def connectAction(self):
        self.actionopen.triggered.connect(self.openFile)
        self.actiondetect.triggered.connect(self.detect_jump)
        self.actionestimateErr.triggered.connect(self.estimateErr)
        self.actionhatchDenoise.triggered.connect(self.hatchDenoise)
        self.actionsave.triggered.connect(self.saveFile)

    def openFile(self):
        path,_ = QFileDialog.getOpenFileName(self, '读取数据','*.txt')
        if path:
            with open(path,'r') as f:
                line = f.readline() #UTC Time, PRN, L1_Pseudo(m), L2_Pseudo(m), L5_Pseudo(m), L1_Phase(cycle), L2_Phase(cycle), L5_Phase(cycle)
                line = f.readline()
                while line:
                    data = CData.fromstr(line)
                    if data.prn not in self.sat_dict:
                        self.sat_dict[data.prn] = CSat(data.prn)
                        self.satKey_list.append(data.prn)
                    self.sat_dict[data.prn].addData(data)
                    line = f.readline()
            QMessageBox.information(self,' ',f'读取数据完成 总计{len(self.satKey_list)}颗卫星')

    def detect_jump(self):
        if len(self.satKey_list)==0:
            QMessageBox.information(self,'提示','请先读取数据')
            return
        text = f'周跳探测结果(True->存在周跳 False->未探测到周跳)\n'
        for key in self.satKey_list:
            sat:CSat = self.sat_dict[key]
            #单频周跳探测
            isJump_list_single = detect_jump_single(sat, self.params, threshold=self.params['threshold']['single'])
            text+=f'{sat.SatName}单频周跳探测:\n'
            text+=list2str(isJump_list_single)
            #双频周跳探测
            isJump_list_dual_1 = detect_jump_dual_1(sat, self.params, threshold=self.params['threshold']['dual'])
            text+=f'{sat.SatName}双频周跳探测(电离层残差法):\n'
            text+=list2str(isJump_list_dual_1)
            isJump_list_dual_MW = detect_jump_dual_MW(sat, self.params, threshold=self.params['threshold']['dual'])
            text += f'{sat.SatName}双频周跳探测(MW组合):\n'
            text += list2str(isJump_list_dual_MW)
            #三频周跳探测
            isJump_list_triple = detect_jump_triple(sat, self.params, threshold=self.params['threshold']['triple'])
            text += f'{sat.SatName}三频周跳探测:\n'
            text += list2str(isJump_list_triple)
        self.result+=text
        self.textBrowser.setText(text)

    def estimateErr(self):
        if len(self.satKey_list)==0:
            QMessageBox.information(self,'提示','请先读取数据')
            return
        # 计算标准差
        def calc_std(data):
            n = len(data)
            mean = sum(data) / n
            var = sum((x - mean)**2 for x in data) / n
            return math.sqrt(var)
        # 时间差分 计算每个卫星的CMC差值标准差 作为多路径误差估计值
        # 使用L1计算CMC
        text = f''
        for key in self.satKey_list:
            sat:CSat = self.sat_dict[key]
            CMC_diff_list = computeCMC_diff(sat,self.params)
            sigma = calc_std(CMC_diff_list)
            text += f'{sat.SatName}多路径误差估计值:{sigma}\n'
        self.result+=text
        self.textBrowser.setText(text)

    def hatchDenoise(self):
        if len(self.satKey_list)==0:
            QMessageBox.information(self,'提示','请先读取数据')
            return
        text = f''
        for key in self.satKey_list:
            text+=f'{key}伪距平滑：\n'
            sat:CSat = self.sat_dict[key]
            dis_dict = get_denoise_dis(sat,self.params)
            text+='L1伪距平滑结果：\n'
            for item in dis_dict['L1']:
                text += f"{item['time']}:{item['dis']}\n"
            text+='L2伪距平滑结果：\n'
            for item in dis_dict['L2']:
                text += f"{item['time']}:{item['dis']}\n"
            text+='L5伪距平滑结果：\n'
            for item in dis_dict['L5']:
                text += f"{item['time']}:{item['dis']}\n"
        self.result+=text
        self.textBrowser.setText(text)

    def saveFile(self):
        #path,_ = QFileDialog.getSaveFileName(self, '<UNK>','*.txt')
        path = r'./result.txt'
        with open(path,'w',encoding='utf-8') as f:
            f.write(self.result)
        QMessageBox.information(self,'提示','保存结果完成')



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()