<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  items: { type: Array, default: () => [] },
})

const paymentLabels = {
  unpaid: 'Не оплачена',
  partially_paid: 'Частично оплачена',
  fully_paid: 'Фул оплачена',
  half_before_sketch: 'Половина до скетча',
}

const paymentTypes = {
  unpaid: 'danger',
  partially_paid: 'warning',
  fully_paid: 'success',
  half_before_sketch: 'primary',
}

const payoutLabels = {
  not_withdrawn: 'Не выведено',
  withdrawn: 'Выведено',
}

const payoutTypes = {
  not_withdrawn: 'info',
  withdrawn: 'success',
}

const paymentOptions = Object.entries(paymentLabels).map(([value, label]) => ({
  value,
  label,
}))

const payoutOptions = Object.entries(payoutLabels).map(([value, label]) => ({
  value,
  label,
}))

const saveOrderFields = async (row) => {
  try {
    await http.patch(`/api/arts/${row.id}/`, {
      order_month: row.order_month,
      price: row.price,
      payment_status: row.payment_status,
      payout_status: row.payout_status,
    })

    ElMessage.success('Заказ сохранён')
  } catch (err) {
    ElMessage.error('Не удалось сохранить заказ')
  }
}

const formatMoney = (value) => {
  const amount = Number(value || 0)

  return new Intl.NumberFormat('ru-RU', {
    maximumFractionDigits: 0,
  }).format(amount)
}

const rows = computed(() => props.items)

const totalPrice = computed(() => {
  return rows.value.reduce((sum, row) => {
    return sum + Number(row.price || 0)
  }, 0)
})

const monthGroups = computed(() => {
  const groups = new Map()

  rows.value.forEach((row) => {
    const month = row.order_month || 'Без месяца'

    const current = groups.get(month) || {
      month,
      count: 0,
      total: 0,
    }

    current.count += 1
    current.total += Number(row.price || 0)

    groups.set(month, current)
  })

  return Array.from(groups.values()).sort((a, b) => {
    return b.month.localeCompare(a.month)
  })
})
</script>

<template>
  <div class="orders-view">
    <div class="orders-summary">
      <el-card
          v-for="group in monthGroups"
          :key="group.month"
          class="orders-summary-card"
          shadow="never"
      >
        <div class="orders-summary-month">
          {{ group.month }}
        </div>

        <div class="orders-summary-meta">
          <span>{{ group.count }} заказ(ов)</span>
          <strong>{{ formatMoney(group.total) }}</strong>
        </div>
      </el-card>

      <el-card
          class="orders-summary-card orders-summary-card--total"
          shadow="never"
      >
        <div class="orders-summary-month">
          Итого
        </div>

        <div class="orders-summary-meta">
          <span>{{ rows.length }} заказ(ов)</span>
          <strong>{{ formatMoney(totalPrice) }}</strong>
        </div>
      </el-card>
    </div>

    <el-table
        :data="rows"
        style="width: 100%"
        size="large"
        stripe
    >
      <el-table-column
          label="Месяц"
          width="140"
          sortable
          prop="order_month"
      >
        <template #default="{ row }">
          <el-input
              v-model="row.order_month"
              size="small"
              placeholder="YYYY-MM"
              @change="saveOrderFields(row)"
          />
        </template>
      </el-table-column>

      <el-table-column
          prop="name"
          label="Заказ"
          min-width="220"
      />

      <el-table-column
          label="Стоимость"
          width="160"
          align="right"
          sortable
          prop="price"
      >
        <template #default="{ row }">
          <el-input-number
              v-model="row.price"
              class="order-price-input"
              :min="0"
              :controls="false"
              size="small"
              @change="saveOrderFields(row)"
          />
        </template>
      </el-table-column>

      <el-table-column
          label="Статус оплаты"
          min-width="220"
      >
        <template #default="{ row }">
          <el-select
              v-model="row.payment_status"
              size="small"
              @change="saveOrderFields(row)"
          >
            <el-option
                v-for="option in paymentOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
            >
              <el-tag :type="paymentTypes[option.value] || 'info'">
                {{ option.label }}
              </el-tag>
            </el-option>
          </el-select>
        </template>
      </el-table-column>

      <el-table-column
          label="Вывод"
          width="170"
      >
        <template #default="{ row }">
          <el-select
              v-model="row.payout_status"
              size="small"
              @change="saveOrderFields(row)"
          >
            <el-option
                v-for="option in payoutOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
            >
              <el-tag :type="payoutTypes[option.value] || 'info'">
                {{ option.label }}
              </el-tag>
            </el-option>
          </el-select>
        </template>
      </el-table-column>

      <el-table-column
          prop="status"
          label="Статус арта"
          width="150"
      />
    </el-table>
  </div>
</template>

<style scoped>
.orders-view {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.orders-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.orders-summary-card :deep(.el-card__body) {
  padding: 14px 16px;
}

.orders-summary-card--total {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
}

.orders-summary-month {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin-bottom: 6px;
}

.orders-summary-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.orders-summary-meta strong {
  color: var(--el-text-color-primary);
  font-size: 18px;
}

.order-price-input {
  width: 120px;
}
</style>