import auth from '@/plugins/auth'
import router, { constantRoutes, dynamicRoutes } from '@/router'
import { getRouters } from '@/api/menu'
import Layout from '@/layout/index'
import ParentView from '@/components/ParentView'
import InnerLink from '@/layout/components/InnerLink'
import { isHttp } from '@/utils/validate'

// 匹配views里面所有的.vue文件
const modules = import.meta.glob('./../../views/**/*.vue')

// 工具函数：检查是否是工作台主页面路由
const isWorkbenchMainRoute = (route) => {
  return (route.path === 'workbench' || route.path === '/workbench') &&
         (route.meta && route.meta.title === '工作台')
}

// 工具函数：移除工作台路由的 children 和 alwaysShow
const removeWorkbenchChildren = (route) => {
  if (isWorkbenchMainRoute(route)) {
    const newRoute = { ...route }
    delete newRoute.children
    delete newRoute.alwaysShow
    return newRoute
  }
  return route
}

const usePermissionStore = defineStore(
  'permission',
  {
    state: () => ({
      routes: [],
      addRoutes: [],
      defaultRoutes: [],
      topbarRouters: [],
      sidebarRouters: [],
      routersData: null // 缓存 getRouters 的原始数据
    }),
    actions: {
      setRoutes(routes) {
        this.addRoutes = routes
        this.routes = constantRoutes.concat(routes)
      },
      setDefaultRoutes(routes) {
        this.defaultRoutes = constantRoutes.concat(routes)
      },
      setTopbarRoutes(routes) {
        this.topbarRouters = routes
      },
      setSidebarRouters(routes) {
        this.sidebarRouters = routes
      },
      generateRoutes(roles) {
        return new Promise((resolve, reject) => {
          // 先获取路由数据（必需）
          // 如果已经有缓存的数据，直接使用；否则请求并缓存
          const fetchRouters = this.routersData 
            ? Promise.resolve({ data: this.routersData })
            : getRouters().then(res => {
                // 缓存原始数据
                this.routersData = res.data
                return res
              })
          
          fetchRouters.then(res => {
            const sdata = JSON.parse(JSON.stringify(res.data))
            const rdata = JSON.parse(JSON.stringify(res.data))
            const defaultData = JSON.parse(JSON.stringify(res.data))
            
            // 处理侧边栏路由：只保留工作台主页面，移除子菜单
            const processSidebarRoutes = (routes) => {
              return routes.map(route => {
                if (route.path === '/' && route.children) {
                  // 找到工作台主页面路由
                  const workbenchMainRoute = route.children.find(child => 
                    isWorkbenchMainRoute(child) && child.component === 'workbench/index'
                  )
                  if (workbenchMainRoute) {
                    // 只保留工作台主页面路由，移除其他子菜单路由
                    return { ...route, children: [removeWorkbenchChildren(workbenchMainRoute)] }
                  }
                }
                if (route.children && route.children.length > 0) {
                  return { ...route, children: processSidebarRoutes(route.children) }
                }
                return route
              })
            }
            
            const processedSdata = processSidebarRoutes(sdata)
            const processedDefaultData = processSidebarRoutes(defaultData)
            
            let sidebarRoutes = filterAsyncRouter(processedSdata)
            const rewriteRoutes = filterAsyncRouter(rdata, false, true)
            let defaultRoutes = filterAsyncRouter(processedDefaultData)
            const asyncRoutes = filterDynamicRoutes(dynamicRoutes)
            
            // 确保工作台路由的 children 被移除（递归处理所有层级）
            const ensureWorkbenchNoChildren = (routes) => {
              if (!routes || !Array.isArray(routes)) return routes
              return routes.map(route => {
                const newRoute = removeWorkbenchChildren(route)
                if (newRoute.path === '/' && newRoute.children) {
                  newRoute.children = newRoute.children.map(child => removeWorkbenchChildren(child))
                }
                if (newRoute.children && newRoute.children.length > 0) {
                  newRoute.children = ensureWorkbenchNoChildren(newRoute.children)
                }
                return newRoute
              })
            }
            
            sidebarRoutes = ensureWorkbenchNoChildren(sidebarRoutes)
            defaultRoutes = ensureWorkbenchNoChildren(defaultRoutes)
            
            asyncRoutes.forEach(route => { router.addRoute(route) })
            
            // 注册 rewriteRoutes 到路由器
            const registerRoute = (route) => {
              if (route.path && !isHttp(route.path)) {
                router.addRoute(route)
              }
            }
            
            rewriteRoutes.forEach(route => registerRoute(route))
            
            // 注册工作台子路由（任务配置等特殊路由）
            // 注意：必须在 rewriteRoutes 注册后再注册，确保父路由已存在
            registerWorkbenchSubRoutes([])
            
            this.setRoutes(rewriteRoutes)
            this.setSidebarRouters(constantRoutes.concat(sidebarRoutes))
            this.setDefaultRoutes(defaultRoutes)
            this.setTopbarRoutes(defaultRoutes)
            resolve(rewriteRoutes)
          }).catch(error => {
            // 捕获错误并传递给调用者
            reject(error)
          })
        })
      }
    }
  })

