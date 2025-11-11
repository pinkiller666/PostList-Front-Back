<script setup>
import { ref } from 'vue'
import http from './api/http'
import { ElMessage } from 'element-plus'
import ArtsTable from './components/ArtsTable.vue'
import RightPanel from './components/RightPanel.vue'

const loading = ref(false)
const items = ref([])

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await http.get('/api/arts/')   // тот же эндпоинт
    // предполагаю структуру { items: [...] }
    items.value = Array.isArray(data?.items) ? data.items : []
    ElMessage.success('Загружено')
  } catch (e) {
    ElMessage.error('Ошибка загрузки')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app-layout">
    <div class="app-content">
      <h1 class="app-title">posthub ui</h1>

      <el-button class="load-button" type="primary" :loading="loading" @click="loadData">
        Загрузить данные с Django
      </el-button>

      <div class="table-wrapper">
        <ArtsTable :items="items" />
      </div>
    </div>

    <RightPanel />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--el-bg-color-page);
}

.app-content {
  flex: 1;
  min-width: 0;
  padding: 32px 48px 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
  box-sizing: border-box;
}

.app-title {
  font-size: 40px;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: lowercase;
  margin: 0;
  text-align: center;
}

.load-button {
  align-self: center;
}

.table-wrapper {
  width: min(840px, 100%);
  align-self: stretch;
}

@media (max-width: 960px) {
  .app-layout {
    flex-direction: column;
  }

  .app-content {
    padding: 24px;
  }
}
</style>
