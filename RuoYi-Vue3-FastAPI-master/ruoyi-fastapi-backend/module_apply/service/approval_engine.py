"""
审批引擎（核心逻辑）
"""
from typing import Callable, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_apply.service.apply_service import ApplyService
from module_apply.service.approval_service import ApprovalService
from module_apply.dao.approval_rules_dao import ApprovalRulesDao
from module_apply.entity.do.apply_rules_do import ApplyRules
from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
from utils.log_util import logger
from exceptions.exception import ServiceException
import json


class ApprovalEngine:
    """审批引擎 - 处理审批流程的核心逻辑"""
    
    @staticmethod
    async def _check_if_post_is_empty(
        query_db: AsyncSession,
        organization_id: int
    ) -> bool:
        """
        检查编制是否为空岗（编制存在但没有员工）
        
        :param query_db: orm对象
        :param organization_id: 编制ID（oa_department.id）
        :return: True=空岗，False=有员工
        """
        employee = await query_db.execute(
            select(OaEmployeePrimary)
            .where(
                OaEmployeePrimary.organization_id == organization_id,
                OaEmployeePrimary.enable == '1'
            )
            .limit(1)
        )
        employee = employee.scalar_one_or_none()
        return employee is None
    
    @staticmethod
    async def _auto_approve_empty_post(
        query_db: AsyncSession,
        apply_id: str,
        approval_nodes: List[int],
        approved_nodes: List[int],
        current_node: int,
        callback: Callable = None
    ) -> bool:
        """
        自动审批空岗节点
        1. 创建审批日志（空岗自动审批）
        2. 更新审批规则（推进到下一节点）
        3. 如果还有下一节点，检查下一节点是否也为空岗（递归处理）
        4. 如果是最后一级，完成审批流程
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :param approval_nodes: 审批节点列表
        :param approved_nodes: 已审批节点列表
        :param current_node: 当前节点（编制ID）
        :param callback: 审批通过后的回调函数
        :return: 是否完成所有审批
        """
        # 创建审批日志（空岗自动审批）
        await ApprovalService.create_approval_log(
            query_db=query_db,
            apply_id=apply_id,
            approval_node=current_node,
            approver_id='system',
            approval_result=1,  # 同意
            approval_comment='空岗自动审批通过',
            approval_images=None,
        )
        
        # 更新已审批节点
        approved_nodes.append(current_node)
        next_index = len(approved_nodes)
        
        if next_index >= len(approval_nodes):
            # 最后一级，审批完成
            update_data = {
                'approved_nodes': approved_nodes,
                'current_approval_node': None,
            }
            await ApprovalRulesDao.update_rules(query_db, apply_id, update_data)
            
            # 更新申请单状态为完成
            await ApplyService.update_apply_status(query_db, apply_id, 1)  # 1-完成
            
            # 调用回调函数
            if callback:
                try:
                    await callback(query_db, apply_id)
                except Exception as e:
                    logger.error(f'空岗自动审批完成回调函数执行失败: apply_id={apply_id}, error={str(e)}', exc_info=True)
                    # 不抛出异常，避免影响审批流程的完成
            
            logger.info(f'空岗自动审批完成: apply_id={apply_id}, node={current_node}')
            return True
        else:
            # 推进到下一节点
            next_node = approval_nodes[next_index]
            update_data = {
                'approved_nodes': approved_nodes,
                'current_approval_node': next_node,
            }
            await ApprovalRulesDao.update_rules(query_db, apply_id, update_data)
            
            logger.info(f'空岗自动审批推进到下一节点: apply_id={apply_id}, next_node={next_node}')
            
            # 检查下一节点是否也为空岗（递归处理连续空岗）
            is_empty = await ApprovalEngine._check_if_post_is_empty(query_db, next_node)
            if is_empty:
                # 下一节点也是空岗，继续自动审批
                return await ApprovalEngine._auto_approve_empty_post(
                    query_db, apply_id, approval_nodes, approved_nodes, next_node, callback
                )
            else:
                # 下一节点有员工，等待手动审批
                return False
    
    @staticmethod
    async def submit_for_approval(
        query_db: AsyncSession,
        apply_id: str,
        approval_nodes: List[int],
        submitter_id: str,
        callback: Callable = None
    ) -> None:
        """
        提交审批
        1. 创建申请单（如果不存在）
        2. 创建审批规则
        3. 创建审批日志（申请提交）
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :param approval_nodes: 审批节点列表（编制ID列表，oa_department.id）
        :param submitter_id: 提交人工号
        """
        if not approval_nodes:
            raise ServiceException(message='审批节点列表不能为空')
        
        # 检查申请单是否存在，不存在则创建
        apply = await ApplyService.get_apply_by_id(query_db, apply_id)
        if not apply:
            # 默认申请类型为1（项目推进任务）
            await ApplyService.create_apply(query_db, apply_type=1, apply_id=apply_id)
        
        # 创建审批规则
        await ApprovalService.create_approval_rules(query_db, apply_id, approval_nodes)
        
        # 创建审批日志（申请提交）
        await ApprovalService.create_approval_log(
            query_db=query_db,
            apply_id=apply_id,
            approval_node=approval_nodes[0],
            approver_id=submitter_id,
            approval_result=0,  # 申请提交
            approval_comment='申请提交',
        )
        
        # 检查第一个节点是否为空岗，如果是则自动审批
        first_node = approval_nodes[0]
        is_empty = await ApprovalEngine._check_if_post_is_empty(query_db, first_node)
        if is_empty:
            # 第一个节点是空岗，自动审批
            approved_nodes = []
            await ApprovalEngine._auto_approve_empty_post(
                query_db, apply_id, approval_nodes, approved_nodes, first_node, callback=callback
            )
            logger.info(f'提交审批成功（第一个节点为空岗，已自动审批）: apply_id={apply_id}, approval_nodes={approval_nodes}')
        else:
            logger.info(f'提交审批成功: apply_id={apply_id}, approval_nodes={approval_nodes}')
    
    @staticmethod
    async def approve(
        query_db: AsyncSession,
        apply_id: str,
        approver_id: str,
        approval_comment: str = None,
        approval_images: List[str] = None,
        callback: Callable = None
    ) -> bool:
        """
        审批同意
        1. 验证审批权限
        2. 更新审批规则（推进到下一节点）
        3. 创建审批日志
        4. 如果是最后一级，调用callback（由业务模块实现）
        5. 返回是否完成所有审批
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :param approver_id: 审批人工号
        :param approval_comment: 审批意见
        :param approval_images: 审批意见附图
        :param callback: 审批通过后的回调函数
        :return: 是否完成所有审批
        """
        # 获取审批规则
        rules = await ApprovalService.get_approval_rules(query_db, apply_id)
        if not rules:
            raise ServiceException(message=f'审批规则不存在: apply_id={apply_id}')
        
        # 验证审批权限（检查当前审批节点）
        if rules.current_approval_node is None:
            raise ServiceException(message='当前没有待审批的节点')
        
        # 解析审批节点列表
        approval_nodes = []
        if rules.approval_nodes:
            try:
                approval_nodes = json.loads(rules.approval_nodes) if isinstance(rules.approval_nodes, str) else rules.approval_nodes
            except (json.JSONDecodeError, TypeError):
                approval_nodes = []
        
        approved_nodes = []
        if rules.approved_nodes:
            try:
                approved_nodes = json.loads(rules.approved_nodes) if isinstance(rules.approved_nodes, str) else rules.approved_nodes
            except (json.JSONDecodeError, TypeError):
                approved_nodes = []
        
        current_node = rules.current_approval_node
        
        # 创建审批日志
        await ApprovalService.create_approval_log(
            query_db=query_db,
            apply_id=apply_id,
            approval_node=current_node,
            approver_id=approver_id,
            approval_result=1,  # 同意
            approval_comment=approval_comment,
            approval_images=approval_images,
        )
        
        # 更新审批规则
        approved_nodes.append(current_node)
        next_index = len(approved_nodes)
        
        if next_index >= len(approval_nodes):
            # 最后一级，审批完成
            update_data = {
                'approved_nodes': approved_nodes,
                'current_approval_node': None,
            }
            await ApprovalRulesDao.update_rules(query_db, apply_id, update_data)
            
            # 更新申请单状态为完成
            await ApplyService.update_apply_status(query_db, apply_id, 1)  # 1-完成
            
            # 调用回调函数
            if callback:
                try:
                    await callback(query_db, apply_id)
                except Exception as e:
                    logger.error(f'审批完成回调函数执行失败: apply_id={apply_id}, error={str(e)}', exc_info=True)
                    # 不抛出异常，避免影响审批流程的完成
            
            logger.info(f'审批完成: apply_id={apply_id}')
            return True
        else:
            # 推进到下一节点
            next_node = approval_nodes[next_index]
            update_data = {
                'approved_nodes': approved_nodes,
                'current_approval_node': next_node,
            }
            await ApprovalRulesDao.update_rules(query_db, apply_id, update_data)
            
            # 检查下一节点是否为空岗，如果是则自动审批
            is_empty = await ApprovalEngine._check_if_post_is_empty(query_db, next_node)
            if is_empty:
                # 下一节点是空岗，自动审批
                return await ApprovalEngine._auto_approve_empty_post(
                    query_db, apply_id, approval_nodes, approved_nodes, next_node, callback
                )
            else:
                # 下一节点有员工，等待手动审批
                logger.info(f'审批推进到下一节点: apply_id={apply_id}, next_node={next_node}')
                return False
    
    @staticmethod
    async def reject(
        query_db: AsyncSession,
        apply_id: str,
        approver_id: str,
        approval_comment: str,
        approval_images: List[str] = None,
        callback: Callable = None
    ) -> None:
        """
        审批驳回
        1. 验证审批权限
        2. 更新审批规则（current_approval_node设为null）
        3. 创建审批日志
        4. 更新申请单状态为驳回
        5. 调用callback（由业务模块实现）
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :param approver_id: 审批人工号
        :param approval_comment: 审批意见（必填）
        :param approval_images: 审批意见附图
        :param callback: 审批驳回后的回调函数
        """
        if not approval_comment:
            raise ServiceException(message='驳回时必须填写审批意见')
        
        # 获取审批规则
        rules = await ApprovalService.get_approval_rules(query_db, apply_id)
        if not rules:
            raise ServiceException(message=f'审批规则不存在: apply_id={apply_id}')
        
        # 验证审批权限
        if rules.current_approval_node is None:
            raise ServiceException(message='当前没有待审批的节点')
        
        current_node = rules.current_approval_node
        
        # 解析已审批节点
        approved_nodes = []
        if rules.approved_nodes:
            try:
                approved_nodes = json.loads(rules.approved_nodes) if isinstance(rules.approved_nodes, str) else rules.approved_nodes
            except (json.JSONDecodeError, TypeError):
                approved_nodes = []
        
        # 创建审批日志
        await ApprovalService.create_approval_log(
            query_db=query_db,
            apply_id=apply_id,
            approval_node=current_node,
            approver_id=approver_id,
            approval_result=2,  # 驳回
            approval_comment=approval_comment,
            approval_images=approval_images,
        )
        
        # 更新审批规则
        approved_nodes.append(current_node)
        update_data = {
            'approved_nodes': approved_nodes,
            'current_approval_node': None,
        }
        await ApprovalRulesDao.update_rules(query_db, apply_id, update_data)
        
        # 更新申请单状态为驳回
        await ApplyService.update_apply_status(query_db, apply_id, 2)  # 2-驳回
        
        # 调用回调函数
        if callback:
            await callback(query_db, apply_id)
        
        logger.info(f'审批驳回: apply_id={apply_id}, comment={approval_comment}')
