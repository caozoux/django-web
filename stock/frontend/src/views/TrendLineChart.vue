<template>
  <div class="trend-analysis-page">
    <div class="page-header">
      <h1 class="page-title">📉 涨跌个数趋势分析</h1>
      <p class="page-subtitle">分析市场涨跌变化趋势，掌握市场情绪走向</p>
    </div>

    <!-- 筛选控制栏 -->
    <form class="filter-section" @submit.prevent>
      <div class="filter-group">
        <label for="startDate" class="filter-label">起始日期</label>
        <input
          type="date"
          id="startDate"
          name="startDate"
          class="date-input"
          v-model="startDate"
          @change="handleDateChange"
        />
      </div>
      <div class="filter-group">
        <label for="endDate" class="filter-label">结束日期</label>
        <input
          type="date"
          id="endDate"
          name="endDate"
          class="date-input"
          v-model="endDate"
          @change="handleDateChange"
        />
      </div>
      <div class="filter-group">
        <span class="filter-label">快捷选择</span>
        <div class="quick-filters">
          <button
            v-for="days in quickDays"
            :key="days.value"
            type="button"
            class="quick-btn"
            :class="{ active: selectedQuickDays === days.value }"
            @click="selectQuickDays(days.value)"
          >
            {{ days.label }}
          </button>
        </div>
      </div>
      <button type="submit" class="query-btn" @click="fetchData" :disabled="isLoading">
        <span v-if="!isLoading">🔍 查询数据</span>
        <span v-else>⏳ 加载中...</span>
      </button>
    </form>

    <!-- 统计概览 -->
    <div class="stats-overview" v-if="statistics">
      <div class="stat-box stat-box-up">
        <div class="stat-icon">📈</div>
        <div class="stat-info">
          <div class="stat-name">累计上涨</div>
          <div class="stat-value">{{ statistics.totalUp }}</div>
          <div class="stat-percent">平均 {{ statistics.avgUp.toFixed(0) }}/天</div>
        </div>
      </div>
      <div class="stat-box stat-box-down">
        <div class="stat-icon">📉</div>
        <div class="stat-info">
          <div class="stat-name">累计下跌</div>
          <div class="stat-value">{{ statistics.totalDown }}</div>
          <div class="stat-percent">平均 {{ statistics.avgDown.toFixed(0) }}/天</div>
        </div>
      </div>
      <div class="stat-box stat-box-flat">
        <div class="stat-icon">➡️</div>
        <div class="stat-info">
          <div class="stat-name">累计平盘</div>
          <div class="stat-value">{{ statistics.totalFlat }}</div>
          <div class="stat-percent">平均 {{ statistics.avgFlat.toFixed(0) }}/天</div>
        </div>
      </div>
      <div class="stat-box stat-box-total">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-name">交易日数</div>
          <div class="stat-value">{{ statistics.totalDays }}</div>
          <div class="stat-percent">总交易天数</div>
        </div>
      </div>
    </div>

    <!-- 趋势图表区域 -->
    <div class="charts-section">
      <!-- 涨跌个数趋势图 -->
      <div class="chart-wrapper">
        <div class="chart-header">
          <h2 class="chart-title">📈 涨跌个数趋势</h2>
          <div class="chart-actions">
            <button class="action-btn" @click="toggleChartType('line')">
              <span :class="{ active: chartType === 'line' }">📉 折线</span>
            </button>
            <button class="action-btn" @click="toggleChartType('bar')">
              <span :class="{ active: chartType === 'bar' }">📊 柱状</span>
            </button>
          </div>
        </div>
        <div class="chart-canvas" id="trendChartCanvas"></div>
      </div>

      <!-- 涨跌占比分析 -->
      <div class="chart-wrapper">
        <div class="chart-header">
          <h2 class="chart-title">📊 涨跌占比分析</h2>
          <div class="chart-legend">
            <span class="legend-item legend-up">● 上涨</span>
            <span class="legend-item legend-down">● 下跌</span>
            <span class="legend-item legend-flat">● 平盘</span>
          </div>
        </div>
        <div class="chart-canvas" id="ratioChartCanvas"></div>
      </div>

      <!-- 市场情绪指数 -->
      <div class="chart-wrapper">
        <div class="chart-header">
          <h2 class="chart-title">🌡️ 市场情绪指数</h2>
          <p class="chart-desc">（上涨-下跌）/总数，正值偏多，负值偏空</p>
        </div>
        <div class="chart-canvas" id="sentimentChartCanvas"></div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '../api/stock'

const startDate = ref('')
const endDate = ref('')
const isLoading = ref(false)
const dailyData = ref([])
const chartType = ref('line')
const selectedQuickDays = ref(30)

const quickDays = [
  { label: '30天', value: 30 },
  { label: '60天', value: 60 },
  { label: '90天', value: 90 },
  { label: '180天', value: 180 },
  { label: '365天', value: 365 }
]

let trendChart = null
let ratioChart = null
let sentimentChart = null

