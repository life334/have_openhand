# 农业土壤 WebGIS 系统

基于三维可视化的农业土壤数据分析与管理平台

## 技术栈

### 前端
- Vue 3
- Cesium (三维地图可视化)
- Element Plus (UI组件库)
- Pinia (状态管理)
- Vue Router (路由管理)

### 后端
- FastAPI (Python Web框架)
- SQLAlchemy (ORM)
- GeoPandas (地理数据处理)
- Rasterio (栅格数据处理)
- Shapely (几何数据处理)

## 功能特性

- 三维土壤地图可视化
- 土壤质量分析
- 作物适宜性评估
- 土壤侵蚀风险评估
- 土壤数据管理

## 项目结构

```
agri_soil_webgis/
├── frontend/             # 前端 Vue 3 + Cesium
│   ├── src/
│   │   ├── assets/       # 静态资源
│   │   ├── components/   # 组件
│   │   ├── router/       # 路由
│   │   ├── store/        # Pinia 状态管理
│   │   ├── views/        # 页面视图
│   │   ├── App.vue       # 主应用组件
│   │   └── main.js       # 入口文件
│   ├── public/           # 公共资源
│   └── vite.config.js    # Vite 配置
│
├── backend/              # 后端 FastAPI
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心功能
│   │   ├── db/           # 数据库模型和连接
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── services/     # 业务逻辑服务
│   │   └── main.py       # 主应用入口
│   ├── tests/            # 测试
│   └── run.py            # 运行脚本
│
└── data/                 # 示例数据
```

## 安装与运行

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

## 开发团队

- 开发者: OpenHands AI

## 许可证

MIT