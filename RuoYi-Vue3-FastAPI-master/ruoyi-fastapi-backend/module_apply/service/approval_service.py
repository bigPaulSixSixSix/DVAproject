"""
审批流程服务
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from module_apply.dao.approval_rules_dao import ApprovalRulesDao
from module_apply.dao.approval_log_dao import ApprovalLogDao
from module_apply.entity.do.apply_rules_do import ApplyRules
from module_apply.entity.do.apply_log_do import ApplyLog
from utils.log_util import logger
import json


class ApprovalService:
    """审批流程服务"""
    
    @staticmethod
    async def create_approval_rules(
        query_db: AsyncSession,
        apply_id: str,
        approval_nodes: List[int]
    ) -> ApplyRules:
        """
        创建审批规则
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :param approval_nodes: 编制ID列表（oa_department.id）
        :return: 创建的审批规则对象
        """
        if not approval_nodes:
            raise ValueError('审批节点列表不能为空')
        
        rules_data = {
            'apply_id': apply_id,
            'approval_nodes': approval_nodes,
            'approved_nodes': [],
            'current_approval_node': approval_nodes[0] if approval_nodes else None,
            'create_time': datetime.now(),
            'update_time': datetime.now(),
        }
        
        rules = await ApprovalRulesDao.create_rules(query_db, rules_data)
        logger.info(f'创建审批规则成功: apply_id={apply_id}, approval_nodes={approval_nodes}')
        return rules
    
    @staticmethod
    async def get_approval_rules(
        query_db: AsyncSession,
        apply_id: str
    ) -> Optional[ApplyRules]:
        """
        获取审批规则
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :return: 审批规则对象或None
        """
        return await ApprovalRulesDao.get_rules_by_apply_id(query_db, apply_id)
    
    @staticmethod
    async def get_current_approver(
        query_db: AsyncSession,
        apply_id: str
    ) -> Optional[int]:
        """
        获取当前审批节点（编制ID）
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :return: 当前审批节点（编制ID，oa_department.id）或None
        """
        rules = await ApprovalRulesDao.get_rules_by_apply_id(query_db, apply_id)
        if rules:
            return rules.current_approval_node
        return None
    
    @staticmethod
    async def create_approval_log(
        query_db: AsyncSession,
        apply_id: str,
        approval_node: int,
        approver_id: str,
        approval_result: int,
        approval_comment: str = None,
        approval_images: List[str] = None
    ) -> ApplyLog:
        """
        创建审批日志
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        :param approval_node: 审批节点（编制ID，oa_department.id）
        :param approver_id: 审批人工号
        :param approval_result: 审批结果（0-申请提交，1-同意，2-驳回）
        :param approval_comment: 审批意见
        :param approval_images: 审批意见附图
        :return: 创建的审批日志对象
        """
        now = datetime.now()
        log_data = {
            'apply_id': apply_id,
            'approval_node': approval_node,
            'approver_id': approver_id,
            'approval_result': approval_result,
            'approval_comment': approval_comment,
            'approval_images': approval_images or [],
            'approval_start_time': now,
            'approval_end_time': now,
        }
        
        log = await ApprovalLogDao.create_log(query_db, log_data)
        logger.info(f'创建审批日志成功: apply_id={apply_id}, approval_node={approval_node}, result={approval_result}')
        return log
