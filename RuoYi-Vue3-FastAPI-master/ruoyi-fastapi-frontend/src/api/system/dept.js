import request from '@/utils/request'

// 查询部门列表
// 注意：此API应该应用数据权限过滤，如果后端没有实现，需要后端修复
export function listDept(query) {
  return request({
    url: '/system/dept/list',
    method: 'get',
    params: query
  })
}

// 查询部门树（带数据权限过滤）
// 使用与用户管理页面相同的API，确保数据权限正确应用
export function deptTreeSelect() {
  return request({
    url: '/system/user/deptTree',
    method: 'get'
  })
}
