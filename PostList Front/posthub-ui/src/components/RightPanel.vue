<script setup>
import { ref } from 'vue'
import './RightPanel.css'

// временные данные (пока без API)
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
</script>

<template>
  <div class="right-panel">
    <div v-for="art in arts" :key="art.id" class="art-row">
      <!-- Название -->
      <div class="art-name">{{ art.name }}</div>

      <!-- Статус -->
      <div class="art-status">
        <el-tooltip :content="art.status">
          <span class="ico status" :class="{ done: art.status === 'complete' }">
            {{ art.status === 'complete' ? '✅' : '⭕' }}
          </span>
        </el-tooltip>
      </div>

      <!-- Тип персонажа -->
      <div class="art-type vstack">
        <span class="ico" :class="{ active: art.human }">👤</span>
        <span class="ico" :class="{ active: art.furry }">🐺</span>
      </div>

      <!-- Контент -->
      <div class="art-content vstack">
        <span class="ico" :class="{ active: art.sfw }">⚪</span>
        <span class="ico" :class="{ active: art.nsfw }">🔞</span>
        <span class="ico" :class="{ active: art.crop }">✂️</span>
      </div>

      <!-- Куда постить (план) -->
      <div class="art-post vstack">
        <span class="ico" :class="{ active: art.post_targets.twi16 }">🕊️</span>
        <span class="ico" :class="{ active: art.post_targets.twi18 }">🦋</span>
        <span class="ico" :class="{ active: art.post_targets.bsky }">🌐</span>
      </div>

      <!-- Уже запощено (факт) -->
      <div class="art-posted vstack">
        <el-checkbox v-model="art.posted.twi16" size="small" />
        <el-checkbox v-model="art.posted.twi18" size="small" />
        <el-checkbox v-model="art.posted.bsky" size="small" />
      </div>
    </div>
  </div>
</template>

