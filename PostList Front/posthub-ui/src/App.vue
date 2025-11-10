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
  <div style="padding:24px; max-width:960px; margin:0 auto">
    <h1 style="font-size:42px; font-weight:800; margin-bottom:16px">PostHub UI</h1>

    <RightPanel />

    <el-button type="primary" :loading="loading" @click="loadData">
      Загрузить данные с Django
    </el-button>

    <div style="margin-top:16px">
      <ArtsTable :items="items" />
    </div>
  </div>
</template>
