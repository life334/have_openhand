<script setup>
import { ref, onMounted, reactive } from 'vue';
import axios from 'axios';

const isLoading = ref(false);
const selectedRegion = ref('beijing');
const selectedSoilType = ref('all');
const selectedTimeRange = ref('2025');

const regions = [
  { value: 'beijing', label: '北京市' },
  { value: 'shanghai', label: '上海市' },
  { value: 'guangzhou', label: '广州市' },
  { value: 'chengdu', label: '成都市' }
];

const soilTypes = [
  { value: 'all', label: '全部类型' },
  { value: 'clay', label: '黏土' },
  { value: 'loam', label: '壤土' },
  { value: 'sandy', label: '砂土' }
];

const timeRanges = [
  { value: '2020', label: '2020年' },
  { value: '2021', label: '2021年' },
  { value: '2022', label: '2022年' },
  { value: '2023', label: '2023年' },
  { value: '2024', label: '2024年' },
  { value: '2025', label: '2025年' }
];

const analysisData = reactive({
  phDistribution: {
    labels: ['强酸性', '酸性', '微酸性', '中性', '碱性', '强碱性'],
    values: [5, 15, 25, 30, 20, 5]
  },
  organicMatter: {
    labels: ['极低', '低', '中等', '高', '极高'],
    values: [10, 20, 40, 20, 10]
  },
  nutrientLevels: {
    nitrogen: {
      labels: ['低', '中', '高'],
      values: [30, 50, 20]
    },
    phosphorus: {
      labels: ['低', '中', '高'],
      values: [40, 40, 20]
    },
    potassium: {
      labels: ['低', '中', '高'],
      values: [20, 60, 20]
    }
  },
  soilTypeDistribution: {
    labels: ['黏土', '壤土', '砂土', '其他'],
    values: [30, 40, 25, 5]
  }
});

// 加载分析数据
const loadAnalysisData = async () => {
  try {
    isLoading.value = true;
    
    // 在实际应用中，这里会从后端 API 获取数据
    // const response = await axios.get(`http://localhost:12001/api/soil-analysis?region=${selectedRegion.value}&soil_type=${selectedSoilType.value}&year=${selectedTimeRange.value}`);
    // 更新分析数据
    // analysisData.phDistribution.values = response.data.ph_distribution;
    // analysisData.organicMatter.values = response.data.organic_matter;
    // analysisData.nutrientLevels.nitrogen.values = response.data.nutrient_levels.nitrogen;
    // analysisData.nutrientLevels.phosphorus.values = response.data.nutrient_levels.phosphorus;
    // analysisData.nutrientLevels.potassium.values = response.data.nutrient_levels.potassium;
    // analysisData.soilTypeDistribution.values = response.data.soil_type_distribution;
    
    // 模拟数据加载延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 根据选择的区域随机生成一些数据
    if (selectedRegion.value === 'beijing') {
      analysisData.phDistribution.values = [5, 15, 25, 30, 20, 5];
      analysisData.organicMatter.values = [10, 20, 40, 20, 10];
    } else if (selectedRegion.value === 'shanghai') {
      analysisData.phDistribution.values = [2, 10, 30, 35, 18, 5];
      analysisData.organicMatter.values = [15, 25, 35, 15, 10];
    } else if (selectedRegion.value === 'guangzhou') {
      analysisData.phDistribution.values = [8, 20, 30, 25, 12, 5];
      analysisData.organicMatter.values = [5, 15, 45, 25, 10];
    } else {
      analysisData.phDistribution.values = [3, 12, 28, 32, 20, 5];
      analysisData.organicMatter.values = [12, 22, 38, 18, 10];
    }
    
  } catch (error) {
    console.error('加载分析数据时出错:', error);
  } finally {
    isLoading.value = false;
  }
};

// 处理区域变化
const handleRegionChange = () => {
  loadAnalysisData();
};

// 处理土壤类型变化
const handleSoilTypeChange = () => {
  loadAnalysisData();
};

// 处理时间范围变化
const handleTimeRangeChange = () => {
  loadAnalysisData();
};

// 组件挂载时加载数据
onMounted(() => {
  loadAnalysisData();
});
</script>

