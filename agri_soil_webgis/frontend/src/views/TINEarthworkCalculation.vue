<script setup>
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue';
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus';
import * as Cesium from 'cesium';
import { 
  calculateTINEarthwork, 
  generateSamplePoints, 
  validatePolygon 
} from '../services/earthworkService';

// 状态变量
const viewer = ref(null);
const isDrawing = ref(false);
const isCalculating = ref(false);
const drawingMode = ref('polygon'); // polygon, line, point
const calculationResults = ref(null);
const activeTab = ref('draw');
const calculationMethod = ref('tin'); // tin, grid
const gridSize = ref(10); // 默认10米网格
const samplePoints = ref([]);
const triangles = ref([]);
const isEditingSamplePoints = ref(false);
const selectedSamplePointIndex = ref(-1);
const isGeneratingSamplePoints = ref(false);

// 绘制工具状态
const drawingTools = reactive({
  handler: null,
  entities: [],
  positions: [],
  polygon: null
});

// 采样点状态
const samplePointsState = reactive({
  entities: [],
  triangleEntities: []
});

// 计算结果
const results = reactive({
  area: 0,
  cutVolume: 0,
  fillVolume: 0,
  netVolume: 0,
  unit: 'm³'
});

// 计算方法选项
const calculationMethodOptions = [
  { label: '三角网(TIN)方法', value: 'tin' },
  { label: '网格法', value: 'grid' }
];

// 计算采样点数量
const samplePointsCount = computed(() => {
  return samplePoints.value.length;
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
  
  // 验证多边形
  validateDrawnPolygon();
  
  ElMessage.success('区域绘制完成，现在可以生成采样点');
  activeTab.value = 'sample';
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
    const validationResult = await validatePolygon(polygonCoordinates);
    
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
  
  // 清除采样点
  clearSamplePoints();
  
  // 重置结果
  results.area = 0;
  results.cutVolume = 0;
  results.fillVolume = 0;
  results.netVolume = 0;
  
  calculationResults.value = null;
  samplePoints.value = [];
  triangles.value = [];
};

// 清除采样点
const clearSamplePoints = () => {
  // 清除采样点实体
  samplePointsState.entities.forEach(entity => {
    viewer.value.entities.remove(entity);
  });
  samplePointsState.entities = [];
  
  // 清除三角形实体
  samplePointsState.triangleEntities.forEach(entity => {
    viewer.value.entities.remove(entity);
  });
  samplePointsState.triangleEntities = [];
};

// 生成采样点
const generateSamplePointsGrid = async () => {
  if (drawingTools.positions.length < 3) {
    ElMessage.warning('请先绘制一个有效的区域');
    return;
  }
  
  isGeneratingSamplePoints.value = true;
  
  try {
    // 清除之前的采样点
    clearSamplePoints();
    
    // 将Cartesian坐标转换为经纬度坐标
    const polygonCoordinates = drawingTools.positions.map(position => {
      const cartographic = Cesium.Cartographic.fromCartesian(position);
      return {
        longitude: Cesium.Math.toDegrees(cartographic.longitude),
        latitude: Cesium.Math.toDegrees(cartographic.latitude)
      };
    });
    
    // 调用API生成采样点
    const result = await generateSamplePoints(
      polygonCoordinates, 
      gridSize.value,
      0, // 默认原始高程
      0  // 默认目标高程
    );
    
    if (result.error) {
      ElMessage.error(`生成采样点时出错: ${result.error}`);
      return;
    }
    
    // 更新采样点
    samplePoints.value = result.sample_points;
    
    // 在地图上显示采样点
    visualizeSamplePoints();
    
    ElMessage.success(`成功生成 ${result.count} 个采样点`);
  } catch (error) {
    console.error('生成采样点时出错:', error);
    ElMessage.error('生成采样点时出错，请重试');
  } finally {
    isGeneratingSamplePoints.value = false;
  }
};

// 可视化采样点
const visualizeSamplePoints = () => {
  // 清除之前的采样点
  clearSamplePoints();
  
  // 添加新的采样点
  samplePoints.value.forEach((point, index) => {
    const position = Cesium.Cartesian3.fromDegrees(
      point.longitude, 
      point.latitude, 
      point.original_height
    );
    
    const entity = viewer.value.entities.add({
      position: position,
      point: {
        color: Cesium.Color.GREEN,
        pixelSize: 8,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 1,
        heightReference: Cesium.HeightReference.NONE
      },
      label: {
        text: `${index}`,
        font: '12px sans-serif',
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -10),
        show: false // 默认不显示标签
      }
    });
    
    // 添加点击事件
    entity.index = index;
    
    samplePointsState.entities.push(entity);
  });
  
  // 调整视图以查看所有采样点
  viewer.value.zoomTo(viewer.value.entities);
};

