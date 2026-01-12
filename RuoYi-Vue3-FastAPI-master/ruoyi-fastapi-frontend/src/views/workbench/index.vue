<template>
  <div class="app-container">
    <!-- 汇总区域 -->
    <div class="summary-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <AnnouncementCard />
        </el-col>
        <el-col :span="8">
          <TaskCard />
        </el-col>
        <el-col :span="8">
          <TaskOverviewCard />
        </el-col>
      </el-row>
    </div>

    <!-- 动态功能区域 -->
    <div 
      v-for="category in workbenchCategories" 
      :key="category.title"
      class="function-section"
    >
      <h3 class="section-title">{{ category.title }}</h3>
      <div class="function-grid">
        <FunctionCard
          v-for="(item, index) in category.children" 
          :key="index"
          :title="item.title"
          :icon-name="item.icon || 'Menu'"
          :icon-color="getIconColor(index)"
          :path="item.path"
        />
      </div>
    </div>

    <!-- 空状态提示 -->
    <div v-if="workbenchCategories.length === 0" class="empty-state">
      <el-empty description="暂无工作台功能配置" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AnnouncementCard from '@/components/Workbench/SummaryCard/AnnouncementCard.vue'
import TaskCard from '@/components/Workbench/SummaryCard/TaskCard.vue'
import TaskOverviewCard from '@/components/Workbench/SummaryCard/TaskOverviewCard.vue'
import FunctionCard from '@/components/Workbench/FunctionCard/index.vue'
import usePermissionStore from '@/store/modules/permission'

defineOptions({
  name: 'Workbench'
})

const workbenchCategories = ref([])

// 从路由数据中查找工作台路由
const findWorkbenchRoute = (routes) => {
  for (const route of routes) {
    if (route.path === '/' && route.children) {
      const workbenchChild = route.children.find(child => 
        (child.path === 'workbench' || child.path === '/workbench') &&
        child.component === 'workbench/index' &&
        (child.meta && child.meta.title === '工作台')
      )
      if (workbenchChild) return workbenchChild
    }
    if (route.children && route.children.length > 0) {
      const found = findWorkbenchRoute(route.children)
        if (found) return found
      }
    }
    return null
  }
  
// 从路由数据中提取分类和功能菜单
const extractCategoriesFromRoutes = (subMenus, basePath = '/workbench') => {
  const categories = []
  
  // 找出所有分类（ParentView 或 Layout 组件且有 children 的）
  subMenus.forEach(menu => {
    // 检查是否是分类组件（ParentView 或 Layout）
    // 可能是字符串 "ParentView"/"Layout" 或组件对象
    const isCategoryComponent = 
      menu.component === 'ParentView' || 
      menu.component === 'Layout' ||
      (typeof menu.component === 'function' && (menu.component.name === 'Layout' || menu.component.name === 'ParentView')) ||
      (menu.component && menu.component.toString().includes('Layout')) ||
      (menu.component && menu.component.toString().includes('ParentView'))
    
    if (isCategoryComponent && menu.children && menu.children.length > 0) {
      // 这是一个分类
      const categoryTitle = menu.meta?.title || menu.name || '未命名分类'
      
      const category = {
        id: menu.path,
        title: categoryTitle,
        orderNum: 0,
        children: []
      }
      
      // 提取该分类下的功能菜单
      menu.children.forEach(child => {
        // 如果子菜单还有 children 且 component 是 Layout，需要递归处理
        if (child.children && child.children.length > 0 && child.component === 'Layout') {
          // 这是一个嵌套的分类，递归处理其 children
          child.children.forEach(nestedChild => {
            if (nestedChild.meta && nestedChild.meta.title) {
              const fullPath = buildFullPath(child.path, nestedChild.path, menu.path, basePath)
              
              category.children.push({
                title: nestedChild.meta.title,
                icon: nestedChild.meta.icon,
        path: fullPath,
                orderNum: 0
              })
            }
          })
        } else if (child.meta && child.meta.title) {
          // 检查是否是空菜单项（component 是 Layout 或 ParentView 但没有 children）
          const isLayoutOrParentView = child.component === 'Layout' || child.component === 'ParentView'
          const hasNoChildren = !child.children || child.children.length === 0
          const isEmptyMenu = isLayoutOrParentView && hasNoChildren
          
          let fullPath = buildFullPath(child.path, null, menu.path, basePath)
          
          // 空菜单项会在 filterChildren 中自动处理
          
          category.children.push({
            title: child.meta.title,
            icon: child.meta.icon,
            path: fullPath,
            orderNum: 0
          })
        }
      })
      
      // 只添加有子菜单的分类
      if (category.children.length > 0) {
        categories.push(category)
            }
          }
  })
  
  return categories
      }
      
