<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const activeIndex = ref('1');

const handleSelect = (key) => {
  console.log(key);
};

const navigateTo = (path) => {
  router.push(path);
};
</script>

<template>
  <header class="app-header">
    <div class="logo-container">
      <img src="@/assets/logo.svg" alt="Logo" class="logo" />
      <h1 class="title">农业土壤 WebGIS</h1>
    </div>
    <el-menu
      :default-active="activeIndex"
      class="nav-menu"
      mode="horizontal"
      @select="handleSelect"
      background-color="#336699"
      text-color="#fff"
      active-text-color="#ffd04b"
    >
      <el-menu-item index="1" @click="navigateTo('/')">首页</el-menu-item>
      <el-menu-item index="2" @click="navigateTo('/soil-map')">土壤地图</el-menu-item>
      <el-menu-item index="3" @click="navigateTo('/soil-analysis')">土壤分析</el-menu-item>
      <el-menu-item index="4" @click="navigateTo('/crop-suitability')">作物适宜性</el-menu-item>
      <el-menu-item index="5" @click="navigateTo('/erosion-risk')">侵蚀风险</el-menu-item>
      <el-menu-item index="6" @click="navigateTo('/data-management')">数据管理</el-menu-item>
    </el-menu>
    <div class="user-actions">
      <el-dropdown>
        <span class="user-dropdown">
          用户 <i class="el-icon-arrow-down"></i>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人资料</el-dropdown-item>
            <el-dropdown-item>设置</el-dropdown-item>
            <el-dropdown-item divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  background-color: #336699;
  color: white;
  padding: 0 20px;
  height: 60px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  margin-right: 20px;
}

.logo {
  height: 40px;
  margin-right: 10px;
}

.title {
  font-size: 1.5rem;
  margin: 0;
  white-space: nowrap;
}

.nav-menu {
  flex: 1;
  border-bottom: none;
}

.user-actions {
  margin-left: 20px;
}

.user-dropdown {
  color: white;
  cursor: pointer;
}
</style>