"""
任务申请详情表DAO
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_task.entity.do.todo_task_apply_do import TodoTaskApply


class TodoTaskApplyDao:
    """任务申请详情表DAO"""
    
    @classmethod
    async def get_apply_by_apply_id(cls, db: AsyncSession, apply_id: str) -> Optional[TodoTaskApply]:
        """
        根据申请单ID查询任务申请详情
        
        :param db: orm对象
        :param apply_id: 申请单ID
        :return: 任务申请详情对象或None
        """
        result = await db.execute(
            select(TodoTaskApply).where(TodoTaskApply.apply_id == apply_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_latest_apply_by_task_id(cls, db: AsyncSession, task_id: int) -> Optional[TodoTaskApply]:
        """
        根据任务ID查询最新的任务申请详情（按提交时间倒序）
        
        :param db: orm对象
        :param task_id: 任务ID（关联todo_task.id）
        :return: 任务申请详情对象或None
        """
        from sqlalchemy import desc
        result = await db.execute(
            select(TodoTaskApply)
            .where(TodoTaskApply.task_id == task_id)
            .order_by(desc(TodoTaskApply.submit_time))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_all_applies_by_task_id(
        cls, 
        db: AsyncSession, 
        task_id: int, 
        exclude_apply_id: Optional[str] = None
    ) -> List[TodoTaskApply]:
        """
        根据任务ID查询所有任务申请详情（按提交时间倒序）
        
        :param db: orm对象
        :param task_id: 任务ID（关联todo_task.id）
        :param exclude_apply_id: 排除的申请单ID（可选，用于排除当前申请单）
        :return: 任务申请详情列表
        """
        from sqlalchemy import desc
        query = select(TodoTaskApply).where(TodoTaskApply.task_id == task_id)
        
        if exclude_apply_id:
            query = query.where(TodoTaskApply.apply_id != exclude_apply_id)
        
        query = query.order_by(desc(TodoTaskApply.submit_time))
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @classmethod
    async def create_apply(cls, db: AsyncSession, apply_data: dict) -> TodoTaskApply:
        """
        创建任务申请详情
        
        :param db: orm对象
        :param apply_data: 申请数据字典
        :return: 创建的任务申请详情对象
        """
        apply = TodoTaskApply(**apply_data)
        db.add(apply)
        await db.flush()
        return apply
