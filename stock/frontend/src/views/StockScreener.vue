<template>
  <div class="stock-screener">
    <h1>股票曲线选股</h1>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <label>
        日期范围:
        <input type="date" v-model="startDate" @change="loadStocks" />
        <span>至</span>
        <input type="date" v-model="endDate" @change="loadStocks" />
      </label>
      <label>
        涨跌幅:
        <input type="number" v-model.number="minChange" placeholder="最小%" @change="loadStocks" />
        <span>-</span>
        <input type="number" v-model.number="maxChange" placeholder="最大%" @change="loadStocks" />
      </label>
      <button @click="loadStocks">筛选</button>
    </div>

    <!-- 股票网格 -->
    <div class="stock-grid" v-if="stocks.length > 0">
      <div
        v-for="stock in stocks"
        :key="stock.ticker"
        class="stock-card"
        @click="viewStockDetail(stock.ticker)"
      >
        <div class="stock-header">
          <span class="ticker">{{ stock.ticker }}</span>
          <span :class="['change', stock.change_percent >= 0 ? 'up' : 'down']">
            {{ stock.change_percent.toFixed(2) }}%
          </span>
        </div>
        <div :id="'chart-' + stock.ticker" class="mini-chart"></div>
      </div>
    </div>

    <div v-else class="empty">
      <p>暂无数据</p>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
      >上一页</button>
      <span>{{ currentPage }} / {{ Math.ceil(total / pageSize) }}</span>
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage >= Math.ceil(total / pageSize)"
      >下一页</button>
      <span>共 {{ total }} 只股票</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '../api/stock'

const startDate = ref('')
const endDate = ref('')
const minChange = ref(null)
const maxChange = ref(null)
const stocks = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 初始化日期范围
const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)

  endDate.value = end.toISOString().split('T')[0]
  startDate.value = start.toISOString().split('T')[0]
}

const loadStocks = async () => {
  try {
    const { data } = await stockAPI.screener({
      start_date: startDate.value,
      end_date: endDate.value,
      min_change: minChange.value,
      max_change: maxChange.value,
      page: currentPage.value,
      page_size: pageSize.value
    })

    stocks.value = data.stocks
    total.value = data.total

    await nextTick()
    renderMiniCharts()
  } catch (error) {
    console.error('加载股票数据失败:', error)
  }
}

const renderMiniCharts = () => {
  stocks.value.forEach(stock => {
    const chartDom = document.getElementById('chart-' + stock.ticker)
    if (!chartDom) return

    const chart = echarts.init(chartDom)

    // 获取该股票的详细数据
    stockAPI.getDetail(stock.ticker, {
      start_date: startDate.value,
      end_date: endDate.value
    }).then(res => {
      const data = res.data.data
      const dates = data.map(d => d.date)
      const prices = data.map(d => d.price)

      chart.setOption({
        grid: { top: 10, bottom: 10, left: 10, right: 10 },
        xAxis: { type: 'category', data: dates, show: false },
        yAxis: { type: 'value', show: false },
        series: [{
          type: 'line',
          data: prices,
          smooth: true,
          symbol: 'none',
          lineStyle: {
            width: 1.5,
            color: stock.change_percent >= 0 ? '#ef232a' : '#14b143'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0, y: 0, x2: 0, y2: 1,
              colorStops: stock.change_percent >= 0
                ? [{ offset: 0, color: 'rgba(239, 35, 42, 0.3)' }, { offset: 1, color: 'rgba(239, 35, 42, 0)' }]
                : [{ offset: 0, color: 'rgba(20, 177, 67, 0.3)' }, { offset: 1, color: 'rgba(20, 177, 67, 0)' }]
            }
          }
        }]
      })
    })
  })
}

const changePage = (page) => {
  currentPage.value = page
  loadStocks()
}

const viewStockDetail = (ticker) => {
  currentView.value = 'detail'
  selectedTicker.value = ticker
}

onMounted(() => {
  initDateRange()
  loadStocks()
})

// 导出事件供父组件使用
const emit = defineEmits(['view-detail'])
</script>

<style scoped>
.stock-screener {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
  color: #333;
}

.filter-bar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-bar label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-bar input[type="date"],
.filter-bar input[type="number"] {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filter-bar button {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.filter-bar button:hover {
  background: #66b1ff;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.stock-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stock-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.ticker {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.change {
  font-size: 14px;
  font-weight: bold;
}

.change.up {
  color: #ef232a;
}

.change.down {
  color: #14b143;
}

.mini-chart {
  width: 100%;
  height: 80px;
}

.empty {
  text-align: center;
  padding: 60px;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination button:not(:disabled):hover {
  background: #f5f5f5;
}
</style>