// 可视化三角网
const visualizeTriangles = () => {
  // 清除之前的三角形
  samplePointsState.triangleEntities.forEach(entity => {
    viewer.value.entities.remove(entity);
  });
  samplePointsState.triangleEntities = [];
  
  // 如果没有三角形数据，返回
  if (!triangles.value || triangles.value.length === 0) return;
  
  // 添加新的三角形
  triangles.value.forEach(triangle => {
    // 获取三角形的三个顶点
    const p1 = samplePoints.value[triangle[0]];
    const p2 = samplePoints.value[triangle[1]];
    const p3 = samplePoints.value[triangle[2]];
    
    // 创建三角形实体
    const entity = viewer.value.entities.add({
      polygon: {
        hierarchy: new Cesium.PolygonHierarchy([
          Cesium.Cartesian3.fromDegrees(p1.longitude, p1.latitude, p1.original_height),
          Cesium.Cartesian3.fromDegrees(p2.longitude, p2.latitude, p2.original_height),
          Cesium.Cartesian3.fromDegrees(p3.longitude, p3.latitude, p3.original_height)
        ]),
        material: new Cesium.ColorMaterialProperty(Cesium.Color.YELLOW.withAlpha(0.3)),
        outline: true,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 1,
        heightReference: Cesium.HeightReference.NONE
      }
    });
    
    samplePointsState.triangleEntities.push(entity);
  });
};

