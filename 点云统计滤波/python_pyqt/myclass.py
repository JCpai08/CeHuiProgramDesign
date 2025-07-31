import math

class CPoint:
    def __init__(self, idx,x, y, z):
        self.idx = idx
        self.x = x
        self.y = y
        self.z = z
        self.candidate_point_list = []
        self.is_inner = False
    
    def distance_to(self, other: 'CPoint'):
        return math.sqrt((self.x - other.x)**2 + 
                         (self.y - other.y)**2 + 
                         (self.z - other.z)**2)
    def get_knn(self,k):
        '''获取最近的k个点'''
        k_point_list = self.candidate_point_list
        if k>=len(k_point_list):
           return k_point_list
        k_point_list.sort(key=lambda x:self.distance_to(x))
        return k_point_list[:k]
    @staticmethod
    def distance(p1: 'CPoint', p2: 'CPoint'):
        return math.sqrt((p1.x - p2.x)**2 + 
                         (p1.y - p2.y)**2 + 
                         (p1.z - p2.z)**2)
    
class CGrid:
    def __init__(self):
        self.point_list = []

    def add_point(self, point:CPoint):
      self.point_list.append(point)
    
    def get_point_list(self):
      return self.point_list
    
    def get_point_num(self):
      return len(self.point_list)

class CGridCollection:
  def __init__(self,point_list,grid_size=3):
      self.grid_size = grid_size
      self.grid_dict = {}
      self.grid_info = self._calculate_grid_info(point_list)
      self._assign_points_to_grids(point_list)

  def _calculate_grid_info(self, point_list):
      min_x = min(p.x for p in point_list)
      max_x = max(p.x for p in point_list)
      min_y = min(p.y for p in point_list)
      max_y = max(p.y for p in point_list)
      min_z = min(p.z for p in point_list)
      max_z = max(p.z for p in point_list)

      padded_max_x = ((max_x - min_x) // self.grid_size + 1) * self.grid_size + min_x
      padded_max_y = ((max_y - min_y) // self.grid_size + 1) * self.grid_size + min_y
      padded_max_z = ((max_z - min_z) // self.grid_size + 1) * self.grid_size + min_z

      return {
          "min_x": min_x,
          "max_x": padded_max_x,
          "min_y": min_y,
          "max_y": padded_max_y,
          "min_z": min_z,
          "max_z": padded_max_z,
          "grid_size": self.grid_size
      }
  def _assign_points_to_grids(self,point_list):
      min_x,min_y,min_z = self.grid_info["min_x"],self.grid_info["min_y"],self.grid_info["min_z"]
      grid_size = self.grid_info["grid_size"]
      #分配点云到格网
      for point in point_list:
        ix = int((point.x - min_x)//grid_size)
        iy = int((point.y - min_y)//grid_size)
        iz = int((point.z - min_z)//grid_size)
        key = (ix, iy, iz)
        if key not in self.grid_dict:
          self.grid_dict[key] = CGrid()
        self.grid_dict[key].add_point(point)
  def get_grid_point_num(self,key):
      if key not in self.grid_dict:
        return 0
      grid = self.grid_dict[key]
      return grid.get_point_num()
     