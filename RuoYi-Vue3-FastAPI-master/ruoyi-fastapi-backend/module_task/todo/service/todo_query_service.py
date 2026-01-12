"""
任务查询服务
"""
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from module_task.todo.dao.todo_query_dao import TodoQueryDao
from module_task.todo.dao.todo_task_apply_dao import TodoTaskApplyDao
from module_apply.service.apply_service import ApplyService
from module_apply.service.approval_service import ApprovalService
from module_apply.dao.approval_log_dao import ApprovalLogDao
from module_admin.service.dict_service import DictDataService
from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
from module_admin.entity.do.oa_department_do import OaDepartment
from module_task.todo.utils.dept_util import DeptUtil
from sqlalchemy import select
from utils.log_util import logger


class TodoQueryService:
    """任务查询服务"""
    
    @classmethod
    async def get_my_tasks_categories(
        cls,
        db: AsyncSession,
        job_number: str
    ) -> Dict[str, Any]:
        """
        获取我的任务分类统计
        
        :param db: orm对象
        :param job_number: 负责人工号
        :return: 分类统计数据
        """
        # 1. 获取当前用户的任务列表
        tasks = await TodoQueryDao.get_my_tasks_for_categories(db, job_number)
        
        # 2. 获取项目字典
        project_dict_list = await DictDataService.query_dict_data_list_services(db, 'sys_task_project')
        project_dict = {item.dict_value: item.dict_label for item in project_dict_list}
        
        # 3. 获取所有相关的员工和部门信息
        job_numbers = list(set([task.job_number for task in tasks if task.job_number]))
        employees_map = {}
        depts_map = {}
        second_level_depts_map = {}
        
        if job_numbers:
            # 查询员工信息
            employees = await db.execute(
                select(OaEmployeePrimary)
                .where(OaEmployeePrimary.job_number.in_(job_numbers))
            )
            employees_list = list(employees.scalars().all())
            employees_map = {emp.job_number: emp for emp in employees_list}
            
            # 查询部门信息
            org_ids = list(set([emp.organization_id for emp in employees_list if emp.organization_id]))
            if org_ids:
                depts = await db.execute(
                    select(OaDepartment)
                    .where(OaDepartment.id.in_(org_ids))
                )
                depts_list = list(depts.scalars().all())
                depts_map = {dept.id: dept for dept in depts_list}
                
                # 获取所有第二级部门code
                second_level_codes = set()
                for dept in depts_list:
                    if dept.code:
                        second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                        if second_level_code:
                            second_level_codes.add(second_level_code)
                
                # 查询第二级部门
                if second_level_codes:
                    second_level_depts = await db.execute(
                        select(OaDepartment)
                        .where(OaDepartment.code.in_(list(second_level_codes)))
                    )
                    second_level_depts_list = list(second_level_depts.scalars().all())
                    second_level_depts_map = {dept.code: dept for dept in second_level_depts_list}
        
        # 4. 统计项目分类
        project_stats = {}
        for task in tasks:
            project_id = task.project_id
            if project_id not in project_stats:
                project_stats[project_id] = {
                    'projectId': project_id,
                    'projectName': project_dict.get(str(project_id), f'项目{project_id}'),
                    'count': 0
                }
            project_stats[project_id]['count'] += 1
        
        # 5. 统计部门分类（第二级部门）
        dept_stats = {}
        for task in tasks:
            employee = employees_map.get(task.job_number)
            if not employee or not employee.organization_id:
                continue
            
            dept = depts_map.get(employee.organization_id)
            if not dept or not dept.code:
                continue
            
            # 获取第二级部门code
            second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
            if not second_level_code:
                continue
            
            second_level_dept = second_level_depts_map.get(second_level_code)
            if not second_level_dept:
                continue
            
            dept_id = second_level_dept.id
            if dept_id not in dept_stats:
                dept_stats[dept_id] = {
                    'deptId': dept_id,
                    'deptName': second_level_dept.name,
                    'count': 0
                }
            dept_stats[dept_id]['count'] += 1
        
        # 6. 统计状态分类
        status_stats = {}
        status_names = {1: '待提交', 2: '审批中', 4: '驳回'}
        for task in tasks:
            status = task.task_status
            if status not in status_stats:
                status_stats[status] = {
                    'status': status,
                    'statusName': status_names.get(status, f'状态{status}'),
                    'count': 0
                }
            status_stats[status]['count'] += 1
        
        return {
            'project': {
                'total': len(tasks),
                'items': list(project_stats.values())
            },
            'department': {
                'total': len(tasks),
                'items': list(dept_stats.values())
            },
            'status': {
                'total': len(tasks),
                'items': list(status_stats.values())
            }
        }
    
    @classmethod
    async def get_my_tasks_list(
        cls,
        db: AsyncSession,
        job_number: str,
        project_id: Optional[int] = None,
        dept_id: Optional[int] = None,
        task_status: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取我的任务列表
        
        :param db: orm对象
        :param job_number: 负责人工号
        :param project_id: 项目ID（可选）
        :param dept_id: 部门ID（可选，第二级部门ID）
        :param task_status: 任务状态（可选）
        :param page_num: 页码
        :param page_size: 每页数量
        :return: 任务列表数据
        """
        # 1. 查询任务列表
        task_data_list, total = await TodoQueryDao.get_my_tasks_list(
            db, job_number, project_id, dept_id, task_status, page_num, page_size
        )
        
        if not task_data_list:
            return {'total': 0, 'rows': []}
        
        # 2. 获取项目字典
        project_dict_list = await DictDataService.query_dict_data_list_services(db, 'sys_task_project')
        project_dict = {item.dict_value: item.dict_label for item in project_dict_list}
        
        # 3. 获取所有相关的任务ID、阶段ID、员工工号
        task_ids = [data['todo_task'].task_id for data in task_data_list]
        stage_ids = list(set([data['todo_task'].stage_id for data in task_data_list if data['todo_task'].stage_id]))
        job_numbers = list(set([data['todo_task'].job_number for data in task_data_list if data['todo_task'].job_number]))
        
        # 4. 查询任务配置
        from module_task.entity.do.proj_task_do import ProjTask
        proj_tasks = await db.execute(
            select(ProjTask).where(ProjTask.task_id.in_(task_ids))
        )
        proj_tasks_map = {task.task_id: task for task in proj_tasks.scalars().all()}
        
        # 5. 查询阶段信息
        from module_task.entity.do.proj_stage_do import ProjStage
        proj_stages_map = {}
        if stage_ids:
            proj_stages = await db.execute(
                select(ProjStage).where(ProjStage.stage_id.in_(stage_ids))
            )
            proj_stages_map = {stage.stage_id: stage for stage in proj_stages.scalars().all()}
        
        # 6. 查询员工和部门信息
        employees_map = {}
        depts_map = {}
        second_level_depts_map = {}
        
        if job_numbers:
            employees = await db.execute(
                select(OaEmployeePrimary)
                .where(OaEmployeePrimary.job_number.in_(job_numbers))
            )
            employees_list = list(employees.scalars().all())
            employees_map = {emp.job_number: emp for emp in employees_list}
            
            org_ids = list(set([emp.organization_id for emp in employees_list if emp.organization_id]))
            if org_ids:
                depts = await db.execute(
                    select(OaDepartment)
                    .where(OaDepartment.id.in_(org_ids))
                )
                depts_list = list(depts.scalars().all())
                depts_map = {dept.id: dept for dept in depts_list}
                
                # 获取第二级部门
                second_level_codes = set()
                for dept in depts_list:
                    if dept.code:
                        second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                        if second_level_code:
                            second_level_codes.add(second_level_code)
                
                if second_level_codes:
                    second_level_depts = await db.execute(
                        select(OaDepartment)
                        .where(OaDepartment.code.in_(list(second_level_codes)))
                    )
                    second_level_depts_list = list(second_level_depts.scalars().all())
                    second_level_depts_map = {dept.code: dept for dept in second_level_depts_list}
        
        # 7. 构建返回数据
        rows = []
        status_names = {1: '待提交', 2: '审批中', 4: '驳回'}
        
        for data in task_data_list:
            todo_task = data['todo_task']
            proj_task = proj_tasks_map.get(todo_task.task_id)
            
            # 获取员工和部门信息
            employee = employees_map.get(todo_task.job_number) if todo_task.job_number else None
            dept = depts_map.get(employee.organization_id) if employee and employee.organization_id else None
            second_level_dept = None
            if dept and dept.code:
                second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                if second_level_code:
                    second_level_dept = second_level_depts_map.get(second_level_code)
            
            # 获取阶段信息
            proj_stage = proj_stages_map.get(todo_task.stage_id) if todo_task.stage_id else None
            
            # 格式化截止时间
            deadline = None
            if todo_task.end_time:
                # 将Date转换为DateTime格式（YYYY-MM-DD HH:MM:SS）
                if isinstance(todo_task.end_time, date):
                    deadline = todo_task.end_time.strftime('%Y-%m-%d') + ' 18:00:00'
                elif isinstance(todo_task.end_time, datetime):
                    deadline = todo_task.end_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 图标类型和颜色（根据状态）
            icon_type = 'arrow-up'  # 默认
            icon_color = '#409EFF'  # 默认蓝色
            if todo_task.task_status == 2:  # 已提交
                icon_type = 'document'
                icon_color = '#67C23A'  # 绿色
            elif todo_task.task_status == 4:  # 驳回
                icon_type = 'close'
                icon_color = '#F56C6C'  # 红色
            
            row = {
                'taskId': todo_task.task_id,
                'taskName': proj_task.name if proj_task else todo_task.name,
                'projectId': todo_task.project_id,
                'projectName': project_dict.get(str(todo_task.project_id), f'项目{todo_task.project_id}'),
                'deptId': second_level_dept.id if second_level_dept else None,
                'deptName': second_level_dept.name if second_level_dept else None,
                'taskStatus': todo_task.task_status,
                'taskStatusName': status_names.get(todo_task.task_status, f'状态{todo_task.task_status}'),
                'jobNumber': todo_task.job_number,
                'assigneeName': employee.name if employee else None,
                'deadline': deadline,
                'stageId': todo_task.stage_id,
                'stageName': proj_stage.name if proj_stage else None,
                'iconType': icon_type,
                'iconColor': icon_color,
            }
            
            # 如果是驳回状态，添加驳回时间
            if todo_task.task_status == 4:
                # 查询驳回的审批日志
                reject_time = None
                task_apply = await TodoTaskApplyDao.get_latest_apply_by_task_id(db, todo_task.id)
                if task_apply:
                    apply_id = task_apply.apply_id
                    logs = await ApprovalLogDao.get_logs_by_apply_id(db, apply_id)
                    for log in logs:
                        if log.approval_result == 2:  # 驳回
                            reject_time = log.approval_end_time.strftime('%Y-%m-%d %H:%M:%S') if log.approval_end_time else None
                            break
                row['rejectTime'] = reject_time
            else:
                row['rejectTime'] = None
            
            rows.append(row)
        
        return {
            'total': total,
            'rows': rows
        }
    
    @classmethod
    async def get_completed_tasks_list(
        cls,
        db: AsyncSession,
        job_number: str,
        project_id: Optional[int] = None,
        dept_id: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        获取已完成任务列表（历史任务）
        
        :param db: orm对象
        :param job_number: 负责人工号
        :param project_id: 项目ID（可选）
        :param dept_id: 部门ID（可选，第二级部门ID）
        :param page_num: 页码
        :param page_size: 每页数量
        :return: 任务列表数据
        """
        # 1. 查询任务列表
        task_data_list, total = await TodoQueryDao.get_completed_tasks_list(
            db, job_number, project_id, dept_id, page_num, page_size
        )
        
        if not task_data_list:
            return {'total': 0, 'rows': []}
        
        # 2. 获取项目字典
        project_dict_list = await DictDataService.query_dict_data_list_services(db, 'sys_task_project')
        project_dict = {item.dict_value: item.dict_label for item in project_dict_list}
        
        # 3. 获取所有相关的任务ID、阶段ID、员工工号
        task_ids = [data['todo_task'].task_id for data in task_data_list]
        stage_ids = list(set([data['todo_task'].stage_id for data in task_data_list if data['todo_task'].stage_id]))
        job_numbers = list(set([data['todo_task'].job_number for data in task_data_list if data['todo_task'].job_number]))
        
        # 4. 查询任务配置
        from module_task.entity.do.proj_task_do import ProjTask
        proj_tasks = await db.execute(
            select(ProjTask).where(ProjTask.task_id.in_(task_ids))
        )
        proj_tasks_map = {task.task_id: task for task in proj_tasks.scalars().all()}
        
        # 5. 查询阶段信息
        from module_task.entity.do.proj_stage_do import ProjStage
        proj_stages_map = {}
        if stage_ids:
            proj_stages = await db.execute(
                select(ProjStage).where(ProjStage.stage_id.in_(stage_ids))
            )
            proj_stages_map = {stage.stage_id: stage for stage in proj_stages.scalars().all()}
        
        # 6. 查询员工和部门信息
        employees_map = {}
        depts_map = {}
        second_level_depts_map = {}
        
        if job_numbers:
            employees = await db.execute(
                select(OaEmployeePrimary)
                .where(OaEmployeePrimary.job_number.in_(job_numbers))
            )
            employees_list = list(employees.scalars().all())
            employees_map = {emp.job_number: emp for emp in employees_list}
            
            org_ids = list(set([emp.organization_id for emp in employees_list if emp.organization_id]))
            if org_ids:
                depts = await db.execute(
                    select(OaDepartment)
                    .where(OaDepartment.id.in_(org_ids))
                )
                depts_list = list(depts.scalars().all())
                depts_map = {dept.id: dept for dept in depts_list}
                
                # 获取第二级部门
                second_level_codes = set()
                for dept in depts_list:
                    if dept.code:
                        second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                        if second_level_code:
                            second_level_codes.add(second_level_code)
                
                if second_level_codes:
                    second_level_depts = await db.execute(
                        select(OaDepartment)
                        .where(OaDepartment.code.in_(list(second_level_codes)))
                    )
                    second_level_depts_list = list(second_level_depts.scalars().all())
                    second_level_depts_map = {dept.code: dept for dept in second_level_depts_list}
        
        # 7. 构建返回数据
        rows = []
        status_names = {3: '完成'}
        
        for data in task_data_list:
            todo_task = data['todo_task']
            proj_task = proj_tasks_map.get(todo_task.task_id)
            
            # 获取员工和部门信息
            employee = employees_map.get(todo_task.job_number) if todo_task.job_number else None
            dept = depts_map.get(employee.organization_id) if employee and employee.organization_id else None
            second_level_dept = None
            if dept and dept.code:
                second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                if second_level_code:
                    second_level_dept = second_level_depts_map.get(second_level_code)
            
            # 获取阶段信息
            proj_stage = proj_stages_map.get(todo_task.stage_id) if todo_task.stage_id else None
            
            # 格式化截止时间
            deadline = None
            if todo_task.end_time:
                # 将Date转换为DateTime格式（YYYY-MM-DD HH:MM:SS）
                if isinstance(todo_task.end_time, date):
                    deadline = todo_task.end_time.strftime('%Y-%m-%d') + ' 18:00:00'
                elif isinstance(todo_task.end_time, datetime):
                    deadline = todo_task.end_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 已完成任务的图标类型和颜色
            icon_type = 'check'  # 已完成
            icon_color = '#67C23A'  # 绿色
            
            # 查询申请单号（无论任务状态如何，都查询最新的申请单）
            apply_id = None
            task_apply = await TodoTaskApplyDao.get_latest_apply_by_task_id(db, todo_task.id)
            if task_apply:
                apply_id = task_apply.apply_id
            
            row = {
                'taskId': todo_task.task_id,
                'taskName': proj_task.name if proj_task else todo_task.name,
                'projectId': todo_task.project_id,
                'projectName': project_dict.get(str(todo_task.project_id), f'项目{todo_task.project_id}'),
                'deptId': second_level_dept.id if second_level_dept else None,
                'deptName': second_level_dept.name if second_level_dept else None,
                'taskStatus': todo_task.task_status,
                'taskStatusName': status_names.get(todo_task.task_status, f'状态{todo_task.task_status}'),
                'jobNumber': todo_task.job_number,
                'assigneeName': employee.name if employee else None,
                'deadline': deadline,
                'stageId': todo_task.stage_id,
                'stageName': proj_stage.name if proj_stage else None,
                'iconType': icon_type,
                'iconColor': icon_color,
                'applyId': apply_id,  # 添加申请单号字段
                'actualCompleteTime': todo_task.actual_complete_time.strftime('%Y-%m-%d %H:%M:%S') if todo_task.actual_complete_time else None,  # 实际完成时间
            }
            
            rows.append(row)
        
        return {
            'total': total,
            'rows': rows
        }
    
    @classmethod
    async def get_completed_tasks_categories(
        cls,
        db: AsyncSession,
        job_number: str
    ) -> Dict[str, Any]:
        """
        获取已完成任务分类统计
        
        :param db: orm对象
        :param job_number: 负责人工号
        :return: 分类统计数据
        """
        # 1. 获取当前用户的已完成任务列表
        tasks = await TodoQueryDao.get_completed_tasks_for_categories(db, job_number)
        
        # 2. 获取项目字典
        project_dict_list = await DictDataService.query_dict_data_list_services(db, 'sys_task_project')
        project_dict = {item.dict_value: item.dict_label for item in project_dict_list}
        
        # 3. 获取所有相关的员工和部门信息
        job_numbers = list(set([task.job_number for task in tasks if task.job_number]))
        employees_map = {}
        depts_map = {}
        second_level_depts_map = {}
        
        if job_numbers:
            # 查询员工信息
            employees = await db.execute(
                select(OaEmployeePrimary)
                .where(OaEmployeePrimary.job_number.in_(job_numbers))
            )
            employees_list = list(employees.scalars().all())
            employees_map = {emp.job_number: emp for emp in employees_list}
            
            # 查询部门信息
            org_ids = list(set([emp.organization_id for emp in employees_list if emp.organization_id]))
            if org_ids:
                depts = await db.execute(
                    select(OaDepartment)
                    .where(OaDepartment.id.in_(org_ids))
                )
                depts_list = list(depts.scalars().all())
                depts_map = {dept.id: dept for dept in depts_list}
                
                # 获取所有第二级部门code
                second_level_codes = set()
                for dept in depts_list:
                    if dept.code:
                        second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                        if second_level_code:
                            second_level_codes.add(second_level_code)
                
                # 查询第二级部门
                if second_level_codes:
                    second_level_depts = await db.execute(
                        select(OaDepartment)
                        .where(OaDepartment.code.in_(list(second_level_codes)))
                    )
                    second_level_depts_list = list(second_level_depts.scalars().all())
                    second_level_depts_map = {dept.code: dept for dept in second_level_depts_list}
        
        # 4. 统计项目分类
        project_stats = {}
        for task in tasks:
            project_id = task.project_id
            if project_id not in project_stats:
                project_stats[project_id] = {
                    'projectId': project_id,
                    'projectName': project_dict.get(str(project_id), f'项目{project_id}'),
                    'count': 0
                }
            project_stats[project_id]['count'] += 1
        
        # 5. 统计部门分类（第二级部门）
        dept_stats = {}
        for task in tasks:
            employee = employees_map.get(task.job_number)
            if not employee or not employee.organization_id:
                continue
            
            dept = depts_map.get(employee.organization_id)
            if not dept or not dept.code:
                continue
            
            # 获取第二级部门code
            second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
            if not second_level_code:
                continue
            
            second_level_dept = second_level_depts_map.get(second_level_code)
            if not second_level_dept:
                continue
            
            dept_id = second_level_dept.id
            if dept_id not in dept_stats:
                dept_stats[dept_id] = {
                    'deptId': dept_id,
                    'deptName': second_level_dept.name,
                    'count': 0
                }
            dept_stats[dept_id]['count'] += 1
        
        # 6. 历史任务只有完成状态，不需要状态分类统计
        # 但为了保持接口结构一致，返回空的状态分类
        status_stats = {}
        status_names = {3: '完成'}
        for task in tasks:
            status = task.task_status
            if status not in status_stats:
                status_stats[status] = {
                    'status': status,
                    'statusName': status_names.get(status, f'状态{status}'),
                    'count': 0
                }
            status_stats[status]['count'] += 1
        
        return {
            'project': {
                'total': len(tasks),
                'items': list(project_stats.values())
            },
            'department': {
                'total': len(tasks),
                'items': list(dept_stats.values())
            },
            'status': {
                'total': len(tasks),
                'items': list(status_stats.values())
            }
        }
    
    @classmethod
    async def get_task_detail(
        cls,
        db: AsyncSession,
        task_id: int,
        current_user_job_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取任务详情
        
        :param db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :param current_user_job_number: 当前用户工号
        :return: 任务详情数据
        """
        # 1. 获取任务基础数据
        task_data = await TodoQueryDao.get_task_detail_data(db, task_id)
        if not task_data:
            return None
        
        todo_task = task_data['todo_task']
        proj_task = task_data['proj_task']
        proj_stage = task_data['proj_stage']
        employee = task_data['employee']
        dept = task_data['dept']
        second_level_dept = task_data['second_level_dept']
        
        # 2. 获取项目名称
        project_dict_list = await DictDataService.query_dict_data_list_services(db, 'sys_task_project')
        project_dict = {item.dict_value: item.dict_label for item in project_dict_list}
        project_name = project_dict.get(str(todo_task.project_id), f'项目{todo_task.project_id}')
        
        # 3. 构建任务基本信息
        status_names = {1: '待提交', 2: '审批中', 3: '完成', 4: '驳回'}
        task_info = {
            'taskId': todo_task.task_id,
            'taskName': proj_task.name if proj_task else todo_task.name,
            'taskDescription': proj_task.description if proj_task else todo_task.description,
            'projectId': todo_task.project_id,
            'projectName': project_name,
            'stageId': todo_task.stage_id,
            'stageName': proj_stage.name if proj_stage else None,
            'deptId': second_level_dept.id if second_level_dept else None,
            'deptName': second_level_dept.name if second_level_dept else None,
            'jobNumber': todo_task.job_number,
            'assigneeName': employee.name if employee else None,
            'taskStatus': todo_task.task_status,
            'taskStatusName': status_names.get(todo_task.task_status, f'状态{todo_task.task_status}'),
        }
        
        # 4. 获取审批流程信息（从todo_task.approval_nodes读取，无论任务状态）
        approval_flow = None
        
        # 从todo_task.approval_nodes读取审批节点（编制ID列表）
        approval_nodes = []
        if todo_task.approval_nodes:
            try:
                approval_nodes = json.loads(todo_task.approval_nodes) if isinstance(todo_task.approval_nodes, str) else todo_task.approval_nodes
            except (json.JSONDecodeError, TypeError):
                approval_nodes = []
        
        if approval_nodes:
            # 查询编制信息（用于审批节点显示）
            dept_ids = list(set(approval_nodes))
            approval_depts = {}
            if dept_ids:
                dept_result = await db.execute(
                    select(OaDepartment).where(OaDepartment.id.in_(dept_ids))
                )
                depts_list = list(dept_result.scalars().all())
                approval_depts = {dept.id: dept for dept in depts_list}
            
            # 查询每个编制对应的岗位信息（通过 rank_id）
            rank_ids = list(set([dept.rank_id for dept in approval_depts.values() if dept.rank_id]))
            ranks = {}
            if rank_ids:
                from module_admin.entity.do.oa_rank_do import OaRank
                rank_result = await db.execute(
                    select(OaRank).where(OaRank.id.in_(rank_ids))
                )
                ranks_list = list(rank_result.scalars().all())
                ranks = {rank.id: rank for rank in ranks_list}
                    
            # 批量查询所有审批节点对应的审批人（用于pending状态显示）
            pending_approvers_map = {}  # key: dept_id, value: employee
            if dept_ids:
                pending_approvers = await db.execute(
                    select(OaEmployeePrimary)
                    .where(OaEmployeePrimary.organization_id.in_(dept_ids))
                )
                pending_approvers_list = list(pending_approvers.scalars().all())
                pending_approvers_map = {emp.organization_id: emp for emp in pending_approvers_list}
            
            # 如果任务已提交，查询审批状态（已审批节点、当前审批节点、审批日志）
            approved_nodes = []
            current_approval_node = None
            logs_map = {}  # key: approval_node, value: log
            apply_id = None
            
            if todo_task.task_status in [2, 3, 4]:  # 已提交、完成、驳回
                # 查询任务申请详情
                task_apply = await TodoTaskApplyDao.get_latest_apply_by_task_id(db, todo_task.id)
                if task_apply:
                    apply_id = task_apply.apply_id
                    
                    # 查询审批规则（获取已审批节点和当前审批节点）
                    rules = await ApprovalService.get_approval_rules(db, apply_id)
                    if rules:
                        if rules.approved_nodes:
                            try:
                                approved_nodes = json.loads(rules.approved_nodes) if isinstance(rules.approved_nodes, str) else rules.approved_nodes
                            except (json.JSONDecodeError, TypeError):
                                approved_nodes = []
                        
                        current_approval_node = rules.current_approval_node
                        
                        # 查询审批日志
                        logs = await ApprovalLogDao.get_logs_by_apply_id(db, apply_id)
                        for log in logs:
                            if log.approval_node not in logs_map:
                                logs_map[log.approval_node] = []
                            logs_map[log.approval_node].append(log)
            
            # 构建审批节点列表
            approval_nodes_list = []
            current_node_index = None
            
            for index, dept_id in enumerate(approval_nodes, start=1):
                dept = approval_depts.get(dept_id)
                # 获取岗位名称（通过编制的rank_id）
                post_name = None
                if dept and dept.rank_id:
                    rank = ranks.get(dept.rank_id)
                    post_name = rank.rank_name if rank else f'岗位{dept.rank_id}'
                else:
                    post_name = f'编制{dept_id}'
                
                # 判断节点状态
                # 首先检查是否有审批日志（包括同意和驳回）
                node_logs = logs_map.get(dept_id, [])
                reject_log = None
                approve_log = None
                
                for log in node_logs:
                    if log.approval_result == 2:  # 驳回
                        reject_log = log
                        break
                    elif log.approval_result == 1:  # 同意
                        if not approve_log:  # 只取第一个同意的日志
                            approve_log = log
                
                # 如果节点在已审批列表中，且有审批日志
                if todo_task.task_status in [2, 3, 4] and dept_id in approved_nodes:
                    if reject_log:
                        # 被驳回（优先显示驳回信息）
                        status = 'rejected'
                        # 查询驳回人信息
                        rejecter_employee = await db.execute(
                            select(OaEmployeePrimary)
                            .where(OaEmployeePrimary.job_number == reject_log.approver_id)
                        )
                        rejecter_employee = rejecter_employee.scalar_one_or_none()
                        
                        approval_nodes_list.append({
                            'nodeIndex': index,
                            'postId': dept.rank_id if dept and dept.rank_id else None,  # 岗位ID
                            'postName': post_name,
                            'status': status,
                            'approverId': reject_log.approver_id,
                            'approverName': rejecter_employee.name if rejecter_employee else reject_log.approver_id,
                            'approvalTime': reject_log.approval_end_time.strftime('%Y-%m-%d %H:%M:%S') if reject_log.approval_end_time else None,
                            'approvalComment': reject_log.approval_comment,
                        })
                    elif approve_log:
                        # 已审批（同意）
                        status = 'approved'
                        # 查询审批人信息
                        approver_employee = await db.execute(
                            select(OaEmployeePrimary)
                            .where(OaEmployeePrimary.job_number == approve_log.approver_id)
                        )
                        approver_employee = approver_employee.scalar_one_or_none()
                        
                        approval_nodes_list.append({
                            'nodeIndex': index,
                            'postId': dept.rank_id if dept and dept.rank_id else None,  # 岗位ID
                            'postName': post_name,
                            'status': status,
                            'approverId': approve_log.approver_id,
                            'approverName': approver_employee.name if approver_employee else approve_log.approver_id,
                            'approvalTime': approve_log.approval_end_time.strftime('%Y-%m-%d %H:%M:%S') if approve_log.approval_end_time else None,
                            'approvalComment': approve_log.approval_comment,
                        })
                    else:
                        # 已审批但找不到日志（可能是空岗自动审批或其他情况）
                        status = 'approved'
                        approval_nodes_list.append({
                            'nodeIndex': index,
                            'postId': dept.rank_id if dept and dept.rank_id else None,  # 岗位ID
                            'postName': post_name,
                            'status': status,
                            'approverId': None,
                            'approverName': None,
                            'approvalTime': None,
                            'approvalComment': None,
                        })
                elif todo_task.task_status in [2, 3, 4] and current_approval_node == dept_id:
                    # 审批中（任务已提交且该节点是当前审批节点）
                    status = 'approving'
                    current_node_index = index
                    
                    # 获取当前审批人（优先从批量查询的map中获取，如果没有则查询）
                    current_approver = pending_approvers_map.get(dept_id)
                    if not current_approver:
                        current_approver_result = await db.execute(
                            select(OaEmployeePrimary)
                            .where(OaEmployeePrimary.organization_id == dept_id)
                        )
                        current_approver = current_approver_result.scalar_one_or_none()
                    
                    approval_nodes_list.append({
                        'nodeIndex': index,
                        'postId': dept.rank_id if dept and dept.rank_id else None,  # 岗位ID
                        'postName': post_name,
                        'status': status,
                        'approverId': current_approver.job_number if current_approver else None,
                        'approverName': current_approver.name if current_approver else None,
                        'approvalTime': None,
                        'approvalComment': None,
                    })
                else:
                    # 待审批（任务未提交，或任务已提交但该节点还未审批）
                    status = 'pending'
                    
                    # 获取该编制对应的审批人（从批量查询的map中获取，即使任务未提交，也要显示将来谁会审批）
                    pending_approver = pending_approvers_map.get(dept_id)
                    
                    approval_nodes_list.append({
                        'nodeIndex': index,
                        'postId': dept.rank_id if dept and dept.rank_id else None,  # 岗位ID
                        'postName': post_name,
                        'status': status,
                        'approverId': pending_approver.job_number if pending_approver else None,
                        'approverName': pending_approver.name if pending_approver else None,
                        'approvalTime': None,
                        'approvalComment': None,
                    })
            
            approval_flow = {
                'applyId': apply_id,  # 如果任务未提交，apply_id为None
                'approvalNodes': approval_nodes_list,
                'currentApprovalNode': current_node_index,  # 如果任务未提交，current_node_index为None
            }
        
        # 5. 获取任务关系（包含完整信息）
        predecessor_tasks = []
        successor_tasks = []
        if proj_task:
            # 解析前置/后置任务ID列表
            predecessor_task_ids = []
            successor_task_ids = []
            
            if proj_task.predecessor_tasks:
                try:
                    predecessor_task_ids = json.loads(proj_task.predecessor_tasks) if isinstance(proj_task.predecessor_tasks, str) else proj_task.predecessor_tasks
                except (json.JSONDecodeError, TypeError):
                    predecessor_task_ids = []
            
            if proj_task.successor_tasks:
                try:
                    successor_task_ids = json.loads(proj_task.successor_tasks) if isinstance(proj_task.successor_tasks, str) else proj_task.successor_tasks
                except (json.JSONDecodeError, TypeError):
                    successor_task_ids = []
            
            # 获取所有相关任务的ID（去重）
            all_related_task_ids = list(set(predecessor_task_ids + successor_task_ids))
            
            # 批量查询所有相关任务的详细信息
            related_tasks_map = {}
            if all_related_task_ids:
                from module_task.todo.dao.todo_task_dao import TodoTaskDao
                from module_task.entity.do.todo_task_do import TodoTask
                from module_task.entity.do.proj_task_do import ProjTask
                from module_task.entity.do.proj_stage_do import ProjStage
                
                # 查询所有相关任务的执行记录
                related_todo_tasks = await db.execute(
                    select(TodoTask).where(TodoTask.task_id.in_(all_related_task_ids))
                )
                related_todo_tasks_list = list(related_todo_tasks.scalars().all())
                
                # 查询所有相关任务的配置
                related_proj_tasks = await db.execute(
                    select(ProjTask).where(ProjTask.task_id.in_(all_related_task_ids))
                )
                related_proj_tasks_list = list(related_proj_tasks.scalars().all())
                related_proj_tasks_map = {task.task_id: task for task in related_proj_tasks_list}
                
                # 获取所有相关的阶段ID
                related_stage_ids = list(set([task.stage_id for task in related_todo_tasks_list if task.stage_id]))
                related_proj_stages_map = {}
                if related_stage_ids:
                    related_proj_stages = await db.execute(
                        select(ProjStage).where(ProjStage.stage_id.in_(related_stage_ids))
                    )
                    related_proj_stages_list = list(related_proj_stages.scalars().all())
                    related_proj_stages_map = {stage.stage_id: stage for stage in related_proj_stages_list}
                
                # 获取所有相关的员工工号
                related_job_numbers = list(set([task.job_number for task in related_todo_tasks_list if task.job_number]))
                related_employees_map = {}
                related_depts_map = {}
                related_second_level_depts_map = {}
                
                if related_job_numbers:
                    related_employees = await db.execute(
                        select(OaEmployeePrimary)
                        .where(OaEmployeePrimary.job_number.in_(related_job_numbers))
                    )
                    related_employees_list = list(related_employees.scalars().all())
                    related_employees_map = {emp.job_number: emp for emp in related_employees_list}
                    
                    # 查询部门信息
                    related_org_ids = list(set([emp.organization_id for emp in related_employees_list if emp.organization_id]))
                    if related_org_ids:
                        related_depts = await db.execute(
                            select(OaDepartment)
                            .where(OaDepartment.id.in_(related_org_ids))
                        )
                        related_depts_list = list(related_depts.scalars().all())
                        related_depts_map = {dept.id: dept for dept in related_depts_list}
                        
                        # 获取第二级部门
                        related_second_level_codes = set()
                        for dept in related_depts_list:
                            if dept.code:
                                second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                                if second_level_code:
                                    related_second_level_codes.add(second_level_code)
                        
                        if related_second_level_codes:
                            related_second_level_depts = await db.execute(
                                select(OaDepartment)
                                .where(OaDepartment.code.in_(list(related_second_level_codes)))
                            )
                            related_second_level_depts_list = list(related_second_level_depts.scalars().all())
                            related_second_level_depts_map = {dept.code: dept for dept in related_second_level_depts_list}
                
                # 为每个已生成的相关任务构建完整信息
                for related_todo_task in related_todo_tasks_list:
                    related_proj_task = related_proj_tasks_map.get(related_todo_task.task_id)
                    related_employee = related_employees_map.get(related_todo_task.job_number) if related_todo_task.job_number else None
                    related_dept = related_depts_map.get(related_employee.organization_id) if related_employee and related_employee.organization_id else None
                    related_second_level_dept = None
                    if related_dept and related_dept.code:
                        second_level_code = DeptUtil.get_second_level_dept_code(related_dept.code)
                        if second_level_code:
                            related_second_level_dept = related_second_level_depts_map.get(second_level_code)
                    
                    related_proj_stage = related_proj_stages_map.get(related_todo_task.stage_id) if related_todo_task.stage_id else None
                    related_project_name = project_dict.get(str(related_todo_task.project_id), f'项目{related_todo_task.project_id}')
                    
                    # 构建任务信息（taskInfo的所有内容）
                    related_task_info = {
                        'taskId': related_todo_task.task_id,
                        'taskName': related_proj_task.name if related_proj_task else related_todo_task.name,
                        'taskDescription': related_proj_task.description if related_proj_task else related_todo_task.description,
                        'projectId': related_todo_task.project_id,
                        'projectName': related_project_name,
                        'stageId': related_todo_task.stage_id,
                        'stageName': related_proj_stage.name if related_proj_stage else None,
                        'deptId': related_second_level_dept.id if related_second_level_dept else None,
                        'deptName': related_second_level_dept.name if related_second_level_dept else None,
                        'jobNumber': related_todo_task.job_number,
                        'assigneeName': related_employee.name if related_employee else None,
                        'taskStatus': related_todo_task.task_status,
                        'taskStatusName': status_names.get(related_todo_task.task_status, f'状态{related_todo_task.task_status}'),
                    }
                    
                    # 添加实际开始时间和结束时间
                    related_task_data = {
                        'taskInfo': related_task_info,
                        'actualStartTime': related_todo_task.actual_start_time.strftime('%Y-%m-%d %H:%M:%S') if related_todo_task.actual_start_time else None,
                        'actualEndTime': related_todo_task.actual_complete_time.strftime('%Y-%m-%d %H:%M:%S') if related_todo_task.actual_complete_time else None,
                    }
                    
                    related_tasks_map[related_todo_task.task_id] = related_task_data
                
                # 处理未生成的任务（在 proj_task 表中但不在 todo_task 表中）
                generated_task_ids = {task.task_id for task in related_todo_tasks_list}
                ungenerated_task_ids = [task_id for task_id in all_related_task_ids if task_id not in generated_task_ids]
                
                if ungenerated_task_ids:
                    # 查询未生成任务的配置
                    ungenerated_proj_tasks = await db.execute(
                        select(ProjTask).where(ProjTask.task_id.in_(ungenerated_task_ids), ProjTask.enable == '1')
                    )
                    ungenerated_proj_tasks_list = list(ungenerated_proj_tasks.scalars().all())
                    
                    # 获取未生成任务的阶段ID和员工工号
                    ungenerated_stage_ids = list(set([task.stage_id for task in ungenerated_proj_tasks_list if task.stage_id]))
                    ungenerated_job_numbers = list(set([task.job_number for task in ungenerated_proj_tasks_list if task.job_number]))
                    
                    # 查询未生成任务的阶段信息
                    ungenerated_proj_stages_map = {}
                    if ungenerated_stage_ids:
                        ungenerated_proj_stages = await db.execute(
                            select(ProjStage).where(ProjStage.stage_id.in_(ungenerated_stage_ids))
                        )
                        ungenerated_proj_stages_list = list(ungenerated_proj_stages.scalars().all())
                        ungenerated_proj_stages_map = {stage.stage_id: stage for stage in ungenerated_proj_stages_list}
                    
                    # 查询未生成任务的员工和部门信息
                    ungenerated_employees_map = {}
                    ungenerated_depts_map = {}
                    ungenerated_second_level_depts_map = {}
                    
                    if ungenerated_job_numbers:
                        ungenerated_employees = await db.execute(
                            select(OaEmployeePrimary)
                            .where(OaEmployeePrimary.job_number.in_(ungenerated_job_numbers))
                        )
                        ungenerated_employees_list = list(ungenerated_employees.scalars().all())
                        ungenerated_employees_map = {emp.job_number: emp for emp in ungenerated_employees_list}
                        
                        ungenerated_org_ids = list(set([emp.organization_id for emp in ungenerated_employees_list if emp.organization_id]))
                        if ungenerated_org_ids:
                            ungenerated_depts = await db.execute(
                                select(OaDepartment)
                                .where(OaDepartment.id.in_(ungenerated_org_ids))
                            )
                            ungenerated_depts_list = list(ungenerated_depts.scalars().all())
                            ungenerated_depts_map = {dept.id: dept for dept in ungenerated_depts_list}
                            
                            # 获取第二级部门
                            ungenerated_second_level_codes = set()
                            for dept in ungenerated_depts_list:
                                if dept.code:
                                    second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                                    if second_level_code:
                                        ungenerated_second_level_codes.add(second_level_code)
                            
                            if ungenerated_second_level_codes:
                                ungenerated_second_level_depts = await db.execute(
                                    select(OaDepartment)
                                    .where(OaDepartment.code.in_(list(ungenerated_second_level_codes)))
                                )
                                ungenerated_second_level_depts_list = list(ungenerated_second_level_depts.scalars().all())
                                ungenerated_second_level_depts_map = {dept.code: dept for dept in ungenerated_second_level_depts_list}
                    
                    # 为每个未生成的任务构建完整信息
                    for ungenerated_proj_task in ungenerated_proj_tasks_list:
                        ungenerated_employee = ungenerated_employees_map.get(ungenerated_proj_task.job_number) if ungenerated_proj_task.job_number else None
                        ungenerated_dept = ungenerated_depts_map.get(ungenerated_employee.organization_id) if ungenerated_employee and ungenerated_employee.organization_id else None
                        ungenerated_second_level_dept = None
                        if ungenerated_dept and ungenerated_dept.code:
                            second_level_code = DeptUtil.get_second_level_dept_code(ungenerated_dept.code)
                            if second_level_code:
                                ungenerated_second_level_dept = ungenerated_second_level_depts_map.get(second_level_code)
                        
                        ungenerated_proj_stage = ungenerated_proj_stages_map.get(ungenerated_proj_task.stage_id) if ungenerated_proj_task.stage_id else None
                        ungenerated_project_name = project_dict.get(str(ungenerated_proj_task.project_id), f'项目{ungenerated_proj_task.project_id}')
                        
                        # 构建任务信息（未生成任务，状态为"未生成"，其他字段为null或适配的空类型）
                        ungenerated_task_info = {
                            'taskId': ungenerated_proj_task.task_id,
                            'taskName': ungenerated_proj_task.name,
                            'taskDescription': ungenerated_proj_task.description,
                            'projectId': ungenerated_proj_task.project_id,
                            'projectName': ungenerated_project_name,
                            'stageId': ungenerated_proj_task.stage_id,
                            'stageName': ungenerated_proj_stage.name if ungenerated_proj_stage else None,
                            'deptId': ungenerated_second_level_dept.id if ungenerated_second_level_dept else None,
                            'deptName': ungenerated_second_level_dept.name if ungenerated_second_level_dept else None,
                            'jobNumber': ungenerated_proj_task.job_number,
                            'assigneeName': ungenerated_employee.name if ungenerated_employee else None,
                            'taskStatus': -1,  # -1 表示未生成
                            'taskStatusName': '未生成',
                        }
                        
                        # 未生成任务没有实际开始时间和结束时间
                        ungenerated_task_data = {
                            'taskInfo': ungenerated_task_info,
                            'actualStartTime': None,
                            'actualEndTime': None,
                        }
                        
                        related_tasks_map[ungenerated_proj_task.task_id] = ungenerated_task_data
            
            # 构建前置任务列表（按ID顺序）
            for pred_id in predecessor_task_ids:
                if pred_id in related_tasks_map:
                    predecessor_tasks.append(related_tasks_map[pred_id])
                else:
                    # 如果任务不存在（既不在todo_task也不在proj_task中），只返回ID（兼容处理）
                    predecessor_tasks.append({'taskId': pred_id})
            
            # 构建后置任务列表（按ID顺序）
            for succ_id in successor_task_ids:
                if succ_id in related_tasks_map:
                    successor_tasks.append(related_tasks_map[succ_id])
                else:
                    # 如果任务不存在（既不在todo_task也不在proj_task中），只返回ID（兼容处理）
                    successor_tasks.append({'taskId': succ_id})
        
        task_relations = {
            'predecessorTasks': predecessor_tasks,
            'successorTasks': successor_tasks,
        }
        
        # 6. 获取任务进度
        is_overdue = False
        overdue_days = 0
        if todo_task.end_time:
            end_date = todo_task.end_time
            if isinstance(end_date, date):
                from datetime import datetime
                end_datetime = datetime.combine(end_date, datetime.min.time())
                now = datetime.now()
                if now > end_datetime:
                    is_overdue = True
                    overdue_days = (now - end_datetime).days
        
        task_progress = {
            'totalDuration': proj_task.duration if proj_task else todo_task.duration,
            'startTime': todo_task.start_time.strftime('%Y-%m-%d') if todo_task.start_time else None,
            'endTime': todo_task.end_time.strftime('%Y-%m-%d') if todo_task.end_time else None,
            'actualStartTime': todo_task.actual_start_time.strftime('%Y-%m-%d %H:%M:%S') if todo_task.actual_start_time else None,
            'actualEndTime': todo_task.actual_complete_time.strftime('%Y-%m-%d %H:%M:%S') if todo_task.actual_complete_time else None,
            'currentStatus': status_names.get(todo_task.task_status, f'状态{todo_task.task_status}'),
            'isOverdue': is_overdue,
            'overdueDays': overdue_days,
        }
        
        # 7. 获取提交内容
        submit_content = None
        if todo_task.task_status in [2, 3, 4]:  # 已提交、完成、驳回
            task_apply = await TodoTaskApplyDao.get_latest_apply_by_task_id(db, todo_task.id)
            if task_apply:
                submit_images = []
                if task_apply.submit_images:
                    try:
                        submit_images = json.loads(task_apply.submit_images) if isinstance(task_apply.submit_images, str) else task_apply.submit_images
                    except (json.JSONDecodeError, TypeError):
                        submit_images = []
                
                submit_content = {
                    'submitText': task_apply.submit_text,
                    'submitImages': submit_images,
                    'submitTime': task_apply.submit_time.strftime('%Y-%m-%d %H:%M:%S') if task_apply.submit_time else None,
                }
        
        # 8. 获取驳回信息（无论任务状态如何，只要申请单状态为驳回，就查询驳回信息）
        reject_info = None
        # 查询任务申请详情
        task_apply = await TodoTaskApplyDao.get_latest_apply_by_task_id(db, todo_task.id)
        if task_apply:
            apply_id_for_reject = task_apply.apply_id
            # 查询申请单状态
            from module_apply.entity.do.apply_primary_do import ApplyPrimary
            apply_primary_result = await db.execute(
                select(ApplyPrimary).where(ApplyPrimary.apply_id == apply_id_for_reject)
            )
            apply_primary = apply_primary_result.scalar_one_or_none()
            
            # 如果申请单状态为驳回（2），或者任务状态为驳回（4），都查询驳回信息
            if (apply_primary and apply_primary.apply_status == 2) or todo_task.task_status == 4:
                # 查询驳回的审批日志
                logs = await ApprovalLogDao.get_logs_by_apply_id(db, apply_id_for_reject)
                reject_log = None
                for log in logs:
                    if log.approval_result == 2:  # 驳回
                        reject_log = log
                        break
                
                if reject_log:
                    reject_info = {
                        'rejectTime': reject_log.approval_end_time.strftime('%Y-%m-%d %H:%M:%S') if reject_log.approval_end_time else None,
                        'rejectReason': reject_log.approval_comment,
                    }
        
        # 9. 权限标识
        can_submit = (todo_task.task_status == 1 and todo_task.job_number == current_user_job_number)
        can_approve = False
        can_resubmit = (todo_task.task_status == 4 and todo_task.job_number == current_user_job_number)
        
        # 判断是否可以审批
        if todo_task.task_status == 2 and approval_flow:
            # 查询当前审批节点（编制ID）
            rules = await ApprovalService.get_approval_rules(db, approval_flow['applyId'])
            if rules and rules.current_approval_node:
                # 查询当前用户的编制ID
                current_user_employee = await db.execute(
                    select(OaEmployeePrimary)
                    .where(OaEmployeePrimary.job_number == current_user_job_number)
                )
                current_user_employee = current_user_employee.scalar_one_or_none()
                
                # 当前用户的编制ID == 当前审批节点的编制ID
                if current_user_employee and current_user_employee.organization_id == rules.current_approval_node:
                    can_approve = True
        
        # 10. 构建历史审批数据
        history_approval = []
        if approval_nodes:  # 如果有审批节点配置
            # 获取当前申请单ID（如果有）
            current_apply_id = approval_flow.get('applyId') if approval_flow else None
            
            # 查询所有历史申请单（排除当前申请单，按提交时间倒序）
            history_applies = await TodoTaskApplyDao.get_all_applies_by_task_id(
                db, todo_task.id, exclude_apply_id=current_apply_id
            )
            
            # 批量查询编制和岗位信息（复用之前查询的结果）
            # approval_depts, ranks, pending_approvers_map 已经在前面查询过了
            
            # 对于每个历史申请单，构建审批流程
            for history_apply in history_applies:
                history_apply_id = history_apply.apply_id
                
                # 查询审批规则
                history_rules = await ApprovalService.get_approval_rules(db, history_apply_id)
                if not history_rules:
                    continue
                
                # 获取已审批节点
                history_approved_nodes = []
                if history_rules.approved_nodes:
                    try:
                        history_approved_nodes = json.loads(history_rules.approved_nodes) if isinstance(history_rules.approved_nodes, str) else history_rules.approved_nodes
                    except (json.JSONDecodeError, TypeError):
                        history_approved_nodes = []
                
                # 查询审批日志
                history_logs = await ApprovalLogDao.get_logs_by_apply_id(db, history_apply_id)
                history_logs_map = {}  # key: approval_node, value: log
                for log in history_logs:
                    if log.approval_node not in history_logs_map:
                        history_logs_map[log.approval_node] = []
                    history_logs_map[log.approval_node].append(log)
                
                # 构建历史审批节点列表
                history_approval_nodes_list = []
                
                for index, dept_id in enumerate(approval_nodes, start=1):
                    dept = approval_depts.get(dept_id)
                    # 获取岗位名称（通过编制的rank_id）
                    post_name = None
                    if dept and dept.rank_id:
                        rank = ranks.get(dept.rank_id)
                        post_name = rank.rank_name if rank else f'岗位{dept.rank_id}'
                    else:
                        post_name = f'编制{dept_id}'
                    
                    # 历史审批一定是结束的，所以节点状态只能是 approved 或 rejected
                    node_logs = history_logs_map.get(dept_id, [])
                    reject_log = None
                    approve_log = None
                    
                    for log in node_logs:
                        if log.approval_result == 2:  # 驳回
                            reject_log = log
                            break
                        elif log.approval_result == 1:  # 同意
                            if not approve_log:  # 只取第一个同意的日志
                                approve_log = log
                    
                    # 处理审批附件
                    approval_images = []
                    log_for_images = reject_log if reject_log else approve_log
                    if log_for_images and log_for_images.approval_images:
                        try:
                            approval_images = json.loads(log_for_images.approval_images) if isinstance(log_for_images.approval_images, str) else log_for_images.approval_images
                        except (json.JSONDecodeError, TypeError):
                            approval_images = []
                    
                    if reject_log:
                        # 被驳回
                        status = 'rejected'
                        rejecter_employee = await db.execute(
                            select(OaEmployeePrimary)
                            .where(OaEmployeePrimary.job_number == reject_log.approver_id)
                        )
                        rejecter_employee = rejecter_employee.scalar_one_or_none()
                        
                        history_approval_nodes_list.append({
                            'nodeIndex': index,
                            'postId': dept.rank_id if dept and dept.rank_id else None,
                            'postName': post_name,
                            'status': status,
                            'approverId': reject_log.approver_id,
                            'approverName': rejecter_employee.name if rejecter_employee else reject_log.approver_id,
                            'approvalTime': reject_log.approval_end_time.strftime('%Y-%m-%d %H:%M:%S') if reject_log.approval_end_time else None,
                            'approvalComment': reject_log.approval_comment,
                            'approvalImages': approval_images,
                        })
                    elif approve_log:
                        # 已审批（同意）
                        status = 'approved'
                        approver_employee = await db.execute(
                            select(OaEmployeePrimary)
                            .where(OaEmployeePrimary.job_number == approve_log.approver_id)
                        )
                        approver_employee = approver_employee.scalar_one_or_none()
                        
                        history_approval_nodes_list.append({
                            'nodeIndex': index,
                            'postId': dept.rank_id if dept and dept.rank_id else None,
                            'postName': post_name,
                            'status': status,
                            'approverId': approve_log.approver_id,
                            'approverName': approver_employee.name if approver_employee else approve_log.approver_id,
                            'approvalTime': approve_log.approval_end_time.strftime('%Y-%m-%d %H:%M:%S') if approve_log.approval_end_time else None,
                            'approvalComment': approve_log.approval_comment,
                            'approvalImages': approval_images,
                        })
                    elif dept_id in history_approved_nodes:
                        # 已审批但找不到日志（可能是空岗自动审批或其他情况）
                        status = 'approved'
                        history_approval_nodes_list.append({
                            'nodeIndex': index,
                            'postId': dept.rank_id if dept and dept.rank_id else None,
                            'postName': post_name,
                            'status': status,
                            'approverId': None,
                            'approverName': None,
                            'approvalTime': None,
                            'approvalComment': None,
                            'approvalImages': [],
                        })
                    else:
                        # 未审批的节点（理论上历史审批不应该有这种情况，但为了完整性还是处理）
                        status = 'pending'
                        pending_approver = pending_approvers_map.get(dept_id)
                        history_approval_nodes_list.append({
                            'nodeIndex': index,
                            'postId': dept.rank_id if dept and dept.rank_id else None,
                            'postName': post_name,
                            'status': status,
                            'approverId': pending_approver.job_number if pending_approver else None,
                            'approverName': pending_approver.name if pending_approver else None,
                            'approvalTime': None,
                            'approvalComment': None,
                            'approvalImages': [],
                        })
                
                # 获取提交内容信息
                # 1. 从 todo_task_apply 中获取提交文本、提交图片、提交时间
                submit_images = []
                if history_apply.submit_images:
                    try:
                        submit_images = json.loads(history_apply.submit_images) if isinstance(history_apply.submit_images, str) else history_apply.submit_images
                    except (json.JSONDecodeError, TypeError):
                        submit_images = []
                
                # 2. 从审批日志中获取提交人（approval_result=0 的日志的 approver_id）
                submitter_id = None
                submitter_name = None
                for log in history_logs:
                    if log.approval_result == 0:  # 申请提交
                        submitter_id = log.approver_id
                        # 查询提交人信息
                        submitter_employee = await db.execute(
                            select(OaEmployeePrimary)
                            .where(OaEmployeePrimary.job_number == submitter_id)
                        )
                        submitter_employee = submitter_employee.scalar_one_or_none()
                        submitter_name = submitter_employee.name if submitter_employee else submitter_id
                        break
                
                # 3. 获取任务ID（todo_task_apply.task_id 是 todo_task 的主键ID，需要转换为 task_id）
                # 这里需要查询 todo_task 来获取 task_id（业务ID）
                from module_task.entity.do.todo_task_do import TodoTask
                history_task_id = None
                if history_apply.task_id:
                    history_todo_task = await db.execute(
                        select(TodoTask).where(TodoTask.id == history_apply.task_id)
                    )
                    history_todo_task = history_todo_task.scalar_one_or_none()
                    if history_todo_task:
                        history_task_id = history_todo_task.task_id
                
                # 构建提交内容
                submit_content_info = {
                    'applyId': history_apply_id,
                    'taskId': history_task_id,
                    'submitterId': submitter_id,
                    'submitterName': submitter_name,
                    'submitText': history_apply.submit_text,
                    'submitImages': submit_images,
                    'submitTime': history_apply.submit_time.strftime('%Y-%m-%d %H:%M:%S') if history_apply.submit_time else None,
                }
                
                # 构建历史审批对象（不包含 currentApprovalNode）
                history_approval.append({
                    'applyId': history_apply_id,
                    'approvalNodes': history_approval_nodes_list,
                    'submitContent': submit_content_info,
                })
        
        return {
            'taskInfo': task_info,
            'approvalFlow': approval_flow,
            'historyApproval': history_approval,
            'taskRelations': task_relations,
            'taskProgress': task_progress,
            'submitContent': submit_content,
            'rejectInfo': reject_info,
            'canSubmit': can_submit,
            'canApprove': can_approve,
            'canResubmit': can_resubmit,
        }
    
    @classmethod
    async def get_workbench_task_stats(
        cls,
        db: AsyncSession,
        job_number: str
    ) -> Dict[str, int]:
        """
        获取工作台任务统计数据
        
        :param db: orm对象
        :param job_number: 负责人工号
        :return: 统计数据字典 {pendingSubmit, pendingApprove, rejected}
        """
        return await TodoQueryDao.get_workbench_task_stats(db, job_number)
