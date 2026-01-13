"""
任务执行服务
"""
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from module_task.configuration.dao.task_dao import TaskDao
from module_task.todo.dao.todo_task_dao import TodoTaskDao
from module_task.todo.dao.todo_stage_dao import TodoStageDao
from module_task.todo.dao.todo_task_apply_dao import TodoTaskApplyDao
from module_task.entity.do.proj_task_do import ProjTask
from module_task.entity.do.proj_stage_do import ProjStage
from module_task.entity.do.todo_task_do import TodoTask
from module_task.entity.do.todo_stage_do import TodoStage
from module_apply.service.apply_service import ApplyService
from module_apply.service.approval_engine import ApprovalEngine
from module_apply.utils.apply_id_generator import ApplyIdGenerator
from module_task.todo.utils.task_generation_util import TaskGenerationUtil
from sqlalchemy import select
from utils.log_util import logger
from exceptions.exception import ServiceException


class TodoService:
    """任务执行服务"""
    
    @staticmethod
    async def generate_tasks_from_project(
        query_db: AsyncSession,
        project_id: int
    ) -> None:
        """
        从项目生成任务（任务生成）- 渐进式生成
        1. 检查项目状态（必须为正常）
        2. 查询项目下所有enable=1的任务配置和阶段配置
        3. 只生成满足条件的阶段（没有前置阶段的阶段）
        4. 只生成满足条件的任务（没有前置任务的任务，且所属阶段没有前置阶段）
        5. 生成的任务/阶段状态为 1（进行中），记录 actual_start_time
        
        :param query_db: orm对象
        :param project_id: 项目ID
        """
        logger.info(f'开始生成任务: project_id={project_id}')
        
        # 1. 检查项目状态（必须为正常）
        validation_stats = await TaskDao.get_project_validation_statistics(query_db)
        project_stats = validation_stats.get(project_id)
        
        if project_stats:
            project_status = project_stats.get('project_status', '正常')
            if project_status != '正常':
                # 获取异常计数详情
                missing_info_count = project_stats.get('missing_info_count', 0)
                time_relation_error_count = project_stats.get('time_relation_error_count', 0)
                unassigned_stage_count = project_stats.get('unassigned_stage_count', 0)
                total_errors = missing_info_count + time_relation_error_count + unassigned_stage_count
                
                logger.warning(
                    f'项目状态异常，无法生成任务: project_id={project_id}, '
                    f'status={project_status}, '
                    f'missing_info={missing_info_count}, '
                    f'time_error={time_relation_error_count}, '
                    f'unassigned={unassigned_stage_count}, '
                    f'total_errors={total_errors}'
                )
                raise ServiceException(message='当前项目状态异常，请完善所有任务后再生成')
        
        # 2. 查询项目下所有enable=1的任务配置和阶段配置
        proj_tasks = await TaskDao.get_tasks_by_project_id(query_db, project_id)
        proj_stages = await TaskDao.get_stages_by_project_id(query_db, project_id)
        
        if not proj_tasks:
            raise ServiceException(message=f'项目 {project_id} 下没有可执行的任务')
        
        # 3. 生成满足条件的阶段（没有前置阶段的阶段）
        # 对于每个阶段：
        # - 如果阶段可以生成：生成该阶段，并自动生成该阶段内的头部任务
        # - 如果阶段不能生成：直接跳过，该阶段内的任务都不需要再校验
        generated_stage_count = 0
        for proj_stage in proj_stages:
            # 检查阶段是否满足生成条件
            can_generate = await TodoService.generate_stage_if_ready(query_db, proj_stage.stage_id, project_id)
            if can_generate:
                generated_stage_count += 1
                # generate_stage_if_ready 内部会自动生成该阶段内的头部任务
        
        # 4. 处理没有归属阶段的任务（stage_id为null）
        # 注意：未分配到阶段的任务不应该生成（check_task_validation_status会检查stage_id）
        # 但这里仍然需要遍历，以便在后续完善信息后能够生成
        unassigned_tasks = [t for t in proj_tasks if t.stage_id is None]
        for proj_task in unassigned_tasks:
            # 检查任务是否满足生成条件（没有前置任务）
            predecessor_tasks = []
            if proj_task.predecessor_tasks:
                try:
                    predecessor_tasks = json.loads(proj_task.predecessor_tasks) if isinstance(proj_task.predecessor_tasks, str) else proj_task.predecessor_tasks
                except (json.JSONDecodeError, TypeError):
                    predecessor_tasks = []
            
            # 如果任务没有前置任务，检查校验状态后再生成
            # 注意：未分配到阶段的任务会在这里被check_task_validation_status拒绝
            if not predecessor_tasks:
                # 检查任务是否通过校验（信息完整且无校验失败）
                validation_passed = await TaskGenerationUtil.check_task_validation_status(query_db, proj_task.task_id)
                if validation_passed:
                    await TodoService.generate_task_if_ready(query_db, proj_task.task_id, project_id)
                else:
                    logger.debug(f'未分配阶段的任务校验未通过，跳过生成: task_id={proj_task.task_id}')
        
        # 5. 统计生成的任务数量（用于日志）
        from module_task.entity.do.todo_task_do import TodoTask
        generated_tasks_result = await query_db.execute(
            select(TodoTask).where(TodoTask.project_id == project_id)
        )
        generated_task_count = len(generated_tasks_result.scalars().all())
        
        logger.info(f'任务生成完成: project_id={project_id}, generated_stages={generated_stage_count}, generated_tasks={generated_task_count}')
    
    @staticmethod
    async def submit_task(
        query_db: AsyncSession,
        task_id: int,
        submitter_id: str,
        submit_text: str = None,
        submit_images: List[str] = None
    ) -> str:
        """
        提交任务
        1. 验证任务状态（必须是进行中）
        2. 生成申请单ID
        3. 插入任务申请详情表
        4. 调用审批引擎提交审批
        5. 更新任务状态为已提交
        
        :param query_db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :param submitter_id: 提交人工号
        :param submit_text: 提交文本
        :param submit_images: 提交图片
        :return: 申请单ID
        """
        # 1. 验证任务状态
        todo_task = await TodoTaskDao.get_task_by_id(query_db, task_id)
        if not todo_task:
            raise ServiceException(message=f'任务不存在: task_id={task_id}')
        
        if todo_task.task_status != 1:  # 必须是进行中
            raise ServiceException(message=f'任务状态不正确，无法提交。当前状态: {todo_task.task_status}')
        
        # 2. 生成申请单ID
        generator = ApplyIdGenerator.get_instance()
        apply_id = generator.generate()
        
        # 3. 插入任务申请详情表
        apply_data = {
            'apply_id': apply_id,
            'task_id': todo_task.id,  # todo_task的主键ID
            'submit_text': submit_text,
            'submit_images': json.dumps(submit_images) if submit_images else None,
            'submit_time': datetime.now(),
        }
        await TodoTaskApplyDao.create_apply(query_db, apply_data)
        
        # 4. 获取审批类型和审批节点（从 proj_task 表获取，因为 todo_task 表没有 approval_type 字段）
        from module_task.entity.do.proj_task_do import ProjTask
        proj_task_result = await query_db.execute(
            select(ProjTask).where(ProjTask.task_id == task_id, ProjTask.enable == '1')
        )
        proj_task = proj_task_result.scalar_one_or_none()
        
        approval_type = None
        approval_nodes = []
        
        if proj_task:
            approval_type = proj_task.approval_type
            if proj_task.approval_nodes:
                try:
                    approval_nodes = json.loads(proj_task.approval_nodes) if isinstance(proj_task.approval_nodes, str) else proj_task.approval_nodes
                except (json.JSONDecodeError, TypeError):
                    approval_nodes = []
        
        # 5. 判断是否需要审批
        if approval_type == 'none':
            # 无需审批模式：直接完成任务，不走审批流程
            logger.info(f'任务无需审批，直接完成: task_id={task_id}, apply_id={apply_id}')
            
            # 更新任务状态为已提交（先标记为已提交，然后立即完成）
            await TodoTaskDao.update_task_status(query_db, task_id, 2)  # 2-已提交
            
            # 直接完成任务（更新状态为完成，检查后置任务和阶段完成）
            now = datetime.now()
            await TodoTaskDao.update_task_status(
                query_db, task_id, 3,  # 3-完成
                actual_complete_time=now
            )
            logger.info(f'任务状态已更新为完成: task_id={task_id}, apply_id={apply_id}')
            
            # 检查后置任务
            try:
                await TodoService._check_and_activate_successor_tasks(query_db, task_id)
            except Exception as e:
                logger.error(f'检查后置任务失败: task_id={task_id}, error={str(e)}', exc_info=True)
            
            # 检查阶段完成
            try:
                await TodoService._check_and_activate_stages(query_db, todo_task.stage_id, todo_task.project_id)
            except Exception as e:
                logger.error(f'检查阶段完成失败: task_id={task_id}, stage_id={todo_task.stage_id}, error={str(e)}', exc_info=True)
            
            logger.info(f'任务提交成功（无需审批，已自动完成）: task_id={task_id}, apply_id={apply_id}')
            return apply_id
        else:
            # 需要审批：检查审批节点
            if not approval_nodes:
                raise ServiceException(message='任务没有配置审批节点，无法提交')
            
            # 调用审批引擎提交审批（传递回调函数，用于处理审批完成后的业务逻辑）
            await ApprovalEngine.submit_for_approval(
                query_db=query_db,
                apply_id=apply_id,
                approval_nodes=approval_nodes,
                submitter_id=submitter_id,
                callback=TodoService.handle_task_approved
            )
            
            # 更新任务状态为已提交
            await TodoTaskDao.update_task_status(query_db, task_id, 2)  # 2-已提交
            
            logger.info(f'任务提交成功: task_id={task_id}, apply_id={apply_id}')
            return apply_id
    
    @staticmethod
    async def handle_task_approved(
        query_db: AsyncSession,
        apply_id: str
    ) -> None:
        """
        处理任务审批通过（回调函数）
        1. 更新任务状态为完成
        2. 检查后置任务
        3. 检查阶段完成
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        """
        try:
            # 获取任务申请详情
            task_apply = await TodoTaskApplyDao.get_apply_by_apply_id(query_db, apply_id)
            if not task_apply:
                logger.error(f'任务申请详情不存在: apply_id={apply_id}')
                return
            
            # 获取任务执行记录（通过todo_task的主键ID）
            from sqlalchemy import select
            from module_task.entity.do.todo_task_do import TodoTask
            
            todo_task_result = await query_db.execute(
                select(TodoTask).where(TodoTask.id == task_apply.task_id)
            )
            todo_task = todo_task_result.scalar_one_or_none()
            
            if not todo_task:
                logger.error(f'任务执行记录不存在: task_id={task_apply.task_id}, apply_id={apply_id}')
                return
            
            task_id = todo_task.task_id  # proj_task的task_id
            
            # 1. 更新任务状态为完成
            now = datetime.now()
            await TodoTaskDao.update_task_status(
                query_db, task_id, 3,  # 3-完成
                actual_complete_time=now
            )
            logger.info(f'任务状态已更新为完成: task_id={task_id}, apply_id={apply_id}')
            
            # 2. 检查后置任务
            try:
                await TodoService._check_and_activate_successor_tasks(query_db, task_id)
            except Exception as e:
                logger.error(f'检查后置任务失败: task_id={task_id}, error={str(e)}', exc_info=True)
            
            # 3. 检查阶段完成
            try:
                await TodoService._check_and_activate_stages(query_db, todo_task.stage_id, todo_task.project_id)
            except Exception as e:
                logger.error(f'检查阶段完成失败: task_id={task_id}, stage_id={todo_task.stage_id}, error={str(e)}', exc_info=True)
            
            logger.info(f'任务审批通过处理完成: task_id={task_id}, apply_id={apply_id}')
        except Exception as e:
            logger.error(f'任务审批通过处理异常: apply_id={apply_id}, error={str(e)}', exc_info=True)
            # 不抛出异常，避免影响审批流程的完成
    
    @staticmethod
    async def handle_task_rejected(
        query_db: AsyncSession,
        apply_id: str
    ) -> None:
        """
        处理任务审批驳回（回调函数）
        1. 更新任务状态为驳回
        
        :param query_db: orm对象
        :param apply_id: 申请单ID
        """
        # 获取任务申请详情
        task_apply = await TodoTaskApplyDao.get_apply_by_apply_id(query_db, apply_id)
        if not task_apply:
            logger.error(f'任务申请详情不存在: apply_id={apply_id}')
            return
        
        # 直接通过task_id查询任务执行记录（task_apply.task_id是todo_task表的主键ID）
        from sqlalchemy import select
        from module_task.entity.do.todo_task_do import TodoTask
        
        todo_task_result = await query_db.execute(
            select(TodoTask).where(TodoTask.id == task_apply.task_id)
        )
        todo_task = todo_task_result.scalar_one_or_none()
        
        if not todo_task:
            logger.error(f'任务执行记录不存在: task_id={task_apply.task_id}')
            return
        
        task_id = todo_task.task_id  # proj_task的task_id
        
        # 更新任务状态为驳回
        await TodoTaskDao.update_task_status(query_db, task_id, 4)  # 4-驳回
        
        logger.info(f'任务审批驳回处理完成: task_id={task_id}, apply_id={apply_id}')
    
    @staticmethod
    async def _check_and_activate_successor_tasks(
        query_db: AsyncSession,
        task_id: int
    ) -> None:
        """
        检查并生成后置任务（渐进式生成）
        
        :param query_db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        """
        # 获取当前任务
        todo_task = await TodoTaskDao.get_task_by_id(query_db, task_id)
        if not todo_task:
            return
        
        # 获取后置任务列表（从 proj_task 表获取，因为后置任务可能还未生成）
        # 需要从 proj_task 表获取当前任务的后置任务列表
        result = await query_db.execute(
            select(ProjTask).where(ProjTask.task_id == task_id, ProjTask.enable == '1')
        )
        proj_task = result.scalar_one_or_none()
        
        if not proj_task:
            return
        
        successor_tasks = []
        if proj_task.successor_tasks:
            try:
                successor_tasks = json.loads(proj_task.successor_tasks) if isinstance(proj_task.successor_tasks, str) else proj_task.successor_tasks
            except (json.JSONDecodeError, TypeError):
                successor_tasks = []
        
        if not successor_tasks:
            return
        
        # 检查每个后置任务，如果满足生成条件，则生成
        for successor_id in successor_tasks:
            await TodoService.generate_task_if_ready(query_db, successor_id, todo_task.project_id)
    
    @staticmethod
    async def _check_and_activate_stages(
        query_db: AsyncSession,
        stage_id: Optional[int],
        project_id: int
    ) -> None:
        """
        检查并激活阶段
        
        :param query_db: orm对象
        :param stage_id: 阶段ID（关联proj_stage.stage_id）
        :param project_id: 项目ID
        """
        if not stage_id:
            return
        
        # 获取当前阶段
        todo_stage = await TodoStageDao.get_stage_by_id(query_db, stage_id)
        if not todo_stage:
            return
        
        # 检查阶段是否完成（所有任务都完成）
        all_tasks = await TodoTaskDao.get_tasks_by_project_id(query_db, project_id)
        stage_tasks = [t for t in all_tasks if t.stage_id == stage_id]
        
        all_tasks_completed = True
        for task in stage_tasks:
            if task.task_status != 3:  # 3-完成
                all_tasks_completed = False
                break
        
        # 如果阶段完成，更新阶段状态
        if all_tasks_completed and todo_stage.stage_status != 2:  # 2-已完成
            now = datetime.now()
            await TodoStageDao.update_stage_status(
                query_db, stage_id, 2,  # 已完成
                actual_complete_time=now
            )
            logger.info(f'阶段完成: stage_id={stage_id}')
            
            # 检查后置阶段（从 proj_stage 表获取，因为后置阶段可能还未生成）
            result = await query_db.execute(
                select(ProjStage).where(ProjStage.stage_id == stage_id, ProjStage.enable == '1')
            )
            proj_stage = result.scalar_one_or_none()
            
            if proj_stage:
                successor_stages = []
                if proj_stage.successor_stages:
                    try:
                        successor_stages = json.loads(proj_stage.successor_stages) if isinstance(proj_stage.successor_stages, str) else proj_stage.successor_stages
                    except (json.JSONDecodeError, TypeError):
                        successor_stages = []
                
                # 生成后置阶段（如果满足生成条件）
                for succ_stage_id in successor_stages:
                    await TodoService.generate_stage_if_ready(query_db, succ_stage_id, project_id)
    
    @staticmethod
    async def _activate_stage_if_ready(
        query_db: AsyncSession,
        stage_id: int,
        project_id: int
    ) -> None:
        """
        如果阶段就绪，激活阶段
        
        :param query_db: orm对象
        :param stage_id: 阶段ID
        :param project_id: 项目ID
        """
        todo_stage = await TodoStageDao.get_stage_by_id(query_db, stage_id)
        if not todo_stage:
            return
        
        # 检查前置阶段是否都完成
        predecessor_stages = []
        if todo_stage.predecessor_stages:
            try:
                predecessor_stages = json.loads(todo_stage.predecessor_stages)
            except (json.JSONDecodeError, TypeError):
                predecessor_stages = []
        
        all_predecessors_completed = True
        for pred_stage_id in predecessor_stages:
            pred_stage = await TodoStageDao.get_stage_by_id(query_db, pred_stage_id)
            if not pred_stage or pred_stage.stage_status != 2:  # 2-已完成
                all_predecessors_completed = False
                break
        
        # 如果所有前置阶段都完成，激活当前阶段
        if all_predecessors_completed and todo_stage.stage_status == 0:  # 0-未开始
            now = datetime.now()
            await TodoStageDao.update_stage_status(
                query_db, stage_id, 1,  # 进行中
                actual_start_time=now
            )
            logger.info(f'激活阶段: stage_id={stage_id}')
            
            # 激活该阶段中所有没有前置任务的任务
            all_tasks = await TodoTaskDao.get_tasks_by_project_id(query_db, project_id)
            stage_tasks = [t for t in all_tasks if t.stage_id == stage_id]
            
            for task in stage_tasks:
                predecessor_tasks = []
                if task.predecessor_tasks:
                    try:
                        predecessor_tasks = json.loads(task.predecessor_tasks)
                    except (json.JSONDecodeError, TypeError):
                        predecessor_tasks = []
                
                # 没有前置任务的任务 -> 进行中
                if len(predecessor_tasks) == 0 and task.task_status == 0:  # 0-未开始
                    await TodoTaskDao.update_task_status(
                        query_db, task.task_id, 1,  # 进行中
                        actual_start_time=now
                    )
                    logger.info(f'激活阶段头任务: task_id={task.task_id}')
    
    @staticmethod
    async def generate_task_if_ready(
        query_db: AsyncSession,
        task_id: int,
        project_id: int
    ) -> bool:
        """
        如果任务满足生成条件，生成任务
        1. 检查任务是否已在 todo_task 表中（如果已生成，跳过）
        2. 如果任务有归属阶段，检查该阶段是否已生成
        3. 检查任务是否满足生成条件（前置任务都完成）
        4. 如果满足，从 proj_task 表读取任务配置，插入到 todo_task 表
        5. 任务状态为 1（进行中），记录 actual_start_time
        
        :param query_db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :param project_id: 项目ID
        :return: True表示已生成，False表示未生成（不满足条件或已存在）
        """
        # 1. 检查任务是否已在 todo_task 表中
        existing_task = await TodoTaskDao.get_task_by_id(query_db, task_id)
        if existing_task:
            logger.debug(f'任务已存在，跳过生成: task_id={task_id}')
            return True
        
        # 2. 从 proj_task 表读取任务配置
        result = await query_db.execute(
            select(ProjTask).where(ProjTask.task_id == task_id, ProjTask.enable == '1')
        )
        proj_task = result.scalar_one_or_none()
        
        if not proj_task:
            logger.warning(f'任务配置不存在: task_id={task_id}')
            return False
        
        # 3. 如果任务有归属阶段，检查该阶段是否已生成
        if proj_task.stage_id is not None:
            existing_stage = await TodoStageDao.get_stage_by_id(query_db, proj_task.stage_id)
            if not existing_stage:
                logger.debug(f'任务所属阶段未生成，跳过任务生成: task_id={task_id}, stage_id={proj_task.stage_id}')
                return False
        
        # 4. 检查任务是否通过校验（信息完整且无校验失败）
        validation_passed = await TaskGenerationUtil.check_task_validation_status(query_db, task_id)
        if not validation_passed:
            logger.debug(f'任务校验未通过，不满足生成条件: task_id={task_id}')
            return False
        
        # 4.5. 如果任务有归属阶段，检查阶段时间是否会与已生成的前置/后置阶段产生冲突
        if proj_task.stage_id is not None:
            conflict_passed, conflict_message = await TaskGenerationUtil.check_stage_time_conflict_with_generated_stages(
                query_db, proj_task.stage_id, task_id
            )
            if not conflict_passed:
                logger.warning(f'任务生成失败，阶段时间冲突: {conflict_message}')
                return False
        
        # 5. 检查任务是否满足生成条件（前置任务都完成）
        can_generate = await TaskGenerationUtil.check_task_generation_condition(query_db, task_id)
        if not can_generate:
            logger.debug(f'任务不满足生成条件: task_id={task_id}')
            return False
        
        # 6. 解析JSON字段
        predecessor_tasks = []
        successor_tasks = []
        approval_nodes = []
        
        if proj_task.predecessor_tasks:
            try:
                predecessor_tasks = json.loads(proj_task.predecessor_tasks) if isinstance(proj_task.predecessor_tasks, str) else proj_task.predecessor_tasks
            except (json.JSONDecodeError, TypeError):
                predecessor_tasks = []
        
        if proj_task.successor_tasks:
            try:
                successor_tasks = json.loads(proj_task.successor_tasks) if isinstance(proj_task.successor_tasks, str) else proj_task.successor_tasks
            except (json.JSONDecodeError, TypeError):
                successor_tasks = []
        
        if proj_task.approval_nodes:
            try:
                approval_nodes = json.loads(proj_task.approval_nodes) if isinstance(proj_task.approval_nodes, str) else proj_task.approval_nodes
            except (json.JSONDecodeError, TypeError):
                approval_nodes = []
        
        # 7. 创建任务执行记录
        now = datetime.now()
        task_data = {
            'task_id': proj_task.task_id,
            'project_id': proj_task.project_id,
            'stage_id': proj_task.stage_id,
            'name': proj_task.name,
            'description': proj_task.description,
            'start_time': proj_task.start_time,
            'end_time': proj_task.end_time,
            'duration': proj_task.duration,
            'job_number': proj_task.job_number,
            'predecessor_tasks': json.dumps(predecessor_tasks) if predecessor_tasks else None,
            'successor_tasks': json.dumps(successor_tasks) if successor_tasks else None,
            'approval_nodes': json.dumps(approval_nodes) if approval_nodes else None,
            'task_status': 1,  # 进行中
            'is_skipped': 0,
            'actual_start_time': now,
        }
        
        await TodoTaskDao.create_task(query_db, task_data)
        logger.info(f'任务生成成功: task_id={task_id}, project_id={project_id}')
        
        return True
    
    @staticmethod
    async def generate_stage_if_ready(
        query_db: AsyncSession,
        stage_id: int,
        project_id: int
    ) -> bool:
        """
        如果阶段满足生成条件，生成阶段
        1. 检查阶段是否已在 todo_stage 表中（如果已生成，跳过）
        2. 检查阶段是否满足生成条件
        3. 如果满足，从 proj_stage 表读取阶段配置，插入到 todo_stage 表
        4. 阶段状态为 1（进行中），记录 actual_start_time
        5. 生成阶段后，检查阶段中的任务是否满足生成条件（生成阶段内的头任务）
        
        :param query_db: orm对象
        :param stage_id: 阶段ID（关联proj_stage.stage_id）
        :param project_id: 项目ID
        :return: True表示已生成，False表示未生成（不满足条件或已存在）
        """
        # 1. 检查阶段是否已在 todo_stage 表中
        existing_stage = await TodoStageDao.get_stage_by_id(query_db, stage_id)
        if existing_stage:
            logger.debug(f'阶段已存在，跳过生成: stage_id={stage_id}')
            return True
        
        # 2. 检查阶段是否满足生成条件
        can_generate = await TaskGenerationUtil.check_stage_generation_condition(query_db, stage_id)
        if not can_generate:
            logger.debug(f'阶段不满足生成条件: stage_id={stage_id}')
            return False
        
        # 3. 从 proj_stage 表读取阶段配置
        result = await query_db.execute(
            select(ProjStage).where(ProjStage.stage_id == stage_id, ProjStage.enable == '1')
        )
        proj_stage = result.scalar_one_or_none()
        
        if not proj_stage:
            logger.warning(f'阶段配置不存在: stage_id={stage_id}')
            return False
        
        # 4. 解析JSON字段
        predecessor_stages = []
        successor_stages = []
        
        if proj_stage.predecessor_stages:
            try:
                predecessor_stages = json.loads(proj_stage.predecessor_stages) if isinstance(proj_stage.predecessor_stages, str) else proj_stage.predecessor_stages
            except (json.JSONDecodeError, TypeError):
                predecessor_stages = []
        
        if proj_stage.successor_stages:
            try:
                successor_stages = json.loads(proj_stage.successor_stages) if isinstance(proj_stage.successor_stages, str) else proj_stage.successor_stages
            except (json.JSONDecodeError, TypeError):
                successor_stages = []
        
        # 5. 创建阶段执行记录
        now = datetime.now()
        stage_data = {
            'stage_id': proj_stage.stage_id,
            'project_id': proj_stage.project_id,
            'stage_status': 1,  # 进行中
            'predecessor_stages': json.dumps(predecessor_stages) if predecessor_stages else None,
            'successor_stages': json.dumps(successor_stages) if successor_stages else None,
            'actual_start_time': now,
            'create_time': now,
            'update_time': now,
        }
        
        await TodoStageDao.create_stage(query_db, stage_data)
        logger.info(f'阶段生成成功: stage_id={stage_id}, project_id={project_id}')
        
        # 6. 生成阶段后，检查阶段中的任务是否满足生成条件（生成阶段内的头任务）
        # 获取阶段中的所有任务
        proj_tasks = await TaskDao.get_tasks_by_project_id(query_db, project_id)
        stage_tasks = [t for t in proj_tasks if t.stage_id == stage_id]
        
        for proj_task in stage_tasks:
            # 检查任务是否没有前置任务（阶段内的头任务）
            predecessor_tasks = []
            if proj_task.predecessor_tasks:
                try:
                    predecessor_tasks = json.loads(proj_task.predecessor_tasks) if isinstance(proj_task.predecessor_tasks, str) else proj_task.predecessor_tasks
                except (json.JSONDecodeError, TypeError):
                    predecessor_tasks = []
            
            # 如果任务没有前置任务，检查校验状态后再生成
            if not predecessor_tasks:
                # 检查任务是否通过校验（信息完整且无校验失败）
                validation_passed = await TaskGenerationUtil.check_task_validation_status(query_db, proj_task.task_id)
                if validation_passed:
                    await TodoService.generate_task_if_ready(query_db, proj_task.task_id, project_id)
                else:
                    logger.debug(f'阶段内头任务校验未通过，跳过生成: task_id={proj_task.task_id}, stage_id={stage_id}')
        
        return True