// 构建完整路径的辅助函数
const buildFullPath = (childPath, nestedPath, categoryPath, basePath) => {
  let fullPath = nestedPath || childPath
  
  // 如果路径不是绝对路径，需要拼接
  if (!fullPath || !fullPath.startsWith('/')) {
    // 构建路径：/workbench + /分类路径 + /功能路径
    const pathParts = [basePath]
    
    if (categoryPath && categoryPath !== 'workbench') {
      pathParts.push(categoryPath.replace(/^\/+/, ''))
    }
    
    if (childPath && childPath !== 'workbench') {
      pathParts.push(childPath.replace(/^\/+/, ''))
    }
    
    if (nestedPath) {
      pathParts.push(nestedPath.replace(/^\/+/, ''))
    }
    
    fullPath = '/' + pathParts.filter(p => p).join('/')
  }
  
  // 清理路径中的双斜杠
  fullPath = fullPath.replace(/\/+/g, '/')
  
  return fullPath
}


// 获取工作台菜单数据并转换为分类结构（从 getRouters 中提取）
const getWorkbenchMenus = async () => {
  try {
    // 优先从 permissionStore 获取已缓存的路由数据，避免重复请求
    const permissionStore = usePermissionStore()
    let registeredRoutes
    
    if (permissionStore.routersData) {
      // 使用已缓存的数据
      registeredRoutes = permissionStore.routersData
    } else {
      // 如果没有缓存，则请求并缓存
      const { getRouters } = await import('@/api/menu')
      const routerResponse = await getRouters()
      registeredRoutes = routerResponse.data
      permissionStore.routersData = registeredRoutes
    }
    
    // 根据后端返回的数据结构：
    // "/" 路由的 children 中：
    // - 第一个是工作台主页面（path: 'workbench', component: 'workbench/index'）
    // - 后续是工作台的子菜单（path: 'routine', 'asset' 等，component: 'ParentView' 或 'Layout'）
    // 我们需要从 "/" 路由的 children 中提取工作台的子菜单（排除工作台主页面本身）
    
    let rootRoute = null
    for (const route of registeredRoutes) {
      if (route.path === '/' && route.children) {
        rootRoute = route
        break
      }
    }
    
    if (!rootRoute || !rootRoute.children || rootRoute.children.length === 0) {
      workbenchCategories.value = []
      return
    }
    
    // 找到工作台主页面路由（component 是 'workbench/index' 的）
    const workbenchMainRoute = rootRoute.children.find(child => 
      (child.path === 'workbench' || child.path === '/workbench') &&
      child.component === 'workbench/index' &&
      (child.meta && child.meta.title === '工作台')
    )
    
    if (!workbenchMainRoute) {
      workbenchCategories.value = []
      return
    }
    
    // 提取工作台的子菜单（排除工作台主页面本身）
    // 子菜单的特征：component 是 'ParentView' 或 'Layout'，且有 children
    const subMenus = rootRoute.children.filter(child => {
      // 排除工作台主页面
      if (child === workbenchMainRoute) {
        return false
      }
      // 只保留有 children 的子菜单（分类）
      return child.children && child.children.length > 0
        })
    
    if (subMenus.length === 0) {
      workbenchCategories.value = []
      return
    }
    
    // 从路由数据中提取分类和功能菜单
    const categories = extractCategoriesFromRoutes(subMenus, '/workbench')

    // 过滤空分类并赋值
    workbenchCategories.value = categories.filter(c => c.children.length > 0)
  } catch (error) {
    workbenchCategories.value = []
  }
}

// 获取图标颜色
const getIconColor = (index) => {
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  return colors[index % colors.length]
}

onMounted(() => {
  getWorkbenchMenus()
})
</script>

<style scoped lang="scss">
.summary-section {
  margin-bottom: 32px;
}

.function-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 16px;
  padding-left: 4px;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  max-width: 100%;
}

@media (min-width: 1200px) {
  .function-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (max-width: 1199px) and (min-width: 992px) {
  .function-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 991px) and (min-width: 768px) {
  .function-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 767px) {
  .function-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.empty-state {
  margin-top: 40px;
  text-align: center;
}
</style>