<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

const isLoading = ref(false);
const viewerReady = ref(false);
const selectedLocation = reactive({
  latitude: 39.9,
  longitude: 116.3
});
const selectedCrop = ref('');

const cropOptions = [
  { value: '', label: '所有作物' },
  { value: 'wheat', label: '小麦' },
  { value: 'corn', label: '玉米' },
  { value: 'rice', label: '水稻' },
  { value: 'soybeans', label: '大豆' },
  { value: 'cotton', label: '棉花' },
  { value: 'vegetables', label: '蔬菜' }
];

const suitabilityResults = ref([]);

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

const analyzeCropSuitability = async () => {
  try {
    isLoading.value = true;
    // In a real application, this would fetch from the backend API
    // const response = await axios.get(`http://localhost:12001/api/analysis/crop-suitability?latitude=${selectedLocation.latitude}&longitude=${selectedLocation.longitude}&crop_type=${selectedCrop.value}`);
    // suitabilityResults.value = response.data;
    
    // For demo purposes, we'll use mock data
    suitabilityResults.value = [
      {
        crop_name: '小麦',
        suitability_score: 85,
        suitability_level: '高',
        limiting_factors: ['土壤pH值略低'],
        recommended_varieties: ['冬小麦', '春小麦']
      },
      {
        crop_name: '玉米',
        suitability_score: 72,
        suitability_level: '中',
        limiting_factors: ['土壤湿度', '氮水平'],
        recommended_varieties: ['抗旱品种']
      },
      {
        crop_name: '大豆',
        suitability_score: 90,
        suitability_level: '很高',
        limiting_factors: [],
        recommended_varieties: ['所有品种适宜']
      }
    ];
    
    // Filter by selected crop if specified
    if (selectedCrop.value) {
      const cropName = cropOptions.find(c => c.value === selectedCrop.value)?.label;
      suitabilityResults.value = suitabilityResults.value.filter(r => r.crop_name === cropName);
    }
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
  } catch (error) {
    console.error('Error analyzing crop suitability:', error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  // Initial analysis will be triggered by the user
});
</script>

<template>
  <div class="crop-suitability-container">
    <div class="analysis-header">
      <h2>作物适宜性评估</h2>
      <p>选择地图上的位置或输入坐标进行作物适宜性评估</p>
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
              <h3>位置与作物选择</h3>
            </div>
          </template>
          <el-form label-position="top">
            <el-form-item label="纬度">
              <el-input v-model="selectedLocation.latitude" type="number" step="0.000001" />
            </el-form-item>
            <el-form-item label="经度">
              <el-input v-model="selectedLocation.longitude" type="number" step="0.000001" />
            </el-form-item>
            <el-form-item label="作物类型">
              <el-select v-model="selectedCrop" placeholder="选择作物类型">
                <el-option
                  v-for="item in cropOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="analyzeCropSuitability" :loading="isLoading">
                评估适宜性
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <div class="results-section" v-if="suitabilityResults.length > 0">
          <h3>评估结果</h3>
          <el-card 
            v-for="(result, index) in suitabilityResults" 
            :key="index"
            class="result-card"
          >
            <div class="result-header">
              <h4>{{ result.crop_name }}</h4>
              <div class="suitability-badge" :class="getSuitabilityClass(result.suitability_level)">
                {{ result.suitability_level }}
              </div>
            </div>
            
            <div class="suitability-score">
              <el-progress 
                :percentage="result.suitability_score" 
                :color="getSuitabilityColor(result.suitability_score)"
                :format="format"
              />
            </div>
            
            <div class="result-details">
              <div class="detail-section" v-if="result.limiting_factors.length > 0">
                <h5>限制因素:</h5>
                <ul>
                  <li v-for="(factor, i) in result.limiting_factors" :key="i">{{ factor }}</li>
                </ul>
              </div>
              
              <div class="detail-section">
                <h5>推荐品种:</h5>
                <ul>
                  <li v-for="(variety, i) in result.recommended_varieties" :key="i">{{ variety }}</li>
                </ul>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.crop-suitability-container {
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

.location-card {
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

.results-section {
  width: 100%;
}

.results-section h3 {
  margin: 0 0 15px 0;
  color: #336699;
}

.result-card {
  margin-bottom: 15px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.result-header h4 {
  margin: 0;
  color: #333;
}

.suitability-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.suitability-badge.very-high {
  background-color: #67c23a;
}

.suitability-badge.high {
  background-color: #409eff;
}

.suitability-badge.medium {
  background-color: #e6a23c;
}

.suitability-badge.low {
  background-color: #f56c6c;
}

.suitability-score {
  margin-bottom: 15px;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-section h5 {
  margin: 0 0 5px 0;
  color: #666;
}

.detail-section ul {
  margin: 0;
  padding-left: 20px;
}

.detail-section li {
  margin-bottom: 3px;
}
</style>

<script>
// Helper functions for styling
function getSuitabilityClass(level) {
  switch (level) {
    case '很高': return 'very-high';
    case '高': return 'high';
    case '中': return 'medium';
    case '低': return 'low';
    default: return 'medium';
  }
}

function getSuitabilityColor(score) {
  if (score >= 80) return '#67c23a';
  if (score >= 60) return '#409eff';
  if (score >= 40) return '#e6a23c';
  return '#f56c6c';
}

function format(percentage) {
  return `${percentage}%`;
}
</script>