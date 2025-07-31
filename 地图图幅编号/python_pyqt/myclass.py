
# noinspection SpellCheckingInspection
class CAngle:
    def __init__(self,D,M,S):
        self.D = D
        self.M = M
        self.S = S

    @classmethod
    def fromStr(cls,sAngle):
        d = int(float(sAngle))
        m = int((float(sAngle)-d)*100)
        s = float(sAngle)*10000-d*10000-m*100
        return CAngle(d,m,s)

    @classmethod
    def fromSecond(cls,dSec):
        d = dSec//3600
        m = (dSec-d*3600)//60
        s = dSec-d*3600-m*60
        return CAngle(d,m,s)

    def toSecond(self):
        return self.D*3600+self.M*60+self.S

    def toDegree(self):
        return self.D+self.M/60+self.S/3600

    def format_ddmmss(self):
        return f'{self.D + self.M / 100 + self.S / 10000:.5f}'

    def __add__(self,other):
        s1=self.toSecond()
        s2=other.toSecond()
        return CAngle.fromSecond(s1+s2)
    def __sub__(self,other):
        s1=self.toSecond()
        s2=other.toSecond()
        return CAngle.fromSecond(s1-s2)
    def __mul__(self,dTime:float):
        s = self.toSecond()
        return CAngle.fromSecond(s*dTime)
    def __rmul__(self,dTime:float):
        s = self.toSecond()
        return CAngle.fromSecond(s*dTime)
    def __floordiv__(self, other):
        s1=self.toSecond()
        s2=other.toSecond()
        return s1//s2
    def __mod__(self, other):
        s1=self.toSecond()
        s2=other.toSecond()
        return CAngle.fromSecond(s1%s2)
    def __repr__(self):
        return f'{self.D}.{self.M:02d}{self.S:02d}'


class CLoc:
    def __init__(self,name,b:CAngle,l:CAngle):
        self.name = name
        self.b = b
        self.l = l

if __name__ == '__main__':
    a = CAngle(4,0,0)
    a2 = a*2
    print(a2)
    a2 = 2*a
    print(a2)
    print(str(a2))

