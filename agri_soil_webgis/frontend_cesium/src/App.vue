<script setup>
import { ref } from 'vue';
import AppHeader from './components/layout/AppHeader.vue';
import AppSidebar from './components/layout/AppSidebar.vue';

const isCollapse = ref(false);

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value;
};
</script>

<template>
  <div class="container">
    <AppHeader @toggle-sidebar="toggleSidebar" />
    
    <div class="main-content">
      <AppSidebar :is-collapse="isCollapse" />
      
      <div class="page-container">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style>
.container {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.page-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>