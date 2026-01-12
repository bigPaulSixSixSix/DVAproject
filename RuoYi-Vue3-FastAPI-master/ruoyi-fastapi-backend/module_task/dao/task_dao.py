from datetime import datetime
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from module_task.entity.do.proj_stage_do import ProjStage
from module_task.entity.do.proj_task_do import ProjTask
from module_task.entity.vo.task_vo import TaskConfigModel, TaskConfigPageQueryModel
from utils.page_util import PageUtil


class TaskDao:
    """
    任务配置模块数据库操作层
    """

    @classmethod
    async def get_stages_by_project_id(cls, db: AsyncSession, project_id: int):
        """
        根据项目ID获取所有阶段（仅查询有效数据，enable='0'）

        :param db: orm对象
        :param project_id: 项目ID
        :return: 阶段列表
        """
        stages = (
            (
                await db.execute(
                    select(ProjStage)
                    .where(ProjStage.project_id == project_id, ProjStage.enable == '1')
                    .order_by(ProjStage.stage_id)
                )
            )
            .scalars()
            .all()
        )
        return stages

    @classmethod
    async def get_tasks_by_project_id(cls, db: AsyncSession, project_id: int):
        """
        根据项目ID获取所有任务（仅查询有效数据，enable='0'）

        :param db: orm对象
        :param project_id: 项目ID
        :return: 任务列表
        """
        tasks = (
            (
                await db.execute(
                    select(ProjTask)
                    .where(ProjTask.project_id == project_id, ProjTask.enable == '1')
                    .order_by(ProjTask.task_id)
                )
            )
            .scalars()
            .all()
        )
        return tasks

    @classmethod
    async def get_project_statistics(cls, db: AsyncSession):
        """
        获取各项目的阶段/任务统计信息

        :param db: orm对象
        :return: 字典列表
        """
        stage_rows = (
            (
                await db.execute(
                    select(
                        ProjStage.project_id,
                        func.count(ProjStage.stage_id).label('stage_count'),
                        func.min(ProjStage.create_time).label('stage_min_create'),
                        func.max(ProjStage.update_time).label('stage_max_update'),
                    )
                    .where(ProjStage.enable == '1')
                    .group_by(ProjStage.project_id)
                )
            )
            .all()
        )

        task_rows = (
            (
                await db.execute(
                    select(
                        ProjTask.project_id,
                        func.count(ProjTask.task_id).label('task_count'),
                        func.min(ProjTask.create_time).label('task_min_create'),
                        func.max(ProjTask.update_time).label('task_max_update'),
                    )
                    .where(ProjTask.enable == '1')
                    .group_by(ProjTask.project_id)
                )
            )
            .all()
        )

        stats_map = {}
        for row in stage_rows:
            project_id = row.project_id
            stats_map[project_id] = {
                'stage_count': row.stage_count or 0,
                'task_count': 0,
                'create_time': row.stage_min_create,
                'update_time': row.stage_max_update,
            }

        for row in task_rows:
            project_id = row.project_id
            stats = stats_map.setdefault(
                project_id,
                {'stage_count': 0, 'task_count': 0, 'create_time': None, 'update_time': None},
            )
            stats['task_count'] = row.task_count or 0
            # 创建时间取阶段/任务最早者
            candidates = [stats['create_time'], row.task_min_create]
            stats['create_time'] = min([dt for dt in candidates if dt], default=None)
            # 更新时间取阶段/任务最晚者
            candidates = [stats['update_time'], row.task_max_update]
            stats['update_time'] = max([dt for dt in candidates if dt], default=None)

        return stats_map

    @classmethod
    async def get_project_validation_statistics(cls, db: AsyncSession):
        """
        获取各项目的验证统计信息
        包括：信息缺失数（仅任务：负责人、开始时间、结束时间、审批层级）、时间关系异常数（阶段+任务）、未分配到阶段数（仅任务）、项目状态

        :param db: orm对象
        :return: 字典 {project_id: {missing_info_count, time_relation_error_count, unassigned_stage_count, project_status}}
        """
        import json
        from datetime import date as DateType

        # 查询所有有效任务
        tasks = (
            (
                await db.execute(
                    select(ProjTask)
                    .where(ProjTask.enable == '1')
                    .order_by(ProjTask.project_id, ProjTask.task_id)
                )
            )
            .scalars()
            .all()
        )

        # 查询所有有效阶段
        stages = (
            (
                await db.execute(
                    select(ProjStage)
                    .where(ProjStage.enable == '1')
                    .order_by(ProjStage.project_id, ProjStage.stage_id)
                )
            )
            .scalars()
            .all()
        )

        # 构建任务映射 {task_id: task}，用于查找前置/后置任务
        task_map = {task.task_id: task for task in tasks}

        # 构建阶段映射 {stage_id: stage}，用于查找前置/后置阶段
        stage_map = {stage.stage_id: stage for stage in stages}

        # 按项目分组统计
        project_stats = {}

        # ===== 统计任务异常 =====
        for task in tasks:
            project_id = task.project_id
            if project_id not in project_stats:
                project_stats[project_id] = {
                    'missing_info_count': 0,
                    'time_error_count': 0,
                    'unassigned_count': 0,
                }

            stats = project_stats[project_id]

            # 1. 检查信息缺失（负责人、开始时间、结束时间、审批层级）
            # job_number 可能是字符串或数字，需要检查是否为空或None
            job_number_empty = task.job_number is None or (isinstance(task.job_number, str) and task.job_number.strip() == '')
            # approval_nodes 是JSON格式的文本，需要检查是否为空或未配置
            approval_nodes_empty = False
            if task.approval_nodes:
                try:
                    approval_nodes_list = json.loads(task.approval_nodes) if isinstance(task.approval_nodes, str) else task.approval_nodes
                    approval_nodes_empty = not approval_nodes_list or len(approval_nodes_list) == 0
                except (json.JSONDecodeError, TypeError):
                    approval_nodes_empty = True
            else:
                approval_nodes_empty = True
            
            if job_number_empty or task.start_time is None or task.end_time is None or approval_nodes_empty:
                stats['missing_info_count'] += 1

            # 2. 检查未分配到阶段
            if task.stage_id is None:
                stats['unassigned_count'] += 1

            # 3. 检查时间关系异常（一个任务只计数一次，即使有多种异常）
            has_time_error = False

            # 3.1 检查任务自身：开始时间 > 结束时间
            if task.start_time and task.end_time and task.start_time > task.end_time:
                has_time_error = True

            # 3.2 检查前置任务关系：当前任务的开始时间 <= 前置任务的结束时间
            if not has_time_error and task.predecessor_tasks and task.start_time:
                try:
                    predecessor_ids = json.loads(task.predecessor_tasks) if isinstance(task.predecessor_tasks, str) else task.predecessor_tasks
                    for pred_id in predecessor_ids:
                        pred_task = task_map.get(pred_id)
                        if pred_task and pred_task.end_time and task.start_time:
                            # 当前任务开始时间 <= 前置任务结束时间，异常
                            if task.start_time <= pred_task.end_time:
                                has_time_error = True
                                break
                except (json.JSONDecodeError, TypeError):
                    pass

            # 3.3 检查后置任务关系：当前任务的结束时间 >= 后置任务的开始时间
            if not has_time_error and task.successor_tasks and task.end_time:
                try:
                    successor_ids = json.loads(task.successor_tasks) if isinstance(task.successor_tasks, str) else task.successor_tasks
                    for succ_id in successor_ids:
                        succ_task = task_map.get(succ_id)
                        if succ_task and succ_task.start_time and task.end_time:
                            # 当前任务结束时间 >= 后置任务开始时间，异常
                            if task.end_time >= succ_task.start_time:
                                has_time_error = True
                                break
                except (json.JSONDecodeError, TypeError):
                    pass

            if has_time_error:
                stats['time_error_count'] += 1

        # ===== 统计阶段时间异常 =====
        for stage in stages:
            project_id = stage.project_id
            if project_id not in project_stats:
                project_stats[project_id] = {
                    'missing_info_count': 0,
                    'time_error_count': 0,
                    'unassigned_count': 0,
                }

            stats = project_stats[project_id]

            # 检查阶段时间关系异常（一个阶段只计数一次，即使有多种异常）
            has_time_error = False

            # 检查前置阶段关系：当前阶段开始时间 <= 前置阶段结束时间
            if stage.predecessor_stages and stage.start_time:
                try:
                    predecessor_ids = json.loads(stage.predecessor_stages) if isinstance(stage.predecessor_stages, str) else stage.predecessor_stages
                    for pred_id in predecessor_ids:
                        pred_stage = stage_map.get(pred_id)
                        if pred_stage and pred_stage.end_time and stage.start_time:
                            # 当前阶段开始时间 <= 前置阶段结束时间，异常
                            if stage.start_time <= pred_stage.end_time:
                                has_time_error = True
                                break
                except (json.JSONDecodeError, TypeError):
                    pass

            # 检查后置阶段关系：当前阶段结束时间 >= 后置阶段开始时间
            if not has_time_error and stage.successor_stages and stage.end_time:
                try:
                    successor_ids = json.loads(stage.successor_stages) if isinstance(stage.successor_stages, str) else stage.successor_stages
                    for succ_id in successor_ids:
                        succ_stage = stage_map.get(succ_id)
                        if succ_stage and succ_stage.start_time and stage.end_time:
                            # 当前阶段结束时间 >= 后置阶段开始时间，异常
                            if stage.end_time >= succ_stage.start_time:
                                has_time_error = True
                                break
                except (json.JSONDecodeError, TypeError):
                    pass

            if has_time_error:
                stats['time_error_count'] += 1

        # 计算项目状态并返回
        result = {}
        for project_id, stats in project_stats.items():
            total_errors = (
                stats['missing_info_count'] +
                stats['time_error_count'] +
                stats['unassigned_count']
            )
            result[project_id] = {
                'missing_info_count': stats['missing_info_count'],
                'time_relation_error_count': stats['time_error_count'],
                'unassigned_stage_count': stats['unassigned_count'],
                'project_status': '异常' if total_errors > 0 else '正常',
            }

        return result

    @classmethod
    async def get_task_config_detail_by_id(cls, db: AsyncSession, task_id: int):
        """
        根据任务ID获取任务配置详细信息

        :param db: orm对象
        :param task_id: 任务ID
        :return: 任务配置信息对象
        """
        task = (
            (
                await db.execute(
                    select(ProjTask).where(ProjTask.task_id == task_id, ProjTask.enable == '0')
                )
            )
            .scalars()
            .first()
        )
        return task

    @classmethod
    async def get_task_config_list(cls, db: AsyncSession, query_object: TaskConfigPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取任务配置列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 任务配置列表信息对象
        """
        # TODO: 后续根据实际数据库表结构实现
        # 暂时返回空列表
        from utils.page_util import PageResponseModel
        return PageResponseModel(
            rows=[],
            total=0,
            page_num=query_object.page_num,
            page_size=query_object.page_size,
        )

    @classmethod
    async def get_stages_by_project_id_with_lock(cls, db: AsyncSession, project_id: int):
        """
        根据项目ID获取所有阶段（包含已删除的，用于全量更新）
        使用行锁避免并发写入问题

        :param db: orm对象
        :param project_id: 项目ID
        :return: 阶段列表
        """
        stages = (
            (
                await db.execute(
                    select(ProjStage)
                    .where(ProjStage.project_id == project_id)
                    .with_for_update()  # 行锁
                    .order_by(ProjStage.stage_id)
                )
            )
            .scalars()
            .all()
        )
        return stages

    @classmethod
    async def get_tasks_by_project_id_with_lock(cls, db: AsyncSession, project_id: int):
        """
        根据项目ID获取所有任务（包含已删除的，用于全量更新）
        使用行锁避免并发写入问题

        :param db: orm对象
        :param project_id: 项目ID
        :return: 任务列表
        """
        tasks = (
            (
                await db.execute(
                    select(ProjTask)
                    .where(ProjTask.project_id == project_id)
                    .with_for_update()  # 行锁
                    .order_by(ProjTask.task_id)
                )
            )
            .scalars()
            .all()
        )
        return tasks

    @classmethod
    async def add_stage_dao(cls, db: AsyncSession, stage_data: dict):
        """
        新增阶段数据库操作

        :param db: orm对象
        :param stage_data: 阶段数据字典
        :return: 新增的阶段对象
        """
        db_stage = ProjStage(**stage_data)
        db.add(db_stage)
        await db.flush()
        return db_stage

    @classmethod
    async def update_stage_dao(cls, db: AsyncSession, stage_data: dict):
        """
        更新阶段数据库操作

        :param db: orm对象
        :param stage_data: 阶段数据字典（必须包含stage_id字段）
        :return: 无返回值
        """
        stage_id = stage_data.get('stage_id')
        if not stage_id:
            raise ValueError('stage_data must contain stage_id')
        update_values = {k: v for k, v in stage_data.items() if k != 'stage_id' and (v is not None or k in ['enable'])}
        await db.execute(
            update(ProjStage)
            .where(ProjStage.stage_id == stage_id)
            .values(**update_values)
        )

    @classmethod
    async def soft_delete_stage_dao(cls, db: AsyncSession, stage_id: int, update_by: str):
        """
        软删除阶段数据库操作

        :param db: orm对象
        :param stage_id: 阶段ID
        :param update_by: 更新者
        :return: 无返回值
        """
        await db.execute(
            update(ProjStage)
            .where(ProjStage.stage_id == stage_id)
            .values(enable='0', update_by=update_by, update_time=datetime.now())
        )

    @classmethod
    async def add_task_dao(cls, db: AsyncSession, task_data: dict):
        """
        新增任务数据库操作

        :param db: orm对象
        :param task_data: 任务数据字典
        :return: 新增的任务对象
        """
        db_task = ProjTask(**task_data)
        db.add(db_task)
        await db.flush()
        return db_task

    @classmethod
    async def update_task_dao(cls, db: AsyncSession, task_data: dict):
        """
        更新任务数据库操作

        :param db: orm对象
        :param task_data: 任务数据字典（必须包含task_id字段）
        :return: 无返回值
        """
        task_id = task_data.get('task_id')
        if not task_id:
            raise ValueError('task_data must contain task_id')
        update_values = {k: v for k, v in task_data.items() if k != 'task_id' and (v is not None or k in ['enable', 'stage_id'])}
        await db.execute(
            update(ProjTask)
            .where(ProjTask.task_id == task_id)
            .values(**update_values)
        )

    @classmethod
    async def soft_delete_task_dao(cls, db: AsyncSession, task_id: int, update_by: str):
        """
        软删除任务数据库操作

        :param db: orm对象
        :param task_id: 任务ID
        :param update_by: 更新者
        :return: 无返回值
        """
        await db.execute(
            update(ProjTask)
            .where(ProjTask.task_id == task_id)
            .values(enable='0', update_by=update_by, update_time=datetime.now())
        )