const statistics = computed(() => {
  if (dailyData.value.length === 0) return null

  const totalUp = dailyData.value.reduce((sum, d) => sum + d.up_count, 0)
  const totalDown = dailyData.value.reduce((sum, d) => sum + d.down_count, 0)
  const totalFlat = dailyData.value.reduce((sum, d) => sum + d.flat_count, 0)

  const tableData = dailyData.value.map(d => {
    const total = d.total_count || 1
    const sentiment = ((d.up_count - d.down_count) / total).toFixed(3)
    let sentimentText = '中性'
    if (sentiment > 0.1) sentimentText = '偏多'
    else if (sentiment < -0.1) sentimentText = '偏空'

    return {
      trade_date: d.trade_date,
      up_count: d.up_count,
      down_count: d.down_count,
      flat_count: d.flat_count,
      total_count: d.total_count,
      upRatio: total > 0 ? ((d.up_count / total) * 100).toFixed(1) : '0',
      downRatio: total > 0 ? ((d.down_count / total) * 100).toFixed(1) : '0',
      sentiment: parseFloat(sentiment),
      sentimentText
    }
  })

  return {
    totalUp,
    totalDown,
    totalFlat,
    totalDays: dailyData.value.length,
    avgUp: totalUp / dailyData.value.length,
    avgDown: totalDown / dailyData.value.length,
    avgFlat: totalFlat / dailyData.value.length,
    tableData
  }
})

const initDateRange = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  endDate.value = end.toISOString().split('T')[0]
  startDate.value = start.toISOString().split('T')[0]
}

const selectQuickDays = (days) => {
  selectedQuickDays.value = days
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days)
  endDate.value = end.toISOString().split('T')[0]
  startDate.value = start.toISOString().split('T')[0]
  fetchData()
}

const handleDateChange = () => {
  selectedQuickDays.value = null
}

const fetchData = async () => {
  if (!startDate.value || !endDate.value) {
    alert('请选择日期范围')
    return
  }

  isLoading.value = true
  try {
    const { data } = await stockAPI.dailySummary({
      start_date: startDate.value,
      end_date: endDate.value
    })
    dailyData.value = data.data
    // 等待DOM更新后再渲染图表
    await nextTick()
    renderAllCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
    alert('加载数据失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const toggleChartType = (type) => {
  chartType.value = type
  renderTrendChart()
}

const exportData = () => {
  if (!statistics.value) return
  const csv = [
    ['日期', '上涨', '下跌', '平盘', '总数', '涨比(%)', '跌比(%)', '情绪'],
    ...statistics.value.tableData.map(d => [
      d.trade_date,
      d.up_count,
      d.down_count,
      d.flat_count,
      d.total_count,
      d.upRatio,
      d.downRatio,
      d.sentimentText
    ])
  ].map(row => row.join(',')).join('\n')

  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `涨跌趋势_${startDate.value}_${endDate.value}.csv`
  link.click()
}

const renderTrendChart = () => {
  try {
    console.log('Rendering trend chart...')
    if (trendChart) {
      trendChart.dispose()
    }

    const canvasEl = document.getElementById('trendChartCanvas')
    if (!canvasEl) {
      console.error('trendChartCanvas element not found!')
      return
    }

    trendChart = echarts.init(canvasEl)
    const dates = dailyData.value.map(d => d.trade_date)
    console.log('Trend chart data points:', dates.length)

    const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['上涨', '下跌', '平盘'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45, interval: Math.ceil(dates.length / 20) },
      boundaryGap: chartType.value === 'bar'
    },
    yAxis: {
      type: 'value',
      name: '个数'
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { show: true, type: 'slider', bottom: 10, start: 0, end: 100 }
    ],
    series: [
      {
        name: '上涨',
        type: chartType.value,
        data: dailyData.value.map(d => d.up_count),
        smooth: chartType.value === 'line',
        itemStyle: { color: '#ef232a' },
        areaStyle: chartType.value === 'line' ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(239, 35, 42, 0.3)' },
              { offset: 1, color: 'rgba(239, 35, 42, 0.05)' }
            ]
          }
        } : null
      },
      {
        name: '下跌',
        type: chartType.value,
        data: dailyData.value.map(d => d.down_count),
        smooth: chartType.value === 'line',
        itemStyle: { color: '#14b143' },
        areaStyle: chartType.value === 'line' ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(20, 177, 67, 0.3)' },
              { offset: 1, color: 'rgba(20, 177, 67, 0.05)' }
            ]
          }
        } : null
      },
      {
        name: '平盘',
        type: chartType.value,
        data: dailyData.value.map(d => d.flat_count),
        smooth: chartType.value === 'line',
        itemStyle: { color: '#909399' },
        areaStyle: chartType.value === 'line' ? {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(144, 147, 153, 0.3)' },
              { offset: 1, color: 'rgba(144, 147, 153, 0.05)' }
            ]
          }
        } : null
      }
    ]
  }

  trendChart.setOption(option)
  console.log('Trend chart rendered successfully')
  } catch (error) {
    console.error('Error rendering trend chart:', error)
  }
}

