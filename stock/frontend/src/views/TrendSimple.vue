<template>
  <div class="simple-page">
    <h1>简单测试页面</h1>

    <!-- 筛选器 -->
    <div class="filter-section">
      <input type="date" v-model="startDate" />
      <input type="date" v-model="endDate" />
      <button @click="fetchData">查询</button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">累计上涨: {{ totalUp }}</div>
      <div class="stat-card">累计下跌: {{ totalDown }}</div>
      <div class="stat-card">累计平盘: {{ totalFlat }}</div>
      <div class="stat-card">交易日数: {{ dayCount }}</div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-container">图表1</div>
      <div class="chart-container">图表2</div>
      <div class="chart-container">图表3</div>
    </div>

    <!-- 数据表格 -->
    <table class="data-table">
      <thead>
        <tr>
          <th>日期</th>
          <th>上涨</th>
          <th>下跌</th>
          <th>平盘</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in tableData" :key="item.trade_date">
          <td>{{ item.trade_date }}</td>
          <td>{{ item.up_count }}</td>
          <td>{{ item.down_count }}</td>
          <td>{{ item.flat_count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { stockAPI } from '../api/stock'

const startDate = ref('')
const endDate = ref('')
const totalUp = ref(0)
const totalDown = ref(0)
const totalFlat = ref(0)
const dayCount = ref(0)
const tableData = ref([])

const fetchData = async () => {
  try {
    const { data } = await stockAPI.dailySummary({
      start_date: startDate.value,
      end_date: endDate.value
    })
    const d = data.data || []
    tableData.value = d
    totalUp.value = d.reduce((sum, item) => sum + item.up_count, 0)
    totalDown.value = d.reduce((sum, item) => sum + item.down_count, 0)
    totalFlat.value = d.reduce((sum, item) => sum + item.flat_count, 0)
    dayCount.value = d.length
  } catch (error) {
    console.error('Error:', error)
  }
}

// 初始化日期
const initDates = () => {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  endDate.value = end.toISOString().split('T')[0]
  startDate.value = start.toISOString().split('T')[0]
}

initDates()
fetchData()
</script>

