import axios from 'axios';

// API基础URL
const API_URL = 'http://localhost:12001/api/earthwork';

/**
 * 计算填挖方量
 * @param {Array} polygonCoordinates - 多边形顶点坐标数组 [{longitude, latitude, height}, ...]
 * @param {Number} originalHeight - 原始地面高程
 * @param {Number} targetHeight - 目标地面高程
 * @returns {Promise} - 返回计算结果的Promise
 */
export const calculateEarthwork = async (polygonCoordinates, originalHeight, targetHeight) => {
  try {
    const response = await axios.post(`${API_URL}/calculate`, {
      polygon_coordinates: polygonCoordinates,
      original_height: originalHeight,
      target_height: targetHeight
    });
    
    return response.data;
  } catch (error) {
    console.error('计算填挖方量时出错:', error);
    throw error;
  }
};

/**
 * 验证多边形是否有效
 * @param {Array} coordinates - 多边形顶点坐标数组 [{longitude, latitude}, ...]
 * @returns {Promise} - 返回验证结果的Promise
 */
export const validatePolygon = async (coordinates) => {
  try {
    const response = await axios.post(`${API_URL}/validate-polygon`, coordinates);
    return response.data;
  } catch (error) {
    console.error('验证多边形时出错:', error);
    throw error;
  }
};

export default {
  calculateEarthwork,
  validatePolygon
};