// 开始编辑采样点
const startEditingSamplePoints = () => {
  if (samplePoints.value.length === 0) {
    ElMessage.warning('没有可编辑的采样点');
    return;
  }
  
  isEditingSamplePoints.value = true;
  
  // 显示所有采样点的标签
  samplePointsState.entities.forEach(entity => {
    entity.label.show = true;
  });
  
  // 添加点击事件处理器
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.value.canvas);
  
  handler.setInputAction((click) => {
    const pickedObject = viewer.value.scene.pick(click.position);
    if (Cesium.defined(pickedObject) && 
        pickedObject.id && 
        typeof pickedObject.id.index === 'number') {
      
      selectedSamplePointIndex.value = pickedObject.id.index;
      
      // 打开编辑对话框
      ElMessageBox.prompt(
        `编辑采样点 #${selectedSamplePointIndex.value} 的高程值`,
        '编辑采样点',
        {
          confirmButtonText: '保存',
          cancelButtonText: '取消',
          inputType: 'text',
          inputValue: `原始高程: ${samplePoints.value[selectedSamplePointIndex.value].original_height}, 目标高程: ${samplePoints.value[selectedSamplePointIndex.value].target_height}`,
          inputPattern: /原始高程:\s*(-?\d+(\.\d+)?),\s*目标高程:\s*(-?\d+(\.\d+)?)/,
          inputErrorMessage: '格式无效，请使用 "原始高程: 数值, 目标高程: 数值" 格式'
        }
      ).then(({ value }) => {
        // 解析输入值
        const match = value.match(/原始高程:\s*(-?\d+(\.\d+)?),\s*目标高程:\s*(-?\d+(\.\d+)?)/);
        if (match) {
          const originalHeight = parseFloat(match[1]);
          const targetHeight = parseFloat(match[3]);
          
          // 更新采样点高程
          samplePoints.value[selectedSamplePointIndex.value].original_height = originalHeight;
          samplePoints.value[selectedSamplePointIndex.value].target_height = targetHeight;
          
          // 更新可视化
          updateSamplePointVisualization(selectedSamplePointIndex.value);
          
          ElMessage.success(`采样点 #${selectedSamplePointIndex.value} 高程已更新`);
        }
      }).catch(() => {
        // 取消编辑
      });
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
  
  // 保存处理器以便后续清理
  drawingTools.handler = handler;
  
  ElMessage.success('点击采样点进行编辑，完成后点击"完成编辑"按钮');
};

// 完成编辑采样点
const finishEditingSamplePoints = () => {
  isEditingSamplePoints.value = false;
  
  // 隐藏所有采样点的标签
  samplePointsState.entities.forEach(entity => {
    entity.label.show = false;
  });
  
  // 清理点击事件处理器
  if (drawingTools.handler) {
    drawingTools.handler.destroy();
    drawingTools.handler = null;
  }
  
  ElMessage.success('采样点编辑已完成');
};

// 更新采样点可视化
const updateSamplePointVisualization = (index) => {
  const point = samplePoints.value[index];
  const entity = samplePointsState.entities[index];
  
  if (entity) {
    // 更新位置
    entity.position = Cesium.Cartesian3.fromDegrees(
      point.longitude, 
      point.latitude, 
      point.original_height
    );
  }
};

// 批量设置高程
const batchSetElevation = () => {
  if (samplePoints.value.length === 0) {
    ElMessage.warning('没有可设置的采样点');
    return;
  }
  
  ElMessageBox.prompt(
    '请输入要设置的高程值',
    '批量设置高程',
    {
      confirmButtonText: '设置',
      cancelButtonText: '取消',
      inputType: 'text',
      inputValue: `原始高程: 0, 目标高程: 0`,
      inputPattern: /原始高程:\s*(-?\d+(\.\d+)?),\s*目标高程:\s*(-?\d+(\.\d+)?)/,
      inputErrorMessage: '格式无效，请使用 "原始高程: 数值, 目标高程: 数值" 格式'
    }
  ).then(({ value }) => {
    // 解析输入值
    const match = value.match(/原始高程:\s*(-?\d+(\.\d+)?),\s*目标高程:\s*(-?\d+(\.\d+)?)/);
    if (match) {
      const originalHeight = parseFloat(match[1]);
      const targetHeight = parseFloat(match[3]);
      
      // 更新所有采样点高程
      samplePoints.value.forEach((point, index) => {
        point.original_height = originalHeight;
        point.target_height = targetHeight;
        
        // 更新可视化
        updateSamplePointVisualization(index);
      });
      
      ElMessage.success(`已批量设置 ${samplePoints.value.length} 个采样点的高程`);
    }
  }).catch(() => {
    // 取消设置
  });
};

// 计算填挖方量
const calculateEarthwork = async () => {
  if (drawingTools.positions.length < 3) {
    ElMessage.warning('请先绘制一个有效的区域');
    return;
  }
  
  if (samplePoints.value.length < 3) {
    ElMessage.warning('至少需要3个采样点才能进行计算');
    return;
  }
  
  isCalculating.value = true;
  
  try {
    // 将Cartesian坐标转换为经纬度坐标
    const polygonCoordinates = drawingTools.positions.map(position => {
      const cartographic = Cesium.Cartographic.fromCartesian(position);
      return {
        longitude: Cesium.Math.toDegrees(cartographic.longitude),
        latitude: Cesium.Math.toDegrees(cartographic.latitude)
      };
    });
    
    // 调用API计算填挖方量
    const apiResult = await calculateTINEarthwork(
      polygonCoordinates,
      samplePoints.value,
      calculationMethod.value
    );
    
    // 更新结果
    results.area = apiResult.area;
    results.cutVolume = apiResult.cut_volume;
    results.fillVolume = apiResult.fill_volume;
    results.netVolume = apiResult.net_volume;
    
    // 更新三角形数据
    triangles.value = apiResult.triangles;
    
    // 显示结果
    calculationResults.value = { ...results };
    
    // 可视化三角网
    if (calculationMethod.value === 'tin') {
      visualizeTriangles();
    }
    
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
    `净体积(填-挖),${results.netVolume},m³`,
    `计算方法,${calculationMethod.value === 'tin' ? '三角网(TIN)' : '网格法'}`,
    `采样点数量,${samplePoints.value.length}`
  ].join('\n');
  
  // 创建Blob对象
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  
  // 创建下载链接
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', '三角网填挖方计算结果.csv');
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
    activeTab.value = 'draw';
    
    ElMessage.success('已重置计算');
  }).catch(() => {
    // 取消重置
  });
};
</script>

