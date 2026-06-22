<script setup>
import AccountingOrderCard from './AccountingOrderCard.vue'
import AccountingPayoutsBlock from './AccountingPayoutsBlock.vue'
import AccountingOrderCreateNew from './AccountingOrderCreateNew.vue'
import AccountingExternalIncomeCreateNew from './AccountingExternalIncomeCreateNew.vue'

import {computed, ref, onMounted} from 'vue'
import http from '../api/http'

const orders = ref([])
const payouts = ref([])
const isLoading = ref(false)
const showCreateOrderForm = ref(false)
const externalIncomes = ref([])

const getCurrentMonth = () => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

const selectedMonth = ref(getCurrentMonth())

const showCreateExternalIncomeForm = ref(false)

const handleExternalIncomeCreated = async () => {
  showCreateExternalIncomeForm.value = false
  await loadAccounting()
}

const totalOrdersUsd = computed(() => {
  return orders.value.reduce((sum, order) => {
    return sum + Number(order.price || 0)
  }, 0)
})

const totalPayoutUsd = computed(() => {
  return payouts.value.reduce((sum, payout) => {
    return sum + Number(payout.amount_usd || 0)
  }, 0)
})

const totalPayoutRub = computed(() => {
  return payouts.value.reduce((sum, payout) => {
    return sum + Number(payout.amount_rub || 0)
  }, 0)
})

const expectedUsd = computed(() => {
  return Math.max(totalOrdersUsd.value - totalPayoutUsd.value, 0)
})

const loadAccounting = async () => {
  isLoading.value = true

  try {
    const {data} = await http.get('/api/accounting/month/', {
      params: {
        month: selectedMonth.value,
      },
    })

    orders.value = data.orders || []
    payouts.value = data.payouts || []
    externalIncomes.value = data.external_incomes || []
  } catch (err) {
    console.error('failed load accounting', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadAccounting()
})
</script>

<template>
  <section class="accounting-page">
    <header class="accounting-header">
      <div class="header-left">
        <h1 class="page-title">Бухгалтерия</h1>

        <el-date-picker
            v-model="selectedMonth"
            type="month"
            value-format="YYYY-MM"
            format="MMMM YYYY"
            placeholder="Выбери месяц"
            :clearable="false"
            @change="loadAccounting"
        />
      </div>

      <div class="header-right">
        <el-card class="money-card" shadow="never">
          <div class="money-label">Всего заказов</div>
          <div class="money-value">${{ totalOrdersUsd }}</div>
        </el-card>

        <el-card class="money-card" shadow="never">
          <div class="money-label">Выведено</div>
          <div class="money-value">${{ totalPayoutUsd }}</div>
        </el-card>

        <el-card class="money-card" shadow="never">
          <div class="money-label">Ожидается</div>
          <div class="money-value">${{ expectedUsd }}</div>
        </el-card>
      </div>
    </header>

    <section class="orders-section">
      <div class="section-title-row">
        <h2 class="section-title">Заказы</h2>

        <el-button
            type="primary"
            plain
            size="small"
            @click="showCreateOrderForm = !showCreateOrderForm"
        >
          {{ showCreateOrderForm ? 'Скрыть' : '+ Добавить заказ' }}
        </el-button>
      </div>

      <AccountingOrderCreateNew
          v-if="showCreateOrderForm"
          :selected-month="selectedMonth"
          @created="loadAccounting"
      />

      <div v-if="orders.length" class="orders-list">
        <AccountingOrderCard
            v-for="order in orders"
            :key="order.id"
            :order="order"
            @updated="loadAccounting"
        />
      </div>

      <el-empty v-else description="Заказов за этот месяц пока нет"/>
    </section>


    <section class="external-income-section">
      <div class="section-title-row">
        <h2 class="section-title">Прочие поступления</h2>

        <el-button
            type="primary"
            plain
            size="small"
            @click="showCreateExternalIncomeForm = !showCreateExternalIncomeForm"
        >
          {{ showCreateExternalIncomeForm ? 'Скрыть' : '+ Добавить поступление' }}
        </el-button>
      </div>

      <AccountingExternalIncomeCreateNew
          v-if="showCreateExternalIncomeForm"
          :selected-month="selectedMonth"
          @created="handleExternalIncomeCreated"
      />

      <div
          v-if="externalIncomes.length"
          class="external-income-list"
      >
        <el-card
            v-for="income in externalIncomes"
            :key="income.id"
            class="external-income-card"
            shadow="never"
        >
          <div class="external-income-main">
            <div>
              <div class="external-income-source">
                {{ income.source }}
              </div>

              <div class="external-income-note">
                {{ income.note || 'Без комментария' }}
              </div>
            </div>

            <div class="external-income-amount">
              ${{ income.amount_usd }}
            </div>
          </div>
        </el-card>
      </div>

      <el-empty
          v-else
          description="Прочих поступлений за этот месяц пока нет"
      />
    </section>


    <AccountingPayoutsBlock
        :payouts="payouts"
        :orders="orders"
        :external-incomes="externalIncomes"
        @created="loadAccounting"
        @updated="loadAccounting"
    />

    <section class="summary-section">
      <h2 class="section-title">Итоги месяца</h2>

      <div class="summary-grid">
        <el-card shadow="never">
          <div class="summary-label">Выведено в рублях</div>
          <div class="summary-value">₽{{ totalPayoutRub }}</div>
        </el-card>
      </div>
    </section>
  </section>
</template>

<style scoped>
.accounting-page {
  width: 100%;
  max-width: 980px;
  margin: 0 auto;
  padding: 40px 32px 80px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.accounting-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.page-title {
  margin: 0;
  font-size: 34px;
  font-weight: 800;
  line-height: 1;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.header-right {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  width: 100%;
}

.money-card,
.payout-card {
  border-radius: 18px;
  background: var(--el-bg-color);
}

.money-label,
.summary-label,
.payout-rate {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.money-value,
.summary-value {
  margin-top: 8px;
  font-size: 24px;
  font-weight: 800;
}

.orders-list,
.payouts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title {
  margin: 0 0 14px;
  font-size: 22px;
  font-weight: 800;
}

.payout-title {
  font-weight: 700;
}

.payout-money {
  margin-top: 8px;
  font-size: 20px;
  font-weight: 800;
}

.payout-rate {
  margin-top: 6px;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.orders-section {
  width: 100%;
  max-width: 760px;
}

.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.external-income-section {
  width: 100%;
  max-width: 760px;
}

.external-income-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.external-income-card {
  border-radius: 16px;
}

.external-income-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.external-income-source {
  font-size: 16px;
  font-weight: 700;
}

.external-income-note {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.external-income-amount {
  font-size: 20px;
  font-weight: 800;
  color: var(--el-color-primary);
  white-space: nowrap;
}
</style>