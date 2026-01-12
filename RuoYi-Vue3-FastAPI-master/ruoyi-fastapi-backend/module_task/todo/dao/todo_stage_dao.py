"""
阶段执行表DAO
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from module_task.entity.do.todo_stage_do import TodoStage


class TodoStageDao:
    """阶段执行表DAO"""
    
    @classmethod
    async def get_stage_by_id(cls, db: AsyncSession, stage_id: int) -> Optional[TodoStage]:
        """
        根据阶段ID查询阶段执行记录
        
        :param db: orm对象
        :param stage_id: 阶段ID（关联proj_stage.stage_id）
        :return: 阶段执行对象或None
        """
        result = await db.execute(
            select(TodoStage).where(TodoStage.stage_id == stage_id)
        )
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_stages_by_project_id(cls, db: AsyncSession, project_id: int) -> List[TodoStage]:
        """
        根据项目ID查询所有阶段执行记录
        
        :param db: orm对象
        :param project_id: 项目ID
        :return: 阶段执行列表
        """
        result = await db.execute(
            select(TodoStage).where(TodoStage.project_id == project_id)
        )
        return list(result.scalars().all())
    
    @classmethod
    async def create_stage(cls, db: AsyncSession, stage_data: dict) -> TodoStage:
        """
        创建阶段执行记录
        
        :param db: orm对象
        :param stage_data: 阶段数据字典
        :return: 创建的阶段执行对象
        """
        stage = TodoStage(**stage_data)
        db.add(stage)
        await db.flush()
        return stage
    
    @classmethod
    async def update_stage_status(cls, db: AsyncSession, stage_id: int, status: int, **kwargs) -> None:
        """
        更新阶段状态
        
        :param db: orm对象
        :param stage_id: 阶段ID（关联proj_stage.stage_id）
        :param status: 新状态
        :param kwargs: 其他更新字段（如actual_start_time, actual_complete_time等）
        """
        from sqlalchemy import update
        update_data = {'stage_status': status, **kwargs}
        await db.execute(
            update(TodoStage)
            .where(TodoStage.stage_id == stage_id)
            .values(**update_data)
        )