<template>
  <div class="tin-earthwork-calculation">
    <el-row :gutter="20">
      <el-col :span="18">
        <div id="cesiumContainer" class="cesium-container"></div>
        <div id="coordinateInfo" class="coordinate-info"></div>
      </el-col>
      <el-col :span="6">
        <el-card class="control-panel">
          <template #header>
            <div class="card-header">
              <span>三角网(TIN)填挖方计算工具</span>
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
                    <li>绘制完成后生成采样点</li>
                  </ul>
                </div>
              </div>
            </el-tab-pane>
            
            <!-- 采样点面板 -->
            <el-tab-pane label="采样点设置" name="sample">
              <div class="tab-content">
                <p>生成和编辑采样点</p>
                
                <el-form label-position="top">
                  <el-form-item label="网格大小 (米)">
                    <el-input-number 
                      v-model="gridSize" 
                      :min="1" 
                      :max="100"
                      :step="1"
                      class="full-width"
                    />
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button 
                      type="primary" 
                      @click="generateSamplePointsGrid" 
                      :loading="isGeneratingSamplePoints"
                      class="action-button"
                    >
                      生成采样点网格
                    </el-button>
                  </el-form-item>
                  
                  <el-divider content-position="center">采样点操作</el-divider>
                  
                  <div class="sample-points-info">
                    <p>当前采样点数量: {{ samplePointsCount }}</p>
                  </div>
                  
                  <el-form-item v-if="samplePointsCount > 0">
                    <el-button 
                      v-if="!isEditingSamplePoints" 
                      type="primary" 
                      @click="startEditingSamplePoints"
                      class="action-button"
                    >
                      编辑采样点高程
                    </el-button>
                    <el-button 
                      v-else 
                      type="success" 
                      @click="finishEditingSamplePoints"
                      class="action-button"
                    >
                      完成编辑
                    </el-button>
                  </el-form-item>
                  
                  <el-form-item v-if="samplePointsCount > 0">
                    <el-button 
                      type="warning" 
                      @click="batchSetElevation"
                      class="action-button"
                    >
                      批量设置高程
                    </el-button>
                  </el-form-item>
                </el-form>
                
                <div class="instruction" v-if="isEditingSamplePoints">
                  <p><strong>编辑说明：</strong></p>
                  <ul>
                    <li>点击采样点进行编辑</li>
                    <li>输入格式: "原始高程: 数值, 目标高程: 数值"</li>
                    <li>完成后点击"完成编辑"按钮</li>
                  </ul>
                </div>
                
                <el-button 
                  type="primary" 
                  @click="activeTab = 'calculate'"
                  :disabled="samplePointsCount < 3"
                  class="action-button"
                >
                  下一步: 计算设置
                </el-button>
              </div>
            </el-tab-pane>
            
            <!-- 计算设置面板 -->
            <el-tab-pane label="计算设置" name="calculate">
              <div class="tab-content">
                <p>设置计算参数</p>
                
                <el-form label-position="top">
                  <el-form-item label="计算方法">
                    <el-radio-group v-model="calculationMethod">
                      <el-radio 
                        v-for="option in calculationMethodOptions" 
                        :key="option.value" 
                        :label="option.value"
                      >
                        {{ option.label }}
                      </el-radio>
                    </el-radio-group>
                  </el-form-item>
                </el-form>
                
                <div class="method-description">
                  <template v-if="calculationMethod === 'tin'">
                    <p><strong>三角网(TIN)方法:</strong></p>
                    <p>使用Delaunay三角剖分生成三角网，计算每个三角柱的体积。适用于复杂地形，精度高。</p>
                  </template>
                  <template v-else>
                    <p><strong>网格法:</strong></p>
                    <p>将区域划分为规则网格，计算每个网格的体积。计算速度快，适用于较平坦地形。</p>
                  </template>
                </div>
                
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
                  
                  <div class="result-item">
                    <span class="result-label">计算方法:</span>
                    <span class="result-value">
                      {{ calculationMethod === 'tin' ? '三角网(TIN)' : '网格法' }}
                    </span>
                  </div>
                  
                  <div class="result-item">
                    <span class="result-label">采样点数量:</span>
                    <span class="result-value">{{ samplePointsCount }}</span>
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
.tin-earthwork-calculation {
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

.sample-points-info {
  background-color: #f0f9eb;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
}

.method-description {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin: 15px 0;
  font-size: 14px;
}
</style>