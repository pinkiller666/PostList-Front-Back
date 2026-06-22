<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import './LeftPanel.css'
import { mapArtFromApi } from '../api/artMappers'
import { updateArt } from '../api/artApi'

const savingError = ref(null)
const statusLabel = (s) => (s ? s.replace(/_/g, ' ') : '')

const API_BASE = 'http://127.0.0.1:8081'          // если нужно — поправишь порт/хост
const ARTS_ENDPOINT = `${API_BASE}/api/arts/`     // эндпоинт arts_list

const arts = ref([])
const isLoading = ref(false)
const loadError = ref(null)

import { ArrowUp } from '@element-plus/icons-vue'
import { Finished } from '@element-plus/icons-vue'

// БЕРЕМ МЕСЯЦ
const getCurrentMonth = () => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

const selectedMonth = ref(getCurrentMonth())

// ГРУЗИМ АРТЫ ИЗ НУЖНОГО МЕСЯЦА
const loadArts = async () => {
  isLoading.value = true
  loadError.value = null

  try {
    const url = `${ARTS_ENDPOINT}?month=${encodeURIComponent(selectedMonth.value)}`
    console.log('load arts url:', url)
    console.log(selectedMonth.value)
    console.log(typeof selectedMonth.value)

    const resp = await fetch(url, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    })

    console.log(selectedMonth.value)
    console.log(typeof selectedMonth.value)

    if (!resp.ok) {
      throw new Error(`Ошибка загрузки: ${resp.status} ${resp.statusText}`)
    }

    const data = await resp.json()
    const items = Array.isArray(data.items) ? data.items : []

    arts.value = items.map(function (item) {
      const art = mapArtFromApi(item)
      if (typeof art.onDisk !== 'boolean') {
        art.onDisk = false
      }
      return art
    })
  } catch (err) {
    console.error('Ошибка загрузки артов:', err)
    loadError.value = err instanceof Error ? err.message : String(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadArts()
})

watch(selectedMonth, () => {
  loadArts()
})

/* ========================
   Локальные изменения + save
   ======================== */

const saveArt = async (art) => {
  savingError.value = null
  try {
    // fire-and-forget: состояние на фронте уже обновили
    await updateArt(art)
  } catch (err) {
    console.error('Ошибка сохранения артa:', err)
    savingError.value = err instanceof Error ? err.message : String(err)
    // TODO LATER: показать тост, откатить изменения, подсветить строку и т.п.
  }
}

// было тернарным адом — теперь обычный if/else
const nextStatus = (art) => {
  if (art.status === 'complete') {
    return 'in_progress'
  }
  return 'complete'
}

const statusTitle = (art) => `Сменить статус на ${statusLabel(nextStatus(art))}`

function archiveArt(art) {
  console.log('Нажата архивация для арта', art.id, art.name)
  // позже сюда прикрутим реальный API-запрос
}

function isAllClosed(art) {
  const targets = art.post_targets || {}
  const entries = Object.entries(targets)
  const selected = entries.filter(function (pair) {
    return pair[1]
  })

  if (selected.length === 0) {
    return false
  }

  const allPosted = selected.every(function (pair) {
    const key = pair[0]
    if (!art.posted) {
      return false
    }
    return !!art.posted[key]
  })

  return art.status === 'complete' && art.onDisk && allPosted
}

function reportAllClosed(art) {
  if (isAllClosed(art)) {
    console.log(`Арт #${art.id}: все закрыто`)
  }
}

function toggleStatus(art) {
  art.status = nextStatus(art)
  saveArt(art)
  reportAllClosed(art)
}

function toggleFlag(art, key) {
  art[key] = !art[key]
  saveArt(art)
}

function toggleNestedFlag(art, scope, key) {
  if (!art[scope]) {
    art[scope] = {}
  }
  art[scope][key] = !art[scope][key]
  saveArt(art)
  if (scope === 'post_targets') {
    reportAllClosed(art)
  }
}

