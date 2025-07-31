from myclass import CPoint, CTriangle

def is_left_turn(p1:CPoint, p2:CPoint, p3:CPoint) -> bool:
    """
    判断三点是否构成左转
    :param p1: 点1
    :param p2: 点2
    :param p3: 点3
    :return: 如果构成左转返回True，否则返回False
    """
    return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x) > 0

def getConvexHull(point_list):
    """
    计算点集的凸包
    :param point_list: 点集
    :return: 凸包点集
    """
    if len(point_list) < 3:
        return point_list

    # 使用Andrew's monotone chain algorithm
    point_list = sorted(set(point_list), key=lambda p: (p.x, p.y))
    lower = []
    p:CPoint
    for p in point_list:
        while len(lower) >= 2 and not is_left_turn(lower[-2], lower[-1], p):
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(point_list):
        while len(upper) >= 2 and not is_left_turn(upper[-2], upper[-1], p):
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]  # 去掉重复的端点

def getPolygonArea(point_list):
    """
    计算多边形面积
    :param point_list: 多边形顶点列表
    :return: 面积
    """
    n = len(point_list)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += point_list[i].x * point_list[j].y
        area -= point_list[j].x * point_list[i].y
    return abs(area) / 2.0

def getCircumCenter(tri:CTriangle)-> CPoint:
    """
    计算三角形的外心
    :param tri: 三角形
    :return: 外心 (CPoint)
    """
    x1, y1 = tri.p1.x, tri.p1.y
    x2, y2 = tri.p2.x, tri.p2.y
    x3, y3 = tri.p3.x, tri.p3.y

    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))

    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d

    return CPoint(ux, uy)

import math
def sort_points_by_angle(circumcenters):
    """
    按照相对于中心点的角度对外心进行排序
    :param circumcenters: 外心列表
    :param center_point: 中心点（重心 坐标平均值）
    :return: 按角度排序的外心列表
    """
    if len(circumcenters) <= 1:
        return circumcenters
    cx = sum(p.x for p in circumcenters) / len(circumcenters)
    cy = sum(p.y for p in circumcenters) / len(circumcenters)
    center_point = CPoint(cx, cy)
    def calculate_angle(point):
        # 计算相对于中心点的角度（弧度）
        dx = point.x - center_point.x
        dy = point.y - center_point.y
        return math.atan2(dy, dx) #math.atan2() 无除零问题 能正确区分象限
    # 按角度排序
    return sorted(circumcenters, key=calculate_angle)
