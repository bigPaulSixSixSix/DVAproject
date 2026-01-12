import json
from datetime import datetime, date as DateType
from typing import Optional, Union
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from module_task.configuration.dao.task_dao import TaskDao
from module_task.entity.do.proj_stage_do import ProjStage
from module_task.entity.do.proj_task_do import ProjTask
from module_task.entity.vo.task_vo import StageModel, TaskModel, TaskConfigPayload
from module_task.todo.utils.task_generation_util import TaskGenerationUtil
from exceptions.exception import ServiceException
from utils.log_util import logger


class TaskPersistence:
    """
    任务配置持久化器
    负责所有数据持久化相关的逻辑
    """

    @classmethod
    async def persist_task_config(
        cls,
        query_db: AsyncSession,
        payload: TaskConfigPayload,
        current_user_id: int,
        current_user_name: str,
        generate_tasks: bool = False,
    ):
        """
        数据持久化
        包含：全量更新逻辑（新增/更新/删除）

        :param query_db: orm对象
        :param payload: 任务配置数据对象
        :param current_user_id: 当前用户ID
        :param current_user_name: 当前用户名
        :param generate_tasks: 是否在保存后生成任务（True-保存并生成，False-仅保存）
        :return: 无返回值，失败抛出异常
        """
        project_id = int(payload.project_id)
        logger.info(f'开始数据持久化 - projectId: {project_id}, stages: {len(payload.stages)}, tasks: {len(payload.tasks)}')

        # ===== 步骤1：读取现有数据（使用行锁） =====
        existing_stages = await TaskDao.get_stages_by_project_id_with_lock(query_db, project_id)
        existing_tasks = await TaskDao.get_tasks_by_project_id_with_lock(query_db, project_id)

        # 构建现有数据的映射（以数据库ID为key）
        existing_stages_map = {stage.stage_id: stage for stage in existing_stages}
        existing_tasks_map = {task.task_id: task for task in existing_tasks}

        # ===== 步骤1.5：检查编辑限制 =====
        await cls._check_edit_permissions(query_db, payload.stages, payload.tasks, existing_stages_map, existing_tasks_map)

        # ===== 步骤2：处理阶段数据 =====
        # 返回临时ID到真实ID的映射
        stage_id_mapping = await cls._process_stages(
            query_db, payload.stages, existing_stages_map, project_id, current_user_name
        )

        # ===== 步骤2.5：更新阶段的前置/后置阶段ID（将临时ID转换为真实ID） =====
        await cls._update_stage_dependencies(query_db, payload.stages, stage_id_mapping, current_user_name)

        # ===== 步骤3：处理任务数据 =====
        # 传递stage_id映射，用于更新任务的stage_id
        # 返回任务临时ID到真实ID的映射
        task_id_mapping = await cls._process_tasks(
            query_db, payload.tasks, existing_tasks_map, project_id, current_user_name, stage_id_mapping
        )

        logger.info('数据持久化完成')
        
        # ===== 步骤4：保存后检查并生成满足条件的任务 =====
        if generate_tasks:
            await cls._check_and_generate_tasks_after_save(query_db, project_id, payload.tasks, existing_tasks_map, task_id_mapping)

    @classmethod
    async def _process_stages(
        cls,
        query_db: AsyncSession,
        stages: list[StageModel],
        existing_stages_map: dict,
        project_id: int,
        current_user_name: str,
    ) -> dict:
        """
        处理阶段数据（新增/更新/删除）

        :param query_db: orm对象
        :param stages: 前端传入的阶段列表
        :param existing_stages_map: 现有阶段映射（stage_id -> stage对象）
        :param project_id: 项目ID
        :param current_user_name: 当前用户名
        :return: 临时ID到真实ID的映射字典 {temp_id: real_id}
        """
        stage_id_mapping = {}  # 临时ID -> 真实ID的映射
        payload_stage_ids = {stage.id for stage in stages if stage.id > 0}

        for stage in stages:
            identifier = stage.id
            is_temp_id = identifier <= 0

            stage_data = cls._prepare_stage_data(stage, project_id, current_user_name)

            if is_temp_id:
                logger.info(f'新增阶段: {stage.name} (临时ID: {identifier})')
                new_stage = await TaskDao.add_stage_dao(query_db, stage_data)
                stage_id_mapping[identifier] = new_stage.stage_id
                logger.info(f'阶段新增成功，真实ID: {new_stage.stage_id}')
            else:
                existing_stage = existing_stages_map.get(identifier)
                if existing_stage:
                    stage_data['stage_id'] = existing_stage.stage_id
                    logger.info(f'更新阶段: {stage.name} (ID: {identifier})')
                    await TaskDao.update_stage_dao(query_db, stage_data)
                else:
                    logger.info(f'新增阶段: {stage.name} (ID: {identifier})')
                    new_stage = await TaskDao.add_stage_dao(query_db, stage_data)
                    stage_id_mapping[identifier] = new_stage.stage_id

        # 软删除：数据库中存在但前端数据中不存在的阶段
        for stage_id, existing_stage in existing_stages_map.items():
            if stage_id not in payload_stage_ids and existing_stage.enable == '1':
                # 检查阶段是否已生成，已生成的阶段不允许删除
                is_generated = not await TaskGenerationUtil.is_stage_editable(query_db, stage_id)
                if is_generated:
                    raise ServiceException(
                        message=f'阶段【{existing_stage.name}】已生成，不允许删除'
                    )
                logger.info(f'软删除阶段: {existing_stage.name} (ID: {existing_stage.stage_id})')
                await TaskDao.soft_delete_stage_dao(query_db, existing_stage.stage_id, current_user_name)

        return stage_id_mapping

    @classmethod
    async def _process_tasks(
        cls,
        query_db: AsyncSession,
        tasks: list[TaskModel],
        existing_tasks_map: dict,
        project_id: int,
        current_user_name: str,
        stage_id_mapping: dict = None,
    ):
        """
        处理任务数据（新增/更新/删除）

        :param query_db: orm对象
        :param tasks: 前端传入的任务列表
        :param existing_tasks_map: 现有任务映射（frontend_id -> task对象）
        :param project_id: 项目ID
        :param current_user_name: 当前用户名
        :param stage_id_mapping: 阶段临时ID到真实ID的映射
        :return: 任务临时ID到真实ID的映射字典 {temp_id: real_id}
        """
        if stage_id_mapping is None:
            stage_id_mapping = {}
        task_id_mapping = {}  # 临时ID -> 真实ID的映射
        frontend_task_ids = {task.id for task in tasks if task.id > 0}

        # 处理每个任务
        for task in tasks:
            task_id_frontend = task.id
            is_temp_id = task_id_frontend <= 0  # 临时ID（负数或0）

            # 处理任务的stage_id：如果是临时ID，转换为真实ID
            task_stage_id = task.stage_id
            if task_stage_id is not None and task_stage_id < 0:
                if task_stage_id in stage_id_mapping:
                    task_stage_id = stage_id_mapping[task_stage_id]
                    logger.info(f'任务 {task.name} 的stage_id从临时ID {task.stage_id} 转换为真实ID {task_stage_id}')
                else:
                    logger.warning(f'任务 {task.name} 的stage_id是临时ID {task.stage_id}，但在stage_id_mapping中未找到，将设置为None')
                    task_stage_id = None

            # 注意：在第一次保存时，predecessor_tasks 和 successor_tasks 可能包含临时ID
            # 这些临时ID会在 _update_task_dependencies 中统一转换
            # 所以这里先保存原始数据（可能包含临时ID），后续再统一更新
            task_data = cls._prepare_task_data(task, project_id, current_user_name, task_stage_id)

            if is_temp_id:
                # 临时ID：新增
                logger.info(f'新增任务: {task.name} (临时ID: {task_id_frontend})')
                new_task = await TaskDao.add_task_dao(query_db, task_data)
                # 记录临时ID到真实ID的映射
                task_id_mapping[task_id_frontend] = new_task.task_id
                logger.info(f'任务新增成功，真实ID: {new_task.task_id}')
            else:
                # 真实ID：更新或新增
                if task_id_frontend in existing_tasks_map:
                    # 更新现有任务
                    existing_task = existing_tasks_map[task_id_frontend]
                    task_data['task_id'] = existing_task.task_id
                    logger.info(f'更新任务: {task.name} (ID: {task_id_frontend})')
                    await TaskDao.update_task_dao(query_db, task_data)
                else:
                    # 前端ID存在但数据库中没有，可能是新数据，执行新增
                    logger.info(f'新增任务: {task.name} (ID: {task_id_frontend})')
                    new_task = await TaskDao.add_task_dao(query_db, task_data)
                    task_id_mapping[task_id_frontend] = new_task.task_id

        # 软删除：数据库中存在但前端数据中不存在的任务
        for frontend_id, existing_task in existing_tasks_map.items():
            if frontend_id not in frontend_task_ids and existing_task.enable == '1':
                # 检查任务是否已生成，已生成的任务不允许删除
                is_generated = not await TaskGenerationUtil.is_task_editable(query_db, existing_task.task_id)
                if is_generated:
                    raise ServiceException(
                        message=f'任务【{existing_task.name}】已生成，不允许删除'
                    )
                logger.info(f'软删除任务: {existing_task.name} (ID: {existing_task.task_id})')
                await TaskDao.soft_delete_task_dao(query_db, existing_task.task_id, current_user_name)

        # 第二遍：更新所有任务的前置/后置任务ID（将临时ID转换为真实ID）
        await cls._update_task_dependencies(query_db, tasks, task_id_mapping, current_user_name)

        return task_id_mapping

    @classmethod
    async def _update_task_dependencies(
        cls,
        query_db: AsyncSession,
        tasks: list[TaskModel],
        task_id_mapping: dict,
        current_user_name: str,
    ):
        """
        更新任务的前置/后置任务ID（将临时ID转换为真实ID）

        :param query_db: orm对象
        :param tasks: 前端传入的任务列表
        :param task_id_mapping: 临时ID到真实ID的映射
        :param current_user_name: 当前用户名
        """
        from sqlalchemy import select
        
        for task in tasks:
            task_identifier = task.id
            # 获取数据库ID
            if task_identifier > 0:
                task_db_id = task_identifier
            elif task_identifier in task_id_mapping:
                # 临时ID，使用映射后的真实ID
                task_db_id = task_id_mapping[task_identifier]
            else:
                continue  # 跳过无法找到数据库ID的任务

            # 转换前置/后置任务ID（将临时ID转换为真实ID）
            predecessor_tasks = cls._convert_task_ids(task.predecessor_tasks, task_id_mapping)
            successor_tasks = cls._convert_task_ids(task.successor_tasks, task_id_mapping)

            # 从数据库读取当前值，用于比较
            db_task_result = await query_db.execute(
                select(ProjTask.predecessor_tasks, ProjTask.successor_tasks)
                .where(ProjTask.task_id == task_db_id)
            )
            db_task = db_task_result.first()
            if not db_task:
                continue

            # 解析数据库中的当前值
            db_predecessor_tasks = []
            db_successor_tasks = []
            if db_task.predecessor_tasks:
                try:
                    db_predecessor_tasks = json.loads(db_task.predecessor_tasks)
                except (json.JSONDecodeError, TypeError):
                    db_predecessor_tasks = []
            if db_task.successor_tasks:
                try:
                    db_successor_tasks = json.loads(db_task.successor_tasks)
                except (json.JSONDecodeError, TypeError):
                    db_successor_tasks = []

            # 检查是否需要更新（与数据库中的值比较）
            need_update = False
            update_data = {'update_by': current_user_name, 'update_time': datetime.now()}

            # 检查前置任务ID是否需要更新
            if sorted(predecessor_tasks) != sorted(db_predecessor_tasks):
                update_data['predecessor_tasks'] = json.dumps(predecessor_tasks) if predecessor_tasks else None
                need_update = True

            # 检查后置任务ID是否需要更新
            if sorted(successor_tasks) != sorted(db_successor_tasks):
                update_data['successor_tasks'] = json.dumps(successor_tasks) if successor_tasks else None
                need_update = True

            # 如果需要更新，执行更新
            if need_update:
                await query_db.execute(
                    update(ProjTask)
                    .where(ProjTask.task_id == task_db_id)
                    .values(**update_data)
                )
                logger.info(f'更新任务 {task.name} (ID: {task_db_id}) 的前置/后置任务ID: predecessor={predecessor_tasks}, successor={successor_tasks}')
                
                # 如果任务已生成，同步更新 todo_task 表的后置任务关系
                # 注意：只更新后置任务关系，前置任务关系不允许修改（已在编辑限制检查中处理）
                from module_task.todo.dao.todo_task_dao import TodoTaskDao
                from module_task.entity.do.todo_task_do import TodoTask
                
                todo_task = await TodoTaskDao.get_task_by_id(query_db, task_db_id)
                if todo_task:
                    # 只更新后置任务关系（如果后置任务关系有变化）
                    if 'successor_tasks' in update_data:
                        await query_db.execute(
                            update(TodoTask)
                            .where(TodoTask.task_id == task_db_id)
                            .values(successor_tasks=update_data['successor_tasks'])
                        )
                        logger.info(f'同步更新已生成任务 {task.name} (ID: {task_db_id}) 的 todo_task 表后置任务关系')

    @classmethod
    async def _update_stage_dependencies(
        cls,
        query_db: AsyncSession,
        stages: list[StageModel],
        stage_id_mapping: dict,
        current_user_name: str,
    ):
        """
        更新阶段的前置/后置阶段ID（将临时ID转换为真实ID）

        :param query_db: orm对象
        :param stages: 前端传入的阶段列表
        :param stage_id_mapping: 临时ID到真实ID的映射
        :param current_user_name: 当前用户名
        """
        from sqlalchemy import select
        
        for stage in stages:
            stage_identifier = stage.id
            # 获取数据库ID
            if stage_identifier > 0:
                stage_db_id = stage_identifier
            elif stage_identifier in stage_id_mapping:
                # 临时ID，使用映射后的真实ID
                stage_db_id = stage_id_mapping[stage_identifier]
            else:
                continue  # 跳过无法找到数据库ID的阶段

            # 转换前置/后置阶段ID（将临时ID转换为真实ID）
            predecessor_stages = cls._convert_stage_ids(stage.predecessor_stages, stage_id_mapping)
            successor_stages = cls._convert_stage_ids(stage.successor_stages, stage_id_mapping)

            # 从数据库读取当前值，用于比较
            db_stage_result = await query_db.execute(
                select(ProjStage.predecessor_stages, ProjStage.successor_stages)
                .where(ProjStage.stage_id == stage_db_id)
            )
            db_stage = db_stage_result.first()
            if not db_stage:
                continue

            # 解析数据库中的当前值
            db_predecessor_stages = []
            db_successor_stages = []
            if db_stage.predecessor_stages:
                try:
                    db_predecessor_stages = json.loads(db_stage.predecessor_stages)
                except (json.JSONDecodeError, TypeError):
                    db_predecessor_stages = []
            if db_stage.successor_stages:
                try:
                    db_successor_stages = json.loads(db_stage.successor_stages)
                except (json.JSONDecodeError, TypeError):
                    db_successor_stages = []

            # 检查是否需要更新（与数据库中的值比较）
            need_update = False
            update_data = {'update_by': current_user_name, 'update_time': datetime.now()}

            # 检查前置阶段ID是否需要更新
            if sorted(predecessor_stages) != sorted(db_predecessor_stages):
                update_data['predecessor_stages'] = json.dumps(predecessor_stages) if predecessor_stages else None
                need_update = True

            # 检查后置阶段ID是否需要更新
            if sorted(successor_stages) != sorted(db_successor_stages):
                update_data['successor_stages'] = json.dumps(successor_stages) if successor_stages else None
                need_update = True

            # 如果需要更新，执行更新
            if need_update:
                await query_db.execute(
                    update(ProjStage)
                    .where(ProjStage.stage_id == stage_db_id)
                    .values(**update_data)
                )
                logger.info(f'更新阶段 {stage.name} (ID: {stage_db_id}) 的前置/后置阶段ID: predecessor={predecessor_stages}, successor={successor_stages}')
                
                # 如果阶段已生成，同步更新 todo_stage 表的后置阶段关系
                # 注意：只更新后置阶段关系，前置阶段关系不允许修改（已在编辑限制检查中处理）
                from module_task.todo.dao.todo_stage_dao import TodoStageDao
                from module_task.entity.do.todo_stage_do import TodoStage
                
                todo_stage = await TodoStageDao.get_stage_by_id(query_db, stage_db_id)
                if todo_stage:
                    # 只更新后置阶段关系（如果后置阶段关系有变化）
                    if 'successor_stages' in update_data:
                        await query_db.execute(
                            update(TodoStage)
                            .where(TodoStage.stage_id == stage_db_id)
                            .values(successor_stages=update_data['successor_stages'])
                        )
                        logger.info(f'同步更新已生成阶段 {stage.name} (ID: {stage_db_id}) 的 todo_stage 表后置阶段关系')

    @classmethod
    def _convert_stage_ids(cls, stage_ids: list[int], stage_id_mapping: dict) -> list[int]:
        """
        将阶段ID列表中的临时ID转换为真实ID

        :param stage_ids: 阶段ID列表
        :param stage_id_mapping: 临时ID到真实ID的映射
        :return: 转换后的阶段ID列表
        """
        if not stage_ids:
            return []
        converted_ids = []
        for identifier in stage_ids:
            if identifier in stage_id_mapping:
                converted_ids.append(stage_id_mapping[identifier])
            else:
                converted_ids.append(identifier)
        return converted_ids

    @classmethod
    def _convert_task_ids(cls, task_ids: list[int], task_id_mapping: dict) -> list[int]:
        """
        将任务ID列表中的临时ID转换为真实ID

        :param task_ids: 任务ID列表
        :param task_id_mapping: 临时ID到真实ID的映射
        :return: 转换后的任务ID列表
        """
        if not task_ids:
            return []
        converted_ids = []
        for identifier in task_ids:
            if identifier in task_id_mapping:
                converted_ids.append(task_id_mapping[identifier])
            else:
                converted_ids.append(identifier)
        return converted_ids

    @classmethod
    def _prepare_stage_data(cls, stage: StageModel, project_id: int, current_user_name: str) -> dict:
        """
        准备阶段数据字典（用于数据库操作）

        :param stage: 阶段模型
        :param project_id: 项目ID
        :param current_user_name: 当前用户名
        :return: 阶段数据字典
        """
        now = datetime.now()
        stage_data = {
            'project_id': project_id,
            'name': stage.name,
            'start_time': cls._normalize_date(stage.start_time),
            'end_time': cls._normalize_date(stage.end_time),
            'duration': stage.duration,
            'predecessor_stages': json.dumps(stage.predecessor_stages) if stage.predecessor_stages else None,
            'successor_stages': json.dumps(stage.successor_stages) if stage.successor_stages else None,
            'position': json.dumps(stage.position.model_dump()) if stage.position else None,
            'enable': '1',
            'update_by': current_user_name,
            'update_time': now,
        }

        if stage.id <= 0:
            stage_data['create_by'] = current_user_name
            stage_data['create_time'] = now

        return stage_data

    @classmethod
    def _prepare_task_data(cls, task: TaskModel, project_id: int, current_user_name: str, stage_id: int = None) -> dict:
        """
        准备任务数据字典（用于数据库操作）

        :param task: 任务模型
        :param project_id: 项目ID
        :param current_user_name: 当前用户名
        :param stage_id: 阶段ID（如果提供，使用此值；否则使用task.stage_id）
        :return: 任务数据字典
        """
        now = datetime.now()
        resolved_stage_id = stage_id if stage_id is not None else task.stage_id
        if isinstance(resolved_stage_id, int) and resolved_stage_id <= 0:
            resolved_stage_id = None

        task_data = {
            'project_id': project_id,
            'stage_id': resolved_stage_id,
            'name': task.name,
            'description': task.description,
            'start_time': cls._normalize_date(task.start_time),
            'end_time': cls._normalize_date(task.end_time),
            'duration': task.duration,
            'job_number': task.job_number if task.job_number else None,
            'predecessor_tasks': json.dumps(task.predecessor_tasks) if task.predecessor_tasks else None,
            'successor_tasks': json.dumps(task.successor_tasks) if task.successor_tasks else None,
            'position': json.dumps(task.position.model_dump()) if task.position else None,
            'approval_type': task.approval_type if task.approval_type else None,
            'approval_nodes': json.dumps(task.approval_nodes) if task.approval_nodes else None,
            'enable': '1',
            'update_by': current_user_name,
            'update_time': now,
        }

        if task.id <= 0:
            task_data['create_by'] = current_user_name
            task_data['create_time'] = now

        return task_data

    @staticmethod
    def _normalize_date(value: Optional[Union[str, datetime, DateType]]) -> Optional[DateType]:
        """
        将字符串或datetime/date对象转换为日期
        """
        if value is None or value == '':
            return None

        if isinstance(value, DateType) and not isinstance(value, datetime):
            return value

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError as exc:
                raise ValueError('日期格式必须为YYYY-MM-DD') from exc

        raise ValueError('日期格式必须为YYYY-MM-DD')
    
    @classmethod
    async def _check_edit_permissions(
        cls,
        query_db: AsyncSession,
        stages: list[StageModel],
        tasks: list[TaskModel],
        existing_stages_map: dict,
        existing_tasks_map: dict,
    ) -> None:
        """
        检查编辑权限
        对于已生成的任务/阶段，只允许编辑后置关系，不允许编辑其他字段
        
        :param query_db: orm对象
        :param stages: 前端传入的阶段列表
        :param tasks: 前端传入的任务列表
        :param existing_stages_map: 现有阶段映射
        :param existing_tasks_map: 现有任务映射
        """
        # 检查阶段的编辑权限
        for stage in stages:
            stage_id = stage.id
            if stage_id > 0 and stage_id in existing_stages_map:
                # 这是已存在的阶段，检查是否已生成
                is_generated = not await TaskGenerationUtil.is_stage_editable(query_db, stage_id)
                if is_generated:
                    # 已生成的阶段，检查是否尝试修改不允许修改的字段
                    existing_stage = existing_stages_map[stage_id]
                    
                    # 检查名称是否被修改（已生成的阶段不允许修改名称）
                    # 注意：开始时间、结束时间、时长允许修改，因为添加新任务可能会改变阶段的时间范围
                    if stage.name != existing_stage.name:
                        raise ServiceException(
                            message=f'阶段【{stage.name}】已生成，不允许修改阶段名称'
                        )
                    
                    # 检查前置关系是否被修改（不允许修改前置关系）
                    existing_predecessor_stages = []
                    if existing_stage.predecessor_stages:
                        try:
                            existing_predecessor_stages = json.loads(existing_stage.predecessor_stages) if isinstance(existing_stage.predecessor_stages, str) else existing_stage.predecessor_stages
                        except (json.JSONDecodeError, TypeError):
                            existing_predecessor_stages = []
                    
                    new_predecessor_stages = stage.predecessor_stages or []
                    if sorted(existing_predecessor_stages) != sorted(new_predecessor_stages):
                        raise ServiceException(
                            message=f'阶段【{stage.name}】已生成，不允许修改前置关系'
                        )
                    
                    # 检查后置关系（允许修改，但只限于添加/删除未生成的阶段）
                    existing_successor_stages = []
                    if existing_stage.successor_stages:
                        try:
                            existing_successor_stages = json.loads(existing_stage.successor_stages) if isinstance(existing_stage.successor_stages, str) else existing_stage.successor_stages
                        except (json.JSONDecodeError, TypeError):
                            existing_successor_stages = []
                    
                    new_successor_stages = stage.successor_stages or []
                    # 检查新增的后置阶段是否都是未生成的
                    added_successor_stages = [s for s in new_successor_stages if s not in existing_successor_stages]
                    for succ_id in added_successor_stages:
                        if not await TaskGenerationUtil.is_stage_editable(query_db, succ_id):
                            raise ServiceException(
                                message=f'阶段【{stage.name}】已生成，只能添加未生成的阶段作为后置阶段'
                            )
        
        # 检查任务的编辑权限
        for task in tasks:
            task_id = task.id
            if task_id > 0 and task_id in existing_tasks_map:
                # 这是已存在的任务，检查是否已生成
                is_generated = not await TaskGenerationUtil.is_task_editable(query_db, task_id)
                if is_generated:
                    # 已生成的任务，检查是否尝试修改不允许修改的字段
                    existing_task = existing_tasks_map[task_id]
                    
                    # 检查基本信息是否被修改
                    if (task.name != existing_task.name or
                        task.description != existing_task.description or
                        task.start_time != existing_task.start_time or
                        task.end_time != existing_task.end_time or
                        task.duration != existing_task.duration or
                        task.job_number != existing_task.job_number or
                        task.approval_type != existing_task.approval_type):
                        raise ServiceException(
                            message=f'任务【{task.name}】已生成，不允许修改基本信息（名称、描述、时间、负责人、审批模式等）'
                        )
                    
                    # 检查审批节点是否被修改
                    existing_approval_nodes = []
                    if existing_task.approval_nodes:
                        try:
                            existing_approval_nodes = json.loads(existing_task.approval_nodes) if isinstance(existing_task.approval_nodes, str) else existing_task.approval_nodes
                        except (json.JSONDecodeError, TypeError):
                            existing_approval_nodes = []
                    
                    new_approval_nodes = task.approval_nodes or []
                    if sorted(existing_approval_nodes) != sorted(new_approval_nodes):
                        raise ServiceException(
                            message=f'任务【{task.name}】已生成，不允许修改审批节点'
                        )
                    
                    # 检查前置关系是否被修改（不允许修改前置关系）
                    existing_predecessor_tasks = []
                    if existing_task.predecessor_tasks:
                        try:
                            existing_predecessor_tasks = json.loads(existing_task.predecessor_tasks) if isinstance(existing_task.predecessor_tasks, str) else existing_task.predecessor_tasks
                        except (json.JSONDecodeError, TypeError):
                            existing_predecessor_tasks = []
                    
                    new_predecessor_tasks = task.predecessor_tasks or []
                    if sorted(existing_predecessor_tasks) != sorted(new_predecessor_tasks):
                        raise ServiceException(
                            message=f'任务【{task.name}】已生成，不允许修改前置关系'
                        )
                    
                    # 检查后置关系（允许修改，但只限于添加/删除未生成的任务）
                    existing_successor_tasks = []
                    if existing_task.successor_tasks:
                        try:
                            existing_successor_tasks = json.loads(existing_task.successor_tasks) if isinstance(existing_task.successor_tasks, str) else existing_task.successor_tasks
                        except (json.JSONDecodeError, TypeError):
                            existing_successor_tasks = []
                    
                    new_successor_tasks = task.successor_tasks or []
                    # 检查新增的后置任务是否都是未生成的
                    added_successor_tasks = [t for t in new_successor_tasks if t not in existing_successor_tasks]
                    for succ_id in added_successor_tasks:
                        if not await TaskGenerationUtil.is_task_editable(query_db, succ_id):
                            raise ServiceException(
                                message=f'任务【{task.name}】已生成，只能添加未生成的任务作为后置任务'
                            )
    
    @classmethod
    async def _check_and_generate_tasks_after_save(
        cls,
        query_db: AsyncSession,
        project_id: int,
        tasks: list[TaskModel],
        existing_tasks_map: dict,
        task_id_mapping: dict,
    ) -> None:
        """
        保存后检查并生成满足条件的任务
        无论项目是否已生成任务，都会执行生成逻辑
        
        :param query_db: orm对象
        :param project_id: 项目ID
        :param tasks: 前端传入的任务列表
        :param existing_tasks_map: 现有任务映射
        :param task_id_mapping: 任务临时ID到真实ID的映射
        """
        from module_task.todo.service.todo_service import TodoService
        
        # 获取所有需要检查的任务ID（新增和编辑的任务）
        task_ids_to_check = set()
        
        # 1. 新增的任务（临时ID）
        for task in tasks:
            if task.id <= 0 and task.id in task_id_mapping:
                task_ids_to_check.add(task_id_mapping[task.id])
        
        # 2. 编辑的任务（真实ID）
        for task in tasks:
            if task.id > 0 and task.id in existing_tasks_map:
                task_ids_to_check.add(task.id)
        
        # 3. 检查由于前后置关系变更而新满足生成条件的任务
        # 获取所有任务的前置/后置关系，检查是否有任务因为关系变更而满足生成条件
        all_proj_tasks = await TaskDao.get_tasks_by_project_id(query_db, project_id)
        all_task_ids = {task.task_id for task in all_proj_tasks}
        
        # 检查所有未生成的任务是否满足生成条件
        for task_id in all_task_ids:
            # 如果任务已生成，跳过
            if not await TaskGenerationUtil.is_task_editable(query_db, task_id):
                continue
            
            # 检查任务是否通过校验（信息完整且无校验失败）
            validation_passed = await TaskGenerationUtil.check_task_validation_status(query_db, task_id)
            if not validation_passed:
                logger.debug(f'任务校验未通过，跳过生成: task_id={task_id}')
                continue
            
            # 检查任务是否满足生成条件（前置任务都完成）
            can_generate = await TaskGenerationUtil.check_task_generation_condition(query_db, task_id)
            if can_generate:
                # 生成任务
                await TodoService.generate_task_if_ready(query_db, task_id, project_id)
        
        # 检查所有未生成的阶段是否满足生成条件
        all_proj_stages = await TaskDao.get_stages_by_project_id(query_db, project_id)
        all_stage_ids = {stage.stage_id for stage in all_proj_stages}
        
        for stage_id in all_stage_ids:
            # 如果阶段已生成，跳过
            if not await TaskGenerationUtil.is_stage_editable(query_db, stage_id):
                continue
            
            # 检查阶段是否满足生成条件
            can_generate = await TaskGenerationUtil.check_stage_generation_condition(query_db, stage_id)
            if can_generate:
                # 生成阶段
                await TodoService.generate_stage_if_ready(query_db, stage_id, project_id)

