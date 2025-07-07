<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  isCollapse: {
    type: Boolean,
    default: false
  }
});

const router = useRouter();
const activeMenu = ref(router.currentRoute.value.path);

const navigateTo = (path) => {
  router.push(path);
  activeMenu.value = path;
};
</script>

<template>
  <el-aside :width="isCollapse ? '64px' : '220px'" class="app-sidebar">
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="isCollapse"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
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
          <span>土壤分析</span>
        </template>
        
        <el-menu-item index="/soil-analysis" @click="navigateTo('/soil-analysis')">
          <el-icon><i class="el-icon-s-data"></i></el-icon>
          <span>基础分析</span>
        </el-menu-item>
        
        <el-menu-item index="/earthwork-calculation" @click="navigateTo('/earthwork-calculation')">
          <el-icon><i class="el-icon-s-operation"></i></el-icon>
          <span>填挖方计算</span>
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
  </el-aside>
</template>

<style scoped>
.app-sidebar {
  height: 100%;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}
</style>