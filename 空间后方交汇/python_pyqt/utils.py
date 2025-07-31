from myclass import CPoint3d,CRotMat

def compute_xy_estimate(R:CRotMat,pGrd:CPoint3d,pCam:CPoint3d,f):
    '''
    计算像方坐标近似值
    R:旋转矩阵 描述相机姿态
    pGrd:物方坐标点
    pCam:相机坐标点
    f:焦距
    '''
    Xa,Ya,Za = pGrd.X,pGrd.Y,pGrd.Z
    Xs,Ys,Zs = pCam.X,pCam.Y,pCam.Z
    X_bar = R.a1*(Xa-Xs)+R.b1*(Ya-Ys)+R.c1*(Za-Zs)
    Y_bar = R.a2*(Xa-Xs)+R.b2*(Ya-Ys)+R.c2*(Za-Zs)
    Z_bar = R.a3*(Xa-Xs)+R.b3*(Ya-Ys)+R.c3*(Za-Zs)
    x = (-1)*f*X_bar/Z_bar
    y = (-1)*f*Y_bar/Z_bar
    return x,y