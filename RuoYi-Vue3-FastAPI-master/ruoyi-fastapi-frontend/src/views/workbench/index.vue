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
import { listMenu } from '@/api/system/menu'
import { getRouters } from '@/api/menu'
import AnnouncementCard from '@/components/Workbench/SummaryCard/AnnouncementCard.vue'
import TaskCard from '@/components/Workbench/SummaryCard/TaskCard.vue'
import TaskOverviewCard from '@/components/Workbench/SummaryCard/TaskOverviewCard.vue'
import FunctionCard from '@/components/Workbench/FunctionCard/index.vue'
import usePermissionStore, { loadView } from '@/store/modules/permission'
import router from '@/router'
import Layout from '@/layout'

defineOptions({
  name: 'Workbench'
})

const workbenchCategories = ref([])

// 从已注册的路由中查找匹配的路径
const findRegisteredPath = (menu, allMenus, registeredRoutes) => {
  // 查找工作台父级菜单
  const workbenchParent = allMenus.find(m => m.path === 'workbench' || m.path === '/workbench')
  if (!workbenchParent) return menu.path
  
  // 构建相对路径：routine/task-configuration（相对于/workbench）
  const pathSegments = []
  let currentMenu = menu
  
  // 向上遍历父级菜单，构建路径（不包括工作台本身）
  while (currentMenu) {
    if (currentMenu.path && currentMenu.path !== 'workbench') {
      pathSegments.unshift(currentMenu.path)
    }
    // 查找父级菜单
    currentMenu = allMenus.find(m => m.menuId === currentMenu.parentId)
  }
  
  // 构建相对路径
  const relativePath = pathSegments.join('/')
  
  // 构建完整路径：/workbench + '/' + relativePath
  const fullPath = '/workbench/' + relativePath
  
  // 在已注册的路由中查找匹配的路径
  const findRouteByPath = (routes, targetPath) => {
    for (const route of routes) {
      if (route.path === targetPath) {
        return route.path
      }
      if (route.children) {
        const found = findRouteByPath(route.children, targetPath)
        if (found) return found
      }
    }
    return null
  }
  
  // 尝试多种路径格式匹配
  const possiblePaths = [
    fullPath,                    // /workbench/routine/taskConfiguration
    relativePath,                // routine/taskConfiguration
    '/' + relativePath,          // /routine/taskConfiguration
    menu.component,              // 直接使用菜单的组件路径
    menu.path,                   // 直接使用菜单的路径
    // 对于跨目录组件，尝试从组件路径推断路由路径
    menu.component ? '/' + menu.component.replace('/index.vue', '').replace('/index', '') : null
  ]
  
  // 去重并过滤空值
  const uniquePaths = [...new Set(possiblePaths.filter(p => p && p.trim()))]
  
  // 依次尝试每个可能的路径
  for (const path of uniquePaths) {
    const registeredPath = findRouteByPath(registeredRoutes, path)
    if (registeredPath) {
      return registeredPath
    }
  }
  
  // 特殊处理：对于跨目录组件，尝试更精确的匹配
  if (menu.component && menu.component.includes('/')) {
    const componentBasedPaths = [
      '/' + menu.component.replace('/index.vue', '').replace('/index', ''),
      '/' + menu.component.split('/')[0] + '/' + menu.component.split('/')[1]
    ]
    
    for (const path of componentBasedPaths) {
      const registeredPath = findRouteByPath(registeredRoutes, path)
      if (registeredPath) {
        return registeredPath
      }
    }
  }
  
  // 如果都没找到，尝试动态注册路由
  if (menu.component && menu.component.trim()) {
    try {
      const dynamicRoute = {
        path: fullPath,
        component: Layout,
        hidden: true,
        children: [
          {
            path: '',
            component: loadView(menu.component.replace('.vue', '')),
            name: menu.menuName?.replace(/\s+/g, ''),
            meta: { 
              title: menu.menuName,
              icon: menu.icon || 'Menu',
              activeMenu: '/workbench'
            }
          }
        ]
      }
      
      // 检查路由是否已存在，避免重复注册
      const existingRoute = router.getRoutes().find(r => r.path === fullPath)
      if (!existingRoute) {
        router.addRoute(dynamicRoute)
        return fullPath
      }
    } catch (error) {
      // 静默失败
    }
  }
  
  // 如果都没找到，返回构建的完整路径（可能需要在后端配置）
  return fullPath
}

// 获取工作台菜单数据并转换为分类结构（基于菜单树，非路由）
const getWorkbenchMenus = async () => {
  try {
    // 同时获取菜单数据和已注册的路由数据
    const [menuResponse, routerResponse] = await Promise.all([
      listMenu(),
      getRouters()
    ])
    
    const allMenus = menuResponse.data
    const registeredRoutes = routerResponse.data

    // 查找工作台父级菜单（兼容是否带斜杠）
    const workbenchParent = allMenus.find(menu => menu.path === 'workbench' || menu.path === '/workbench')
    if (!workbenchParent) return

    // 1) 分类：父级为工作台且类型为目录(M)
    const categories = allMenus
      .filter(menu => 
        menu.parentId === workbenchParent.menuId &&
        menu.menuType === 'M' &&
        menu.status === '0'
      )
      .map(categoryMenu => ({
        id: categoryMenu.menuId,
        title: categoryMenu.menuName,
        orderNum: categoryMenu.orderNum || 0,
        children: []
      }))

    // 2) 功能：父级为分类且类型为菜单(C)
    const categoriesById = new Map(categories.map(c => [c.id, c]))
    allMenus.forEach(menu => {
      if (
        menu.menuType === 'C' &&
        menu.status === '0' &&
        categoriesById.has(menu.parentId)
      ) {
        const category = categoriesById.get(menu.parentId)
        // 从已注册的路由中查找匹配的路径
        const registeredPath = findRegisteredPath(menu, allMenus, registeredRoutes)
        
        category.children.push({
          title: menu.menuName,
          icon: menu.icon,
          path: registeredPath,
          orderNum: menu.orderNum || 0
        })
      }
    })

    // 排序
    categories.forEach(category => {
      category.children.sort((a, b) => a.orderNum - b.orderNum)
    })
    categories.sort((a, b) => a.orderNum - b.orderNum)

    // 过滤空分类并赋值
    workbenchCategories.value = categories.filter(c => c.children.length > 0)
  } catch (error) {
    // 静默失败，避免干扰页面
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