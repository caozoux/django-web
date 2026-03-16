import { useState, useRef, useEffect } from 'react'
import './TaskList.css'

// 示例任务数据
const initialTasks = [
  {
    id: 1,
    title: '任务',
    expanded: true,
    children: [
      {
        id: 11,
        title: '任务需求汇总',
        expanded: false,
        subtasks: [
          { id: 111, title: '需求1', completed: false, description: '请输入需求1的详细描述...' },
          { id: 112, title: '需求2', completed: false, description: '请输入需求2的详细描述...' },
        ]
      },
      {
        id: 12,
        title: '架构设计与实现',
        expanded: false,
        subtasks: []
      },
      {
        id: 2,
        title: '子任务',
        expanded: true,
        isGroup: true,
        subtasks: [
          { id: 201, title: '搭建项目结构', completed: true, description: '' },
          { id: 202, title: '实现组件', completed: false, description: '' },
          { id: 203, title: '样式优化', completed: false, description: '' },
        ]
      },
      {
        id: 3,
        title: '测试验收',
        expanded: true,
        isGroup: true,
        subtasks: [
          { id: 301, title: '功能测试', completed: false, description: '' },
          { id: 302, title: '性能测试', completed: false, description: '' },
          { id: 303, title: '验收确认', completed: false, description: '' },
        ]
      }
    ]
  },
]

