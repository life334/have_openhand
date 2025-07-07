<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import * as Cesium from 'cesium';
import { calculateEarthwork as apiCalculateEarthwork, validatePolygon } from '../services/earthworkService';

// 状态变量
const viewer = ref(null);
const isDrawing = ref(false);
const isCalculating = ref(false);
const drawingMode = ref('polygon'); // polygon, line, point
const calculationResults = ref(null);
const originalSurface = ref(null);
const targetSurface = ref(null);
const activeTab = ref('draw');

// 绘制工具状态
const drawingTools = reactive({
  handler: null,
  entities: [],
  positions: [],
  polygon: null,
  originalHeight: 0,
  targetHeight: 0
});

// 计算结果
const results = reactive({
  area: 0,
  cutVolume: 0,
  fillVolume: 0,
  netVolume: 0,
  unit: 'm³'
});

// 初始化Cesium查看器
onMounted(() => {
  // 配置Cesium访问令牌
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYTIzNTY3ZS01MWJmLTQzYjEtYjE0OS1kODVkMTY2NDRlODIiLCJpZCI6OTYyMCwic2NvcGVzIjpbImFzciIsImdjIl0sImlhdCI6MTU1MzIyODM0OX0.aW0_PLxl0L_UtZXizVSXciJGomjLNpOw8PFXLnXYFYw';

  // 创建Cesium查看器
  viewer.value = new Cesium.Viewer('cesiumContainer', {
    terrainProvider: Cesium.createWorldTerrain(),
    timeline: false,
    animation: false,
    baseLayerPicker: true,
    geocoder: true,
    homeButton: true,
    sceneModePicker: true,
    navigationHelpButton: true,
    infoBox: true,
    fullscreenButton: true
  });

  // 启用地形深度测试，以便正确渲染地形上的多边形
  viewer.value.scene.globe.depthTestAgainstTerrain = true;

  // 设置初始视图位置（可以根据需要调整）
  viewer.value.camera.setView({
    destination: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 5000), // 北京附近
    orientation: {
      heading: 0.0,
      pitch: -Cesium.Math.PI_OVER_TWO / 2,
      roll: 0.0
    }
  });

  // 添加地形高度读取功能
  viewer.value.screenSpaceEventHandler.setInputAction((movement) => {
    if (!isDrawing.value) return;
    
    const cartesian = viewer.value.scene.pickPosition(movement.position);
    if (Cesium.defined(cartesian)) {
      const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
      const height = cartographic.height;
      const longitude = Cesium.Math.toDegrees(cartographic.longitude);
      const latitude = Cesium.Math.toDegrees(cartographic.latitude);
      
      // 更新状态显示
      document.getElementById('coordinateInfo').innerText = 
        `经度: ${longitude.toFixed(6)}, 纬度: ${latitude.toFixed(6)}, 高度: ${height.toFixed(2)}m`;
    }
  }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);
});

// 组件卸载时清理资源
onUnmounted(() => {
  if (viewer.value) {
    viewer.value.destroy();
    viewer.value = null;
  }
});

