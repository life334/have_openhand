from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
import numpy as np
from shapely.geometry import Polygon, Point
import json
from scipy.spatial import Delaunay
import math

router = APIRouter()

# 定义请求模型
class EarthworkCalculationRequest(BaseModel):
    polygon_coordinates: List[Dict[str, float]]  # 格式: [{"longitude": x, "latitude": y, "height": z}, ...]
    original_height: float
    target_height: float

# 定义响应模型
class EarthworkCalculationResponse(BaseModel):
    area: float
    cut_volume: float
    fill_volume: float
    net_volume: float
    unit: str = "m³"

# 定义三角网计算请求模型
class TINEarthworkCalculationRequest(BaseModel):
    polygon_coordinates: List[Dict[str, float]]  # 外部边界多边形
    sample_points: List[Dict[str, float]]  # 采样点 [{"longitude": x, "latitude": y, "original_height": z1, "target_height": z2}, ...]
    calculation_method: str = "tin"  # 计算方法: "tin" 或 "grid"

# 定义三角网计算响应模型
class TINEarthworkCalculationResponse(BaseModel):
    area: float
    cut_volume: float
    fill_volume: float
    net_volume: float
    triangles: List[List[int]] = []  # 三角形索引，用于前端可视化
    unit: str = "m³"
    method: str = "tin"

