<script setup>
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

const isLoading = ref(false);
const activeTab = ref('soil-data');
const dialogVisible = ref(false);
const dialogType = ref('add');
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const searchForm = reactive({
  soil_type: '',
  min_ph: null,
  max_ph: null,
  date_from: '',
  date_to: ''
});

const soilDataForm = reactive({
  id: null,
  latitude: null,
  longitude: null,
  soil_type: '',
  ph_value: null,
  organic_matter: null,
  moisture: null,
  nitrogen: null,
  phosphorus: null,
  potassium: null
});

const soilTypeOptions = [
  { value: 'Clay', label: '黏土' },
  { value: 'Loam', label: '壤土' },
  { value: 'Sandy', label: '砂土' },
  { value: 'Silt', label: '粉土' },
  { value: 'Peat', label: '泥炭土' }
];

const tableData = ref([
  {
    id: 1,
    location: { type: 'Point', coordinates: [116.3, 39.9] },
    soil_type: 'Clay',
    ph_value: 6.5,
    organic_matter: 2.3,
    moisture: 0.35,
    nitrogen: 0.15,
    phosphorus: 0.08,
    potassium: 0.12,
    created_at: '2025-07-01T00:00:00',
    updated_at: '2025-07-01T00:00:00'
  },
  {
    id: 2,
    location: { type: 'Point', coordinates: [104.0, 30.7] },
    soil_type: 'Loam',
    ph_value: 7.2,
    organic_matter: 3.1,
    moisture: 0.42,
    nitrogen: 0.18,
    phosphorus: 0.11,
    potassium: 0.15,
    created_at: '2025-07-02T00:00:00',
    updated_at: '2025-07-02T00:00:00'
  },
  {
    id: 3,
    location: { type: 'Point', coordinates: [121.5, 31.2] },
    soil_type: 'Sandy',
    ph_value: 5.8,
    organic_matter: 1.5,
    moisture: 0.28,
    nitrogen: 0.12,
    phosphorus: 0.06,
    potassium: 0.09,
    created_at: '2025-07-03T00:00:00',
    updated_at: '2025-07-03T00:00:00'
  }
]);

const rules = {
  latitude: [
    { required: true, message: '请输入纬度', trigger: 'blur' },
    { type: 'number', message: '纬度必须为数字', trigger: 'blur' },
    { min: -90, max: 90, message: '纬度范围为-90到90', trigger: 'blur' }
  ],
  longitude: [
    { required: true, message: '请输入经度', trigger: 'blur' },
    { type: 'number', message: '经度必须为数字', trigger: 'blur' },
    { min: -180, max: 180, message: '经度范围为-180到180', trigger: 'blur' }
  ],
  soil_type: [
    { required: true, message: '请选择土壤类型', trigger: 'change' }
  ],
  ph_value: [
    { required: true, message: '请输入pH值', trigger: 'blur' },
    { type: 'number', message: 'pH值必须为数字', trigger: 'blur' },
    { min: 0, max: 14, message: 'pH值范围为0到14', trigger: 'blur' }
  ],
  organic_matter: [
    { required: true, message: '请输入有机质含量', trigger: 'blur' },
    { type: 'number', message: '有机质含量必须为数字', trigger: 'blur' },
    { min: 0, message: '有机质含量必须大于0', trigger: 'blur' }
  ],
  moisture: [
    { required: true, message: '请输入湿度', trigger: 'blur' },
    { type: 'number', message: '湿度必须为数字', trigger: 'blur' },
    { min: 0, max: 1, message: '湿度范围为0到1', trigger: 'blur' }
  ]
};

const formRef = ref(null);

const fetchData = async () => {
  try {
    isLoading.value = true;
    // In a real application, this would fetch from the backend API
    // const response = await axios.get(`http://localhost:12001/api/soil-data?soil_type=${searchForm.soil_type}&min_ph=${searchForm.min_ph || ''}&max_ph=${searchForm.max_ph || ''}&skip=${(currentPage.value - 1) * pageSize.value}&limit=${pageSize.value}`);
    // tableData.value = response.data;
    // total.value = response.headers['x-total-count'] || tableData.value.length;
    
    // For demo purposes, we'll use the mock data
    // Filter based on search criteria
    let filteredData = [...tableData.value];
    
    if (searchForm.soil_type) {
      filteredData = filteredData.filter(item => item.soil_type === searchForm.soil_type);
    }
    
    if (searchForm.min_ph !== null) {
      filteredData = filteredData.filter(item => item.ph_value >= searchForm.min_ph);
    }
    
    if (searchForm.max_ph !== null) {
      filteredData = filteredData.filter(item => item.ph_value <= searchForm.max_ph);
    }
    
    total.value = filteredData.length;
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
  } catch (error) {
    console.error('Error fetching data:', error);
  } finally {
    isLoading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchData();
};

const resetSearch = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = '';
  });
  handleSearch();
};

