<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import * as Cesium from 'cesium';
import axios from 'axios';

// 状态变量
const cesiumContainer = ref(null);
const viewer = ref(null);
const isDrawing = ref(false);
const isCalculating = ref(false);
const activeTab = ref('draw');
const originalHeight = ref(0);
const targetHeight = ref(0);
const calculationResults = ref(null);

// 绘制工具状态
const drawingTools = reactive({
  handler: null,
  entities: [],
  positions: [],
  polygon: null
});

// 计算结果
const results = reactive({
  area: 0,
  cutVolume: 0,
  fillVolume: 0,
  netVolume: 0,
  unit: 'm³'
});

// 初始化 Cesium 查看器
const initCesium = () => {
  if (viewer.value) return;
  
  // 配置 Cesium ion 访问令牌
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYTIzNTY3ZS01MWJmLTQzYjEtYjE0OS1kODVkMTY2NDRlODIiLCJpZCI6OTYyMCwic2NvcGVzIjpbImFzciIsImdjIl0sImlhdCI6MTU1MzIyODM0OX0.aW0_PLxl0L_UtZXizVSXciJGomjLNpOw8PFXLnXYFYw';
  
  // 创建 Cesium 查看器
  viewer.value = new Cesium.Viewer(cesiumContainer.value, {
    terrainProvider: Cesium.createWorldTerrain(),
    animation: false,
    baseLayerPicker: true,
    fullscreenButton: true,
    vrButton: false,
    geocoder: true,
    homeButton: true,
    infoBox: true,
    sceneModePicker: true,
    selectionIndicator: true,
    timeline: false,
    navigationHelpButton: true,
    navigationInstructionsInitiallyVisible: false,
    scene3DOnly: false,
    shouldAnimate: true
  });
  
  // 启用地形深度测试
  viewer.value.scene.globe.depthTestAgainstTerrain = true;
  
  // 设置默认视图到中国
  viewer.value.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(116.4, 39.9, 5000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-45),
      roll: 0.0
    }
  });
  
  // 添加地形图层
  const terrainProvider = Cesium.createWorldTerrain({
    requestVertexNormals: true,
    requestWaterMask: true
  });
  viewer.value.terrainProvider = terrainProvider;
  
  // 添加地形高度读取功能
  viewer.value.screenSpaceEventHandler.add(
    new Cesium.ScreenSpaceEventHandler(viewer.value.canvas)
  );
  
  viewer.value.screenSpaceEventHandler.setInputAction((movement) => {
    if (!isDrawing.value) return;
    
    const cartesian = viewer.value.scene.pickPosition(movement.endPosition);
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
};

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
  
  // 验证多边形
  validateDrawnPolygon();
  
  ElMessage.success('区域绘制完成，现在可以设置高程参数');
  activeTab.value = 'params';
};

// 验证绘制的多边形
const validateDrawnPolygon = async () => {
  try {
    // 将Cartesian坐标转换为经纬度坐标
    const polygonCoordinates = drawingTools.positions.map(position => {
      const cartographic = Cesium.Cartographic.fromCartesian(position);
      return {
        longitude: Cesium.Math.toDegrees(cartographic.longitude),
        latitude: Cesium.Math.toDegrees(cartographic.latitude)
      };
    });
    
    // 调用API验证多边形
    // 在实际应用中，这里会调用后端API
    // const response = await axios.post('http://localhost:12001/api/earthwork/validate-polygon', polygonCoordinates);
    
    // 模拟验证结果
    const validationResult = {
      is_valid: true,
      area: 10000 // 平方米
    };
    
    if (validationResult.is_valid) {
      results.area = validationResult.area;
      ElMessage.success(`多边形有效，面积: ${results.area} m²`);
    } else {
      ElMessage.warning(`多边形无效: ${validationResult.message}`);
    }
  } catch (error) {
    console.error('验证多边形时出错:', error);
    ElMessage.error('验证多边形时出错，请重试');
  }
};

// 清除绘制
const clearDrawing = () => {
  // 清除多边形和顶点
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

// 计算填挖方量
const calculateEarthwork = async () => {
  if (drawingTools.positions.length < 3) {
    ElMessage.warning('请先绘制一个有效的区域');
    return;
  }
  
  if (originalHeight.value === targetHeight.value) {
    ElMessage.warning('原始高程和目标高程相同，无需计算');
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
    
    // 调用API计算填挖方量
    // 在实际应用中，这里会调用后端API
    // const response = await axios.post('http://localhost:12001/api/earthwork/calculate', {
    //   polygon_coordinates: polygonCoordinates,
    //   original_height: originalHeight.value,
    //   target_height: targetHeight.value
    // });
    
    // 模拟计算结果
    const apiResult = {
      area: results.area,
      cut_volume: originalHeight.value > targetHeight.value ? results.area * (originalHeight.value - targetHeight.value) : 0,
      fill_volume: targetHeight.value > originalHeight.value ? results.area * (targetHeight.value - originalHeight.value) : 0,
      net_volume: results.area * (targetHeight.value - originalHeight.value)
    };
    
    // 更新结果
    results.cutVolume = apiResult.cut_volume;
    results.fillVolume = apiResult.fill_volume;
    results.netVolume = apiResult.net_volume;
    
    // 显示结果
    calculationResults.value = { ...results };
    
    ElMessage.success('填挖方计算完成');
    activeTab.value = 'results';
  } catch (error) {
    console.error('计算填挖方量时出错:', error);
    ElMessage.error('计算过程中出错，请重试');
  } finally {
    isCalculating.value = false;
  }
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
    `净体积(填-挖),${results.netVolume},m³`
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
    originalHeight.value = 0;
    targetHeight.value = 0;
    activeTab.value = 'draw';
    
    ElMessage.success('已重置计算');
  }).catch(() => {
    // 取消重置
  });
};

// 组件挂载时初始化 Cesium
onMounted(() => {
  initCesium();
});

// 组件卸载时销毁 Cesium 查看器
onUnmounted(() => {
  if (viewer.value) {
    viewer.value.destroy();
    viewer.value = null;
  }
});
</script>

<template>
  <div class="earthwork-calculation">
    <el-row :gutter="20">
      <el-col :span="18">
        <div ref="cesiumContainer" class="cesium-container"></div>
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
                    <li>绘制完成后设置高程参数</li>
                  </ul>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- 参数设置面板 -->
            <el-tab-pane label="高程参数" name="params">
              <div class="tab-content">
                <p>设置原始高程和目标高程</p>
                <el-form label-position="top">
                  <el-form-item label="原始高程 (米)">
                    <el-input-number 
                      v-model="originalHeight" 
                      :precision="2" 
                      :step="0.1"
                      class="full-width"
                    />
                  </el-form-item>
                  <el-form-item label="目标高程 (米)">
                    <el-input-number 
                      v-model="targetHeight" 
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
                <div class="instruction">
                  <p><strong>参数说明：</strong></p>
                  <ul>
                    <li>原始高程：当前地面高程</li>
                    <li>目标高程：计划地面高程</li>
                    <li>目标高程 > 原始高程：需要填方</li>
                    <li>目标高程 < 原始高程：需要挖方</li>
                  </ul>
                </div>
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