<script setup>
import { ref } from 'vue'
import AccountingPayoutCard from './AccountingPayoutCard.vue'
import AccountingPayoutCreateNew from './AccountingPayoutCreateNew.vue'

defineProps({
  payouts: {
    type: Array,
    default: () => [],
  },
  orders: {
    type: Array,
    default: () => [],
  },
  externalIncomes: {
    type: Array,
    default: () => [],
  },
})

const showCreateForm = ref(false)

const emit = defineEmits(['created', 'updated'])

const handlePayoutCreated = () => {
  showCreateForm.value = false
  emit('created')
}
</script>

<template>
  <section class="payouts-block">
    <!-- Заголовок блока выводов -->
    <div class="payouts-head">
      <h2 class="section-title">Выводы</h2>

      <el-button
          type="primary"
          plain
          size="small"
          @click="showCreateForm = !showCreateForm"
      >
        {{ showCreateForm ? 'Скрыть' : '+ Добавить вывод' }}
      </el-button>
    </div>

    <!-- Форма создания нового вывода -->
    <AccountingPayoutCreateNew
        v-if="showCreateForm"
        :orders="orders"
        :external-incomes="externalIncomes"
        @created="handlePayoutCreated"
    />

    <!-- Список уже созданных выводов -->
    <div v-if="payouts.length" class="payouts-list">
      <AccountingPayoutCard
          v-for="payout in payouts"
          :key="payout.id"
          :payout="payout"
          @updated="emit('updated')"
      />
    </div>

    <!-- Пустое состояние -->
    <el-empty
        v-else
        description="Выводов за этот месяц пока нет"
    />
  </section>
</template>

<style scoped>
.payouts-block {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.payouts-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.section-title {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
}

.payouts-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
</style>