const handleAdd = () => {
  dialogType.value = 'add';
  resetForm();
  dialogVisible.value = true;
};

const handleEdit = (row) => {
  dialogType.value = 'edit';
  resetForm();
  
  // Populate form with row data
  soilDataForm.id = row.id;
  soilDataForm.latitude = row.location.coordinates[1];
  soilDataForm.longitude = row.location.coordinates[0];
  soilDataForm.soil_type = row.soil_type;
  soilDataForm.ph_value = row.ph_value;
  soilDataForm.organic_matter = row.organic_matter;
  soilDataForm.moisture = row.moisture;
  soilDataForm.nitrogen = row.nitrogen;
  soilDataForm.phosphorus = row.phosphorus;
  soilDataForm.potassium = row.potassium;
  
  dialogVisible.value = true;
};

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条数据吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    isLoading.value = true;
    // In a real application, this would call the backend API
    // await axios.delete(`http://localhost:12001/api/soil-data/${row.id}`);
    
    // For demo purposes, we'll just remove from the local array
    const index = tableData.value.findIndex(item => item.id === row.id);
    if (index !== -1) {
      tableData.value.splice(index, 1);
    }
    
    ElMessage({
      type: 'success',
      message: '删除成功'
    });
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Error deleting data:', error);
      ElMessage({
        type: 'error',
        message: '删除失败'
      });
    }
  } finally {
    isLoading.value = false;
  }
};

const resetForm = () => {
  soilDataForm.id = null;
  soilDataForm.latitude = null;
  soilDataForm.longitude = null;
  soilDataForm.soil_type = '';
  soilDataForm.ph_value = null;
  soilDataForm.organic_matter = null;
  soilDataForm.moisture = null;
  soilDataForm.nitrogen = null;
  soilDataForm.phosphorus = null;
  soilDataForm.potassium = null;
  
  if (formRef.value) {
    formRef.value.resetFields();
  }
};

const submitForm = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    
    isLoading.value = true;
    
    const formData = {
      location: {
        type: 'Point',
        coordinates: [soilDataForm.longitude, soilDataForm.latitude]
      },
      soil_type: soilDataForm.soil_type,
      ph_value: soilDataForm.ph_value,
      organic_matter: soilDataForm.organic_matter,
      moisture: soilDataForm.moisture,
      nitrogen: soilDataForm.nitrogen,
      phosphorus: soilDataForm.phosphorus,
      potassium: soilDataForm.potassium
    };
    
    if (dialogType.value === 'add') {
      // In a real application, this would call the backend API
      // const response = await axios.post('http://localhost:12001/api/soil-data', formData);
      // const newData = response.data;
      
      // For demo purposes, we'll just add to the local array
      const newData = {
        ...formData,
        id: tableData.value.length + 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      tableData.value.push(newData);
      
      ElMessage({
        type: 'success',
        message: '添加成功'
      });
    } else {
      // In a real application, this would call the backend API
      // const response = await axios.put(`http://localhost:12001/api/soil-data/${soilDataForm.id}`, formData);
      // const updatedData = response.data;
      
      // For demo purposes, we'll just update the local array
      const index = tableData.value.findIndex(item => item.id === soilDataForm.id);
      if (index !== -1) {
        tableData.value[index] = {
          ...tableData.value[index],
          ...formData,
          updated_at: new Date().toISOString()
        };
      }
      
      ElMessage({
        type: 'success',
        message: '更新成功'
      });
    }
    
    dialogVisible.value = false;
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
  } catch (error) {
    console.error('Form validation failed:', error);
  } finally {
    isLoading.value = false;
  }
};

const handleSizeChange = (val) => {
  pageSize.value = val;
  fetchData();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchData();
};

const exportData = () => {
  // In a real application, this would call the backend API to generate a CSV/Excel file
  ElMessage({
    type: 'success',
    message: '数据导出成功'
  });
};

const importData = () => {
  // In a real application, this would open a file upload dialog and send to backend
  ElMessage({
    type: 'info',
    message: '数据导入功能正在开发中'
  });
};

onMounted(() => {
  fetchData();
});
</script>

