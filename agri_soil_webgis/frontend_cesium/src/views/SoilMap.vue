<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue';
import axios from 'axios';
import * as Cesium from 'cesium';

const isLoading = ref(false);
const selectedLayer = ref('soil_type');
const selectedTime = ref('2025');
const cesiumContainer = ref(null);
const viewer = ref(null);

const layers = [
  { value: 'soil_type', label: '土壤类型' },
  { value: 'ph_value', label: 'pH值' },
  { value: 'organic_matter', label: '有机质含量' },
  { value: 'moisture', label: '土壤湿度' },
  { value: 'nutrients', label: '养分含量' }
];

const timeOptions = [
  { value: '2020', label: '2020年' },
  { value: '2021', label: '2021年' },
  { value: '2022', label: '2022年' },
  { value: '2023', label: '2023年' },
  { value: '2024', label: '2024年' },
  { value: '2025', label: '2025年' }
];

const soilData = reactive({
  features: [],
  entities: []
});

// 初始化 Cesium 查看器
const initCesium = () => {
  if (viewer.value) return;
  
  // 配置 Cesium ion 访问令牌
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYTIzNTY3ZS01MWJmLTQzYjEtYjE0OS1kODVkMTY2NDRlODIiLCJpZCI6OTYyMCwic2NvcGVzIjpbImFzciIsImdjIl0sImlhdCI6MTU1MzIyODM0OX0.aW0_PLxl0L_UtZXizVSXciJGomjLNpOw8PFXLnXYFYw';
  
  // 创建 Cesium 查看器
  viewer.value = new Cesium.Viewer(cesiumContainer.value, {
    terrainProvider: Cesium.createWorldTerrainAsync({
      requestVertexNormals: true,
      requestWaterMask: true
    }),
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
    destination: Cesium.Cartesian3.fromDegrees(104.0, 35.0, 10000000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-90),
      roll: 0.0
    }
  });
  
  // 加载土壤数据
  loadSoilData();
};

// 加载土壤数据
const loadSoilData = async () => {
  try {
    isLoading.value = true;
    
    // 清除之前的实体
    clearSoilEntities();
    
    // 在实际应用中，这里会从后端 API 获取数据
    // const response = await axios.get(`http://localhost:12001/api/soil-data/geojson?layer=${selectedLayer.value}&year=${selectedTime.value}`);
    // soilData.features = response.data.features;
    
    // 使用模拟数据
    soilData.features = [
      {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [116.3, 39.9]
        },
        properties: {
          id: 1,
          soil_type: 'Clay',
          ph_value: 6.5,
          organic_matter: 2.3,
          moisture: 0.35
        }
      },
      {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [104.0, 30.7]
        },
        properties: {
          id: 2,
          soil_type: 'Loam',
          ph_value: 7.2,
          organic_matter: 3.1,
          moisture: 0.42
        }
      },
      {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [121.5, 31.2]
        },
        properties: {
          id: 3,
          soil_type: 'Sandy',
          ph_value: 5.8,
          organic_matter: 1.5,
          moisture: 0.28
        }
      }
    ];
    
    // 添加土壤数据实体
    addSoilEntities();
  } catch (error) {
    console.error('加载土壤数据时出错:', error);
  } finally {
    isLoading.value = false;
  }
};

// 添加土壤数据实体
const addSoilEntities = () => {
  if (!viewer.value) return;
  
  soilData.features.forEach(feature => {
    const position = Cesium.Cartesian3.fromDegrees(
      feature.geometry.coordinates[0],
      feature.geometry.coordinates[1],
      0
    );
    
    // 创建点实体
    const entity = viewer.value.entities.add({
      position: position,
      point: {
        color: Cesium.Color.RED,
        pixelSize: 10,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
      },
      billboard: {
        image: '/src/assets/soil-marker.png',
        width: 32,
        height: 32,
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
      },
      label: {
        text: feature.properties[selectedLayer.value].toString(),
        font: '14px sans-serif',
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        outlineWidth: 2,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -20),
        heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
      }
    });
    
    // 存储实体引用
    soilData.entities.push(entity);
  });
};

// 清除土壤实体
const clearSoilEntities = () => {
  if (!viewer.value) return;
  
  // 移除所有实体
  soilData.entities.forEach(entity => {
    viewer.value.entities.remove(entity);
  });
  
  // 清空实体数组
  soilData.entities = [];
};

// 处理图层变化
const handleLayerChange = () => {
  loadSoilData();
};

// 处理时间变化
const handleTimeChange = () => {
  loadSoilData();
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
  <div class="soil-map-container">
    <div class="map-controls">
      <el-form :inline="true" class="control-form">
        <el-form-item label="数据图层">
          <el-select v-model="selectedLayer" @change="handleLayerChange">
            <el-option
              v-for="item in layers"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="时间">
          <el-select v-model="selectedTime" @change="handleTimeChange">
            <el-option
              v-for="item in timeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="map-container">
      <!-- Cesium 容器 -->
      <div ref="cesiumContainer" class="cesium-container"></div>
      
      <!-- 加载遮罩 -->
      <div v-if="isLoading" class="loading-overlay">
        <el-loading />
      </div>
    </div>
    
    <div class="map-legend">
      <h3>图例</h3>
      <div class="legend-content">
        <template v-if="selectedLayer === 'soil_type'">
          <div class="legend-item">
            <div class="color-box" style="background-color: #8B4513;"></div>
            <span>黏土 (Clay)</span>
          </div>
          <div class="legend-item">
            <div class="color-box" style="background-color: #CD853F;"></div>
            <span>壤土 (Loam)</span>
          </div>
          <div class="legend-item">
            <div class="color-box" style="background-color: #F4A460;"></div>
            <span>砂土 (Sandy)</span>
          </div>
        </template>
        
        <template v-else-if="selectedLayer === 'ph_value'">
          <div class="legend-item">
            <div class="color-box" style="background-color: #FF0000;"></div>
            <span>酸性 (pH < 6.0)</span>
          </div>
          <div class="legend-item">
            <div class="color-box" style="background-color: #FFFF00;"></div>
            <span>中性 (pH 6.0-7.5)</span>
          </div>
          <div class="legend-item">
            <div class="color-box" style="background-color: #0000FF;"></div>
            <span>碱性 (pH > 7.5)</span>
          </div>
        </template>
        
        <template v-else>
          <div class="legend-item">
            <div class="color-box" style="background-color: #FF0000;"></div>
            <span>低</span>
          </div>
          <div class="legend-item">
            <div class="color-box" style="background-color: #FFFF00;"></div>
            <span>中</span>
          </div>
          <div class="legend-item">
            <div class="color-box" style="background-color: #00FF00;"></div>
            <span>高</span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.soil-map-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.map-controls {
  padding: 10px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e6e6e6;
}

.control-form {
  display: flex;
  align-items: center;
}

.map-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.cesium-container {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.map-legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.map-legend h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #333;
}

.legend-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-box {
  width: 20px;
  height: 20px;
  border: 1px solid #ddd;
}
</style>