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
 * 使用三角网(TIN)方法计算填挖方量
 * @param {Array} polygonCoordinates - 多边形顶点坐标数组 [{longitude, latitude}, ...]
 * @param {Array} samplePoints - 采样点数组 [{longitude, latitude, original_height, target_height}, ...]
 * @param {String} calculationMethod - 计算方法，"tin"或"grid"
 * @returns {Promise} - 返回计算结果的Promise
 */
export const calculateTINEarthwork = async (polygonCoordinates, samplePoints, calculationMethod = "tin") => {
  try {
    const response = await axios.post(`${API_URL}/calculate-tin`, {
      polygon_coordinates: polygonCoordinates,
      sample_points: samplePoints,
      calculation_method: calculationMethod
    });
    
    return response.data;
  } catch (error) {
    console.error('使用三角网计算填挖方量时出错:', error);
    throw error;
  }
};

/**
 * 生成采样点网格
 * @param {Array} polygonCoordinates - 多边形顶点坐标数组 [{longitude, latitude}, ...]
 * @param {Number} gridSize - 网格大小（米）
 * @param {Number} originalHeight - 默认原始高程
 * @param {Number} targetHeight - 默认目标高程
 * @returns {Promise} - 返回采样点数组的Promise
 */
export const generateSamplePoints = async (polygonCoordinates, gridSize = 10, originalHeight = 0, targetHeight = 0) => {
  try {
    const response = await axios.post(`${API_URL}/generate-sample-points`, {
      polygon_coordinates: polygonCoordinates,
      grid_size: gridSize,
      original_height: originalHeight,
      target_height: targetHeight
    });
    
    return response.data;
  } catch (error) {
    console.error('生成采样点网格时出错:', error);
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
  calculateTINEarthwork,
  generateSamplePoints,
  validatePolygon
};