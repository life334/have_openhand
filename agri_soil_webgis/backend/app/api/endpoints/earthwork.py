from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import numpy as np
from shapely.geometry import Polygon, Point
import json

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