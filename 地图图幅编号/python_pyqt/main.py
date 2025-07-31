# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from map_main import Ui_MainWindow
import sys
from myclass import CAngle, CLoc


# noinspection SpellCheckingInspection
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.connectAction()
        self.loc_list = []
        self.code_list = []
        self.pAvg = None
        self.result = f''
        self.scale_dict = {
            '1000000':{'dl':CAngle(6,0,0),'db':CAngle(4,0,0),'scale_code':'B'},
            '500000': {'dl': CAngle(3, 0, 0), 'db': CAngle(2, 0, 0),'scale_code':'B'},
            '250000': {'dl': CAngle(1, 30, 0), 'db': CAngle(1, 0, 0),'scale_code':'C'},
            '100000': {'dl': CAngle(0, 30, 0), 'db': CAngle(0, 20, 0),'scale_code':'D'},
            '50000': {'dl': CAngle(0, 15, 0), 'db': CAngle(0, 10, 0),'scale_code':'E'},
            '25000': {'dl': CAngle(0, 7, 30), 'db': CAngle(0, 5, 0),'scale_code':'F'},
            '10000': {'dl': CAngle(0, 3, 45), 'db': CAngle(0, 2, 30),'scale_code':'G'},
            '5000': {'dl': CAngle(0, 1, 52.5), 'db': CAngle(0, 1, 15),'scale_code':'H'},
            '2000': {'dl': CAngle(0, 0, 37.5), 'db': CAngle(0, 0, 25),'scale_code':'I'},
            '1000': {'dl': CAngle(0, 0, 18.75), 'db': CAngle(0, 0, 12.5),'scale_code':'J'},
            '500': {'dl': CAngle(0, 0, 9.375), 'db': CAngle(0, 0, 6.25),'scale_code':'K'},
        }
        self.code_scale_dict = {'B':'500000','C':'250000','D':'100000',
                               'E':'50000','F':'25000','G':'10000',
                               'H':'5000','I':'2000','J':'1000','K':'500'}

    def connectAction(self):
        self.actionopenbl.triggered.connect(self.openbl)
        self.actionopencode.triggered.connect(self.opencode)
        self.actionencode.triggered.connect(self.encode)
        self.actiondecode.triggered.connect(self.decode)
        self.actionsave.triggered.connect(self.save)

    def openbl(self):
        path,_ = QFileDialog.getOpenFileName(self, "读取经纬度", "./", "*.txt")
        if path:
            with open(path,"r",encoding="utf-8") as f:
                line = f.readline()
                while line:
                    name,sb,sl = line.split(',')
                    self.loc_list.append(CLoc(name,CAngle.fromStr(sb),CAngle.fromStr(sl)))
                    line = f.readline()
            b_sumSec = sum([loc.b.toSecond() for loc in self.loc_list])
            l_sumSec = sum([loc.l.toSecond() for loc in self.loc_list])
            n = len(self.loc_list)
            self.pAvg = CLoc('Pavg',CAngle.fromSecond(b_sumSec/n),CAngle.fromSecond(l_sumSec/n))
            text = f''
            text += f'P1点的经度（单位：dd.mmss）:{self.loc_list[0].l.format_ddmmss()}\n'
            text += f'P3点的纬度（单位：dd.mmss）:{self.loc_list[2].b.format_ddmmss()}\n'
            text += f'P3点的经度（单位：度）:{self.loc_list[2].l.toDegree():.6f}\n'
            text += f'P3点的纬度（单位：度）:{self.loc_list[2].b.toDegree():.6f}\n'
            text += f'Pavg点的经度（单位：dd.mmss）:{self.pAvg.l.format_ddmmss()}\n'
            text += f'Pavg点的纬度（单位：dd.mmss）:{self.pAvg.b.format_ddmmss()}\n'
            text += f'P3点的纬度（单位：度）:{self.pAvg.b.toDegree():.6f}\n'
            text += f'P3点的经度（单位：度）:{self.pAvg.l.toDegree():.6f}\n'
            self.textBrowser.setText(text)
            self.result+=text
            self.statusbar.setStatusTip('读取经纬度完成！')

    def encode(self):
        if self.pAvg is None:
            QMessageBox.information(self, "错误", "请先读入经纬度")
            return
        text = f''
        #1：100万图幅编号计算
        B = self.pAvg.b
        L = self.pAvg.l
        db100w = self.scale_dict['1000000']['db']
        dl100w = self.scale_dict['1000000']['dl']
        # a = int(B // db100w+1)
        # b = int(L // dl100w+31)
        # row_letter = chr(a+64)
        #1:25万图幅行列号计算
        db25w = self.scale_dict['250000']['db']
        dl25w = self.scale_dict['250000']['dl']
        c = int(db100w//db25w - B % db100w // db25w)
        d = int(L % dl100w // dl25w + 1)
        text+=f'Pavg点的1：25万图幅行号:{c}\n'
        text+=f'Pavg点的1：25万图幅列号:{d}\n'
        #1:500图幅行列号计算
        db500 = self.scale_dict['500']['db']
        dl500 = self.scale_dict['500']['dl']
        c = int(db100w//db500 - B % db100w // db500)
        d = int(L % dl100w // dl500 + 1)
        text+=f'Pavg点的1：500图幅行号:{c}\n'
        text+=f'Pavg点的1：500图幅列号:{d}\n'
        self.textBrowser.setText(text)
        self.result+=text

    def opencode(self):
        path, _ = QFileDialog.getOpenFileName(self, "读取图幅号文件", "./", "*.txt")
        if path:
            text = f''
            with open(path, "r", encoding="utf-8") as f:
                line = f.readline()
                while line:
                    _,code = line.split(',')
                    self.code_list.append(code)
                    line = f.readline()
            QMessageBox.information(self, " ", f"读取图幅号文件完成 共{len(self.code_list)}条数据")

    def decode(self):
        if len(self.code_list) == 0:
            QMessageBox.information(self, " ", "请先读取图幅号数据")
            return
        text = f''
        for idx, code in enumerate(self.code_list):
            row_letter = code[0]
            a = ord(row_letter) - ord('A') + 1
            b = int(code[1:3])
            B100 = (a - 1) * CAngle(4, 0, 0)
            L100 = (b - 31) * CAngle(6, 0, 0)
            scale = self.code_scale_dict[code[3]]
            db = self.scale_dict[scale]['db']
            dl = self.scale_dict[scale]['dl']
            # c为对应比例尺地形图在1∶100万地形图中的行号，d为对应比例尺地形图在1∶100万地形图中的列号
            # c和d为3位或4位(1:1000、1:500比例尺用4位表示，其余比例尺为3位)。
            cd_str = code[4:]
            c = int(cd_str[:len(cd_str) // 2])
            d = int(cd_str[len(cd_str) // 2:])
            n = int(CAngle(4, 0, 0) // db)  # n为对应比例尺地形图在1：100万比例尺地形图中的分幅数
            # 计算西南图廓点经纬度
            B1 = B100 + db * (n - c)
            L1 = L100 + dl * (d - 1)
            B2, L2 = B1, L1 + dl
            B3, L3 = B1 + db, L1 + dl
            B4, L4 = B1 + db, L1
            text += f'地形图{idx + 1}:\n'
            text += f'地形图{idx + 1}的1：100万图幅行号：{a}\n'
            text += f'地形图{idx + 1}的1：100万图幅列号：{b}\n'
            text += f'地形图{idx + 1}的比例尺分母：{scale}\n'
            text += f'地形图{idx + 1}在1∶100万地形图中的行号c:{c}列号d:{d}\n'
            text += f'西南图廓点经度:{L1}\n'
            text += f'西南图廓点纬度:{B1}\n'
            text += f'东南图廓点经度:{L2}\n'
            text += f'东南图廓点纬度:{B2}\n'
            text += f'东北图廓点经度:{L3}\n'
            text += f'东北图廓点纬度:{B3}\n'
            text += f'西北图廓点经度:{L4}\n'
            text += f'西北图廓点纬度:{B4}\n'
        self.result += text
        self.textBrowser.setText(text)

    def save(self):
        #path = QFileDialog.getSaveFileName(self, "<UNK>", "./", "*.txt")
        path = f'./result.txt'
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.result)
        QMessageBox.information(self, " ", "保存结果完成")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()