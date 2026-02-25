<template>
  <div class="stock-kline">
    <div :id="chartId" class="kline-chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  chartId: { type: String, required: true },
  data: { type: Array, default: () => [] },
  period: { type: String, default: 'daily' }
})

let chart = null

const initChart = () => {
  if (chart) {
    chart.dispose()
  }

  chart = echarts.init(document.getElementById(props.chartId))
  renderChart()
}

const renderChart = () => {
  if (!props.data || props.data.length === 0) return

  const dates = props.data.map(d => d.trade_date)
  const klineData = props.data.map(d => [
    parseFloat(d.open_price),
    parseFloat(d.close_price),
    parseFloat(d.low_price),
    parseFloat(d.high_price)
  ])
  const volumes = props.data.map((d, i) => [
    i,
    parseFloat(d.volume),
    d.close_price >= d.open_price ? 1 : -1
  ])
  const ma1 = props.data.map(d => d.ma_1 ? parseFloat(d.ma_1) : null)
  const ma2 = props.data.map(d => d.ma_2 ? parseFloat(d.ma_2) : null)
  const ma3 = props.data.map(d => d.ma_3 ? parseFloat(d.ma_3) : null)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['K线', 'MA5', 'MA10', 'MA20', '成交量'],
      top: 10
    },
    grid: [
      { left: '10%', right: '8%', height: '55%', top: 80 },
      { left: '10%', right: '8%', top: '68%', height: '15%' }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        gridIndex: 0,
        axisLabel: { show: false }
      },
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        gridIndex: 1,
        axisLabel: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        gridIndex: 0,
        splitLine: { show: true, lineStyle: { color: '#e0e0e0' } }
      },
      {
        scale: true,
        gridIndex: 1,
        splitLine: { show: false },
        axisLabel: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 70,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        bottom: 10,
        start: 70,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData,
        itemStyle: {
          color: '#ef232a',
          color0: '#14b143',
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma1,
        smooth: true,
        lineStyle: { opacity: 0.8, width: 1 },
        showSymbol: false
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma2,
        smooth: true,
        lineStyle: { opacity: 0.8, width: 1 },
        showSymbol: false
      },
      {
        name: 'MA20',
        type: 'line',
        data: ma3,
        smooth: true,
        lineStyle: { opacity: 0.8, width: 1 },
        showSymbol: false
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: (params) => params.data[2] > 0 ? '#ef232a' : '#14b143'
        }
      }
    ]
  }

  chart.setOption(option)
}

watch(() => props.data, () => {
  renderChart()
}, { deep: true })

watch(() => props.period, () => {
  renderChart()
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', () => chart?.resize())
})
</script>

<style scoped>
.kline-chart {
  width: 100%;
  height: 600px;
}
</style>
