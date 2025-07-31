from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem
from main_ui0713 import Ui_MainWindow
from input_correct import Ui_Dialog
from myclass import CPoint3d, CMatrix, CRotMat, CPointPair
from utils import compute_xy_estimate
import math as m
import sys
import re


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.connect_buttons()
        self.param_dict = {}
        self.point_pair_list = []
        self.A = None #存储迭代过程中的矩阵A 用于精度评定
        self.result = f''

    def connect_buttons(self):
        self.actionopen.triggered.connect(self.open)
        self.actioncompute.triggered.connect(self.compute)
        self.actionevaluate.triggered.connect(self.evaluate)
        self.actionsave.triggered.connect(self.save)

    def input_correct(self):
        dialog = QtWidgets.QDialog()
        ui = Ui_Dialog()
        ui.setupUi(dialog)
        ui.bOK.clicked.connect(dialog.accept)

        ui.lineEdit.setText(str(self.param_dict["m"]))
        ui.lineEdit_2.setText(str(self.param_dict["x0"]))
        ui.lineEdit_3.setText(str(self.param_dict["y0"]))
        ui.lineEdit_4.setText(str(self.param_dict["f"] * 1000))

        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            try:
                m_new = int(ui.lineEdit.text())
                x0_new = float(ui.lineEdit_2.text())
                y0_new = float(ui.lineEdit_3.text())
                f_new = float(ui.lineEdit_4.text())
                self.param_dict = {
                    "m": m_new,
                    "x0": x0_new,
                    "y0": y0_new,
                    "f": f_new / 1000,
                }
            except ValueError:
                QtWidgets.QMessageBox.warning(self, "输入错误", "请输入有效的数值")

    def open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", ".txt")
        if path:
            self.point_pair_list = []
            with open(path, "r", encoding="utf-8") as file:
                # 读取影像比例尺m 影像内方位元素,x0,y0,f(mm)
                p = re.compile(r"\d[\d.,]*")
                m = int(p.findall(file.readline())[-1])
                x0, y0, f = map(
                    lambda x: float(x), p.findall(file.readline())[-1].split(",")
                )
                self.param_dict = {
                    "m": m,
                    "x0": x0,
                    "y0": y0,
                    "f": f / 1000,
                }  # f 单位mm 转换成m
                self.input_correct()
                # 读取点坐标数据
                line = (
                    file.readline()
                )  # skip line: 点号,地面坐标X(m),地面坐标Y,地面坐标Z,影像坐标x(mm),影像坐标y(mm)
                r = 0
                self.tableWidget.clearContents()
                self.tableWidget.setRowCount(0)
                line = file.readline()
                while line:
                    values = [float(x) for x in line.split(",")]
                    idx, X, Y, Z, x, y = values
                    self.point_pair_list.append(
                        CPointPair(idx, X, Y, Z, x / 1000, y / 1000)
                    )  # 影像坐标 单位转换为m
                    self.tableWidget.insertRow(self.tableWidget.rowCount())
                    for c, item in enumerate(values):
                        self.tableWidget.setItem(r, c, QTableWidgetItem(str(item)))
                    r += 1
                    line = file.readline()
            # 计算线元素初始值
            n = len(self.point_pair_list)
            Xs = sum(point.X for point in self.point_pair_list) / n
            Ys = sum(point.Y for point in self.point_pair_list) / n
            Zs = self.param_dict["m"] * self.param_dict["f"]
            #self.param_dict = self.param_dict | {"Xs": Xs, "Ys": Ys, "Zs": Zs}
            self.param_dict.update({"Xs": Xs, "Ys": Ys, "Zs": Zs})
            # 初始化旋转角
            #self.param_dict = self.param_dict | {"phi": 0, "omiga": 0, "kappa": 0}
            self.param_dict.update({"phi": 0, "omiga": 0, "kappa": 0})
            text = f"控制点总数: {n}\n线元素初始值: Xs={Xs:.3f},Ys={Ys:.3f},Zs={Zs:.3f}\n"
            self.textBrowser.setText(text)
            self.result+=text

    def compute(self):
        if len(self.point_pair_list)==0:
            QtWidgets.QMessageBox.warning(self, "提示", "请先导入数据")
            return
        dXs = dYs = dZs = 999
        dPhi = dOmiga = dKappa = 999
        cnt = 0
        text = f""
        #收敛条件 线元素的改正数均小于0.1米，角元素的改正数均小于10秒
        while (
            abs(dXs) >= 0.1
            or abs(dYs) >= 0.1
            or abs(dZs) >= 0.1
            or abs(dPhi)  >= (1 / 60.0) * (m.pi / 180.0)
            or abs(dOmiga)  >= (1 / 60.0) * (m.pi / 180.0)
            or abs(dKappa)   >= (1 / 60.0) * (m.pi / 180.0)
        ):
            # 计算旋转矩阵
            self.R = R = CRotMat(
                self.param_dict["phi"],
                self.param_dict["omiga"],
                self.param_dict["kappa"],
            )
            Xs, Ys, Zs = (
                self.param_dict["Xs"],
                self.param_dict["Ys"],
                self.param_dict["Zs"],
            )
            f = self.param_dict["f"]
            A_data_list = []
            l_data_list = []
            # 根据物方像方点对计算矩阵A和向量l
            point_pair: CPointPair
            for idx, point_pair in enumerate(self.point_pair_list):
                x, y = compute_xy_estimate(R, point_pair.p3d, CPoint3d(Xs, Ys, Zs), f)
                Z_bar = (
                    R.a3 * (point_pair.X - Xs)
                    + R.b3 * (point_pair.Y - Ys)
                    + R.c3 * (point_pair.Z - Zs)
                )
                if cnt == 0 and idx == 1:
                    text += f"控制点2对应像点的初始近似值x21 = {x*1000:.3f}mm,y21 = {y*1000:.3f}mm\n"
                if cnt == 0 and idx == 2:
                    text += f"控制点2对应像点的初始近似值x31 = {x*1000:.3f}mm,y31 = {y*1000:.3f}mm\n"
                lx = point_pair.x - x
                ly = point_pair.y - y
                a11 = 1 / Z_bar * (R.a1 * f + R.a3 * x)
                a12 = 1 / Z_bar * (R.b1 * f + R.b3 * x)
                a13 = 1 / Z_bar * (R.c1 * f + R.c3 * x)
                a21 = 1 / Z_bar * (R.a2 * f + R.a3 * y)
                a22 = 1 / Z_bar * (R.b2 * f + R.b3 * y)
                a23 = 1 / Z_bar * (R.c2 * f + R.c3 * y)
                o, k = m.radians(self.param_dict["omiga"]), m.radians(self.param_dict["kappa"])
                a14 = y * m.sin(o) - (x / f * (x * m.cos(k) - y * m.sin(k)) + f * m.cos(k)) * m.cos(o)
                a15 = (-1) * f * m.sin(k) - x / f * (x * m.sin(k) + y * m.cos(k))
                a16 = y
                a24 = (-1) * x * m.sin(o) - (y / f * (x * m.cos(k) - y * m.sin(k)) - f * m.sin(k)) * m.cos(o)
                a25 = (-1) * f * m.cos(k) - y / f * (x * m.sin(k) + y * m.cos(k))
                a26 = (-1) * x
                A_data_list.append([a11, a12, a13, a14, a15, a16])
                A_data_list.append([a21, a22, a23, a24, a25, a26])
                l_data_list.append([lx])
                l_data_list.append([ly])
            A = self.A = CMatrix(2 * len(self.point_pair_list), 6, A_data_list)
            l = CMatrix(2 * len(self.point_pair_list), 1, l_data_list)
            # X = (AtA)^(-1) * Atl
            X = (A.get_transpose() * A).get_invert() * A.get_transpose() * l
            dXs, dYs, dZs, dPhi, dOmiga, dKappa = X.get_transpose().matrix[0]
            if cnt == 0:
                text += f"第一次迭代得到的外方位元素改正数:\n"
                text += f"dX = {dXs:.6f}\ndY = {dYs:.6f}\ndZ = {dZs:.6f}\ndPhi = {dPhi:.6f}\ndOmiga = {dOmiga:.6f}\ndKappa = {dKappa:.6f}\n"
            self.param_dict["Xs"] += dXs
            self.param_dict["Ys"] += dYs
            self.param_dict["Zs"] += dZs
            self.param_dict["phi"] += dPhi
            self.param_dict["omiga"] += dOmiga
            self.param_dict["kappa"] += dKappa
            cnt += 1 # 一次迭代完成
        text+=f'最后一次迭代的旋转矩阵的对角线上的元素a1、b2、c3\na1: {self.R.a1:.3f} b2: {self.R.b2:.3f} c3: {self.R.c3:.3f}\n'
        text += f"最终的外方位元素:\n"
        text += f'Xs = {self.param_dict["Xs"]:.6f}\nYs = {self.param_dict["Ys"]:.6f}\nZs = {self.param_dict["Zs"]:.6f}\nphi = {self.param_dict["phi"]:.6f}\nomiga = {self.param_dict["omiga"]:.6f}\nkappa = {self.param_dict["kappa"]:.6f}\n'
        text += f"总迭代次数: {cnt}"
        self.textBrowser.setText(text)
        self.result+=text

    def evaluate(self):
        if self.A is None: 
            QtWidgets.QMessageBox.warning(self, "警告", "请先进行迭代计算")
            return
        R = CRotMat(
            self.param_dict["phi"], self.param_dict["omiga"], self.param_dict["kappa"]
        )
        Xs, Ys, Zs = self.param_dict["Xs"], self.param_dict["Ys"], self.param_dict["Zs"]
        f = self.param_dict["f"]
        n = len(self.point_pair_list)
        v_list = []
        point_pair: CPointPair
        for point_pair in self.point_pair_list:
            x, y = compute_xy_estimate(R, point_pair.p3d, CPoint3d(Xs, Ys, Zs), f)
            v_list += [point_pair.x - x, point_pair.y - y]
        sigma0 = m.sqrt(sum(v**2 for v in v_list) / (2 * n - 6))
        text = f'单位权中误差: {sigma0:.6f}\n'
        AtA_inv_data = (self.A.get_transpose() * self.A).get_invert().matrix
        text+=f'外方位元素的中误差:\n'
        sigma = m.sqrt(AtA_inv_data[0][0]) * sigma0
        text+=f'Xs: {sigma:.6f}\n'
        sigma = m.sqrt(AtA_inv_data[1][1]) * sigma0
        text+=f'Ys: {sigma:.6f}\n'
        sigma = m.sqrt(AtA_inv_data[2][2]) * sigma0
        text+=f'Zs: {sigma:.6f}\n'
        sigma = m.sqrt(AtA_inv_data[3][3]) * sigma0
        text+=f'phi: {sigma:.6f}\n'
        sigma = m.sqrt(AtA_inv_data[4][4]) * sigma0
        text+=f'omiga: {sigma:.6f}\n'
        sigma = m.sqrt(AtA_inv_data[5][5]) * sigma0
        text+=f'kappa: {sigma:.6f}\n'
        self.textBrowser.setText(text)
        self.statusbar.showMessage('精度评定完成')
        self.result+=text

    def save(self):
        #path,_ = QFileDialog.getSaveFileName(self, '保存文件', './', '*.txt')
        path = r'./result.txt'
        with open(path, 'w',encoding='utf-8') as f:
            f.write(self.result)
        self.statusbar.showMessage('保存完成')
        QtWidgets.QMessageBox.information(self, '提示', '保存完成')
        


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
