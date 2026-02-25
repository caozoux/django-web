import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const stockAPI = {
  // 每日涨跌统计
  dailySummary(params) {
    return api.get('/market/daily-summary', { params })
  },

  // 股票选股
  screener(params) {
    return api.get('/stocks/screener', { params })
  },

  // 股票K线数据
  getKLine(ticker, params) {
    return api.get(`/stocks/${ticker}/kline`, { params })
  },

  // 股票列表
  getList() {
    return api.get('/stocks/list')
  },

  // 股票详情（用于曲线选股）
  getDetail(ticker, params) {
    return api.get(`/stocks/${ticker}/detail`, { params })
  }
}
