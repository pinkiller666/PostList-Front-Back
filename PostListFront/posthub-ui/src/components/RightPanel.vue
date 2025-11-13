<script setup>
import { ref } from 'vue'
import './RightPanel.css'

// временные данные (пока без API)
const statusLabel = (status) => (status ? status.replace(/_/g, ' ') : '')

const arts = ref([
  {
    id: 1,
    name: 'Парочка из Финалки',
    status: 'complete',
    human: true,
    furry: false,
    sfw: true,
    nsfw: false,
    crop: false,
    post_targets: { twi16: true, twi18: false, bsky: true },
    posted: { twi16: true, twi18: false, bsky: false }
  },
  {
    id: 2,
    name: 'Тёмный рыцарь из Тарковы',
    status: 'in_progress',
    human: false,
    furry: true,
    sfw: false,
    nsfw: true,
    crop: true,
    post_targets: { twi16: false, twi18: true, bsky: true },
    posted: { twi16: false, twi18: false, bsky: false }
  }
])

const isLocked = ref(false)

const toggleLock = () => {
  isLocked.value = !isLocked.value
}

const toggleStatus = (art) => {
  art.status = art.status === 'complete' ? 'in_progress' : 'complete'
}

const toggleFlag = (art, key) => {
  if (isLocked.value) return
  art[key] = !art[key]
}

const toggleNestedFlag = (art, scope, key) => {
  if (isLocked.value) return
  art[scope][key] = !art[scope][key]
}
</script>

<template>
  <div class="right-panel" :class="{ locked: isLocked }">
    <div class="panel-header">
      <h2 class="panel-title">Арты</h2>
      <button
        type="button"
        class="lock-button"
        :aria-pressed="isLocked"
        :aria-label="isLocked ? 'Разблокировать панель' : 'Заблокировать панель'"
        :title="isLocked ? 'Разблокировать панель' : 'Заблокировать панель'"
        @click="toggleLock"
      >
        <span class="icon">{{ isLocked ? '🔒' : '🔓' }}</span>
      </button>
    </div>

    <div class="panel-list">
      <div v-for="art in arts" :key="art.id" class="art-row">
        <!-- Название -->
        <div class="art-name">{{ art.name }}</div>

        <!-- Статус -->
        <div class="art-status">
          <button
            type="button"
            class="status-button"
            :class="{ done: art.status === 'complete' }"
            :aria-pressed="art.status === 'complete'"
            @click="toggleStatus(art)"
          >
            {{ statusLabel(art.status) }}
          </button>
        </div>

        <!-- Тип персонажа -->
        <div class="art-type vstack">
          <button
            type="button"
            class="label-button"
            :class="{ active: art.human }"
            :disabled="isLocked"
            :aria-pressed="art.human"
            @click="toggleFlag(art, 'human')"
          >
            human
          </button>
          <button
            type="button"
            class="label-button"
            :class="{ active: art.furry }"
            :disabled="isLocked"
            :aria-pressed="art.furry"
            @click="toggleFlag(art, 'furry')"
          >
            furry
          </button>
        </div>

        <!-- Контент -->
        <div class="art-content vstack">
          <button
            type="button"
            class="label-button"
            :class="{ active: art.sfw }"
            :disabled="isLocked"
            :aria-pressed="art.sfw"
            @click="toggleFlag(art, 'sfw')"
          >
            sfw
          </button>
          <button
            type="button"
            class="label-button"
            :class="{ active: art.nsfw }"
            :disabled="isLocked"
            :aria-pressed="art.nsfw"
            @click="toggleFlag(art, 'nsfw')"
          >
            nsfw
          </button>
          <button
            type="button"
            class="label-button"
            :class="{ active: art.crop }"
            :disabled="isLocked"
            :aria-pressed="art.crop"
            @click="toggleFlag(art, 'crop')"
          >
            crop
          </button>
        </div>

        <!-- Куда постить (план) -->
        <div class="art-post vstack">
          <button
            type="button"
            class="label-button"
            :class="{ active: art.post_targets.twi16 }"
            :disabled="isLocked"
            :aria-pressed="art.post_targets.twi16"
            @click="toggleNestedFlag(art, 'post_targets', 'twi16')"
          >
            twi16
          </button>
          <button
            type="button"
            class="label-button"
            :class="{ active: art.post_targets.twi18 }"
            :disabled="isLocked"
            :aria-pressed="art.post_targets.twi18"
            @click="toggleNestedFlag(art, 'post_targets', 'twi18')"
          >
            twi18
          </button>
          <button
            type="button"
            class="label-button"
            :class="{ active: art.post_targets.bsky }"
            :disabled="isLocked"
            :aria-pressed="art.post_targets.bsky"
            @click="toggleNestedFlag(art, 'post_targets', 'bsky')"
          >
            bsky
          </button>
        </div>

        <!-- Уже запощено (факт) -->
        <div class="art-posted vstack">
          <el-checkbox v-model="art.posted.twi16" size="small" />
          <el-checkbox v-model="art.posted.twi18" size="small" />
          <el-checkbox v-model="art.posted.bsky" size="small" />
        </div>
      </div>
    </div>
  </div>
</template>

