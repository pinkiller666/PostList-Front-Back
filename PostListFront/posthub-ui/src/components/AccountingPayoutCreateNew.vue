<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  orders: {
    type: Array,
    default: () => [],
  },
  externalIncomes: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['created'])

const draftPayout = ref({
  amountRub: '',
  allocations: {},
  externalAllocations: {},
})

const hasAvailableMoney = computed(() => {
  return availableOrders.value.length > 0
      || availableExternalIncomes.value.length > 0
})

const availableExternalIncomes = computed(() => {
  return props.externalIncomes.filter((income) => {
    return Number(income.broker_usd || 0) > 0
  })
})

const availableOrders = computed(() => {
  return props.orders.filter((order) => {
    return Number(order.broker_usd || 0) > 0
  })
})

const totalUsd = computed(() => {
  const ordersTotal = Object.values(draftPayout.value.allocations).reduce((sum, value) => {
    return sum + Number(value || 0)
  }, 0)

  const externalTotal = Object.values(draftPayout.value.externalAllocations).reduce((sum, value) => {
    return sum + Number(value || 0)
  }, 0)

  return ordersTotal + externalTotal
})

const hasSomethingToSave = computed(() => {
  return totalUsd.value > 0
})

const setAllAvailable = () => {
  availableOrders.value.forEach((order) => {
    draftPayout.value.allocations[order.id] = Number(order.broker_usd || 0)
  })

  availableExternalIncomes.value.forEach((income) => {
    draftPayout.value.externalAllocations[income.id] = Number(income.amount_usd || 0)
  })
}

const createPayout = async () => {
  if (!hasSomethingToSave.value) {
    return
  }

  const allocations = Object.entries(draftPayout.value.allocations)
      .map(([artId, amount]) => {
        return {
          art_id: Number(artId),
          amount_usd: Number(amount || 0),
        }
      })
      .filter((item) => item.amount_usd > 0)

  const externalAllocations = Object.entries(draftPayout.value.externalAllocations)
      .map(([incomeId, amount]) => {
        return {
          external_income_id: Number(incomeId),
          amount_usd: Number(amount || 0),
        }
      })
      .filter((item) => item.amount_usd > 0)

  try {
    await http.post('/api/payouts/', {
      amount_rub: draftPayout.value.amountRub || 0,
      allocations,
      external_allocations: externalAllocations,
    })

    draftPayout.value = {
      amountRub: '',
      allocations: {},
      externalAllocations: {},
    }

    ElMessage.success('Вывод создан')
    emit('created')
  } catch (err) {
    console.error('failed create payout', err)
    ElMessage.error('Не удалось создать вывод')
  }
}
</script>

<template>
  <el-card
      class="payout-create-card"
      shadow="never"
  >
    <!-- Верх формы: главный итог и подтверждение всего вывода -->
    <div class="create-head">
      <div class="create-total">
        <span>Выводим</span>
        <strong>${{ totalUsd }}</strong>
      </div>

      <el-button
          class="confirm-payout-button"
          :class="{ 'confirm-payout-button--active': hasSomethingToSave }"
          circle
          plain
          :disabled="!hasSomethingToSave"
          @click="createPayout"
      >
        ✓
      </el-button>
    </div>

    <!-- Рубли по факту: можно заполнить сразу или позже -->
    <div class="rub-row">
      <span class="rub-label">Рубли по факту</span>

      <el-input
          v-model="draftPayout.amountRub"
          class="rub-input"
          placeholder="Можно дописать позже"
      >
        <template #prefix>₽</template>
      </el-input>
    </div>

    <!-- Распределение вывода по заказам -->
    <div class="allocation-table">
      <div class="allocation-header">
        <span>Заказ</span>
        <span>У посредника</span>
        <span>Сколько выводим</span>
      </div>

      <div
          v-for="order in availableOrders"
          :key="order.id"
          class="allocation-row"
      >
        <div class="allocation-name">
          {{ order.name }}
        </div>

        <div class="allocation-broker">
          ${{ order.broker_usd }}
        </div>

        <el-input-number
            v-model="draftPayout.allocations[order.id]"
            class="allocation-input"
            :min="0"
            :max="Number(order.broker_usd || 0)"
            :controls="false"
            size="small"
        />
      </div>

      <div
          v-if="availableExternalIncomes.length > 0"
          class="allocation-group"
      >
        <div class="allocation-group-title">
          Прочие поступления
        </div>

        <div
            v-for="income in availableExternalIncomes"
            :key="income.id"
            class="allocation-row"
        >
          <div class="allocation-name">
            {{ income.source }}
            <span v-if="income.note">· {{ income.note }}</span>
          </div>

          <div class="allocation-broker">
            ${{ income.amount_usd }}
          </div>

          <el-input-number
              v-model="draftPayout.externalAllocations[income.id]"
              class="allocation-input"
              :min="0"
              :max="Number(income.amount_usd || 0)"
              :controls="false"
              size="small"
          />
        </div>
      </div>

      <el-empty
          v-if="!hasAvailableMoney"
          description="Нет денег у посредника для вывода"
      />

      <div
          v-if="hasAvailableMoney"
          class="allocation-actions"
      >
        <el-button
            class="all-available-button"
            size="small"
            plain
            @click="setAllAvailable"
        >
          всё доступное
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.payout-create-card {
  border-radius: 18px;
}

