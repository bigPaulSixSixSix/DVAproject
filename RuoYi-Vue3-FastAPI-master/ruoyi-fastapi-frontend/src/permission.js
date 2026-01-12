import router from './router'
import { ElMessage } from 'element-plus'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { getToken, removeToken } from '@/utils/auth'
import { isHttp, isPathMatch } from '@/utils/validate'
import { isRelogin } from '@/utils/request'
import useUserStore from '@/store/modules/user'
import useSettingsStore from '@/store/modules/settings'
import usePermissionStore from '@/store/modules/permission'

NProgress.configure({ showSpinner: false })

const whiteList = ['/login', '/register']

const isWhiteList = (path) => {
  return whiteList.some(pattern => isPathMatch(pattern, path))
}

router.beforeEach((to, from, next) => {
  NProgress.start()
  if (getToken()) {
    to.meta.title && useSettingsStore().setTitle(to.meta.title)
    /* has token*/
    if (to.path === '/login') {
      // 如果有 token 但访问登录页，检查是否有角色
      // 如果没有角色，说明 token 无效，清除后允许访问登录页
      if (useUserStore().roles.length === 0) {
        // 清除无效的 token
        useUserStore().token = ''
        useUserStore().roles = []
        useUserStore().permissions = []
        removeToken()
        next()
        NProgress.done()
      } else {
        // 有角色，跳转到工作台
      next({ path: '/workbench' })
      NProgress.done()
      }
    } else if (isWhiteList(to.path)) {
      next()
    } else {
      if (useUserStore().roles.length === 0) {
        isRelogin.show = true
        // 判断当前用户是否已拉取完user_info信息
        useUserStore().getInfo().then(() => {
          isRelogin.show = false
          usePermissionStore().generateRoutes().then(accessRoutes => {
            // 根据roles权限生成可访问的路由表
            accessRoutes.forEach(route => {
              if (!isHttp(route.path)) {
                router.addRoute(route) // 动态添加可访问路由表
              }
            })
            next({ ...to, replace: true }) // hack方法 确保addRoutes已完成
          }).catch(err => {
            // generateRoutes 失败，可能是权限不足
            isRelogin.show = false
            // 立即清除 token，避免死循环
            useUserStore().token = ''
            useUserStore().roles = []
            useUserStore().permissions = []
            removeToken()
            // 显示错误信息
            const errorMsg = err?.response?.data?.msg || err?.message || err || '获取路由信息失败，请重新登录'
            ElMessage.error(errorMsg)
            // 跳转到登录页
            next(`/login?redirect=${to.fullPath}`)
            NProgress.done()
          })
        }).catch(err => {
          isRelogin.show = false
          // 立即清除 token，避免死循环
          useUserStore().token = ''
          useUserStore().roles = []
          useUserStore().permissions = []
          removeToken()
          // 显示错误信息
          const errorMsg = err?.response?.data?.msg || err?.message || err || '获取用户信息失败，请重新登录'
          ElMessage.error(errorMsg)
          // 跳转到登录页
          next(`/login?redirect=${to.fullPath}`)
          NProgress.done()
        })
      } else {
        next()
      }
    }
  } else {
    // 没有token
    if (isWhiteList(to.path)) {
      // 在免登录白名单，直接进入
      next()
    } else {
      next(`/login?redirect=${to.fullPath}`) // 否则全部重定向到登录页
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})
