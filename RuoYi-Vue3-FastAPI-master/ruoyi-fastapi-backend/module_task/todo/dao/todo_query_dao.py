"""
任务查询DAO
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased
from module_task.entity.do.todo_task_do import TodoTask
from module_task.entity.do.proj_task_do import ProjTask
from module_task.entity.do.proj_stage_do import ProjStage
from module_task.entity.do.todo_task_apply_do import TodoTaskApply
from module_apply.entity.do.apply_primary_do import ApplyPrimary
from module_apply.entity.do.apply_rules_do import ApplyRules
from module_admin.entity.do.oa_employee_primary_do import OaEmployeePrimary
from module_admin.entity.do.oa_department_do import OaDepartment
from module_admin.entity.do.dict_do import SysDictData


class TodoQueryDao:
    """任务查询DAO"""
    
    @classmethod
    async def get_my_tasks_for_categories(
        cls, 
        db: AsyncSession, 
        job_number: str
    ) -> List[TodoTask]:
        """
        获取当前用户的任务列表（用于分类统计）
        包含两类任务：
        1. 负责人是当前用户的任务
        2. 需要当前用户审批的任务
        只返回状态为【进行中】、【已提交】、【驳回】的任务
        
        :param db: orm对象
        :param job_number: 负责人工号
        :return: 任务列表
        """
        # 1. 查询当前用户的 organization_id（用于判断是否需要审批）
        current_user_employee = await db.execute(
            select(OaEmployeePrimary)
            .where(OaEmployeePrimary.job_number == job_number)
        )
        current_user_employee = current_user_employee.scalar_one_or_none()
        current_user_organization_id = current_user_employee.organization_id if current_user_employee else None
        
        # 2. 构建条件1：负责人是当前用户的任务
        condition1 = TodoTask.job_number == job_number
        
        # 3. 构建条件2：需要当前用户审批的任务
        condition2 = None
        if current_user_organization_id:
            # 先查询需要当前用户审批的任务ID列表
            # 注意：不在子查询中检查 task_status，因为主查询已经有 base_status_condition 来过滤状态
            # TodoTaskApply.task_id 关联的是 todo_task.id（主键），不是 task_id（业务ID）
            try:
                approval_task_ids_result = await db.execute(
                    select(TodoTaskApply.task_id)
                    .select_from(TodoTaskApply)
                    .join(ApplyPrimary, TodoTaskApply.apply_id == ApplyPrimary.apply_id)
                    .join(ApplyRules, ApplyPrimary.apply_id == ApplyRules.apply_id)
                    .where(
                        ApplyRules.current_approval_node == current_user_organization_id
                    )
                    .distinct()
                )
                approval_task_ids = [row[0] for row in approval_task_ids_result.all() if row[0] is not None]
                
                # 如果列表不为空，构建条件（使用 todo_task.id，即主键）
                if approval_task_ids and len(approval_task_ids) > 0:
                    condition2 = TodoTask.id.in_(approval_task_ids)
            except Exception as e:
                # 如果查询出错，记录日志但不影响主流程
                from utils.log_util import logger
                logger.warning(f'查询审批任务ID列表失败: {str(e)}', exc_info=True)
                condition2 = None
        
        # 4. 组合条件：条件1 OR 条件2
        if condition2 is not None:
            # 如果有审批任务条件，使用 OR 组合
            base_condition = or_(condition1, condition2)
        else:
            # 只有负责人任务条件
            base_condition = condition1
        
        # 5. 执行查询
        result = await db.execute(
            select(TodoTask)
            .where(
                base_condition,
                TodoTask.task_status.in_([1, 2, 4])  # 1-进行中，2-已提交，4-驳回
            )
        )
        return list(result.scalars().all())
    
    @classmethod
    async def get_completed_tasks_for_categories(
        cls, 
        db: AsyncSession, 
        job_number: str
    ) -> List[TodoTask]:
        """
        获取当前用户已完成的任务列表（用于分类统计）
        只返回状态为【完成】的任务
        
        :param db: orm对象
        :param job_number: 负责人工号
        :return: 任务列表
        """
        # 查询负责人是当前用户且状态为已完成的任务
        result = await db.execute(
            select(TodoTask)
            .where(
                TodoTask.job_number == job_number,
                TodoTask.task_status == 3  # 3-完成
            )
        )
        return list(result.scalars().all())
    
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
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        获取当前用户的任务列表（分页、筛选）
        包含两类任务：
        1. 负责人是当前用户的任务
        2. 需要当前用户审批的任务
        
        :param db: orm对象
        :param job_number: 负责人工号
        :param project_id: 项目ID（可选）
        :param dept_id: 部门ID（可选，第二级部门ID）
        :param task_status: 任务状态（可选，1-进行中，2-已提交，4-驳回）
        :param page_num: 页码
        :param page_size: 每页数量
        :return: (任务列表, 总数)
        """
        # 1. 查询当前用户的 organization_id（用于判断是否需要审批）
        current_user_employee = await db.execute(
            select(OaEmployeePrimary)
            .where(OaEmployeePrimary.job_number == job_number)
        )
        current_user_employee = current_user_employee.scalar_one_or_none()
        current_user_organization_id = current_user_employee.organization_id if current_user_employee else None
        
        # 2. 构建基础条件（状态筛选）
        base_status_condition = TodoTask.task_status.in_([1, 2, 4])  # 只查询进行中、已提交、驳回
        
        # 3. 构建条件1：负责人是当前用户的任务
        condition1 = TodoTask.job_number == job_number
        
        # 4. 构建条件2：需要当前用户审批的任务
        # 通过关联查询：todo_task_apply → apply_primary → apply_rules
        condition2 = None
        if current_user_organization_id:
            # 先查询需要当前用户审批的任务ID列表
            # 注意：不在子查询中检查 task_status，因为主查询已经有 base_status_condition 来过滤状态
            # TodoTaskApply.task_id 关联的是 todo_task.id（主键），不是 task_id（业务ID）
            try:
                approval_task_ids_result = await db.execute(
                    select(TodoTaskApply.task_id)
                    .select_from(TodoTaskApply)
                    .join(ApplyPrimary, TodoTaskApply.apply_id == ApplyPrimary.apply_id)
                    .join(ApplyRules, ApplyPrimary.apply_id == ApplyRules.apply_id)
                    .where(
                        ApplyRules.current_approval_node == current_user_organization_id
                    )
                    .distinct()
                )
                approval_task_ids = [row[0] for row in approval_task_ids_result.all() if row[0] is not None]
                
                # 如果列表不为空，构建条件（使用 todo_task.id，即主键）
                if approval_task_ids and len(approval_task_ids) > 0:
                    condition2 = TodoTask.id.in_(approval_task_ids)
            except Exception as e:
                # 如果查询出错，记录日志但不影响主流程
                from utils.log_util import logger
                logger.warning(f'查询审批任务ID列表失败: {str(e)}', exc_info=True)
                condition2 = None
        
        # 5. 组合条件：条件1 OR 条件2
        if condition2 is not None:
            base_condition = or_(condition1, condition2)
        else:
            base_condition = condition1
        
        # 6. 构建完整查询条件
        conditions = [
            base_condition,
            base_status_condition
        ]
        
        # 7. 项目筛选
        if project_id:
            conditions.append(TodoTask.project_id == project_id)
        
        # 8. 状态筛选（如果指定了具体状态）
        if task_status:
            conditions.append(TodoTask.task_status == task_status)
        
        # 9. 部门筛选（如果指定了部门ID）
        if dept_id:
            # 先查询该部门（第二级部门）
            dept = await db.execute(
                select(OaDepartment).where(OaDepartment.id == dept_id)
            )
            dept = dept.scalar_one_or_none()
            
            if not dept or not dept.code:
                return [], 0
            
            # 查询该部门及其所有子部门的员工
            # 使用 code LIKE 查询子部门
            employees = await db.execute(
                select(OaEmployeePrimary.job_number)
                .join(
                    OaDepartment,
                    OaEmployeePrimary.organization_id == OaDepartment.id
                )
                .where(
                    OaDepartment.code.like(f'{dept.code}%'),  # 查询该部门及其所有子部门
                    OaEmployeePrimary.enable == '1'
                )
            )
            employee_job_numbers = [row[0] for row in employees.all() if row[0]]
            
            if employee_job_numbers:
                # 部门筛选只应用于负责人任务（condition1），不影响审批任务
                # 所以需要修改条件：condition1 AND dept_filter OR condition2
                dept_filter = TodoTask.job_number.in_(employee_job_numbers)
                if condition2 is not None:
                    # 重新组合：负责人任务（且符合部门筛选） OR 审批任务
                    base_condition = or_(
                        and_(condition1, dept_filter),
                        condition2
                    )
                    # 替换第一个条件
                    conditions[0] = base_condition
                else:
                    # 只有负责人任务，直接添加部门筛选
                    conditions.append(dept_filter)
            else:
                # 如果没有员工，且没有审批任务，返回空列表
                if condition2 is None:
                    return [], 0
                # 如果有审批任务，仍然可以返回（只返回审批任务）
        
        # 10. 查询数据（按创建时间正序，早创建的在前面）
        query = (
            select(TodoTask)
            .where(and_(*conditions))
            .order_by(TodoTask.id.asc())  # 按ID正序（ID小的创建时间早）
        )
        
        # 如果 page_size > 0，则分页；否则返回所有数据
        if page_size > 0:
            query = query.limit(page_size).offset((page_num - 1) * page_size)
        
        tasks = await db.execute(query)
        task_list = list(tasks.scalars().all())
        
        # 11. 查询总数（如果分页，才需要查询总数）
        if page_size > 0:
            count_query = select(func.count(TodoTask.id)).where(and_(*conditions))
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0
        else:
            # 不分页时，总数就是列表长度
            total = len(task_list)
        
        # 12. 转换为字典列表（包含关联数据）
        result = []
        for task in task_list:
            result.append({
                'todo_task': task,
            })
        
        return result, total
    
    @classmethod
    async def get_completed_tasks_list(
        cls,
        db: AsyncSession,
        job_number: str,
        project_id: Optional[int] = None,
        dept_id: Optional[int] = None,
        page_num: int = 1,
        page_size: int = 10
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        获取当前用户已完成的任务列表（分页、筛选）
        只查询负责人是当前用户且状态为已完成（3）的任务
        
        :param db: orm对象
        :param job_number: 负责人工号
        :param project_id: 项目ID（可选）
        :param dept_id: 部门ID（可选，第二级部门ID）
        :param page_num: 页码
        :param page_size: 每页数量
        :return: (任务列表, 总数)
        """
        # 1. 构建基础条件：只查询已完成的任务（状态为3）
        base_status_condition = TodoTask.task_status == 3
        
        # 2. 构建条件：负责人是当前用户的任务
        base_condition = TodoTask.job_number == job_number
        
        # 3. 构建完整查询条件
        conditions = [
            base_condition,
            base_status_condition
        ]
        
        # 4. 项目筛选
        if project_id:
            conditions.append(TodoTask.project_id == project_id)
        
        # 5. 部门筛选（如果指定了部门ID）
        if dept_id:
            # 先查询该部门（第二级部门）
            dept = await db.execute(
                select(OaDepartment).where(OaDepartment.id == dept_id)
            )
            dept = dept.scalar_one_or_none()
            
            if not dept or not dept.code:
                return [], 0
            
            # 查询该部门及其所有子部门的员工
            # 使用 code LIKE 查询子部门
            employees = await db.execute(
                select(OaEmployeePrimary.job_number)
                .join(
                    OaDepartment,
                    OaEmployeePrimary.organization_id == OaDepartment.id
                )
                .where(
                    OaDepartment.code.like(f'{dept.code}%'),  # 查询该部门及其所有子部门
                    OaEmployeePrimary.enable == '1'
                )
            )
            employee_job_numbers = [row[0] for row in employees.all() if row[0]]
            
            if employee_job_numbers:
                # 添加部门筛选
                conditions.append(TodoTask.job_number.in_(employee_job_numbers))
            else:
                # 如果没有员工，返回空列表
                return [], 0
        
        # 6. 查询数据（按完成时间倒序，最近完成的在前面）
        # MySQL不支持NULLS LAST，使用CASE WHEN来处理NULL值排序
        from sqlalchemy import case
        query = (
            select(TodoTask)
            .where(and_(*conditions))
            .order_by(
                case((TodoTask.actual_complete_time.is_(None), 1), else_=0),  # NULL值排在后面
                TodoTask.actual_complete_time.desc(),  # 有值的按完成时间倒序
                TodoTask.id.desc()  # 完成时间为NULL的按ID倒序
            )
        )
        
        # 如果 page_size > 0，则分页；否则返回所有数据
        if page_size > 0:
            query = query.limit(page_size).offset((page_num - 1) * page_size)
        
        tasks = await db.execute(query)
        task_list = list(tasks.scalars().all())
        
        # 7. 查询总数（如果分页，才需要查询总数）
        if page_size > 0:
            count_query = select(func.count(TodoTask.id)).where(and_(*conditions))
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0
        else:
            # 不分页时，总数就是列表长度
            total = len(task_list)
        
        # 8. 转换为字典列表（包含关联数据）
        result = []
        for task in task_list:
            result.append({
                'todo_task': task,
            })
        
        return result, total
    
    @classmethod
    async def get_task_detail_data(
        cls,
        db: AsyncSession,
        task_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取任务详情数据（包含所有关联信息）
        
        :param db: orm对象
        :param task_id: 任务ID（关联proj_task.task_id）
        :return: 任务详情数据字典
        """
        # 查询任务执行记录
        todo_task = await db.execute(
            select(TodoTask).where(TodoTask.task_id == task_id)
        )
        todo_task = todo_task.scalar_one_or_none()
        
        if not todo_task:
            return None
        
        # 查询任务配置
        proj_task = await db.execute(
            select(ProjTask).where(ProjTask.task_id == task_id)
        )
        proj_task = proj_task.scalar_one_or_none()
        
        # 查询阶段信息
        proj_stage = None
        if todo_task.stage_id:
            proj_stage = await db.execute(
                select(ProjStage).where(ProjStage.stage_id == todo_task.stage_id)
            )
            proj_stage = proj_stage.scalar_one_or_none()
        
        # 查询负责人信息
        employee = None
        if todo_task.job_number:
            employee = await db.execute(
                select(OaEmployeePrimary)
                .where(OaEmployeePrimary.job_number == todo_task.job_number)
            )
            employee = employee.scalar_one_or_none()
        
        # 查询部门信息（第二级部门）
        dept = None
        second_level_dept = None
        if employee and employee.organization_id:
            # 查询员工所属的部门
            dept = await db.execute(
                select(OaDepartment)
                .where(OaDepartment.id == employee.organization_id)
            )
            dept = dept.scalar_one_or_none()
            
            # 如果部门存在，获取第二级部门
            if dept and dept.code:
                from module_task.todo.utils.dept_util import DeptUtil
                second_level_code = DeptUtil.get_second_level_dept_code(dept.code)
                if second_level_code:
                    second_level_dept = await db.execute(
                        select(OaDepartment)
                        .where(OaDepartment.code == second_level_code)
                    )
                    second_level_dept = second_level_dept.scalar_one_or_none()
        
        return {
            'todo_task': todo_task,
            'proj_task': proj_task,
            'proj_stage': proj_stage,
            'employee': employee,
            'dept': dept,
            'second_level_dept': second_level_dept,
        }
    
    @classmethod
    async def get_workbench_task_stats(
        cls,
        db: AsyncSession,
        job_number: str
    ) -> Dict[str, int]:
        """
        获取工作台任务统计数据
        1. 待提交：负责人是当前用户，状态为1（进行中）
        2. 待审批：当前审批节点是当前用户，状态为2（已提交）
        3. 被驳回：负责人是当前用户，状态为4（驳回）
        
        :param db: orm对象
        :param job_number: 负责人工号
        :return: 统计数据字典 {pendingSubmit, pendingApprove, rejected}
        """
        # 1. 查询当前用户的 organization_id（用于判断是否需要审批）
        current_user_employee = await db.execute(
            select(OaEmployeePrimary)
            .where(OaEmployeePrimary.job_number == job_number)
        )
        current_user_employee = current_user_employee.scalar_one_or_none()
        current_user_organization_id = current_user_employee.organization_id if current_user_employee else None
        
        # 2. 统计待提交任务（负责人是当前用户，状态为1-进行中）
        pending_submit_count = await db.execute(
            select(func.count(TodoTask.id))
            .where(
                TodoTask.job_number == job_number,
                TodoTask.task_status == 1  # 进行中
            )
        )
        pending_submit = pending_submit_count.scalar() or 0
        
        # 3. 统计待审批任务（当前审批节点是当前用户，状态为2-已提交）
        pending_approve = 0
        if current_user_organization_id:
            # 查询需要当前用户审批的任务ID列表（状态为2-已提交）
            try:
                approval_task_ids_result = await db.execute(
                    select(TodoTaskApply.task_id)
                    .select_from(TodoTaskApply)
                    .join(ApplyPrimary, TodoTaskApply.apply_id == ApplyPrimary.apply_id)
                    .join(ApplyRules, ApplyPrimary.apply_id == ApplyRules.apply_id)
                    .join(TodoTask, TodoTaskApply.task_id == TodoTask.id)
                    .where(
                        TodoTask.task_status == 2,  # 已提交
                        ApplyRules.current_approval_node == current_user_organization_id
                    )
                    .distinct()
                )
                approval_task_ids = [row[0] for row in approval_task_ids_result.all() if row[0] is not None]
                pending_approve = len(approval_task_ids)
            except Exception as e:
                from utils.log_util import logger
                logger.warning(f'查询待审批任务统计失败: {str(e)}', exc_info=True)
                pending_approve = 0
        
        # 4. 统计被驳回任务（负责人是当前用户，状态为4-驳回）
        rejected_count = await db.execute(
            select(func.count(TodoTask.id))
            .where(
                TodoTask.job_number == job_number,
                TodoTask.task_status == 4  # 驳回
            )
        )
        rejected = rejected_count.scalar() or 0
        
        return {
            'pendingSubmit': pending_submit,
            'pendingApprove': pending_approve,
            'rejected': rejected
        }
