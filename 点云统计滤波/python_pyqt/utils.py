from myclass import CPoint,CGridCollection

def get_grid_key(point:CPoint,grid_info):
    '''
    获取当前点对应的格网索引
    param point: 当前点
    param grid_info: 格网信息
    return: 格网索引 元组类型作为字典键值
    '''
    min_x,min_y,min_z = grid_info["min_x"],grid_info["min_y"],grid_info["min_z"]
    grid_size = grid_info["grid_size"]
    ix = int((point.x - min_x)//grid_size)
    iy = int((point.y - min_y)//grid_size)
    iz = int((point.z - min_z)//grid_size)
    return (ix,iy,iz)

def get_neighbor_key_list(point:CPoint,grid_info):
    '''
    获取当前点对应的相邻格网索引
    立体格网 邻域 3*3*3
    '''
    ix,iy,iz = get_grid_key(point,grid_info)
    neighbor_key_list = []
    for dx in [-1,0,1]:
        for dy in [-1,0,1]:
            for dz in [-1,0,1]:
                neighbor_key_list.append((ix+dx,iy+dy,iz+dz))
    return neighbor_key_list
def assign_candidate_points(point_list,gird_collection:CGridCollection):
    '''
    为每个点分配候选点
    '''
    grid_dict = gird_collection.grid_dict
    grid_info = gird_collection.grid_info
    for point in point_list:
        neighbor_key_list = get_neighbor_key_list(point,grid_info)
        for neighbor_key in neighbor_key_list:
            # 如果该格网没有点或不存在该格网 则跳过
            if (gird_collection.get_grid_point_num(neighbor_key)==0):
                continue
            point.candidate_point_list+=grid_dict[neighbor_key].get_point_list()  
        # 删除自身
        for i,p in enumerate(point.candidate_point_list):
            if p.idx==point.idx:
                del point.candidate_point_list[i]
                break
        
