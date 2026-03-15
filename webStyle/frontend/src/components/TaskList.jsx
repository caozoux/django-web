import { useState, useRef, useEffect } from 'react'
import './TaskList.css'

// 示例任务数据
const initialTasks = [
  {
    id: 1,
    title: '项目规划',
    expanded: true,
    subtasks: [
      { id: 101, title: '需求分析', completed: false },
      { id: 102, title: '技术选型', completed: true },
      { id: 103, title: '制定计划', completed: false },
    ]
  },
  {
    id: 2,
    title: '前端开发',
    expanded: false,
    subtasks: [
      { id: 201, title: '搭建项目结构', completed: true },
      { id: 202, title: '实现组件', completed: false },
      { id: 203, title: '样式优化', completed: false },
    ]
  },
  {
    id: 3,
    title: '后端开发',
    expanded: false,
    subtasks: [
      { id: 301, title: 'API 设计', completed: false },
      { id: 302, title: '数据库设计', completed: false },
    ]
  },
  {
    id: 4,
    title: '测试与部署',
    expanded: false,
    subtasks: [
      { id: 401, title: '单元测试', completed: false },
      { id: 402, title: '集成测试', completed: false },
      { id: 403, title: '部署上线', completed: false },
    ]
  },
]

function TaskList() {
  const [tasks, setTasks] = useState(initialTasks)
  const [selectedTask, setSelectedTask] = useState(null)
  const [messages, setMessages] = useState([
    { id: 1, type: 'system', text: '欢迎使用聊天助手，有什么可以帮助您的？' }
  ])
  const [inputValue, setInputValue] = useState('')
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

  const toggleSubtask = (taskId, subtaskId) => {
    setTasks(tasks.map(task => {
      if (task.id === taskId) {
        return {
          ...task,
          subtasks: task.subtasks.map(st =>
            st.id === subtaskId ? { ...st, completed: !st.completed } : st
          )
        }
      }
      return task
    }))
  }

  const selectSubtask = (task, subtask) => {
    setSelectedTask({ task, subtask })
    // 添加任务选择提示消息
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'system',
      text: `已选择任务: ${task.title} > ${subtask.title}`
    }])
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

  return (
    <div className="task-layout">
      {/* 左侧任务列表 */}
      <div className="task-sidebar">
        <div className="task-header">
          <h3>任务列表</h3>
          <button className="add-task-btn">+ 新建</button>
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
              {task.expanded && (
                <div className="subtask-list">
                  {task.subtasks.map(subtask => (
                    <div
                      key={subtask.id}
                      className={`subtask-item ${subtask.completed ? 'completed' : ''} ${selectedTask?.subtask.id === subtask.id ? 'selected' : ''}`}
                      onClick={() => selectSubtask(task, subtask)}
                    >
                      <input
                        type="checkbox"
                        checked={subtask.completed}
                        onChange={(e) => {
                          e.stopPropagation()
                          toggleSubtask(task.id, subtask.id)
                        }}
                      />
                      <span>{subtask.title}</span>
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
        <div className="content-section content-top">
          {selectedTask ? (
            <div className="task-detail">
              <h2>{selectedTask.subtask.title}</h2>
              <p className="task-parent">所属任务: {selectedTask.task.title}</p>
              <div className="task-status">
                状态: {selectedTask.subtask.completed ? '已完成' : '进行中'}
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
    </div>
  )
}

export default TaskList
