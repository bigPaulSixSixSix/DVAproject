"""
任务执行控制器
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_admin.aspect.interface_auth import CheckWorkbenchMenuAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_task.todo.service.todo_service import TodoService
from module_task.todo.service.todo_query_service import TodoQueryService
from module_task.entity.vo.task_vo import SubmitTaskModel, ApproveTaskModel, RejectTaskModel, WorkbenchTaskStatsModel
from module_apply.service.approval_engine import ApprovalEngine
from module_apply.service.apply_service import ApplyService
from module_apply.service.approval_service import ApprovalService
from exceptions.exception import ServiceException
from utils.log_util import logger
from utils.response_util import ResponseUtil


todoController = APIRouter(prefix='/todo', dependencies=[Depends(LoginService.get_current_user)])


@todoController.post('/generate/{project_id}', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def generate_tasks(
    project_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    生成任务（从项目配置生成任务执行记录）
    
    :param project_id: 项目ID
    :param query_db: orm对象
    :param current_user: 当前用户
    """
    try:
        await TodoService.generate_tasks_from_project(query_db, project_id)
        await query_db.commit()
        return ResponseUtil.success(msg='任务生成成功')
    except ServiceException as e:
        await query_db.rollback()
        return ResponseUtil.failure(msg=e.message)
    except Exception as e:
        logger.error(f'任务生成异常: {str(e)}', exc_info=True)
        await query_db.rollback()
        return ResponseUtil.error(msg=f'任务生成失败：{str(e)}')


