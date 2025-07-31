import math as m
class CPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def dis_to(self, p:'CPoint'):
        return m.sqrt((self.x - p.x)**2 + (self.y - p.y)**2)
    def to_key(self):
        return (self.x, self.y)

    
class CTriangle:
    def __init__(self, p1:CPoint, p2:CPoint, p3:CPoint):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.point_list = [p1, p2, p3]
        self.isBad = False
    
    def _getCircumCycle(self):
        """
        获得三角形的外接圆圆心和半径
        return: (x0,y0,r)
        """
        x1,x2,x3 = self.p1.x,self.p2.x,self.p3.x
        y1,y2,y3 = self.p1.y,self.p2.y,self.p3.y
        D = 2*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))
        Dx = (x1**2+y1**2)*(y2-y3)+(x2**2+y2**2)*(y3-y1)+(x3**2+y3**2)*(y1-y2)
        Dy = (x1**2+y1**2)*(x3-x2)+(x2**2+y2**2)*(x1-x3)+(x3**2+y3**2)*(x2-x1)
        x0 = Dx/D
        y0 = Dy/D
        return x0,y0,m.sqrt((x0-x1)**2+(y0-y1)**2)

    def containPoint(self, p:CPoint):
        """
        通过比较点到外接圆圆心的距离与外接圆半径的大小  判断点是否在三角形外接圆内
        return: bool 在外接圆内为True
        """
        x0,y0,r = self._getCircumCycle()
        circumcenter:CPoint = CPoint(x0,y0)
        return p.dis_to(circumcenter) < r

    def get_s(self):
        p1,p2,p3 = self.point_list
        a,b,c = p1.dis_to(p2), p1.dis_to(p3), p2.dis_to(p3)
        s = 0.5*(a+b+c)
        return m.sqrt(s*(s-a)*(s-b)*(s-c))


    
if __name__ == '__main__':
    p1 = CPoint(0,0)
    p2 = CPoint(2,2)
    p3 = CPoint(2,0)
    t = CTriangle(p1,p2,p3)
    print(t._getCircumCycle())
