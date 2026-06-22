<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  payout: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['updated'])

const rubAmount = ref('')
const showRubEdit = ref(false)

const sourceLabels = {
  patreon: 'Patreon',
  boosty: 'Boosty',
  tip: 'Типсы',
  family: 'Родня',
  state: 'Государство',
  other: 'Другое',
}

watch(
    () => props.payout.amount_rub,
    (newValue) => {
      rubAmount.value = String(newValue || 0)
    },
    { immediate: true },
)

const canSaveRub = computed(() => {
  return Number(rubAmount.value || 0) !== Number(props.payout.amount_rub || 0)
      && Number(rubAmount.value || 0) >= 0
})

const openRubEdit = () => {
  showRubEdit.value = true
}

const saveRubAmount = async () => {
  if (!canSaveRub.value) {
    return
  }

  try {
    await http.patch(`/api/payouts/${props.payout.id}/`, {
      amount_rub: Number(rubAmount.value || 0),
    })

    ElMessage.success('Рубли сохранены')
    showRubEdit.value = false
    emit('updated')
  } catch (err) {
    console.error('failed save payout rub', err)
    ElMessage.error('Не удалось сохранить рубли')
  }
}

const formatMoney = (value) => {
  const number = Number(value || 0)

  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(number)
}

const formatUsd = (value) => {
  return `$${formatMoney(value)}`
}

const formatRub = (value) => {
  return `${formatMoney(value)} ₽`
}

const formatRate = (value) => {
  const number = Number(value || 0)

  return new Intl.NumberFormat('ru-RU', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(number)
}

const getSourceLabel = (source) => {
  return sourceLabels[source] || source || 'Прочее поступление'
}
</script>

<template>
  <article class="payout-card">
    <!-- Верх карточки: дата, курс и редактируемая сумма вывода -->
    <div class="payout-head">
      <div>
        <div class="payout-title">
          Вывод · {{ payout.date }}
        </div>

        <div class="payout-subtitle">
          {{ payout.comment || 'Без комментария' }}
        </div>

        <div class="payout-rate">
          Курс: {{ formatRate(payout.exchange_rate) }} ₽/$
        </div>
      </div>

      <div class="payout-money-block">
        <button
            class="payout-money-edit-trigger"
            type="button"
            @click="openRubEdit"
        >
          <span class="payout-money">
            {{ formatUsd(payout.amount_usd) }} → {{ formatRub(payout.amount_rub) }}
          </span>

          <span class="edit-pencil">✎</span>
        </button>

        <div
            v-if="showRubEdit"
            class="rub-edit-popover"
        >
          <el-input
              v-model="rubAmount"
              class="rub-edit-input"
              size="small"
              placeholder="Рубли"
          >
            <template #suffix>₽</template>
          </el-input>

          <el-button
              class="rub-save-button"
              :class="{ 'rub-save-button--active': canSaveRub }"
              circle
              plain
              size="small"
              :disabled="!canSaveRub"
              @click="saveRubAmount"
          >
            ✓
          </el-button>
        </div>
      </div>
    </div>

    <!-- Деньги из заказов -->
    <div
        v-if="payout.allocations?.length"
        class="payout-section"
    >
      <div class="payout-section-title">
        Заказы
      </div>

      <div
          v-for="allocation in payout.allocations"
          :key="`art-${allocation.id}`"
          class="allocation-row"
      >
        <span>{{ allocation.art_name }}</span>
        <strong>{{ formatUsd(allocation.amount_usd) }}</strong>
      </div>
    </div>

    <!-- Деньги из прочих поступлений -->
    <div
        v-if="payout.external_allocations?.length"
        class="payout-section"
    >
      <div class="payout-section-title">
        Прочие поступления
      </div>

      <div
          v-for="allocation in payout.external_allocations"
          :key="`external-${allocation.id}`"
          class="allocation-row"
      >
        <span>
          {{ getSourceLabel(allocation.source) }}
          <small v-if="allocation.note">· {{ allocation.note }}</small>
        </span>

        <strong>{{ formatUsd(allocation.amount_usd) }}</strong>
      </div>
    </div>
  </article>
</template>

<style scoped>
.payout-card {
  width: 100%;
  padding: 18px 20px;
  border-radius: 18px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  box-sizing: border-box;
}

.payout-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
}

.payout-title {
  font-size: 17px;
  font-weight: 800;
  color: var(--el-text-color-primary);
}

.payout-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.payout-rate {
  margin-top: 10px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.payout-money-block {
  position: relative;
  display: flex;
  justify-content: flex-end;
}

.payout-money-edit-trigger {
  border: none;
  padding: 0;
  background: transparent;
  cursor: pointer;

  display: flex;
  align-items: center;
  gap: 8px;
}

.payout-money {
  font-size: 22px;
  font-weight: 800;
  color: var(--el-color-success);
  white-space: nowrap;
}

.edit-pencil {
  opacity: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  transition: opacity 0.15s ease;
}

.payout-money-edit-trigger:hover .edit-pencil {
  opacity: 1;
}

.rub-edit-popover {
  position: absolute;
  z-index: 10;
  top: calc(100% + 8px);
  right: 0;

  display: grid;
  grid-template-columns: 120px 24px;
  gap: 8px;
  align-items: center;

  padding: 8px;
  border-radius: 12px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.rub-edit-input {
  width: 120px;
}

.rub-save-button {
  width: 24px;
  height: 24px;
  color: var(--el-text-color-placeholder);
  border-color: var(--el-border-color-lighter);
  background: var(--el-fill-color-lighter);
}

.rub-save-button--active {
  color: var(--el-color-success);
  border-color: var(--el-color-success-light-5);
  background: var(--el-color-success-light-9);
}

.rub-save-button--active:hover {
  color: white;
  border-color: var(--el-color-success);
  background: var(--el-color-success);
}

.payout-section {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--el-border-color-lighter);

  display: flex;
  flex-direction: column;
  gap: 8px;
}

.payout-section-title {
  margin-bottom: 2px;
  font-size: 12px;
  font-weight: 700;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.allocation-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  font-size: 14px;
}

.allocation-row span {
  color: var(--el-text-color-primary);
}

.allocation-row small {
  color: var(--el-text-color-secondary);
}

.allocation-row strong {
  color: var(--el-text-color-primary);
  white-space: nowrap;
}

@media (max-width: 760px) {
  .payout-head {
    flex-direction: column;
  }

  .payout-money {
    white-space: normal;
  }
}
</style>