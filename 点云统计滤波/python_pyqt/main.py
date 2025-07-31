# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog,QDialog,QMessageBox
from gui_windowView import Ui_MainWindow
from input_k import Ui_InputK

import math
from myclass import CPoint,CGrid,CGridCollection
from utils import assign_candidate_points

class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)

        self.point_list = []
        self.grid_collection = None
        self.result = f''

        self.actionopen.triggered.connect(self.open)
        self.actionbuild_grids.triggered.connect(self.buildGrids)
        self.actiondenoise.triggered.connect(self.denoise)
        self.actionsave.triggered.connect(self.save)
    
    def open(self):
        path,_ = QFileDialog.getOpenFileName(self, '打开文件', './', '*.txt')
        if len(self.point_list)==0:
            with open(path, 'r') as f:
                for idx,line in enumerate(f.readlines()):
                    x,y,z = [float(i) for i in line.split()]
                    self.point_list.append(CPoint(idx,x,y,z))
        self.textBrowser.setText(f'文件已打开,点数：{len(self.point_list)}')
        self.result+=f'点数：{len(self.point_list)}\n'
        self.statusbar.showMessage('文件已打开')
        return
    def buildGrids(self):
        if len(self.point_list)==0:
            QMessageBox.warning(self, '提示', '请先打开文件')
            return
        self.grid_collection = CGridCollection(self.point_list,grid_size=3)
        grid_info = self.grid_collection.grid_info
        first_gird_point_num = self.grid_collection.get_grid_point_num((0,0,0))
        text = f'xmin:{grid_info["min_x"]}\nxmax:{grid_info["max_x"]}\nymin:{grid_info["min_y"]}\nymax:{grid_info["max_y"]}\nzmin:{grid_info["min_z"]}\nzmax:{grid_info["max_z"]}\n'
        self.textBrowser.setText(text)
        self.textBrowser.append(f'第一个格网单元(0,0,0)的点个数：{first_gird_point_num}\n')
        self.result+=f'{text}\n第一个格网单元(0,0,0)的点个数：{first_gird_point_num}\n'
        return 
    def denoise(self):
        text = f''
        if self.grid_collection is None:
            QMessageBox.warning(self, '提示', '请先构建格网')
            return
        # 弹出对话框 输入用于滤波去噪的邻近点个数k 默认为6
        ui = Ui_InputK()
        dialog = QDialog()
        ui.setupUi(dialog)
        if dialog.exec_()==QDialog.Accepted:
            k = int(ui.lineEdit.text())
        assign_candidate_points(self.point_list,self.grid_collection)
        text+=f'第一个点的候选点数目：{len(self.point_list[0].candidate_point_list)}\n'
        global_sum_mean = 0
        global_sum_std = 0
        for idx,point in enumerate(self.point_list):
            knn_point_list = point.get_knn(k)
            if idx==0:
                text+=f'第一个点的k个点序号：{[p.idx+1 for p in knn_point_list]}\n'
            # 计算均值和标准差
            # 如果邻近点个数为0，则设置均值为6，标准差为6
            if len(knn_point_list)==0:
                point.neighbor_dis_mean = 6
                point.neighbor_dis_std = 6
            else:
                miu = point.neighbor_dis_mean = sum([CPoint.distance(point,p) for p in knn_point_list]) / len(knn_point_list)
                sigma2 = sum([(CPoint.distance(point,p)-miu)**2 for p in knn_point_list]) / len(knn_point_list)
                point.neighbor_dis_std = math.sqrt(sigma2)
            global_sum_mean += point.neighbor_dis_mean
            global_sum_std += point.neighbor_dis_std
        global_mean = global_sum_mean / len(self.point_list)
        global_std = global_sum_std / len(self.point_list)
        text+=f'所有点的邻域点平均距离均值: {global_mean}\n'
        text+=f'所有点的邻域点距离标准差均值: {global_std}\n'
        num_inner_points = 0
        threshold = global_mean + global_std * 2 # 阈值
        for point in self.point_list:
            # 根据阈值判断是否为噪声点
            # 如果距离均值小于阈值，则该点为内点
            if point.neighbor_dis_mean <= threshold:
                point.is_inner = True
                num_inner_points+=1
        text+=f'滤波后的点数: {num_inner_points}\n'
        self.textBrowser.setText(text)
        self.result+=text

    def save(self):
        #path,_ = QFileDialog.getSaveFileName(self, '保存文件', './', '*.txt')
        path = r'./result.txt'
        with open(path, 'w') as f:
            f.write(self.result)
            for point in self.point_list:
                if point.is_inner:
                    f.write(f'{point.x} {point.y} {point.z}\n')
        self.statusbar.showMessage('结果保存成功')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainForm()
    myWin.show()
    sys.exit(app.exec_())