// 遍历后台传来的路由字符串，转换为组件对象
function filterAsyncRouter(asyncRouterMap, lastRouter = false, type = false) {
  return asyncRouterMap.filter(route => {
    // 侧边栏路由：移除工作台路由的 children
    if (!type && isWorkbenchMainRoute(route)) {
      route.children = undefined
      route.alwaysShow = undefined
    }
    
    // 任务配置菜单项：确保路径正确（移除参数部分）
    // 后端返回的 path 通常是正确的，但为了安全起见，这里做一次清理
    if (route.component && typeof route.component === 'string' && 
        route.component.includes('task-configuration/project-list') &&
        route.path && route.path.includes('task-configuration')) {
      route.path = route.path.replace(/\/:projectId.*$/, '').replace(/\/\d+$/, '')
      if (!route.path.endsWith('task-configuration')) {
        route.path = '/workbench/routine/task-configuration'
      }
    }
    
    // 注意：filterChildren 应该在递归处理完所有 children 后再调用，而不是在这里
    // 因为 filterChildren 需要处理 ParentView 的展开，这需要在所有 children 都处理完后进行
    if (route.component) {
      // Layout ParentView 组件特殊处理
      if (route.component === 'Layout') {
        // 特殊处理：如果 component 是 Layout 但没有 children，说明这是一个空菜单
        // 但是我们不能直接将 component 改为空页面组件，因为这样会破坏路由嵌套结构
        // 应该在 filterChildren 中处理，或者保持 Layout 但添加一个空的 children
        // 实际上，这种情况应该在 filterChildren 中处理，将空菜单项展开为实际路由
        if (!route.children || route.children.length === 0) {
          // 标记这是一个空菜单项，稍后在 filterChildren 中处理
          route._isEmptyMenu = true
        }
        route.component = Layout
      } else if (route.component === 'ParentView') {
        route.component = ParentView
      } else if (route.component === 'InnerLink') {
        route.component = InnerLink
      } else {
        route.component = loadView(route.component)
      }
    }
    if (route.children != null && route.children && route.children.length) {
      // 递归处理 children，在递归中也会检查工作台路由
      route.children = filterAsyncRouter(route.children, route, type)
      
      // 如果 type=true，使用 filterChildren 展开 ParentView 的 children 并处理空菜单项
      // 注意：filterChildren 需要在递归处理完所有 children 后调用，以便正确处理嵌套结构
      if (type && route.children) {
        // 判断是否是根级别的路由（"/" 路由）
        const isRootLevel = route.path === '/' || route.path === ''
        route.children = filterChildren(route.children, route, isRootLevel)
      }
      
      // 递归后再次检查：如果 children 中有工作台路由，移除其 children
      if (!type && route.children) {
        route.children = route.children.map(child => removeWorkbenchChildren(child))
      }
    } else {
      // 如果没有 children，检查是否是空菜单项（在 type=true 时处理）
      if (type && route._isEmptyMenu) {
        route.component = () => import('@/views/error/EmptyPage.vue')
        delete route._isEmptyMenu
      }
      delete route['children']
      delete route['redirect']
    }
    return true
  })
}

