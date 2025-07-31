from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from mainWin import Ui_MainWindow
import sys
from myclass import CPoint,CTriangle
from utils import getConvexHull,getPolygonArea,getCircumCenter,sort_points_by_angle

from matplotlib import pyplot as plt

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self._connect()
        self.point_list = []
        self.triangle_list = [] # 三角网列表元素为CTriangle对象
        self.voronoi_list = []  # Voronoi图列表元素为CPoint对象的列表
        self.hull_point_list = [] # 凸包点集列表元素为CPoint对象
        self.result =f''
        self.fig = plt.figure()
    def _connect(self):
        self.actionopen.triggered.connect(self.openFile)
        self.actioncomputeDel.triggered.connect(self.computeDel)
        self.actioncomputeHull.triggered.connect(self.computeHull)
        self.actioncomputeVor.triggered.connect(self.computeVoronoi)
        self.actionsave.triggered.connect(self.saveResult)

    def openFile(self):
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,'open file','*.txt')
        if path:
            with open(path,'r') as f:
                f.readline() #跳过第一行 X坐标 Y坐标
                line = f.readline() 
                while line:
                    x,y = line.split()
                    self.point_list.append(CPoint(float(x),float(y)))
                    line = f.readline()
            QMessageBox.information(self,' ',f'读取数据完成，共{len(self.point_list)}个点')
    def saveResult(self):
        #path,_ = QtWidgets.QFileDialog.getSaveFileName(self,'save file','*.txt')
        path = r'./result.txt'
        if path:
            with open(path,'w',encoding='utf-8') as f:
                f.write(self.result)
            QMessageBox.information(self,' ',f'保存结果完成')
    def computeDel(self):
        if len(self.point_list) == 0:
            QtWidgets.QMessageBox.warning(self,'warning','请先读取数据！')
            return
        # 初始化三角形列表 计算超级大三角形
        x_min = min([p.x for p in self.point_list])
        x_max = max([p.x for p in self.point_list])
        y_min = min([p.y for p in self.point_list])
        y_max = max([p.y for p in self.point_list])
        w,h = x_max - x_min, y_max - y_min
        superTri = CTriangle(
            CPoint(x_min-w-10,y_min-10),
            CPoint(x_max+10,y_max+h+10),
            CPoint(x_max+10,y_min-10)
        )
        self.triangle_list = [superTri]
        # 从点集V中选择点插入，并分割插入点所在的三角形
        p:CPoint
        for idx,p in enumerate(self.point_list):
            print(len(self.triangle_list))
            bad_triangle_list = []
            edge_count_dict = {}
            # 找出所有坏三角形
            t:CTriangle
            for t in self.triangle_list:
                if t.containPoint(p): # 如果点在外接圆内 则为坏三角形
                    bad_triangle_list.append(t)
                    t.isBad = True
            # 找到被插入点分割的多边形边界
            poly_edge_list = []
            for t in bad_triangle_list:
                p1,p2,p3 = t.point_list
                #使用frozenset 保证是无向边 同时可作为字典键值
                edge_list = [frozenset({p1,p2}),frozenset({p2,p3}),frozenset({p1,p3})]
                e:frozenset
                for e in edge_list:
                    if e in edge_count_dict:
                        edge_count_dict[e] += 1
                    else:
                        edge_count_dict[e] = 1
            # 只有出现一次的边才是多边形边界
            for edge, count in edge_count_dict.items():
                if count == 1:
                    poly_edge_list.append(edge)
            # 分割多边形为三角形 生成目前所有点的三角网 三角网包含所有非坏三角形和分割后的三角形
            self.triangle_list = [t for t in self.triangle_list if not t.isBad] #非坏三角形 isBad = False
            for e in poly_edge_list:
                self.triangle_list.append(CTriangle(list(e)[0],list(e)[1],p))

        #所有点插入后 移除包含超级三角形顶点的三角形
        tri_list = []
        for t in self.triangle_list:
            if (t.p1 not in superTri.point_list) and (t.p2 not in superTri.point_list) and (t.p3 not in superTri.point_list):
                tri_list.append(t)
        self.triangle_list = tri_list
        s_list = [t.get_s() for t in self.triangle_list]
        s_list.sort()
        text = f'delaunay剖分:\n' + '\n'.join([str(x) for x in s_list])
        self.result += text
        self.textBrowser.setText(text)
        self.fig = plot_triangulation(self.triangle_list,self.point_list, './img/final.png',self.fig)
        plt.axis('off')
        plt.show()

    def computeHull(self):
        if len(self.point_list) == 0:
            QtWidgets.QMessageBox.warning(self,'warning','请先读取数据！')
            return
        # 计算凸包
        self.hull_point_list = getConvexHull(self.point_list)
        self.fig = plot_polygon(self.hull_point_list, self.fig, path='./img/hull.png')
        s = getPolygonArea(self.hull_point_list)
        text = f'凸包面积: {s}\n' 
        self.result += text
        self.textBrowser.setText(text)
        plt.axis('off')
        plt.show()
    def computeVoronoi(self):
        if len(self.hull_point_list) == 0:
            QtWidgets.QMessageBox.warning(self,'warning','请先计算凸包！')
            return
        point_tri_dict = {} #存储每个点关联的三角形索引
        t:CTriangle
        for idx,t in enumerate(self.triangle_list):
            key_list = [p.to_key() for p in t.point_list]
            for key in key_list:
                if key in point_tri_dict:
                    point_tri_dict[key].append(idx)
                else:
                    point_tri_dict[key] = [idx]
        # 预处理凸包点集 便于查找判断点是否在凸包上
        hull_set = {p.to_key() for p in self.hull_point_list}
        p:CPoint
        for p in self.point_list:
            circumcenter_list = []
            # 如果点在凸包上 则不需要计算Voronoi图
            if p.to_key() in hull_set:
                continue
            # 查找与点关联的三角形
            for idx in point_tri_dict[p.to_key()]:
                circumcenter_list.append(getCircumCenter(self.triangle_list[idx]))
            # 如果circumcenters 列表中的点数少于3个，则跳过该点，因为无法构成多边形
            if len(circumcenter_list) < 3:
                continue
            # 对外心进行排序
            circumcenter_list = sort_points_by_angle(circumcenter_list)
            self.voronoi_list.append(circumcenter_list)
        # 计算面积排序
        area_list = [getPolygonArea(polygon) for polygon in self.voronoi_list]
        area_list.sort()
        text = f'Voronoi图面积排序:\n' + '\n'.join([f'{i+1}: {area}' for i, area in enumerate(area_list)])
        self.result += text
        self.textBrowser.setText(text)
        # 绘制Voronoi图
        for polygon in self.voronoi_list:
            self.fig = plot_polygon(polygon, self.fig)
        plt.savefig('./img/voronoi.png')
def plot_triangulation(triangles, points,path,fig,ax=None):
    if ax is None:
        ax = plt.gca()
    for tri in triangles:
        ax.plot([tri.p1.x, tri.p2.x], [tri.p1.y, tri.p2.y], 'b-')
        ax.plot([tri.p2.x, tri.p3.x], [tri.p2.y, tri.p3.y], 'b-')
        ax.plot([tri.p3.x, tri.p1.x], [tri.p3.y, tri.p1.y], 'b-')
    for p in points:
        ax.plot(p.x, p.y, 'ro')
    fig.savefig(path)
    return fig

def plot_polygon(point_list, fig, ax=None, path=None):
    if ax is None:
        ax = fig.gca()
    x_coords = [p.x for p in point_list]
    y_coords = [p.y for p in point_list]
    ax.plot(x_coords, y_coords, 'g-')  # 绘制连线
    ax.plot(x_coords, y_coords, 'ro')  # 绘制点
    ax.plot([x_coords[0], x_coords[-1]], [y_coords[0], y_coords[-1]], 'g-')  # 闭合图形
    # 添加这一行来保持坐标轴比例一致
    ax.set_aspect('equal', adjustable='box')
    if path:
        fig.savefig(path)
    return fig

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())