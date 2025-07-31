import math as m
class CPoint3d:
    '''
    存储物方点
    '''
    def __init__(self, X, Y, Z):
        self.X = X
        self.Y = Y
        self.Z = Z
class CPointPair:
    '''
    存储物方像方点对
    '''
    def __init__(self, idx, X, Y, Z, x, y):
        self.idx = idx
        self.X = X
        self.Y = Y
        self.Z = Z
        self.p3d = CPoint3d(X, Y, Z)
        self.x = x
        self.y = y
class CRotMat:
    def __init__(self,phi,omiga, kappa):
        '''
        param: phi, omiga, kappa 以度为单位
        '''
        p,o,k = phi, omiga, kappa
        self.a1 = m.cos(p)*m.cos(k) - m.sin(p)*m.sin(o)*m.sin(k)
        self.a2 = (-1)*m.cos(p)*m.sin(k) - m.sin(p)*m.sin(o)*m.cos(k)
        self.a3 = (-1)*m.sin(p)*m.cos(o)
        self.b1 = m.cos(o)*m.sin(k)
        self.b2 = m.cos(o)*m.cos(k)
        self.b3 = (-1)*m.sin(o)
        self.c1 = m.sin(p)*m.cos(k) + m.cos(p)*m.sin(o)*m.sin(k)
        self.c2 = (-1)*m.sin(p)*m.sin(k) + m.cos(p)*m.sin(o)*m.cos(k)
        self.c3 = m.cos(p)*m.cos(o)
    def __str__(self) -> str:
        return f"a1: {self.a1}\na2: {self.a2}\na3: {self.a3}\nb1: {self.b1}\nb2: {self.b2}\nb3: {self.b3}\nc1: {self.c1}\nc2: {self.c2}\nc3: {self.c3}"

class CMatrix:
    def __init__(self, r, c, mat_data_list):
        self.r = r
        self.c = c
        self.matrix = mat_data_list
    def __str__(self) -> str:
        result = f'{self.r}x{self.c} matrix:\n'
        result += '\n'.join([str(row) for row in self.matrix])
        return result

    def get_transpose(self)->'CMatrix':
        transpose_matrix = []
        for i in range(self.c):
            transpose_matrix.append([])
            for j in range(self.r):
                transpose_matrix[i].append(self.matrix[j][i])
        return CMatrix(self.c, self.r, transpose_matrix)
    
    def get_invert(self)->'CMatrix':
        n = self.r #要求为方阵, r = c
        #构建增广矩阵
        aug_matrix = [
            ([self.matrix[i][j] for j in range(n)] + [1 if i==j else 0 for j in range(n)])
            for i in range(n)
        ]        
        # 高斯-约旦消元
        for i in range(n):
            # 查找主元行（避免除以零）
            max_row = i
            for k in range(i, n):
                if abs(aug_matrix[k][i]) > abs(aug_matrix[max_row][i]):
                    max_row = k
            aug_matrix[i], aug_matrix[max_row] = aug_matrix[max_row], aug_matrix[i]

            pivot = aug_matrix[i][i]

            # 主元归一化
            for j in range(2 * n): # range范围(i,2*n)效率更高
                aug_matrix[i][j] /= pivot

            # 消去其他所有行的当前列
            for k in range(n):
                if k != i:
                    factor = aug_matrix[k][i]
                    for j in range(2 * n): # range范围(i,2*n)效率更高
                        aug_matrix[k][j] -= factor * aug_matrix[i][j]
                            # 提取逆矩阵部分
        inverse_matrix = [[aug_matrix[i][j] for j in range(n, 2 * n)] for i in range(n)]

        return CMatrix(n, n, inverse_matrix)
    
    def __add__(self, other):
        if self.r != other.r or self.c != other.c:
            return None
        else:
            result_matrix = []
            for i in range(self.r):
                result_matrix.append([])
                for j in range(self.c):
                    result_matrix[i].append(self.matrix[i][j] + other.matrix[i][j])
        return CMatrix(self.r, self.c, result_matrix)
    def __sub__(self, other):
        if self.r != other.r or self.c != other.c:
            return None
        else:
            result_matrix = []
            for i in range(self.r):
                result_matrix.append([])
                for j in range(self.c):
                    result_matrix[i].append(self.matrix[i][j] - other.matrix[i][j])
        return CMatrix(self.r, self.c, result_matrix)
    def __mul__(self, other)->'CMatrix':
        if self.c != other.r:
            raise ValueError("矩阵乘法错误")
        else:
            result_matrix = []
            for i in range(self.r):
                result_matrix.append([])
                for j in range(other.c):
                    result_matrix[i].append(0)
                    for k in range(self.c): #self.c = other.r
                        result_matrix[i][j] += self.matrix[i][k] * other.matrix[k][j]
        return  CMatrix(self.r, other.c, result_matrix)

if __name__ == '__main__':
    # mat = CMatrix(3,3,[[2,-1,0],[-1,2,-1],[0,-1,2]])
    # mat_inv = mat.get_invert()
    # print(mat_inv.matrix)
    # print((mat * mat_inv).matrix)
    R = CRotMat(0,0,0)
    print(R)
    mat = CMatrix(2,2,[[2,0],[0,2]])
    print(mat.get_invert())
