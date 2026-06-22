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

const currencyOptions = [
  { value: 'usd', label: 'USD', symbol: '$' },
  { value: 'rub', label: 'RUB', symbol: '₽' },
]

const draftOrder = ref({
  name: '',
  price: 0,
  priceCurrency: 'usd',
  orderMonth: props.selectedMonth,
})

watch(
    () => props.selectedMonth,
    (newMonth) => {
      draftOrder.value.orderMonth = newMonth
    },
)

const priceCurrencySymbol = computed(() => {
  const currency = currencyOptions.find((option) => {
    return option.value === draftOrder.value.priceCurrency
  })

  if (!currency) {
    return '$'
  }

  return currency.symbol
})

const canSave = computed(() => {
  return draftOrder.value.name.trim()
      && Number(draftOrder.value.price || 0) > 0
      && draftOrder.value.priceCurrency
      && draftOrder.value.orderMonth
})

const createOrder = async () => {
  if (!canSave.value || isSaving.value) {
    return
  }

  isSaving.value = true

  try {
    await http.post('/api/arts/', {
      name: draftOrder.value.name.trim(),
      price: Number(draftOrder.value.price || 0),
      price_currency: draftOrder.value.priceCurrency,
      order_month: draftOrder.value.orderMonth,
      status: 'waiting_to_start',
    })

    // reset
    draftOrder.value = {
      name: '',
      price: 0,
      priceCurrency: 'usd',
      orderMonth: props.selectedMonth,
    }

    ElMessage.success('Заказ создан')
    emit('created')
  } catch (err) {
    console.error('failed create order', err)
    ElMessage.error('Не удалось создать заказ')
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <el-card class="order-create-card" shadow="never">
    <!-- Верх формы: что создаём и кнопка сохранения -->
    <div class="create-head">
      <div class="create-title-block">
        <span class="create-label">Новый заказ</span>
        <strong>Добавить заказ</strong>
      </div>

      <div class="save-action">
        <el-button
            class="confirm-order-button"
            :class="{ 'confirm-order-button--active': canSave }"
            circle
            plain
            :loading="isSaving"
            :disabled="!canSave"
            @click="createOrder"
        >
          ✓
        </el-button>

        <span class="save-label">сохранить заказ</span>
      </div>
    </div>

    <!-- Месяц заказа: по умолчанию копируется из выбранного месяца бухгалтерии -->
    <div class="month-row">
      <span class="month-label">Месяц заказа</span>

      <el-date-picker
          v-model="draftOrder.orderMonth"
          class="month-picker"
          type="month"
          value-format="YYYY-MM"
          format="MMMM YYYY"
          placeholder="Выбрать месяц"
          :clearable="false"
      />
    </div>

    <!-- Основные поля заказа -->
    <div class="create-fields">
      <label class="order-field order-field--name">
        <span>Название заказа</span>

        <el-input
            v-model="draftOrder.name"
            placeholder="Например: Marvel YCH"
        />
      </label>

      <label class="order-field order-field--currency">
        <span>Валюта</span>

        <el-select
            v-model="draftOrder.priceCurrency"
            class="currency-select"
            placeholder="Валюта"
        >
          <el-option
              v-for="option in currencyOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
          />
        </el-select>
      </label>

      <label class="order-field order-field--price">
        <span>Полная стоимость</span>

        <el-input-number
            v-model="draftOrder.price"
            class="price-input"
            :min="0"
            :controls="false"
        >
          <template #prefix>{{ priceCurrencySymbol }}</template>
        </el-input-number>
      </label>
    </div>
  </el-card>
</template>

<style scoped>
.order-create-card {
  width: 100%;
  border-radius: 18px;
  border-color: var(--el-color-primary-light-7);
  background: var(--el-color-primary-light-9);
}

.order-create-card :deep(.el-card__body) {
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
.order-field span,
.save-label,
.month-label {
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

.month-row {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.month-picker {
  width: 200px;
}

.create-fields {
  margin-top: 18px;
  display: grid;
  grid-template-columns: minmax(240px, 1fr) 110px 180px;
  gap: 14px;
  align-items: end;
}

.order-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.price-input {
  width: 100%;
}

.currency-select {
  width: 100%;
}

.confirm-order-button {
  width: 34px;
  height: 34px;
  color: var(--el-text-color-placeholder);
  border-color: var(--el-border-color-lighter);
  background: var(--el-fill-color-lighter);
}

.confirm-order-button--active {
  width: 38px;
  height: 38px;
  color: var(--el-color-success);
  border-color: var(--el-color-success-light-5);
  background: var(--el-color-success-light-9);
}

.confirm-order-button--active:hover {
  color: white;
  border-color: var(--el-color-success);
  background: var(--el-color-success);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.25);
}

@media (max-width: 760px) {
  .month-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .month-picker {
    width: 100%;
  }

  .create-fields {
    grid-template-columns: 1fr;
  }
}
</style>