function hasAnyPostTarget(art) {
  var targets = art.post_targets || {}
  var keys = Object.keys(targets)
  var i

  for (i = 0; i < keys.length; i += 1) {
    if (targets[keys[i]]) {
      return true
    }
  }

  return false
}


function toggleOnDisk(art) {
  if (typeof art.onDisk !== 'boolean') {
    art.onDisk = false
  }
  art.onDisk = !art.onDisk
  reportAllClosed(art)
}

function handlePostedChange(art) {
  saveArt(art)
  reportAllClosed(art)
}

/* --- Редактирование названия --- */

const editingNameId = ref(null)
const editNameValue = ref('')
const editNameInput = ref(null)

const startEditName = (art) => {
  editingNameId.value = art.id
  editNameValue.value = art.name

  nextTick(() => {
    const inputComp = editNameInput.value
    const el = inputComp && inputComp.input
    if (el) {
      el.focus()
      el.setSelectionRange(0, el.value.length)
    }
  })
}

const finishEditName = (art) => {
  if (editingNameId.value !== art.id) return
  const newName = editNameValue.value.trim()
  if (newName && newName !== art.name) {
    art.name = newName
    saveArt(art)
  }
  editingNameId.value = null
}
</script>

<template>
  <div class="right-panel">
    <div class="panel-header">
      <div class="panel-header">
        <h2 class="panel-title">Арты</h2>

        <el-date-picker
            v-model="selectedMonth"
            class="panel-month-picker"
            type="month"
            value-format="YYYY-MM"
            format="MMMM YYYY"
            placeholder="Месяц"
            size="small"
            :clearable="false"
        />
      </div>
    </div>
    <el-scrollbar class="scroll-area">
      <div class="panel-list">
        <div
            v-for="art in arts"
            :key="art.id"
            class="art-row"
            :class="{ 'art-row--all-closed': isAllClosed(art) }"
        >
          <!-- ВЕРХНЯЯ ПОЛОСА: только заголовок "выложено" -->
          <div class="art-row-header">
            <!-- Левая часть: либо кнопка архива, либо просто пустой спейсер -->
            <div
                v-if="isAllClosed(art)"
                class="header-archive"
                @click="archiveArt(art)"
            >
              <el-icon class="header-archive-arrow">
                <ArrowUp />
              </el-icon>
            </div>
            <div
                v-else
                class="header-archive header-archive--empty"
            ></div>
            <div class="header-posted">
              <span class="col-head">posted</span>
            </div>
          </div>

          <!-- ОСНОВНАЯ СЕТКА КАРТОЧКИ -->
          <div class="art-row-body">
            <!-- Название + иконки редактирования -->
            <div class="art-name-wrap">
              <!-- Кнопка удаления, появляется при hover -->
              <div class="art-name-actions">
                <el-button
                    class="art-name-action-btn"
                    text
                    :icon="Delete"
                    size="small"
                    @click.stop
                    title="Удалить арт"
                />
              </div>

              <!-- Режим редактирования -->
              <div
                  v-if="editingNameId === art.id"
                  class="art-name-edit"
              >
                <el-input
                    ref="editNameInput"
                    v-model="editNameValue"
                    size="small"
                    @blur="finishEditName(art)"
                    @keyup.enter="finishEditName(art)"
                />
              </div>

              <!-- Обычный режим отображения -->
              <div
                  v-else
                  class="art-name"
                  tabindex="0"
                  @click="startEditName(art)"
                  @keydown.enter.prevent="startEditName(art)"
              >
                {{ art.name }}
              </div>
            </div>

            <!-- Статус -->
            <div class="art-status col-sep">
              <div class="status-wrap">
                <div
                    v-if="isAllClosed(art)"
                    class="finish-icon"
                >
                  <el-icon>
                    <Finished />
                  </el-icon>
                </div>

                <button
                    type="button"
                    class="status-button"
                    :class="{ done: art.status === 'complete' }"
                    :aria-pressed="art.status === 'complete'"
                    :title="statusTitle(art)"
                    @click="toggleStatus(art)"
                >
                  {{ statusLabel(art.status) }}
                </button>

                <button
                    v-if="art.status === 'complete'"
                    type="button"
                    class="on-disk-button"
                    :class="{ active: art.onDisk }"
                    :aria-pressed="art.onDisk"
                    @click="toggleOnDisk(art)"
                >
                  downloaded
                </button>
              </div>
            </div>


            <!-- Тип персонажа -->
            <div class="art-type vstack col-sep">
              <button
                  type="button"
                  class="label-button"
                  :class="{ active: art.human }"
                  :aria-pressed="art.human"
                  @click="toggleFlag(art, 'human')"
              >
                human
              </button>
              <button
                  type="button"
                  class="label-button"
                  :class="{ active: art.furry }"
                  :aria-pressed="art.furry"
                  @click="toggleFlag(art, 'furry')"
              >
                furry
              </button>
            </div>

            <!-- Контент -->
            <div class="art-content vstack col-sep">
              <button
                  type="button"
                  class="label-button"
                  :class="{ active: art.sfw }"
                  :aria-pressed="art.sfw"
                  @click="toggleFlag(art, 'sfw')"
              >
                sfw
              </button>
              <button
                  type="button"
                  class="label-button"
                  :class="{ active: art.nsfw }"
                  :aria-pressed="art.nsfw"
                  @click="toggleFlag(art, 'nsfw')"
              >
                nsfw
              </button>
              <button
                  type="button"
                  class="label-button"
                  :class="{ active: art.crop }"
                  :aria-pressed="art.crop"
                  @click="toggleFlag(art, 'crop')"
              >
                crop
              </button>
            </div>

            <!-- Куда постить (план) -->
            <div class="art-post vstack col-sep">
              <button
                  type="button"
                  class="label-button"
                  :class="{ active: art.post_targets.twi16 }"
                  :aria-pressed="art.post_targets.twi16"
                  @click="toggleNestedFlag(art, 'post_targets', 'twi16')"
              >
                twi16
              </button>
              <button
                  type="button"
                  class="label-button"
                  :class="{ active: art.post_targets.twi18 }"
                  :aria-pressed="art.post_targets.twi18"
                  @click="toggleNestedFlag(art, 'post_targets', 'twi18')"
              >
                twi18
              </button>
              <button
                  type="button"
                  class="label-button"
                  :class="{ active: art.post_targets.bsky }"
                  :aria-pressed="art.post_targets.bsky"
                  @click="toggleNestedFlag(art, 'post_targets', 'bsky')"
              >
                bsky
              </button>
            </div>

            <!-- Уже выложено (факт) -->
            <div class="art-posted vstack col-sep">
              <template v-if="hasAnyPostTarget(art)">
                <el-checkbox
                    class="posted-checkbox"
                    :class="{ 'posted-checkbox--hidden': !art.post_targets.twi16 }"
                    v-model="art.posted.twi16"
                    size="small"
                    @change="handlePostedChange(art)"
                />
                <el-checkbox
                    class="posted-checkbox"
                    :class="{ 'posted-checkbox--hidden': !art.post_targets.twi18 }"
                    v-model="art.posted.twi18"
                    size="small"
                    @change="handlePostedChange(art)"
                />
                <el-checkbox
                    class="posted-checkbox"
                    :class="{ 'posted-checkbox--hidden': !art.post_targets.bsky }"
                    v-model="art.posted.bsky"
                    size="small"
                    @change="handlePostedChange(art)"
                />
              </template>

              <div v-else class="art-posted-placeholder">
                choose where to post
              </div>
            </div>

          </div>
        </div>
      </div>
    </el-scrollbar>
  </div>
</template>