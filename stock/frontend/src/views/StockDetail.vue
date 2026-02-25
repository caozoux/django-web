<template>
  <div class="stock-detail">
    <div class="detail-header">
      <h1>{{ ticker }} - 股票详情</h1>
      <div class="controls">
        <div class="period-selector">
          <button
            :class="{ active: period === 'daily' }"
            @click="changePeriod('daily')"
          >日线</button>
          <button
            :class="{ active: period === 'weekly' }"
            @click="changePeriod('weekly')"
          >周线</button>
          <button
            :class="{ active: period === 'monthly' }"
            @click="changePeriod('monthly')"
          >月线</button>
        </div>
        <button class="back-btn" @click="$emit('back')">返回</button>
      </div>
    </div>

    <div class="kline-container">
      <StockKLine
        :chart-id="'main-kline'"
        :data="klineData"
        :period="period"
      />
    </div>

    <!-- 股票基本信息 -->
    <div class="stock-info" v-if="klineData.length > 0">
      <div class="info-item">
        <span class="label">最新价:</span>
        <span class="value">{{ latestClose }}</span>
      </div>
      <div class="info-item">
        <span class="label">涨跌幅:</span>
        <span :class="['value', changePercent >= 0 ? 'up' : 'down']">
          {{ changePercent > 0 ? '+' : '' }}{{ changePercent }}%
        </span>
      </div>
      <div class="info-item">
        <span class="label">成交量:</span>
        <span class="value">{{ latestVolume }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import StockKLine from '../components/StockKLine.vue'
import { stockAPI } from '../api/stock'

const props = defineProps({
  ticker: { type: String, required: true }
})

defineEmits(['back'])

const period = ref('daily')
const klineData = ref([])

const latestClose = computed(() => {
  if (klineData.value.length === 0) return '-'
  return klineData.value[klineData.value.length - 1].close_price.toFixed(2)
})

const changePercent = computed(() => {
  if (klineData.value.length < 2) return 0
  const prev = klineData.value[klineData.value.length - 2].close_price
  const curr = klineData.value[klineData.value.length - 1].close_price
  return ((curr - prev) / prev * 100).toFixed(2)
})

const latestVolume = computed(() => {
  if (klineData.value.length === 0) return '-'
  const vol = klineData.value[klineData.value.length - 1].volume
  if (vol >= 100000000) return (vol / 100000000).toFixed(2) + '亿'
  if (vol >= 10000) return (vol / 10000).toFixed(2) + '万'
  return vol.toFixed(2)
})

const loadKLineData = async () => {
  try {
    const { data } = await stockAPI.getKLine(props.ticker, {
      period: period.value,
      start_date: getStartDate(),
      end_date: new Date().toISOString().split('T')[0]
    })
    klineData.value = data.data
  } catch (error) {
    console.error('加载K线数据失败:', error)
  }
}

const getStartDate = () => {
  const start = new Date()
  if (period.value === 'daily') {
    start.setDate(start.getDate() - 365)
  } else if (period.value === 'weekly') {
    start.setFullYear(start.getFullYear() - 3)
  } else {
    start.setFullYear(start.getFullYear() - 5)
  }
  return start.toISOString().split('T')[0]
}

const changePeriod = (newPeriod) => {
  period.value = newPeriod
  loadKLineData()
}

onMounted(() => {
  loadKLineData()
})

watch(() => props.ticker, () => {
  loadKLineData()
})
</script>

<style scoped>
.stock-detail {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-header h1 {
  color: #333;
  margin: 0;
}

.controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.period-selector {
  display: flex;
  gap: 4px;
}

.period-selector button {
  padding: 8px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.period-selector button.active {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

.back-btn {
  padding: 8px 16px;
  background: #909399;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.back-btn:hover {
  background: #a6a9ad;
}

.kline-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stock-info {
  display: flex;
  gap: 32px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.info-item .label {
  color: #666;
  font-size: 14px;
}

.info-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.info-item .value.up {
  color: #ef232a;
}

.info-item .value.down {
  color: #14b143;
}
</style>
