<template>
  <div class="daily-stats">
    <!-- 日期选择 -->
    <div class="date-picker">
      <label>
        日期范围:
        <input type="date" id="startDate" name="startDate" v-model="startDate" @change="loadStats" />
        <span>至</span>
        <input type="date" id="endDate" name="endDate" v-model="endDate" @change="loadStats" />
      </label>
      <button @click="loadStats">查询</button>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-cards" v-if="dailyStats.length > 0">
      <div class="stat-card">
        <div class="stat-label">上涨</div>
        <div class="stat-value up">{{ latestStats.up_count }}</div>
        <div class="stat-desc">{{ latestStats.avg_up_percent?.toFixed(2) }}%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">下跌</div>
        <div class="stat-value down">{{ latestStats.down_count }}</div>
        <div class="stat-desc">{{ latestStats.avg_down_percent?.toFixed(2) }}%</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">平盘</div>
        <div class="stat-value">{{ latestStats.flat_count }}</div>
        <div class="stat-desc">-</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">总股票数</div>
        <div class="stat-value">{{ latestStats.total_count }}</div>
        <div class="stat-desc">-</div>
      </div>
    </div>

    <!-- 涨跌趋势图 -->
    <div class="chart-container">
      <h3>涨跌趋势</h3>
      <div id="trendChart"></div>
    </div>

    <!-- 涨跌个数线性图 -->
    <div class="chart-container">
      <h3>涨跌个数趋势</h3>
      <div id="lineChart"></div>
    </div>

    <!-- 涨跌分布饼图 -->
    <div class="chart-container">
      <h3>涨跌分布</h3>
      <div id="pieChart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '../api/stock'

const startDate = ref('')
const endDate = ref('')
const dailyStats = ref([])
const latestStats = ref({})

let trendChart = null
let lineChart = null
let pieChart = null

const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)

  endDate.value = end.toISOString().split('T')[0]
  startDate.value = start.toISOString().split('T')[0]
}

const loadStats = async () => {
  try {
    const { data } = await stockAPI.dailySummary({
      start_date: startDate.value,
      end_date: endDate.value
    })

    dailyStats.value = data.data
    latestStats.value = data.data[data.data.length - 1]

    renderTrendChart()
    renderLineChart()
    renderPieChart()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const renderTrendChart = () => {
  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(document.getElementById('trendChart'))

  const dates = dailyStats.value.map(d => d.trade_date)

  trendChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['上涨', '下跌', '平盘'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    dataZoom: [
      { type: 'inside', start: 50, end: 100 },
      { show: true, type: 'slider', bottom: 10, start: 50, end: 100 }
    ],
    series: [
      {
        name: '上涨',
        type: 'bar',
        data: dailyStats.value.map(d => d.up_count),
        itemStyle: { color: '#ef232a' }
      },
      {
        name: '下跌',
        type: 'bar',
        data: dailyStats.value.map(d => d.down_count),
        itemStyle: { color: '#14b143' }
      },
      {
        name: '平盘',
        type: 'bar',
        data: dailyStats.value.map(d => d.flat_count),
        itemStyle: { color: '#909399' }
      }
    ]
  })
}

const renderLineChart = () => {
  if (lineChart) {
    lineChart.dispose()
  }

  lineChart = echarts.init(document.getElementById('lineChart'))

  const dates = dailyStats.value.map(d => d.trade_date)

  lineChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['上涨个数', '下跌个数', '平盘个数'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      },
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '个数'
    },
    dataZoom: [
      { type: 'inside', start: 50, end: 100 },
      { show: true, type: 'slider', bottom: 10, start: 50, end: 100 }
    ],
    series: [
      {
        name: '上涨个数',
        type: 'line',
        data: dailyStats.value.map(d => d.up_count),
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#ef232a'
        },
        itemStyle: {
          color: '#ef232a'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(239, 35, 42, 0.3)' },
            { offset: 1, color: 'rgba(239, 35, 42, 0.05)' }
          ])
        }
      },
      {
        name: '下跌个数',
        type: 'line',
        data: dailyStats.value.map(d => d.down_count),
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#14b143'
        },
        itemStyle: {
          color: '#14b143'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(20, 177, 67, 0.3)' },
            { offset: 1, color: 'rgba(20, 177, 67, 0.05)' }
          ])
        }
      },
      {
        name: '平盘个数',
        type: 'line',
        data: dailyStats.value.map(d => d.flat_count),
        smooth: true,
        lineStyle: {
          width: 3,
          color: '#909399'
        },
        itemStyle: {
          color: '#909399'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(144, 147, 153, 0.3)' },
            { offset: 1, color: 'rgba(144, 147, 153, 0.05)' }
          ])
        }
      }
    ]
  })
}

const renderPieChart = () => {
  if (pieChart) {
    pieChart.dispose()
  }

  pieChart = echarts.init(document.getElementById('pieChart'))

  pieChart.setOption({
    title: {
      text: `${latestStats.value.trade_date || ''}`,
      left: 'center',
      top: 20
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      data: [
        { value: latestStats.value.up_count, name: '上涨', itemStyle: { color: '#ef232a' } },
        { value: latestStats.value.down_count, name: '下跌', itemStyle: { color: '#14b143' } },
        { value: latestStats.value.flat_count, name: '平盘', itemStyle: { color: '#909399' } }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

onMounted(() => {
  initDateRange()
  loadStats()

  window.addEventListener('resize', () => {
    trendChart?.resize()
    lineChart?.resize()
    pieChart?.resize()
  })
})
</script>

<style scoped>
.daily-stats {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
  color: #333;
}

.date-picker {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
}

.date-picker label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-picker input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.date-picker button {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.date-picker button:hover {
  background: #66b1ff;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-label {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-value.up {
  color: #ef232a;
}

.stat-value.down {
  color: #14b143;
}

.stat-desc {
  color: #999;
  font-size: 12px;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-container h3 {
  margin-bottom: 16px;
  color: #333;
}

#trendChart, #lineChart, #pieChart {
  width: 100%;
  height: 400px;
}
</style>
