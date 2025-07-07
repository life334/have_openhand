<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

const isLoading = ref(false);
const viewerReady = ref(false);
const selectedLocation = reactive({
  latitude: 39.9,
  longitude: 116.3,
  depth: 30
});

const analysisResult = reactive({
  quality_index: null,
  fertility_level: '',
  recommendations: [],
  analysis_date: null
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
  shouldAnimate: true
};

const handleViewerReady = (viewer) => {
  viewerReady.value = true;
  console.log('Cesium viewer is ready');
  
  // Set default view to China
  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(selectedLocation.longitude, selectedLocation.latitude, 10000),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-45),
      roll: 0.0
    }
  });
  
  // Add click event to select location
  viewer.screenSpaceEventHandler.setInputAction((movement) => {
    const pickedPosition = viewer.scene.pickPosition(movement.position);
    if (Cesium.defined(pickedPosition)) {
      const cartographic = Cesium.Cartographic.fromCartesian(pickedPosition);
      selectedLocation.longitude = Cesium.Math.toDegrees(cartographic.longitude);
      selectedLocation.latitude = Cesium.Math.toDegrees(cartographic.latitude);
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
};

const analyzeSoil = async () => {
  try {
    isLoading.value = true;
    // In a real application, this would fetch from the backend API
    // const response = await axios.get(`http://localhost:12001/api/analysis/soil-quality?latitude=${selectedLocation.latitude}&longitude=${selectedLocation.longitude}&depth=${selectedLocation.depth}`);
    // analysisResult.quality_index = response.data.quality_index;
    // analysisResult.fertility_level = response.data.fertility_level;
    // analysisResult.recommendations = response.data.recommendations;
    // analysisResult.analysis_date = response.data.analysis_date;
    
    // For demo purposes, we'll use mock data
    analysisResult.quality_index = 78.5;
    analysisResult.fertility_level = '良好';
    analysisResult.recommendations = [
      '增加有机质以改善土壤结构',
      '考虑添加石灰以调节pH值',
      '增加氮肥以提高养分水平'
    ];
    analysisResult.analysis_date = new Date().toISOString();
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
  } catch (error) {
    console.error('Error analyzing soil:', error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  // Initial analysis will be triggered by the user
});
</script>

<template>
  <div class="soil-analysis-container">
    <div class="analysis-header">
      <h2>土壤质量分析</h2>
      <p>选择地图上的位置或输入坐标进行土壤质量分析</p>
    </div>
    
    <div class="analysis-content">
      <div class="map-panel">
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
          
          <!-- Selected location marker -->
          <vc-entity
            :position="{ lng: selectedLocation.longitude, lat: selectedLocation.latitude, height: 0 }"
          >
            <vc-graphics-point
              :color="'GREEN'"
              :pixel-size="10"
            />
            <vc-graphics-billboard>
              <vc-billboard-image src="/src/assets/location-marker.png" />
            </vc-graphics-billboard>
          </vc-entity>
        </vc-viewer>
        
        <div v-if="isLoading" class="loading-overlay">
          <el-loading />
        </div>
      </div>
      
      <div class="analysis-panel">
        <el-card class="location-card">
          <template #header>
            <div class="card-header">
              <h3>位置信息</h3>
            </div>
          </template>
          <el-form label-position="top">
            <el-form-item label="纬度">
              <el-input v-model="selectedLocation.latitude" type="number" step="0.000001" />
            </el-form-item>
            <el-form-item label="经度">
              <el-input v-model="selectedLocation.longitude" type="number" step="0.000001" />
            </el-form-item>
            <el-form-item label="土壤深度 (cm)">
              <el-input v-model="selectedLocation.depth" type="number" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="analyzeSoil" :loading="isLoading">
                分析土壤
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card class="result-card" v-if="analysisResult.quality_index !== null">
          <template #header>
            <div class="card-header">
              <h3>分析结果</h3>
            </div>
          </template>
          <div class="result-content">
            <div class="quality-index">
              <el-progress
                type="dashboard"
                :percentage="analysisResult.quality_index"
                :color="customColors"
              />
              <div class="quality-label">土壤质量指数</div>
            </div>
            
            <div class="result-details">
              <div class="detail-item">
                <span class="label">肥力水平:</span>
                <span class="value">{{ analysisResult.fertility_level }}</span>
              </div>
              
              <div class="detail-item">
                <span class="label">改良建议:</span>
                <ul class="recommendations">
                  <li v-for="(rec, index) in analysisResult.recommendations" :key="index">
                    {{ rec }}
                  </li>
                </ul>
              </div>
              
              <div class="detail-item">
                <span class="label">分析日期:</span>
                <span class="value">{{ new Date(analysisResult.analysis_date).toLocaleString() }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.soil-analysis-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.analysis-header {
  margin-bottom: 20px;
}

.analysis-header h2 {
  margin: 0 0 10px 0;
  color: #336699;
}

.analysis-header p {
  margin: 0;
  color: #666;
}

.analysis-content {
  display: flex;
  flex: 1;
  gap: 20px;
  overflow: hidden;
}

.map-panel {
  flex: 2;
  position: relative;
  min-height: 500px;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.analysis-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.location-card, .result-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #336699;
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

.result-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.quality-index {
  text-align: center;
}

.quality-label {
  margin-top: 10px;
  font-weight: bold;
  color: #336699;
}

.result-details {
  width: 100%;
}

.detail-item {
  margin-bottom: 15px;
}

.label {
  font-weight: bold;
  color: #666;
}

.value {
  margin-left: 5px;
}

.recommendations {
  margin: 5px 0 0 0;
  padding-left: 20px;
}

.recommendations li {
  margin-bottom: 5px;
}
</style>

<script>
// Define custom colors for the progress bar
const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
];
</script>