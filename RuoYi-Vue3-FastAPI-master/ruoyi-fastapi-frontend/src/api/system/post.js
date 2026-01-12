import request from '@/utils/request'

// 查询岗位列表
export function listPost(query) {
  return request({
    url: '/system/post/list',
    method: 'get',
    params: query
  })
}

// 查询岗位详细（保留，但前端不需要添加查看明细功能）
export function getPost(postId) {
  return request({
    url: '/system/post/' + postId,
    method: 'get'
  })
}