function filterChildren(childrenMap, lastRouter = false, isRootLevel = false) {
  var children = []
  childrenMap.forEach(el => {
    // 保存原始路径，用于后续判断
    const originalPath = el.path || ''
    
    // 路径拼接：如果 lastRouter 存在，需要拼接路径
    // 注意：需要处理相对路径和绝对路径的情况
    if (lastRouter) {
      const lastPath = lastRouter.path || ''
      const currentPath = el.path || ''
      
      // 如果 currentPath 已经是绝对路径（以 / 开头），直接使用
      // 否则，拼接 lastPath 和 currentPath
      if (currentPath.startsWith('/')) {
        el.path = currentPath
      } else {
        // 确保路径拼接正确，避免双斜杠
        const basePath = lastPath.endsWith('/') ? lastPath.slice(0, -1) : lastPath
        el.path = basePath ? `${basePath}/${currentPath}` : currentPath
      }
    }
    
    // 检查是否是 ParentView 组件（可能是字符串 'ParentView' 或组件对象）
    const isParentView = el.component === 'ParentView' || 
                        el.component === ParentView ||
                        (typeof el.component === 'function' && el.component.name === 'ParentView')
    
    if (el.children && el.children.length && isParentView) {
      // 展开 ParentView 的 children
      // 注意：对于 "/" 路由下的 ParentView（如 routine、asset），需要确保路径以 /workbench 开头
      // 但是，在递归调用 filterChildren 时，不要传递 el 作为 lastRouter，因为我们需要手动构建路径
      const expandedChildren = filterChildren(el.children, false, false)
      
      // 特殊处理：如果是根级别的 ParentView（即 "/" 路由下的 ParentView），其 children 的路径应该以 /workbench 开头
      if (isRootLevel) {
        expandedChildren.forEach(child => {
          // 获取 child 的原始路径（在 filterChildren 中可能已经被修改）
          const childOriginalPath = child.path || ''
          // 构建正确的路径：/workbench/{parentPath}/{childPath}
          // 例如：/workbench/asset/2
          const childPath = childOriginalPath.startsWith('/') ? childOriginalPath.slice(1) : childOriginalPath
          // 检查 childPath 是否已经包含了 originalPath（如 asset）
          // 如果 childPath 是 "asset/2"，说明已经包含了，只需要添加 /workbench 前缀
          // 如果 childPath 是 "2"，说明不包含，需要添加 originalPath
          if (childPath.startsWith(originalPath + '/') || childPath === originalPath) {
            // 路径已经包含了 parent 路径，直接添加 /workbench 前缀
            child.path = `/workbench/${childPath}`
          } else {
            // 路径不包含 parent 路径，需要添加 parent 路径
            child.path = `/workbench/${originalPath}/${childPath}`
          }
          
          // 统一处理：移除路径中的重复段和双斜杠
          if (child.path) {
            const pathParts = child.path.split('/').filter(p => p)
            // 移除连续重复的路径段
            const uniquePathParts = []
            for (let i = 0; i < pathParts.length; i++) {
              if (i === 0 || pathParts[i] !== pathParts[i - 1]) {
                uniquePathParts.push(pathParts[i])
              }
            }
            child.path = '/' + uniquePathParts.join('/')
          }
        })
      }
      
      children = children.concat(expandedChildren)
    } else {
      // 特殊处理：如果是空菜单项（Layout 但没有 children），将其转换为空页面路由
      // 注意：此时 el.component 可能已经被转换为 Layout 组件对象，需要检查字符串或组件对象
      const isLayoutComponent = el.component === 'Layout' || 
                                el.component === Layout || 
                                (typeof el.component === 'function' && el.component.name === 'Layout')
      const isEmptyMenu = el._isEmptyMenu || (isLayoutComponent && (!el.children || el.children.length === 0))
      
      if (isEmptyMenu) {
        // 将空菜单项转换为空页面组件，但保持路由结构
        el.component = () => import('@/views/error/EmptyPage.vue')
        delete el._isEmptyMenu
        // 确保没有 children，避免路由嵌套问题
        delete el.children
        delete el.redirect
        // 空菜单项已转换为 EmptyPage 组件
      }
      children.push(el)
    }
  })
  return children
}

// 动态路由遍历，验证是否具备权限
export function filterDynamicRoutes(routes) {
  const res = []
  routes.forEach(route => {
    if (route.permissions) {
      if (auth.hasPermiOr(route.permissions)) {
        res.push(route)
      }
    } else if (route.roles) {
      if (auth.hasRoleOr(route.roles)) {
        res.push(route)
      }
    } else {
      // 没有权限限制的路由直接添加（如工作台）
      res.push(route)
    }
  })
  return res
}

export const loadView = (view) => {
  let res;
  for (const path in modules) {
    const dir = path.split('views/')[1].split('.vue')[0];
    if (dir === view) {
      res = () => modules[path]();
    }
  }
  return res
}

// 工具函数：检查路由是否已存在（支持嵌套路由和参数路由）
const checkRouteExists = (targetPath) => {
    const allRoutes = router.getRoutes()
    for (const route of allRoutes) {
      // 检查路由路径是否匹配（支持参数路由）
      if (route.path === targetPath) {
        return true
      }
      // 检查参数路由匹配（例如 /workbench/routine/task-configuration/:projectId 匹配 /workbench/routine/task-configuration/1）
      if (route.path.includes(':') && targetPath.includes('/')) {
        const routePattern = route.path.replace(/:[^/]+/g, '[^/]+')
        const regex = new RegExp(`^${routePattern}$`)
        if (regex.test(targetPath)) {
          return true
        }
      }
      // 检查嵌套路由
      if (route.children) {
        for (const child of route.children) {
          // 构建完整路径
          let fullPath
          if (route.path === '/') {
            fullPath = `/${child.path}`
          } else if (child.path === '') {
            fullPath = route.path
          } else {
            fullPath = `${route.path}/${child.path}`
          }
          // 检查精确匹配
          if (fullPath === targetPath) {
            return true
          }
          // 检查参数路由匹配
          if (fullPath.includes(':') && targetPath.includes('/')) {
            const routePattern = fullPath.replace(/:[^/]+/g, '[^/]+')
            const regex = new RegExp(`^${routePattern}$`)
            if (regex.test(targetPath)) {
              return true
            }
          }
        }
      }
    }
    return false
}

