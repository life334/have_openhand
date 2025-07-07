<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

const isLoading = ref(false);
const viewerReady = ref(false);
const selectedLocation = reactive({
  latitude: 39.9,
  longitude: 116.3,
  area_size: 10 // hectares
});

const erosionResult = reactive({
  risk_level: '',
  risk_score: null,
  annual_soil_loss: null,
  contributing_factors: [],
  mitigation_strategies: []
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

const analyzeErosionRisk = async () => {
  try {
    isLoading.value = true;
    // In a real application, this would fetch from the backend API
    // const response = await axios.get(`http://localhost:12001/api/analysis/erosion-risk?latitude=${selectedLocation.latitude}&longitude=${selectedLocation.longitude}&area_size=${selectedLocation.area_size}`);
    // erosionResult.risk_level = response.data.risk_level;
    // erosionResult.risk_score = response.data.risk_score;
    // erosionResult.annual_soil_loss = response.data.annual_soil_loss;
    // erosionResult.contributing_factors = response.data.contributing_factors;
    // erosionResult.mitigation_strategies = response.data.mitigation_strategies;
    
    // For demo purposes, we'll use mock data
    erosionResult.risk_level = '中';
    erosionResult.risk_score = 45.2;
    erosionResult.annual_soil_loss = 3.5; // tons per hectare per year
    erosionResult.contributing_factors = [
      '坡度',
      '降雨强度',
      '植被覆盖'
    ];
    erosionResult.mitigation_strategies = [
      '实施等高种植',
      '在非生长季节种植覆盖作物',
      '在水体周围建立缓冲带'
    ];
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
  } catch (error) {
    console.error('Error analyzing erosion risk:', error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  // Initial analysis will be triggered by the user
});
</script>

<template>
  <div class="erosion-risk-container">
    <div class="analysis-header">
      <h2>土壤侵蚀风险评估</h2>
      <p>选择地图上的位置或输入坐标进行土壤侵蚀风险评估</p>
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
              :color="'RED'"
              :pixel-size="10"
            />
            <vc-graphics-billboard>
              <vc-billboard-image src="/src/assets/location-marker.png" />
            </vc-graphics-billboard>
          </vc-entity>
          
          <!-- Add 3D visualization for erosion risk -->
          <vc-entity v-if="erosionResult.risk_score">
            <vc-graphics-cylinder
              :length="100"
              :topRadius="500"
              :bottomRadius="500"
              :material="getRiskColor(erosionResult.risk_level)"
              :outline="true"
              :outlineColor="'BLACK'"
              :position="{ lng: selectedLocation.longitude, lat: selectedLocation.latitude, height: 50 }"
              :alpha="0.5"
            />
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
            <el-form-item label="面积 (公顷)">
              <el-input v-model="selectedLocation.area_size" type="number" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="analyzeErosionRisk" :loading="isLoading">
                评估侵蚀风险
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <el-card class="result-card" v-if="erosionResult.risk_score !== null">
          <template #header>
            <div class="card-header">
              <h3>风险评估结果</h3>
              <div class="risk-badge" :class="getRiskClass(erosionResult.risk_level)">
                {{ erosionResult.risk_level }}风险
              </div>
            </div>
          </template>
          <div class="result-content">
            <div class="risk-score">
              <el-progress
                type="dashboard"
                :percentage="erosionResult.risk_score"
                :color="getRiskProgressColor(erosionResult.risk_score)"
              />
              <div class="score-label">风险指数</div>
            </div>
            
            <div class="result-details">
              <div class="detail-item">
                <span class="label">年土壤流失量:</span>
                <span class="value">{{ erosionResult.annual_soil_loss }} 吨/公顷/年</span>
              </div>
              
              <div class="detail-item">
                <span class="label">影响因素:</span>
                <ul class="factors">
                  <li v-for="(factor, index) in erosionResult.contributing_factors" :key="index">
                    {{ factor }}
                  </li>
                </ul>
              </div>
              
              <div class="detail-item">
                <span class="label">缓解策略:</span>
                <ul class="strategies">
                  <li v-for="(strategy, index) in erosionResult.mitigation_strategies" :key="index">
                    {{ strategy }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.erosion-risk-container {
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

.risk-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.risk-badge.high {
  background-color: #f56c6c;
}

.risk-badge.medium {
  background-color: #e6a23c;
}

.risk-badge.low {
  background-color: #67c23a;
}

.result-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.risk-score {
  text-align: center;
}

.score-label {
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

.factors, .strategies {
  margin: 5px 0 0 0;
  padding-left: 20px;
}

.factors li, .strategies li {
  margin-bottom: 5px;
}
</style>

<script>
// Helper functions for styling
function getRiskClass(level) {
  switch (level) {
    case '高': return 'high';
    case '中': return 'medium';
    case '低': return 'low';
    default: return 'medium';
  }
}

function getRiskColor(level) {
  switch (level) {
    case '高': return 'RED';
    case '中': return 'ORANGE';
    case '低': return 'GREEN';
    default: return 'YELLOW';
  }
}

function getRiskProgressColor(score) {
  if (score >= 70) return '#f56c6c';
  if (score >= 40) return '#e6a23c';
  return '#67c23a';
}
</script>