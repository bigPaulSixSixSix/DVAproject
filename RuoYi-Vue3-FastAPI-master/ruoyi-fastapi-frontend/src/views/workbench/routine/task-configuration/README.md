# 任务配置模块 (Task Configuration)

本模块用于管理工作流中的任务配置，包括阶段管理、任务管理、连接关系等功能。

## 目录结构

```
task-configuration/
├── components/          # 组件
│   ├── WorkflowCanvas.vue    # 工作流画布主组件
│   ├── Stage/                # 阶段相关组件
│   ├── Task/                 # 任务相关组件
│   └── Connection/           # 连接相关组件
│
├── composables/        # 可复用的组合式函数
│   ├── canvas/              # 画布相关操作
│   ├── workflowdata/        # 工作流数据相关
│   ├── task/                # 任务相关
│   ├── stage/               # 阶段相关
│   ├── connection/          # 连接相关
│   ├── utils/               # 工具函数
│   └── system/              # 系统功能
│
├── stores/             # 状态管理
│   ├── workflowStore.js
│   └── projectStore.js
│
├── utils/              # 工具函数
│
├── index.vue           # 主入口组件
├── project-list.vue    # 项目列表组件
└── README.md           # 本文档
```

## Composables 文件夹结构

所有可复用的组合式函数（composables）按功能模块组织在 `composables/` 目录下。

### 完整结构

```
composables/
├── canvas/              # 画布相关操作
│   ├── useCanvasZoom.js
│   ├── useCanvasZoomControls.js
│   ├── useCanvasDrag.js
│   ├── useCanvasLayout.js
│   ├── useCanvasEventHandlers.js
│   ├── useDragToAdd.js
│   ├── useDragDrop.js
│   └── useGridSnap.js
│
├── workflowdata/        # 工作流数据相关
│   ├── useWorkflowData.js
│   ├── useWorkflowDataOperations.js
│   ├── useWorkflowLoader.js
│   ├── useWorkflowInitializer.js
│   ├── useWorkflowSave.js
│   ├── useWorkflowController.js (原 useCanvasController.js)
│   └── useTaskValidationInitializer.js
│
├── task/                # 任务相关
│   ├── useTaskManagement.js
│   ├── useTaskDrag.js
│   ├── useTaskDragEnd.js
│   ├── useTaskDragHandler.js
│   ├── useTaskDragPreview.js
│   ├── useTaskDragSnapshot.js
│   ├── useTaskEdit.js
│   ├── useTaskEditController.js
│   ├── useTaskValidation.js
│   ├── useTaskTimeValidation.js
│   ├── useTaskFocus.js
│   ├── useTaskVisibility.js
│   ├── useAbnormalTasks.js
│   └── useAbnormalTaskDialog.js
│
├── stage/               # 阶段相关
│   ├── useStageManagement.js
│   ├── useStageEdit.js
│   └── useStageController.js
│
├── connection/          # 连接相关
│   ├── useConnection.js
│   ├── config/
│   │   └── testConfig.js
│   ├── creation/
│   │   ├── useConnectionBuilder.js
│   │   └── useConnectionCreator.js
│   ├── interaction/
│   │   ├── useConnectionHandlers.js
│   │   └── usePreviewConnection.js
│   ├── data/
│   │   └── useConnectionManager.js
│   ├── rendering/
│   │   └── useConnectionLine.js
│   ├── utils/
│   │   ├── useConnectionInitializer.js
│   │   ├── useConnectionLogger.js
│   │   └── useConnectionUtils.js
│   └── validation/
│       ├── useConnectionValidation.js
│       └── useCycleDetection.js
│
├── utils/               # 工具函数
│   ├── useUtils.js
│   ├── useIdManager.js
│   └── useDebug.js
│
└── system/              # 系统功能
    └── useAutoSave.js
```

### 模块说明

#### canvas/
画布相关的操作，包括：
- **缩放**：`useCanvasZoom`, `useCanvasZoomControls`
- **拖拽**：`useCanvasDrag`, `useDragToAdd`, `useDragDrop`
- **布局**：`useCanvasLayout`
- **事件处理**：`useCanvasEventHandlers`
- **网格对齐**：`useGridSnap`

#### workflowdata/
工作流数据相关的操作，包括：
- **数据管理**：`useWorkflowData`, `useWorkflowDataOperations`
- **加载和保存**：`useWorkflowLoader`, `useWorkflowSave`
- **初始化**：`useWorkflowInitializer`, `useTaskValidationInitializer`
- **控制器**：`useWorkflowController`（原 `useCanvasController`，处理保存、创建等操作）

#### task/
任务相关的操作，包括：
- **管理**：`useTaskManagement`
- **拖拽**：`useTaskDrag`, `useTaskDragEnd`, `useTaskDragHandler`, `useTaskDragPreview`, `useTaskDragSnapshot`
- **编辑**：`useTaskEdit`, `useTaskEditController`
- **验证**：`useTaskValidation`, `useTaskTimeValidation`
- **UI 相关**：`useTaskFocus`, `useTaskVisibility`, `useAbnormalTasks`, `useAbnormalTaskDialog`

#### stage/
阶段相关的操作，包括：
- **管理**：`useStageManagement`
- **编辑**：`useStageEdit`
- **控制器**：`useStageController`