<template>
  <div class="soil-analysis-container">
    <div class="filter-panel">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="区域">
          <el-select v-model="selectedRegion" @change="handleRegionChange">
            <el-option
              v-for="item in regions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="土壤类型">
          <el-select v-model="selectedSoilType" @change="handleSoilTypeChange">
            <el-option
              v-for="item in soilTypes"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="时间">
          <el-select v-model="selectedTimeRange" @change="handleTimeRangeChange">
            <el-option
              v-for="item in timeRanges"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    
    <div v-if="isLoading" class="loading-container">
      <el-loading />
    </div>
    
    <div v-else class="analysis-content">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>pH值分布</span>
              </div>
            </template>
            <div class="chart-container">
              <!-- 在实际应用中，这里会使用图表库如 ECharts -->
              <div class="mock-chart">
                <div 
                  v-for="(value, index) in analysisData.phDistribution.values" 
                  :key="index"
                  class="chart-bar"
                  :style="{ height: `${value * 3}px`, backgroundColor: getPhColor(index) }"
                >
                  <span class="bar-value">{{ value }}%</span>
                </div>
              </div>
              <div class="chart-labels">
                <span 
                  v-for="(label, index) in analysisData.phDistribution.labels" 
                  :key="index"
                  class="chart-label"
                >
                  {{ label }}
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>有机质含量</span>
              </div>
            </template>
            <div class="chart-container">
              <!-- 在实际应用中，这里会使用图表库如 ECharts -->
              <div class="mock-chart">
                <div 
                  v-for="(value, index) in analysisData.organicMatter.values" 
                  :key="index"
                  class="chart-bar"
                  :style="{ height: `${value * 3}px`, backgroundColor: getOrganicColor(index) }"
                >
                  <span class="bar-value">{{ value }}%</span>
                </div>
              </div>
              <div class="chart-labels">
                <span 
                  v-for="(label, index) in analysisData.organicMatter.labels" 
                  :key="index"
                  class="chart-label"
                >
                  {{ label }}
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="chart-row">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>养分水平</span>
              </div>
            </template>
            <div class="nutrient-charts">
              <div class="nutrient-chart">
                <h4>氮 (N)</h4>
                <div class="mock-chart">
                  <div 
                    v-for="(value, index) in analysisData.nutrientLevels.nitrogen.values" 
                    :key="index"
                    class="chart-bar"
                    :style="{ height: `${value * 3}px`, backgroundColor: getNutrientColor(index) }"
                  >
                    <span class="bar-value">{{ value }}%</span>
                  </div>
                </div>
                <div class="chart-labels">
                  <span 
                    v-for="(label, index) in analysisData.nutrientLevels.nitrogen.labels" 
                    :key="index"
                    class="chart-label"
                  >
                    {{ label }}
                  </span>
                </div>
              </div>
              
              <div class="nutrient-chart">
                <h4>磷 (P)</h4>
                <div class="mock-chart">
                  <div 
                    v-for="(value, index) in analysisData.nutrientLevels.phosphorus.values" 
                    :key="index"
                    class="chart-bar"
                    :style="{ height: `${value * 3}px`, backgroundColor: getNutrientColor(index) }"
                  >
                    <span class="bar-value">{{ value }}%</span>
                  </div>
                </div>
                <div class="chart-labels">
                  <span 
                    v-for="(label, index) in analysisData.nutrientLevels.phosphorus.labels" 
                    :key="index"
                    class="chart-label"
                  >
                    {{ label }}
                  </span>
                </div>
              </div>
              
              <div class="nutrient-chart">
                <h4>钾 (K)</h4>
                <div class="mock-chart">
                  <div 
                    v-for="(value, index) in analysisData.nutrientLevels.potassium.values" 
                    :key="index"
                    class="chart-bar"
                    :style="{ height: `${value * 3}px`, backgroundColor: getNutrientColor(index) }"
                  >
                    <span class="bar-value">{{ value }}%</span>
                  </div>
                </div>
                <div class="chart-labels">
                  <span 
                    v-for="(label, index) in analysisData.nutrientLevels.potassium.labels" 
                    :key="index"
                    class="chart-label"
                  >
                    {{ label }}
                  </span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
// 辅助函数，获取 pH 值对应的颜色
function getPhColor(index) {
  const colors = ['#FF4500', '#FF8C00', '#FFD700', '#32CD32', '#1E90FF', '#4169E1'];
  return colors[index] || '#409EFF';
}

// 辅助函数，获取有机质含量对应的颜色
function getOrganicColor(index) {
  const colors = ['#FFCCCC', '#FF9999', '#FF6666', '#FF3333', '#CC0000'];
  return colors[index] || '#409EFF';
}

// 辅助函数，获取养分水平对应的颜色
function getNutrientColor(index) {
  const colors = ['#FF6666', '#FFCC66', '#66CC66'];
  return colors[index] || '#409EFF';
}
</script>

<style scoped>
.soil-analysis-container {
  padding: 20px;
}

.filter-panel {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.chart-row {
  margin-top: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  display: flex;
  flex-direction: column;
}

.mock-chart {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding: 20px 0;
}

.chart-bar {
  width: 40px;
  min-height: 20px;
  background-color: #409EFF;
  border-radius: 4px 4px 0 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 5px;
  transition: height 0.5s;
}

.bar-value {
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
}

.chart-label {
  font-size: 12px;
  color: #606266;
}

.nutrient-charts {
  display: flex;
  justify-content: space-around;
}

.nutrient-chart {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nutrient-chart h4 {
  margin-bottom: 15px;
  color: #303133;
}
</style>