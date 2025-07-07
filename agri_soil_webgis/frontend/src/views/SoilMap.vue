<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';

const isLoading = ref(false);
const selectedLayer = ref('soil_type');
const selectedTime = ref('2025');
const viewerReady = ref(false);

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
  features: []
});

const cesiumOptions = {
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
  shouldAnimate: true,
  terrainProvider: {
    requestVertexNormals: true,
    requestWaterMask: true
  }
};

const handleViewerReady = (viewer) => {
  viewerReady.value = true;
  console.log('Cesium viewer is ready');
  
  // Set default view to China
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(104.0, 35.0, 10000000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-90),
      roll: 0.0
    }
  });
  
  // Load soil data
  loadSoilData();
};

const loadSoilData = async () => {
  try {
    isLoading.value = true;
    // In a real application, this would fetch from the backend API
    // const response = await axios.get(`http://localhost:12001/api/soil-data/geojson?layer=${selectedLayer.value}&year=${selectedTime.value}`);
    // soilData.features = response.data.features;
    
    // For demo purposes, we'll use mock data
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
  } catch (error) {
    console.error('Error loading soil data:', error);
  } finally {
    isLoading.value = false;
  }
};

const handleLayerChange = () => {
  loadSoilData();
};

const handleTimeChange = () => {
  loadSoilData();
};

onMounted(() => {
  // Initial data load will happen when the Cesium viewer is ready
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
      <vc-viewer
        :animation="cesiumOptions.animation"
        :base-layer-picker="cesiumOptions.baseLayerPicker"
        :fullscreen-button="cesiumOptions.fullscreenButton"
        :vr-button="cesiumOptions.vrButton"
        :geocoder="cesiumOptions.geocoder"
        :home-button="cesiumOptions.homeButton"
        :info-box="cesiumOptions.infoBox"
        :scene-mode-picker="cesiumOptions.sceneModePicker"
        :selection-indicator="cesiumOptions.selectionIndicator"
        :timeline="cesiumOptions.timeline"
        :navigation-help-button="cesiumOptions.navigationHelpButton"
        :navigation-instructions-initially-visible="cesiumOptions.navigationInstructionsInitiallyVisible"
        :scene3-d-only="cesiumOptions.scene3DOnly"
        :should-animate="cesiumOptions.shouldAnimate"
        @ready="handleViewerReady"
      >
        <!-- Terrain provider for 3D terrain -->
        <vc-terrain-provider-cesium />
        
        <!-- Add entities for soil data points -->
        <vc-entity
          v-for="feature in soilData.features"
          :key="feature.properties.id"
          :position="{ lng: feature.geometry.coordinates[0], lat: feature.geometry.coordinates[1], height: 0 }"
        >
          <vc-graphics-point
            :color="'RED'"
            :pixel-size="10"
          />
          <vc-graphics-billboard>
            <vc-billboard-image src="/src/assets/soil-marker.png" />
          </vc-graphics-billboard>
          <vc-graphics-label
            :text="feature.properties[selectedLayer]"
            :font="'14px sans-serif'"
            :style="'FILL_AND_OUTLINE'"
            :outline-width="2"
            :horizontal-origin="'CENTER'"
            :vertical-origin="'BOTTOM'"
            :pixelOffset="{ x: 0, y: -20 }"
          />
        </vc-entity>
        
        <!-- Add 3D terrain visualization for soil properties -->
        <vc-primitive-tileset
          url="https://assets.cesium.com/43978/tileset.json"
          :color-blend-mode="'HIGHLIGHT'"
        />
      </vc-viewer>
      
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