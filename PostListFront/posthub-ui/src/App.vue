<script setup>
import { ref } from 'vue'
import http from './api/http'
import { ElMessage } from 'element-plus'
import ArtsTable from './components/ArtsTable.vue'
import RightPanel from './components/RightPanel.vue'

const loading = ref(false)
const items = ref([])
const showContent = ref(false)

const contentPanelId = 'central-panel'

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await http.get('/api/arts/')
    items.value = Array.isArray(data?.items) ? data.items : []
    ElMessage.success('Загружено')
  } catch (e) {
    ElMessage.error('Ошибка загрузки')
  } finally {
    loading.value = false
  }
}

const toggleContent = () => {
  showContent.value = !showContent.value
}
</script>

<template>
  <div class="app-layout">
    <RightPanel />

    <div class="content-shell">
      <div class="content-transition-wrapper" :id="contentPanelId">
        <transition name="content-fade" mode="out-in">
          <div v-if="showContent" key="content" class="app-content">
            <div class="content-controls">
              <el-button
                  class="toggle-button"
                  type="primary"
                  plain
                  size="small"
                  :aria-expanded="showContent"
                  :aria-controls="contentPanelId"
                  @click="toggleContent"
              >
                Скрыть центральную панель
              </el-button>
            </div>

            <h1 class="app-title">posthub ui</h1>

            <el-button class="load-button" type="primary" :loading="loading" @click="loadData">
              Загрузить данные с Django
            </el-button>

            <div class="table-wrapper">
              <ArtsTable :items="items" />
            </div>
          </div>

          <div v-else key="placeholder" class="content-placeholder">
            <el-button
                class="toggle-button"
                type="primary"
                plain
                size="small"
                :aria-expanded="showContent"
                :aria-controls="contentPanelId"
                @click="toggleContent"
            >
              Открыть центральную панель
            </el-button>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: var(--el-bg-color-page);
  align-items: stretch;
}

.content-shell {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: stretch;
}

.content-transition-wrapper {
  flex: 1;
  display: flex;
  align-items: stretch;
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

.content-controls {
  align-self: stretch;
  display: flex;
  justify-content: flex-start;
}

.content-placeholder {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  padding: 32px 24px;
  box-sizing: border-box;
  background: var(--el-bg-color-page);
}

.content-placeholder .toggle-button {
  margin-top: 12px;
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

.toggle-button {
  letter-spacing: 0.3px;
}

.content-fade-enter-active,
.content-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.content-fade-enter-from,
.content-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 960px) {
  .app-layout {
    flex-direction: column;
  }

  .content-shell {
    width: 100%;
  }

  .app-content {
    padding: 24px;
  }

  .content-placeholder {
    padding: 24px;
  }
}
</style>
