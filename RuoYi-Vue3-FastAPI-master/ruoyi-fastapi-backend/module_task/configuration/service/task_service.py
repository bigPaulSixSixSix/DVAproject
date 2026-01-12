import json
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_task.configuration.dao.task_dao import TaskDao
from module_admin.service.dict_service import DictDataService
from module_task.entity.vo.task_vo import (
    StageModel,
    StagePositionModel,
    TaskConfigModel,
    TaskConfigPageQueryModel,
    TaskConfigPayload,
    TaskModel,
    TaskPositionModel,
    ProjectSummaryModel,
)
from module_task.configuration.service.validator.task_validator import TaskValidator
from module_task.configuration.service.persistence.task_persistence import TaskPersistence
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from exceptions.exception import ServiceException


class TaskService:
    """
    任务配置模块服务层
    """

    @classmethod
    async def process_task_config_services(
        cls, query_db: AsyncSession, raw_data: bytes, current_user_id: int, current_user_name: str, generate_tasks: bool = False
    ) -> CrudResponseModel:
        """
        统一处理任务配置的主流程方法
        包含：结构校验 -> 内容校验 -> 数据持久化

        :param query_db: orm对象
        :param raw_data: 原始请求数据（bytes）
        :param current_user_id: 当前用户ID
        :param current_user_name: 当前用户名
        :param generate_tasks: 是否在保存后生成任务（True-保存并生成，False-仅保存）
        :return: 处理结果
        """
        logger.info('开始处理任务配置请求')

        # ===== 步骤1：结构校验（字段完整性校验） =====
        logger.info('步骤1：开始结构校验')
        try:
            payload = TaskConfigPayload.model_validate_json(raw_data)
            logger.info('步骤1：结构校验通过')
        except ValidationError as exc:
            # 格式化错误信息，便于前端显示
            error_details = []
            for error in exc.errors():
                field_path = ' -> '.join(str(loc) for loc in error.get('loc', []))
                error_type = error.get('type', 'unknown')
                error_msg = error.get('msg', '')
                error_details.append({
                    'field': field_path,
                    'type': error_type,
                    'message': error_msg,
                    'input': error.get('input'),
                })
            
            error_msg = '任务配置结构校验失败，请检查数据结构是否与示例一致'
            logger.warning(f'步骤1：结构校验失败 - {error_msg}')
            logger.warning(f'校验错误详情: {error_details}')
            
            # 生成用户友好的错误消息
            if error_details:
                first_error = error_details[0]
                user_friendly_msg = f'{error_msg}\n字段: {first_error["field"]}, 错误: {first_error["message"]}'
            else:
                user_friendly_msg = error_msg
            
            raise ServiceException(message=user_friendly_msg, data={'errors': error_details})

        # ===== 步骤2：数据内容校验 =====
        logger.info('步骤2：开始数据内容校验')
        try:
            await TaskValidator.validate_task_config_content(query_db, payload, current_user_id)
            logger.info('步骤2：数据内容校验通过')
        except ServiceException as e:
            logger.warning(f'步骤2：数据内容校验失败 - {e.message}')
            raise e

        # ===== 步骤3：数据持久化 =====
        logger.info(f'步骤3：开始数据持久化（generate_tasks={generate_tasks}）')
        try:
            await TaskPersistence.persist_task_config(query_db, payload, current_user_id, current_user_name, generate_tasks)
            logger.info('步骤3：数据持久化成功')
        except Exception as e:
            logger.error(f'步骤3：数据持久化失败 - {str(e)}')
            await query_db.rollback()
            raise ServiceException(message=f'数据持久化失败：{str(e)}')

        # ===== 步骤4：查询并返回全表数据 =====
        logger.info('步骤4：查询全表数据')
        try:
            # 调用独立的查询接口获取完整数据
            full_data = await cls.get_task_config_by_project_id_services(query_db, int(payload.project_id))
            logger.info('步骤4：全表数据查询成功')
            
            # 返回成功结果，包含完整数据
            message = '任务配置保存并生成成功' if generate_tasks else '任务配置保存成功'
            return CrudResponseModel(
                is_success=True,
                message=message,
                result=full_data  # 使用result字段返回完整数据
            )
        except Exception as e:
            logger.error(f'步骤4：全表数据查询失败 - {str(e)}')
            # 即使查询失败，保存已经成功，返回成功消息但不包含数据
            message = '任务配置保存并生成成功，但数据查询失败' if generate_tasks else '任务配置保存成功，但数据查询失败'
            return CrudResponseModel(is_success=True, message=message)

    @classmethod
    async def get_task_config_list_services(
        cls, query_db: AsyncSession, query_object: TaskConfigPageQueryModel, is_page: bool = True
    ):
        """
        获取任务配置列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 任务配置列表信息对象
        """
        task_list_result = await TaskDao.get_task_config_list(query_db, query_object, is_page)

        return task_list_result

    @classmethod
    async def get_project_summary_list_services(cls, query_db: AsyncSession) -> list[ProjectSummaryModel]:
        """
        获取项目任务列表摘要
        """
        from utils.log_util import logger
        from sqlalchemy import select, func
        from module_task.entity.do.todo_task_do import TodoTask
        
        dict_data_list = await DictDataService.query_dict_data_list_services(query_db, 'sys_task_project')
        logger.info(f'[项目列表] 字典数据查询结果: dict_type=sys_task_project, count={len(dict_data_list)}')
        stats_map = await TaskDao.get_project_statistics(query_db)
        logger.info(f'[项目列表] 项目统计信息: count={len(stats_map)}')
        validation_stats_map = await TaskDao.get_project_validation_statistics(query_db)
        logger.info(f'[项目列表] 项目验证统计信息: count={len(validation_stats_map)}')
        
        # 批量查询哪些项目已经有生成的任务
        generated_projects_result = await query_db.execute(
            select(TodoTask.project_id)
            .distinct()
        )
        generated_project_ids = set([row[0] for row in generated_projects_result.all()])
        logger.info(f'[项目列表] 已生成任务的项目数量: {len(generated_project_ids)}')

        result: list[ProjectSummaryModel] = []
        seen_ids = set()

        for dict_data in dict_data_list:
            try:
                project_id = int(dict_data.dict_value)
            except (TypeError, ValueError):
                continue

            stats = stats_map.get(project_id, {})
            stage_count = stats.get('stage_count', 0)
            task_count = stats.get('task_count', 0)

            # 如果阶段数量和任务数量都为0，项目状态为"未配置"，不进行验证检查
            if stage_count == 0 and task_count == 0:
                validation_stats = {
                    'missing_info_count': 0,
                    'time_relation_error_count': 0,
                    'unassigned_stage_count': 0,
                    'project_status': '未配置',
                }
            else:
                validation_stats = validation_stats_map.get(project_id, {
                    'missing_info_count': 0,
                    'time_relation_error_count': 0,
                    'unassigned_stage_count': 0,
                    'project_status': '正常',
                })

            result.append(
                ProjectSummaryModel(
                    project_id=project_id,
                    project_name=dict_data.dict_label,
                    stage_count=stage_count,
                    task_count=task_count,
                    create_time=stats.get('create_time'),
                    update_time=stats.get('update_time'),
                    project_status=validation_stats.get('project_status', '正常'),
                    missing_info_count=validation_stats.get('missing_info_count', 0),
                    time_relation_error_count=validation_stats.get('time_relation_error_count', 0),
                    unassigned_stage_count=validation_stats.get('unassigned_stage_count', 0),
                    tasks_generated=project_id in generated_project_ids,
                )
            )
            seen_ids.add(project_id)

        logger.info(f'[项目列表] 从字典数据生成的项目数量: {len(result)}')

        for project_id, stats in stats_map.items():
            if project_id in seen_ids:
                continue

            stage_count = stats.get('stage_count', 0)
            task_count = stats.get('task_count', 0)

            # 如果阶段数量和任务数量都为0，项目状态为"未配置"，不进行验证检查
            if stage_count == 0 and task_count == 0:
                validation_stats = {
                    'missing_info_count': 0,
                    'time_relation_error_count': 0,
                    'unassigned_stage_count': 0,
                    'project_status': '未配置',
                }
            else:
                validation_stats = validation_stats_map.get(project_id, {
                    'missing_info_count': 0,
                    'time_relation_error_count': 0,
                    'unassigned_stage_count': 0,
                    'project_status': '正常',
                })

            result.append(
                ProjectSummaryModel(
                    project_id=project_id,
                    project_name=str(project_id),
                    stage_count=stage_count,
                    task_count=task_count,
                    create_time=stats.get('create_time'),
                    update_time=stats.get('update_time'),
                    project_status=validation_stats.get('project_status', '正常'),
                    missing_info_count=validation_stats.get('missing_info_count', 0),
                    time_relation_error_count=validation_stats.get('time_relation_error_count', 0),
                    unassigned_stage_count=validation_stats.get('unassigned_stage_count', 0),
                    tasks_generated=project_id in generated_project_ids,
                )
            )

        logger.info(f'[项目列表] 最终返回的项目数量: {len(result)}')
        return result

    @classmethod
    async def get_task_config_by_project_id_services(
        cls, query_db: AsyncSession, project_id: int
    ) -> dict:
        """
        根据项目ID获取完整的任务配置数据（独立的通用查询接口）
        返回格式与TaskConfigPayload一致，用于前端渲染
        包含 isEditable 字段（动态计算）

        :param query_db: orm对象
        :param project_id: 项目ID
        :return: 包含stages和tasks的字典
        """
        from module_task.todo.utils.task_generation_util import TaskGenerationUtil
        
        # 查询阶段和任务
        stages_do = await TaskDao.get_stages_by_project_id(query_db, project_id)
        tasks_do = await TaskDao.get_tasks_by_project_id(query_db, project_id)
        
        # 检查项目是否已生成任务
        tasks_generated = await TaskGenerationUtil.get_tasks_generated_status(query_db, project_id)

        # 转换阶段数据
        stages = []
        for stage_do in stages_do:
            # 解析JSON字段
            predecessor_stages = []
            successor_stages = []
            position = None

            if stage_do.predecessor_stages:
                try:
                    predecessor_stages = json.loads(stage_do.predecessor_stages)
                except (json.JSONDecodeError, TypeError):
                    predecessor_stages = []

            if stage_do.successor_stages:
                try:
                    successor_stages = json.loads(stage_do.successor_stages)
                except (json.JSONDecodeError, TypeError):
                    successor_stages = []

            if stage_do.position:
                try:
                    position_data = json.loads(stage_do.position)
                    position = StagePositionModel(**position_data) if position_data else None
                except (json.JSONDecodeError, TypeError):
                    position = None

            # 计算阶段是否可编辑
            if tasks_generated:
                is_editable = await TaskGenerationUtil.is_stage_editable(query_db, stage_do.stage_id)
            else:
                # 未生成任务的项目，所有阶段都可以编辑
                is_editable = True
            
            stage = StageModel(
                id=stage_do.stage_id,
                name=stage_do.name,
                start_time=stage_do.start_time,
                end_time=stage_do.end_time,
                duration=stage_do.duration,
                predecessor_stages=predecessor_stages,
                successor_stages=successor_stages,
                position=position,
                project_id=stage_do.project_id,
            )
            # 添加 isEditable 字段（通过 model_dump 后添加，使用 by_alias=True 保持 camelCase 格式）
            stage_dict = stage.model_dump(by_alias=True)
            stage_dict['isEditable'] = is_editable
            stages.append(stage_dict)

        # 转换任务数据
        tasks = []
        for task_do in tasks_do:
            # 解析JSON字段
            predecessor_tasks = []
            successor_tasks = []
            position = None
            approval_nodes = []

            if task_do.predecessor_tasks:
                try:
                    predecessor_tasks = json.loads(task_do.predecessor_tasks)
                except (json.JSONDecodeError, TypeError):
                    predecessor_tasks = []

            if task_do.successor_tasks:
                try:
                    successor_tasks = json.loads(task_do.successor_tasks)
                except (json.JSONDecodeError, TypeError):
                    successor_tasks = []

            if task_do.position:
                try:
                    position_data = json.loads(task_do.position)
                    position = TaskPositionModel(**position_data) if position_data else None
                except (json.JSONDecodeError, TypeError):
                    position = None

            if task_do.approval_nodes:
                try:
                    approval_nodes = json.loads(task_do.approval_nodes)
                except (json.JSONDecodeError, TypeError):
                    approval_nodes = []

            # 计算任务是否可编辑
            if tasks_generated:
                is_editable = await TaskGenerationUtil.is_task_editable(query_db, task_do.task_id)
            else:
                # 未生成任务的项目，所有任务都可以编辑
                is_editable = True
            
            task = TaskModel(
                id=task_do.task_id,
                name=task_do.name,
                description=task_do.description,
                start_time=task_do.start_time,
                end_time=task_do.end_time,
                duration=task_do.duration,
                job_number=task_do.job_number,
                stage_id=task_do.stage_id,
                predecessor_tasks=predecessor_tasks,
                successor_tasks=successor_tasks,
                position=position,
                project_id=task_do.project_id,
                approval_type=task_do.approval_type,
                approval_nodes=approval_nodes,
            )
            # 添加 isEditable 字段（通过 model_dump 后添加，使用 by_alias=True 保持 camelCase 格式）
            task_dict = task.model_dump(by_alias=True)
            task_dict['isEditable'] = is_editable
            tasks.append(task_dict)

        return {
            'project_id': project_id,  # 保持原有字段名
            'tasksGenerated': tasks_generated,  # 新增字段（camelCase）
            'stages': stages,
            'tasks': tasks,
        }

    @classmethod
    async def get_task_config_detail_services(cls, query_db: AsyncSession, task_id: int):
        """
        获取任务配置详细信息service

        :param query_db: orm对象
        :param task_id: 任务ID
        :return: 任务配置详细信息
        """
        task = await TaskDao.get_task_config_detail_by_id(query_db, task_id=task_id)
        if task:
            result = TaskConfigModel(**CamelCaseUtil.transform_result(task))
        else:
            result = TaskConfigModel(**dict())

        return result

