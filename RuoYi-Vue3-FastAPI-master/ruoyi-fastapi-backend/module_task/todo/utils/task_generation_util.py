"""
任务生成工具类
用于判断任务/阶段的可编辑性和生成条件
"""
import json
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from module_task.todo.dao.todo_task_dao import TodoTaskDao
from module_task.todo.dao.todo_stage_dao import TodoStageDao
from module_task.configuration.dao.task_dao import TaskDao
from module_task.entity.do.proj_task_do import ProjTask
from module_task.entity.do.proj_stage_do import ProjStage
from module_task.entity.do.todo_task_do import TodoTask
from module_task.entity.do.todo_stage_do import TodoStage
from utils.log_util import logger


class TaskGenerationUtil:
    """任务生成工具类"""
    
    @staticmethod
    async def is_task_editable(db: AsyncSession, task_id: int) -> bool:
        """
        判断任务是否可编辑
        规则：只要是没被生成的任务，就可以被编辑
        
        :param db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :return: True表示可编辑，False表示不可编辑
        """
        # 查询 todo_task 表，如果任务ID存在，则任务已生成，不可编辑
        todo_task = await TodoTaskDao.get_task_by_id(db, task_id)
        return todo_task is None
    
    @staticmethod
    async def is_stage_editable(db: AsyncSession, stage_id: int) -> bool:
        """
        判断阶段是否可编辑
        规则：只要是没被生成的阶段，就可以被编辑
        
        :param db: orm对象
        :param stage_id: 阶段ID（关联proj_stage.stage_id）
        :return: True表示可编辑，False表示不可编辑
        """
        # 查询 todo_stage 表，如果阶段ID存在，则阶段已生成，不可编辑
        todo_stage = await TodoStageDao.get_stage_by_id(db, stage_id)
        return todo_stage is None
    
    @staticmethod
    async def check_task_generation_condition(db: AsyncSession, task_id: int) -> bool:
        """
        检查任务是否满足生成条件
        规则：
        1. 没有前置任务（predecessor_tasks 为空）-> 满足生成条件
        2. 所有前置任务都完成（在 todo_task 表中查询，状态为3）-> 满足生成条件
        
        :param db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :return: True表示满足生成条件，False表示不满足
        """
        # 1. 从 proj_task 表获取任务配置
        result = await db.execute(
            select(ProjTask).where(ProjTask.task_id == task_id, ProjTask.enable == '1')
        )
        proj_task = result.scalar_one_or_none()
        
        if not proj_task:
            logger.warning(f'任务配置不存在: task_id={task_id}')
            return False
        
        # 2. 获取前置任务列表
        predecessor_tasks = []
        if proj_task.predecessor_tasks:
            try:
                predecessor_tasks = json.loads(proj_task.predecessor_tasks) if isinstance(proj_task.predecessor_tasks, str) else proj_task.predecessor_tasks
            except (json.JSONDecodeError, TypeError):
                predecessor_tasks = []
        
        # 3. 如果前置任务为空，满足生成条件
        if not predecessor_tasks:
            return True
        
        # 4. 检查所有前置任务是否都完成
        for pred_id in predecessor_tasks:
            todo_task = await TodoTaskDao.get_task_by_id(db, pred_id)
            if not todo_task or todo_task.task_status != 3:  # 3-完成
                return False
        
        return True
    
    @staticmethod
    async def check_stage_generation_condition(db: AsyncSession, stage_id: int) -> bool:
        """
        检查阶段是否满足生成条件
        规则：
        1. 没有前置阶段（predecessor_stages 为空）-> 满足生成条件
        2. 所有前置阶段都完成（在 todo_stage 表中查询，状态为2）-> 满足生成条件
        
        :param db: orm对象
        :param stage_id: 阶段ID（关联proj_stage.stage_id）
        :return: True表示满足生成条件，False表示不满足
        """
        # 1. 从 proj_stage 表获取阶段配置
        result = await db.execute(
            select(ProjStage).where(ProjStage.stage_id == stage_id, ProjStage.enable == '1')
        )
        proj_stage = result.scalar_one_or_none()
        
        if not proj_stage:
            logger.warning(f'阶段配置不存在: stage_id={stage_id}')
            return False
        
        # 2. 获取前置阶段列表
        predecessor_stages = []
        if proj_stage.predecessor_stages:
            try:
                predecessor_stages = json.loads(proj_stage.predecessor_stages) if isinstance(proj_stage.predecessor_stages, str) else proj_stage.predecessor_stages
            except (json.JSONDecodeError, TypeError):
                predecessor_stages = []
        
        # 3. 如果前置阶段为空，满足生成条件
        if not predecessor_stages:
            return True
        
        # 4. 检查所有前置阶段是否都完成
        for pred_id in predecessor_stages:
            todo_stage = await TodoStageDao.get_stage_by_id(db, pred_id)
            if not todo_stage or todo_stage.stage_status != 2:  # 2-已完成
                return False
        
        return True
    
    @staticmethod
    async def get_tasks_generated_status(db: AsyncSession, project_id: int) -> bool:
        """
        判断项目是否已生成任务
        查询 todo_task 表，如果存在 project_id 对应的记录，则为 true
        
        :param db: orm对象
        :param project_id: 项目ID
        :return: True表示已生成任务，False表示未生成任务
        """
        tasks = await TodoTaskDao.get_tasks_by_project_id(db, project_id)
        return len(tasks) > 0
    
    @staticmethod
    async def check_task_validation_status(db: AsyncSession, task_id: int) -> bool:
        """
        检查任务是否通过校验（信息完整且无校验失败）
        用于判断任务是否可以生成
        
        检查项：
        1. 信息缺失：负责人、开始时间、结束时间、审批层级
        2. 未分配到阶段：stage_id为null
        3. 时间关系异常：自身开始时间>结束时间，或与前置/后置任务的时间冲突
        
        :param db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :return: True表示通过校验可以生成，False表示有校验失败不应生成
        """
        from module_task.configuration.service.validator.task_validator import TaskValidator
        
        # 1. 从 proj_task 表获取任务配置
        result = await db.execute(
            select(ProjTask).where(ProjTask.task_id == task_id, ProjTask.enable == '1')
        )
        proj_task = result.scalar_one_or_none()
        
        if not proj_task:
            logger.warning(f'任务配置不存在: task_id={task_id}')
            return False
        
        # 2. 调用校验器中的校验方法
        validation_result = await TaskValidator.check_single_task_validation(db, proj_task)
        
        if not validation_result['is_valid']:
            if validation_result['has_missing_info']:
                logger.debug(f'任务信息缺失，不满足生成条件: task_id={task_id}')
            elif validation_result['is_unassigned']:
                logger.debug(f'任务未分配到阶段，不满足生成条件: task_id={task_id}')
            elif validation_result['has_time_error']:
                logger.debug(f'任务时间关系异常，不满足生成条件: task_id={task_id}')
            return False
        
        return True
    
    @staticmethod
    async def check_stage_time_conflict_with_generated_stages(
        db: AsyncSession, 
        stage_id: int, 
        task_id: int = None
    ) -> Tuple[bool, Optional[str]]:
        """
        检查阶段时间是否会与已生成的前置/后置阶段产生冲突
        用于判断任务是否可以生成（如果任务会导致阶段时间变化并产生冲突，则不应生成）
        
        :param db: orm对象
        :param stage_id: 阶段ID（关联proj_stage.stage_id）
        :param task_id: 任务ID（可选，用于错误消息）
        :return: (是否通过检查, 错误消息)
            - (True, None): 通过检查，无冲突
            - (False, str): 未通过检查，返回冲突详情
        """
        # 1. 从 proj_stage 表获取阶段配置（包含最新的时间信息）
        result = await db.execute(
            select(ProjStage).where(ProjStage.stage_id == stage_id, ProjStage.enable == '1')
        )
        proj_stage = result.scalar_one_or_none()
        
        if not proj_stage:
            return True, None  # 阶段不存在，不检查
        
        # 2. 检查阶段是否已生成（如果未生成，不需要检查）
        todo_stage = await TodoStageDao.get_stage_by_id(db, stage_id)
        if not todo_stage:
            return True, None  # 阶段未生成，不检查
        
        # 3. 获取阶段的前置阶段列表
        predecessor_stages = []
        if proj_stage.predecessor_stages:
            try:
                predecessor_stages = json.loads(proj_stage.predecessor_stages) if isinstance(proj_stage.predecessor_stages, str) else proj_stage.predecessor_stages
            except (json.JSONDecodeError, TypeError):
                predecessor_stages = []
        
        # 4. 检查前置阶段冲突
        if predecessor_stages and proj_stage.start_time:
            # 获取所有已生成的前置阶段
            generated_predecessor_stages = []
            for pred_id in predecessor_stages:
                pred_todo_stage = await TodoStageDao.get_stage_by_id(db, pred_id)
                if pred_todo_stage:
                    # 前置阶段已生成，获取其配置信息
                    pred_proj_result = await db.execute(
                        select(ProjStage).where(ProjStage.stage_id == pred_id, ProjStage.enable == '1')
                    )
                    pred_proj_stage = pred_proj_result.scalar_one_or_none()
                    if pred_proj_stage and pred_proj_stage.end_time:
                        generated_predecessor_stages.append({
                            'stage_id': pred_id,
                            'name': pred_proj_stage.name,
                            'end_time': pred_proj_stage.end_time
                        })
            
            # 检查阶段开始时间是否 <= 任何已生成前置阶段的结束时间
            if generated_predecessor_stages:
                # 找到结束时间最晚的前置阶段
                latest_pred = max(generated_predecessor_stages, key=lambda x: x['end_time'])
                if proj_stage.start_time <= latest_pred['end_time']:
                    task_info = f'任务【{task_id}】' if task_id else '任务'
                    error_msg = f'{task_info}所属阶段【{proj_stage.name}】的开始时间 {proj_stage.start_time} 不能早于或等于已生成的前置阶段【{latest_pred["name"]}】(ID: {latest_pred["stage_id"]}) 的结束时间 {latest_pred["end_time"]}'
                    return False, error_msg
        
        # 5. 获取阶段的后置阶段列表
        successor_stages = []
        if proj_stage.successor_stages:
            try:
                successor_stages = json.loads(proj_stage.successor_stages) if isinstance(proj_stage.successor_stages, str) else proj_stage.successor_stages
            except (json.JSONDecodeError, TypeError):
                successor_stages = []
        
        # 6. 检查后置阶段冲突
        if successor_stages and proj_stage.end_time:
            # 获取所有已生成的后置阶段
            generated_successor_stages = []
            for succ_id in successor_stages:
                succ_todo_stage = await TodoStageDao.get_stage_by_id(db, succ_id)
                if succ_todo_stage:
                    # 后置阶段已生成，获取其配置信息
                    succ_proj_result = await db.execute(
                        select(ProjStage).where(ProjStage.stage_id == succ_id, ProjStage.enable == '1')
                    )
                    succ_proj_stage = succ_proj_result.scalar_one_or_none()
                    if succ_proj_stage and succ_proj_stage.start_time:
                        generated_successor_stages.append({
                            'stage_id': succ_id,
                            'name': succ_proj_stage.name,
                            'start_time': succ_proj_stage.start_time
                        })
            
            # 检查阶段结束时间是否 >= 任何已生成后置阶段的开始时间
            if generated_successor_stages:
                # 找到开始时间最早的后置阶段
                earliest_succ = min(generated_successor_stages, key=lambda x: x['start_time'])
                if proj_stage.end_time >= earliest_succ['start_time']:
                    task_info = f'任务【{task_id}】' if task_id else '任务'
                    error_msg = f'{task_info}所属阶段【{proj_stage.name}】的结束时间 {proj_stage.end_time} 不能晚于或等于已生成的后置阶段【{earliest_succ["name"]}】(ID: {earliest_succ["stage_id"]}) 的开始时间 {earliest_succ["start_time"]}'
                    return False, error_msg
        
        return True, None