// 开始绘制多边形
const startDrawing = () => {
  if (!viewer.value) return;
  
  isDrawing.value = true;
  drawingTools.positions = [];
  
  // 清除之前的实体
  clearDrawing();
  
  // 创建绘制处理器
  drawingTools.handler = new Cesium.ScreenSpaceEventHandler(viewer.value.canvas);
  
  // 点击添加点
  drawingTools.handler.setInputAction((click) => {
    const cartesian = viewer.value.scene.pickPosition(click.position);
    if (Cesium.defined(cartesian)) {
      if (drawingTools.positions.length === 0) {
        // 第一个点，创建点实体
        drawingTools.positions.push(cartesian);
        createPoint(cartesian);
        
        // 创建多边形实体
        createPolygon();
      } else {
        // 添加新点
        drawingTools.positions.push(cartesian);
        createPoint(cartesian);
        
        // 更新多边形
        updatePolygon();
      }
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
  
  // 双击完成绘制
  drawingTools.handler.setInputAction((click) => {
    finishDrawing();
  }, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
  
  ElMessage.success('开始绘制区域，单击添加点，双击完成绘制');
};

// 创建点实体
const createPoint = (position) => {
  const point = viewer.value.entities.add({
    position: position,
    point: {
      color: Cesium.Color.WHITE,
      pixelSize: 10,
      outlineColor: Cesium.Color.BLUE,
      outlineWidth: 2,
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    }
  });
  
  drawingTools.entities.push(point);
};

// 创建多边形实体
const createPolygon = () => {
  drawingTools.polygon = viewer.value.entities.add({
    polygon: {
      hierarchy: new Cesium.CallbackProperty(() => {
        return new Cesium.PolygonHierarchy(drawingTools.positions);
      }, false),
      material: new Cesium.ColorMaterialProperty(Cesium.Color.BLUE.withAlpha(0.5)),
      heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
    }
  });
  
  drawingTools.entities.push(drawingTools.polygon);
};

// 更新多边形
const updatePolygon = () => {
  // 多边形通过回调自动更新
};

// 完成绘制
const finishDrawing = () => {
  if (drawingTools.handler) {
    drawingTools.handler.destroy();
    drawingTools.handler = null;
  }
  
  isDrawing.value = false;
  
  if (drawingTools.positions.length < 3) {
    ElMessage.warning('至少需要3个点才能形成有效的多边形');
    clearDrawing();
    return;
  }
  
  // 计算面积
  calculateArea();
  
  ElMessage.success('区域绘制完成，现在可以设置原始高程和目标高程');
  activeTab.value = 'settings';
};

// 清除绘制
const clearDrawing = () => {
  drawingTools.entities.forEach(entity => {
    viewer.value.entities.remove(entity);
  });
  
  drawingTools.entities = [];
  drawingTools.positions = [];
  drawingTools.polygon = null;
  
  // 重置结果
  results.area = 0;
  results.cutVolume = 0;
  results.fillVolume = 0;
  results.netVolume = 0;
  
  calculationResults.value = null;
};

// 计算面积
const calculateArea = () => {
  if (drawingTools.positions.length < 3) return;
  
  // 将Cartesian坐标转换为经纬度坐标
  const positions = drawingTools.positions.map(position => {
    const cartographic = Cesium.Cartographic.fromCartesian(position);
    return {
      longitude: Cesium.Math.toDegrees(cartographic.longitude),
      latitude: Cesium.Math.toDegrees(cartographic.latitude),
      height: cartographic.height
    };
  });
  
  // 使用球面几何计算面积
  const geographicPositions = positions.map(pos => 
    Cesium.Cartographic.fromDegrees(pos.longitude, pos.latitude)
  );
  
  const polygonGeometry = new Cesium.PolygonGeometry({
    polygonHierarchy: new Cesium.PolygonHierarchy(
      Cesium.Ellipsoid.WGS84.cartographicArrayToCartesianArray(geographicPositions)
    )
  });
  
  // 计算面积（平方米）
  results.area = Cesium.PolygonGeometry.computeArea(polygonGeometry);
  
  // 四舍五入到两位小数
  results.area = Math.round(results.area * 100) / 100;
};

// 计算填挖方量
const calculateEarthwork = async () => {
  if (!drawingTools.polygon || drawingTools.positions.length < 3) {
    ElMessage.warning('请先绘制一个有效的区域');
    return;
  }
  
  if (isNaN(drawingTools.originalHeight) || isNaN(drawingTools.targetHeight)) {
    ElMessage.warning('请输入有效的原始高程和目标高程');
    return;
  }
  
  isCalculating.value = true;
  
  try {
    // 将Cartesian坐标转换为经纬度坐标
    const polygonCoordinates = drawingTools.positions.map(position => {
      const cartographic = Cesium.Cartographic.fromCartesian(position);
      return {
        longitude: Cesium.Math.toDegrees(cartographic.longitude),
        latitude: Cesium.Math.toDegrees(cartographic.latitude),
        height: cartographic.height
      };
    });
    
    // 调用后端API计算填挖方量
    const apiResult = await apiCalculateEarthwork(
      polygonCoordinates, 
      drawingTools.originalHeight, 
      drawingTools.targetHeight
    );
    
    // 更新结果
    results.area = apiResult.area;
    results.cutVolume = apiResult.cut_volume;
    results.fillVolume = apiResult.fill_volume;
    results.netVolume = apiResult.net_volume;
    
    // 显示结果
    calculationResults.value = { ...results };
    
    // 计算高度差
    const heightDifference = drawingTools.targetHeight - drawingTools.originalHeight;
    
    // 可视化填挖方区域
    visualizeEarthwork(heightDifference);
    
    ElMessage.success('填挖方计算完成');
    activeTab.value = 'results';
  } catch (error) {
    console.error('计算填挖方量时出错:', error);
    ElMessage.error('计算过程中出错，请重试');
  } finally {
    isCalculating.value = false;
  }
};

// 可视化填挖方区域
const visualizeEarthwork = (heightDifference) => {
  // 移除之前的可视化
  if (originalSurface.value) {
    viewer.value.entities.remove(originalSurface.value);
    originalSurface.value = null;
  }
  
  if (targetSurface.value) {
    viewer.value.entities.remove(targetSurface.value);
    targetSurface.value = null;
  }
  
  // 创建原始表面
  originalSurface.value = viewer.value.entities.add({
    polygon: {
      hierarchy: new Cesium.PolygonHierarchy(drawingTools.positions),
      material: Cesium.Color.RED.withAlpha(0.5),
      height: drawingTools.originalHeight,
      outline: true,
      outlineColor: Cesium.Color.BLACK
    }
  });
  
  // 创建目标表面
  targetSurface.value = viewer.value.entities.add({
    polygon: {
      hierarchy: new Cesium.PolygonHierarchy(drawingTools.positions),
      material: Cesium.Color.GREEN.withAlpha(0.5),
      height: drawingTools.targetHeight,
      outline: true,
      outlineColor: Cesium.Color.BLACK
    }
  });
  
  // 调整视图以查看填挖方区域
  viewer.value.zoomTo(viewer.value.entities);
};

// 导出计算结果
const exportResults = () => {
  if (!calculationResults.value) {
    ElMessage.warning('没有可导出的计算结果');
    return;
  }
  
  // 创建CSV内容
  const csvContent = [
    '参数,数值,单位',
    `区域面积,${results.area},m²`,
    `挖方量,${results.cutVolume},m³`,
    `填方量,${results.fillVolume},m³`,
    `净体积(填-挖),${results.netVolume},m³`,
    `原始高程,${drawingTools.originalHeight},m`,
    `目标高程,${drawingTools.targetHeight},m`
  ].join('\n');
  
  // 创建Blob对象
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  
  // 创建下载链接
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', '填挖方计算结果.csv');
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 重置计算
const resetCalculation = () => {
  ElMessageBox.confirm('确定要重置当前计算吗？这将清除所有绘制和计算结果。', '确认重置', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    clearDrawing();
    drawingTools.originalHeight = 0;
    drawingTools.targetHeight = 0;
    activeTab.value = 'draw';
    
    if (originalSurface.value) {
      viewer.value.entities.remove(originalSurface.value);
      originalSurface.value = null;
    }
    
    if (targetSurface.value) {
      viewer.value.entities.remove(targetSurface.value);
      targetSurface.value = null;
    }
    
    ElMessage.success('已重置计算');
  }).catch(() => {
    // 取消重置
  });
};
</script>

<template>
  <div class="earthwork-calculation">
    <el-row :gutter="20">
      <el-col :span="18">
        <div id="cesiumContainer" class="cesium-container"></div>
        <div id="coordinateInfo" class="coordinate-info"></div>
      </el-col>
      <el-col :span="6">
        <el-card class="control-panel">
          <template #header>
            <div class="card-header">
              <span>填挖方计算工具</span>
            </div>
          </template>
          
          <el-tabs v-model="activeTab" class="control-tabs">
            <!-- 绘制工具面板 -->
            <el-tab-pane label="绘制区域" name="draw">
              <div class="tab-content">
                <p>绘制需要计算填挖方的区域</p>
                <el-button 
                  type="primary" 
                  @click="startDrawing" 
                  :disabled="isDrawing"
                  class="action-button"
                >
                  开始绘制
                </el-button>
                <el-button 
                  type="danger" 
                  @click="clearDrawing" 
                  class="action-button"
                >
                  清除绘制
                </el-button>
                <div class="instruction">
                  <p><strong>操作说明：</strong></p>
                  <ul>
                    <li>单击添加多边形顶点</li>
                    <li>双击完成多边形绘制</li>
                    <li>绘制完成后可设置高程参数</li>
                  </ul>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- 参数设置面板 -->
            <el-tab-pane label="高程设置" name="settings">
              <div class="tab-content">
                <p>设置原始地面和目标地面的高程</p>
                
                <el-form label-position="top">
                  <el-form-item label="原始地面高程 (米)">
                    <el-input-number 
                      v-model="drawingTools.originalHeight" 
                      :precision="2" 
                      :step="0.1"
                      class="full-width"
                    />
                  </el-form-item>
                  
                  <el-form-item label="目标地面高程 (米)">
                    <el-input-number 
                      v-model="drawingTools.targetHeight" 
                      :precision="2" 
                      :step="0.1"
                      class="full-width"
                    />
                  </el-form-item>
                </el-form>
                
                <el-button 
                  type="primary" 
                  @click="calculateEarthwork" 
                  :loading="isCalculating"
                  class="action-button"
                >
                  计算填挖方量
                </el-button>
              </div>
            </el-tab-pane>
            
            <!-- 计算结果面板 -->
            <el-tab-pane label="计算结果" name="results">
              <div class="tab-content">
                <template v-if="calculationResults">
                  <div class="result-item">
                    <span class="result-label">区域面积:</span>
                    <span class="result-value">{{ calculationResults.area }} m²</span>
                  </div>
                  
                  <div class="result-item">
                    <span class="result-label">挖方量:</span>
                    <span class="result-value">{{ calculationResults.cutVolume }} m³</span>
                  </div>
                  
                  <div class="result-item">
                    <span class="result-label">填方量:</span>
                    <span class="result-value">{{ calculationResults.fillVolume }} m³</span>
                  </div>
                  
                  <div class="result-item">
                    <span class="result-label">净体积(填-挖):</span>
                    <span class="result-value" :class="{
                      'positive': calculationResults.netVolume > 0,
                      'negative': calculationResults.netVolume < 0
                    }">
                      {{ calculationResults.netVolume }} m³
                    </span>
                  </div>
                  
                  <div class="result-summary">
                    <p v-if="calculationResults.netVolume > 0">
                      <strong>结论:</strong> 需要填入 {{ calculationResults.netVolume }} m³ 的土方
                    </p>
                    <p v-else-if="calculationResults.netVolume < 0">
                      <strong>结论:</strong> 需要挖出 {{ Math.abs(calculationResults.netVolume) }} m³ 的土方
                    </p>
                    <p v-else>
                      <strong>结论:</strong> 填挖方平衡，无需额外操作
                    </p>
                  </div>
                  
                  <el-button 
                    type="success" 
                    @click="exportResults" 
                    class="action-button"
                  >
                    导出结果
                  </el-button>
                </template>
                
                <template v-else>
                  <p>尚未进行计算或没有有效结果</p>
                </template>
              </div>
            </el-tab-pane>
          </el-tabs>
          
          <div class="control-footer">
            <el-button 
              type="warning" 
              @click="resetCalculation"
              class="reset-button"
            >
              重置计算
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.earthwork-calculation {
  height: 100%;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.cesium-container {
  width: 100%;
  height: calc(100vh - 140px);
  position: relative;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.coordinate-info {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 1000;
}

.control-panel {
  height: calc(100vh - 140px);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-tabs {
  height: 100%;
}

.tab-content {
  padding: 10px 0;
}

.action-button {
  margin-top: 15px;
  width: 100%;
}

.reset-button {
  width: 100%;
}

.instruction {
  margin-top: 20px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
}

.instruction ul {
  padding-left: 20px;
  margin: 5px 0;
}

.full-width {
  width: 100%;
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.result-label {
  font-weight: bold;
}

.result-value {
  font-family: monospace;
}

.result-value.positive {
  color: #67c23a;
}

.result-value.negative {
  color: #f56c6c;
}

.result-summary {
  margin: 15px 0;
  padding: 10px;
  background-color: #ecf5ff;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.control-footer {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}
</style>