@todoController.post('/submit/{task_id}', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def submit_task(
    task_id: int,
    body: SubmitTaskModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    提交任务
    
    :param task_id: 任务ID（关联proj_task.task_id）
    :param body: 提交任务请求体
    :param query_db: orm对象
    :param current_user: 当前用户
    """
    try:
        apply_id = await TodoService.submit_task(
            query_db=query_db,
            task_id=task_id,
            submitter_id=current_user.user.user_name,
            submit_text=body.submitText,
            submit_images=body.submitImages
        )
        await query_db.commit()
        return ResponseUtil.success(msg='任务提交成功', data={'apply_id': apply_id})
    except ServiceException as e:
        await query_db.rollback()
        return ResponseUtil.failure(msg=e.message)
    except Exception as e:
        logger.error(f'任务提交异常: {str(e)}', exc_info=True)
        await query_db.rollback()
        return ResponseUtil.error(msg=f'任务提交失败：{str(e)}')


@todoController.post('/approve/{apply_id}', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def approve_task(
    apply_id: str,
    body: ApproveTaskModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    审批同意
    
    :param apply_id: 申请单ID
    :param body: 审批同意请求体
    :param query_db: orm对象
    :param current_user: 当前用户
    """
    try:
        # 设置回调函数
        callback = TodoService.handle_task_approved
        
        is_completed = await ApprovalEngine.approve(
            query_db=query_db,
            apply_id=apply_id,
            approver_id=current_user.user.user_name,
            approval_comment=body.approvalComment,
            approval_images=body.approvalImages,
            callback=callback
        )
        
        await query_db.commit()
        return ResponseUtil.success(
            msg='审批成功',
            data={'is_completed': is_completed}
        )
    except ServiceException as e:
        await query_db.rollback()
        return ResponseUtil.failure(msg=e.message)
    except Exception as e:
        logger.error(f'审批异常: {str(e)}', exc_info=True)
        await query_db.rollback()
        return ResponseUtil.error(msg=f'审批失败：{str(e)}')


@todoController.post('/reject/{apply_id}', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def reject_task(
    apply_id: str,
    body: RejectTaskModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    审批驳回
    
    :param apply_id: 申请单ID
    :param body: 审批驳回请求体
    :param query_db: orm对象
    :param current_user: 当前用户
    """
    try:
        # 设置回调函数
        callback = TodoService.handle_task_rejected
        
        await ApprovalEngine.reject(
            query_db=query_db,
            apply_id=apply_id,
            approver_id=current_user.user.user_name,
            approval_comment=body.approvalComment,
            approval_images=body.approvalImages,
            callback=callback
        )
        
        await query_db.commit()
        return ResponseUtil.success(msg='审批驳回成功')
    except ServiceException as e:
        await query_db.rollback()
        return ResponseUtil.failure(msg=e.message)
    except Exception as e:
        logger.error(f'审批驳回异常: {str(e)}', exc_info=True)
        await query_db.rollback()
        return ResponseUtil.error(msg=f'审批驳回失败：{str(e)}')


@todoController.post('/resubmit/{task_id}', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def resubmit_task(
    task_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    重新提交任务（被驳回后重新提交）
    功能：将被驳回的任务重置为进行中状态，用户可以在我的任务页面看到该任务，然后填写内容并提交
    
    :param task_id: 任务ID（关联proj_task.task_id）
    :param query_db: orm对象
    :param current_user: 当前用户
    """
    try:
        from module_task.todo.dao.todo_task_dao import TodoTaskDao
        from module_task.entity.do.todo_task_do import TodoTask
        from sqlalchemy import select
        
        # 1. 验证任务是否存在且状态为驳回
        todo_task_result = await query_db.execute(
            select(TodoTask).where(TodoTask.task_id == task_id)
        )
        todo_task = todo_task_result.scalar_one_or_none()
        
        if not todo_task:
            return ResponseUtil.failure(msg=f'任务不存在: task_id={task_id}')
        
        if todo_task.task_status != 4:  # 必须是驳回状态
            return ResponseUtil.failure(msg=f'任务状态不正确，无法重新提交。当前状态: {todo_task.task_status}，只有驳回状态的任务才能重新提交')
        
        # 2. 验证是否是任务负责人
        if todo_task.job_number != current_user.user.user_name:
            return ResponseUtil.failure(msg='只有任务负责人才能重新提交任务')
        
        # 3. 更新任务状态为进行中（不更新实际开始时间）
        # 旧申请单保持驳回状态即可，不需要额外操作
        await TodoTaskDao.update_task_status(query_db, task_id, 1)  # 1-进行中
        
        await query_db.commit()
        logger.info(f'任务重新提交成功: task_id={task_id}，任务状态已重置为进行中')
        return ResponseUtil.success(msg='任务已重置为进行中状态，请在我的任务页面查看并提交')
    except ServiceException as e:
        await query_db.rollback()
        return ResponseUtil.failure(msg=e.message)
    except Exception as e:
        logger.error(f'任务重新提交异常: {str(e)}', exc_info=True)
        await query_db.rollback()
        return ResponseUtil.error(msg=f'任务重新提交失败：{str(e)}')


@todoController.get('/my/tasks/categories', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_my_tasks_categories(
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    获取我的任务分类统计
    
    :param query_db: orm对象
    :param current_user: 当前用户
    :return: 分类统计数据
    """
    try:
        job_number = current_user.user.user_name
        data = await TodoQueryService.get_my_tasks_categories(query_db, job_number)
        return ResponseUtil.success(data=data)
    except Exception as e:
        logger.error(f'获取任务分类统计异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'获取任务分类统计失败：{str(e)}')


@todoController.get('/my/tasks/list', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_my_tasks_list(
    project_id: Optional[int] = Query(None, alias='projectId', description='项目ID'),
    dept_id: Optional[int] = Query(None, alias='deptId', description='部门ID（第二级部门）'),
    task_status: Optional[int] = Query(None, alias='taskStatus', description='任务状态（1-待提交，2-审批中，4-驳回）'),
    page_num: Optional[int] = Query(1, alias='pageNum', description='页码（可选，如果pageSize为0或未提供，则不分页）'),
    page_size: Optional[int] = Query(0, alias='pageSize', description='每页数量（0表示不分页，返回所有数据）'),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    获取我的任务列表
    
    :param project_id: 项目ID（可选）
    :param dept_id: 部门ID（可选，第二级部门）
    :param task_status: 任务状态（可选）
    :param page_num: 页码
    :param page_size: 每页数量
    :param query_db: orm对象
    :param current_user: 当前用户
    :return: 任务列表数据
    """
    try:
        job_number = current_user.user.user_name
        data = await TodoQueryService.get_my_tasks_list(
            query_db, job_number, project_id, dept_id, task_status, page_num, page_size
        )
        return ResponseUtil.success(data=data)
    except Exception as e:
        logger.error(f'获取任务列表异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'获取任务列表失败：{str(e)}')


@todoController.get('/history/tasks/list', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_history_tasks_list(
    project_id: Optional[int] = Query(None, alias='projectId', description='项目ID'),
    dept_id: Optional[int] = Query(None, alias='deptId', description='部门ID（第二级部门）'),
    page_num: Optional[int] = Query(1, alias='pageNum', description='页码（可选，如果pageSize为0或未提供，则不分页）'),
    page_size: Optional[int] = Query(0, alias='pageSize', description='每页数量（0表示不分页，返回所有数据）'),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    获取历史任务列表（已完成任务）
    
    :param project_id: 项目ID（可选）
    :param dept_id: 部门ID（可选，第二级部门）
    :param page_num: 页码
    :param page_size: 每页数量
    :param query_db: orm对象
    :param current_user: 当前用户
    :return: 已完成任务列表数据
    """
    try:
        job_number = current_user.user.user_name
        data = await TodoQueryService.get_completed_tasks_list(
            query_db, job_number, project_id, dept_id, page_num, page_size
        )
        return ResponseUtil.success(data=data)
    except Exception as e:
        logger.error(f'获取历史任务列表异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'获取历史任务列表失败：{str(e)}')


@todoController.get('/history/tasks/categories', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_history_tasks_categories(
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    获取历史任务分类统计
    
    :param query_db: orm对象
    :param current_user: 当前用户
    :return: 分类统计数据
    """
    try:
        job_number = current_user.user.user_name
        data = await TodoQueryService.get_completed_tasks_categories(query_db, job_number)
        return ResponseUtil.success(data=data)
    except Exception as e:
        logger.error(f'获取历史任务分类统计异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'获取历史任务分类统计失败：{str(e)}')


@todoController.get('/task/{task_id}/detail', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_task_detail(
    task_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    获取任务详情
    
    :param task_id: 任务ID（关联proj_task.task_id）
    :param query_db: orm对象
    :param current_user: 当前用户
    :return: 任务详情数据
    """
    try:
        job_number = current_user.user.user_name
        data = await TodoQueryService.get_task_detail(query_db, task_id, job_number)
        if not data:
            return ResponseUtil.failure(msg='任务不存在')
        return ResponseUtil.success(data=data)
    except Exception as e:
        logger.error(f'获取任务详情异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'获取任务详情失败：{str(e)}')


@todoController.get('/task/{task_id}/detail/simple', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_task_detail_simple(
    task_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    获取其他任务详情（用于弹窗）
    
    :param task_id: 任务ID（关联proj_task.task_id）
    :param query_db: orm对象
    :param current_user: 当前用户
    :return: 任务详情数据（简化版）
    """
    try:
        job_number = current_user.user.user_name
        data = await TodoQueryService.get_task_detail(query_db, task_id, job_number)
        if not data:
            return ResponseUtil.failure(msg='任务不存在')
        
        # 简化返回数据，添加审批结果列表
        # 移除权限标识字段
        simple_data = {
            'taskInfo': data.get('taskInfo'),
            'approvalFlow': data.get('approvalFlow'),
            'submitContent': data.get('submitContent'),
        }
        
        # 添加审批结果列表
        approval_results = []
        if data.get('approvalFlow') and data.get('approvalFlow').get('approvalNodes'):
            for node in data['approvalFlow']['approvalNodes']:
                if node.get('status') == 'approved':
                    approval_results.append({
                        'nodeIndex': node.get('nodeIndex'),
                        'postName': node.get('postName'),
                        'approverName': node.get('approverName'),
                        'approvalTime': node.get('approvalTime'),
                        'approvalComment': node.get('approvalComment'),
                        'approvalImages': [],  # 暂时返回空数组
                    })
        
        simple_data['approvalResults'] = approval_results
        
        return ResponseUtil.success(data=simple_data)
    except Exception as e:
        logger.error(f'获取任务详情（简化）异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'获取任务详情失败：{str(e)}')


@todoController.get('/workbench/stats', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_workbench_task_stats(
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    获取工作台任务统计数据
    
    :param query_db: orm对象
    :param current_user: 当前用户
    :return: 任务统计数据
    """
    try:
        job_number = current_user.user.user_name
        data = await TodoQueryService.get_workbench_task_stats(query_db, job_number)
        return ResponseUtil.success(data=data)
    except Exception as e:
        logger.error(f'获取工作台任务统计异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'获取工作台任务统计失败：{str(e)}')


