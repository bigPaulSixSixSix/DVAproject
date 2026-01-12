"""
申请主表DAO
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_apply.entity.do.apply_primary_do import ApplyPrimary
from utils.log_util import logger


class ApplyDao:
    """申请主表DAO"""
    
    @classmethod
    async def get_apply_by_id(cls, db: AsyncSession, apply_id: str) -> Optional[ApplyPrimary]:
        """
        根据申请单ID查询申请单
        
        :param db: orm对象
        :param apply_id: 申请单ID
        :return: 申请单对象或None
        """
        result = await db.execute(
            select(ApplyPrimary).where(ApplyPrimary.apply_id == apply_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def create_apply(cls, db: AsyncSession, apply_data: dict) -> ApplyPrimary:
        """
        创建申请单
        
        :param db: orm对象
        :param apply_data: 申请单数据字典
        :return: 创建的申请单对象
        """
        apply = ApplyPrimary(**apply_data)
        db.add(apply)
        await db.flush()
        return apply
    
    @classmethod
    async def update_apply_status(cls, db: AsyncSession, apply_id: str, status: int) -> None:
        """
        更新申请单状态
        
        :param db: orm对象
        :param apply_id: 申请单ID
        :param status: 新状态
        """
        from sqlalchemy import update
        await db.execute(
            update(ApplyPrimary)
            .where(ApplyPrimary.apply_id == apply_id)
            .values(apply_status=status, update_time=datetime.now())
        )
