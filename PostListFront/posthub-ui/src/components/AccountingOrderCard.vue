<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const props = defineProps({
  order: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['updated'])

const totalAmount = ref(0)
const withdrawnAmount = ref(0)
const brokerAmount = ref(0)
const directAmount = ref(0)
const paymentFlow = ref('broker')

const showAddPayment = ref(false)
const newPaymentAmount = ref('')
const isSavingPrice = ref(false)
const isSavingPayment = ref(false)

const syncFromOrder = () => {
  totalAmount.value = Number(props.order.price || 0)
  withdrawnAmount.value = Number(props.order.withdrawn_usd || 0)
  brokerAmount.value = Number(props.order.broker_usd || 0)
  directAmount.value = Number(props.order.direct_usd || 0)

  if (directAmount.value > 0 && brokerAmount.value === 0 && withdrawnAmount.value === 0) {
    paymentFlow.value = 'direct'
  } else {
    paymentFlow.value = 'broker'
  }
}

watch(
    () => props.order,
    () => {
      syncFromOrder()
    },
    { immediate: true },
)

const paidTotalAmount = computed(() => {
  return withdrawnAmount.value + brokerAmount.value + directAmount.value
})

const paidPercent = computed(() => {
  if (!totalAmount.value) return 0

  return Math.min(
      Math.round((paidTotalAmount.value / totalAmount.value) * 100),
      100,
  )
})

const maxNewPaymentAmount = computed(() => {
  return Math.max(totalAmount.value - paidTotalAmount.value, 0)
})

const currentReceivedAmount = computed(() => {
  if (paymentFlow.value === 'direct') {
    return directAmount.value
  }

  return brokerAmount.value
})

const currentFlowLabel = computed(() => {
  if (paymentFlow.value === 'direct') {
    return 'Напрямую'
  }

  return 'У посредника'
})

const setPaymentFlow = (flow) => {
  if (paidTotalAmount.value > 0 && flow !== paymentFlow.value) {
    ElMessage.warning('Нельзя менять способ получения после добавления оплаты')
    return
  }

  paymentFlow.value = flow
  closeAddPayment()
}

const canAddPayment = computed(() => {
  const value = Number(newPaymentAmount.value || 0)
  return value > 0 && value <= maxNewPaymentAmount.value
})

const savePrice = async () => {
  if (isSavingPrice.value) return

  isSavingPrice.value = true

  try {
    await http.patch(`/api/arts/${props.order.id}/`, {
      price: Number(totalAmount.value || 0),
    })

    ElMessage.success('Стоимость сохранена')
    emit('updated')
  } catch (err) {
    console.error('failed save price', err)
    ElMessage.error('Не удалось сохранить стоимость')
    syncFromOrder()
  } finally {
    isSavingPrice.value = false
  }
}

const openAddPayment = () => {
  showAddPayment.value = true
}

const closeAddPayment = () => {
  showAddPayment.value = false
  newPaymentAmount.value = ''
}

const addPayment = async () => {
  if (!canAddPayment.value || isSavingPayment.value) {
    return
  }

  isSavingPayment.value = true

  try {
    await http.post('/api/payment-parts/', {
      art_id: props.order.id,
      amount_usd: Number(newPaymentAmount.value || 0),
      currency: 'usd',
      received_via: paymentFlow.value,
      status: 'received',
    })

    closeAddPayment()

    ElMessage.success('Оплата добавлена')
    emit('updated')
  } catch (err) {
    console.error('failed add payment', err)
    ElMessage.error('Не удалось добавить оплату')
  } finally {
    isSavingPayment.value = false
  }
}
</script>

<template>
  <article
      class="accounting-order-card"
      :class="{ 'accounting-order-card--payment-open': showAddPayment }"
  >
    <!-- Верх карточки: название заказа и полная стоимость справа -->
    <div class="order-head">
      <div>
        <div class="order-name">{{ order.name }}</div>
        <div class="order-meta">ID {{ order.id }} · {{ order.status }}</div>
      </div>

      <div class="order-total">
        ${{ totalAmount }}
      </div>
    </div>

    <!-- Три основные денежные точки заказа -->
    <div class="money-row">
      <label class="money-field">
        <span>Полная стоимость</span>

        <el-input-number
            v-model="totalAmount"
            class="money-input"
            :min="paidTotalAmount"
            :controls="false"
            size="small"
            @change="savePrice"
        />
      </label>

      <label
          v-if="paymentFlow === 'broker'"
          class="money-field"
      >
        <span>Уже выведено</span>

        <el-input-number
            v-model="withdrawnAmount"
            :controls="false"
            size="small"
            disabled
        />
      </label>

      <div class="money-field broker-field">
        <el-dropdown
            trigger="click"
            @command="setPaymentFlow"
        >
          <button
              class="payment-flow-label"
              type="button"
          >
            {{ currentFlowLabel }}
          </button>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="broker">
                Через посредника
              </el-dropdown-item>

              <el-dropdown-item command="direct">
                Напрямую
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <div class="broker-input-wrap">
          <el-input-number
              :model-value="currentReceivedAmount"
              :controls="false"
              size="small"
              disabled
          />

          <el-button
              v-if="!showAddPayment"
              class="broker-action-button"
              circle
              plain
              size="small"
              @click="openAddPayment"
          >
            +
          </el-button>

          <div
              v-if="showAddPayment"
              class="add-payment-popover"
          >
            <el-input
                v-model="newPaymentAmount"
                class="add-payment-input"
                placeholder=" Новый перевод"
                size="small"
            >
              <template #prefix>$ </template>
            </el-input>

            <el-button
                class="add-payment-confirm"
                :class="{ 'add-payment-confirm--active': canAddPayment }"
                circle
                plain
                size="small"
                :loading="isSavingPayment"
                :disabled="!canAddPayment"
                @click="addPayment"
            >
              ✓
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Прогресс оплаты заказа -->
    <div class="progress-block">
      <div class="progress-label">
        <span>Оплачено: ${{ paidTotalAmount }} из ${{ totalAmount }}</span>
      </div>

      <el-progress
          :percentage="paidPercent"
          :stroke-width="10"
          :show-text="false"
      />
    </div>
  </article>
</template>

<style scoped>
.accounting-order-card {
  width: min(720px, 100%);
  padding: 18px 20px;
  border-radius: 18px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
}

.order-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.order-name {
  font-size: 17px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.order-meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.order-total {
  font-size: 22px;
  font-weight: 800;
  color: var(--el-color-primary);
  white-space: nowrap;
}

.money-row {
  display: grid;
  grid-template-columns: repeat(3, max-content);
  gap: 90px;
  align-items: end;
  justify-content: start;
}

.money-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  width: 140px;
}

.money-field span {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.money-field :deep(.el-input-number) {
  width: 140px;
}

.broker-input-wrap {
  position: relative;
  width: 140px;
}

.broker-action-button {
  position: absolute;
  z-index: 4;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);

  width: 24px;
  height: 24px;

  opacity: 0.58;
  pointer-events: auto;

  color: var(--el-text-color-secondary);
  border-color: var(--el-border-color-lighter);
  background: var(--el-fill-color-blank);

  transition:
      opacity 0.15s ease,
      color 0.15s ease,
      border-color 0.15s ease,
      background 0.15s ease;
}

.broker-action-button:hover {
  opacity: 1;
  color: var(--el-color-primary);
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
}

.add-payment-popover {
  position: absolute;
  z-index: 5;

  top: calc(100% + 6px);
  left: 0;

  display: grid;
  grid-template-columns: 140px 24px;
  gap: 8px;
  align-items: center;
}

.add-payment-input {
  width: 140px;
}

.add-payment-confirm {
  width: 24px;
  height: 24px;

  color: var(--el-text-color-placeholder);
  border-color: var(--el-border-color-lighter);
  background: var(--el-fill-color-lighter);
}

.add-payment-confirm--active {
  color: var(--el-color-success);
  border-color: var(--el-color-success-light-5);
  background: var(--el-color-success-light-9);
}

.add-payment-confirm--active:hover {
  color: white;
  border-color: var(--el-color-success);
  background: var(--el-color-success);
}

.progress-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-label {
  display: flex;
  justify-content: flex-start;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.payment-flow-label {
  width: fit-content;
  padding: 0;
  border: none;
  border-bottom: 1px dashed var(--el-text-color-secondary);
  background: transparent;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  line-height: 1.2;
  cursor: pointer;
}

.payment-flow-label:hover {
  color: var(--el-color-primary);
  border-bottom-color: var(--el-color-primary);
}

@media (max-width: 620px) {
  .money-row {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .money-field,
  .broker-input-wrap,
  .money-field :deep(.el-input-number),
  .add-payment-input {
    width: 140px;
  }
}
</style>