#### connection/
连接相关的操作，按子功能进一步分类：
- **创建**：`creation/`
- **交互**：`interaction/` - UI交互层，处理用户操作和状态管理
- **数据**：`data/` - 数据管理层，处理连接数据的CRUD操作
- **渲染**：`rendering/`
- **工具**：`utils/`
- **验证**：`validation/`

#### utils/
通用的工具函数，包括：
- **通用工具**：`useUtils`
- **ID 管理**：`useIdManager`
- **调试**：`useDebug`

#### system/
系统级别的功能，包括：
- **自动保存**：`useAutoSave`

## 代码组织原则

### 1. 代码规范性
- **单一职责原则**：每个 composable 只负责一个功能领域
- **关注点分离**：UI 组件只负责渲染，业务逻辑在 composables 中
- **可复用性**：提取的逻辑可以在其他组件中复用

### 2. 角色和功能划分

#### UI 组件（如 WorkflowCanvas.vue）
- **职责**：UI 渲染、事件绑定、props/emit 传递
- **保留内容**：
  - 模板结构
  - 样式定义
  - 简单的 UI 状态管理（如 `canvasRef`）
  - 事件绑定和转发

#### Composables（业务逻辑）
- **职责**：业务逻辑、计算属性、状态管理
- **提取内容**：
  - 复杂计算（如画布尺寸计算）
  - 业务逻辑（如任务定位、异常任务对话框）
  - 事件处理逻辑（简单的 emit 转发除外）

### 3. 封装和调用

#### 应该封装的情况
1. **复杂计算逻辑**：如 `canvasSize`、`zoomOptions`
2. **业务逻辑**：如 `focusOnTask`、`handleAbnormalButtonClick`
3. **可复用的工具函数**：如 `findTaskById`
4. **状态管理**：如异常任务对话框的显示状态

#### 可以保留在组件中的情况
1. **简单的 emit 转发**：如 `handleUndo = () => emit('undo')`
   - **注意**：为了代码一致性，这些也被提取到了 `useCanvasEventHandlers`
2. **UI 相关的 ref**：如 `canvasRef`
3. **模板绑定**：直接在模板中使用的事件处理

## 导入路径示例

```javascript
// Canvas 相关
import { useCanvasZoom } from '../composables/canvas/useCanvasZoom'
import { useCanvasDrag } from '../composables/canvas/useCanvasDrag'

// WorkflowData 相关
import { useWorkflowData } from '../composables/workflowdata/useWorkflowData'
import { useWorkflowController } from '../composables/workflowdata/useWorkflowController'

// Task 相关
import { useTaskManagement } from '../composables/task/useTaskManagement'

// Utils 相关
import { useIdManager } from '../composables/utils/useIdManager'

// System 相关
import { useAutoSave } from '../composables/system/useAutoSave'
```

## 命名规范

1. **文件名**：使用 `use` 前缀，采用驼峰命名，如 `useCanvasZoom.js`
2. **文件夹名**：使用小写，多个单词用连字符或直接连接，如 `canvas/`, `workflowdata/`
3. **导出函数**：与文件名保持一致（去掉 `.js` 和 `use` 前缀），如 `useCanvasZoom` 导出 `useCanvasZoom`

## 使用建议

### 1. 添加新功能时
- 如果是业务逻辑，创建新的 composable
- 如果是 UI 相关，直接在组件中添加

### 2. 修改现有功能时
- 先检查是否已有对应的 composable
- 如果没有，考虑是否需要创建
- 保持代码风格一致

### 3. 测试
- Composables 可以独立测试
- 组件测试专注于 UI 交互

## 注意事项

1. **依赖关系**：注意 composables 之间的依赖关系，避免循环依赖
2. **路径更新**：移动文件后，记得更新所有引用该文件的 import 路径
3. **功能划分**：如果某个 composable 变得过大，考虑进一步拆分到子文件夹
4. **Props 传递**：某些函数（如 `findTaskById`）通过 props 传入，确保父组件正确传递
5. **响应式数据**：使用 `computed` 包装 props，确保响应式更新

## 重构历史

### WorkflowCanvas.vue 重构

将 `WorkflowCanvas.vue` 中的业务逻辑提取到 composables，使组件专注于 UI 渲染和事件转发。

#### 重构前后对比

**重构前**：
- 代码行数：~940 行
- 业务逻辑和 UI 混合
- 函数职责不清晰
- 难以测试和复用

**重构后**：
- 代码行数：~730 行（减少约 200 行）
- 业务逻辑分离到 composables
- 函数职责清晰
- 易于测试和复用

#### 新创建的 Composables

1. **useCanvasLayout.js** - 画布尺寸计算、包装器样式
2. **useCanvasZoomControls.js** - 缩放控制相关
3. **useTaskFocus.js** - 任务定位功能
4. **useTaskVisibility.js** - 任务可见性过滤
5. **useCanvasEventHandlers.js** - 统一的事件处理器（简单的 emit 转发）
6. **useAbnormalTaskDialog.js** - 异常任务对话框管理

## 后续优化建议

1. **进一步拆分**：如果某个 composable 变得过大，考虑进一步拆分
2. **类型定义**：考虑添加 TypeScript 类型定义
3. **单元测试**：为每个 composable 添加单元测试
4. **文档完善**：为每个 composable 添加 JSDoc 注释

