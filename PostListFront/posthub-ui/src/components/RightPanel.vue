<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { Lock, Unlock, Edit, Delete } from '@element-plus/icons-vue'
import './RightPanel.css'
import { mapArtFromApi } from '../api/artMappers'
import { updateArt } from '../api/artApi'

const savingError = ref(null)
const statusLabel = (s) => (s ? s.replace(/_/g, ' ') : '')

const API_BASE = 'http://127.0.0.1:8081'          // если нужно — поправишь порт/хост
const ARTS_ENDPOINT = `${API_BASE}/api/arts/`     // эндпоинт arts_list

const arts = ref([])
const isLoading = ref(false)
const loadError = ref(null)

const loadArts = async () => {
  isLoading.value = true
  loadError.value = null

  try {
    const resp = await fetch(ARTS_ENDPOINT, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    })

    if (!resp.ok) {
      throw new Error(`Ошибка загрузки: ${resp.status} ${resp.statusText}`)
    }

    const data = await resp.json()
    const items = Array.isArray(data.items) ? data.items : []

    arts.value = items.map(mapArtFromApi)
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

const toggleRowLock = (art) => {
  art.locked = !art.locked
  saveArt(art)
}

// было тернарным адом — теперь обычный if/else
const nextStatus = (art) => {
  if (art.status === 'complete') {
    return 'in_progress'
  }
  return 'complete'
}

const statusTitle = (art) => `Сменить статус на ${statusLabel(nextStatus(art))}`

const toggleStatus = (art) => {
  if (art.locked) return
  art.status = nextStatus(art)
  saveArt(art)
}

const toggleFlag = (art, key) => {
  if (art.locked) return
  art[key] = !art[key]
  saveArt(art)
}

const toggleNestedFlag = (art, scope, key) => {
  if (art.locked) return
  art[scope][key] = !art[scope][key]
  saveArt(art)
}

/* --- Редактирование названия --- */

const editingNameId = ref(null)
const editNameValue = ref('')
const editNameInput = ref(null)

const startEditName = (art) => {
  if (art.locked) return
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
      <h2 class="panel-title">Арты</h2>
    </div>
    <el-scrollbar class="scroll-area">
      <div class="panel-list">
        <div
            v-for="art in arts"
            :key="art.id"
            class="art-row"
            :class="{ frozen: art.locked }"
        >
          <!-- ВЕРХНЯЯ ПОЛОСА: только заголовок "выложено" -->
          <div class="art-row-header">
            <div class="header-lock"></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div class="header-posted">
              <span class="col-head">выложено</span>
            </div>
          </div>

          <!-- ОСНОВНАЯ СЕТКА КАРТОЧКИ -->
          <div class="art-row-body">
            <!-- Название + плавающий замок + иконки редактирования -->
            <div class="art-name-wrap">
              <el-button
                  circle
                  size="small"
                  class="lock-icon-btn floating-lock"
                  :class="{
                  'is-locked': art.locked,
                  'is-unlocked': !art.locked
                }"
                  :title="art.locked ? 'Разблокировать' : 'Заблокировать'"
                  @click.stop="toggleRowLock(art)"
              >
                <el-icon>
                  <Lock v-if="art.locked" />
                  <Unlock v-else />
                </el-icon>
              </el-button>

              <!-- Кнопки редактировать / удалить, появляются при hover -->
              <div class="art-name-actions">
                <el-button
                    class="art-name-action-btn"
                    text
                    :icon="Edit"
                    size="small"
                    @click.stop="startEditName(art)"
                    title="Редактировать название"
                />
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
              <div v-else class="art-name">
                {{ art.name }}
              </div>
            </div>

            <!-- Статус -->
            <div class="art-status col-sep">
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
              <el-checkbox
                  v-model="art.posted.twi16"
                  size="small"
                  @change="saveArt(art)"
              />
              <el-checkbox
                  v-model="art.posted.twi18"
                  size="small"
                  @change="saveArt(art)"
              />
              <el-checkbox
                  v-model="art.posted.bsky"
                  size="small"
                  @change="saveArt(art)"
              />
            </div>
          </div>
        </div>
      </div>
    </el-scrollbar>
    </div>
</template>
