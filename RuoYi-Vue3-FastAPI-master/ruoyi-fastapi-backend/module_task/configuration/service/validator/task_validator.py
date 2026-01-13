from sqlalchemy.ext.asyncio import AsyncSession
from module_task.entity.vo.task_vo import TaskConfigPayload
from utils.log_util import logger
from exceptions.exception import ServiceException


class TaskValidator:
    """
    任务配置校验器
    负责所有数据校验相关的逻辑
    """

    @classmethod
    async def validate_task_config_content(
        cls, query_db: AsyncSession, payload: TaskConfigPayload, current_user_id: int
    ):
        """
        数据内容校验
        包含：基础数据校验、阶段图校验、任务图校验、阶段时间校验

        :param query_db: orm对象
        :param payload: 任务配置数据对象
        :param current_user_id: 当前用户ID
        :return: 无返回值，校验失败抛出ServiceException
        """
        # 1. 基础数据校验
        await cls._validate_basic_data(query_db, payload, current_user_id)

        # 2. 阶段图回环检测
        cls._validate_stage_cycles(payload)

        # 3. 任务图回环检测
        cls._validate_task_cycles(payload)

        # 4. 阶段时间校验（允许保存，只记录日志）
        cls._validate_stage_time_relations(payload)

    @classmethod
    async def _validate_basic_data(
        cls, query_db: AsyncSession, payload: TaskConfigPayload, current_user_id: int
    ):
        """
        基础数据校验
        校验projectId和userId是否存在

        :param query_db: orm对象
        :param payload: 任务配置数据对象
        :param current_user_id: 当前用户ID
        """
        # TODO: 校验projectId是否存在于字典配置中
        # 暂时跳过，等确认字典类型后再实现
        # project_id = payload.project_id
        # dict_data_list = await DictDataService.query_dict_data_list_services(query_db, 'sys_project')
        # project_ids = [item.dict_value for item in dict_data_list]
        # if str(project_id) not in project_ids:
        #     raise ServiceException(message=f'项目ID {project_id} 不存在于系统配置中')

        # 校验userId是否存在（当前用户ID应该已经在登录时验证过，这里可以跳过）
        # 如果需要额外校验，可以查询用户表
        pass

    @classmethod
    def _validate_stage_cycles(cls, payload: TaskConfigPayload):
        """
        阶段图回环检测
        使用DFS染色算法检测阶段之间的回环依赖

        :param payload: 任务配置数据对象
        """
        stages = payload.stages
        if not stages:
            return

        # 构建阶段ID到阶段对象的映射
        stage_map = {stage.id: stage for stage in stages}

        # ===== 校验1：自连接检查 =====
        for stage in stages:
            stage_name = stage.name
            # 检查前置阶段列表中是否包含自己
            if stage.id in stage.predecessor_stages:
                raise ServiceException(
                    message=f'阶段数据校验失败，涉及阶段【{stage_name}】，错误信息：阶段不能将自己设置为前置阶段（自连接）'
                )
            # 检查后置阶段列表中是否包含自己
            if stage.id in stage.successor_stages:
                raise ServiceException(
                    message=f'阶段数据校验失败，涉及阶段【{stage_name}】，错误信息：阶段不能将自己设置为后置阶段（自连接）'
                )

        # ===== 校验2：不同类型元素连接检查 =====
        for stage in stages:
            stage_name = stage.name
            # 检查前置阶段列表中的ID是否都是阶段ID（存在于stage_map中）
            for pred_id in stage.predecessor_stages:
                if pred_id not in stage_map:
                    raise ServiceException(
                        message=f'阶段数据校验失败，涉及阶段【{stage_name}】，错误信息：前置阶段 {pred_id} 不存在于阶段列表中，阶段只能与阶段连接'
                    )
            # 检查后置阶段列表中的ID是否都是阶段ID（存在于stage_map中）
            for succ_id in stage.successor_stages:
                if succ_id not in stage_map:
                    raise ServiceException(
                        message=f'阶段数据校验失败，涉及阶段【{stage_name}】，错误信息：后置阶段 {succ_id} 不存在于阶段列表中，阶段只能与阶段连接'
                    )

        # 构建邻接表（有向图）：stage_id -> [successor_stage_ids]
        # 注意：同时考虑predecessor和successor关系，构建完整的图
        adjacency = {}
        for stage in stages:
            # 初始化邻接表
            if stage.id not in adjacency:
                adjacency[stage.id] = []
            # 添加后置阶段（A的后置是B，表示A->B）
            adjacency[stage.id].extend(stage.successor_stages)
            # 添加前置阶段的反向关系（A的前置是B，表示B->A）
            for pred_id in stage.predecessor_stages:
                if pred_id not in adjacency:
                    adjacency[pred_id] = []
                if stage.id not in adjacency[pred_id]:
                    adjacency[pred_id].append(stage.id)

        # 使用DFS检测回环（染色算法：0=未访问，1=访问中，2=已访问）
        color = {stage_id: 0 for stage_id in stage_map.keys()}
        cycle_path = []

        def dfs(node_id: int, path: list):
            """DFS遍历，检测回环"""
            if color[node_id] == 1:  # 发现回环
                # 找到回环路径
                cycle_start = path.index(node_id)
                cycle_path.extend(path[cycle_start:] + [node_id])
                return True
            if color[node_id] == 2:  # 已访问过，无回环
                return False

            color[node_id] = 1  # 标记为访问中
            path.append(node_id)

            # 遍历所有后继节点
            for successor_id in adjacency.get(node_id, []):
                # 验证后继节点是否存在
                if successor_id not in stage_map:
                    current_stage = stage_map.get(node_id)
                    stage_name = current_stage.name if current_stage else str(node_id)
                    raise ServiceException(
                        message=f'阶段数据校验失败，涉及阶段【{stage_name}】，错误信息：后置阶段 {successor_id} 不存在于阶段列表中'
                    )
                if dfs(successor_id, path):
                    return True

            color[node_id] = 2  # 标记为已访问
            path.pop()
            return False

        # 对每个未访问的节点进行DFS（处理多个独立的有向图）
        for stage_id in stage_map.keys():
            if color[stage_id] == 0:
                if dfs(stage_id, []):
                    # 发现回环，生成错误信息
                    # 获取回环中第一个阶段的名称
                    first_stage_id = cycle_path[0] if cycle_path else stage_id
                    first_stage = stage_map.get(first_stage_id)
                    stage_name = first_stage.name if first_stage else str(first_stage_id)
                    raise ServiceException(
                        message=f'回环检测失败，涉及阶段【{stage_name}】。请检查阶段的前置/后置关系配置。'
                    )

    @classmethod
    def _validate_task_cycles(cls, payload: TaskConfigPayload):
        """
        任务图回环检测
        按阶段分组，对每个阶段内的任务进行回环检测
        同时校验跨阶段任务引用和未归属阶段任务的规则

        :param payload: 任务配置数据对象
        """
        tasks = payload.tasks
        if not tasks:
            return

        # 构建任务ID到任务对象的映射
        task_map = {task.id: task for task in tasks}

        # 按阶段分组任务
        tasks_by_stage = {}
        tasks_without_stage = []

        for task in tasks:
            if task.stage_id is None:
                tasks_without_stage.append(task)
            else:
                if task.stage_id not in tasks_by_stage:
                    tasks_by_stage[task.stage_id] = []
                tasks_by_stage[task.stage_id].append(task)

        # 校验未归属阶段的任务
        for task in tasks_without_stage:
            if task.predecessor_tasks or task.successor_tasks:
                raise ServiceException(
                    message=f'任务数据校验失败，涉及任务【{task.name}】，错误信息：未归属任何阶段的任务不能配置前后置关系'
                )

        # ===== 校验1：任务自连接检查 =====
        for task in tasks:
            task_name = task.name
            # 检查前置任务列表中是否包含自己
            if task.id in task.predecessor_tasks:
                raise ServiceException(
                    message=f'任务数据校验失败，涉及任务【{task_name}】，错误信息：任务不能将自己设置为前置任务（自连接）'
                )
            # 检查后置任务列表中是否包含自己
            if task.id in task.successor_tasks:
                raise ServiceException(
                    message=f'任务数据校验失败，涉及任务【{task_name}】，错误信息：任务不能将自己设置为后置任务（自连接）'
                )

        # ===== 校验2：不同类型元素连接检查 =====
        for task in tasks:
            task_name = task.name
            # 检查前置任务列表中的ID是否都是任务ID（存在于task_map中）
            for pred_id in task.predecessor_tasks:
                if pred_id not in task_map:
                    raise ServiceException(
                        message=f'任务数据校验失败，涉及任务【{task_name}】，错误信息：前置任务 {pred_id} 不存在于任务列表中，任务只能与任务连接'
                    )
            # 检查后置任务列表中的ID是否都是任务ID（存在于task_map中）
            for succ_id in task.successor_tasks:
                if succ_id not in task_map:
                    raise ServiceException(
                        message=f'任务数据校验失败，涉及任务【{task_name}】，错误信息：后置任务 {succ_id} 不存在于任务列表中，任务只能与任务连接'
                    )

        # 对每个阶段内的任务进行回环检测
        for stage_id, stage_tasks in tasks_by_stage.items():
            # 构建该阶段内任务的ID集合，用于快速查找
            stage_task_ids = {task.id for task in stage_tasks}

            # 构建该阶段内任务的邻接表（有向图）
            # 同时考虑predecessor和successor关系，构建完整的图
            adjacency = {}
            for task in stage_tasks:
                # 初始化邻接表
                if task.id not in adjacency:
                    adjacency[task.id] = []
                # 添加后置任务（A的后置是B，表示A->B）
                # ===== 校验3：任务跨阶段链接检查（后置任务） =====
                for succ_id in task.successor_tasks:
                    if succ_id not in stage_task_ids:
                        raise ServiceException(
                            message=f'任务数据校验失败，涉及任务【{task.name}】，错误信息：后置任务 {succ_id} 不属于当前阶段，不同阶段的任务不能直接关联'
                        )
                    adjacency[task.id].append(succ_id)
                # 添加前置任务的反向关系（A的前置是B，表示B->A）
                # ===== 校验3：任务跨阶段链接检查（前置任务） =====
                for pred_id in task.predecessor_tasks:
                    if pred_id not in stage_task_ids:
                        raise ServiceException(
                            message=f'任务数据校验失败，涉及任务【{task.name}】，错误信息：前置任务 {pred_id} 不属于当前阶段，不同阶段的任务不能直接关联'
                        )
                    if pred_id not in adjacency:
                        adjacency[pred_id] = []
                    if task.id not in adjacency[pred_id]:
                        adjacency[pred_id].append(task.id)

            # 使用DFS检测回环
            color = {task.id: 0 for task in stage_tasks}
            cycle_path = []

            def dfs(node_id: int, path: list):
                """DFS遍历，检测回环"""
                if color[node_id] == 1:  # 发现回环
                    cycle_start = path.index(node_id)
                    cycle_path.extend(path[cycle_start:] + [node_id])
                    return True
                if color[node_id] == 2:  # 已访问过
                    return False

                color[node_id] = 1
                path.append(node_id)

                # 遍历所有后继任务
                # 注意：跨阶段检查和任务存在性检查已在构建邻接表时完成，这里只需要进行DFS遍历
                for successor_id in adjacency.get(node_id, []):
                    if dfs(successor_id, path):
                        return True

                color[node_id] = 2
                path.pop()
                return False

            # 对每个未访问的任务进行DFS
            for task in stage_tasks:
                if color[task.id] == 0:
                    if dfs(task.id, []):
                        # 发现回环，获取回环中第一个任务的名称
                        first_task_id = cycle_path[0] if cycle_path else task.id
                        first_task = task_map.get(first_task_id)
                        task_name = first_task.name if first_task else task.name
                        raise ServiceException(
                            message=f'回环检测失败，涉及任务【{task_name}】。请检查任务的前置/后置关系配置。'
                        )

    @classmethod
    def _validate_stage_time_relations(cls, payload: TaskConfigPayload):
        """
        阶段时间关系校验
        校验前置阶段的结束时间是否早于后置阶段的开始时间
        允许保存，只记录日志，不抛出异常

        :param payload: 任务配置数据对象
        """
        stages = payload.stages
        if not stages:
            return

        # 构建阶段ID到阶段对象的映射
        stage_map = {stage.id: stage for stage in stages}

        # 检查每个阶段的前后置时间关系
        for stage in stages:
            stage_name = stage.name
            has_time_error = False

            # 检查前置阶段关系：当前阶段开始时间 <= 前置阶段结束时间，异常
            if stage.predecessor_stages and stage.start_time:
                for pred_id in stage.predecessor_stages:
                    pred_stage = stage_map.get(pred_id)
                    if pred_stage and pred_stage.end_time and stage.start_time:
                        if stage.start_time <= pred_stage.end_time:
                            has_time_error = True
                            logger.warning(
                                f'阶段时间关系异常：阶段【{stage_name}】(ID: {stage.id}) 的开始时间 {stage.start_time} '
                                f'<= 前置阶段【{pred_stage.name}】(ID: {pred_id}) 的结束时间 {pred_stage.end_time}'
                            )
                            break

            # 检查后置阶段关系：当前阶段结束时间 >= 后置阶段开始时间，异常
            if not has_time_error and stage.successor_stages and stage.end_time:
                for succ_id in stage.successor_stages:
                    succ_stage = stage_map.get(succ_id)
                    if succ_stage and succ_stage.start_time and stage.end_time:
                        if stage.end_time >= succ_stage.start_time:
                            has_time_error = True
                            logger.warning(
                                f'阶段时间关系异常：阶段【{stage_name}】(ID: {stage.id}) 的结束时间 {stage.end_time} '
                                f'>= 后置阶段【{succ_stage.name}】(ID: {succ_id}) 的开始时间 {succ_stage.start_time}'
                            )
                            break
    
    @classmethod
    async def check_single_task_validation(cls, db: AsyncSession, task, task_map: dict = None) -> dict:
        """
        检查单个任务的校验状态（信息完整性和时间关系）
        用于任务生成前的校验和项目列表的统计
        
        :param db: orm对象
        :param task: 任务对象（ProjTask）
        :param task_map: 任务映射 {task_id: task}，用于查找前置/后置任务。如果为None，会查询项目内所有任务
        :return: 字典 {
            'has_missing_info': bool,  # 是否有信息缺失
            'is_unassigned': bool,  # 是否未分配到阶段
            'has_time_error': bool,  # 是否有时间关系异常
            'is_valid': bool  # 是否通过校验（所有检查都通过）
        }
        """
        import json
        from module_task.configuration.dao.task_dao import TaskDao
        
        result = {
            'has_missing_info': False,
            'is_unassigned': False,
            'has_time_error': False,
            'is_valid': True
        }
        
        # 1. 检查信息缺失（负责人、开始时间、结束时间、审批层级）
        job_number_empty = task.job_number is None or (isinstance(task.job_number, str) and task.job_number.strip() == '')
        
        # 检查审批节点是否为空
        # 特殊情况：如果审批类型为"none"（无需审批），则允许审批节点为空
        approval_nodes_empty = False
        approval_type = getattr(task, 'approval_type', None)
        is_no_approval = approval_type == 'none'
        
        if is_no_approval:
            # 无需审批模式：允许审批节点为空
            approval_nodes_empty = False
        else:
            # 其他审批模式：必须配置审批节点
            if task.approval_nodes:
                try:
                    approval_nodes_list = json.loads(task.approval_nodes) if isinstance(task.approval_nodes, str) else task.approval_nodes
                    approval_nodes_empty = not approval_nodes_list or len(approval_nodes_list) == 0
                except (json.JSONDecodeError, TypeError):
                    approval_nodes_empty = True
            else:
                approval_nodes_empty = True
        
        if job_number_empty or task.start_time is None or task.end_time is None or approval_nodes_empty:
            result['has_missing_info'] = True
            result['is_valid'] = False
        
        # 2. 检查未分配到阶段
        if task.stage_id is None:
            result['is_unassigned'] = True
            result['is_valid'] = False
        
        # 3. 检查时间关系异常
        has_time_error = False
        
        # 如果没有提供task_map，需要查询项目内所有任务来构建映射
        if task_map is None:
            project_tasks = await TaskDao.get_tasks_by_project_id(db, task.project_id)
            task_map = {t.task_id: t for t in project_tasks}
        
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
            result['has_time_error'] = True
            result['is_valid'] = False
        
        return result

