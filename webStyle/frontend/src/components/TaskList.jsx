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
          { id: 111, title: '需求1', completed: false },
          { id: 112, title: '需求2', completed: false },
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
          { id: 201, title: '搭建项目结构', completed: true },
          { id: 202, title: '实现组件', completed: false },
          { id: 203, title: '样式优化', completed: false },
        ]
      },
      {
        id: 3,
        title: '测试验收',
        expanded: true,
        isGroup: true,
        subtasks: [
          { id: 301, title: '功能测试', completed: false },
          { id: 302, title: '性能测试', completed: false },
          { id: 303, title: '验收确认', completed: false },
        ]
      }
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
  const [showModal, setShowModal] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDesc, setNewTaskDesc] = useState('')
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
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'system',
      text: `已选择任务: ${task.title} > ${child.title} > ${subtask.title}`
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
                        onClick={() => toggleChild(task.id, child.id)}
                      >
                        <span className="task-arrow">{child.expanded ? '▼' : '▶'}</span>
                        <span>{child.title}</span>
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
                              <span>{subtask.title}</span>
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
        <div className="content-section content-top">
          {selectedTask ? (
            <div className="task-detail">
              <h2>{selectedTask.subtask.title}</h2>
              <p className="task-parent">
                所属任务: {selectedTask.task.title}
                {selectedTask.child && ` > ${selectedTask.child.title}`}
              </p>
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
    </div>
  )
}

export default TaskList
