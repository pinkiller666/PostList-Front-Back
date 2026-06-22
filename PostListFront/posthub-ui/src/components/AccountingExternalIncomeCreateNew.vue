<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  selectedMonth: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['created'])

const isSaving = ref(false)

const sourceOptions = [
  { value: 'patreon', label: 'Patreon' },
  { value: 'boosty', label: 'Boosty' },
  { value: 'tip', label: 'Типсы' },
  { value: 'family', label: 'Родня' },
  { value: 'state', label: 'Государство' },
  { value: 'other', label: 'Другое' },
]

const draftIncome = ref({
  orderMonth: props.selectedMonth,
  source: 'patreon',
  amountUsd: 0,
  receivedVia: 'broker',
  note: '',
})

watch(
    () => props.selectedMonth,
    (newMonth) => {
      draftIncome.value.orderMonth = newMonth
    },
)

const canSave = computed(() => {
  return draftIncome.value.orderMonth
      && draftIncome.value.source
      && Number(draftIncome.value.amountUsd || 0) > 0
})

const createIncome = async () => {
  if (!canSave.value || isSaving.value) {
    return
  }

  isSaving.value = true

  try {
    await http.post('/api/external-incomes/', {
      order_month: draftIncome.value.orderMonth,
      source: draftIncome.value.source,
      amount_usd: Number(draftIncome.value.amountUsd || 0),
      currency: 'usd',
      received_via: draftIncome.value.receivedVia,
      note: draftIncome.value.note.trim(),
    })

    draftIncome.value = {
      orderMonth: props.selectedMonth,
      source: 'patreon',
      amountUsd: 0,
      receivedVia: 'broker',
      note: '',
    }

    ElMessage.success('Поступление добавлено')
    emit('created')
  } catch (err) {
    console.error('failed create external income', err)
    ElMessage.error('Не удалось добавить поступление')
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <el-card class="external-income-create-card" shadow="never">
    <div class="create-head">
      <div class="create-title-block">
        <span class="create-label">Новое поступление</span>
        <strong>Добавить не-арт доход</strong>
      </div>

      <div class="save-action">
        <el-button
            class="confirm-income-button"
            :class="{ 'confirm-income-button--active': canSave }"
            circle
            plain
            :loading="isSaving"
            :disabled="!canSave"
            @click="createIncome"
        >
          ✓
        </el-button>

        <span class="save-label">сохранить</span>
      </div>
    </div>

    <div class="create-fields">
      <label class="income-field">
        <span>Месяц</span>

        <el-date-picker
            v-model="draftIncome.orderMonth"
            type="month"
            value-format="YYYY-MM"
            format="MMMM YYYY"
            placeholder="Месяц"
            :clearable="false"
        />
      </label>

      <label class="income-field">
        <span>Источник</span>

        <el-select
            v-model="draftIncome.source"
            placeholder="Источник"
        >
          <el-option
              v-for="option in sourceOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
          />
        </el-select>
      </label>

      <label class="income-field">
        <span>Куда пришли</span>

        <el-select
            v-model="draftIncome.receivedVia"
            placeholder="Куда пришли"
        >
          <el-option
              label="Через посредника"
              value="broker"
          />

          <el-option
              label="Напрямую"
              value="direct"
          />
        </el-select>
      </label>

      <label class="income-field income-field--amount">
        <span>Сумма</span>

        <el-input-number
            v-model="draftIncome.amountUsd"
            class="amount-input"
            :min="0"
            :controls="false"
        >
          <template #prefix>$</template>
        </el-input-number>
      </label>

      <label class="income-field income-field--note">
        <span>Заметка</span>

        <el-input
            v-model="draftIncome.note"
            placeholder="Например: May Patreon"
        />
      </label>
    </div>
  </el-card>
</template>

<style scoped>
.external-income-create-card {
  width: 100%;
  border-radius: 18px;
  border-color: var(--el-color-primary-light-7);
  background: var(--el-color-primary-light-9);
}

.external-income-create-card :deep(.el-card__body) {
  padding: 18px 20px 20px;
}

.create-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.create-title-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.create-label,
.income-field span,
.save-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.create-title-block strong {
  font-size: 20px;
  font-weight: 800;
}

.save-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.create-fields {
  margin-top: 18px;
  display: grid;
  grid-template-columns: 160px 160px 120px 1fr;
  gap: 14px;
  align-items: end;
}

.income-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.amount-input {
  width: 100%;
}

.confirm-income-button {
  width: 34px;
  height: 34px;
  color: var(--el-text-color-placeholder);
  border-color: var(--el-border-color-lighter);
  background: var(--el-fill-color-lighter);
}

.confirm-income-button--active {
  width: 38px;
  height: 38px;
  color: var(--el-color-success);
  border-color: var(--el-color-success-light-5);
  background: var(--el-color-success-light-9);
}

.confirm-income-button--active:hover {
  color: white;
  border-color: var(--el-color-success);
  background: var(--el-color-success);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.25);
}

@media (max-width: 900px) {
  .create-fields {
    grid-template-columns: 1fr;
  }
}
</style>