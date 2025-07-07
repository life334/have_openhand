# 农业土壤 WebGIS 系统 - 原生 Cesium 前端

这是一个使用原生 Cesium 和 Vue 3 构建的农业土壤 WebGIS 系统前端项目。与使用 vue-cesium 的版本不同，本项目直接使用原生 Cesium API 进行开发，提供更灵活的控制和更好的性能。

## 功能特点

- 使用原生 Cesium 进行 3D 地图可视化
- 土壤数据的三维展示和分析
- 填挖方计算工具
- 响应式设计，适配不同设备

## 技术栈

- Vue 3 - 前端框架
- Cesium - 3D 地图引擎
- Element Plus - UI 组件库
- Vite - 构建工具
- Axios - HTTP 客户端

## 项目结构

```
frontend_cesium/
├── public/              # 静态资源
├── src/
│   ├── assets/          # 图片、字体等资源
│   ├── components/      # 组件
│   │   └── layout/      # 布局组件
│   ├── styles/          # 样式文件
│   ├── utils/           # 工具函数
│   ├── views/           # 页面视图
│   ├── App.vue          # 根组件
│   ├── main.js          # 入口文件
│   └── router.js        # 路由配置
├── index.html           # HTML 模板
├── package.json         # 项目依赖
├── vite.config.js       # Vite 配置
└── README.md            # 项目说明
```

## 安装和运行

### 安装依赖

```bash
cd agri_soil_webgis/frontend_cesium
npm install
```

### 开发模式运行

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 与 vue-cesium 版本的区别

本项目与使用 vue-cesium 的版本相比，主要区别在于：

1. **直接使用原生 Cesium API**：不依赖 vue-cesium 封装，直接使用 Cesium 的原生 API 进行开发
2. **更灵活的控制**：可以直接访问和操作 Cesium 的所有功能和属性
3. **更好的性能**：减少了额外的封装层，可能在某些场景下提供更好的性能
4. **更直接的调试体验**：错误和问题可以直接追踪到 Cesium 原生 API

## 主要视图

- **首页**：系统概览和功能导航
- **土壤地图**：使用 Cesium 展示土壤数据的三维地图
- **土壤分析**：土壤属性分析和统计图表
- **填挖方计算**：使用 Cesium 进行土方工程量计算

## 后端 API

本前端项目设计为与 FastAPI 后端配合使用，主要 API 端点包括：

- `/api/soil-data/geojson` - 获取土壤 GeoJSON 数据
- `/api/soil-analysis` - 获取土壤分析结果
- `/api/earthwork/calculate` - 计算填挖方量
- `/api/earthwork/validate-polygon` - 验证多边形有效性

## 许可证

MIT