<template>
  <div class="data-management-container">
    <div class="page-header">
      <h2>数据管理</h2>
    </div>
    
    <el-tabs v-model="activeTab" class="data-tabs">
      <el-tab-pane label="土壤数据" name="soil-data">
        <div class="tab-content">
          <div class="search-section">
            <el-form :inline="true" :model="searchForm" class="search-form">
              <el-form-item label="土壤类型">
                <el-select v-model="searchForm.soil_type" placeholder="选择土壤类型" clearable>
                  <el-option
                    v-for="item in soilTypeOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="pH值范围">
                <el-input-number v-model="searchForm.min_ph" :min="0" :max="14" :precision="1" placeholder="最小值" />
                <span class="range-separator">-</span>
                <el-input-number v-model="searchForm.max_ph" :min="0" :max="14" :precision="1" placeholder="最大值" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSearch" :loading="isLoading">搜索</el-button>
                <el-button @click="resetSearch">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <div class="table-actions">
            <el-button type="primary" @click="handleAdd">添加数据</el-button>
            <el-button type="success" @click="exportData">导出数据</el-button>
            <el-button type="warning" @click="importData">导入数据</el-button>
          </div>
          
          <el-table
            :data="tableData"
            border
            style="width: 100%"
            v-loading="isLoading"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="位置" width="180">
              <template #default="scope">
                {{ scope.row.location.coordinates[1].toFixed(4) }}, {{ scope.row.location.coordinates[0].toFixed(4) }}
              </template>
            </el-table-column>
            <el-table-column prop="soil_type" label="土壤类型" width="120">
              <template #default="scope">
                {{ soilTypeOptions.find(item => item.value === scope.row.soil_type)?.label || scope.row.soil_type }}
              </template>
            </el-table-column>
            <el-table-column prop="ph_value" label="pH值" width="100" />
            <el-table-column prop="organic_matter" label="有机质 (%)" width="120" />
            <el-table-column prop="moisture" label="湿度" width="100" />
            <el-table-column prop="nitrogen" label="氮 (%)" width="100" />
            <el-table-column prop="phosphorus" label="磷 (%)" width="100" />
            <el-table-column prop="potassium" label="钾 (%)" width="100" />
            <el-table-column label="创建时间" width="180">
              <template #default="scope">
                {{ new Date(scope.row.created_at).toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination-container">
            <el-pagination
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              :current-page="currentPage"
              :page-sizes="[10, 20, 50, 100]"
              :page-size="pageSize"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
            />
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="用户管理" name="user-management">
        <div class="tab-content">
          <div class="placeholder-content">
            <el-empty description="用户管理功能正在开发中" />
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="系统设置" name="system-settings">
        <div class="tab-content">
          <div class="placeholder-content">
            <el-empty description="系统设置功能正在开发中" />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 添加/编辑土壤数据对话框 -->
    <el-dialog
      :title="dialogType === 'add' ? '添加土壤数据' : '编辑土壤数据'"
      v-model="dialogVisible"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="soilDataForm"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="纬度" prop="latitude">
          <el-input-number v-model="soilDataForm.latitude" :precision="6" :step="0.000001" :min="-90" :max="90" />
        </el-form-item>
        <el-form-item label="经度" prop="longitude">
          <el-input-number v-model="soilDataForm.longitude" :precision="6" :step="0.000001" :min="-180" :max="180" />
        </el-form-item>
        <el-form-item label="土壤类型" prop="soil_type">
          <el-select v-model="soilDataForm.soil_type" placeholder="选择土壤类型">
            <el-option
              v-for="item in soilTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="pH值" prop="ph_value">
          <el-input-number v-model="soilDataForm.ph_value" :precision="1" :step="0.1" :min="0" :max="14" />
        </el-form-item>
        <el-form-item label="有机质 (%)" prop="organic_matter">
          <el-input-number v-model="soilDataForm.organic_matter" :precision="1" :step="0.1" :min="0" />
        </el-form-item>
        <el-form-item label="湿度" prop="moisture">
          <el-input-number v-model="soilDataForm.moisture" :precision="2" :step="0.01" :min="0" :max="1" />
        </el-form-item>
        <el-form-item label="氮 (%)" prop="nitrogen">
          <el-input-number v-model="soilDataForm.nitrogen" :precision="2" :step="0.01" :min="0" />
        </el-form-item>
        <el-form-item label="磷 (%)" prop="phosphorus">
          <el-input-number v-model="soilDataForm.phosphorus" :precision="2" :step="0.01" :min="0" />
        </el-form-item>
        <el-form-item label="钾 (%)" prop="potassium">
          <el-input-number v-model="soilDataForm.potassium" :precision="2" :step="0.01" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="isLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.data-management-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #336699;
}

.data-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tab-content {
  padding: 20px 0;
}

.search-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.range-separator {
  margin: 0 5px;
}

.table-actions {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.placeholder-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}
</style>