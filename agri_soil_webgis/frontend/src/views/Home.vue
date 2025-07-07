<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateTo = (path) => {
  router.push(path);
};
</script>

<template>
  <div class="home-container">
    <div class="hero-section">
      <h1>农业土壤 WebGIS 系统</h1>
      <p>基于三维可视化的农业土壤数据分析与管理平台</p>
      <el-button type="primary" size="large" @click="navigateTo('/soil-map')">
        开始探索
      </el-button>
    </div>
    
    <div class="features-section">
      <h2>主要功能</h2>
      <div class="feature-cards">
        <el-card class="feature-card" @click="navigateTo('/soil-map')">
          <template #header>
            <div class="card-header">
              <h3>三维土壤地图</h3>
            </div>
          </template>
          <div class="card-content">
            <p>使用Cesium实现三维土壤数据可视化，支持多层次数据展示和交互式查询</p>
          </div>
        </el-card>
        
        <el-card class="feature-card" @click="navigateTo('/soil-analysis')">
          <template #header>
            <div class="card-header">
              <h3>土壤质量分析</h3>
            </div>
          </template>
          <div class="card-content">
            <p>分析土壤pH值、有机质含量、养分等指标，提供综合评估和改良建议</p>
          </div>
        </el-card>
        
        <el-card class="feature-card" @click="navigateTo('/crop-suitability')">
          <template #header>
            <div class="card-header">
              <h3>作物适宜性评估</h3>
            </div>
          </template>
          <div class="card-content">
            <p>基于土壤特性和气候条件，评估不同作物的适宜性，提供种植建议</p>
          </div>
        </el-card>
        
        <el-card class="feature-card" @click="navigateTo('/erosion-risk')">
          <template #header>
            <div class="card-header">
              <h3>土壤侵蚀风险</h3>
            </div>
          </template>
          <div class="card-content">
            <p>评估和预测土壤侵蚀风险，提供防治措施建议</p>
          </div>
        </el-card>
      </div>
    </div>
    
    <div class="about-section">
      <h2>关于系统</h2>
      <p>
        本系统采用现代Web技术开发，前端基于Vue 3和Cesium实现三维可视化，
        后端使用FastAPI提供高性能API服务。系统整合了地理信息系统、土壤科学和
        农业生产知识，为农业生产决策提供科学依据。
      </p>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  padding: 20px;
}

.hero-section {
  text-align: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #e6f7ff 0%, #d9f2e6 100%);
  border-radius: 8px;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 2.5rem;
  color: #336699;
  margin-bottom: 16px;
}

.hero-section p {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 30px;
}

.features-section {
  margin-bottom: 40px;
}

.features-section h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #336699;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.feature-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
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

.card-content {
  height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.about-section {
  background-color: #f9f9f9;
  padding: 30px;
  border-radius: 8px;
}

.about-section h2 {
  color: #336699;
  margin-bottom: 20px;
}

.about-section p {
  line-height: 1.6;
  color: #555;
}
</style>