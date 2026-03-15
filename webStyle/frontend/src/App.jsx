import { useState } from 'react'
import FlowDiagram from './components/FlowDiagram'
import TaskList from './components/TaskList'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('task')

  return (
    <div className="app">
      {/* 顶部导航栏 */}
      <nav className="navbar">
        <div className="navbar-brand">WebStyle</div>
        <div className="navbar-menu">
          <div
            className={`navbar-item ${activeTab === 'task' ? 'active' : ''}`}
            onClick={() => setActiveTab('task')}
          >
            任务
          </div>
          <div
            className={`navbar-item ${activeTab === 'flow' ? 'active' : ''}`}
            onClick={() => setActiveTab('flow')}
          >
            流程图
          </div>
          <div
            className={`navbar-item ${activeTab === 'other' ? 'active' : ''}`}
            onClick={() => setActiveTab('other')}
          >
            其他功能
          </div>
        </div>
        <div className="navbar-spacer"></div>
        <div className="navbar-action">设置</div>
      </nav>

      {/* 主内容区域 */}
      <main className="main">
        <div className="content-card">
          {activeTab === 'task' && <TaskList />}
          {activeTab === 'flow' && <FlowDiagram />}
          {activeTab === 'other' && (
            <div className="placeholder">
              <h3>其他功能</h3>
              <p>这里可以放置其他内容</p>
            </div>
          )}
        </div>
      </main>

      {/* 底部状态栏 */}
      <footer className="footer">
        <div className="footer-item">
          <span className="footer-dot"></span>
          <span>就绪</span>
        </div>
        <div className="footer-spacer"></div>
        <span>v1.0.0</span>
      </footer>
    </div>
  )
}

export default App
