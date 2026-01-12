"""
任务执行表DAO
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_task.entity.do.todo_task_do import TodoTask


class TodoTaskDao:
    """任务执行表DAO"""
    
    @classmethod
    async def get_task_by_id(cls, db: AsyncSession, task_id: int) -> Optional[TodoTask]:
        """
        根据任务ID查询任务执行记录
        
        :param db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :return: 任务执行对象或None
        """
        result = await db.execute(
            select(TodoTask).where(TodoTask.task_id == task_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_tasks_by_project_id(cls, db: AsyncSession, project_id: int) -> List[TodoTask]:
        """
        根据项目ID查询所有任务执行记录
        
        :param db: orm对象
        :param project_id: 项目ID
        :return: 任务执行列表
        """
        result = await db.execute(
            select(TodoTask).where(TodoTask.project_id == project_id)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def create_task(cls, db: AsyncSession, task_data: dict) -> TodoTask:
        """
        创建任务执行记录
        
        :param db: orm对象
        :param task_data: 任务数据字典
        :return: 创建的任务执行对象
        """
        task = TodoTask(**task_data)
        db.add(task)
        await db.flush()
        return task
    
    @classmethod
    async def update_task_status(cls, db: AsyncSession, task_id: int, status: int, **kwargs) -> None:
        """
        更新任务状态
        
        :param db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :param status: 新状态
        :param kwargs: 其他更新字段（如actual_start_time, actual_complete_time等）
        """
        from sqlalchemy import update
        update_data = {'task_status': status, **kwargs}
        await db.execute(
            update(TodoTask)
            .where(TodoTask.task_id == task_id)
            .values(**update_data)
        )
