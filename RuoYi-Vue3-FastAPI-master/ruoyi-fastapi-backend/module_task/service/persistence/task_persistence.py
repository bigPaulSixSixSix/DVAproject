import json
from datetime import datetime, date as DateType
from typing import Optional, Union
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from module_task.dao.task_dao import TaskDao
from module_task.entity.do.proj_stage_do import ProjStage
from module_task.entity.do.proj_task_do import ProjTask
from module_task.entity.vo.task_vo import StageModel, TaskModel, TaskConfigPayload
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
    ):
        """
        数据持久化
        包含：全量更新逻辑（新增/更新/删除）

        :param query_db: orm对象
        :param payload: 任务配置数据对象
        :param current_user_id: 当前用户ID
        :param current_user_name: 当前用户名
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