// 自动注册 workbench 的所有子路由（从文件系统）
function registerWorkbenchSubRoutes(allMenus) {
  // 任务配置的特殊路由结构：
  // 1. 项目列表页: /workbench/routine/task-configuration
  // 2. 任务配置页: /workbench/routine/task-configuration/:projectId
  const taskConfigDir = 'workbench/routine/task-configuration'
  const taskConfigRoutePath = '/workbench/routine/task-configuration'
  
  const existingProjectListRoute = checkRouteExists(taskConfigRoutePath)
  const existingDetailRoute = checkRouteExists(taskConfigRoutePath + '/:projectId')
  
  // 如果项目列表页路由不存在，注册它
  if (!existingProjectListRoute) {
    // 查找对应的菜单名称
    let menuTitle = '任务配置'
    const menu = allMenus.find(m => {
      const componentPath = taskConfigDir + '/index'
      return m.component === componentPath || m.path === taskConfigRoutePath
    })
    if (menu) {
      menuTitle = menu.menuName
    }
    
    // 先注册项目列表页路由（不带参数的路由必须先注册，避免被带参数的路由匹配）
    // 注意：Vue Router 会按照注册顺序匹配路由，更具体的路由（带参数）应该后注册
    const projectListRoute = {
      path: taskConfigRoutePath,
      component: Layout,
      hidden: true,
      children: [{
        path: '',
        component: loadView(taskConfigDir + '/project-list'),
        name: 'ProjectList',
        meta: { 
          title: '任务配置-项目列表',
          activeMenu: '/workbench'
        }
      }]
    }
    router.addRoute(projectListRoute)
  }
    
  // 如果任务配置详情页路由不存在，注册它
  if (!existingDetailRoute) {
    const taskConfigDetailRoute = {
      path: taskConfigRoutePath + '/:projectId',
      component: Layout,
      hidden: true,
      children: [{
        path: '',
        component: loadView(taskConfigDir + '/index'),
        name: 'TaskConfiguration',
        meta: { 
          title: '项目编辑', // 会在组件中动态更新为"项目编辑-项目名"
          activeMenu: '/workbench'
        }
      }]
    }
    router.addRoute(taskConfigDetailRoute)
  }
  
  // 注册其他 workbench 子路由
  for (const path in modules) {
    if (path.includes('/workbench/') && path.endsWith('/index.vue') && path !== '../../views/workbench/index.vue') {
      let dir = path.split('views/')[1].split('.vue')[0]
      // 移除末尾的 '/index'，因为路径不需要它
      if (dir.endsWith('/index')) {
        dir = dir.substring(0, dir.length - 6) // 6 = '/index'.length
      }
      const routePath = '/' + dir.replace(/\\/g, '/')
      
      // 跳过任务配置，因为已经特殊处理了
      if (dir === taskConfigDir) {
        continue
      }
      
      // 检查路由是否已存在
      const existingRoute = router.getRoutes().find(r => r.path === routePath)
      if (!existingRoute) {
        // 查找对应的菜单名称
        let menuTitle = dir.split('/').pop()
        const menu = allMenus.find(m => {
          // 匹配组件路径，例如：workbench/routine/task-configuration/index
          const componentPath = dir + '/index'
          return m.component === componentPath || m.path === routePath
        })
        if (menu) {
          menuTitle = menu.menuName
        } else {
          // 为固定路由设置标题（不在菜单管理中配置的路由）
          if (dir === 'workbench/todo') {
            menuTitle = '我的任务'
          } else if (dir === 'workbench/todo-history') {
            menuTitle = '历史任务'
          }
        }
        
        const subRoute = {
          path: routePath,
          component: Layout,
          hidden: true,
          children: [{
            path: '',
            component: loadView(dir + '/index'),
            name: dir.split('/').pop().replace(/[^a-zA-Z0-9]/g, ''),
            meta: { 
              title: menuTitle,
              activeMenu: '/workbench'
            }
          }]
        }
        
        router.addRoute(subRoute)
      }
    }
  }
}

export default usePermissionStore
