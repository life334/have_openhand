<script setup>
import { ref, onMounted } from 'vue';
</script>

<template>
  <div class="home-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>欢迎使用农业土壤 WebGIS 系统</h2>
          <p>本系统基于 Cesium 和 Vue 3 开发，提供土壤数据可视化、分析和管理功能。</p>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="feature-row">
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <span>土壤地图</span>
            </div>
          </template>
          <div class="feature-content">
            <i class="el-icon-map-location feature-icon"></i>
            <p>三维可视化土壤数据，支持多种图层和时间序列展示。</p>
            <el-button type="primary" @click="$router.push('/soil-map')">查看地图</el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <span>土壤分析</span>
            </div>
          </template>
          <div class="feature-content">
            <i class="el-icon-data-analysis feature-icon"></i>
            <p>分析土壤属性，生成统计图表，支持多种分析模型。</p>
            <el-button type="primary" @click="$router.push('/soil-analysis')">开始分析</el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <span>填挖方计算</span>
            </div>
          </template>
          <div class="feature-content">
            <i class="el-icon-s-operation feature-icon"></i>
            <p>精确计算土方工程量，支持多种计算方法和可视化结果。</p>
            <el-button type="primary" @click="$router.push('/earthwork-calculation')">开始计算</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 30px;
  text-align: center;
  padding: 30px;
  background: linear-gradient(to right, #f0f9eb, #ecf5ff);
}

.welcome-card h2 {
  font-size: 28px;
  color: #409EFF;
  margin-bottom: 15px;
}

.welcome-card p {
  font-size: 16px;
  color: #606266;
}

.feature-row {
  margin-top: 20px;
}

.feature-card {
  height: 100%;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feature-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 0;
}

.feature-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 20px;
}

.feature-content p {
  margin-bottom: 20px;
  color: #606266;
  min-height: 40px;
}
</style>