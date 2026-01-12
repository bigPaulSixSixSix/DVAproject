"""
审批日志表DAO
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_apply.entity.do.apply_log_do import ApplyLog
import json


class ApprovalLogDao:
    """审批日志表DAO"""
    
    @classmethod
    async def get_logs_by_apply_id(cls, db: AsyncSession, apply_id: str) -> List[ApplyLog]:
        """
        根据申请单ID查询审批日志列表
        
        :param db: orm对象
        :param apply_id: 申请单ID
        :return: 审批日志列表
        """
        result = await db.execute(
            select(ApplyLog)
            .where(ApplyLog.apply_id == apply_id)
            .order_by(desc(ApplyLog.approval_start_time))
        )
        return list(result.scalars().all())
    
    @classmethod
    async def create_log(cls, db: AsyncSession, log_data: dict) -> ApplyLog:
        """
        创建审批日志
        
        :param db: orm对象
        :param log_data: 审批日志数据字典
        :return: 创建的审批日志对象
        """
        # 处理JSON字段
        if 'approval_images' in log_data and isinstance(log_data['approval_images'], list):
            log_data['approval_images'] = json.dumps(log_data['approval_images'])
        
        log = ApplyLog(**log_data)
        db.add(log)
        await db.flush()
        return log
