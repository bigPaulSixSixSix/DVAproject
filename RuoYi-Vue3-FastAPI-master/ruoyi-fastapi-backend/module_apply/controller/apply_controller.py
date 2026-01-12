"""
通用申请/审批控制器
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.get_db import get_db
from module_admin.aspect.interface_auth import CheckWorkbenchMenuAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_apply.service.apply_service import ApplyService
from module_apply.service.approval_service import ApprovalService
from module_apply.dao.approval_log_dao import ApprovalLogDao
from exceptions.exception import ServiceException
from utils.log_util import logger
from utils.response_util import ResponseUtil
import json


applyController = APIRouter(prefix='/apply', dependencies=[Depends(LoginService.get_current_user)])


@applyController.get('/{apply_id}', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_apply_detail(
    apply_id: str,
    query_db: AsyncSession = Depends(get_db),
):
    """
    查询申请单详情
    
    :param apply_id: 申请单ID
    :param query_db: orm对象
    """
    try:
        apply = await ApplyService.get_apply_by_id(query_db, apply_id)
        if not apply:
            return ResponseUtil.failure(msg='申请单不存在')
        
        return ResponseUtil.success(data={
            'id': apply.id,
            'applyType': apply.apply_type,
            'applyId': apply.apply_id,
            'applyStatus': apply.apply_status,
            'createTime': apply.create_time,
            'updateTime': apply.update_time,
        })
    except Exception as e:
        logger.error(f'查询申请单详情异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'查询申请单详情失败：{str(e)}')


@applyController.get('/{apply_id}/approval/rules', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_approval_rules(
    apply_id: str,
    query_db: AsyncSession = Depends(get_db),
):
    """
    查询审批规则
    
    :param apply_id: 申请单ID
    :param query_db: orm对象
    """
    try:
        rules = await ApprovalService.get_approval_rules(query_db, apply_id)
        if not rules:
            return ResponseUtil.failure(msg='审批规则不存在')
        
        approval_nodes = []
        approved_nodes = []
        
        if rules.approval_nodes:
            try:
                approval_nodes = json.loads(rules.approval_nodes) if isinstance(rules.approval_nodes, str) else rules.approval_nodes
            except (json.JSONDecodeError, TypeError):
                approval_nodes = []
        
        if rules.approved_nodes:
            try:
                approved_nodes = json.loads(rules.approved_nodes) if isinstance(rules.approved_nodes, str) else rules.approved_nodes
            except (json.JSONDecodeError, TypeError):
                approved_nodes = []
        
        return ResponseUtil.success(data={
            'id': rules.id,
            'applyId': rules.apply_id,
            'approvalNodes': approval_nodes,
            'approvedNodes': approved_nodes,
            'currentApprovalNode': rules.current_approval_node,
            'createTime': rules.create_time,
            'updateTime': rules.update_time,
        })
    except Exception as e:
        logger.error(f'查询审批规则异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'查询审批规则失败：{str(e)}')


@applyController.get('/{apply_id}/approval/logs', dependencies=[Depends(CheckWorkbenchMenuAuth())])
async def get_approval_logs(
    apply_id: str,
    query_db: AsyncSession = Depends(get_db),
):
    """
    查询审批日志列表
    
    :param apply_id: 申请单ID
    :param query_db: orm对象
    """
    try:
        logs = await ApprovalLogDao.get_logs_by_apply_id(query_db, apply_id)
        
        result = []
        for log in logs:
            approval_images = []
            if log.approval_images:
                try:
                    approval_images = json.loads(log.approval_images) if isinstance(log.approval_images, str) else log.approval_images
                except (json.JSONDecodeError, TypeError):
                    approval_images = []
            
            result.append({
                'id': log.id,
                'applyId': log.apply_id,
                'approvalNode': log.approval_node,
                'approverId': log.approver_id,
                'approvalResult': log.approval_result,
                'approvalComment': log.approval_comment,
                'approvalImages': approval_images,
                'approvalStartTime': log.approval_start_time,
                'approvalEndTime': log.approval_end_time,
            })
        
        return ResponseUtil.success(data=result)
    except Exception as e:
        logger.error(f'查询审批日志异常: {str(e)}', exc_info=True)
        return ResponseUtil.error(msg=f'查询审批日志失败：{str(e)}')
