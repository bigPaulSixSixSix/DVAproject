"""
审批规则表DAO
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_apply.entity.do.apply_rules_do import ApplyRules
import json


class ApprovalRulesDao:
    """审批规则表DAO"""
    
    @classmethod
    async def get_rules_by_apply_id(cls, db: AsyncSession, apply_id: str) -> Optional[ApplyRules]:
        """
        根据申请单ID查询审批规则
        
        :param db: orm对象
        :param apply_id: 申请单ID
        :return: 审批规则对象或None
        """
        result = await db.execute(
            select(ApplyRules).where(ApplyRules.apply_id == apply_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def create_rules(cls, db: AsyncSession, rules_data: dict) -> ApplyRules:
        """
        创建审批规则
        
        :param db: orm对象
        :param rules_data: 审批规则数据字典
        :return: 创建的审批规则对象
        """
        # 处理JSON字段
        if 'approval_nodes' in rules_data and isinstance(rules_data['approval_nodes'], list):
            rules_data['approval_nodes'] = json.dumps(rules_data['approval_nodes'])
        if 'approved_nodes' in rules_data and isinstance(rules_data['approved_nodes'], list):
            rules_data['approved_nodes'] = json.dumps(rules_data['approved_nodes'])
        
        rules = ApplyRules(**rules_data)
        db.add(rules)
        await db.flush()
        return rules
    
    @classmethod
    async def update_rules(cls, db: AsyncSession, apply_id: str, update_data: dict) -> None:
        """
        更新审批规则
        
        :param db: orm对象
        :param apply_id: 申请单ID
        :param update_data: 更新数据字典
        """
        # 处理JSON字段
        if 'approval_nodes' in update_data and isinstance(update_data['approval_nodes'], list):
            update_data['approval_nodes'] = json.dumps(update_data['approval_nodes'])
        if 'approved_nodes' in update_data and isinstance(update_data['approved_nodes'], list):
            update_data['approved_nodes'] = json.dumps(update_data['approved_nodes'])
        
        update_data['update_time'] = datetime.now()
        await db.execute(
            update(ApplyRules)
            .where(ApplyRules.apply_id == apply_id)
            .values(**update_data)
        )
