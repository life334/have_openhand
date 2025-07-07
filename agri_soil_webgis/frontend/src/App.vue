<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import AppHeader from './components/layout/AppHeader.vue';
import AppSidebar from './components/layout/AppSidebar.vue';

const router = useRouter();
const isLoading = ref(false);
</script>

<template>
  <div class="app-container">
    <AppHeader />
    <div class="main-container">
      <AppSidebar />
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

#app {
  height: 100vh;
  width: 100vw;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.main-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.content {
  flex: 1;
  overflow: auto;
  position: relative;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