function TaskList() {
  const [tasks, setTasks] = useState(initialTasks)
  const [selectedTask, setSelectedTask] = useState(null)
  const [editContent, setEditContent] = useState('')
  const [messages, setMessages] = useState([
    { id: 1, type: 'system', text: '欢迎使用聊天助手，有什么可以帮助您的？' }
  ])
  const [inputValue, setInputValue] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDesc, setNewTaskDesc] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editingTitle, setEditingTitle] = useState('')
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [showSummary, setShowSummary] = useState(false)
  const [summaryContent, setSummaryContent] = useState('')
  const [showCharts, setShowCharts] = useState(false)
  const [chartData, setChartData] = useState(null)
  const [aiAnalysis, setAiAnalysis] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const toggleTask = (taskId) => {
    setTasks(tasks.map(task =>
      task.id === taskId ? { ...task, expanded: !task.expanded } : task
    ))
  }

  const toggleChild = (taskId, childId) => {
    setTasks(tasks.map(task => {
      if (task.id === taskId && task.children) {
        return {
          ...task,
          children: task.children.map(child =>
            child.id === childId ? { ...child, expanded: !child.expanded } : child
          )
        }
      }
      return task
    }))
  }

  const toggleSubtask = (taskId, childId, subtaskId) => {
    setTasks(tasks.map(task => {
      if (task.id === taskId && task.children) {
        return {
          ...task,
          children: task.children.map(child => {
            if (child.id === childId) {
              return {
                ...child,
                subtasks: child.subtasks.map(st =>
                  st.id === subtaskId ? { ...st, completed: !st.completed } : st
                )
              }
            }
            return child
          })
        }
      }
      return task
    }))
  }

  const selectSubtask = (task, child, subtask) => {
    setSelectedTask({ task, child, subtask })
    setEditContent(subtask.description || '')
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'system',
      text: `已选择任务: ${task.title} > ${child.title} > ${subtask.title}`
    }])
  }

  const addSubtask = (taskId, childId) => {
    const newId = Date.now()
    const newSubtask = {
      id: newId,
      title: `需求${newId.toString().slice(-3)}`,
      completed: false,
      description: ''
    }

    setTasks(tasks.map(task => {
      if (task.id === taskId && task.children) {
        return {
          ...task,
          children: task.children.map(child => {
            if (child.id === childId) {
              return {
                ...child,
                expanded: true,
                subtasks: [...child.subtasks, newSubtask]
              }
            }
            return child
          })
        }
      }
      return task
    }))

    setMessages(prev => [...prev, {
      id: Date.now() + 1,
      type: 'system',
      text: `已添加新需求`
    }])
  }

  const showDeleteConfirm = (taskId, childId, subtaskId, subtaskTitle) => {
    setDeleteConfirm({ taskId, childId, subtaskId, subtaskTitle })
  }

  const confirmDelete = () => {
    if (!deleteConfirm) return

    const { taskId, childId, subtaskId } = deleteConfirm

    // 如果删除的是当前选中的任务，清除选中状态
    if (selectedTask?.subtask.id === subtaskId) {
      setSelectedTask(null)
      setEditContent('')
    }

    setTasks(tasks.map(task => {
      if (task.id === taskId && task.children) {
        return {
          ...task,
          children: task.children.map(child => {
            if (child.id === childId) {
              return {
                ...child,
                subtasks: child.subtasks.filter(st => st.id !== subtaskId)
              }
            }
            return child
          })
        }
      }
      return task
    }))

    setMessages(prev => [...prev, {
      id: Date.now() + 1,
      type: 'system',
      text: `已删除: ${deleteConfirm.subtaskTitle}`
    }])

    setDeleteConfirm(null)
  }

  const cancelDelete = () => {
    setDeleteConfirm(null)
  }

  const generateSummary = (taskId, childId) => {
    // 找到对应的child
    const task = tasks.find(t => t.id === taskId)
    if (!task || !task.children) return

    const child = task.children.find(c => c.id === childId)
    if (!child || !child.subtasks) return

    // 汇总所有需求
    const summary = child.subtasks.map((st, index) => {
      return `【${st.title}】\n${st.description || '暂无描述'}`
    }).join('\n\n---\n\n')

    setSummaryContent(summary)
    // 在右侧显示，而不是弹窗
    setSelectedTask({
      task,
      child,
      subtask: { id: 'summary', title: `${child.title} - 汇总`, description: summary }
    })
    setEditContent(summary)

    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'system',
      text: `已汇总 ${child.subtasks.length} 个需求，显示在右侧`
    }])
  }

  // AI 分析任务数据
  const analyzeTaskData = (taskId, childId) => {
    const task = tasks.find(t => t.id === taskId)
    if (!task || !task.children) return

    const child = task.children.find(c => c.id === childId)
    if (!child || !child.subtasks) return

    // 统计数据
    const completed = child.subtasks.filter(st => st.completed).length
    const pending = child.subtasks.length - completed
    const withDescription = child.subtasks.filter(st => st.description && st.description.trim()).length
    const withoutDescription = child.subtasks.length - withDescription

    // 计算描述字符数分布
    const charCounts = child.subtasks.map(st => ({
      title: st.title,
      count: st.description ? st.description.length : 0
    }))

    setChartData({
      total: child.subtasks.length,
      completed,
      pending,
      withDescription,
      withoutDescription,
      charCounts,
      childTitle: child.title,
      subtasks: child.subtasks
    })
    setShowCharts(true)

    // 模拟 AI 分析
    setIsAnalyzing(true)
    setAiAnalysis('')

    setTimeout(() => {
      const analysis = generateAIAnalysis(child.subtasks, { completed, pending, withDescription, withoutDescription })
      setAiAnalysis(analysis)
      setIsAnalyzing(false)
    }, 1500)

    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'system',
      text: `正在进行 AI 分析...`
    }])
  }

  // 生成 AI 分析报告
  const generateAIAnalysis = (subtasks, stats) => {
    const completionRate = stats.completed / subtasks.length * 100
    const descriptionRate = stats.withDescription / subtasks.length * 100

    let analysis = `## 🤖 AI 智能分析报告\n\n`
    analysis += `### 📊 数据概览\n`
    analysis += `- 总需求数：${subtasks.length} 个\n`
    analysis += `- 完成进度：${stats.completed}/${subtasks.length} (${completionRate.toFixed(1)}%)\n`
    analysis += `- 需求完善度：${stats.withDescription}/${subtasks.length} (${descriptionRate.toFixed(1)}%)\n\n`

    analysis += `### 💡 智能建议\n`
    if (completionRate < 30) {
      analysis += `- ⚠️ 进度较慢，建议加快开发节奏\n`
    } else if (completionRate > 70) {
      analysis += `- ✅ 进度良好，继续保持\n`
    } else {
      analysis += `- 📌 进度正常，按计划推进\n`
    }

    if (descriptionRate < 50) {
      analysis += `- 📝 部分需求缺少详细描述，建议补充完善\n`
    }

    const pendingItems = subtasks.filter(st => !st.completed)
    if (pendingItems.length > 0) {
      analysis += `\n### 📋 待处理项\n`
      pendingItems.forEach((item, index) => {
        analysis += `${index + 1}. ${item.title}${item.description ? ' ✍️' : ' ⚠️需补充描述'}\n`
      })
    }

    return analysis
  }

  const startEditTitle = (taskId, childId, subtaskId, currentTitle) => {
    setEditingId(subtaskId)
    setEditingTitle(currentTitle)
  }

  const saveEditTitle = (taskId, childId, subtaskId) => {
    if (!editingTitle.trim()) return

    setTasks(tasks.map(task => {
      if (task.id === taskId && task.children) {
        return {
          ...task,
          children: task.children.map(child => {
            if (child.id === childId) {
              return {
                ...child,
                subtasks: child.subtasks.map(st =>
                  st.id === subtaskId ? { ...st, title: editingTitle.trim() } : st
                )
              }
            }
            return child
          })
        }
      }
      return task
    }))

    // 更新选中状态
    if (selectedTask?.subtask.id === subtaskId) {
      setSelectedTask({
        ...selectedTask,
        subtask: { ...selectedTask.subtask, title: editingTitle.trim() }
      })
    }

    setEditingId(null)
    setEditingTitle('')
  }

  const cancelEditTitle = () => {
    setEditingId(null)
    setEditingTitle('')
  }

  const handleSendMessage = (e) => {
    e.preventDefault()
    if (!inputValue.trim()) return

    // 添加用户消息
    const userMessage = { id: Date.now(), type: 'user', text: inputValue }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')

    // 模拟回复
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        text: `收到您的消息: "${inputValue}"。这是一个模拟回复。`
      }])
    }, 500)
  }

  const handleAddTask = () => {
    if (!newTaskTitle.trim()) return

    const newTask = {
      id: Date.now(),
      title: newTaskTitle,
      expanded: true,
      subtasks: newTaskDesc.trim() ? [
        { id: Date.now() + 1, title: newTaskDesc, completed: false }
      ] : []
    }

    setTasks([...tasks, newTask])
    setNewTaskTitle('')
    setNewTaskDesc('')
    setShowModal(false)

    // 添加系统消息
    setMessages(prev => [...prev, {
      id: Date.now() + 2,
      type: 'system',
      text: `已创建新任务: ${newTaskTitle}`
    }])
  }

  const closeModal = () => {
    setShowModal(false)
    setNewTaskTitle('')
    setNewTaskDesc('')
  }

  return (
    <div className="task-layout">
      {/* 左侧任务列表 */}
      <div className="task-sidebar">
        <div className="task-header">
          <h3>任务列表</h3>
          <button className="add-task-btn" onClick={() => setShowModal(true)}>+ 新建</button>
        </div>
        <div className="task-list">
          {tasks.map(task => (
            <div key={task.id} className="task-item">
              <div
                className={`task-title ${task.expanded ? 'expanded' : ''}`}
                onClick={() => toggleTask(task.id)}
              >
                <span className="task-arrow">{task.expanded ? '▼' : '▶'}</span>
                <span>{task.title}</span>
              </div>
              {task.expanded && task.children && (
                <div className="child-list">
                  {task.children.map(child => (
                    <div key={child.id} className={`child-item ${child.isGroup ? 'is-group' : ''}`}>
                      <div
                        className={`child-title ${child.expanded ? 'expanded' : ''}`}
                      >
                        <span
                          className="task-arrow clickable-arrow"
                          onClick={() => toggleChild(task.id, child.id)}
                        >
                          {child.expanded ? '▼' : '▶'}
                        </span>
                        <span
                          className="child-title-text"
                          onClick={() => {
                            if (!child.isGroup) {
                              generateSummary(task.id, child.id)
                            }
                          }}
                        >
                          {child.title}
                        </span>
                        {/* 非分组项显示添加按钮 */}
                        {!child.isGroup && (
                          <>
                            <span
                              className="chart-icon ai-icon"
                              onClick={(e) => {
                                e.stopPropagation()
                                analyzeTaskData(task.id, child.id)
                              }}
                              title="AI 分析"
                            >
                              🤖
                            </span>
                            <span
                              className="chart-icon"
                              onClick={(e) => {
                                e.stopPropagation()
                                analyzeTaskData(task.id, child.id)
                              }}
                              title="趋势分析"
                            >
                              📈
                            </span>
                            <span
                              className="add-icon"
                              onClick={(e) => {
                                e.stopPropagation()
                                addSubtask(task.id, child.id)
                              }}
                              title="添加子需求"
                            >
                              +
                            </span>
                          </>
                        )}
                      </div>
                      {child.expanded && child.subtasks && child.subtasks.length > 0 && (
                        <div className="subtask-list">
                          {child.subtasks.map(subtask => (
                            <div
                              key={subtask.id}
                              className={`subtask-item ${subtask.completed ? 'completed' : ''} ${selectedTask?.subtask.id === subtask.id ? 'selected' : ''}`}
                              onClick={() => selectSubtask(task, child, subtask)}
                            >
                              <input
                                type="checkbox"
                                checked={subtask.completed}
                                onChange={(e) => {
                                  e.stopPropagation()
                                  toggleSubtask(task.id, child.id, subtask.id)
                                }}
                              />
                              {editingId === subtask.id ? (
                                <input
                                  type="text"
                                  className="edit-title-input"
                                  value={editingTitle}
                                  onChange={(e) => setEditingTitle(e.target.value)}
                                  onBlur={() => saveEditTitle(task.id, child.id, subtask.id)}
                                  onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                      saveEditTitle(task.id, child.id, subtask.id)
                                    } else if (e.key === 'Escape') {
                                      cancelEditTitle()
                                    }
                                  }}
                                  onClick={(e) => e.stopPropagation()}
                                  autoFocus
                                />
                              ) : (
                                <span
                                  className="subtask-title"
                                  onDoubleClick={(e) => {
                                    e.stopPropagation()
                                    startEditTitle(task.id, child.id, subtask.id, subtask.title)
                                  }}
                                >
                                  {subtask.title}
                                </span>
                              )}
                              {/* 非分组项的子任务显示删除按钮 */}
                              {!child.isGroup && editingId !== subtask.id && (
                                <span
                                  className="delete-icon"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    showDeleteConfirm(task.id, child.id, subtask.id, subtask.title)
                                  }}
                                  title="删除"
                                >
                                  −
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 右侧显示区域 */}
      <div className="task-content">
        {/* 图表分析弹窗 */}
        {showCharts && chartData && (
          <div className="modal-overlay" onClick={() => setShowCharts(false)}>
            <div className="modal chart-modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>🤖 {chartData.childTitle} - AI 智能分析</h3>
                <button className="modal-close" onClick={() => setShowCharts(false)}>×</button>
              </div>
              <div className="modal-body">
                <div className="charts-container">
                  {/* 饼图 - 任务完成状态 */}
                  <div className="chart-box">
                    <h4>任务完成状态</h4>
                    <div className="pie-chart">
                      <div className="pie-chart-visual">
                        <svg viewBox="0 0 100 100">
                          {chartData.total > 0 && (
                            <>
                              <circle
                                cx="50"
                                cy="50"
                                r="40"
                                fill="transparent"
                                stroke="#e6f7ff"
                                strokeWidth="20"
                              />
                              <circle
                                cx="50"
                                cy="50"
                                r="40"
                                fill="transparent"
                                stroke="#52c41a"
                                strokeWidth="20"
                                strokeDasharray={`${(chartData.completed / chartData.total) * 251.2} 251.2`}
                                strokeDashoffset="0"
                                transform="rotate(-90 50 50)"
                              />
                            </>
                          )}
                        </svg>
                        <div className="pie-center">
                          <span className="pie-percent">
                            {chartData.total > 0 ? Math.round((chartData.completed / chartData.total) * 100) : 0}%
                          </span>
                          <span className="pie-label">完成率</span>
                        </div>
                      </div>
                      <div className="chart-legend">
                        <div className="legend-item">
                          <span className="legend-color completed"></span>
                          <span>已完成: {chartData.completed}</span>
                        </div>
                        <div className="legend-item">
                          <span className="legend-color pending"></span>
                          <span>待处理: {chartData.pending}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* 柱状图 - 描述字符数 */}
                  <div className="chart-box">
                    <h4>需求描述详情</h4>
                    <div className="bar-chart">
                      <div className="bar-chart-stats">
                        <div className="stat-item">
                          <div className="stat-value">{chartData.total}</div>
                          <div className="stat-label">总需求数</div>
                        </div>
                        <div className="stat-item">
                          <div className="stat-value has-desc">{chartData.withDescription}</div>
                          <div className="stat-label">有描述</div>
                        </div>
                        <div className="stat-item">
                          <div className="stat-value no-desc">{chartData.withoutDescription}</div>
                          <div className="stat-label">无描述</div>
                        </div>
                      </div>
                      <div className="bar-chart-bars">
                        {chartData.charCounts.slice(0, 5).map((item, index) => (
                          <div key={index} className="bar-row">
                            <span className="bar-label">{item.title}</span>
                            <div className="bar-wrapper">
                              <div
                                className="bar-fill"
                                style={{ width: `${Math.min(item.count / 10, 100)}%` }}
                              ></div>
                            </div>
                            <span className="bar-value">{item.count}字</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI 分析报告 */}
                <div className="ai-analysis-section">
                  <h4>🤖 AI 智能分析</h4>
                  {isAnalyzing ? (
                    <div className="ai-loading">
                      <div className="loading-spinner"></div>
                      <span>AI 正在分析中...</span>
                    </div>
                  ) : (
                    <div className="ai-report">
                      {aiAnalysis.split('\n').map((line, index) => {
                        if (line.startsWith('## ')) {
                          return <h2 key={index} className="ai-title">{line.replace('## ', '')}</h2>
                        } else if (line.startsWith('### ')) {
                          return <h3 key={index} className="ai-subtitle">{line.replace('### ', '')}</h3>
                        } else if (line.startsWith('- ')) {
                          return <p key={index} className="ai-item">{line.replace('- ', '')}</p>
                        } else if (line.match(/^\d+\./)) {
                          return <p key={index} className="ai-item numbered">{line}</p>
                        } else if (line.trim()) {
                          return <p key={index} className="ai-text">{line}</p>
                        }
                        return null
                      })}
                    </div>
                  )}
                </div>
              </div>
              <div className="modal-footer">
                <button className="btn-cancel" onClick={() => setShowCharts(false)}>关闭</button>
              </div>
            </div>
          </div>
        )}

        <div className="content-section content-top">
          {selectedTask ? (
            <div className="editor-container">
              <div className="editor-header">
                <h3>{selectedTask.subtask.title}</h3>
                <span className="editor-path">
                  {selectedTask.task.title} &gt; {selectedTask.child.title}
                </span>
              </div>
              <textarea
                className="editor-textarea"
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                placeholder="请输入需求描述..."
              />
              <div className="editor-footer">
                <span className="char-count">{editContent.length} 字</span>
                <button
                  className="btn-save"
                  onClick={() => {
                    // 保存编辑内容
                    setTasks(tasks.map(task => {
                      if (task.id === selectedTask.task.id && task.children) {
                        return {
                          ...task,
                          children: task.children.map(child => {
                            if (child.id === selectedTask.child.id) {
                              return {
                                ...child,
                                subtasks: child.subtasks.map(st =>
                                  st.id === selectedTask.subtask.id
                                    ? { ...st, description: editContent }
                                    : st
                                )
                              }
                            }
                            return child
                          })
                        }
                      }
                      return task
                    }))
                    setMessages(prev => [...prev, {
                      id: Date.now(),
                      type: 'system',
                      text: `已保存: ${selectedTask.subtask.title} 的描述`
                    }])
                  }}
                >
                  保存
                </button>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <h3>选择一个任务</h3>
              <p>从左侧列表选择任务查看详情</p>
            </div>
          )}
        </div>
        <div className="content-section content-bottom">
          <div className="section-header">
            <h3>💬 对话助手</h3>
          </div>
          <div className="chat-container">
            <div className="chat-messages">
              {messages.map(msg => (
                <div key={msg.id} className={`chat-message ${msg.type}`}>
                  <div className="message-bubble">{msg.text}</div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            <form className="chat-input-form" onSubmit={handleSendMessage}>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="输入消息..."
                className="chat-input"
              />
              <button type="submit" className="chat-send-btn">发送</button>
            </form>
          </div>
        </div>
      </div>

      {/* 新建任务对话框 */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>新建任务</h3>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>任务名称</label>
                <input
                  type="text"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="输入任务名称..."
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>任务描述</label>
                <textarea
                  value={newTaskDesc}
                  onChange={(e) => setNewTaskDesc(e.target.value)}
                  placeholder="输入任务描述（可选）..."
                  rows={4}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-cancel" onClick={closeModal}>取消</button>
              <button className="btn-confirm" onClick={handleAddTask}>确定</button>
            </div>
          </div>
        </div>
      )}

      {/* 删除确认对话框 */}
      {deleteConfirm && (
        <div className="modal-overlay" onClick={cancelDelete}>
          <div className="modal confirm-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>确认删除</h3>
            </div>
            <div className="modal-body">
              <p className="confirm-text">
                确定要删除 "<strong>{deleteConfirm.subtaskTitle}</strong>" 吗？
              </p>
              <p className="confirm-hint">此操作无法撤销</p>
            </div>
            <div className="modal-footer">
              <button className="btn-cancel" onClick={cancelDelete}>取消</button>
              <button className="btn-delete" onClick={confirmDelete}>删除</button>
            </div>
          </div>
        </div>
      )}

    </div>
  )
}

export default TaskList