@router.post("/calculate", response_model=EarthworkCalculationResponse)
async def calculate_earthwork(request: EarthworkCalculationRequest):
    """
    计算指定多边形区域的填挖方量
    
    - polygon_coordinates: 多边形顶点坐标列表
    - original_height: 原始地面高程
    - target_height: 目标地面高程
    
    返回:
    - area: 区域面积 (m²)
    - cut_volume: 挖方量 (m³)
    - fill_volume: 填方量 (m³)
    - net_volume: 净体积 (填方 - 挖方) (m³)
    """
    try:
        # 检查多边形是否有效
        if len(request.polygon_coordinates) < 3:
            raise HTTPException(status_code=400, detail="多边形至少需要3个顶点")
        
        # 提取多边形坐标
        polygon_points = [(point["longitude"], point["latitude"]) for point in request.polygon_coordinates]
        
        # 创建Shapely多边形
        polygon = Polygon(polygon_points)
        
        # 计算面积 (平方米)
        # 注意: 这是一个简化的计算，对于大区域可能需要更精确的地理计算
        area = calculate_geographic_area(polygon_points)
        
        # 计算高度差
        height_difference = request.target_height - request.original_height
        
        # 计算体积
        volume = area * abs(height_difference)
        
        # 确定填方和挖方
        cut_volume = 0
        fill_volume = 0
        
        if height_difference > 0:
            # 目标高程高于原始高程，需要填方
            fill_volume = volume
        elif height_difference < 0:
            # 目标高程低于原始高程，需要挖方
            cut_volume = volume
        
        # 计算净体积
        net_volume = fill_volume - cut_volume
        
        # 返回结果
        return {
            "area": round(area, 2),
            "cut_volume": round(cut_volume, 2),
            "fill_volume": round(fill_volume, 2),
            "net_volume": round(net_volume, 2),
            "unit": "m³"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算填挖方量时出错: {str(e)}")

def calculate_geographic_area(coordinates):
    """
    使用Haversine公式计算地理坐标多边形的面积
    
    参数:
    - coordinates: 经纬度坐标列表 [(lon1, lat1), (lon2, lat2), ...]
    
    返回:
    - 面积 (平方米)
    """
    # 这是一个简化的计算方法，对于小区域足够精确
    # 对于大区域或跨越多个经纬度的区域，应使用更精确的地理计算库
    
    # 将多边形转换为UTM坐标系统进行面积计算
    # 这里使用简化的方法，假设地球是球形，使用平均纬度作为参考
    
    # 地球半径 (米)
    R = 6371000
    
    # 计算多边形的平均纬度
    avg_lat = sum(lat for _, lat in coordinates) / len(coordinates)
    
    # 在平均纬度下，1度经度对应的距离 (米)
    lon_scale = np.cos(np.radians(avg_lat)) * R * np.pi / 180
    
    # 1度纬度对应的距离 (米)
    lat_scale = R * np.pi / 180
    
    # 转换坐标为米
    scaled_coords = [(lon * lon_scale, lat * lat_scale) for lon, lat in coordinates]
    
    # 使用Shapely计算面积
    polygon = Polygon(scaled_coords)
    return polygon.area

def convert_to_local_coordinates(points, avg_lat=None):
    """
    将经纬度坐标转换为本地平面坐标（米）
    
    参数:
    - points: 经纬度坐标列表 [{"longitude": x, "latitude": y, ...}, ...]
    - avg_lat: 平均纬度，如果为None则计算
    
    返回:
    - 本地坐标列表 [(x, y), ...]
    """
    # 地球半径 (米)
    R = 6371000
    
    # 计算平均纬度
    if avg_lat is None:
        avg_lat = sum(p["latitude"] for p in points) / len(points)
    
    # 在平均纬度下，1度经度对应的距离 (米)
    lon_scale = np.cos(np.radians(avg_lat)) * R * np.pi / 180
    
    # 1度纬度对应的距离 (米)
    lat_scale = R * np.pi / 180
    
    # 找到最小经纬度作为原点
    min_lon = min(p["longitude"] for p in points)
    min_lat = min(p["latitude"] for p in points)
    
    # 转换坐标为米，相对于原点
    local_coords = []
    for p in points:
        x = (p["longitude"] - min_lon) * lon_scale
        y = (p["latitude"] - min_lat) * lat_scale
        local_coords.append((x, y))
    
    return local_coords

def calculate_triangle_area(p1, p2, p3):
    """
    计算三角形面积
    
    参数:
    - p1, p2, p3: 三角形的三个顶点坐标 (x, y)
    
    返回:
    - 面积
    """
    return 0.5 * abs((p1[0]*(p2[1]-p3[1]) + p2[0]*(p3[1]-p1[1]) + p3[0]*(p1[1]-p2[1])))

def calculate_triangular_prism_volume(triangle_points, original_heights, target_heights):
    """
    计算三棱柱体积
    
    参数:
    - triangle_points: 三角形的三个顶点坐标 [(x1, y1), (x2, y2), (x3, y3)]
    - original_heights: 原始高程 [h1, h2, h3]
    - target_heights: 目标高程 [h1', h2', h3']
    
    返回:
    - 体积
    """
    # 计算三角形面积
    area = calculate_triangle_area(triangle_points[0], triangle_points[1], triangle_points[2])
    
    # 计算三个顶点的高程差
    height_diffs = [target_heights[i] - original_heights[i] for i in range(3)]
    
    # 计算平均高程差
    avg_height_diff = sum(height_diffs) / 3
    
    # 计算体积
    volume = area * avg_height_diff
    
    return volume

def is_point_in_polygon(point, polygon_points):
    """
    检查点是否在多边形内
    
    参数:
    - point: 点坐标 (x, y)
    - polygon_points: 多边形顶点坐标列表 [(x1, y1), (x2, y2), ...]
    
    返回:
    - 布尔值，表示点是否在多边形内
    """
    polygon = Polygon(polygon_points)
    point_obj = Point(point)
    return polygon.contains(point_obj)

def generate_tin(points, boundary_polygon=None):
    """
    生成三角不规则网络 (TIN)
    
    参数:
    - points: 点坐标列表 [(x, y), ...]
    - boundary_polygon: 边界多边形顶点坐标列表 [(x1, y1), (x2, y2), ...]
    
    返回:
    - 三角形列表 [(i1, i2, i3), ...] 其中i是points中的索引
    """
    # 转换为numpy数组
    points_array = np.array(points)
    
    # 使用Delaunay三角剖分
    tri = Delaunay(points_array)
    
    # 获取三角形列表
    triangles = tri.simplices.tolist()
    
    # 如果提供了边界多边形，过滤掉边界外的三角形
    if boundary_polygon:
        filtered_triangles = []
        for t in triangles:
            # 计算三角形的中心点
            p1, p2, p3 = points[t[0]], points[t[1]], points[t[2]]
            center_x = (p1[0] + p2[0] + p3[0]) / 3
            center_y = (p1[1] + p2[1] + p3[1]) / 3
            center = (center_x, center_y)
            
            # 检查中心点是否在边界内
            if is_point_in_polygon(center, boundary_polygon):
                filtered_triangles.append(t)
        
        return filtered_triangles
    
    return triangles

@router.post("/calculate-tin", response_model=TINEarthworkCalculationResponse)
async def calculate_tin_earthwork(request: TINEarthworkCalculationRequest):
    """
    使用三角网(TIN)方法计算填挖方量
    
    参数:
    - polygon_coordinates: 外部边界多边形
    - sample_points: 采样点列表，包含原始高程和目标高程
    - calculation_method: 计算方法，"tin"或"grid"
    
    返回:
    - area: 区域面积 (m²)
    - cut_volume: 挖方量 (m³)
    - fill_volume: 填方量 (m³)
    - net_volume: 净体积 (填方 - 挖方) (m³)
    - triangles: 三角形索引列表，用于前端可视化
    """
    try:
        # 检查多边形是否有效
        if len(request.polygon_coordinates) < 3:
            raise HTTPException(status_code=400, detail="多边形至少需要3个顶点")
        
        # 检查采样点是否足够
        if len(request.sample_points) < 3:
            raise HTTPException(status_code=400, detail="至少需要3个采样点才能形成三角网")
        
        # 提取边界多边形坐标
        boundary_points = request.polygon_coordinates
        
        # 计算平均纬度
        avg_lat = sum(p["latitude"] for p in boundary_points) / len(boundary_points)
        
        # 将边界多边形转换为本地坐标
        boundary_local = convert_to_local_coordinates(boundary_points, avg_lat)
        
        # 将采样点转换为本地坐标
        sample_local = convert_to_local_coordinates(request.sample_points, avg_lat)
        
        # 提取原始高程和目标高程
        original_heights = [p.get("original_height", 0) for p in request.sample_points]
        target_heights = [p.get("target_height", 0) for p in request.sample_points]
        
        # 计算区域面积
        boundary_coords = [(p["longitude"], p["latitude"]) for p in boundary_points]
        area = calculate_geographic_area(boundary_coords)
        
        # 根据计算方法选择不同的处理方式
        if request.calculation_method == "tin":
            # 生成三角网
            triangles = generate_tin(sample_local, boundary_local)
            
            # 计算每个三角形的填挖方量
            cut_volume = 0
            fill_volume = 0
            
            for t in triangles:
                # 获取三角形的三个顶点
                triangle_points = [sample_local[i] for i in t]
                
                # 获取三个顶点的原始高程和目标高程
                triangle_original_heights = [original_heights[i] for i in t]
                triangle_target_heights = [target_heights[i] for i in t]
                
                # 计算三角柱体积
                volume = calculate_triangular_prism_volume(
                    triangle_points, 
                    triangle_original_heights, 
                    triangle_target_heights
                )
                
                # 根据体积正负确定是填方还是挖方
                if volume > 0:
                    fill_volume += volume
                else:
                    cut_volume -= volume  # 转为正值
            
            # 计算净体积
            net_volume = fill_volume - cut_volume
            
            # 返回结果
            return {
                "area": round(area, 2),
                "cut_volume": round(cut_volume, 2),
                "fill_volume": round(fill_volume, 2),
                "net_volume": round(net_volume, 2),
                "triangles": triangles,
                "unit": "m³",
                "method": "tin"
            }
        
        elif request.calculation_method == "grid":
            # 网格法计算（简化版，实际应用中可能需要更复杂的实现）
            # 这里仅作为示例，实际应用中可能需要更精确的网格划分
            
            # 创建一个简单的网格
            grid_size = 5  # 5米网格
            
            # 找到边界范围
            min_x = min(p[0] for p in boundary_local)
            min_y = min(p[1] for p in boundary_local)
            max_x = max(p[0] for p in boundary_local)
            max_y = max(p[1] for p in boundary_local)
            
            # 计算网格数量
            grid_count_x = math.ceil((max_x - min_x) / grid_size)
            grid_count_y = math.ceil((max_y - min_y) / grid_size)
            
            # 初始化体积
            cut_volume = 0
            fill_volume = 0
            
            # 遍历网格
            for i in range(grid_count_x):
                for j in range(grid_count_y):
                    # 计算网格中心点
                    center_x = min_x + (i + 0.5) * grid_size
                    center_y = min_y + (j + 0.5) * grid_size
                    center = (center_x, center_y)
                    
                    # 检查中心点是否在边界内
                    if is_point_in_polygon(center, boundary_local):
                        # 找到最近的采样点，计算高程差
                        # 这里使用简单的最近邻插值，实际应用中可能需要更复杂的插值方法
                        nearest_idx = min(range(len(sample_local)), 
                                         key=lambda i: (sample_local[i][0] - center_x)**2 + 
                                                      (sample_local[i][1] - center_y)**2)
                        
                        # 获取原始高程和目标高程
                        original_height = original_heights[nearest_idx]
                        target_height = target_heights[nearest_idx]
                        
                        # 计算高程差
                        height_diff = target_height - original_height
                        
                        # 计算网格体积
                        volume = grid_size * grid_size * height_diff
                        
                        # 根据体积正负确定是填方还是挖方
                        if volume > 0:
                            fill_volume += volume
                        else:
                            cut_volume -= volume  # 转为正值
            
            # 计算净体积
            net_volume = fill_volume - cut_volume
            
            # 返回结果
            return {
                "area": round(area, 2),
                "cut_volume": round(cut_volume, 2),
                "fill_volume": round(fill_volume, 2),
                "net_volume": round(net_volume, 2),
                "triangles": [],  # 网格法不返回三角形
                "unit": "m³",
                "method": "grid"
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的计算方法: {request.calculation_method}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算填挖方量时出错: {str(e)}")

@router.post("/generate-sample-points")
async def generate_sample_points(request: dict):
    """
    在多边形区域内生成采样点网格
    
    参数:
    - polygon_coordinates: 多边形顶点坐标列表 [{"longitude": x, "latitude": y}, ...]
    - grid_size: 网格大小（米）
    - original_height: 默认原始高程
    - target_height: 默认目标高程
    
    返回:
    - sample_points: 采样点列表 [{"longitude": x, "latitude": y, "original_height": z1, "target_height": z2}, ...]
    """
    try:
        coordinates = request.get("polygon_coordinates", [])
        grid_size = request.get("grid_size", 10)  # 默认10米网格
        original_height = request.get("original_height", 0)
        target_height = request.get("target_height", 0)
        
        if len(coordinates) < 3:
            return {"error": "多边形至少需要3个顶点"}
        
        # 提取多边形坐标
        polygon_points = [(point["longitude"], point["latitude"]) for point in coordinates]
        
        # 创建Shapely多边形
        polygon = Polygon(polygon_points)
        
        if not polygon.is_valid:
            return {"error": "多边形无效，可能存在自相交"}
        
        # 计算平均纬度
        avg_lat = sum(point["latitude"] for point in coordinates) / len(coordinates)
        
        # 将多边形转换为本地坐标
        local_coords = convert_to_local_coordinates(coordinates, avg_lat)
        
        # 找到边界范围
        min_x = min(p[0] for p in local_coords)
        min_y = min(p[1] for p in local_coords)
        max_x = max(p[0] for p in local_coords)
        max_y = max(p[1] for p in local_coords)
        
        # 计算网格数量
        grid_count_x = math.ceil((max_x - min_x) / grid_size)
        grid_count_y = math.ceil((max_y - min_y) / grid_size)
        
        # 生成网格点
        sample_points = []
        
        # 地球半径 (米)
        R = 6371000
        
        # 在平均纬度下，1米对应的经度变化
        lon_scale = 1 / (np.cos(np.radians(avg_lat)) * R * np.pi / 180)
        
        # 1米对应的纬度变化
        lat_scale = 1 / (R * np.pi / 180)
        
        # 找到最小经纬度作为原点
        min_lon = min(p["longitude"] for p in coordinates)
        min_lat = min(p["latitude"] for p in coordinates)
        
        # 遍历网格
        for i in range(grid_count_x + 1):
            for j in range(grid_count_y + 1):
                # 计算本地坐标
                x = min_x + i * grid_size
                y = min_y + j * grid_size
                
                # 检查点是否在多边形内
                if is_point_in_polygon((x, y), local_coords):
                    # 转换回经纬度坐标
                    lon = min_lon + x * lon_scale
                    lat = min_lat + y * lat_scale
                    
                    # 添加采样点
                    sample_points.append({
                        "longitude": lon,
                        "latitude": lat,
                        "original_height": original_height,
                        "target_height": target_height
                    })
        
        return {
            "sample_points": sample_points,
            "count": len(sample_points)
        }
    
    except Exception as e:
        return {"error": f"生成采样点时出错: {str(e)}"}

@router.post("/validate-polygon")
async def validate_polygon(coordinates: List[Dict[str, float]]):
    """
    验证多边形是否有效
    
    参数:
    - coordinates: 多边形顶点坐标列表 [{"longitude": x, "latitude": y}, ...]
    
    返回:
    - is_valid: 多边形是否有效
    - message: 验证消息
    """
    try:
        if len(coordinates) < 3:
            return {"is_valid": False, "message": "多边形至少需要3个顶点"}
        
        # 提取多边形坐标
        polygon_points = [(point["longitude"], point["latitude"]) for point in coordinates]
        
        # 创建Shapely多边形
        polygon = Polygon(polygon_points)
        
        if not polygon.is_valid:
            return {"is_valid": False, "message": "多边形无效，可能存在自相交"}
        
        # 计算面积
        area = calculate_geographic_area(polygon_points)
        
        return {
            "is_valid": True, 
            "message": "多边形有效", 
            "area": round(area, 2),
            "unit": "m²"
        }
    
    except Exception as e:
        return {"is_valid": False, "message": f"验证多边形时出错: {str(e)}"}