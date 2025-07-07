<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const isCollapse = ref(false);

const activeMenu = computed(() => {
  return route.path;
});

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value;
};

const navigateTo = (path) => {
  router.push(path);
};
</script>

<template>
  <aside class="app-sidebar" :class="{ 'is-collapsed': isCollapse }">
    <div class="sidebar-header">
      <span>功能菜单</span>
      <el-button 
        type="text" 
        @click="toggleSidebar" 
        class="collapse-btn"
      >
        <i :class="isCollapse ? 'el-icon-s-unfold' : 'el-icon-s-fold'"></i>
      </el-button>
    </div>
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapse"
      background-color="#f5f7fa"
      text-color="#333"
      active-text-color="#336699"
    >
      <el-menu-item index="/" @click="navigateTo('/')">
        <el-icon><i class="el-icon-s-home"></i></el-icon>
        <template #title>首页</template>
      </el-menu-item>
      
      <el-menu-item index="/soil-map" @click="navigateTo('/soil-map')">
        <el-icon><i class="el-icon-map-location"></i></el-icon>
        <template #title>土壤地图</template>
      </el-menu-item>
      
      <el-sub-menu index="analysis">
        <template #title>
          <el-icon><i class="el-icon-data-analysis"></i></el-icon>
          <span>分析工具</span>
        </template>
        <el-menu-item index="/soil-analysis" @click="navigateTo('/soil-analysis')">
          土壤分析
        </el-menu-item>
        <el-menu-item index="/crop-suitability" @click="navigateTo('/crop-suitability')">
          作物适宜性
        </el-menu-item>
        <el-menu-item index="/erosion-risk" @click="navigateTo('/erosion-risk')">
          侵蚀风险
        </el-menu-item>
      </el-sub-menu>
      
      <el-menu-item index="/data-management" @click="navigateTo('/data-management')">
        <el-icon><i class="el-icon-document"></i></el-icon>
        <template #title>数据管理</template>
      </el-menu-item>
      
      <el-sub-menu index="settings">
        <template #title>
          <el-icon><i class="el-icon-setting"></i></el-icon>
          <span>系统设置</span>
        </template>
        <el-menu-item index="user-settings">
          用户设置
        </el-menu-item>
        <el-menu-item index="system-settings">
          系统参数
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </aside>
</template>

<style scoped>
.app-sidebar {
  width: 240px;
  height: 100%;
  background-color: #f5f7fa;
  transition: width 0.3s;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  overflow-x: hidden;
}

.app-sidebar.is-collapsed {
  width: 64px;
}

.sidebar-header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid #e6e6e6;
}

.collapse-btn {
  padding: 0;
  margin: 0;
}

.sidebar-menu {
  border-right: none;
  height: calc(100% - 50px);
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}
</style>