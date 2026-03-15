import { useCallback } from 'react'
import ReactFlow, {
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
} from 'reactflow'
import 'reactflow/dist/style.css'

// 初始节点
const initialNodes = [
  {
    id: '1',
    type: 'input',
    data: { label: '开始' },
    position: { x: 250, y: 0 },
    style: { background: '#e6f7ff', border: '1px solid #1890ff', borderRadius: 8 },
  },
  {
    id: '2',
    data: { label: '处理步骤 1' },
    position: { x: 250, y: 100 },
    style: { background: '#fff', border: '1px solid #d9d9d9', borderRadius: 8 },
  },
  {
    id: '3',
    data: { label: '处理步骤 2' },
    position: { x: 250, y: 200 },
    style: { background: '#fff', border: '1px solid #d9d9d9', borderRadius: 8 },
  },
  {
    id: '4',
    type: 'output',
    data: { label: '结束' },
    position: { x: 250, y: 300 },
    style: { background: '#f6ffed', border: '1px solid #52c41a', borderRadius: 8 },
  },
]

// 初始连线
const initialEdges = [
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3', animated: true },
  { id: 'e3-4', source: '3', target: '4', animated: true },
]

function FlowDiagram() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        attributionPosition="bottom-left"
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
      </ReactFlow>
    </div>
  )
}

export default FlowDiagram