.payout-create-card :deep(.el-card__body) {
  padding: 18px 20px 20px;
}

.create-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.create-total {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.create-total span {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.create-total strong {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
}

.rub-row {
  margin-top: 18px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.rub-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

.rub-input {
  width: 240px;
}

.allocation-table {
  margin-top: 22px;
  margin-left: 28px;
  padding-left: 18px;
  border-left: 1px solid var(--el-border-color-lighter);

  display: flex;
  flex-direction: column;
  gap: 8px;
}

.allocation-header {
  display: grid;
  grid-template-columns: minmax(180px, 260px) 120px 140px;
  gap: 12px;
  align-items: center;

  font-size: 12px;
  color: var(--el-text-color-secondary);
  padding-bottom: 4px;
}

.allocation-row {
  display: grid;
  grid-template-columns: minmax(180px, 260px) 120px 140px;
  gap: 12px;
  align-items: center;

  opacity: 0.86;
}

.allocation-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.allocation-broker {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.allocation-input {
  width: 140px;
}

.allocation-actions {
  display: grid;
  grid-template-columns: minmax(180px, 260px) 120px 140px;
  gap: 12px;
  margin-top: 4px;
}

.all-available-button {
  grid-column: 3;
}

.confirm-payout-button {
  width: 34px;
  height: 34px;

  color: var(--el-text-color-placeholder);
  border-color: var(--el-border-color-lighter);
  background: var(--el-fill-color-lighter);
}

.confirm-payout-button--active {
  width: 38px;
  height: 38px;

  color: var(--el-color-success);
  border-color: var(--el-color-success-light-5);
  background: var(--el-color-success-light-9);
}

.confirm-payout-button--active:hover {
  color: white;
  border-color: var(--el-color-success);
  background: var(--el-color-success);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.25);
}

.confirm-payout-button--active:active {
  transform: translateY(1px);
}

.confirm-payout-button.is-disabled,
.confirm-payout-button.is-disabled:hover {
  color: var(--el-text-color-placeholder);
  border-color: var(--el-border-color-lighter);
  background: var(--el-fill-color-lighter);
}

.allocation-group {
  margin-top: 14px;
}

.allocation-group-title {
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--el-text-color-secondary);
  text-transform: lowercase;
}

.allocation-name span {
  font-weight: 400;
  color: var(--el-text-color-secondary);
}

@media (max-width: 760px) {
  .rub-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .rub-input {
    width: 100%;
  }

  .allocation-header {
    display: none;
  }

  .allocation-row,
  .allocation-actions {
    grid-template-columns: 1fr;
  }

  .allocation-input {
    width: 100%;
  }

  .all-available-button {
    grid-column: auto;
  }

}
</style>