<template>
    <!-- 导航栏 - 仅在非趋势页面显示 -->
    <nav class="navbar" v-if="currentView !== 'trend'">
      <div class="nav-container">
        <h1 class="nav-title">股票量化交易可视化系统</h1>
        <div class="nav-links">
          <a
            :class="{ active: currentView === 'screener' }"
            @click="currentView = 'screener'"
          >曲线选股</a>
          <a
            :class="{ active: currentView === 'stats' }"
            @click="currentView = 'stats'"
          >涨跌统计</a>
          <a
            :class="{ active: currentView === 'trend' }"
            @click="currentView = 'trend'"
          >涨跌趋势</a>
          <a
            :class="{ active: currentView === 'detail' }"
            v-if="selectedTicker"
            @click="currentView = 'detail'"
          >股票详情</a>
        </div>
      </div>
    </nav>

    <!-- 主内容 -->
    <main v-if="isReady">
      <StockScreener v-if="currentView === 'screener'" @view-detail="viewDetail" />
      <TrendLineChart v-if="currentView === 'trend'" />
      <StockDetail
        v-if="currentView === 'detail'"
        :ticker="selectedTicker"
        @back="currentView = 'screener'"
      />
      <TestLayout v-if="currentView === 'test'" />
      <TrendSimple v-if="currentView === 'simple'" />
    </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import StockScreener from './views/StockScreener.vue'
import TrendLineChart from './views/TrendLineChart.vue'
import StockDetail from './views/StockDetail.vue'
import TestLayout from './views/TestLayout.vue'
import TrendSimple from './views/TrendSimple.vue'

const currentView = ref('screener')
const selectedTicker = ref('')
const isReady = ref(false)

const viewDetail = (ticker) => {
  selectedTicker.value = ticker
  currentView.value = 'detail'
}

// 从 URL 查询参数获取初始视图
onMounted(() => {
  console.log('App onMounted, initial view:', currentView.value)
  const urlParams = new URLSearchParams(window.location.search)
  const view = urlParams.get('view')
  console.log('URL view parameter:', view)
  if (view && ['screener', 'trend', 'test', 'simple'].includes(view)) {
    currentView.value = view
    console.log('Set currentView to:', currentView.value)
  }
  // 标记为就绪，允许组件渲染
  isReady.value = true
  console.log('App is ready, rendering view:', currentView.value)
})
</script>

<style>
.navbar {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-title {
  font-size: 20px;
  color: #333;
}

.nav-links {
  display: flex;
  gap: 24px;
}

.nav-links a {
  color: #666;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-links a:hover {
  background: #f5f5f5;
  color: #409eff;
}

.nav-links a.active {
  color: #409eff;
  background: #ecf5ff;
  font-weight: 500;
}
</style>