const renderRatioChart = () => {
  if (ratioChart) {
    ratioChart.dispose()
  }

  ratioChart = echarts.init(document.getElementById('ratioChartCanvas'))
  const dates = dailyData.value.map(d => d.trade_date)

  const upRatio = dailyData.value.map(d => {
    const total = d.total_count || 1
    return ((d.up_count / total) * 100).toFixed(2)
  })
  const downRatio = dailyData.value.map(d => {
    const total = d.total_count || 1
    return ((d.down_count / total) * 100).toFixed(2)
  })
  const flatRatio = dailyData.value.map(d => {
    const total = d.total_count || 1
    return ((d.flat_count / total) * 100).toFixed(2)
  })

  ratioChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: params => {
        let result = params[0].axisValue + '<br/>'
        params.forEach(p => {
          result += `${p.marker} ${p.seriesName}: ${p.value}%<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['上涨占比', '下跌占比', '平盘占比'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45, interval: Math.ceil(dates.length / 20) }
    },
    yAxis: {
      type: 'value',
      name: '占比 (%)',
      max: 100
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { show: true, type: 'slider', bottom: 10, start: 0, end: 100 }
    ],
    series: [
      {
        name: '上涨占比',
        type: 'line',
        data: upRatio,
        smooth: true,
        lineStyle: { width: 2.5, color: '#ef232a' },
        itemStyle: { color: '#ef232a' }
      },
      {
        name: '下跌占比',
        type: 'line',
        data: downRatio,
        smooth: true,
        lineStyle: { width: 2.5, color: '#14b143' },
        itemStyle: { color: '#14b143' }
      },
      {
        name: '平盘占比',
        type: 'line',
        data: flatRatio,
        smooth: true,
        lineStyle: { width: 2.5, color: '#909399' },
        itemStyle: { color: '#909399' }
      }
    ]
  })
}

const renderSentimentChart = () => {
  if (sentimentChart) {
    sentimentChart.dispose()
  }

  sentimentChart = echarts.init(document.getElementById('sentimentChartCanvas'))
  const dates = dailyData.value.map(d => d.trade_date)
  const sentimentData = dailyData.value.map(d => {
    const total = d.total_count || 1
    return ((d.up_count - d.down_count) / total).toFixed(3)
  })

  sentimentChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: params => {
        const val = params[0].value
        const label = val > 0 ? '偏多' : (val < 0 ? '偏空' : '中性')
        return `${params[0].axisValue}<br/>情绪指数: ${val}<br/>市场: ${label}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45, interval: Math.ceil(dates.length / 20) }
    },
    yAxis: {
      type: 'value',
      name: '情绪指数'
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { show: true, type: 'slider', bottom: 10, start: 0, end: 100 }
    ],
    series: [
      {
        type: 'line',
        data: sentimentData,
        smooth: true,
        lineStyle: {
          width: 2.5,
          color: function(params) {
            const val = parseFloat(params[1])
            if (val > 0.1) return '#ef232a'
            if (val < -0.1) return '#14b143'
            return '#909399'
          }
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(239, 35, 42, 0.2)' },
              { offset: 0.5, color: 'rgba(144, 147, 153, 0.1)' },
              { offset: 1, color: 'rgba(20, 177, 67, 0.2)' }
            ]
          }
        },
        markLine: {
          symbol: 'none',
          data: [
            { yAxis: 0, label: '中性线', lineStyle: { color: '#909399', type: 'dashed', width: 2 } }
          ]
        },
        markPoint: {
          data: [
            { type: 'max', name: '最乐观', itemStyle: { color: '#ef232a' } },
            { type: 'min', name: '最悲观', itemStyle: { color: '#14b143' } }
          ]
        }
      }
    ]
  })
}

const renderAllCharts = () => {
  console.log('Rendering all charts, dailyData length:', dailyData.value.length)

  const trendEl = document.getElementById('trendChartCanvas')
  const ratioEl = document.getElementById('ratioChartCanvas')
  const sentimentEl = document.getElementById('sentimentChartCanvas')

  console.log('Chart elements exist:', {
    trendEl: !!trendEl,
    ratioEl: !!ratioEl,
    sentimentEl: !!sentimentEl
  })

  if (trendEl) renderTrendChart()
  else console.error('trendChartCanvas element not found')

  if (ratioEl) renderRatioChart()
  else console.error('ratioChartCanvas element not found')

  if (sentimentEl) renderSentimentChart()
  else console.error('sentimentChartCanvas element not found')
}

onMounted(async () => {
  console.log('TrendLineChart component mounted')
  console.log('Component element:', document.querySelector('.trend-analysis-page'))

  // 等待DOM完全渲染
  await nextTick()
  console.log('After nextTick, chart elements:', {
    trendChartCanvas: document.getElementById('trendChartCanvas'),
    ratioChartCanvas: document.getElementById('ratioChartCanvas'),
    sentimentChartCanvas: document.getElementById('sentimentChartCanvas')
  })

  initDateRange()
  await fetchData()

  window.addEventListener('resize', () => {
    trendChart?.resize()
    ratioChart?.resize()
    sentimentChart?.resize()
  })
})
</script>

