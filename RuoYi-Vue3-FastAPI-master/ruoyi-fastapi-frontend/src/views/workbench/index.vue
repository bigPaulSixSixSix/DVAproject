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
import AnnouncementCard from '@/components/Workbench/SummaryCard/AnnouncementCard.vue'
import TaskCard from '@/components/Workbench/SummaryCard/TaskCard.vue'
import TaskOverviewCard from '@/components/Workbench/SummaryCard/TaskOverviewCard.vue'
import FunctionCard from '@/components/Workbench/FunctionCard/index.vue'

defineOptions({
  name: 'Workbench'
})

const workbenchCategories = ref([])

// 获取工作台菜单数据并转换为分类结构（基于菜单树，非路由）
const getWorkbenchMenus = async () => {
  try {
    const response = await listMenu()
    const allMenus = response.data

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
        category.children.push({
          title: menu.menuName,
          icon: menu.icon,
          path: menu.path,
          orderNum: menu.orderNum || 0
        })
        console.log('Added function:', menu.menuName, 'icon:', menu.icon)
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