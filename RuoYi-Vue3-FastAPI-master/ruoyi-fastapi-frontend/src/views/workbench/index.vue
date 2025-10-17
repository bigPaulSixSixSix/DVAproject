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
      <el-row :gutter="20">
        <el-col 
          v-for="(item, index) in category.children" 
          :key="index" 
          :span="6"
          class="function-col"
        >
          <FunctionCard
            :title="item.title"
            :icon-name="item.icon || 'Menu'"
            :icon-color="getIconColor(index)"
            :path="item.path"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 占位功能区域（如果总功能数不足7个） -->
    <div v-if="placeholderCount > 0" class="function-section">
      <h3 class="section-title">分类名称</h3>
      <el-row :gutter="20">
        <el-col 
          v-for="n in placeholderCount" 
          :key="`placeholder-${n}`" 
          :span="6"
          class="function-col"
        >
          <FunctionCard
            title="功能名称"
            icon-name="Menu"
            icon-color="#909399"
            path="#"
          />
        </el-col>
      </el-row>
      <div class="no-more-text">没有更多啦</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import usePermissionStore from '@/store/modules/permission'
import AnnouncementCard from '@/components/Workbench/SummaryCard/AnnouncementCard.vue'
import TaskCard from '@/components/Workbench/SummaryCard/TaskCard.vue'
import TaskOverviewCard from '@/components/Workbench/SummaryCard/TaskOverviewCard.vue'
import FunctionCard from '@/components/Workbench/FunctionCard/index.vue'

defineOptions({
  name: 'Workbench'
})

const permissionStore = usePermissionStore()
const workbenchCategories = ref([])

// 获取工作台菜单数据并转换为分类结构
const getWorkbenchMenus = () => {
  const allRoutes = permissionStore.routes
  console.log('All routes:', allRoutes) // 调试用
  
  // 查找工作台父级菜单
  const workbenchParent = allRoutes.find(route => route.path === '/workbench')
  console.log('Workbench parent:', workbenchParent) // 调试用
  
  if (workbenchParent && workbenchParent.children) {
    // 过滤出工作台下的子菜单，排除工作台首页
    const workbenchChildren = workbenchParent.children.filter(child => 
      child.meta && child.meta.title && child.path !== '/workbench/index'
    )
    
    // 按菜单类型分组：目录类型作为分类，菜单类型作为功能
    const categories = []
    const categoryMap = new Map()
    
    workbenchChildren.forEach(child => {
      const menuType = child.meta.menuType || 'M' // 默认为菜单类型
      
      if (menuType === 'C') {
        // 目录类型 - 作为分类
        const category = {
          title: child.meta.title,
          orderNum: child.orderNum || 0,
          children: []
        }
        categoryMap.set(child.menuId, category)
        categories.push(category)
      } else if (menuType === 'M') {
        // 菜单类型 - 作为功能
        const parentId = child.parentId
        if (parentId && categoryMap.has(parentId)) {
          const category = categoryMap.get(parentId)
          category.children.push({
            title: child.meta.title,
            icon: child.meta.icon,
            path: child.path,
            orderNum: child.orderNum || 0
          })
        }
      }
    })
    
    // 排序：先按分类排序，再按功能排序
    categories.sort((a, b) => a.orderNum - b.orderNum)
    categories.forEach(category => {
      category.children.sort((a, b) => a.orderNum - b.orderNum)
    })
    
    // 过滤掉没有子功能的分类
    workbenchCategories.value = categories.filter(category => category.children.length > 0)
    
    console.log('Workbench categories:', workbenchCategories.value) // 调试用
  }
}

// 计算占位卡片数量（确保总功能数达到7个）
const placeholderCount = computed(() => {
  const totalFunctions = workbenchCategories.value.reduce((sum, category) => sum + category.children.length, 0)
  const targetCount = 7 // 目标功能数
  return Math.max(0, targetCount - totalFunctions)
})

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

.function-col {
  margin-bottom: 20px;
}

.no-more-text {
  text-align: center;
  color: var(--el-text-color-placeholder);
  font-size: 14px;
  margin-top: 20px;
  padding: 20px 0;
}
</style>